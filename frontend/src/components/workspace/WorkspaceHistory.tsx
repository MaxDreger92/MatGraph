import { SetStateAction, useContext, useEffect, useState } from 'react'
import { Upload, Graph, UploadListItem } from '../../types/workspace.types'
import { TRelationship, TNode } from '../../types/canvas.types'
import { convertFromJsonFormat } from '../../common/workspaceHelpers'
import { RiDeleteBin2Line } from 'react-icons/ri'
import { UserContext } from '../../context/UserContext'
import {
    deleteUpload,
    deleteGraph,
    fetchUploads,
    fetchGraphs,
} from '../../common/clientHelpers'
import toast from 'react-hot-toast'
import { useQuery } from 'react-query'
import client from '../../client'

interface WorkspaceHistoryProps {
    uploadMode: boolean
    graph: string | null
    setNodes: React.Dispatch<SetStateAction<TNode[]>>
    setRelationships: React.Dispatch<SetStateAction<TRelationship[]>>
    setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
    upload: Upload | undefined
    setUpload: React.Dispatch<React.SetStateAction<Upload | undefined>>
    uploadProcessing: boolean
    darkTheme: boolean
}

export default function WorkspaceHistory(props: WorkspaceHistoryProps) {
    const { uploadMode, graph, setNodes, setRelationships, setNeedLayout, upload, setUpload, uploadProcessing, darkTheme } =
        props

    const user = useContext(UserContext)
    const [hovered, setHovered] = useState<number | undefined>()
    const [trashHovered, setTrashHovered] = useState(false)

    const [graphs, setGraphs] = useState<Graph[] | undefined>([])
    const [uploads, setUploads] = useState<Upload[] | undefined>([])
    const [historyItems, setHistoryItems] = useState<Graph[] | Upload[]>([])

    // ###################################################################### Set Current History List
    useEffect(() => {
        setHistoryItems([])
        if (uploadMode && uploads) {
            console.log('uploadLength: ', uploads.length)
            setHistoryItems(uploads)
        } else if (graphs) {
            setHistoryItems(graphs)
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [uploads, graphs, uploadMode])

    // ###################################################################### Fetch History Items
    // const {
    //     data: uploadListData,
    //     error: uploadListError,
    //     isLoading: uploadListLoading,
    // } = useQuery('uploadList', () => client.getUploads(), {
    //     enabled: uploadProcessing,
    //     refetchInterval: 2000,
    //     onSuccess: (data) => {
    //         // console.log('history polling')
    //         // if (data.uploadList) {
    //         //     setUploads(data.uploadList)
    //         // }
    //     },
    // })

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
            const selectedGraph = graphs.find(graph => graph._id === id)
            if (!selectedGraph) return
            setNodesAndRelationships(selectedGraph.data)
        } else {
            if (!uploads) return
            const selectedUpload = uploads.find(upload => upload._id === id)
            if (!selectedUpload || !selectedUpload._id) return
            setUpload(undefined)
            setUpload(selectedUpload)
        }
    }

    const setNodesAndRelationships = (graph: string) => {
        const { nodes, relationships } = convertFromJsonFormat(graph, false)
        setNodes(nodes)
        setRelationships(relationships)
        setNeedLayout(true)
    }

    return (
        <div
            className="workspace-history-list"
            style={{
            paddingTop: 15,
                paddingLeft: 10,
                paddingRight: 10,
                overflow: 'auto'
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
                            paddingLeft: 10,
                            borderRadius: '5px',
                            cursor: 'pointer',
                        }}
                        onMouseEnter={() => setHovered(index)}
                        onMouseLeave={() => setHovered(undefined)}
                        onClick={() => handleSelectItem(item._id)}
                    >
                        {hovered === index && (
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
                        <span
                            style={{
                                textAlign: 'left',
                                color: 'inherit',
                                fontSize: 16,
                                fontWeight: 'bold',
                                userSelect: 'none',
                            }}
                        >
                            Test
                        </span>
                        <span
                            style={{
                                textAlign: 'left',
                                color: 'inherit',
                                fontSize: 14,
                                userSelect: 'none',
                            }}
                        >
                            {new Date(item.timestamp).toLocaleString()}
                        </span>
                    </div>
                ))}
        </div>
    )
}
