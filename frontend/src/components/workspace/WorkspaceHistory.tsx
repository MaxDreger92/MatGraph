import { SetStateAction, useContext, useEffect, useState } from 'react'
import { Upload, Graph, UploadListItem } from '../../types/workspace.types'
import { TRelationship, TNode } from '../../types/canvas.types'
import { convertFromJsonFormat } from '../../common/workspaceHelpers'
import { RiDeleteBin2Line } from 'react-icons/ri'
import { UserContext } from '../../context/UserContext'
import { deleteUpload, deleteGraph, fetchUploads, fetchGraphs } from '../../common/clientHelpers'
import { useQuery } from 'react-query'
import client from '../../client'
import logo_sm from '../../img/logo_nodes_sm.png'
import logo_light_sm from '../../img/logo_nodes_light_sm.png'
import { getLocalStorageItem, setLocalStorageItem } from '../../common/localStorageHelpers'

interface WorkspaceHistoryProps {
    uploadMode: boolean
    graph: string | null
    setNodes: React.Dispatch<SetStateAction<TNode[]>>
    setRelationships: React.Dispatch<SetStateAction<TRelationship[]>>
    setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
    upload: Upload | undefined
    setUpload: React.Dispatch<React.SetStateAction<Upload | undefined>>
    uploadProcessing: Set<string>
    setUploadProcessing: React.Dispatch<React.SetStateAction<Set<string>>>
    historyView: boolean
    darkTheme: boolean
}

