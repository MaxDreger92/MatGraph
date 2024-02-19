import { useEffect, useRef, useState, useMemo } from "react"
import toast from "react-hot-toast"
import client from "../../client"
import Papa from "papaparse"
import { MultiGrid, GridCellProps, Index } from "react-virtualized"
import "react-virtualized/styles.css"
import WorkflowTableDropzone from "./WorkflowTableDropzone"
import WorkflowPipeline from "./WorkflowPipeline"
import { IconUpload } from "@tabler/icons-react"
import { Button } from "@mantine/core"
import { TableRow, IDictionary, IWorkflow } from "../../types/workflow.types"
import { IRelationship, INode } from "../../types/canvas.types"
import {
  convertFromJsonFormat,
  convertToJSONFormat,
} from "../../common/helpers"
import WorkflowTable from "./WorkflowTable"

const USE_MOCK_DATA = false

const exampleLabelDict: IDictionary = {
  Header1: { Label: "matter" },
  Header2: { Label: "manufacturing" },
  Header3: { Label: "measurement" },
}
const exampleAttrDict: IDictionary = {
  Header1: { Label: "matter", Attribute: "name" },
  Header2: { Label: "manufacturing", Attribute: "identifier" },
  Header3: { Label: "measurement", Attribute: "name" },
}

interface WorkflowDrawerProps {
  tableView: boolean
  progress: number
  setProgress: React.Dispatch<React.SetStateAction<number>>
  setNodes: React.Dispatch<React.SetStateAction<INode[]>>
  setRelationships: React.Dispatch<React.SetStateAction<IRelationship[]>>
  setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
  workflow: string | null
  workflows: IWorkflow[] | undefined
}

