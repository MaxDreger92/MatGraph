import { useState } from "react"

import DoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft'
import DoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight'

import Canvas from "./canvas/canvas.component"

interface SearchProps {
  colorIndex: number
}

export default function Search(props: SearchProps) {
  const { colorIndex } = props
  const [workflow, setWorkflow] = useState<string | null>(null)
  const [splitView, setSplitView] = useState(false)
  const [splitViewWidth, setSplitViewWidth] = useState(400)

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
        <div>
          <textarea
            readOnly
            value={workflow ? workflow : "asd"}
            style={{
              width: splitViewWidth,
              height: "100vh",
              backgroundColor: "#25262b",
              position: "relative",
              color: "#A6A7AB"
            }}
          />
        </div>
      )}
      <div
        className="canvas-btn-icon" // superfluous atm
        style={{
          position: "absolute",
          top: "42%",
          right: splitView ? splitViewWidth + 10 : 10,
          width: 40,
          height: 40,
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