export default function WorkspaceHistory(props: WorkspaceHistoryProps) {
    const {
        uploadMode,
        graph,
        setNodes,
        setRelationships,
        setNeedLayout,
        upload,
        setUpload,
        uploadProcessing,
        setUploadProcessing,
        historyView,
        darkTheme,
    } = props

    const user = useContext(UserContext)
    const [hovered, setHovered] = useState<number | undefined>()
    const [trashHovered, setTrashHovered] = useState(false)

    const [graphs, setGraphs] = useState<Graph[] | undefined>([])
    const [uploads, setUploads] = useState<Upload[] | undefined>([])
    const [historyItems, setHistoryItems] = useState<Graph[] | Upload[]>([])

    const [notHighlighted, setNotHighlighted] = useState<Set<string>>(new Set())

    // ###################################################################### Set Current History List
    useEffect(() => {
        setHistoryItems([])
        if (uploadMode && uploads) {
            setHistoryItems(uploads)
        } else if (graphs) {
            setHistoryItems(graphs)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [uploads, graphs, uploadMode])

    // ###################################################################### Fetch History Items
    useQuery('uploadList', () => client.getUploads(), {
        enabled: uploadProcessing.size > 0,
        refetchInterval: 2000,
        onSuccess: (data) => {
            console.log('polling')
            if (data.uploads) {
                setUploads(data.uploads)
            }
        },
    })

    useEffect(() => {
        if (uploads) {
            uploads.forEach((item) => {
                if (item.processing === true) {
                    removeNotHighlighted(item._id)
                } else if (uploadProcessing.has(item._id)) {
                    setUploadProcessing(prev => {
                        const newSet = new Set(prev)
                        newSet.delete(item._id)
                        return newSet
                    })
                }
            })

            const reloadedUpload = uploads.find((up) => up._id === upload?._id)
            if (
                reloadedUpload &&
                reloadedUpload.processing === false &&
                reloadedUpload.timestamp !== upload?.timestamp
            ) {
                setUpload(reloadedUpload)
            }
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [uploads])

    useEffect(() => {
        if (!user || !uploadMode) return

        handleFetchUploads()
    }, [user, uploadMode, upload])

    const handleFetchUploads = async () => {
        const uploads = await fetchUploads()
        if (!uploads) {
            return
        }
        setUploads(uploads)
    }

    useEffect(() => {
        if (!user || uploadMode) return

        handleFetchGraphs()
    }, [user, uploadMode, graph])

    const handleFetchGraphs = async () => {
        const graphs = await fetchGraphs()
        if (!graphs) {
            return
        }
        setGraphs(graphs)
    }

    // ###################################################################### Delete Items
    const handleDeleteItem = async (e: React.MouseEvent, index: number) => {
        if (!uploadMode) {
            if (!graphs) return

            try {
                await deleteGraph(graphs[index]._id)

                handleFetchGraphs()
            } catch (err: any) {
                // toast.error(err.message) // Do some error handling
            }
        } else {
            if (!uploads) return

            try {
                await deleteUpload(uploads[index]._id)

                handleFetchUploads()
            } catch (err: any) {
                // toast.error(err.message) // Do some error handling
            }
        }
    }

    // ###################################################################### Select Item
    const handleSelectItem = (id: string) => {
        if (!uploadMode) {
            if (!graphs) return
            const selectedGraph = graphs.find((graph) => graph._id === id)
            if (!selectedGraph) return
            console.log(selectedGraph.graph)
            setNodesAndRelationships(selectedGraph.graph)
        } else {
            if (!uploads) return
            const selectedUpload = uploads.find((upload) => upload._id === id)
            if (!selectedUpload || !selectedUpload._id) return
            localStorage.setItem('currentUploadId', selectedUpload._id)
            setUpload(selectedUpload)
        }
    }

    const setNodesAndRelationships = (graph: string) => {
        console.log(graph)
        const { nodes, relationships } = convertFromJsonFormat(graph, false)
        setNodes(nodes)
        setRelationships(relationships)
        setNeedLayout(true)
    }

    // ###################################################################### Item Name
    const getItemName = (item: Upload | Graph, index: number) => {
        if (!uploadMode) {
            return item.name ?? 'Graph ' + (index + 1)
        } else {
            const uploadItem = item as Upload
            let contextAdd: string = ''
            if (uploadItem.context) {
                contextAdd = ': ' + uploadItem.context
            }
            return uploadItem.name ?? uploadItem.fileName + contextAdd
        }
    }

    // ###################################################################### Other
    useEffect(() => {
        const savedNotHighlighted = getLocalStorageItem('historyItemNotHighlighted')
        if (!savedNotHighlighted || !Array.isArray(savedNotHighlighted)) return
        const newSet = new Set(savedNotHighlighted)
        setNotHighlighted(newSet)
    }, [])

    const isHighlighted = (item: Graph | Upload): boolean => {
        if (isUpload(item)) {
            return item.processing === false && !notHighlighted.has(item._id)
        }
        return !notHighlighted.has(item._id)
    }

    const addNotHighlighted = (itemId: string) => {
        setNotHighlighted((prev) => {
            const newSet = new Set(prev)
            newSet.add(itemId)
            const array = Array.from(newSet)
            setLocalStorageItem('historyItemNotHighlighted', array)
            return newSet
        })
    }

    const removeNotHighlighted = (itemId: string) => {
        setNotHighlighted((prev) => {
            const newSet = new Set(prev)
            newSet.delete(itemId)
            const array = Array.from(newSet)
            setLocalStorageItem('historyItemNotHighlighted', array)
            return newSet
        })
    }

    const isUpload = (item: Graph | Upload): item is Upload => {
        return (item as Upload).processing !== undefined
    }

    const isProcessing = (item: Graph | Upload): boolean => {
        return isUpload(item) && item.processing === true
    }

    return (
        <div
            className="workspace-history-list"
            style={{
                width: 300,
                paddingTop: 15,
                paddingLeft: 10,
                paddingRight: 10,
                overflowY: 'auto',
                overflowX: 'hidden',
                display: historyView ? 'block' : 'none',
            }}
        >
            {historyItems &&
                historyItems.map((item, index) => (
                    <div
                        key={index}
                        style={{
                            position: 'relative',
                            width: '100%',
                            height: 50,
                            backgroundColor:
                                hovered === index
                                    ? darkTheme
                                        ? '#373A40'
                                        : '#f1f3f5'
                                    : 'transparent',
                            justifyContent: 'center',
                            display: 'flex',
                            flexDirection: 'column',
                            marginBottom: 10,
                            padding: '0 0 5px 15px',
                            borderRadius: '5px',
                            cursor: 'pointer',
                        }}
                        onMouseEnter={() => setHovered(index)}
                        onMouseLeave={() => setHovered(undefined)}
                        onMouseOver={() => addNotHighlighted(item._id)}
                        onClick={() => handleSelectItem(item._id)}
                    >
                        {/* Selected Indicator */}
                        {upload?._id === item._id && (
                            <div
                                style={{
                                    position: 'absolute',
                                    top: '9%',
                                    left: 5,
                                    height: '80%',
                                    width: 3,
                                    borderRadius: 2,
                                    backgroundColor: darkTheme ? '#c1c2c5' : '#000'
                                }}
                            ></div>
                        )}
                        {/* Highlighted Indicator */}
                        {isHighlighted(item) && upload?._id !== item._id && <div
                            style={{
                                position: 'absolute',
                                top: '36%',
                                left: 5,
                                height: '24%',
                                width: 3,
                                borderRadius: 2,
                                // border: `1px solid ${darkTheme ? '#0ff48b' : '#7fb800'}`
                                backgroundColor: darkTheme ? '#0ff48b' : '#7fb800'
                            }}
                            // onMouseOver={() => addNotHighlighted(item._id)}
                        ></div>}
                        <span
                            className='history-item-fadeout'
                            style={{
                                textAlign: 'left',
                                // color: isHighlighted(item) ? darkTheme ? '#0ff48b' : '#7fb800' : 'inherit',
                                color: 'inherit',
                                fontSize: 16,
                                fontWeight: 'bold',
                                userSelect: 'none',
                                whiteSpace: 'nowrap'
                            }}
                        >
                            {getItemName(item, index)}
                        </span>
                        <span
                            style={{
                                textAlign: 'left',
                                // color: isHighlighted(item) ? darkTheme ? '#0ff48b' : '#7fb800' : 'inherit',
                                color: 'inherit',
                                fontSize: 14,
                                userSelect: 'none',
                            }}
                        >
                            {new Date(item.timestamp).toLocaleString()}
                        </span>

                        {hovered === index && !isProcessing(item) && (
                            <RiDeleteBin2Line
                                style={{
                                    position: 'absolute',
                                    right: '5%',
                                    fontSize: 20,
                                    top: 14,
                                    color: trashHovered
                                        ? '#ff0000'
                                        : darkTheme
                                        ? '#909296'
                                        : '#495057',
                                }}
                                onMouseEnter={() => setTrashHovered(true)}
                                onMouseLeave={() => setTrashHovered(false)}
                                onClick={(e) => {
                                    e.stopPropagation()
                                    handleDeleteItem(e, index)
                                }}
                            />
                        )}
                        {isProcessing(item) && (
                            <img
                                className='logo-sm-spinner logo-spin-anim'
                                src={darkTheme ? logo_sm : logo_light_sm}
                                alt='Logo'
                            />
                        )}
                    </div>
                ))}
        </div>
    )
}
