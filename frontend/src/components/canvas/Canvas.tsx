// TODO: copy - paste?

import React, { useState, useRef, useEffect, useCallback, useContext } from 'react'
import { v4 as uuidv4 } from 'uuid'
import cytoscape from 'cytoscape'
import fcose from 'cytoscape-fcose'
import _ from 'lodash'
import { toast } from 'react-hot-toast'
import { useMantineColorScheme } from '@mantine/core'

import ContextCanvas from './CanvasContext'
import Node from './node/Node'
import Relationship, { TempRelationship } from './relationship/Relationship'
import {
    Rect,
    INode,
    IRelationship,
    Position,
    Vector2D,
    ICanvasButton,
} from '../../types/canvas.types'
import { graphLayouts } from '../../types/canvas.graphLayouts'
import {
    calculateNodeOptimalSize,
    isConnectableNode,
    isRelationshipLegitimate,
} from '../../common/nodeHelpers'
import CanvasButtonGroup from './CanvasButtonGroup'
import WorkflowContext from '../workflow/context/WorkflowContext'

const DETECTION_RADIUS = 31

interface CanvasProps {
    nodesFn: {
        nodes: INode[]
        relationships: IRelationship[]
        setNodes: React.Dispatch<React.SetStateAction<INode[]>>
        setRelationships: React.Dispatch<React.SetStateAction<IRelationship[]>>
        selectedNodes: INode[]
        setSelectedNodes: React.Dispatch<React.SetStateAction<INode[]>>
        highlightedNodeIds: Set<string> | null
        nodeEditing: boolean
        setNodeEditing: React.Dispatch<React.SetStateAction<boolean>>
    }
    indexFn: {
        rebuildIndexDictionary: () => void
        updateIndexDictionary: (node: INode) => void
    }
    saveWorkflow: () => void
    historyFn: {
        updateHistory: () => void
        updateHistoryWithCaution: () => void
        updateHistoryRevert: () => void
        updateHistoryComplete: () => void
        handleReset: () => void
        undo: () => void
        redo: () => void
    }
    needLayout: boolean
    setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
    style?: React.CSSProperties
    canvasRect: DOMRect
}

