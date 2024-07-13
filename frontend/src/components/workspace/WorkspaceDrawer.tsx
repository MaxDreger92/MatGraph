import { SetStateAction, useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import 'react-virtualized/styles.css'
import WorkspaceTableDropzone from './WorkspaceTableDropzone'
import WorkspacePipeline from './WorkspacePipeline'
import { TableRow, Dictionary, Upload } from '../../types/workspace.types'
import { TRelationship, TNode } from '../../types/canvas.types'
import {
    arrayToDict,
    buildRevertUpdates,
    convertFromJsonFormat,
    dictToArray,
    filterCsvTable,
    getAdditionalTables,
    getTableFromFile,
    joinDict,
    splitDict,
} from '../../common/workspaceHelpers'
import WorkspaceTable from './WorkspaceTable'
import WorkspacePartialTable from './WorkspacePartialTable'
import WorkspaceTableTabs from './WorkspaceTableTabs'
import {
    requestExtractAttributes,
    requestExtractGraph,
    requestExtractLabels,
    requestExtractNodes,
    requestFileUpload,
    requestImportGraph,
    updateUpload,
} from '../../common/clientHelpers'
// import testNodes from '../../alt/testNodesN.json'

const USE_MOCK_DATA = false

const exampleLabelDict: Dictionary = {
    Header1: ['matter'],
    Header2: ['manufacturing'],
    Header3: ['measurement'],
}
const exampleAttrDict: Dictionary = {
    Header1: ['matter', 'name'],
    Header2: ['manufacturing', 'identifier'],
    Header3: ['measurement', 'name'],
}

interface WorkspaceDrawerProps {
    tableView: boolean
    tableViewHeight: number
    progress: number
    setProgress: React.Dispatch<React.SetStateAction<number>>
    setNodes: React.Dispatch<React.SetStateAction<TNode[]>>
    setRelationships: React.Dispatch<React.SetStateAction<TRelationship[]>>
    setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
    graph: string | null
    upload: Upload | undefined
    setUpload: React.Dispatch<React.SetStateAction<Upload | undefined>>
    uploadProcessing: Set<string>
    setUploadProcessing: React.Dispatch<React.SetStateAction<Set<string>>>
    selectedNodes: TNode[]
    rebuildIndexDictionary: () => void
    darkTheme: boolean
}

export default function WorkspaceDrawer(props: WorkspaceDrawerProps) {
    const {
        tableView,
        tableViewHeight,
        progress,
        setProgress,
        setNodes,
        setRelationships,
        setNeedLayout,
        graph,
        upload,
        setUpload,
        uploadProcessing,
        setUploadProcessing,
        selectedNodes,
        rebuildIndexDictionary,
        darkTheme,
    } = props

    const [file, setFile] = useState<File | undefined>()
    const [fileId, setFileId] = useState<string>('')
    const [context, setContext] = useState<string>('')
    const [csvTable, setCsvTable] = useState<TableRow[]>([])
    const [labelTable, setLabelTable] = useState<TableRow[]>([])
    const [labelInfo, setLabelInfo] = useState<Dictionary | null>(null)
    const [attributeTable, setAttributeTable] = useState<TableRow[]>([])
    const [currentTable, setCurrentTable] = useState<TableRow[]>([])
    const [currentTableId, setCurrentTableId] = useState('')
    const [additionalTables, setAdditionalTables] = useState<number[][]>([])
    const [columnLength, setColumnLength] = useState(0)

    useEffect(() => {
        if (!upload) return

        const { progress, fileId, context, csvTable, labelDict, attributeDict, graph } = upload

        setProgress(progress)
        setFileId(fileId ?? '')
        setContext(context ?? '')
        setCsvTable(csvTable ? JSON.parse(csvTable) : [])

        let labelTable: TableRow[] = []
        let attributeTable: TableRow[] = []

        if (labelDict) {
            const parsedDict = JSON.parse(labelDict)
            const [labelDictCore, labelDictInfo] = splitDict(parsedDict, 1)
            if (Object.entries(labelDictInfo).length > 0) {
                setLabelInfo(labelDictInfo)
            }
            labelTable = dictToArray(labelDictCore)
            setLabelTable(labelTable)
        } else {
            setLabelTable([])
            setLabelInfo(null)
        }

        if (attributeDict) {
            attributeTable = dictToArray(JSON.parse(attributeDict))
            setAttributeTable(attributeTable)
        } else {
            setAttributeTable([])
        }

        switch (progress) {
            case 2:
                handleSetCurrentTable('labelTable', labelTable)
                break
            case 3:
                handleSetCurrentTable('attributeTable', attributeTable)
                break
            case 6:
                toast.success('Graph was successfully imported!')
            // FALLS THROUGH to default
            default:
                handleSetCurrentTable('csvTable', JSON.parse(csvTable ?? ''))
                break
        }

        if (!graph) {
            setNodes([])
            setRelationships([])
            return
        }

        let parsed = JSON.parse(graph)
        if (typeof parsed === 'object') {
            parsed = JSON.stringify(parsed)
        }
        const { nodes, relationships } = convertFromJsonFormat(parsed, true)

        setNodes(nodes)
        setRelationships(relationships)
        setNeedLayout(true)
        rebuildIndexDictionary()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [upload])

    const handleContextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const contextString = e.target.value
        setContext(contextString)
    }

    const handleFileSelect = async (file: File) => {
        if (!file) return
        setFile(file)

        let csvTable: TableRow[] = []
        try {
            csvTable = await getTableFromFile(file)
            setColumnLength(Object.keys(csvTable[0]).length)
        } catch (error) {
            console.error('Error parsing file:', error)
        }

        if (!USE_MOCK_DATA) {
            const newUpload = await requestFileUpload(file, JSON.stringify(csvTable))
            if (!newUpload) {
                await handlePipelineReset()
                return
            }
            localStorage.setItem('uploadId', newUpload._id)
            setUpload(newUpload)
        } else {
            setCsvTable(csvTable)
            handleSetCurrentTable('csvTable', csvTable)
            setProgress(1)
        }
    }

    const handleSetCurrentTable = (tableId: string, tableRows?: TableRow[]) => {
        if (tableRows) {
            setCurrentTable(tableRows)
        } else {
            switch (tableId) {
                case 'csvTable':
                    setCurrentTable(csvTable)
                    break
                case 'labelTable':
                    setCurrentTable(labelTable)
                    break
                case 'attributeTable':
                    setCurrentTable(attributeTable)
                    break
                default:
                    // do nothing
                    break
            }
        }
        setCurrentTableId(tableId)
    }

    const handleRevertProgress = async (newProgress: number) => {
        if (newProgress >= progress) return

        if (!upload || !upload._id) {
            toast.error('Upload process not found!')
            return
        }

        const updates = buildRevertUpdates(newProgress, graph as string)

        try {
            const revertSuccess = await updateUpload(upload._id, updates)
            if (!revertSuccess) {
                toast.error('Progress could not be reverted!')
                return
            }
            console.log('success')
            const decoyUpload = { ...upload, progress: newProgress }
            setUpload(decoyUpload)
        } catch (err: any) {
            toast.error(err.message)
            return
        }

        if (newProgress < 5) {
            setRelationships([])
        }
        if (newProgress < 4) {
            setNodes([])
        }
        if (newProgress < 3) {
            setAttributeTable([])
        }
        if (newProgress < 2) {
            setLabelTable([])
        }
        if (newProgress < 1) {
            setContext('')
        }
    }

    const handlePipelineReset = () => {
        setProgress(0)
        setUpload(undefined)
        setCsvTable([])
        setLabelTable([])
        setAttributeTable([])
        handleSetCurrentTable('', [])
        setNodes([])
        setRelationships([])
    }

    const addUploadProcessing = (uploadId: string) => {
        setUploadProcessing((prev) => {
            const newSet = new Set(prev)
            newSet.add(uploadId)
            return newSet
        })
    }

    // (file,context) => label_dict, file_link, file_name
    const extractLabels = async () => {
        if (!USE_MOCK_DATA) {
            if (!fileId) {
                toast.error('File not found!')
                return
            }

            if (!(context && context.length > 0)) {
                toast.error('Pls enter context!')
                return
            }
        }

        try {
            if (USE_MOCK_DATA) {
                const dictArray = dictToArray(exampleLabelDict)
                setLabelTable(dictArray)
                handleSetCurrentTable('labelTable', dictArray)
                setProgress(2)
            } else {
                if (!upload || !upload._id || !upload.fileId) {
                    toast.error('Upload process not found!')
                    return
                }

                const processStarted = await requestExtractLabels(
                    upload._id,
                    context,
                    upload.fileId
                )
                if (!processStarted) return
                addUploadProcessing(upload._id)
            }
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (label_dict, context, file_link, file_name) => attribute_dict
    const extractAttributes = async () => {
        try {
            if (USE_MOCK_DATA) {
                const dictArray = dictToArray(exampleAttrDict)
                setAttributeTable(dictArray)
                handleSetCurrentTable('attributeTable', dictArray)
                setProgress(3)
            } else {
                if (!upload || !upload._id) {
                    toast.error('Upload process not found!')
                    return
                }

                let labelDict = arrayToDict(labelTable)
                if (labelInfo) {
                    labelDict = joinDict(labelDict, labelInfo)
                }

                const processStarted = await requestExtractAttributes(
                    upload._id,
                    context,
                    fileId,
                    labelDict
                )
                if (!processStarted) return
                addUploadProcessing(upload._id)
            }
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (attribute_dict, context, file_link, file_name) => node_json
    const extractNodes = async () => {
        try {
            if (!USE_MOCK_DATA) {
                if (!upload || !upload._id) {
                    toast.error('Upload process not found!')
                    return
                }

                const attributeDict = arrayToDict(attributeTable)

                const processStarted = await requestExtractNodes(
                    upload._id,
                    context,
                    fileId,
                    attributeDict
                )
                if (!processStarted) return
                addUploadProcessing(upload._id)
            } else {
            }
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (node_json, context, file_link, file_name) => graph_json
    const extractGraph = async () => {
        try {
            if (!upload || !upload._id) {
                toast.error('Upload process not found!')
                return
            }
            if (!graph) {
                toast.error('Graph JSON not found!')
                return
            }

            const processStarted = await requestExtractGraph(upload._id, context, fileId, graph)
            if (!processStarted) return
            addUploadProcessing(upload._id)
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (graph_json, context, fileLink, fileName) => success
    const importGraph = async () => {
        try {
            if (!upload || !upload._id) {
                toast.error('Upload process not found!')
                return
            }
            if (!graph) {
                toast.error('Graph JSON not found!')
                return
            }

            const processStarted = await requestImportGraph(upload._id, context, fileId, graph)
            if (!processStarted) return
            addUploadProcessing(upload._id)
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // Additional tables for highlighted Nodes ########################################
    useEffect(() => {
        if (progress < 4) return

        const newAdditionalTables = getAdditionalTables(selectedNodes)

        setAdditionalTables(newAdditionalTables)
    }, [selectedNodes, progress])

    const loadNodes = () => {
        // console.log(testNodes)
        // // const nodeString = JSON.stringify(testNodes)
        // const { nodes, relationships } = convertFromJsonFormat(JSON.stringify(testNodes), true)
        //   setRelationships([])
        //   setNodes(nodes)
        //   setNeedLayout(true)
    }

    return (
        <div
            style={{
                display: tableView ? 'block' : 'none',
            }}
        >
            {progress === 0 && tableViewHeight >= 250 && (
                <WorkspaceTableDropzone handleFileSelect={handleFileSelect} />
            )}
            {progress > 0 && (
                <div
                    className="workspace-drawer"
                    style={{
                        position: 'relative',
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                    }}
                >
                    <WorkspaceTableTabs
                        progress={progress}
                        currentTableId={currentTableId}
                        setCurrentTableFn={handleSetCurrentTable}
                    />
                    {progress > 0 && csvTable && (
                        <WorkspacePipeline
                            handlePipelineReset={handlePipelineReset}
                            handleRevertProgress={handleRevertProgress}
                            handleContextChange={handleContextChange}
                            extractLabels={extractLabels}
                            extractAttributes={extractAttributes}
                            extractNodes={extractNodes}
                            extractGraph={extractGraph}
                            importGraph={importGraph}
                            progress={progress}
                            upload={upload}
                            uploadProcessing={uploadProcessing}
                            darkTheme={darkTheme}
                        />
                    )}

                    {/* All Tables */}
                    <div
                        style={{
                            position: 'relative',
                            display: 'flex',
                            flexDirection: 'row',
                            width: '100%',
                        }}
                    >
                        {/* Additional Tables */}
                        {additionalTables.length > 0 &&
                            progress > 3 &&
                            currentTableId === 'csvTable' && (
                                <>
                                    <div
                                        style={{
                                            paddingLeft: 10,
                                            paddingRight: 10,
                                            maxWidth: '50%',
                                            overflow: 'hidden',
                                        }}
                                    >
                                        <div
                                            style={{
                                                position: 'relative',
                                                display: 'flex',
                                                flexDirection: 'row',
                                                overflowX: 'auto',
                                            }}
                                        >
                                            {filterCsvTable(csvTable, additionalTables).map(
                                                (additionalTable, index) => (
                                                    <div
                                                        id={'portalRoot' + index}
                                                        key={index}
                                                        style={{
                                                            position: 'relative',
                                                            display: 'flex',
                                                            flexDirection: 'column',
                                                            overflow: 'hidden',
                                                            paddingLeft: index > 0 ? 10 : 15,
                                                            minWidth: 'fit-content',
                                                        }}
                                                    >
                                                        <WorkspacePartialTable
                                                            tableRows={additionalTable}
                                                            outerTableHeight={tableViewHeight}
                                                            darkTheme={darkTheme}
                                                            columnsLength={
                                                                Object.keys(additionalTable[0])
                                                                    .length
                                                            }
                                                            filteredColumns={additionalTables[
                                                                index
                                                            ].slice(1)}
                                                            numericalNodeType={
                                                                additionalTables[index][0]
                                                            }
                                                        />
                                                    </div>
                                                )
                                            )}
                                        </div>
                                    </div>
                                    <div
                                        style={{
                                            height: '100%',
                                            width: 2,
                                            backgroundColor: darkTheme ? '#555' : '#ced4da',
                                        }}
                                    />
                                </>
                            )}

                        {/* CSV Table */}
                        <div
                            style={{
                                position: 'relative',
                                minWidth: '50%',
                                flex: '1 1 50%',
                                paddingLeft:
                                    additionalTables.length > 0 &&
                                    progress > 3 &&
                                    currentTableId === 'csvTable'
                                        ? 10
                                        : 25,
                                paddingRight: 25,
                            }}
                        >
                            <div
                                style={{
                                    position: 'relative',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    maxWidth: 'fit-content',
                                    minWidth: '100%',
                                }}
                            >
                                <WorkspaceTable
                                    setLabelTable={setLabelTable}
                                    setAttributeTable={setAttributeTable}
                                    setCurrentTableFn={handleSetCurrentTable}
                                    tableRows={currentTable}
                                    progress={progress}
                                    currentTableId={currentTableId}
                                    outerTableHeight={tableViewHeight}
                                    darkTheme={darkTheme}
                                    columnsLength={columnLength}
                                    additionalTables={additionalTables}
                                />
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
