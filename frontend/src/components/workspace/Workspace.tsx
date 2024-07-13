import React, { useCallback, useContext, useEffect, useRef, useState } from 'react'
import { useSpring, animated } from 'react-spring'
import { useMantineColorScheme } from '@mantine/core'
import { useQuery } from 'react-query'

import Canvas from '../canvas/Canvas'
import WorkspaceButtons from './WorkspaceButtons'
import WorkspaceJson from './WorkspaceJson'
import WorkspaceHistory from './WorkspaceHistory'
import WorkspaceDrawer from './WorkspaceDrawer'
import { TRelationship, TNode, IndexDictionary } from '../../types/canvas.types'
import { convertToJSONFormat, getNodeIndices } from '../../common/workspaceHelpers'
import toast from 'react-hot-toast'
import { WorkspaceTableContext } from '../../context/WorkspaceContext'
import _ from 'lodash'
import { UserContext } from '../../context/UserContext'
import WorkspaceDrawerHandle from './WorkspaceDrawerHandle'
import WorkspaceSearch from './WorkspaceSearch'
import { fetchUploads, fetchGraphs, saveGraph, fetchUpload } from '../../common/clientHelpers'
import { Upload } from '../../types/workspace.types'
import { getLocalStorageItem, setLocalStorageItem } from '../../common/localStorageHelpers'

const UNDO_STEPS = 200

interface WorkspaceProps {
    uploadMode: boolean
}

