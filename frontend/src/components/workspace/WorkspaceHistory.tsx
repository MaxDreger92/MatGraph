import { SetStateAction, useContext, useEffect, useState } from 'react'
import { Upload, Workflow, UploadListItem } from '../../types/workspace.types'
import { TRelationship, TNode } from '../../types/canvas.types'
import { convertFromJsonFormat } from '../../common/workspaceHelpers'
import { RiDeleteBin2Line } from 'react-icons/ri'
import { UserContext } from '../../context/UserContext'
import {
    deleteUpload,
    deleteWorkflow,
    fetchUploads,
    fetchWorkflows,
} from '../../common/clientHelpers'
import toast from 'react-hot-toast'
import { useQuery } from 'react-query'
import client from '../../client'

interface WorkspaceHistoryProps {
    uploadMode: boolean
    setNodes: React.Dispatch<SetStateAction<TNode[]>>
    setRelationships: React.Dispatch<SetStateAction<TRelationship[]>>
    setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
    upload: Upload | undefined
    setUpload: React.Dispatch<React.SetStateAction<Upload | undefined>>
    uploadProcessing: boolean
    darkTheme: boolean
}

export default function WorkspaceHistory(props: WorkspaceHistoryProps) {
    const { uploadMode, setNodes, setRelationships, setNeedLayout, upload, setUpload, uploadProcessing, darkTheme } =
        props

    const user = useContext(UserContext)
    const [hovered, setHovered] = useState<number | undefined>()
    const [trashHovered, setTrashHovered] = useState(false)

    const [workflows, setWorkflows] = useState<Workflow[] | undefined>([])
    const [uploads, setUploads] = useState<Upload[] | undefined>([])
    const [historyItems, setHistoryItems] = useState<Workflow[] | Upload[]>([])

    // ###################################################################### Set Current History List
    useEffect(() => {
        setHistoryItems([])
        if (uploadMode && uploads) {
            console.log('uploadLength: ', uploads.length)
            setHistoryItems(uploads)
        } else if (workflows) {
            setHistoryItems(workflows)
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [uploads, workflows, uploadMode])

    // ###################################################################### Fetch History Items
    const {
        data: uploadListData,
        error: uploadListError,
        isLoading: uploadListLoading,
    } = useQuery('uploadList', () => client.getUploads(), {
        enabled: uploadProcessing,
        refetchInterval: 2000,
        onSuccess: (data) => {
            // console.log('history polling')
            // if (data.uploadList) {
            //     setUploads(data.uploadList)
            // }
        },
    })

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

        handleFetchWorkflows()
    }, [user, uploadMode])

    const handleFetchWorkflows = async () => {
        const workflows = await fetchWorkflows()
        if (!workflows) {
            return
        }
        setWorkflows(workflows)
    }

    // ###################################################################### Delete Items
    const handleDeleteItem = async (e: React.MouseEvent, index: number) => {
        if (!uploadMode) {
            if (!workflows) return

            try {
                await deleteWorkflow(workflows[index]._id)
    
                handleFetchWorkflows()
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
            if (!workflows) return
            const selectedWorkflow = workflows.find(workflow => workflow._id === id)
            if (!selectedWorkflow) return
            setNodesAndRelationships(selectedWorkflow.data)
        } else {
            if (!uploads) return
            const selectedUpload = uploads.find(upload => upload._id === id)
            if (!selectedUpload || !selectedUpload._id) return
            setUpload(undefined)
            setUpload(selectedUpload)
        }
    }

    const setNodesAndRelationships = (workflow: string) => {
        const { nodes, relationships } = convertFromJsonFormat(workflow, false)
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
