// TODO: copy - paste?

import React, { useState, useRef, useEffect, useCallback } from "react"
import { v4 as uuidv4 } from "uuid"
import cytoscape from "cytoscape"
import fcose from "cytoscape-fcose"
import _ from "lodash"
import { toast } from "react-hot-toast"

import ContextCanvas from "./CanvasContext"
import Node from "./node/Node"
import Relationship, { TempRelationship } from "./relationship/Relationship"
import {
  Rect,
  INode,
  IRelationship,
  Position,
  Vector2D,
  ICanvasButton,
} from "../../types/canvas.types"
import { graphLayouts } from "../../types/canvas.graphLayouts"
import {
  isConnectableNode,
  isRelationshipLegitimate
} from "../../common/helpers"
import CanvasButtonGroup from "./CanvasButtonGroup"

interface CanvasProps {
  uploadMode: boolean
  nodes: INode[]
  relationships: IRelationship[]
  setNodes: React.Dispatch<React.SetStateAction<INode[]>>
  setRelationships: React.Dispatch<React.SetStateAction<IRelationship[]>>
  selectedNodes: INode[]
  setSelectedNodes: React.Dispatch<React.SetStateAction<INode[]>>
  saveWorkflow: () => void
  updateHistory: () => void
  updateHistoryWithCaution: () => void
  updateHistoryRevert: () => void
  updateHistoryComplete: () => void
  handleReset: () => void
  undo: () => void
  redo: () => void
  needLayout: boolean
  setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
  style?: React.CSSProperties
  colorIndex: number
}

