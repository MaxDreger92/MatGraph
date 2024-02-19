import { useEffect, useRef, useState } from "react"
import toast from "react-hot-toast"
import client from "../../client"
import Papa from "papaparse"
import { MultiGrid, GridCellProps, Index } from "react-virtualized"
import "react-virtualized/styles.css"
import WorkflowTableDropzone from "./WorkflowTableDropzone"
import { IconUpload } from "@tabler/icons-react"
import { Button } from "@mantine/core"
import { IDictionary, IWorkflow } from "../../types/workflow.types"
import { IRelationship, INode } from "../../types/canvas.types"
import {
  convertFromJsonFormat,
  convertToJSONFormat,
} from "../../common/helpers"

interface WorkflowTableProps {
  tableView: boolean
  progress: number
  setProgress: React.Dispatch<React.SetStateAction<number>>
  setNodes: React.Dispatch<React.SetStateAction<INode[]>>
  setRelationships: React.Dispatch<React.SetStateAction<IRelationship[]>>
  setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
  workflow: string | null
  workflows: IWorkflow[] | undefined
}

const exampleLabelDict: IDictionary = {
  Header1: {Label: "Label1"},
  Header2: {Label: "Label2"},
  Header3: {Label: "Label3"},
  // Add more key-value pairs as needed
}

const exampleAttrDict: IDictionary = {
  Header1: {Label: "Label1", Attribute: "Attribute1"},
  Header2: {Label: "Label2", Attribute: "Attribute2"},
  Header3: {Label: "Label3", Attribute: "Attribute3"},
  // Add more key-value pairs as needed
}

