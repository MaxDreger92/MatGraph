import React, { useState, useRef, useEffect, useCallback } from "react"
import { v4 as uuidv4 } from "uuid"
import cytoscape from "cytoscape"
import fcose from "cytoscape-fcose"
import _ from "lodash"
import { toast } from "react-hot-toast"

import { TbBinaryTree } from "react-icons/tb"
import RestartAltIcon from "@mui/icons-material/RestartAlt"
import UndoIcon from "@mui/icons-material/Undo"
import RedoIcon from "@mui/icons-material/Redo"
import { LuFileJson } from "react-icons/lu"

import ContextCanvas from "./ctxt/canvas-ctxt.component"
import Node from "./node.component"
import Connection, { TempConnection } from "./connection.component"
import {
  Rect,
  INode,
  IConnection,
  Position,
  Vector2D,
} from "./types/canvas.types"
import { graphLayouts } from "./types/graphLayouts"
import {
  isConnectableNode,
  isConnectionLegitimate,
  convertToJSONFormat,
  saveToFile,
} from "../../common/helpers"

interface CanvasProps {
  colorIndex: number
  setWorkflow: React.Dispatch<React.SetStateAction<string | null>>
  style?: React.CSSProperties
}

export default function Canvas(props: CanvasProps) {
  const { colorIndex, setWorkflow, style } = props
  const [nodes, setNodes] = useState<INode[]>([])
  const [selectedNodes, setSelectedNodes] = useState<INode[]>([])
  const [selectedNodeIDs, setSelectedNodeIDs] = useState<Set<string> | null>(
    null
  )
  const [connectingNode, setConnectingNode] = useState<INode | null>(null)
  const [connections, setConnections] = useState<IConnection[]>([])
  const [selectedConnectionID, setSelectedConnectionID] = useState<
    IConnection["id"] | null
  >(null)
  const [history, setHistory] = useState<{
    nodes: INode[][]
    connections: IConnection[][]
  }>({ nodes: [], connections: [] })
  const [future, setFuture] = useState<{
    nodes: INode[][]
    connections: IConnection[][]
  }>({ nodes: [], connections: [] })
  const [navOpen, setNavOpen] = useState(false)
  const [clickPosition, setClickPosition] = useState<Position | null>(null)
  const [selectionRect, setSelectionRect] = useState<Rect | null>(null)
  const [dragging, setDragging] = useState(false)
  const [canvasRect, setCanvasRect] = useState<DOMRect | null>(null)
  const canvasRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const savedNodes = localStorage.getItem("nodes")
    const savedConnections = localStorage.getItem("connections")

    if (savedNodes) {
      setNodes(JSON.parse(savedNodes))
      if (savedConnections) setConnections(JSON.parse(savedConnections))
    }
  }, [])

  useEffect(() => {
    localStorage.setItem("nodes", JSON.stringify(nodes))
    localStorage.setItem("connections", JSON.stringify(connections))
  }, [nodes, connections])

  useEffect(() => {
    const resizeObserver = new ResizeObserver(() => {
      if (canvasRef.current) {
        setCanvasRect(canvasRef.current.getBoundingClientRect())
      }
    })

    const currentCanvas = canvasRef.current
    if (currentCanvas) {
      resizeObserver.observe(currentCanvas)
    }

    return () => {
      if (currentCanvas) {
        resizeObserver.unobserve(currentCanvas)
      }
    }
  }, [canvasRef])

  useEffect(() => {
    setWorkflow(convertToJSONFormat(nodes, connections))
  }, [nodes, connections, setWorkflow])

  const saveWorkflow = () => {
    const workflow = convertToJSONFormat(nodes, connections) //stringified
    saveToFile(workflow, "json", "workflow.json")
  }

  const addNode = (type: INode["type"], position: Position) => {
    const id = uuidv4().replaceAll("-", "")
    const layer = 0
    const size = 100
    const newNode = {
      id,
      name: "",
      type,
      position,
      size,
      layer,
      isEditing: true,
    }
    if (connectingNode) {
      addConnection(connectingNode, newNode)
    } else {
      updateHistory()
    }
    setNodes((prevNodes) => [...prevNodes, newNode])
  }

  const handleNodeClick = (node: INode) => {
    setSelectionRect(null)
    if (connectingNode) {
      addConnection(connectingNode, node)
      setConnectingNode(null)
    } else {
      updateHistoryRevert()
      if (nodeSelectionStatus(node.id) > 0) {
        setSelectedNodes([])
      } else if (!navOpen) {
        setSelectedNodes([node])
        setSelectedConnectionID(null)
      } else {
        setNavOpen(false)
      }
    }
  }

  const initNodeMove = (nodeID: INode["id"]) => {
    updateHistoryWithCaution()
    setConnectingNode(null)
    setNavOpen(false)
    switch (nodeSelectionStatus(nodeID)) {
      case 0:
        setSelectedNodes([])
        setSelectedNodeIDs(null)
        break
      case 1:
        setSelectedNodeIDs(null)
        break
      case 2:
        setSelectedNodeIDs(new Set(selectedNodes.map((n) => n.id)))
        break
      default:
        return
    }
  }

  const completeNodeMove = () => {
    updateHistoryComplete()
  }

  const handleNodeMove = _.throttle(
    (nodeID: INode["id"], displacement: Vector2D) => {
      if (selectedNodes.length > 1) {
        if (!selectedNodeIDs) return
        setNodes((prevNodes) =>
          prevNodes.map((n) =>
            selectedNodeIDs.has(n.id)
              ? {
                  ...n,
                  position: {
                    x: n.position.x + displacement.x,
                    y: n.position.y + displacement.y,
                  },
                }
              : n
          )
        )
      } else {
        setNodes((prevNodes) =>
          prevNodes.map((n) =>
            n.id === nodeID
              ? {
                  ...n,
                  position: {
                    x: n.position.x + displacement.x,
                    y: n.position.y + displacement.y,
                  },
                }
              : n
          )
        )
      }
    },
    10
  )

  const handleNodeConnect = (node: INode) => {
    setNavOpen(false)
    setClickPosition(null)
    setSelectedNodes([])
    setSelectedConnectionID(null)
    setConnectingNode(node)
  }

  const initNodeNameChange = (nodeID: INode["id"], undoHistory?: boolean) => {
    if (undoHistory) updateHistoryRevert()
    setNodes((prevNodes) =>
      prevNodes.map((node) =>
        node.id === nodeID ? { ...node, isEditing: true } : node
      )
    )
  }

  const handleNodeNameChange = (
    nodeID: INode["id"],
    name?: string,
    value?: number,
    operator?: INode["operator"]
  ) => {
    const newName = name ? name : ""
    setNodes((prevNodes) =>
      prevNodes.map((n) => {
        if (n.id === nodeID) {
          const updatedNode: INode = {
            ...n,
            name: newName,
            value: value,
            operator: operator,
            isEditing: false,
          }
          // Check if any fields have changed
          if (
            newName !== n.name ||
            value !== n.value ||
            operator !== n.operator
          ) {
            updateHistory() // Call updateHistory only if a change has occurred
          }
          return updatedNode
        }
        return n
      })
    )
    setSelectedNodes([])
  }

  const handleNodeLayerChange = (node: INode, up?: boolean) => {
    updateHistory()
    setNodes((prevNodes) =>
      prevNodes.map((n) => {
        if (n.id === node.id) {
          return {
            ...n,
            layer: up === true ? n.layer + 1 : n.layer - 1 > 0 ? n.layer - 1 : 0,
          }
        } else {
          return n
        }
      })
    )
  }

  const handleNodeScale = (nodeID: INode["id"], delta?: number) => {
    if (!delta) return
    updateHistory()
    setNodes((prevNodes) =>
      prevNodes.map((n) => {
        if (n.id === nodeID) {
          return {
            ...n,
            size:
              delta < 0 && n.size < 350
                ? n.size - delta * 5
                : delta > 0 && n.size > 75
                ? n.size - delta * 5
                : n.size,
          }
        } else {
          return n
        }
      })
    )
  }

  const handleNodeDelete = (nodeID: INode["id"]) => {
    updateHistory()
    setNodes((prevNodes) => prevNodes.filter((n) => n.id !== nodeID))
    setConnections((prevConnections) =>
      prevConnections.filter(
        (connection) =>
          connection.start.id !== nodeID && connection.end.id !== nodeID
      )
    )
    setSelectedNodes([])
  }

  const handleNodeAction = (
    node: INode,
    action: string,
    name?: string,
    value?: number,
    operator?: INode["operator"],
    conditional?: boolean,
  ) => {
    switch (action) {
      case "click":
        handleNodeClick(node)
        break
      case "initMove":
        initNodeMove(node.id)
        break
      case "completeMove":
        completeNodeMove()
        break
      case "scale":
        handleNodeScale(node.id, value)
        break
      case "connect":
        handleNodeConnect(node)
        break
      case "rename":
        handleNodeNameChange(node.id, name, value, operator)
        break
      case "setIsEditing":
        initNodeNameChange(node.id, conditional)
        break
      case "delete":
        setSelectedNodes([])
        handleNodeDelete(node.id)
        break
      case "changeLayer":
        handleNodeLayerChange(node, conditional)
        break
      default:
        break
    }
  }

  const nodeSelectionStatus = (nodeID: string) => {
    const isSelected = selectedNodes.some(
      (selectedNode) => selectedNode.id === nodeID
    )
    if (isSelected) {
      if (selectedNodes.length > 1) return 2
      return 1
    }
    return 0
  }

  const addConnection = (start: INode, end: INode) => {
    if (start.id === end.id) return
    const connectionExists = connections.some(
      (connection) =>
        (connection.start.id === start.id && connection.end.id === end.id) ||
        (connection.start.id === end.id && connection.end.id === start.id)
    )
    if (connectionExists || !isConnectionLegitimate(start, end)) {
      toast.error("Connection invalid!")
      return
    }
    updateHistory()
    const connectionID = uuidv4().replaceAll("-", "")
    setConnections((prevConnections) => [
      ...prevConnections,
      { start: start, end: end, id: connectionID },
    ])
  }

  const handleConnectionClick = (connectionID: IConnection["id"]) => {
    setSelectedConnectionID(connectionID)
    setSelectedNodes([])
    if (navOpen) {
      setNavOpen(false)
      setClickPosition(null)
    }
  }

  const handleConnectionDelete = (connectionID: IConnection["id"]) => {
    updateHistory()
    setConnections((prevConnections) =>
      prevConnections.filter((connection) => connection.id !== connectionID)
    )
  }

  const handleConnectionReverse = (connectionID: IConnection["id"]) => {
    setConnections((prevConnections) =>
      prevConnections.map((c) => {
        if (c.id === connectionID && isConnectionLegitimate(c.end, c.start)) {
          updateHistory()
          return { ...c, start: c.end, end: c.start }
        } else {
          toast.error("Connection cannot be reversed!")
          return c
        }
      })
    )
  }

  const handleConnectionAction = (
    connectionID: IConnection["id"],
    action: string
  ) => {
    switch (action) {
      case "click":
        handleConnectionClick(connectionID)
        break
      case "reverse":
        handleConnectionReverse(connectionID)
        break
      case "delete":
        handleConnectionDelete(connectionID)
        break
      default:
        break
    }
  }

  const handleCanvasMouseDown = (e: React.MouseEvent) => {
    if (!canvasRect || navOpen || e.button === 2) return
    setDragging(true)
    setClickPosition({
      x: e.clientX - canvasRect.left,
      y: e.clientY - canvasRect.top,
    })
  }

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (!dragging || !clickPosition || !canvasRect) return

    const mousePos = {
      x: e.clientX - canvasRect.left,
      y: e.clientY - canvasRect.top,
    }

    setSelectionRect({
      left: Math.min(clickPosition.x, mousePos.x),
      top: Math.min(clickPosition.y, mousePos.y),
      width: Math.abs(mousePos.x - clickPosition.x),
      height: Math.abs(mousePos.y - clickPosition.y),
    })
  }

  const handleCanvasMouseUp = (e: React.MouseEvent) => {
    if (e.button === 2) return
    setDragging(false)
    if (selectionRect) {
      const rectSelectedNodes = nodes.filter((node) => {
        return (
          node.position.x >= selectionRect.left &&
          node.position.x <= selectionRect.left + selectionRect.width &&
          node.position.y >= selectionRect.top &&
          node.position.y <= selectionRect.top + selectionRect.height
        )
      })
      setSelectedNodes(rectSelectedNodes)
      setSelectionRect(null)
      setClickPosition(null)
    } else if (navOpen) {
      setNavOpen(false)
      setConnectingNode(null)
    } else if (connectingNode) {
      if (isConnectableNode(connectingNode.type) && canvasRect) {
        const canvasClickPosition = {
          x: e.clientX - canvasRect.left,
          y: e.clientY - canvasRect.top,
        }
        setClickPosition(canvasClickPosition)
        setNavOpen(true)
      } else {
        setConnectingNode(null)
        toast.error("No possible connection!")
      }
    } else {
      setConnectingNode(null)
      setSelectedNodes([])
    }
    setSelectedConnectionID(null)
  }

  const handleCanvasClick = (e: React.MouseEvent) => {
    console.log("canvasClick")
  }

  const handleDefaultContextMenu = (e: React.MouseEvent) => {
    e.preventDefault()
    setSelectionRect(null)
    if (canvasRect) {
      const canvasClickPosition = {
        x: e.clientX - canvasRect.left,
        y: e.clientY - canvasRect.top,
      }
      setClickPosition(canvasClickPosition)
      setNavOpen(true)
    }
    setSelectedNodes([])
    setSelectedConnectionID(null)
    setConnectingNode(null)
  }

  const handleCanvasKeyUp = (e: React.KeyboardEvent) => {
    if (e.key !== "Delete" || (!selectedNodes && !selectedConnectionID)) return
    updateHistory()
    if (selectedNodes.length > 0) {
      const nodeIDs = new Set(selectedNodes.map((n) => n.id))
      if (!nodeIDs) return
      setNodes((prevNodes) => prevNodes.filter((n) => !nodeIDs.has(n.id)))
      setConnections((prevConnections) =>
        prevConnections.filter(
          (connection) =>
            !nodeIDs.has(connection.start.id) && !nodeIDs.has(connection.end.id)
        )
      )
    } else if (selectedConnectionID) {
      setConnections((prevConnections) =>
        prevConnections.filter(
          (connection) => connection.id !== selectedConnectionID 
        ))
      // setConnections((prevConnections) =>
      //   prevConnections.filter((connection) => connection.id !== connectionID)
      // )
    }
  }

  const handleContextSelect = (type?: INode["type"]) => {
    console.log("i get it")
    if (type && clickPosition) {
      addNode(type, clickPosition)
    }
    setNavOpen(false)
    setClickPosition(null)
  }

  const handleLayoutNodes = (e: React.MouseEvent) => {
    updateHistory()
    e.stopPropagation()

    cytoscape.use(fcose)
    const cy = cytoscape({
      elements: {
        nodes: nodes.map((node) => ({ data: { id: node.id } })),
        edges: connections.map((connection) => ({
          data: {
            id: connection.id,
            source: connection.start.id,
            target: connection.end.id,
          },
        })), // Transform connections to Cytoscape format
      },
      headless: true,
    })

    const layout = cy.layout(graphLayouts[3]) // choose layout
    layout.run()

    const nodePositions = cy.nodes().map((node) => ({
      id: node.id(),
      position: node.position(),
    }))

    if (canvasRect) {
      const updatedNodes = nodes.map((node) => {
        const newNode = { ...node } // Copy node to not mutate the original object
        const foundPosition = nodePositions.find((np) => np.id === node.id)
        if (foundPosition) {
          // const xPrime =
          //   foundPosition.position.x * Math.cos(-Math.PI / 2) -
          //   foundPosition.position.y * Math.sin(-Math.PI / 2)
          // const yPrime =
          //   foundPosition.position.x * Math.sin(-Math.PI / 2) +
          //   foundPosition.position.y * Math.cos(-Math.PI / 2)

          newNode.position = {
            x:
              foundPosition.position.x + canvasRect.width / 2 - canvasRect.left,
            y:
              foundPosition.position.y +
              canvasRect.height / 2 -
              canvasRect.top +
              20,
          }
        }
        return newNode
      })

      setNodes(updatedNodes)
    }
  }

  const updateHistory = () => {
    setHistory((prev) => ({
      nodes: [...prev.nodes, nodes].slice(-20),
      connections: [...prev.connections, connections].slice(-20),
    }))
    setFuture({ nodes: [], connections: [] })
  }

  const updateHistoryWithCaution = () => {
    setHistory((prev) => ({
      nodes: [...prev.nodes, nodes].slice(-20),
      connections: [...prev.connections, connections].slice(-20),
    }))
  }

  const updateHistoryRevert = () => {
    setHistory((prev) => ({
      nodes: prev.nodes.slice(0, -1),
      connections: prev.connections.slice(0, -1),
    }))
  }

  const updateHistoryComplete = () => {
    setFuture({ nodes: [], connections: [] })
  }

  const logHistory = () => {
    history.nodes.forEach((nodesArray, index) => {
      console.log(`History entry ${index}:`)

      nodesArray.forEach((node, index) => {
        console.log(
          `Node ${index}: x = ${node.position.x}, y = ${node.position.y}`
        )
      })
    })
  }

  const handleReset = () => {
    if (!nodes.length) return
    updateHistory()
    setNodes([])
    setConnections([])
  }

  const undo = useCallback(() => {
    if (history.nodes.length) {
      setFuture((prev) => ({
        nodes: [nodes, ...prev.nodes].slice(-20),
        connections: [connections, ...prev.connections].slice(-20),
      }))
      setNodes(history.nodes[history.nodes.length - 1].map(node => ({ ...node, isEditing: false })))
      setConnections(history.connections[history.connections.length - 1])
      setHistory((prev) => ({
        nodes: prev.nodes.slice(0, -1),
        connections: prev.connections.slice(0, -1),
      }))
    }
  }, [history, nodes, connections])

  const redo = useCallback(() => {
    if (future.nodes.length) {
      setHistory((prev) => ({
        nodes: [...prev.nodes, nodes].slice(-20),
        connections: [...prev.connections, connections].slice(-20),
      }))
      setNodes(future.nodes[0].map(node => ({ ...node, isEditing: false })))
      setConnections(future.connections[0])
      setFuture((prev) => ({
        nodes: prev.nodes.slice(1),
        connections: prev.connections.slice(1),
      }))
    }
  }, [future, nodes, connections])

  useEffect(() => {
    const handleCanvasKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === "Z") {
        e.preventDefault()
        redo()
      } else if (e.ctrlKey) {
        switch (e.key) {
          case "z":
            e.preventDefault()
            undo()
            break
          case "y":
            e.preventDefault()
            redo()
            break
          default:
            break
        }
      }
    }

    window.addEventListener("keydown", handleCanvasKeyDown)

    return () => {
      window.removeEventListener("keydown", handleCanvasKeyDown)
    }
  }, [undo, redo])

  return (
    <div
      className="canvas"
      style={style}
      // Selection rectangle
      onMouseDown={handleCanvasMouseDown}
      onMouseMove={handleCanvasMouseMove}
      onMouseUp={handleCanvasMouseUp}
      // Context menu
      // onClick={handleCanvasClick}
      onContextMenu={handleDefaultContextMenu}
      // Delete stuff
      onKeyUp={handleCanvasKeyUp}
      ref={canvasRef}
      tabIndex={0}
    >
      {/* Connections */}
      {connections.map((connection, i) => {
        const startNode = nodes.find((node) => node.id === connection.start.id)
        const endNode = nodes.find((node) => node.id === connection.end.id)
        if (!startNode || !endNode) return null // Skip rendering if nodes are not found
        return (
          <Connection
            key={i}
            handleConnectionAction={handleConnectionAction}
            connection={{ start: startNode, end: endNode, id: connection.id }}
            isSelected={connection.id === selectedConnectionID}
          />
        )
      })}
      {/* Temp Connection */}
      {connectingNode && (
        <TempConnection
          startPosition={connectingNode.position}
          endPosition={clickPosition}
          canvasRect={canvasRect}
        />
      )}
      {/* Nodes */}
      {nodes.map((node, i) => (
        <Node
          key={node.id}
          node={node}
          isSelected={nodeSelectionStatus(node.id)}
          connecting={Boolean(connectingNode)}
          colorIndex={colorIndex}
          canvasRect={canvasRect}
          handleNodeMove={handleNodeMove}
          handleNodeAction={handleNodeAction}
        />
      ))}
      {/* Selection rectangle */}
      {selectionRect && (
        <div
          className="selection-rect"
          style={{
            top: selectionRect.top,
            left: selectionRect.left,
            width: selectionRect.width,
            height: selectionRect.height,
          }}
        />
      )}
      {/* Canvas Buttons */}
      <div
        className="canvas-btn-wrap"
        style={{ left: canvasRect ? canvasRect.width / 2 : "50%" }}
      >
        <div className="canvas-btn" style={{ textAlign: "center" }}>
          {history.nodes.length}
        </div>
        <div className="canvas-btn-divider" />
        <div className="canvas-btn" onClick={undo}>
          <UndoIcon className="canvas-btn-icon" />
        </div>
        <div className="canvas-btn-divider" />
        <div className="canvas-btn" onClick={handleReset}>
          <RestartAltIcon className="canvas-btn-icon" />
        </div>
        <div className="canvas-btn-divider" />
        <div className="canvas-btn" onClick={redo}>
          <RedoIcon className="canvas-btn-icon" />
        </div>
        <div className="canvas-btn-divider" />
        <div className="canvas-btn" onClick={handleLayoutNodes}>
          <TbBinaryTree
            className="canvas-btn-icon"
            style={{ width: "80%", height: "80%", marginLeft: "3px" }}
          />
        </div>
        <div className="canvas-btn-divider" />
        <div className="canvas-btn" onClick={saveWorkflow}>
          <LuFileJson
            className="canvas-btn-icon"
            style={{ width: "80%", height: "80%", marginLeft: "3px" }}
          />
        </div>

        {/* Log History button for debugging */}
        {/* <div className="canvas-btn-divider" /> 
        <div className="canvas-btn" onClick={logHistory}>
          Log 
        </div>  */}
      </div>
      {/* Canvas Context Menu */}
      {navOpen && clickPosition && (
        <div
          style={{
            position: "absolute",
            left: clickPosition.x,
            top: clickPosition.y,
            transform: "translate(-50%, -50%)",
          }}
        >
          <ContextCanvas
            onSelect={handleContextSelect}
            open={navOpen}
            colorIndex={colorIndex}
            contextRestrict={connectingNode?.type}
          />
        </div>
      )}
    </div>
  )
}
