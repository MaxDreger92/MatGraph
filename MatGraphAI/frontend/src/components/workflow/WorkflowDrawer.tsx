import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import client from '../../client'
import Papa from 'papaparse'
import 'react-virtualized/styles.css'
import WorkflowTableDropzone from './WorkflowTableDropzone'
import WorkflowPipeline from './WorkflowPipeline'
import { TableRow, IDictionary, IWorkflow } from '../../types/workflow.types'
import {
    IRelationship,
    INode,
    NodeAttribute,
    NodeValOpAttribute,
} from '../../types/canvas.types'
import {
    convertFromJsonFormat,
    mapNodeTypeNumerical,
} from '../../common/helpers'
import WorkflowTable from './WorkflowTable'
import WorkflowPartialTable from './WorkflowPartialTable'
// import testNodes from '../../alt/testNodesN.json'

const USE_MOCK_DATA = true

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

interface WorkflowDrawerProps {
    tableView: boolean
    tableViewHeight: number
    progress: number
    setProgress: React.Dispatch<React.SetStateAction<number>>
    setNodes: React.Dispatch<React.SetStateAction<INode[]>>
    setRelationships: React.Dispatch<React.SetStateAction<IRelationship[]>>
    setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
    workflow: string | null
    workflows: IWorkflow[] | undefined
    selectedNodes: INode[]
    rebuildIndexDictionary: () => void
    darkTheme: boolean
}