export default function Canvas(props: CanvasProps) {
  const {
    uploadMode,
    nodes,
    relationships,
    setNodes,
    setRelationships,
    selectedNodes,
    setSelectedNodes,
    saveWorkflow,
    updateHistory,
    updateHistoryWithCaution,
    updateHistoryRevert,
    updateHistoryComplete,
    handleReset,
    undo,
    redo,
    needLayout,
    setNeedLayout,
    style,
    colorIndex,
  } = props

  const [nodeEditing, setNodeEditing] = useState(false)
  const [isLayouting, setIsLayouting] = useState(false)
  const [movingNodeIDs, setMovingNodeIDs] = useState<Set<string> | null>(null)
  const [connectingNode, setConnectingNode] = useState<INode | null>(null)
  const [selectedRelationshipID, setSelectedRelationshipID] = useState<
    IRelationship["id"] | null
  >(null)
  const [mousePosition, setMousePosition] = useState<Position>({ x: 0, y: 0 })
  const [navOpen, setNavOpen] = useState(false)
  const [clickPosition, setClickPosition] = useState<Position | null>(null)
  const [selectionRect, setSelectionRect] = useState<Rect | null>(null)
  const [dragging, setDragging] = useState(false)
  const [dragCurrentPos, setDragCurrentPos] = useState<Position | null>(null)
  const [altPressed, setAltPressed] = useState(false)
  const [ctrlPressed, setCtrlPressed] = useState(false)
  const [canvasRect, setCanvasRect] = useState<DOMRect | null>(null)
  const canvasRef = useRef<HTMLDivElement>(null)
  const layoutingTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Resize Observer to get correct canvas bounds and
  // successively correct mouse positions
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
    const handleMouseMove = (e: MouseEvent) => {
      if (!canvasRect) return
      setMousePosition({
        x: e.clientX - canvasRect.left,
        y: e.clientY - canvasRect.top,
      })
    }

    window.addEventListener("mousemove", handleMouseMove)
    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
    }
  })

  // addNode from canvas context menu
  // if created from connector, automatically
  // add relationship between nodes
  const addNode = (type: INode["type"], position: Position) => {
    const id = uuidv4().replaceAll("-", "")
    const layer = 0
    const size = 100
    const newNode = {
      id,
      name: {value:"", index: ""},
      value: {valOp:{value: "", operator: ""}},
      batch_num: {value:""},
      ratio: {valOp:{value: "", operator: ""}},
      concentration: {valOp:{value: "", operator: ""}},
      unit: {value:""},
      std: {valOp:{value: "", operator: ""}},
      error: {valOp:{value: "", operator: ""}},
      identifier: {value:""},
      type,
      with_indices: uploadMode,
      position,
      size,
      layer, 
      isEditing: true,
    }
    if (connectingNode) {
      addRelationship(connectingNode, newNode)
    } else {
      updateHistory()
    }
    setNodes((prevNodes) => [...prevNodes, newNode])
  }

  // handle click (release) on node
  // adds relationship if connecting from other node
  // selects node (will also open node context)
  const handleNodeClick = (node: INode) => {
    cleanupDrag()
    if (selectionRect) {
      selectNodesBySelectionRect(node)
    } else if (connectingNode) {
      addRelationship(connectingNode, node)
      setConnectingNode(null)
    } else {
      if (nodeEditing) return
      updateHistoryRevert()
      switch (nodeSelectionStatus(node.id)) {
        case 0:
          if (!navOpen) {
            setSelectedRelationshipID(null)
            if (ctrlPressed) {
              setSelectedNodes((selectedNodes) => [...selectedNodes, node])
              return
            }
            setSelectedNodes([node])
          } else {
            setNavOpen(false)
          }
          break
        case 1:
          setSelectedNodes([])
          break
        case 2:
          if (ctrlPressed) {
            setSelectedNodes(
              selectedNodes.filter(
                (selectedNode) => selectedNode.id !== node.id
              )
            )
            return
          }
          setSelectedNodes([node])
          break
        default:
          return
      }
    }
  }

  // initialize node movement
  // mainly prevents unwanted actions
  // like moving nodes that are not involved
  const initNodeMove = (nodeID: INode["id"]) => {
    updateHistoryWithCaution()
    setConnectingNode(null)
    setNavOpen(false)
    setClickPosition(null)
    setDragging(true)
    setDragCurrentPos(mousePosition)
    if (altPressed) {
      setMovingNodeIDs(new Set(nodes.map((n) => n.id)))
    } else {
      switch (nodeSelectionStatus(nodeID)) {
        case 0:
          if (ctrlPressed) {
            setMovingNodeIDs(new Set(selectedNodes.map((n) => n.id)))
            return
          }
          setSelectedNodes([])
          setMovingNodeIDs(new Set([nodeID]))
          break
        case 1:
          setMovingNodeIDs(new Set([nodeID]))
          break
        case 2:
          setMovingNodeIDs(new Set(selectedNodes.map((n) => n.id)))
          break
        default:
          return
      }
    }
  }

  // finalize node movement
  // saves movement to history
  // -> action can be undone and redone properly
  const completeNodeMove = () => {
    cleanupDrag()
    updateHistoryComplete()
  }

  const cleanupDrag = () => {
    setClickPosition(null)
    setDragging(false)
    setDragCurrentPos(null)
  }

  // actual node movement
  // TODO: change method of moving nodes
  // from mapping whole node array for
  // each movement step, to splitting array
  // into static and dynamic nodes and
  // moving whole array more efficiently
  const handleNodeMove = _.throttle((displacement: Vector2D) => {
    if (!movingNodeIDs) return
    setNodes((prevNodes) =>
      prevNodes.map((n) =>
        movingNodeIDs.has(n.id)
          ? {
              ...n,
              position: {
                // x: clamp(n.position.x + displacement.x, n.size/2 + 10, window.innerWidth - (n.size/2)),
                // y: clamp(n.position.y + displacement.y, n.size/2, window.innerHeight - (n.size/2)),
                x: n.position.x + displacement.x,
                y: n.position.y + displacement.y,
              },
            }
          : n
      )
    )
  })

  // move all nodes
  const handleCanvasGrab = (displacement: Vector2D) => {
    setNodes((prevNodes) =>
      prevNodes.map((n) => ({
        ...n,
        position: {
          // x: clamp(n.position.x + displacement.x, n.size / 2 + 10, window.innerWidth - (n.size / 2)),
          // y: clamp(n.position.y + displacement.y, n.size / 2, window.innerHeight - (n.size / 2)),
          x: n.position.x + displacement.x,
          y: n.position.y + displacement.y,
        },
      }))
    )
  }

  // initialize node relationship
  // -> mouse needs to be released on another node
  //    to create a relationship
  const handleNodeConnect = (node: INode) => {
    setNavOpen(false)
    setClickPosition(null)
    setSelectedNodes([])
    setSelectedRelationshipID(null)
    setConnectingNode(node)
  }

  // sets node isEditing field
  // so input field will show
  const initNodeNameChange = (nodeID: INode["id"], undoHistory?: boolean) => {
    cleanupDrag()
    if (nodeEditing || ctrlPressed) return
    if (undoHistory) updateHistoryRevert()
    // if (ctrlPressed) {
    //   return
    //   // const node = nodes.find((node) => node.id === nodeID)
    //   // if (node) {
    //   //   handleNodeClick(node)
    //   //   return
    //   // }
    // } else {
    //   // setSelectedNodes([])
    // }
    setNodes((prevNodes) =>
      prevNodes.map((node) =>
        node.id === nodeID ? { ...node, isEditing: true } : node
      )
    )
    setNodeEditing(true)
  }

  // rename node -> resetting isEditing to false
  const handleSetNodeVals = (node: INode) => {
    setNodes((prevNodes) =>
      prevNodes.map((n) => {
        if (n.id === node.id) {
          const updatedNode = {
            ...node,
            isEditing: false
          }
          // Check if any fields have changed
          if (
            node.name.value !== n.name.value ||
            node.value.valOp !== n.value.valOp ||
            node.batch_num.value !== n.batch_num.value ||
            node.ratio.valOp !== n.ratio.valOp ||
            node.concentration.valOp !== n.concentration.valOp ||
            node.unit.value !== n.unit.value ||
            node.std.valOp !== n.std.valOp ||
            node.error.valOp !== n.error.valOp ||
            node.identifier.value !== n.identifier.value
          ) {
            updateHistory() // Call updateHistory only if a change has occurred
          }
          return updatedNode
        }
        return n
      })
    )
    setNodeEditing(false)
    setSelectedNodes([])
  }

  // deprecated
  const handleNodeLayerChange = (node: INode, up?: boolean) => {
    updateHistory()
    setNodes((prevNodes) =>
      prevNodes.map((n) => {
        if (n.id === node.id) {
          return {
            ...n,
            layer:
              up === true ? n.layer + 1 : n.layer - 1 > 0 ? n.layer - 1 : 0,
          }
        } else {
          return n
        }
      })
    )
  }

  // scale node
  // TODO: enable scaling of nodes when
  //       when autoscaling is disabled
  const handleNodeScale = (nodeID: INode["id"], delta?: number) => {
    if (!delta) return
    updateHistory()
    setNodes((prevNodes) =>
      prevNodes.map((n) => {
        if (n.id === nodeID) {
          return {
            ...n,
            size:
              // 100
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

  // delete node
  const handleNodeDelete = (nodeID: INode["id"]) => {
    updateHistory()
    setNodes((prevNodes) => prevNodes.filter((n) => n.id !== nodeID))
    setRelationships((prevRelationships) =>
      prevRelationships.filter(
        (relationship) =>
          relationship.start.id !== nodeID && relationship.end.id !== nodeID
      )
    )
    setSelectedNodes([])
  }

  const selectNodesBySelectionRect = (node?: INode) => {
    if (!selectionRect) return

    let rectSelectedNodes = nodes.filter((node) => {
      return (
        node.position.x >= selectionRect.left &&
        node.position.x <= selectionRect.left + selectionRect.width &&
        node.position.y >= selectionRect.top &&
        node.position.y <= selectionRect.top + selectionRect.height
      )
    })

    if (node) {
      const alreadySelected = rectSelectedNodes.some(
        (selectedNode) => selectedNode.id === node.id
      )
      if (!alreadySelected) {
        rectSelectedNodes.push(node)
      }
    }

    setSelectedNodes(rectSelectedNodes)
    setSelectionRect(null)
  }

  const copyNodes = () => {
    if (selectedNodes.length > 0) {
    }
  }

  const pasteNodes = () => {}

  // switch node action
  // prevents the need for passing
  // too many functions as props
  const handleNodeAction = (
    node: INode,
    action: string,
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
        // ############# REDO SCALE ############
        // if (typeof value === 'number')
        // handleNodeScale(node.id, value)
        break
      case "connect":
        handleNodeConnect(node)
        break
      case "setNodeVals":
        handleSetNodeVals(node)
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

  // set node selection status
  // 0 = node is not selected
  // 1 = node is selected alone
  // 2 = node is selected among others
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

  // add relationship between two nodes
  // checks for already existing relationships
  // checks for legitimate relationships
  const addRelationship = (start: INode, end: INode) => {
    if (start.id === end.id) return
    const relationshipExists = relationships.some(
      (relationship) =>
        (relationship.start.id === start.id && relationship.end.id === end.id) ||
        (relationship.start.id === end.id && relationship.end.id === start.id)
    )
    if (relationshipExists || !isRelationshipLegitimate(start, end)) {
      toast.error("Relationship invalid!")
      return
    }
    updateHistory()
    const relationshipID = uuidv4().replaceAll("-", "")
    setRelationships((prevRelationships) => [
      ...prevRelationships,
      { start: start, end: end, id: relationshipID },
    ])
  }

  // selects a relationship
  // (will also open relationship context menu)
  const handleRelationshipClick = (relationshipID: IRelationship["id"]) => {
    setSelectedRelationshipID(relationshipID)
    setSelectedNodes([])
    if (navOpen) {
      setNavOpen(false)
      setClickPosition(null)
    }
  }

  // deletes relationship
  const handleRelationshipDelete = (relationshipID: IRelationship["id"]) => {
    updateHistory()
    setRelationships((prevRelationships) =>
      prevRelationships.filter((relationship) => relationship.id !== relationshipID)
    )
  }

  // reverses relationship direction if possible
  const handleRelationshipReverse = (relationshipID: IRelationship["id"]) => {
    setRelationships((prevRelationships) =>
      prevRelationships.map((c) => {
        if (c.id === relationshipID) {
          if (isRelationshipLegitimate(c.end, c.start)) {
            updateHistory()
            return { ...c, start: c.end, end: c.start }
          } else {
            toast.error("Relationship cannot be reversed!")
            return c
          }
        } else {
          return c
        }
      })
    )
  }

  // relationship action switch
  const handleRelationshipAction = (
    relationshipID: IRelationship["id"],
    action: string
  ) => {
    switch (action) {
      case "click":
        handleRelationshipClick(relationshipID)
        break
      case "reverse":
        handleRelationshipReverse(relationshipID)
        break
      case "delete":
        handleRelationshipDelete(relationshipID)
        break
      default:
        break
    }
  }

  const handleLayoutNodes = useCallback(async (setLayouting = true) => {

    if (setLayouting) {
      setIsLayouting(true)

      if (layoutingTimeoutRef.current) {
        clearTimeout(layoutingTimeoutRef.current);
      }
    }

    if (!canvasRect) return

    cytoscape.use(fcose)
    const cy = cytoscape({
      elements: {
        nodes: nodes.map((node) => ({ data: { id: node.id } })),
        edges: relationships.map((relationship) => ({
          data: {
            id: relationship.id,
            source: relationship.start.id,
            target: relationship.end.id,
          },
        })), // Transform relationships to Cytoscape format
      },
      headless: true,
    })

    const layout = cy.layout(graphLayouts[4])

    await new Promise((resolve) => {
      layout.one('layoutstop', resolve)
      layout.run()
    })

    const nodePositions = cy.nodes().map((node) => ({
      id: node.id(),
      position: node.position(),
    }))

    let bounds = {
      minX: Infinity,
      maxX: -Infinity,
      minY: Infinity,
      maxY: -Infinity,
    }

    nodePositions.forEach((node) => {
      if (node.position.x < bounds.minX) bounds.minX = node.position.x
      if (node.position.x > bounds.maxX) bounds.maxX = node.position.x
      if (node.position.y < bounds.minY) bounds.minY = node.position.y
      if (node.position.y > bounds.maxY) bounds.maxY = node.position.y
    })

    const graphWidth = bounds.maxX - bounds.minX
    const graphHeight = bounds.maxY - bounds.minY

    const nodeSize = 100 - (10 * Math.floor(nodes.length / 10))

    const canvasWidth = canvasRect.width - 200
    const canvasHeight = canvasRect.height - nodeSize - 50

    let rotate = false
    if (canvasWidth > canvasHeight) {
      if (graphHeight > graphWidth) rotate = true
    } else {
      if (graphWidth > graphHeight) rotate = true
    }
    
    const scaleX = rotate ? canvasWidth / graphHeight : canvasWidth / graphWidth
    const scaleY = rotate ? canvasHeight / graphWidth : canvasHeight / graphHeight
    const scale = Math.min(Math.min(scaleX, scaleY), 1)



    // ############# handle nodes out of bounds
    // let nodeOutOfBounds = false
    const updatedNodes = nodes.map((node) => {
      const newNode = { ...node } // Copy node to not mutate the original object
      const foundPosition = nodePositions.find((np) => np.id === node.id)
      if (foundPosition) {
        let xPrime, yPrime

        //rotate
        if (rotate) {
          xPrime = -foundPosition.position.y * scale
          yPrime = foundPosition.position.x * scale
        } else {
          xPrime = foundPosition.position.x * scale
          yPrime = foundPosition.position.y * scale
        }

        newNode.position = {
          x: xPrime + canvasWidth / 2 + 100,
          y: yPrime + canvasHeight / 2 + nodeSize / 2 + 25,
        }

        newNode.size = nodeSize

        // ############# handle nodes out of bounds
        // if (
        //   newNode.position.x < newNode.size / 2 + 10 || newNode.position.x > window.innerWidth - (newNode.size / 2) ||
        //   newNode.position.y < newNode.size / 2 || newNode.position.y > window.innerHeight - (newNode.size / 2)
        // ) {
        //   nodeOutOfBounds = true
        // }
      }
      return newNode
    })
    setNodes(updatedNodes)

    layoutingTimeoutRef.current = setTimeout(() => {
      setIsLayouting(false);
    }, 500);

    //add timeout to set islayouting here
  }, [canvasRect, nodes, relationships, setNodes])

  useEffect(() => {
    if (needLayout) {
      handleLayoutNodes(true)
      setNeedLayout(false)
    }
  }, [needLayout, setNeedLayout])

  useEffect(() => {
    const handleCanvasKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === "Z") {
        e.preventDefault()
        redo()
      } else if (e.ctrlKey) {
        setCtrlPressed(true)
        switch (e.key) {
          case "a":
            e.preventDefault()
            setSelectedNodes(nodes)
            break
          case "c":
            e.preventDefault()
            break
          case "d":
            e.preventDefault()
            setSelectedNodes([])
            break
          case "v":
            e.preventDefault()
            break
          case "y":
            e.preventDefault()
            redo()
            break
          case "z":
            e.preventDefault()
            undo()
            break
          default:
            break
        }
      } else if (e.altKey) {
        setAltPressed(true)
      }
    }

    window.addEventListener("keydown", handleCanvasKeyDown)

    return () => {
      window.removeEventListener("keydown", handleCanvasKeyDown)
    }
  }, [undo, redo, nodes, setSelectedNodes])

  const handleCanvasKeyUp = (e: React.KeyboardEvent) => {
    if (e.key === "Alt") {
      e.preventDefault()
      setAltPressed(false)
    }
    if (e.key === "Control") {
      setCtrlPressed(false)
    }
    if (e.key !== "Delete" || (!selectedNodes && !selectedRelationshipID)) return
    updateHistory()
    if (selectedNodes.length > 0) {
      const nodeIDs = new Set(selectedNodes.map((n) => n.id))
      if (!nodeIDs) return
      setNodes((prevNodes) => prevNodes.filter((n) => !nodeIDs.has(n.id)))
      setRelationships((prevRelationships) =>
        prevRelationships.filter(
          (relationship) =>
            !nodeIDs.has(relationship.start.id) && !nodeIDs.has(relationship.end.id)
        )
      )
    } else if (selectedRelationshipID) {
      setRelationships((prevRelationships) =>
        prevRelationships.filter(
          (relationship) => relationship.id !== selectedRelationshipID
        )
      )
      // setRelationships((prevRelationships) =>
      //   prevRelationships.filter((relationship) => relationship.id !== selectedRelationshipID)
      // )
    }
  }

  const handleCanvasMouseDown = (e: React.MouseEvent) => {
    if (!canvasRect || navOpen || e.button === 2) return

    setDragging(true)

    if (e.button === 1 || altPressed) {
      setMovingNodeIDs(new Set(nodes.map((n) => n.id)))
      setDragCurrentPos(mousePosition)
      // initNodeMove()
      return
    }

    setClickPosition(mousePosition)
  }

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (!dragging || !canvasRect) return

    if (dragCurrentPos) {
      const displacement: Vector2D = {
        x: mousePosition.x - dragCurrentPos.x,
        y: mousePosition.y - dragCurrentPos.y,
      }
      if (movingNodeIDs?.size === nodes.length) {
        handleCanvasGrab(displacement)
      } else {
        handleNodeMove(displacement)
      }

      setDragCurrentPos({
        x: mousePosition.x,
        y: mousePosition.y,
      })
    }

    if (!clickPosition) return

    setSelectionRect({
      left: Math.min(clickPosition.x, mousePosition.x),
      top: Math.min(clickPosition.y, mousePosition.y),
      width: Math.abs(mousePosition.x - clickPosition.x),
      height: Math.abs(mousePosition.y - clickPosition.y),
    })
  }

  const handleCanvasMouseUp = (e: React.MouseEvent) => {
    if (e.button === 2) return
    if (e.button !== 1 && !altPressed) setSelectedNodes([])

    setClickPosition(null)
    setMovingNodeIDs(null)
    setSelectedRelationshipID(null)
    cleanupDrag()

    if (selectionRect) {
      selectNodesBySelectionRect()
    } else if (navOpen) {
      setNavOpen(false)
      setConnectingNode(null)
    } else if (connectingNode) {
      if (isConnectableNode(connectingNode.type) && canvasRect) {
        const canvasClickPosition = mousePosition
        setClickPosition(canvasClickPosition)
        setNavOpen(true)
      } else {
        setConnectingNode(null)
        toast.error("No possible relationship!")
      }
    }
  }

  const canvasZoom = useCallback(
    (delta: number, mousePos: Position) => {
      const updatedNodes = nodes.map((node) => {
        const zoomFactor = 1 - 0.1 * delta

        const dx = node.position.x - mousePos.x
        const dy = node.position.y - mousePos.y

        const newNodePosition: Position = {
          x: mousePos.x + dx * zoomFactor,
          y: mousePos.y + dy * zoomFactor,
        }
        return {
          ...node,
          size: node.size * (1 - (delta * 0.1)),
          position: newNodePosition,
        }
      })

      setNodes(updatedNodes)
    },
    [nodes, setNodes]
  )

  useEffect(() => {
    const handleCanvasWheel = (e: WheelEvent) => {
      e.preventDefault()
      if (!canvasRect || nodeEditing) return

      const delta = Math.sign(e.deltaY)

      canvasZoom(delta, mousePosition)
    }

    const canvas = canvasRef.current
    if (!canvas) return

    canvas.addEventListener("wheel", handleCanvasWheel, { passive: false })
    return () => {
      canvas.removeEventListener("wheel", handleCanvasWheel)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canvasRect, canvasZoom])

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault()
    setSelectionRect(null)
    if (canvasRect) {
      const canvasClickPosition = mousePosition
      setClickPosition(canvasClickPosition)
      setNavOpen(true)
    }
    setSelectedNodes([])
    setSelectedRelationshipID(null)
    setConnectingNode(null)
  }

  const handleContextSelect = (type?: INode["type"]) => {
    if (type && clickPosition) {
      addNode(type, clickPosition)
    }
    setNavOpen(false)
    setClickPosition(null)
  }

  const handleButtonSelect = (buttonType: ICanvasButton["type"]) => {
    switch (buttonType) {
      case "undo":
        undo()
        break
      case "redo":
        redo()
        break
      case "reset":
        handleReset()
        break
      case "layout":
        updateHistory()
        handleLayoutNodes()
        break
      case "saveWorkflow":
        saveWorkflow()
        break
    }
  }

  return (
    <div
      className="canvas"
      style={{
        ...style,
        cursor: (dragging && dragCurrentPos) ? "grabbing" : "default",
        backgroundColor: "#1a1b1e",
      }}
      // Selection rectangle
      onMouseDown={handleCanvasMouseDown}
      onMouseMove={handleCanvasMouseMove}
      onMouseUp={handleCanvasMouseUp}
      // Context menu
      onContextMenu={handleContextMenu}
      // Delete stuff
      onKeyUp={handleCanvasKeyUp}
      ref={canvasRef}
      tabIndex={0}
    >
      {/* Relationships */}
      {relationships.map((relationship, i) => {
        const startNode = nodes.find((node) => node.id === relationship.start.id)
        const endNode = nodes.find((node) => node.id === relationship.end.id)
        if (!startNode || !endNode) return null // Skip rendering if nodes are not found
        return (
          <Relationship
            key={i}
            handleRelationshipAction={handleRelationshipAction}
            relationship={{ start: startNode, end: endNode, id: relationship.id }}
            isSelected={relationship.id === selectedRelationshipID}
          />
        )
      })}
      {/* Temp Relationship */}
      {connectingNode && (
        <TempRelationship
          startPosition={connectingNode.position}
          endPosition={clickPosition}
          canvasRect={canvasRect}
        />
      )}
      {/* Nodes */}
      {nodes.map((node) => (
        <Node
          key={node.id}
          node={node}
          isSelected={nodeSelectionStatus(node.id)}
          connecting={Boolean(connectingNode)}
          colorIndex={colorIndex}
          canvasRect={canvasRect}
          mousePosition={mousePosition}
          isMoving={movingNodeIDs !== null && movingNodeIDs.has(node.id)}
          isLayouting={isLayouting}
          // handleNodeMove={handleNodeMove}
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
      <CanvasButtonGroup
        canvasRect={canvasRect}
        onSelect={handleButtonSelect}
      />
      {/* Canvas Context Menu */}
      {navOpen && clickPosition && (
        <div
          style={{
            position: "absolute",
            left: clickPosition.x,
            top: clickPosition.y,
            transform: "translate(-50%, -50%)",
            zIndex: 3,
          }}
        >
          <ContextCanvas
            onSelect={handleContextSelect}
            open={navOpen}
            colorIndex={colorIndex}
            contextRestrict={connectingNode?.type}
            position={clickPosition}
          />
        </div>
      )}
    </div>
  )
}
