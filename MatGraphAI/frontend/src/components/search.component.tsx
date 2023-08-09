import { useState } from "react"

import DoubleArrowLeftIcon from '@mui/icons-material/KeyboardDoubleArrowLeft'
import DoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight'

import Canvas from "./canvas/canvas.component"

interface SearchProps {
  colorIndex: number
}

export default function Search(props: SearchProps) {
  const { colorIndex } = props
  const [workflow, setWorkflow] = useState<JSON | null>(null)
  const [splitView, setSplitView] = useState(false)

  return(
    <div style={{position: "fixed", display: "flex"}}>
      <Canvas colorIndex={colorIndex} setWorkflow={setWorkflow}/>
      {splitView && (
        <div>
          <textarea
            readOnly
            value={workflow ? JSON.stringify(workflow, null, 2) : ""}
            style={{
              width: "400px", height: "100vh"
            }}
          />
        </div>
      )}
    </div>
  )
}