export default function Canvas(props: CanvasProps) {
    const { saveWorkflow, needLayout, setNeedLayout, style, canvasRect } = props

    const {
        nodes,
        relationships,
        setNodes,
        setRelationships,
        selectedNodes,
        setSelectedNodes,
        highlightedNodeIds,
        nodeEditing,
        setNodeEditing,
    } = props.nodesFn

    const {
        updateHistory,
        updateHistoryWithCaution,
        updateHistoryRevert,
        updateHistoryComplete,
        handleReset,
        undo,
        redo,
    } = props.historyFn

    const { rebuildIndexDictionary, updateIndexDictionary } = props.indexFn

    // Canvas
    const [navOpen, setNavOpen] = useState(false)
    const [isLayouting, setIsLayouting] = useState(false)
    const [mousePosition, setMousePosition] = useState<Position>({ x: 0, y: 0 })
    const [clickPosition, setClickPosition] = useState<Position | null>(null)
    const [selectionRect, setSelectionRect] = useState<Rect | null>(null)
    const [dragging, setDragging] = useState(false)
    const [dragCurrentPos, setDragCurrentPos] = useState<Position | null>(null)
    const [altPressed, setAltPressed] = useState(false)
    const [ctrlPressed, setCtrlPressed] = useState(false)

    // Nodes
    const [interestingNodeIds, setInterestingNodeIds] = useState<Set<string>>(new Set())
    const [movingNodeIds, setMovingNodeIds] = useState<Set<string> | null>(null)
    const [connectingNode, setConnectingNode] = useState<INode | null>(null)

    // Relationships
    const [selectedRelationshipID, setSelectedRelationshipID] = useState<
        IRelationship['id'] | null
    >(null)

    // Refs
    const selectionRectRef = useRef(selectionRect)
    const mousePositionRef = useRef(mousePosition)
    const canvasRef = useRef<HTMLDivElement>(null)
    const layoutingTimeoutRef = useRef<NodeJS.Timeout | null>(null)

    const { forceEndEditing, uploadMode } = useContext(WorkflowContext)

    // ########################################################################## Mousemove listener
    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (!canvasRect) return

            const mousePosition: Position = {
                x: e.clientX,
                y: e.clientY - canvasRect.top,
            }

            setMousePosition(mousePosition)

            const newInterestingNodeIDs = new Set<string>()

            // Don't pass mouse position if currently moving nodes
            if (dragging) {
                setInterestingNodeIds(newInterestingNodeIDs)
                return
            }

            // Perform box check on all nodes to create list
            // of nodes that receive mouse position
            nodes.forEach((node) => {
                if (
                    mousePosition.x >=
                        node.position.x - (node.optimalSize / 2 + DETECTION_RADIUS) &&
                    mousePosition.x <=
                        node.position.x + (node.optimalSize / 2 + DETECTION_RADIUS) &&
                    mousePosition.y >=
                        node.position.y - (node.optimalSize / 2 + DETECTION_RADIUS) &&
                    mousePosition.y <= node.position.y + (node.optimalSize / 2 + DETECTION_RADIUS)
                ) {
                    newInterestingNodeIDs.add(node.id)
                }
            })

            setInterestingNodeIds(newInterestingNodeIDs)
        }

        const throttledHandleMouseMove = _.throttle(handleMouseMove, 10)

        window.addEventListener('mousemove', throttledHandleMouseMove)
        return () => {
            window.removeEventListener('mousemove', throttledHandleMouseMove)
        }
    }, [canvasRect, nodes, dragging])

    useEffect(() => {
        mousePositionRef.current = mousePosition
    }, [mousePosition])

    // ################################################################################ Create node
    // AddNode from canvas context menu
    // if created from connector, automatically
    // add relationship between nodes
    const addNode = (type: INode['type'], position: Position) => {
        const id = uuidv4().replaceAll('-', '')
        const layer = 0
        const size = 100
        const optimalSize = 100
        const newNode = {
            id,
            name: { value: '', index: '' },
            value: { valOp: { value: '', operator: '' }, index: '' },
            batch_num: { value: '', index: '' },
            ratio: { valOp: { value: '', operator: '' }, index: '' },
            concentration: { valOp: { value: '', operator: '' }, index: '' },
            unit: { value: '', index: '' },
            std: { valOp: { value: '', operator: '' }, index: '' },
            error: { valOp: { value: '', operator: '' }, index: '' },
            identifier: { value: '', index: '' },
            type,
            withIndices: uploadMode,
            position,
            size,
            optimalSize,
            layer,
            isEditing: true,
        }
        if (connectingNode) {
            addRelationship(connectingNode, newNode)
        } else {
            updateHistory()
        }
        setNodeEditing(true)
        setNodes((prevNodes) => [...prevNodes, newNode])
    }

    // ######################################################################### Create relationship
    // add relationship between two nodes
    // checks for already existing relationships
    // checks for legitimate relationships
    const addRelationship = useCallback(
        (start: INode, end: INode) => {
            if (start.id === end.id) return
            const relationshipExists = relationships.some(
                (relationship) =>
                    (relationship.start.id === start.id && relationship.end.id === end.id) ||
                    (relationship.start.id === end.id && relationship.end.id === start.id)
            )
            if (relationshipExists || !isRelationshipLegitimate(start, end)) {
                toast.error('Relationship invalid!')
                return
            }
            updateHistory()
            const relationshipID = uuidv4().replaceAll('-', '')
            setRelationships((prevRelationships) => [
                ...prevRelationships,
                { start: start, end: end, id: relationshipID },
            ])
        },
        [relationships, setRelationships, updateHistory]
    )

    // ################################################################################ Node actions
    // set node selection status
    // 0 = node is not selected
    // 1 = node is selected alone
    // 2 = node is selected among others
    const nodeSelectionStatus = useCallback(
        (nodeId: string) => {
            const isSelected = selectedNodes.some((selectedNode) => selectedNode.id === nodeId)
            if (isSelected) {
                if (selectedNodes.length > 1) return 2
                return 1
            }
            return 0
        },
        [selectedNodes]
    )

    const selectNodesBySelectionRect = useCallback(
        (node?: INode) => {
            if (!selectionRectRef.current) return

            const newSelectionRect = selectionRectRef.current

            let rectSelectedNodes = nodes.filter((node) => {
                return (
                    node.position.x >= newSelectionRect.left &&
                    node.position.x <= newSelectionRect.left + newSelectionRect.width &&
                    node.position.y >= newSelectionRect.top &&
                    node.position.y <= newSelectionRect.top + newSelectionRect.height
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
        },
        [nodes, setSelectedNodes]
    )

    // Sets node isEditing field
    // so input field will show
    const initNodeUpdate = useCallback(
        (nodeID: INode['id'], undoHistory?: boolean) => {
            cleanupDrag()
            if (nodeEditing || ctrlPressed) return
            if (undoHistory) updateHistoryRevert()

            setNodes((prevNodes) =>
                prevNodes.map((node) => (node.id === nodeID ? { ...node, isEditing: true } : node))
            )
            setNodeEditing(true)
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [nodeEditing, ctrlPressed, updateHistoryRevert, setNodes, setNodeEditing]
    )

    // Update node attributes
    const handleNodeUpdate = useCallback(
        (node: INode, endEditing?: boolean) => {
            setNodes((prevNodes) =>
                prevNodes.map((n) => {
                    if (n.id === node.id) {
                        const updatedNode = {
                            ...node,
                            isEditing: endEditing ? false : true,
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
                            // recalculate node optimal size if relevant
                            // attributes or parameters have changed
                            updatedNode.optimalSize = calculateNodeOptimalSize(
                                node.size,
                                node.name,
                                node.value,
                            )
                            // Call updateHistory only if a change has occurred
                            updateHistory()
                        }
                        return updatedNode
                    }
                    return n
                })
            )
            updateIndexDictionary(node)
            if (endEditing) {
                setNodeEditing(false)
            } else {
                setSelectedNodes([node])
            }
        },
        [setNodeEditing, setNodes, setSelectedNodes, updateHistory, updateIndexDictionary]
    )

    // useEffect(() => {
    //     nodes.map((node) => console.log(node.optimalSize))
    // }, [nodes])

    // Initialize node movement
    // mainly prevents unwanted actions
    // like moving nodes that are not involved
    const initNodeMove = useCallback(
        (nodeId: INode['id']) => {
            updateHistoryWithCaution()
            setConnectingNode(null)
            setNavOpen(false)
            setClickPosition(null)
            setDragging(true)
            setDragCurrentPos(mousePositionRef.current)
            if (altPressed) {
                setMovingNodeIds(new Set(nodes.map((n) => n.id)))
            } else {
                switch (nodeSelectionStatus(nodeId)) {
                    // 0 not selected; 1 selected alone; 2 selected among others
                    case 0:
                        if (ctrlPressed) {
                            setMovingNodeIds(new Set(selectedNodes.map((n) => n.id)))
                            return
                        }
                        setSelectedNodes([])
                        setMovingNodeIds(new Set([nodeId]))
                        break
                    case 1:
                        setMovingNodeIds(new Set([nodeId]))
                        break
                    case 2:
                        setMovingNodeIds(new Set(selectedNodes.map((n) => n.id)))
                        break
                    default:
                        return
                }
            }
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [
            altPressed,
            ctrlPressed,
            nodeSelectionStatus,
            nodes,
            selectedNodes,
            setSelectedNodes,
            updateHistoryWithCaution,
        ]
    )

    // Actual node movement
    // TODO: rethink node movement performance
    const handleNodeMove = _.throttle((displacement: Vector2D) => {
        if (!movingNodeIds) return
        setNodes((prevNodes) =>
            prevNodes.map((n) =>
                movingNodeIds.has(n.id)
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
    }, 10)

    // Finalize node movement
    // saves movement to history
    // -> action can be undone and redone properly
    const completeNodeMove = useCallback(() => {
        cleanupDrag()
        updateHistoryComplete()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [updateHistoryComplete])

    const cleanupDrag = () => {
        setClickPosition(null)
        setDragging(false)
        setDragCurrentPos(null)
    }

    // Move all nodes
    const handleCanvasGrab = _.throttle((displacement: Vector2D) => {
        setNodes((prevNodes) =>
            prevNodes.map((n) => ({
                ...n,
                position: {
                    x: n.position.x + displacement.x,
                    y: n.position.y + displacement.y,
                },
            }))
        )
    }, 10)

    // handle click (release) on node
    // adds relationship if connecting from other node
    // selects node (will also open node context)
    const handleNodeClick = useCallback(
        (node: INode) => {
            cleanupDrag()
            if (selectionRectRef.current) {
                // if selection rect is set, do not perform regular
                // node click but complete selection rect node selection
                selectNodesBySelectionRect(node)
            } else if (connectingNode) {
                addRelationship(connectingNode, node)
                setConnectingNode(null)
            } else {
                // prevent node click when edit form is open
                if (nodeEditing) {
                    forceEndEditing()
                    return
                }
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
                                selectedNodes.filter((selectedNode) => selectedNode.id !== node.id)
                            )
                            return
                        }
                        setSelectedNodes([node])
                        break
                    default:
                        return
                }
            }
        },
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [
            connectingNode,
            selectNodesBySelectionRect,
            addRelationship,
            nodeEditing,
            updateHistoryRevert,
            nodeSelectionStatus,
            forceEndEditing,
            navOpen,
            setSelectedNodes,
            ctrlPressed,
            selectedNodes,
        ]
    )

    // initialize node relationship
    // -> mouse needs to be released on another node
    //    to create a relationship
    const handleNodeConnect = useCallback((node: INode) => {
        setNavOpen(false)
        setClickPosition(null)
        setSelectedNodes([])
        setSelectedRelationshipID(null)
        setConnectingNode(node)
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    // Delete node
    const handleNodeDelete = useCallback(
        (nodeID: INode['id']) => {
            updateHistory()
            setNodes((prevNodes) => prevNodes.filter((n) => n.id !== nodeID))
            setRelationships((prevRelationships) =>
                prevRelationships.filter(
                    (relationship) =>
                        relationship.start.id !== nodeID && relationship.end.id !== nodeID
                )
            )
            setSelectedNodes([])
            rebuildIndexDictionary()
        },
        [updateHistory, setNodes, setRelationships, setSelectedNodes, rebuildIndexDictionary]
    )

    const isNodeHighlighted = (nodeId: string) => {
        const isHighlighted = highlightedNodeIds?.has(nodeId)

        return isHighlighted === true
    }

    const handleNodeAction = useCallback(
        (node: INode, action: string, conditional?: any) => {
            switch (action) {
                case 'click':
                    handleNodeClick(node)
                    break
                case 'completeMove':
                    completeNodeMove()
                    break
                case 'connect':
                    handleNodeConnect(node)
                    break
                case 'nodeUpdate':
                    handleNodeUpdate(node, conditional)
                    break
                case 'setIsEditing':
                    initNodeUpdate(node.id, conditional)
                    break
                case 'delete':
                    setSelectedNodes([])
                    handleNodeDelete(node.id)
                    break
                default:
                    break
            }
        },
        [
            handleNodeClick,
            completeNodeMove,
            handleNodeConnect,
            handleNodeUpdate,
            initNodeUpdate,
            setSelectedNodes,
            handleNodeDelete,
        ]
    )

    // ######################################################################## Relationship actions
    // selects a relationship
    // (will also open relationship context menu)
    const handleRelationshipClick = (relationshipID: IRelationship['id']) => {
        setSelectedRelationshipID(relationshipID)
        setSelectedNodes([])
        if (navOpen) {
            setNavOpen(false)
            setClickPosition(null)
        }
    }

    // deletes relationship
    const handleRelationshipDelete = (relationshipID: IRelationship['id']) => {
        updateHistory()
        setRelationships((prevRelationships) =>
            prevRelationships.filter((relationship) => relationship.id !== relationshipID)
        )
    }

    // reverses relationship direction if possible
    const handleRelationshipReverse = (relationshipID: IRelationship['id']) => {
        setRelationships((prevRelationships) =>
            prevRelationships.map((c) => {
                if (c.id === relationshipID) {
                    if (isRelationshipLegitimate(c.end, c.start)) {
                        updateHistory()
                        return { ...c, start: c.end, end: c.start }
                    } else {
                        toast.error('Relationship cannot be reversed!')
                        return c
                    }
                } else {
                    return c
                }
            })
        )
    }

    // relationship action switch
    const handleRelationshipAction = (relationshipID: IRelationship['id'], action: string) => {
        switch (action) {
            case 'click':
                handleRelationshipClick(relationshipID)
                break
            case 'reverse':
                handleRelationshipReverse(relationshipID)
                break
            case 'delete':
                handleRelationshipDelete(relationshipID)
                break
            default:
                break
        }
    }

    const handleLayoutNodes = useCallback(
        async (setLayouting = true) => {
            if (setLayouting) {
                setIsLayouting(true)

                if (layoutingTimeoutRef.current) {
                    clearTimeout(layoutingTimeoutRef.current)
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

            const nodeSize = 100 - 10 * Math.floor(nodes.length / 10)

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
                        x: xPrime + canvasWidth / 2 + 100 + canvasRect.left,
                        y: yPrime + canvasHeight / 2 + nodeSize / 2 + 25,
                    }

                    newNode.size = nodeSize
                    newNode.optimalSize = calculateNodeOptimalSize(
                        nodeSize,
                        node.name,
                        node.value,
                    )

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
            rebuildIndexDictionary()

            layoutingTimeoutRef.current = setTimeout(() => {
                setIsLayouting(false)
            }, 500)

            //add timeout to set islayouting here
        },
        [canvasRect, nodes, relationships, setNodes, rebuildIndexDictionary]
    )

    useEffect(() => {
        if (needLayout) {
            setNeedLayout(false)
            setTimeout(() => {
                handleLayoutNodes(true)
            }, 50)
        }
    }, [needLayout, setNeedLayout, handleLayoutNodes])

    useEffect(() => {
        const handleCanvasKeyDown = (e: KeyboardEvent) => {
            if (e.ctrlKey && e.shiftKey && e.key === 'Z') {
                e.preventDefault()
                redo()
            } else if (e.ctrlKey) {
                setCtrlPressed(true)
                switch (e.key) {
                    case 'a':
                        e.preventDefault()
                        setSelectedNodes(nodes)
                        break
                    case 'c':
                        e.preventDefault()
                        break
                    case 'd':
                        e.preventDefault()
                        setSelectedNodes([])
                        break
                    case 'v':
                        e.preventDefault()
                        break
                    case 'y':
                        e.preventDefault()
                        redo()
                        break
                    case 'z':
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

        window.addEventListener('keydown', handleCanvasKeyDown)

        return () => {
            window.removeEventListener('keydown', handleCanvasKeyDown)
        }
    }, [undo, redo, nodes, setSelectedNodes])

    const handleCanvasKeyUp = (e: React.KeyboardEvent) => {
        if (e.key === 'Alt') {
            e.preventDefault()
            setAltPressed(false)
        }
        if (e.key === 'Control') {
            setCtrlPressed(false)
        }
        if (e.key !== 'Delete' || (!selectedNodes && !selectedRelationshipID)) return
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
            rebuildIndexDictionary()
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
            setMovingNodeIds(new Set(nodes.map((n) => n.id)))
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
            if (movingNodeIds?.size === nodes.length) {
                handleCanvasGrab(displacement)
            } else {
                handleNodeMove(displacement)
            }

            setDragCurrentPos({
                x: mousePosition.x,
                y: mousePosition.y,
            })
        }

        // clickPosition is not set when dragging a node
        // but only when dragging on the canvas
        if (!clickPosition) return

        setSelectionRect({
            left: Math.min(clickPosition.x, mousePosition.x),
            top: Math.min(clickPosition.y, mousePosition.y),
            width: Math.abs(mousePosition.x - clickPosition.x),
            height: Math.abs(mousePosition.y - clickPosition.y),
        })
    }

    useEffect(() => {
        selectionRectRef.current = selectionRect
    }, [selectionRect])

    const handleCanvasMouseUp = (e: React.MouseEvent) => {
        if (e.button === 2) return
        if (e.button !== 1 && !altPressed) setSelectedNodes([])

        if (nodeEditing) {
            forceEndEditing()
        }

        setClickPosition(null)
        setMovingNodeIds(null)
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
                toast.error('No possible relationship!')
            }
        }
    }

    const canvasZoom = _.throttle(
        useCallback(
            (delta: number, mousePos: Position) => {
                // console.log('test')
                const updatedNodes = nodes.map((node) => {
                    const zoomFactor = 1 - 0.1 * delta

                    const dx = node.position.x - mousePos.x
                    const dy = node.position.y - mousePos.y

                    const newNodePosition: Position = {
                        x: mousePos.x + dx * zoomFactor,
                        y: mousePos.y + dy * zoomFactor,
                    }

                    const nodeSize = node.size * (1 - delta * 0.1)
                    const nodeOptimalSize = calculateNodeOptimalSize(
                        nodeSize,
                        node.name,
                        node.value,
                    )
                    return {
                        ...node,
                        size: nodeSize,
                        optimalSize: nodeOptimalSize,
                        position: newNodePosition,
                    }
                })

                setNodes(updatedNodes)
            },
            [nodes, setNodes]
        ),
        1000
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

        canvas.addEventListener('wheel', handleCanvasWheel, { passive: false })
        return () => {
            canvas.removeEventListener('wheel', handleCanvasWheel)
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

    const handleContextSelect = (type?: INode['type']) => {
        if (type && clickPosition) {
            addNode(type, clickPosition)
        }
        setNavOpen(false)
        setClickPosition(null)
    }

    const handleButtonSelect = (buttonType: ICanvasButton['type']) => {
        switch (buttonType) {
            case 'undo':
                undo()
                break
            case 'redo':
                redo()
                break
            case 'reset':
                handleReset()
                break
            case 'layout':
                updateHistory()
                handleLayoutNodes()
                break
            case 'saveWorkflow':
                saveWorkflow()
                break
        }
    }

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'

    return (
        <div
            className="canvas"
            style={{
                ...style,
                cursor: dragging && dragCurrentPos ? 'grabbing' : 'default',
                backgroundColor: darkTheme ? '#1a1b1e' : '#f8f9fa',
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
            {/* Grid */}
            {/* <CanvasGrid
        canvasRect={canvasRect}
      /> */}

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
                    isHighlighted={isNodeHighlighted(node.id)}
                    connecting={Boolean(connectingNode)}
                    canvasRect={canvasRect}
                    mousePosition={interestingNodeIds.has(node.id) ? mousePosition : null}
                    isLayouting={isLayouting}
                    darkTheme={darkTheme}
                    initNodeMove={initNodeMove}
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
            <CanvasButtonGroup canvasRect={canvasRect} onSelect={handleButtonSelect} />
            {/* Canvas Context Menu */}
            {navOpen && clickPosition && (
                <div
                    style={{
                        position: 'absolute',
                        left: clickPosition.x,
                        top: clickPosition.y,
                        transform: 'translate(-50%, -50%)',
                        zIndex: 3,
                    }}
                >
                    <ContextCanvas
                        onSelect={handleContextSelect}
                        open={navOpen}
                        contextRestrict={connectingNode?.type}
                        position={clickPosition}
                    />
                </div>
            )}
        </div>
    )
}
