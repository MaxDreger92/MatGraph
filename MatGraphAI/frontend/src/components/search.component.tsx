import { useState } from "react"

import DoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft'
import DoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight'
import SearchIcon from '@mui/icons-material/Search';

import Canvas from "./canvas/canvas.component"
import client from "../client"
import { saveToFile } from "../common/helpers"

interface SearchProps {
  colorIndex: number
}

export default function Search(props: SearchProps) {
  const { colorIndex } = props
  const [workflow, setWorkflow] = useState<string | null>(null)
  const [splitView, setSplitView] = useState(false)
  const [splitViewWidth, setSplitViewWidth] = useState(0)

  function saveBlobAsFile(blob: Blob, filename: string) {
    if (!(blob instanceof Blob)) {
          console.error("Provided data is not a Blob");
          return;
      }
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  // Asynchronous function to search for a workflow
  async function workflowSearch() {
    try {
      // Call to the client to search for the workflow and get a response
      const response = await client.workflowSearch(workflow);

      // If the search response is successful, save the returned data to a CSV file
      if (response) {
        console.log(response.data);  // log the response data
        saveBlobAsFile(response.data, "workflows.csv");
      }
    } catch (err: any) {
      // Handle errors in the search and throw a new error message
      throw new Error(`Search failed: ${err.message}`);
    }
  }

  const handleSplitView = () => {
    if (splitView) {
      setSplitViewWidth(0)
    } else {
      setSplitViewWidth(450)
    }
    setSplitView(!splitView)
  }

  return(
    <div style={{position: "fixed", display: "flex"}}>
      <Canvas
        colorIndex={colorIndex}
        setWorkflow={setWorkflow}
        style={{
          width: `calc(100vw - ${splitViewWidth}px)`,
          height: "100vh"
        }}
      />
      {splitView && (
        <div
          style={{
            display: "flex",
            flexDirection: "column"
          }}
        >
          <div
            className="wflow-buttons" 
          >
            <SearchIcon onClick={workflowSearch}/>
          </div>
          <div className="wflow-text"> 
            <textarea
              readOnly
              value={workflow ? workflow : "asd"}
              style={{
                width: splitViewWidth,
                height: "100vh",
              }}
            />
          </div>
        </div>
      )}
      <div
        className="canvas-btn-icon" // superfluous atm
        style={{
          position: "absolute",
          top: "42%",
          right: splitView ? splitViewWidth + 10 : 10,
          width: 35,
          height: 35,
        }}
        onClick={handleSplitView}
      >
        {splitView
          ? <DoubleArrowRightIcon style={{color: "#909296", width: "100%", height: "auto"}}/>
          : <DoubleArrowLeftIcon style={{color: "#909296", width: "100%", height: "auto"}}/>
        }
      </div>

    </div>
  )
}