import { useState } from "react"

import DoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft'
import DoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight'
import SearchIcon from '@mui/icons-material/Search';

import Canvas from "./canvas/canvas.component"
import client from "../client"
import { saveToFile, saveBlobAsFile } from "../common/helpers"

interface SearchProps {
  colorIndex: number
}

export default function Search(props: SearchProps) {
  const { colorIndex } = props
  const [workflow, setWorkflow] = useState<string | null>(null)
  const [splitView, setSplitView] = useState(false)
  const [splitViewWidth, setSplitViewWidth] = useState(0)

  async function workflowSearch() {
    try {
      const response = await client.workflowSearch(workflow)
      if (response) {
        saveBlobAsFile(response.data, "workflows.csv")
      }
    } catch (err: any) {
      throw new Error("Search failed: " + err.message)
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