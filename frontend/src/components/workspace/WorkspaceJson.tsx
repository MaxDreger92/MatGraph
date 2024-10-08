import SearchIcon from "@mui/icons-material/Search"
import { GiSpiralLollipop } from "react-icons/gi";

import client from "../../client"
import { saveBlobAsFile } from "../../common/workspaceHelpers"
import toast from "react-hot-toast"

interface WorkspaceJsonProps {
  graph: string | null
  jsonView: boolean
  darkTheme: boolean
}

export default function WorkspaceJson(props: WorkspaceJsonProps) {
  const {
    graph,
    jsonView,
    darkTheme,
  } = props

  return (
    <>
      <div
        className="workspace-json"
        style={{
          position: "relative",
          width: 450,
          flex: 1,
          paddingTop: 15,
          display: jsonView ? 'block' : 'none',
        }}
      >
        <textarea
          readOnly
          value={graph ? graph : ""}
          style={{
            position:"relative",
            top: 0,
            width: "100%",
            height: "100%",
            resize: "none",
            color: darkTheme ? "#a6a7ab" : "#040404"
          }}
        />
      </div>
    </>
  )
}