export default function WorkflowDrawer(props: WorkflowDrawerProps) {
    const {
        tableViewHeight,
        progress,
        setProgress,
        setNodes,
        setRelationships,
        setNeedLayout,
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
    const [attributeTable, setAttributeTable] = useState<TableRow[]>([])
    const [currentTable, setCurrentTable] = useState<TableRow[]>([])
    const [additionalTables, setAdditionalTables] = useState<number[][]>([])
    const [columnLength, setColumnLength] = useState(0)

    // #################################### Saving tables to local storage should only be temporary measure
    // Load tables and progress from local storage
    useEffect(() => {
        const storedProgress = localStorage.getItem('upload-progress')
        const storedFileLink = localStorage.getItem('upload-fileLink')
        const storedFileName = localStorage.getItem('upload-fileName')
        const storedContext = localStorage.getItem('upload-context')
        const storedCsvTable = localStorage.getItem('upload-input-table')
        const storedLabelTable = localStorage.getItem('upload-label-table')
        const storedAttributeTable = localStorage.getItem('upload-attribute-table')

        if (storedFileLink) setFileLink(JSON.parse(storedFileLink))
        if (storedFileName) setFileName(JSON.parse(storedFileName))
        if (storedContext) setContext(JSON.parse(storedContext))
        if (storedCsvTable) setCsvTable(JSON.parse(storedCsvTable))
        if (storedLabelTable) setLabelTable(JSON.parse(storedLabelTable))
        if (storedAttributeTable) setAttributeTable(JSON.parse(storedAttributeTable))
        if (storedProgress) {
            const parsedStoredProgress = JSON.parse(storedProgress)
            setProgress(parsedStoredProgress)
            switch (parsedStoredProgress) {
                case 0:
                    handlePipelineReset()
                    break
                case 1:
                    handlePipelineReset()
                    break
                case 2:
                    if (storedLabelTable) {
                        setCurrentTable(JSON.parse(storedLabelTable))
                    } else {
                        handlePipelineReset()
                    }
                    break
                case 3:
                    if (storedAttributeTable) {
                        setCurrentTable(JSON.parse(storedAttributeTable))
                    } else {
                        handlePipelineReset()
                    }
                    break
                default:
                    if (storedCsvTable) {
                        setCurrentTable(JSON.parse(storedCsvTable))
                    } else {
                        handlePipelineReset()
                    }
                    break
            }
        }
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    // Save tables and progress to local storage
    useEffect(() => {
        localStorage.setItem('upload-progress', JSON.stringify(progress))
    }, [progress])

    useEffect(() => {
        localStorage.setItem('upload-fileLink', JSON.stringify(fileLink))
    }, [fileLink])

    useEffect(() => {
        localStorage.setItem('upload-fileName', JSON.stringify(fileName))
    }, [fileName])

    useEffect(() => {
        localStorage.setItem('upload-context', JSON.stringify(context))
    }, [context])

    useEffect(() => {
        localStorage.setItem('upload-input-table', JSON.stringify(csvTable))
    }, [csvTable])

    useEffect(() => {
        localStorage.setItem('upload-label-table', JSON.stringify(labelTable))
    }, [labelTable])

    useEffect(() => {
        localStorage.setItem('upload-attribute-table', JSON.stringify(attributeTable))
    }, [attributeTable])

    const handlePipelineReset = () => {
        setCsvTable([])
        setCurrentTable([])
        setProgress(0)
    }

    const handleContextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const contextString = e.target.value
        setContext(contextString)
    }

    const handleFileUpload = (file: File) => {
        if (file) {
            setFile(file)
            Papa.parse(file, {
                header: true,
                dynamicTyping: true,
                complete: (result) => {
                    const safeData = result.data as { [key: string]: unknown }[]
                    const typedData: TableRow[] = safeData.map((row) => {
                        const typedRow: TableRow = {}
                        Object.entries(row).forEach(([key, value]) => {
                            if (
                                typeof value === 'string' ||
                                typeof value === 'number' ||
                                typeof value === 'boolean'
                            ) {
                                typedRow[key] = value
                            } else {
                                // console.warn(`Unexpected value type for key "${key}":`, value);
                                if (value !== null) {
                                    typedRow[key] = String(value)
                                } else {
                                    typedRow[key] = ''
                                }
                                // typedRow[key] = String(value)
                            }
                        })
                        return typedRow
                    })
                    setCsvTable(typedData)
                    setCurrentTable(typedData)
                    setColumnLength(Object.keys(typedData[0]).length)
                },
                skipEmptyLines: true,
            })
        }
        setProgress(1)
    }

    const loadNodes = () => {
        // console.log(testNodes)
        // // const nodeString = JSON.stringify(testNodes)
        // const { nodes, relationships } = convertFromJsonFormat(JSON.stringify(testNodes), true)
        //   setRelationships([])
        //   setNodes(nodes)
        //   setNeedLayout(true)
    }

    // (file,context) => label_dict, file_link, file_name
    async function requestExtractLabels() {
        if (!file && !USE_MOCK_DATA) {
            toast.error('File not found!')
            return
        }

        if (!USE_MOCK_DATA) {
            if (!(context && context.length > 0)) {
                toast.error('Pls enter context!')
                return
            }
        }

        try {
            if (USE_MOCK_DATA) {
                const dictArray = dictToArray(exampleLabelDict)
                setLabelTable(dictArray)
                setCurrentTable(dictArray)
            } else {
                const data = await client.requestExtractLabels(file as File, context)

                if (data.graph_json && data.file_link) {
                    const { nodes, relationships } = convertFromJsonFormat(data.graph_json, true)
                    setNodes(nodes)
                    setRelationships(relationships)
                    setNeedLayout(true)
                    setProgress(5)
                    setFileLink(data.file_link)
                    return
                }

                if (!(data && data.label_dict && data.file_link && data.file_name)) {
                    throw new Error('Error while extracting labels!')
                }

                const labelArray = dictToArray(data.label_dict)
                setLabelTable(labelArray)
                setCurrentTable(labelArray)
                setFileLink(data.file_link)
                setFileName(data.file_name)
            }

            setProgress(2)
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (label_dict, context, file_link, file_name) => attribute_dict
    async function requestExtractAttributes() {
        try {
            if (USE_MOCK_DATA) {
                const dictArray = dictToArray(exampleAttrDict)
                setAttributeTable(dictArray)
                setCurrentTable(dictArray)
            } else {
                const labelDict = arrayToDict(labelTable)

                if (!labelDict) return

                const data = await client.requestExtractAttributes(
                    labelDict,
                    context,
                    fileLink,
                    fileName
                )

                if (!(data && data.attribute_dict)) {
                    throw new Error('Error while extracting attributes!')
                }

                const attrArray = dictToArray(data.attribute_dict)

                setAttributeTable(attrArray)
                setCurrentTable(attrArray)
            }

            setProgress(3)
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (attribute_dict, context, file_link, file_name) => node_json
    async function requestExtractNodes() {
        try {
            if (USE_MOCK_DATA) {
                setCurrentTable(csvTable)
                setProgress(4)
            } else {
                const attrDict = arrayToDict(attributeTable)

                if (!attrDict) return

                const data = await client.requestExtractNodes(attrDict, context, fileLink, fileName)

                if (!(data && data.node_json)) {
                    throw new Error('Error while extracting nodes!')
                }

                const { nodes, relationships } = convertFromJsonFormat(data.node_json, true)

                setRelationships([])
                setNodes(nodes)
                setNeedLayout(true)
                rebuildIndexDictionary()

                setProgress(4)
            }

            // if (!workflows || !workflows[1]) {
            //   console.log("workflow not found")
            //   return
            // }
            // const { nodes, relationships } = convertFromJSONFormat(
            //   workflows[1].workflow
            // )
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (node_json, context, file_link, file_name) => graph_json
    async function requestExtractGraph() {
        try {
            const nodeJson = workflow

            if (!nodeJson) return

            const data = await client.requestExtractGraph(nodeJson, context, fileLink, fileName)

            if (!(data && data.graph_json)) {
                throw new Error('Error while extracting graph!')
            }

            const { nodes, relationships } = convertFromJsonFormat(data.graph_json, true)

            setNodes(nodes)
            setRelationships(relationships)
            setNeedLayout(true)
            rebuildIndexDictionary()

            setProgress(5)

            // if (!workflows || !workflows[2]) {
            //   console.log("workflow not found")
            //   return
            // }
            // const { nodes, relationships } = convertFromJSONFormat(
            //   workflows[2].workflow
            // )
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    // (graph_json, context, fileLink, fileName) => success
    async function requestImportGraph() {
        try {
            const graphJson = workflow

            if (!graphJson) return

            const data = await client.requestImportGraph(
                graphJson,
                context, // Pass context parameter
                fileLink, // Pass fileLink parameter
                fileName // Pass fileName parameter
            )

            if (!(data && data.success)) {
                throw new Error('Error while extracting graph!')
            }

            toast.success(data.success)
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    function dictToArray(dict: IDictionary): TableRow[] {
        // Initialize an object to hold the combined rows
        const combinedRows: { [property: string]: TableRow } = {}

        // Iterate through each header in the dictionary
        Object.entries(dict).forEach(([header, properties]) => {
            // Then iterate through each property (Label, Attribute, etc.) under that header
            Object.entries(properties).forEach(([property, value]) => {
                // If a row for this property doesn't exist yet, create it
                if (!combinedRows[property]) {
                    combinedRows[property] = {}
                }
                // Add the current value to the appropriate property row under the correct header
                combinedRows[property][header] = value
            })
        })

        // Convert the combinedRows object into an array of TableRow objects
        return Object.values(combinedRows)
    }

    function arrayToDict(tableRows: TableRow[]): IDictionary {
        const dict: IDictionary = {}

        // Assume all rows have the same structure, use the first row to determine headers
        const headers = Object.keys(tableRows[0])

        // Initialize the dictionary with headers pointing to empty objects
        headers.forEach((header) => {
            dict[header] = {}
        })

        // Populate the dictionary by iterating over each row and then each cell in the row
        tableRows.forEach((row, rowIndex) => {
            Object.entries(row).forEach(([header, value]) => {
                // Convert value to string, since IDictionary expects string values
                const stringValue = String(value)

                let key = 'Default_Key'

                if (rowIndex === 0) {
                    key = 'Label'
                } else if (rowIndex === 1) {
                    key = 'Attribute'
                } else {
                    key = `Row${rowIndex + 1}`
                }

                // Use rowIndex to create a unique key for each row in the inner dictionary

                dict[header][key] = stringValue
            })
        })

        return dict
    }

    // Additional tables for highlighted Nodes ########################################
    useEffect(() => {
        if (progress < 4) return

        const newAdditionalTables = selectedNodes.reduce<number[][]>((acc, node) => {
            // Initialize an empty array for each node to store indices
            let indices: number[] = []

            // Function to extract and add number indices from attributes
            const addIndices = (attr: NodeAttribute | NodeValOpAttribute) => {
                if (typeof attr.index === 'number') {
                    indices.push(attr.index)
                } else if (Array.isArray(attr.index)) {
                    attr.index.forEach((index) => {
                        if (typeof index === 'number') {
                            indices.push(index)
                        }
                    })
                }
            }

            // First entry nodeType
            const numericalNodeType = mapNodeTypeNumerical(node.type)
            indices.push(numericalNodeType)

            // Extract indices from each relevant attribute of the node
            addIndices(node.name)
            addIndices(node.value)
            addIndices(node.batch_num)
            addIndices(node.ratio)
            addIndices(node.concentration)
            addIndices(node.unit)
            addIndices(node.std)
            addIndices(node.error)
            addIndices(node.identifier)

            if (indices.length > 1) {
                acc.push(indices)
            }
            return acc
        }, [])

        // Update state with the newly generated arrays of indices

        setAdditionalTables(newAdditionalTables)
    }, [selectedNodes, progress])

    // Define a function to filter csvTable based on additionalTables
    function filterCsvTable(csvTable: TableRow[], additionalTables: number[][]): TableRow[][] {
        const filteredTables: TableRow[][] = []

        // Iterate through each entry in additionalTables
        additionalTables.forEach((additionalTable: number[]) => {
            // Create a new table with only the specified columns
            const filteredTable: TableRow[] = []
            const rowIndexMap: Map<string, number> = new Map() // Map to store row index based on row content
            // Remove first element as it is the node type
            const columnsToInclude = additionalTable.slice(1)

            columnsToInclude.forEach((columnIndex: number) => {
                // Get the column name from the index
                const columnName = Object.keys(csvTable[0])[columnIndex]
                // Iterate through each row in csvTable and copy the selected column values
                csvTable.forEach((row: TableRow) => {
                    const rowKey = JSON.stringify(row) // Convert the row object to a string to use as key
                    // Check if the row already exists in the filtered table
                    if (!rowIndexMap.has(rowKey)) {
                        // If the row doesn't exist, create a new row in the filtered table
                        filteredTable.push({}) // Push an empty object to represent the new row
                        rowIndexMap.set(rowKey, filteredTable.length - 1) // Store the index of the new row
                    }
                    const rowIndex = rowIndexMap.get(rowKey)! // Get the index of the row in the filtered table
                    // Copy the column value to the filtered table
                    filteredTable[rowIndex][columnName] = row[columnName]
                })
            })
            // Add the filtered table to the result
            filteredTables.push(filteredTable)
        })

        return filteredTables
    }

    return (
        <>
            {progress === 0 && <WorkflowTableDropzone handleFileUpload={handleFileUpload} />}
            {progress > 0 && (
                <div
                    className="workflow-drawer"
                    style={{
                        position: 'relative',
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        flexDirection: 'column',
                        // justifyContent:"center",
                    }}
                >
                    {progress > 0 && csvTable && (
                        <WorkflowPipeline
                            loadNodes={loadNodes}
                            handlePipelineReset={handlePipelineReset}
                            handleContextChange={handleContextChange}
                            requestExtractLabels={requestExtractLabels}
                            requestExtractAttributes={requestExtractAttributes}
                            requestExtractNodes={requestExtractNodes}
                            requestExtractGraph={requestExtractGraph}
                            requestImportGraph={requestImportGraph}
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
                        {additionalTables.length > 0 && progress > 3 && (
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
                                                        paddingLeft: index > 0 ? 10 : 0,
                                                        minWidth: 'fit-content',
                                                    }}
                                                >
                                                    <WorkflowPartialTable
                                                        tableRows={additionalTable}
                                                        outerTableHeight={tableViewHeight}
                                                        darkTheme={darkTheme}
                                                        columnsLength={
                                                            Object.keys(additionalTable[0]).length
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
                                paddingLeft: 10,
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
                                <WorkflowTable
                                    setLabelTable={setLabelTable}
                                    setAttributeTable={setAttributeTable}
                                    setTableRows={setCurrentTable}
                                    tableRows={currentTable}
                                    progress={progress}
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
        </>
    )
}