export default function Workspace(props: WorkspaceProps) {
    const user = useContext(UserContext)
    const { uploadMode } = props

    const [nodes, setNodes] = useState<TNode[]>([])
    const [relationships, setRelationships] = useState<TRelationship[]>([])
    const [selectedNodes, setSelectedNodes] = useState<TNode[]>([])
    const [highlightedNodeIds, setHighlightedNodeIds] = useState<Set<string> | null>(null)
    const [nodeEditing, setNodeEditing] = useState(false)
    const nodesFn = {
        nodes,
        setNodes,
        relationships,
        setRelationships,
        selectedNodes,
        setSelectedNodes,
        highlightedNodeIds,
        nodeEditing,
        setNodeEditing,
    }

    const [graph, setGraph] = useState<string | null>(null)
    const [graphProcessing, setGraphProcessing] = useState(false)
    let setGraphRef: React.MutableRefObject<
        _.DebouncedFunc<(nodes: TNode[], relationships: TRelationship[]) => void> | undefined
    > = React.useRef()

    const [upload, setUpload] = useState<Upload>()
    const [uploadProcessing, setUploadProcessing] = useState<Set<string>>(new Set())

    const [highlightedColumnIndex, setHighlightedColumnIndex] = useState<number | null>(null)
    const [selectedColumnIndex, setSelectedColumnIndex] = useState<number | null>(null)
    const [indexDictionary, setIndexDictionary] = useState<IndexDictionary>({})

    const [needLayout, setNeedLayout] = useState(false)

    const [history, setHistory] = useState<{
        nodes: TNode[][]
        relationships: TRelationship[][]
    }>({ nodes: [], relationships: [] })
    const [future, setFuture] = useState<{
        nodes: TNode[][]
        relationships: TRelationship[][]
    }>({ nodes: [], relationships: [] })

    const [canvasRect, setCanvasRect] = useState<DOMRect>(new DOMRect())
    const workspaceWindowRef = useRef<HTMLDivElement>(null)
    const [workspaceWindowRect, setWorkspaceWindowRect] = useState<DOMRect | null>(null)

    const [jsonView, setJsonView] = useState(false)
    const [jsonViewWidth, setJsonViewWidth] = useState(0)
    const [historyView, setHistoryView] = useState(false)
    const [historyViewWidth, setHistoryViewWidth] = useState(0)
    const [tableView, setTableView] = useState(false)
    const [tableViewHeight, setTableViewHeight] = useState(0)
    const drawerHandleActiveRef = useRef(false)

    const [progress, setProgress] = useState<number>(0)

    useEffect(() => {
        if (!uploadMode) {
            setUpload(undefined)
            setProgress(0)
        }
    }, [uploadMode])

    // GRAPH STUFF ########################################################

    // set current graph (and show in json viewer)
    if (!setGraphRef.current) {
        setGraphRef.current = _.throttle(
            (nodes: TNode[], relationships: TRelationship[]) => {
                setGraph(convertToJSONFormat(nodes, relationships, true))
            },
            1000,
            { trailing: true }
        ) // Trailing: true ensures the last call in a trailing edge is executed
    }

    useEffect(() => {
        if (setGraphRef.current) {
            setGraphRef.current(nodes, relationships)
        }
    }, [nodes, relationships])

    async function setGraphLocal() {
        setGraph('')
        const graph = convertToJSONFormat(nodes, relationships, true)

        try {
            await saveGraph(graph)

            setGraph(graph)
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // WINDOW STUFF ########################################################

    useEffect(() => {
        if (workspaceWindowRect) {
            const width = workspaceWindowRect.width - jsonViewWidth - historyViewWidth
            const height = workspaceWindowRect.height - (tableView ? tableViewHeight : 0)

            setCanvasRect(new DOMRect(historyViewWidth, workspaceWindowRect.top, width, height))

            // setCanvasWidth(width)
            // setCanvasHeight(height)
        }
    }, [workspaceWindowRect, jsonViewWidth, historyViewWidth, tableViewHeight, tableView])

    // Resize Observer for workspace window
    useEffect(() => {
        const resizeObserver = new ResizeObserver(() => {
            if (workspaceWindowRef.current) {
                setWorkspaceWindowRect(workspaceWindowRef.current.getBoundingClientRect())
            }
        })

        const currentWorkspace = workspaceWindowRef.current
        if (currentWorkspace) {
            resizeObserver.observe(currentWorkspace)
        }

        return () => {
            if (currentWorkspace) {
                resizeObserver.unobserve(currentWorkspace)
            }
        }
    }, [workspaceWindowRef])

    const handleSplitView = (view: String) => {
        switch (view) {
            case 'json':
                if (jsonView) {
                    setJsonViewWidth(0)
                } else {
                    setJsonViewWidth(450)
                }
                setJsonView(!jsonView)
                break
            case 'history':
                if (historyView) {
                    setHistoryViewWidth(0)
                } else {
                    setHistoryViewWidth(300)
                }
                setHistoryView(!historyView)
                break
            case 'table':
                if (!tableView && tableViewHeight === 0) {
                    setLocalStorageItem('uploadTableViewHeight', 400)
                    setTableViewHeight(400)
                }
                setTableView(!tableView)

                break
            default:
                break
        }
    }

    useEffect(() => {
        if (uploadMode) {
            setLocalStorageItem('uploadJsonViewWidth', jsonViewWidth)
            setLocalStorageItem('uploadJsonView', jsonView)
        } else {
            setLocalStorageItem('searchJsonViewWidth', jsonViewWidth)
            setLocalStorageItem('searchJsonView', jsonView)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [jsonViewWidth, jsonView])
    useEffect(() => {
        if (uploadMode) {
            setLocalStorageItem('uploadHistoryViewWidth', historyViewWidth)
            setLocalStorageItem('uploadHistoryView', historyView)
        } else {
            setLocalStorageItem('searchHistoryViewWidth', historyViewWidth)
            setLocalStorageItem('searchHistoryView', historyView)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [historyViewWidth, historyView])
    useEffect(() => {
        if (uploadMode) {
            setLocalStorageItem('uploadTableView', tableView)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [tableView])

    useEffect(() => {
        if (uploadMode) {
            setJsonViewWidth(getLocalStorageItem('uploadJsonViewWidth') ?? 0)
            setJsonView(getLocalStorageItem('uploadJsonView') ?? false)
            setHistoryViewWidth(getLocalStorageItem('uploadHistoryViewWidth') ?? 0)
            setHistoryView(getLocalStorageItem('uploadHistoryView') ?? false)
            setTableViewHeight(getLocalStorageItem('uploadTableViewHeight') ?? 0)
            setTableView(getLocalStorageItem('uploadTableView') ?? false)
        } else {
            setJsonViewWidth(getLocalStorageItem('searchJsonViewWidth') ?? 0)
            setJsonView(getLocalStorageItem('searchJsonView') ?? false)
            setHistoryViewWidth(getLocalStorageItem('searchHistoryViewWidth') ?? 0)
            setHistoryView(getLocalStorageItem('searchHistoryView') ?? false)
            setTableViewHeight(0)
            setTableView(false)
        }
    }, [uploadMode])

    const springProps = useSpring({
        jsonViewWidth: jsonViewWidth,
        historyViewWidth: historyViewWidth,
        tableViewHeight: tableView ? tableViewHeight : 0,
        canvasWidth: canvasRect.width,
        canvasHeight: canvasRect.height,
        config: {
            tension: 300,
            friction: 30,
        },
    })

    // CANVAS STUFF ########################################################
    // LOCAL STORAGE, NODES, HISTORY ###################################

    // Save and retrieve nodes and relationships to / from local storage
    useEffect(() => {
        setNodes([])
        setRelationships([])
        if (uploadMode) {
            const uploadId = localStorage.getItem('uploadId')
            if (!uploadId) return

            fetchUpload(uploadId, setUpload)
        } else {
            // handle set search
        }
    }, [uploadMode])

    // Rebuilds entire Index Dictionary
    const rebuildIndexDictionary = useCallback(() => {
        const newIndexDictionary: IndexDictionary = {}

        nodes.forEach((node) => {
            const indices = getNodeIndices(node)

            indices.forEach((index) => {
                if (newIndexDictionary[index]) {
                    newIndexDictionary[index].push(node.id)
                } else {
                    newIndexDictionary[index] = [node.id]
                }
            })
        })

        setIndexDictionary(newIndexDictionary)
    }, [nodes])

    // Rebuilds singular Node Entry in Index Dictionary
    const updateIndexDictionary = useCallback(
        (node: TNode) => {
            setIndexDictionary((prevIndexDictionary) => {
                let updatedIndexDictionary = { ...prevIndexDictionary }

                const nodeIndices = getNodeIndices(node)

                Object.keys(updatedIndexDictionary).forEach((index) => {
                    const indexNumber = parseInt(index)
                    const nodeIndex = updatedIndexDictionary[indexNumber].indexOf(node.id)
                    if (nodeIndex > -1) {
                        updatedIndexDictionary[indexNumber].splice(nodeIndex, 1)
                        if (updatedIndexDictionary[indexNumber].length === 0) {
                            delete updatedIndexDictionary[indexNumber]
                        }
                    }
                })

                nodeIndices.forEach((index) => {
                    if (!updatedIndexDictionary[index]) {
                        updatedIndexDictionary[index] = [node.id]
                    } else if (!updatedIndexDictionary[index].includes(node.id)) {
                        updatedIndexDictionary[index].push(node.id)
                    }
                })

                return updatedIndexDictionary
            })
        },
        [setIndexDictionary]
    )

    const indexFn = {
        rebuildIndexDictionary,
        updateIndexDictionary,
    }

    // Select nodes based on selectedColumnIndex
    useEffect(() => {
        if (!selectedColumnIndex) return

        if (indexDictionary.hasOwnProperty(selectedColumnIndex)) {
            let nodesWithIndex: TNode[] = []
            indexDictionary[selectedColumnIndex].forEach((nodeId) => {
                const nodeWithIndex = nodes.find((node) => node.id === nodeId)
                if (nodeWithIndex) nodesWithIndex.push(nodeWithIndex)
            })
            setSelectedNodes(nodesWithIndex)
        }
    }, [selectedColumnIndex, indexDictionary, nodes, setSelectedNodes])

    // Highlight nodes based on highlightedColumnIndex
    useEffect(() => {
        if (!highlightedColumnIndex || nodes.length === 0) {
            setHighlightedNodeIds(new Set([]))
            return
        }

        setHighlightedNodeIds(new Set(indexDictionary[highlightedColumnIndex] || []))
    }, [highlightedColumnIndex, nodes, indexDictionary])

    const forceEndEditing = () => {
        const updatedNodes = nodes.map((node) => {
            node.isEditing = false
            return node
        })

        setNodeEditing(false)
        setNodes(updatedNodes)
    }

    // History ########################################
    const updateHistory = useCallback(() => {
        setHistory((prev) => ({
            nodes: [...prev.nodes, nodes].slice(-UNDO_STEPS),
            relationships: [...prev.relationships, relationships].slice(-UNDO_STEPS),
        }))
        setFuture({ nodes: [], relationships: [] })
    }, [nodes, relationships])

    const updateHistoryWithCaution = useCallback(() => {
        setHistory((prev) => ({
            nodes: [...prev.nodes, nodes].slice(-UNDO_STEPS),
            relationships: [...prev.relationships, relationships].slice(-UNDO_STEPS),
        }))
    }, [nodes, relationships])

    const updateHistoryRevert = useCallback(() => {
        setHistory((prev) => ({
            nodes: prev.nodes.slice(0, -1),
            relationships: prev.relationships.slice(0, -1),
        }))
    }, [])

    const updateHistoryComplete = () => {
        setFuture({ nodes: [], relationships: [] })
    }

    const handleReset = () => {
        if (!nodes.length) return
        updateHistory()
        setNodes([])
        setRelationships([])
    }

    const undo = useCallback(() => {
        if (history.nodes.length) {
            setFuture((prev) => ({
                nodes: [nodes, ...prev.nodes].slice(-UNDO_STEPS),
                relationships: [relationships, ...prev.relationships].slice(-UNDO_STEPS),
            }))
            setNodes(
                history.nodes[history.nodes.length - 1].map((node) => ({
                    ...node,
                    isEditing: false,
                }))
            )
            setRelationships(history.relationships[history.relationships.length - 1])
            setHistory((prev) => ({
                nodes: prev.nodes.slice(0, -1),
                relationships: prev.relationships.slice(0, -1),
            }))
        }
    }, [history, nodes, relationships, setNodes, setRelationships])

    const redo = useCallback(() => {
        if (future.nodes.length) {
            setHistory((prev) => ({
                nodes: [...prev.nodes, nodes].slice(-UNDO_STEPS),
                relationships: [...prev.relationships, relationships].slice(-UNDO_STEPS),
            }))
            setNodes(future.nodes[0].map((node) => ({ ...node, isEditing: false })))
            setRelationships(future.relationships[0])
            setFuture((prev) => ({
                nodes: prev.nodes.slice(1),
                relationships: prev.relationships.slice(1),
            }))
        }
    }, [future, nodes, relationships, setNodes, setRelationships])

    const historyFn = {
        updateHistory,
        updateHistoryWithCaution,
        updateHistoryRevert,
        updateHistoryComplete,
        handleReset,
        undo,
        redo,
    }

    // Dark theme #############################
    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'

    // TableContext value
    const tableContextValue = {
        setHighlightedColumnIndex,
        selectedColumnIndex,
        setSelectedColumnIndex,
        forceEndEditing,
        uploadMode,
        tableViewHeight,
    }

    // GraphContext value
    const graphContextValue = {
        setNodes,
        setRelationships,
        setNeedLayout,
    }

    return (
        <div className="workspace" ref={workspaceWindowRef}>
            <WorkspaceTableContext.Provider value={tableContextValue}>
                <div
                    className="workspace-canvas"
                    style={{
                        overflow: 'hidden',
                        position: 'absolute',
                        left: 0,
                        width: '100%',
                        height: '100%',
                        zIndex: 0,
                    }}
                    children={
                        <>
                            <Canvas
                                nodesFn={nodesFn}
                                indexFn={indexFn}
                                saveGraph={setGraphLocal}
                                historyFn={historyFn}
                                needLayout={needLayout}
                                setNeedLayout={setNeedLayout}
                                style={{
                                    position: 'relative',
                                    width: '100%',
                                    height: '100%',
                                }}
                                canvasRect={canvasRect}
                            />
                            <div
                                className='hodenball'
                                style={{
                                    display: uploadProcessing.has(upload?._id ?? '') ? 'block' : 'none',
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    // display: 'block',
                                    width: '100%',
                                    height: '100%',
                                    backgroundColor: '#1a1b1e',
                                    opacity: 0.5,
                                }}
                            ></div>
                        </>
                    }
                />
            </WorkspaceTableContext.Provider>

            <animated.div
                className="workspace-history"
                style={{
                    height: springProps.canvasHeight,
                    width: springProps.historyViewWidth,
                    borderRight: historyView
                        ? darkTheme
                            ? '1px solid #333'
                            : '1px solid #ced4da'
                        : 'none',
                    backgroundColor: darkTheme ? '#25262b' : '#fff',
                    zIndex: 1,
                }}
                children={
                    <WorkspaceHistory
                        uploadMode={uploadMode}
                        graph={graph}
                        setNodes={setNodes}
                        setRelationships={setRelationships}
                        setNeedLayout={setNeedLayout}
                        upload={upload}
                        setUpload={setUpload}
                        uploadProcessing={uploadProcessing}
                        setUploadProcessing={setUploadProcessing}
                        historyView={historyView}
                        darkTheme={darkTheme}
                    />
                }
            />

            <animated.div
                className="workspace-drawer-right"
                style={{
                    height: springProps.canvasHeight,
                    width: springProps.jsonViewWidth,
                    borderLeft: jsonView
                        ? darkTheme
                            ? '1px solid #333'
                            : '1px solid #ced4da'
                        : 'none',
                    backgroundColor: darkTheme ? '#25262b' : '#fff',
                    zIndex: 1,
                }}
                children={
                    <>
                        {!uploadMode && (
                            <WorkspaceSearch
                                graph={graph}
                                jsonView={jsonView}
                                darkTheme={darkTheme}
                            />
                        )}
                        <WorkspaceJson graph={graph} jsonView={jsonView} darkTheme={darkTheme} />
                    </>
                }
            />

            {uploadMode && (
                <animated.div
                    className="workspace-drawer-bottom"
                    style={{
                        height: drawerHandleActiveRef.current
                            ? tableViewHeight
                            : springProps.tableViewHeight,
                        width: '100%',
                        borderTop: tableView
                            ? darkTheme
                                ? '1px solid #333'
                                : '1px solid #ced4da'
                            : 'none',
                        backgroundColor: darkTheme ? '#25262b' : '#fff',
                        zIndex: 1,
                        overflow: 'visible',
                    }}
                    children={
                        <div
                            className={`${drawerHandleActiveRef.current ? 'unselectable' : ''}`}
                            style={{
                                height: '100%',
                            }}
                        >
                            <WorkspaceTableContext.Provider value={tableContextValue}>
                                <WorkspaceDrawer
                                    tableView={tableView}
                                    tableViewHeight={tableViewHeight}
                                    progress={progress}
                                    setProgress={setProgress}
                                    setNodes={setNodes}
                                    setRelationships={setRelationships}
                                    setNeedLayout={setNeedLayout}
                                    graph={graph}
                                    upload={upload}
                                    uploadProcessing={uploadProcessing}
                                    setUploadProcessing={setUploadProcessing}
                                    setUpload={setUpload}
                                    selectedNodes={selectedNodes}
                                    rebuildIndexDictionary={rebuildIndexDictionary}
                                    darkTheme={darkTheme}
                                />
                            </WorkspaceTableContext.Provider>
                            {tableView && (
                                <WorkspaceDrawerHandle
                                    handleActive={drawerHandleActiveRef}
                                    tableViewHeight={tableViewHeight}
                                    setTableViewHeight={setTableViewHeight}
                                    setTableView={setTableView}
                                />
                            )}
                        </div>
                    }
                />
            )}
            <div className="workspace-btn-wrap" style={{ zIndex: 1 }}>
                <WorkspaceButtons
                    uploadMode={uploadMode}
                    jsonView={jsonView}
                    jsonViewWidth={jsonViewWidth}
                    historyView={historyView}
                    historyViewWidth={historyViewWidth}
                    tableView={tableView}
                    tableViewHeight={tableViewHeight}
                    onSelect={handleSplitView}
                    darkTheme={darkTheme}
                />
            </div>
        </div>
    )
}