export default function WorkflowTable(props: WorkflowTableProps) {
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
  const tableViewRef = useRef<HTMLDivElement>(null)
  const [tableViewRect, setTableViewRect] = useState<DOMRect | null>(null)
  const [hovered, setHovered] = useState(false)

  const [file, setFile] = useState<File | undefined>()
  const [fileLink, setFileLink] = useState<string>("Link")
  const [fileName, setFileName] = useState<string>("Name")
  const [context, setContext] = useState<string>("")
  const [csvTable, setCsvTable] = useState<any[] | null>(null)
  const [labelTable, setLabelTable] = useState<any[] | null>(null)
  const [attributeTable, setAttributeTable] = useState<any[] | null>(null)

  const multiGridRef = useRef<any>(null)
  // if (multiGridRef.current) {
  //   multiGridRef.current.recomputeGridSize()
  // }

  useEffect(() => {
    const resizeObserver = new ResizeObserver(() => {
      if (tableViewRef.current) {
        setTableViewRect(tableViewRef.current.getBoundingClientRect())
      }
    })

    const currentView = tableViewRef.current
    if (currentView) {
      resizeObserver.observe(currentView)
    }

    return () => {
      if (currentView) {
        resizeObserver.unobserve(currentView)
      }
    }
  })

  const handleContextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const contextString = e.target.value
    setContext(contextString)
  }

  const handleFileView = (file: File) => {
    if (file) {
      setFile(file)
      Papa.parse(file, {
        header: true,
        complete: (result) => {
          setCsvTable(result.data)
        },
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
    if (!(context && context.length > 0)) {
      toast.error("Pls enter context!")
      return
    }

    try {

      const data = await client.requestExtractLabels(file, context)

      if (data.graph_json) {
        setFileLink(data.file_link)
        const { nodes, relationships } = convertFromJsonFormat(data.graph_json)
        setNodes(nodes)
        setRelationships(relationships)
        setNeedLayout(true)
        setProgress(5)
        return
      }

      if (!(data && data.label_dict && data.file_link && data.file_name)) {
        throw new Error("Error while extracting labels!")
      }

      const dictArray = dictToArray(data.label_dict)
      setLabelTable(dictArray)
      setFileLink(data.file_link)
      setFileName(data.file_name)

      // const dictArray = dictToArray(exampleLabelDict)
      // setLabelTable(dictArray)

      setProgress(2)
    } catch (err: any) {
      toast.error(err.message)
    }
  }

  // (label_dict, context, file_link, file_name) => attribute_dict
  async function requestExtractAttributes() {
    try {
      const dict = arrayToDict(labelTable)

      if (!dict) return

      const data = await client.requestExtractAttributes(
        dict,
        context,
        fileLink,
        fileName
      )

      if (!(data && data.attribute_dict)) {
        throw new Error("Error while extracting attributes!")
      }

      const dictArray = dictToArray(data.attribute_dict)

      // const dictArray = dictToArray(exampleAttrDict)

      setAttributeTable(dictArray)
      setProgress(3)
    } catch (err: any) {
      toast.error(err.message)
    }
  }

  // (attribute_dict, context, file_link, file_name) => node_json
  async function requestExtractNodes() {
    try {
      const dict = arrayToDict(attributeTable)

      if (!dict) return

      const data = await client.requestExtractNodes(
        dict,
        context,
        fileLink,
        fileName
      )

      if (!(data && data.node_json)) {
        throw new Error("Error while extracting nodes!")
      }

      const { nodes, relationships } = convertFromJsonFormat(data.node_json)
      // if (!workflows || !workflows[1]) {
      //   console.log("workflow not found")
      //   return
      // }
      // const { nodes, relationships } = convertFromJSONFormat(
      //   workflows[1].workflow
      // )

      setRelationships([])
      setNodes(nodes)
      setNeedLayout(true)

      setProgress(4)
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
    } catch (err: any) {
      toast.error(err.message)
    }
  }

    // (graph_json, context, fileLink, fileName) => success
    async function requestImportGraph() {
      try {
        const graphJson = workflow;

        if (!graphJson) return;

        const data = await client.requestImportGraph(
          graphJson,
          context,    // Pass context parameter
          fileLink,   // Pass fileLink parameter
          fileName    // Pass fileName parameter
        );

        if (!(data && data.success)) {
          throw new Error("Error while extracting graph!");
        }
      } catch (err: any) {
        toast.error(err.message);
      }
    }

  function dictToArray(dict: IDictionary): string[][] {
    if (!dict || Object.keys(dict).length === 0) {
      return [];
    }
  
    // Extract headers from the outer dictionary keys
    const headers = Object.keys(dict);
    
    // Prepare the first row of the table with these headers
    const table: string[][] = [headers];
  
    // Determine the maximum number of rows needed by finding the longest inner dictionary
    const maxRows = Math.max(...Object.values(dict).map(innerDict => Object.keys(innerDict).length));
    
    // Initialize each row with empty strings to accommodate all headers
    for (let i = 0; i < maxRows; i++) {
      table.push(new Array(headers.length).fill(""));
    }
  
    // Populate the table rows with values from each inner dictionary
    headers.forEach((header, headerIndex) => {
      const innerDict = dict[header];
      const keys = Object.keys(innerDict);
      keys.forEach((key, rowIndex) => {
        table[rowIndex + 1][headerIndex] = innerDict[key]; // rowIndex + 1 to skip header row
      });
    });
  
    // Clean up any rows at the end that contain only undefined values
    return table.filter(row => row.some(cell => cell !== undefined && cell !== ""));
  }
  
  function arrayToDict(array: string[][] | null): IDictionary | null {
    // Validate the input array
    if (!array || array.length < 2 || !Array.isArray(array[0])) {
      return null; // Return null if input is null, has less than 2 rows, or if the first row is not an array
    }
  
    const dict: IDictionary = {};
    const headers = array[0]; // The first row contains headers
  
    // Initialize dict with headers
    headers.forEach(header => {
      if (typeof header === "string") {
        dict[header] = {}; // Each header becomes a key to an empty inner dictionary
      } else {
        return null; // Return null if any header is not a string
      }
    });
  
    // Iterate over each row starting from the second row
    array.slice(1).forEach((row, rowIndex) => {
      headers.forEach((header, columnIndex) => {
        const value = row[columnIndex];
        if (typeof header === "string" && value !== undefined && value !== null) {
          // Determine the appropriate key based on rowIndex
          let key;
          if (rowIndex === 0) {
            key = "Label";
          } else if (rowIndex === 1) {
            key = "Attribute";
          } else {
            key = `Row${rowIndex}`;
          }
  
          // Assign or update the value in the inner dictionary
          dict[header][key] = value;
        }
      });
    });
  
    return dict;
  }
  
  const cellRenderer: React.FC<GridCellProps> = ({
    columnIndex,
    key,
    rowIndex,
    style,
  }) => {
    let content: string | string[] = ""

    if (progress === 1 && csvTable) {
      content =
        rowIndex === 0
          ? Object.keys(csvTable[0])[columnIndex]
          : csvTable[rowIndex - 1][Object.keys(csvTable[0])[columnIndex]]
    } else if (progress === 2 && labelTable) {
      content = labelTable[rowIndex][columnIndex] || ""
    } else if (progress === 3 && attributeTable) {
      content = attributeTable[rowIndex][columnIndex] || ""
    }

    const newStyle = {
      ...style,
      border: "1px solid #333",
      padding: "2px",
    }

    return (
      <div key={key} style={newStyle}>
        {content}
      </div>
    )
  }

  const getColumnCount = (): number => {
    if (progress === 1 && csvTable) {
      return csvTable[0] ? Object.keys(csvTable[0]).length : 0
    } else if (progress === 2 && labelTable) {
      return labelTable[0] ? Object.keys(labelTable[0]).length : 0
    } else if (progress === 3 && attributeTable) {
      return attributeTable[0] ? Object.keys(attributeTable[0]).length : 0
    }
    return 0
  }

  const getRowCount = (): number => {
    if (progress === 1 && csvTable) {
      return csvTable.length + 1
    } else if (progress === 2 && labelTable) {
      return labelTable.length
    } else if (progress === 3 && attributeTable) {
      return attributeTable.length
    }
    return 0
  }

  const getColumnWidth = ( {index} : Index): number => {
    if (progress === 1 && csvTable) {
      const headerText = csvTable[0] ? Object.keys(csvTable[0])[index] : ""
      return Math.max(headerText.length * 15, 90)
    } else if (progress === 2 && labelTable) {
      const headerText = labelTable[0] ? labelTable[0][index] : ""
      return Math.max(headerText.length * 15, 90)
    } else if (progress === 3 && attributeTable) {
      const headerText = attributeTable[0] ? attributeTable[0][index] : ""
      return Math.max(headerText.length * 15, 90)
    }
    return 0
  }

  return (
    <>
      {progress === 0 && (
        <WorkflowTableDropzone handleFileView={handleFileView} />
      )}
      {progress > 0 && (
        <div
          className="workflow-table-upload"
          style={{
            position: "relative",
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "row",
          }}
        >
          {progress > 0 && csvTable && (
            <div
              className="workflow-table-specs"
              style={{
                position: "relative",
                width: "18%",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                transform: "translate(0,-20px)",
              }}
            >
              <div
                style={{
                  width: "75%",
                }}
              >
                <label
                  htmlFor="contextInput"
                  style={{
                    alignSelf: "flex-start",
                    marginTop: "15%",
                    marginBottom: 2,
                  }}
                >
                  Context:
                </label>
                <input
                  type="text"
                  id="contextInput"
                  placeholder={"Enter table context..."}
                  defaultValue={undefined}
                  onChange={handleContextChange} // write nodeName state
                  autoFocus={true}
                />
                {/* <Button type="submit" radius="xl">
                  Upload
                </Button> */}
                <div
                  style={{
                    backgroundColor: hovered ? "#1864ab" : "#1971c2",
                    height: "55%",
                    borderRadius: "5px",
                    border: "2px solid #333",
                    marginTop: 20,
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                  }}
                  onMouseEnter={() => setHovered(true)}
                  onMouseLeave={() => setHovered(false)}
                >
                  {progress === 1 ? (
                    <IconUpload
                      size="3rem"
                      stroke={1.5}
                      onClick={requestExtractLabels}
                    />
                  ) : progress === 2 ? (
                    <IconUpload
                      size="3rem"
                      stroke={1.5}
                      onClick={requestExtractAttributes}
                    />
                  ) : progress === 3 ? (
                    <IconUpload
                      size="3rem"
                      stroke={1.5}
                      onClick={requestExtractNodes}
                    />
                  ) : progress === 4 ? (
                    <IconUpload
                      size="3rem"
                      stroke={1.5}
                      onClick={requestExtractGraph}
                    />
                    ) : (
                    <IconUpload
                      size="3rem"
                      stroke={1.5}
                      onClick={requestImportGraph}
                    />
                  )}
                  {/* Upload */}
                </div>
              </div>
            </div>
          )}
          <div
            ref={tableViewRef}
            className="workflow-table-grid"
            style={{
              position: "relative",
              height: `calc(100%)`,
              overflow: "hidden",
              width: "100%",
            }}
          >
            <MultiGrid
              ref={multiGridRef}
              columnWidth={getColumnWidth} // Adjust as needed
              columnCount={getColumnCount()}
              fixedColumnCount={progress === 1 ? 1 : 0}
              fixedRowCount={1} // One fixed row for headers
              height={tableViewRect ? tableViewRect.height - 5 : 0} // Adjust as needed
              rowHeight={30} // Adjust as needed
              rowCount={getRowCount()} // One header row and one data row
              cellRenderer={cellRenderer}
              width={tableViewRect ? tableViewRect.width - 5 : 0} // Adjust as needed
              // style={{ border: "1px solid #333" }}
            />
          </div>
        </div>
      )}
    </>
  )
}