export default function WorkflowDrawer(props: WorkflowDrawerProps) {
  const {
    tableView,
    progress,
    setProgress,
    setNodes,
    setRelationships,
    setNeedLayout,
    workflow,
    workflows,
  } = props

  const [file, setFile] = useState<File | undefined>()
  const [fileLink, setFileLink] = useState<string>("Link")
  const [fileName, setFileName] = useState<string>("Name")
  const [context, setContext] = useState<string>("")
  const [csvTable, setCsvTable] = useState<TableRow[]>([])
  const [labelTable, setLabelTable] = useState<TableRow[]>([])
  const [attributeTable, setAttributeTable] = useState<TableRow[]>([])
  const [currentTable, setCurrentTable] = useState<TableRow[]>([])

  const [drawerRect, setDrawerRect] = useState<DOMRect | null>(null)
  const workflowDrawerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (workflowDrawerRef.current && typeof ResizeObserver === 'function') {
      const observer = new ResizeObserver(entries => {
        const [entry] = entries;
        setDrawerRect(entry.contentRect);
      });

      observer.observe(workflowDrawerRef.current);

      return () => observer.disconnect();
    }
  }, [workflowDrawerRef, currentTable]);

  const handlePipelineReset = () => {
    setCsvTable([])
    setProgress(0)
  }

  const handleContextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const contextString = e.target.value
    setContext(contextString)
  }

  const handleFileView = (file: File) => {
    if (file) {
      setFile(file)
      Papa.parse(file, {
        header: true,
        dynamicTyping: true,
        complete: (result) => {
          const safeData = result.data as { [key: string]: unknown}[]
          const typedData: TableRow[] = safeData.map(row => {
            const typedRow: TableRow = {}
            Object.entries(row).forEach(([key, value]) => {
              if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
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
        },
        skipEmptyLines: true,
      })
    }
    setProgress(1)
  }

  // (file,context) => label_dict, file_link, file_name
  async function requestExtractLabels() {
    if (!file) {
      toast.error("File not found!")
      return
    }

    if (!USE_MOCK_DATA) {
      if (!(context && context.length > 0)) {
        toast.error("Pls enter context!")
        return
      }
    }

    try {
      if (USE_MOCK_DATA) {
        const dictArray = dictToArray(exampleLabelDict)
        setLabelTable(dictArray)
        setCurrentTable(dictArray)
      } else {
        const data = await client.requestExtractLabels(file, context)

        if (data.graph_json && data.file_link) {
          const { nodes, relationships } = convertFromJsonFormat(data.graph_json)
          setNodes(nodes)
          setRelationships(relationships)
          setNeedLayout(true)
          setProgress(5)
          setFileLink(data.file_link)
          return
        }
  
        if (!(data && data.label_dict && data.file_link && data.file_name)) {
          throw new Error("Error while extracting labels!")
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
          fileName,
        )
  
        if (!(data && data.attribute_dict)) {
          throw new Error("Error while extracting attributes!")
        }
  
        const attrArray = dictToArray(data.attribute_dict)
  
        setAttributeTable(attrArray)
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
        const dict = arrayToDict(attributeTable)
        console.log(exampleAttrDict)
        console.log(dict)
      } else {
      const attrDict = arrayToDict(attributeTable)

      if (!attrDict) return

      const data = await client.requestExtractNodes(
        attrDict,
        context,
        fileLink,
        fileName
      )

      if (!(data && data.node_json)) {
        throw new Error("Error while extracting nodes!")
      }

      const { nodes, relationships } = convertFromJsonFormat(data.node_json)

      setRelationships([])
      setNodes(nodes)
      setNeedLayout(true)

      setProgress(4)}

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

      const data = await client.requestExtractGraph(
        nodeJson,
        context,
        fileLink,
        fileName
      )

      if (!(data && data.graph_json)) {
        throw new Error("Error while extracting graph!")
      }

      const { nodes, relationships } = convertFromJsonFormat(data.graph_json)

      setNodes(nodes)
      setRelationships(relationships)
      setNeedLayout(true)

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
        throw new Error("Error while extracting graph!")
      }

      toast.success(data.success)
    } catch (err: any) {
      toast.error(err.message)
    }
  }

  function dictToArray(dict: IDictionary): TableRow[] {
    // Initialize an object to hold the combined rows
    const combinedRows: { [property: string]: TableRow } = {};
  
    // Iterate through each header in the dictionary
    Object.entries(dict).forEach(([header, properties]) => {
      // Then iterate through each property (Label, Attribute, etc.) under that header
      Object.entries(properties).forEach(([property, value]) => {
        // If a row for this property doesn't exist yet, create it
        if (!combinedRows[property]) {
          combinedRows[property] = {};
        }
        // Add the current value to the appropriate property row under the correct header
        combinedRows[property][header] = value;
      });
    });
  
    // Convert the combinedRows object into an array of TableRow objects
    return Object.values(combinedRows);
  }

  function arrayToDict(tableRows: TableRow[]): IDictionary {  
    const dict: IDictionary = {};
  
    // Assume all rows have the same structure, use the first row to determine headers
    const headers = Object.keys(tableRows[0]);
  
    // Initialize the dictionary with headers pointing to empty objects
    headers.forEach(header => {
      dict[header] = {};
    });
  
    // Populate the dictionary by iterating over each row and then each cell in the row
    tableRows.forEach((row, rowIndex) => {
      Object.entries(row).forEach(([header, value]) => {
        // Convert value to string, since IDictionary expects string values
        const stringValue = String(value);

        let key = "Default_Key"

        if (rowIndex === 0) {
          key = "Label"
        } else if (rowIndex === 1) {
          key = "Attribute"
        } else {
          key = `Row${rowIndex + 1}`
        }
  
        // Use rowIndex to create a unique key for each row in the inner dictionary
  
        dict[header][key] = stringValue;
      });
    });
  
    return dict;
  }
  

  return (
    <>
      {progress === 0 && (
        <WorkflowTableDropzone handleFileView={handleFileView} />
      )}
      {progress > 0 && (
        <div
          ref={workflowDrawerRef}
          className="workflow-drawer"
          style={{
            position: "relative",
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "column",
            // justifyContent:"center",
          }}
        >
          {progress > 0 && csvTable && (
            <WorkflowPipeline 
              handlePipelineReset={handlePipelineReset}
              handleContextChange={handleContextChange}
              requestExtractLabels={requestExtractLabels}
              requestExtractAttributes={requestExtractAttributes}
              requestExtractNodes={requestExtractNodes}
              requestExtractGraph={requestExtractGraph}
              requestImportGraph={requestImportGraph}
              progress={progress}
            />
          )}
          <WorkflowTable
            setLabelTable={setLabelTable}
            setAttributeTable={setAttributeTable}
            setTableRows={setCurrentTable}
            tableRows={currentTable}
            progress={progress}
            drawerRect={drawerRect}
          />
        </div>
      )}
    </>
  )
}
