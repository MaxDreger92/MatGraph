import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import client from '../../client'
import 'react-virtualized/styles.css'
import WorkspaceTableDropzone from './WorkspaceTableDropzone'
import WorkspacePipeline from './WorkspacePipeline'
import { TableRow, IDictionary, IUpload } from '../../types/workspace.types'
import { IRelationship, INode } from '../../types/canvas.types'
import {
    arrayToDict,
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
    createUpload,
    fetchUpload,
    requestExtractAttributes,
    requestExtractGraph,
    requestExtractLabels,
    requestExtractNodes,
    requestImportGraph,
    updateUpload,
} from '../../common/clientHelpers'
// import testNodes from '../../alt/testNodesN.json'

const USE_MOCK_DATA = false

const exampleLabelDict: IDictionary = {
    Header1: { Label: 'matter' },
    Header2: { Label: 'manufacturing' },
    Header3: { Label: 'measurement' },
}
const exampleAttrDict: IDictionary = {
    Header1: { Label: 'matter', Attribute: 'name' },
    Header2: { Label: 'manufacturing', Attribute: 'identifier' },
    Header3: { Label: 'measurement', Attribute: 'name' },
}

interface WorkspaceDrawerProps {
    tableView: boolean
    tableViewHeight: number
    progress: number
    setProgress: React.Dispatch<React.SetStateAction<number>>
    setNodes: React.Dispatch<React.SetStateAction<INode[]>>
    setRelationships: React.Dispatch<React.SetStateAction<IRelationship[]>>
    setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
    upload: IUpload | undefined
    setUpload: React.Dispatch<React.SetStateAction<IUpload | undefined>>
    setUploadProcessing: React.Dispatch<React.SetStateAction<boolean>>
    workflow: string | null
    selectedNodes: INode[]
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
        upload,
        setUpload,
        setUploadProcessing,
        workflow,
        selectedNodes,
        rebuildIndexDictionary,
        darkTheme,
    } = props

    const [file, setFile] = useState<File | undefined>()
    const [fileLink, setFileLink] = useState<string>('Link')
    const [fileName, setFileName] = useState<string>('Name')
    const [context, setContext] = useState<string>('')
    const [csvTable, setCsvTable] = useState<TableRow[]>([])
    const [labelTable, setLabelTable] = useState<TableRow[]>([])
    const [labelInfo, setLabelInfo] = useState<IDictionary | null>(null)
    const [attributeTable, setAttributeTable] = useState<TableRow[]>([])
    const [currentTable, setCurrentTable] = useState<TableRow[]>([])
    const [currentTableId, setCurrentTableId] = useState('')
    const [additionalTables, setAdditionalTables] = useState<number[][]>([])
    const [columnLength, setColumnLength] = useState(0)

    useEffect(() => {
        if (!upload || upload.processing) return

        const {
            progress,
            fileLink,
            fileName,
            context,
            csvTable,
            labelDict,
            attributeDict,
            workflow,
        } = upload

        setProgress(progress)
        setFileLink(fileLink ?? '')
        setFileName(fileName ?? '')
        setContext(context ?? '')
        setCsvTable(csvTable ? JSON.parse(csvTable) : [])

        let labelTable: TableRow[] = []
        let attributeTable: TableRow[] = []

        if (labelDict) {
            const [labelDictCore, labelDictInfo] = splitDict(JSON.parse(labelDict), 1)
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
                toast.success('Workflow was successfully imported!')
            // FALLS THROUGH to default
            default:
                handleSetCurrentTable('csvTable', JSON.parse(csvTable ?? ''))
                break
        }

        if (!workflow) return

        const { nodes, relationships } = convertFromJsonFormat(workflow, true)

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
            if (upload && upload._id) {
                const updates = {
                    progress: 1,
                    fileLink: '',
                    fileName: '',
                    context: '',
                    csvTable: JSON.stringify(csvTable),
                    labelDict: '',
                    attributeDict: '',
                    workflow: '',
                    processing: false,
                }
                const updateSuccess = await updateUpload(upload._id, updates)
                if (!updateSuccess) {
                    handlePipelineReset()
                    return
                }
                const updatedUpload = await fetchUpload(upload._id)
                if (!updatedUpload) return
                setUpload(updatedUpload)
            } else {
                const newUpload = await createUpload(JSON.stringify(csvTable))
                if (!newUpload) {
                    handlePipelineReset()
                    return
                }
                setUpload(newUpload)
            }
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

    const handlePipelineReset = async () => {
        setCsvTable([])
        setLabelTable([])
        setAttributeTable([])
        handleSetCurrentTable('', [])
        setProgress(0)
    }

    // (file,context) => label_dict, file_link, file_name
    const extractLabels = async () => {
        if (!USE_MOCK_DATA) {
            if (!file) {
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
                if (!upload || !upload._id) {
                    toast.error('Upload process not found!')
                    return
                }

                const uploadProcessing = await requestExtractLabels(file as File, context)
                setUploadProcessing(!!uploadProcessing)
            }
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (label_dict, context, file_link, file_name) => attribute_dict
    async function extractAttributes() {
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

                const uploadProcessing = await requestExtractAttributes(
                    context,
                    fileLink,
                    fileName,
                    labelDict
                )
                setUploadProcessing(!!uploadProcessing)
            }
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (attribute_dict, context, file_link, file_name) => node_json
    async function extractNodes() {
        try {
            if (!USE_MOCK_DATA) {
                if (!upload || !upload._id) {
                    toast.error('Upload process not found!')
                    return
                }

                const attributeDict = arrayToDict(attributeTable)

                const uploadProcessing = await requestExtractNodes(
                    context,
                    fileLink,
                    fileName,
                    attributeDict
                )
                setUploadProcessing(!!uploadProcessing)
            } else {
            }
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (node_json, context, file_link, file_name) => graph_json
    async function extractGraph() {
        try {
            if (!upload || !upload._id) {
                toast.error('Upload process not found!')
                return
            }
            if (!workflow) {
                toast.error('Workflow JSON not found!')
                return
            }

            const uploadProcessing = await requestExtractGraph(
                context,
                fileLink,
                fileName,
                workflow
            )
            setUploadProcessing(!!uploadProcessing)
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (graph_json, context, fileLink, fileName) => success
    async function importGraph() {
        try {
            if (!upload || !upload._id) {
                toast.error('Upload process not found!')
                return
            }
            if (!workflow) {
                toast.error('Workflow JSON not found!')
                return
            }

            const uploadProcessing = await requestImportGraph(context, fileLink, fileName, workflow)
            setUploadProcessing(!!uploadProcessing)
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
        <>
            {progress === 0 && tableView && tableViewHeight >= 250 && (
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
                            loadNodes={loadNodes}
                            handlePipelineReset={handlePipelineReset}
                            handleContextChange={handleContextChange}
                            requestExtractLabels={extractLabels}
                            requestExtractAttributes={extractAttributes}
                            requestExtractNodes={extractNodes}
                            requestExtractGraph={extractGraph}
                            requestImportGraph={importGraph}
                            progress={progress}
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
                            currentTableId === 'csvTable' &&
                            tableView && (
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
                        {tableView && (
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
                        )}
                    </div>
                </div>
            )}
        </>
    )
}
