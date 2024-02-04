// TODO: favorite nodes

import React, { useState, useRef, useEffect, useCallback } from "react"
import chroma from "chroma-js"
import { useSpring, animated } from "react-spring"

import NodeContext from "./NodeContext"
import NodeInput from "./NodeInput"
import NodeLabel from "./NodeLabel"
import NodeWarning from "./NodeWarning"
// import { NodeLabelOutline } from "./node-label.component"
import NodeConnector from "./NodeConnector"
import { INode, Position, ValOpPair, Vector2D } from "../../../types/canvas.types"
import { colorPalette } from "../../../types/colors"
import { isAttrDefined } from "../../../common/helpers"

interface NodeProps {
  node: INode
  isSelected: number // 1 = solo selected, 2 = multi selected
  connecting: boolean
  colorIndex: number
  canvasRect: DOMRect | null
  mousePosition: Position
  isMoving: boolean
  isLayouting: boolean
  handleNodeAction: (
    node: INode,
    action: string,
    conditional?: boolean
  ) => void
}

export default React.memo(function Node(props: NodeProps) {
  const {
    node,
    isSelected,
    connecting,
    colorIndex,
    canvasRect,
    mousePosition,
    isMoving,
    isLayouting,
    // handleNodeMove,
    handleNodeAction,
  } = props
  const [fieldsMissing, setFieldsMissing] = useState(true)
  const [dragging, setDragging] = useState(false)
  const [dragStartPos, setDragStartPos] = useState<Position | null>(null)
  const [nodeHovered, setNodeHovered] = useState(false)
  const [connectorPos, setConnectorPos] = useState<Position>({ x: 0, y: 0 })
  const [connectorActive, setConnectorActive] = useState(false)
  const [mouseDist, setMouseDist] = useState(0)
  const [mouseAngle, setMouseAngle] = useState(0)
  const [colors, setColors] = useState<string[]>([])
  const [hasLabelOverflow, setHasLabelOverflow] = useState(false)
  const [isValueNode, setIsValueNode] = useState(false)
  const [nodeOptimalSize, setNodeOptimalSize] = useState<number | null>(null)
  const [nodeActualSize, setNodeActualSize] = useState(100)
  const nodeRef = useRef<HTMLDivElement>(null)
  const nodeLabelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new ResizeObserver(() => {
      if (nodeRef.current) {
        const width = nodeRef.current.offsetWidth
        setNodeActualSize(width)
      }
    })

    const currentNode = nodeRef.current
    if (currentNode) {
      observer.observe(currentNode)
    }

    // Cleanup on unmount or if nodeRef changes
    return () => {
      if (currentNode) {
        observer.unobserve(currentNode)
      }
    }
  }, [nodeRef])

  // scale node by mouse wheel
  // useEffect(() => {
  //   const nodeCpy = nodeRef.current
  //   if (!nodeCpy) return

  //   const scaleNode = (e: WheelEvent) => {
  //     e.preventDefault()
  //     if (node.isEditing) return
  //     const delta = Math.sign(e.deltaY)
  //     handleNodeAction(node, "scale", undefined, delta)
  //   }

  //   nodeCpy.addEventListener("wheel", scaleNode, { passive: false })
  //   return () => {
  //     nodeCpy.removeEventListener("wheel", scaleNode)
  //   }
  // }, [node, handleNodeAction])

  // setIsValueNode
  useEffect(() => {
    setIsValueNode(["property", "parameter"].includes(node.type))
  }, [node.type])

  // update missing fields
  useEffect(() => {
    if (isValueNode) {
      setFieldsMissing(!isAttrDefined(node.name) || !isAttrDefined(node.value))
    } else {
      setFieldsMissing(!isAttrDefined(node.name))
    }
  }, [isValueNode, node.name, node.value])

  /* set label overflow
   * 1. based on labelwidth */

  // useEffect(() => {
  //   if (!nodeLabelRef.current) return
  //   setHasLabelOverflow(nodeLabelRef.current.offsetWidth > node.size + 5)
  // }, [nodeLabelRef.current?.offsetWidth, node.size, isSelected])

  /* set label overflow
   * 2. based on characters <-- seems better for now */
  // useEffect(() => {
  //   if (!node.name) return
  //   if (node.name.length > node.size / 9.65) {
  //     setHasLabelOverflow(true)
  //     return
  //   }
  //   if (isValueNode && node.value !== undefined) {
  //     setHasLabelOverflow(node.value.toString().length > (node.size - 20) / 8.2)
  //   }
  // }, [node.name, node.value, node.size, isValueNode])

  // calculate nodeOptimalSize
  useEffect(() => {
    if (!isAttrDefined(node.name)) {
      setNodeOptimalSize(node.size)
      return
    }

    const nameMinimumSize = node.name.length * 11
    let nodeMinimumSize = nameMinimumSize

    if (isValueNode && isAttrDefined(node.value)) {
      const valueMinimumSize = node.value.value.length * 9 + 20
      nodeMinimumSize = Math.max(nodeMinimumSize, valueMinimumSize)
    }

    setNodeOptimalSize(nodeMinimumSize > 100 ? nodeMinimumSize : null)
  }, [node.size, node.name, node.value, isValueNode])

  // setup color array
  useEffect(() => {
    const paletteColors = colorPalette[colorIndex]

    setColors([
      paletteColors[node.type],
      chroma(paletteColors[node.type]).brighten(1).hex(),
      chroma(paletteColors[node.type]).darken(0.5).hex(),
    ])
  }, [node.type, colorIndex])

  // calculate connector stats (position, and active status)
  // is called when mousePos is inside node bounding box
  const calculateConnectorAngle = useCallback((dx: number, dy: number) => {
    const angle = Math.atan2(dy, dx)
    setMouseAngle(angle)
  }, [])

  useEffect(() => {
    const radius = nodeActualSize / 2 + 2

    const connectorPosition = {
      x: nodeActualSize / 2 + radius * Math.cos(mouseAngle),
      y: nodeActualSize / 2 + radius * Math.sin(mouseAngle),
    }

    setConnectorPos(connectorPosition)

    if (mouseDist > nodeActualSize / 2 - 5 && nodeHovered) {
      setConnectorActive(true)
    } else {
      setConnectorActive(false)
    }
  }, [nodeHovered, nodeActualSize, mouseDist, mouseAngle])

  // ################### handleMouseMove ###################
  // check if mousePos is inside node
  // bounding box. if it is, setMouseDist and call calculateConnector
  useEffect(() => {
    if (!canvasRect) return
    if (!connecting) {
      const detectionRadius = 31
      // box detection, mouse inside box -> calculateConnector
      if (
        mousePosition.x >=
          node.position.x - (nodeActualSize / 2 + detectionRadius) &&
        mousePosition.x <=
          node.position.x + (nodeActualSize / 2 + detectionRadius) &&
        mousePosition.y >=
          node.position.y - (nodeActualSize / 2 + detectionRadius) &&
        mousePosition.y <=
          node.position.y + (nodeActualSize / 2 + detectionRadius)
      ) {
        const dx = mousePosition.x - node.position.x
        const dy = mousePosition.y - node.position.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        setMouseDist(dist)
        calculateConnectorAngle(dx, dy)
        return // prevent rewrite of mouseDist
      }
    }
    setMouseDist(1000)
    setConnectorActive(false)
  }, [node, nodeActualSize, canvasRect, connecting, dragging, calculateConnectorAngle, mousePosition])

  // initiate node movement
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 2) return
    if (e.button === 1) {
      setDragging(true)
      return
    }
    e.stopPropagation()
    if (connectorActive && !node.isEditing) {
      handleNodeAction(node, "connect")
    } else {
      if (!canvasRect || node.isEditing) return
      setDragging(true)
      setDragStartPos({ x: node.position.x, y: node.position.y })
      handleNodeAction(node, "initMove")
    }
  }

  // either complete relationship between 2 nodes or
  // open node nav menu (if node hasnt been moved significantly)
  const handleMouseUp = (e: React.MouseEvent) => {
    e.stopPropagation()
    if (connecting) {
      // always carry out node click if a node is trying to connect (favour relationship)
      handleNodeAction(node, "click")
    } else if (
      // carry out node click if node is not trying to connect
      // only when node has not been moved significantly (prevent click after drag)
      dragStartPos &&
      Math.abs(dragStartPos.x - node.position.x) < 5 &&
      Math.abs(dragStartPos.y - node.position.y) < 5
    ) {
      handleNodeAction(node, "click")
      if (fieldsMissing) handleNodeAction(node, "setIsEditing")
    } else if (dragStartPos || e.button === 1) {
      handleNodeAction(node, "completeMove")
    } else if (!dragStartPos) {
      handleNodeAction(node, "click")
    }
    cleanupDrag()
  }

  const handleContextActionLocal = (ctxtAction: string) => {
    handleNodeAction(node, ctxtAction)
  }

  const handleNodeRename = (updatedNode: INode) => {
    handleNodeAction(updatedNode, "setNodeVals")
  }

  const handleNameMouseUp = (e: React.MouseEvent) => {
    if (
      isSelected === 1 &&
      dragStartPos &&
      Math.abs(dragStartPos.x - node.position.x) < 15 &&
      Math.abs(dragStartPos.y - node.position.y) < 15
    ) {
      e.stopPropagation()
      cleanupDrag()
      handleNodeAction(
        node,
        "setIsEditing",
        true
      )
    }
  }

  const cleanupDrag = () => {
    setDragging(false)
    setDragStartPos(null)
  }

  const springProps = useSpring({
    positionTop: node.position.y,
    positionLeft: node.position.x,
    size:
      nodeOptimalSize &&
      ((nodeHovered && mouseDist < 25) || isSelected === 1 || dragging)
        ? nodeOptimalSize
        : node.size,
    config: {
      tension: nodeHovered && mouseDist < 25 ? 1000 : 200,
      friction: 26,
    },
  })

  return (
    <animated.div
      style={{
        position: "absolute",
        width: nodeActualSize + 20,
        height: nodeActualSize + 20,
        top: isLayouting ? springProps.positionTop : node.position.y,
        left: isLayouting ? springProps.positionLeft : node.position.x,
        transform: "translate(-50%,-50%)",
        zIndex: isSelected === 1 ? 1000 : node.layer,
      }}
    >
      {/* node context menu */}
      {isSelected === 1 && (
        <div
          style={{
            position: "absolute",
            top: nodeActualSize / 2 + 10,
            left: nodeActualSize / 2 + 10,
          }}
        >
          <NodeContext
            onSelect={handleContextActionLocal}
            isOpen={isSelected === 1}
            nodeSize={nodeActualSize}
            isEditing={node.isEditing}
            type={node.type}
          />
        </div>
      )}
      {/* clickable node (larger than actual node but not visible) */}
      <animated.div
        style={{
          width: springProps.size.to((size) => size + 20),
          height: springProps.size.to((size) => size + 20),
          cursor: nodeHovered
            ? !dragging
              ? "pointer"
              : "grabbing"
            : "default",
        }}
        className="node-clickable"
        onMouseDown={handleMouseDown} // init relationship
        onMouseUp={handleMouseUp} // handleNodeClick (complete relationship || open node nav)
        onMouseEnter={() => setNodeHovered(true)}
        onMouseLeave={() => setNodeHovered(false)}
        onContextMenu={(e) => {
          e.stopPropagation()
          e.preventDefault()
        }}
        tabIndex={0}
      >
        {/* visible node */}
        <animated.div
          className="node"
          tabIndex={0}
          ref={nodeRef}
          style={{
            width: springProps.size,
            height: springProps.size,
            backgroundColor: colors[0],
            opacity: !fieldsMissing ? 1 : 0.7,
            outlineColor: isSelected > 0 || nodeHovered ? colors[1] : colors[2],
            outlineStyle: "solid",
            outlineWidth: "4px",
            outlineOffset: "-1px",
            zIndex: node.layer,
          }}
        >
          {/* node labels */}
          {!node.isEditing && (
            <NodeLabel
              isSelected={isSelected}
              isValueNode={isValueNode}
              fieldsMissing={fieldsMissing}
              labelRef={nodeLabelRef}
              hovered={nodeHovered}
              size={nodeActualSize}
              name={node.name}
              value={node.value}
              type={node.type}
              layer={node.layer}
              // hasLabelOverflow={hasLabelOverflow}
              color={colors[0]}
              onMouseUp={handleNameMouseUp}
            />
          )}
          {/* node connector */}
          {mouseDist < nodeActualSize / 2 + 30 &&
            mouseDist > 30 &&
            !node.isEditing && (
              <NodeConnector
                nodeSize={nodeActualSize}
                color={colors[1]}
                active={connectorActive}
                position={connectorPos}
                layer={node.layer}
              />
            )}
        </animated.div>
        {/* end of visible */}
        {/* node input fields
         * outside of visible node to not be
         * affected by opacity changes */}
        {node.isEditing && (
          <NodeInput
            isValueNode={isValueNode}
            node={node}
            handleNodeRename={handleNodeRename}
          />
        )}
        {/* node warning */}
        {fieldsMissing &&
          !isSelected &&
          !node.isEditing && ( // warning: !nodeName
            <NodeWarning
              size={nodeActualSize}
              hovered={nodeHovered}
              color={colors[0]}
              layer={node.layer}
            />
          )}
      </animated.div>
      {/* end of clickable */}
    </animated.div> // top
  )
})
