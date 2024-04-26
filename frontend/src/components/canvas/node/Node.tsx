// TODO: favorite nodes

import React, { useState, useRef, useEffect, useCallback } from 'react'
import chroma from 'chroma-js'
import { useSpring, animated } from 'react-spring'

import NodeContext from './NodeContext'
import NodeInput from './NodeInput'
import NodeLabel from './NodeLabel'
import NodeWarning from './NodeWarning'
import NodeConnector from './NodeConnector'
import { INode, Position } from '../../../types/canvas.types'
import { colorPalette } from '../../../types/colors'
import { isAttrDefined } from '../../../common/workflowHelpers'
import { getIsValueNode } from '../../../common/nodeHelpers'
import _ from 'lodash'

interface NodeProps {
    node: INode
    isSelected: number // 1 = solo selected, 2 = multi selected
    isHighlighted: boolean
    isLayouting: boolean
    connecting: boolean
    canvasRect: DOMRect | null
    mousePosition: Position | null
    darkTheme: boolean
    initNodeMove: (nodeId: INode['id']) => void
    handleNodeAction: (node: INode, action: string, conditional?: any) => void
}

export default React.memo(function Node(props: NodeProps) {
    const {
        node,
        isSelected,
        isHighlighted,
        connecting,
        canvasRect,
        mousePosition,
        isLayouting,
        darkTheme,
        initNodeMove,
        handleNodeAction,
    } = props

    // Node general
    const [nodeRenderedSize, setNodeRenderedSize] = useState(100)
    const [isHovered, setIsHovered] = useState(false)
    const [isValueNode, setIsValueNode] = useState(false)
    const [fieldsMissing, setFieldsMissing] = useState(true)
    const [colors, setColors] = useState<string[]>([])

    // Node movement parameters
    const [dragging, setDragging] = useState(false)
    const [dragStartPos, setDragStartPos] = useState<Position | null>(null)

    // Node connector parameters
    const [connectorPos, setConnectorPos] = useState<Position>({ x: 0, y: 0 })
    const [connectorVisible, setConnectorVisible] = useState(false)
    const [connectorActive, setConnectorActive] = useState(false)
    const [mouseDist, setMouseDist] = useState(0)
    const [mouseAngle, setMouseAngle] = useState(0)

    // Node refs
    const nodeRef = useRef<HTMLDivElement>(null)
    const nodeLabelRef = useRef<HTMLDivElement>(null)

    // ############################################################################## Mouse position
    // calculate mouse distance and connector angle
    useEffect(() => {
        if (!(canvasRect && mousePosition)) return
        if (!connecting) {
            const dx = mousePosition.x - node.position.x
            const dy = mousePosition.y - node.position.y
            const dist = Math.sqrt(dx * dx + dy * dy)
            setMouseDist(dist)
            calculateMouseAngle(dx, dy)
        } else {
            setMouseDist(1000)
            setConnectorActive(false)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [canvasRect, connecting, mousePosition])

    const calculateMouseAngle = (dx: number, dy: number) => {
        const angle = Math.atan2(dy, dx)
        setMouseAngle(angle)
    }

    // calculate connector position
    useEffect(() => {
        const radius = nodeRenderedSize / 2 + 2

        const connectorPosition = {
            x: nodeRenderedSize / 2 + radius * Math.cos(mouseAngle),
            y: nodeRenderedSize / 2 + radius * Math.sin(mouseAngle),
        }

        setConnectorPos(connectorPosition)
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [mouseDist, nodeRenderedSize])

    // calculate connector visibility and active status
    useEffect(() => {
        if (mouseDist > 30 && mousePosition) {
            setConnectorVisible(true)
            if (isHovered && mouseDist > nodeRenderedSize / 2 - 5) {
                setConnectorActive(true)
            } else {
                setConnectorActive(false)
            }
        } else {
            setConnectorActive(false)
            setConnectorVisible(false)
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [mouseDist, mousePosition])

    // calculate node rendered size (the current size of the rendered node)
    useEffect(() => {
        if (!nodeRef.current) return

        const throttledObservation = _.throttle(() => {
            if (nodeRef.current) {
                setNodeRenderedSize(nodeRef.current.offsetWidth)
            }
        }, 15)

        const resizeObserver = new ResizeObserver(() => {
            throttledObservation()
        })

        resizeObserver.observe(nodeRef.current)

        return () => {
            resizeObserver.disconnect()
            throttledObservation.cancel()
        }
    }, [nodeRef, mousePosition, isSelected])

    // ################################################################################ Mouse clicks
    // initiate node movement
    const handleMouseDown = (e: React.MouseEvent) => {
        if (e.button === 2) return
        if (e.button === 1) {
            setDragging(true)
            return
        }
        e.stopPropagation()
        if (connectorActive && !node.isEditing) {
            handleNodeAction(node, 'connect')
        } else {
            if (!canvasRect || node.isEditing) return
            setDragging(true)
            setDragStartPos({ x: node.position.x, y: node.position.y })
            initNodeMove(node.id)
        }
    }

    // either complete relationship between 2 nodes or
    // open node nav menu (if node hasnt been moved significantly)
    const handleMouseUp = (e: React.MouseEvent) => {
        e.stopPropagation()
        if (connecting) {
            // always carry out node click if a node is trying to connect (favour relationship)
            handleNodeAction(node, 'click')
        } else if (
            // carry out node click if node is not trying to connect
            // only when node has not been moved significantly (prevent click after drag)
            dragStartPos &&
            Math.abs(dragStartPos.x - node.position.x) < 5 &&
            Math.abs(dragStartPos.y - node.position.y) < 5
        ) {
            handleNodeAction(node, 'click')
            if (fieldsMissing) handleNodeAction(node, 'setIsEditing')
        } else if (dragStartPos || e.button === 1) {
            handleNodeAction(node, 'completeMove')
        } else if (!dragStartPos) {
            handleNodeAction(node, 'click')
        }
        cleanupDrag()
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
            handleNodeAction(node, 'setIsEditing', true)
        }
    }

    // ####################################################################################### Stuff

    useEffect(() => {
        const result = getIsValueNode(node.type)
        setIsValueNode(result)
    }, [node.type])

    // Update missing fields
    useEffect(() => {
        if (isValueNode) {
            setFieldsMissing(!isAttrDefined(node.name.value) || !isAttrDefined(node.value.valOp))
        } else {
            setFieldsMissing(!isAttrDefined(node.name.value))
        }
    }, [node.name, node.value, isValueNode])

    // Handle context menu action (e.g. delete node)
    const handleContextActionLocal = (ctxtAction: string) => {
        handleNodeAction(node, ctxtAction)
    }

    // Update node attributes
    const handleNodeUpdate = useCallback(
        (updatedNode: INode, endEditing?: boolean) => {
            handleNodeAction(updatedNode, 'nodeUpdate', endEditing)
        },
        [handleNodeAction]
    )

    // Cleanup node movement parameters
    const cleanupDrag = () => {
        setDragging(false)
        setDragStartPos(null)
    }

    // ####################################################################### Colors and animations
    // setup color array
    useEffect(() => {
        const colorIndex = darkTheme ? 0 : 1
        const paletteColors = colorPalette[colorIndex]

        setColors([
            paletteColors[node.type],
            chroma(paletteColors[node.type]).brighten(1).hex(),
            chroma(paletteColors[node.type]).darken(0.5).hex(),
        ])
    }, [node.type, darkTheme])

    const springProps = useSpring({
        positionTop: node.position.y,
        positionLeft: node.position.x,
        size:
            node.optimalSize && isSelected === 1
                ? node.optimalSize
                : node.size,
        config: {
            tension: isHovered && mouseDist < 25 ? 1000 : 200,
            friction: 26,
        },
    })

    // const [springProps, setSpringProps] = useSpring(() => ({
    //     positionTop: node.position.y,
    //     positionLeft: node.position.x,
    //     size:
    //         node.optimalSize && isSelected === 1
    //             ? node.optimalSize
    //             : node.size,
    //     config: {
    //         tension: isHovered && mouseDist < 25 ? 1000 : 200,
    //         friction: 26,
    //     },
    // }))

    // useEffect(() => {
    //     // console.log(node.optimalSize)
    //     setSpringProps({
    //         size:             node.optimalSize && isSelected === 1
    //         ? node.optimalSize
    //         : node.size,
    //     })
    // }, [node, isSelected, setSpringProps])

    // ######################################################################################## HTML
    return (
        <animated.div
            style={{
                position: 'absolute',
                top: isLayouting ? springProps.positionTop : node.position.y,
                left: isLayouting ? springProps.positionLeft : node.position.x,
                transform: 'translate(-50%,-50%)',
                zIndex: isSelected === 1 ? 1000 : node.layer,
            }}
        >
            {/* node context menu */}
            {isSelected === 1 && (
                <div
                    style={{
                        position: 'absolute',
                    }}
                >
                    <NodeContext
                        onSelect={handleContextActionLocal}
                        isOpen={isSelected === 1}
                        nodeSize={nodeRenderedSize}
                        isEditing={node.isEditing}
                        type={node.type}
                        darkTheme={darkTheme}
                    />
                </div>
            )}
            {/* clickable node (larger than actual node but not visible) */}
            <animated.div
                style={{
                    width: springProps.size.to((size) => size + 20),
                    height: springProps.size.to((size) => size + 20),
                    cursor: isHovered ? (!dragging ? 'pointer' : 'grabbing') : 'default',
                }}
                className="node-clickable"
                onMouseDown={handleMouseDown} // init relationship
                onMouseUp={handleMouseUp} // handleNodeClick (complete relationship || open node nav)
                onMouseEnter={() => {
                    setIsHovered(true)
                }}
                onMouseLeave={() => {
                    setIsHovered(false)
                }}
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
                        outlineColor:
                            isSelected > 0 || isHovered || isHighlighted ? colors[1] : colors[2],
                        outlineStyle: 'solid',
                        outlineWidth: '4px',
                        outlineOffset: isHighlighted && isSelected === 0 ? '3px' : '-1px',
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
                            hovered={isHovered}
                            size={nodeRenderedSize}
                            name={node.name.value}
                            valOp={node.value.valOp}
                            type={node.type}
                            layer={node.layer}
                            // hasLabelOverflow={hasLabelOverflow}
                            color={colors[0]}
                            onMouseUp={handleNameMouseUp}
                        />
                    )}
                    {/* node connector */}
                    {connectorVisible && (
                            <NodeConnector
                                nodeSize={nodeRenderedSize}
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
                        handleNodeUpdate={handleNodeUpdate}
                    />
                )}
                {/* node warning */}
                {fieldsMissing &&
                    !isSelected &&
                    !node.isEditing && ( // warning: !nodeName
                        <NodeWarning
                            size={node.size}
                            hovered={isHovered}
                            color={colors[0]}
                            layer={node.layer}
                        />
                    )}
            </animated.div>
            {/* end of clickable */}
        </animated.div> // top
    )
})
