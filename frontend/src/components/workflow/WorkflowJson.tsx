import SearchIcon from "@mui/icons-material/Search"
import { GiSpiralLollipop } from "react-icons/gi";

import client from "../../client"
import { saveBlobAsFile } from "../../common/workflowHelpers"
import toast from "react-hot-toast"

interface WorkflowJsonProps {
  workflow: string | null
  setWorkflow: React.Dispatch<React.SetStateAction<string | null>>
  darkTheme: boolean
}

export default function WorkflowJson(props: WorkflowJsonProps) {
  const {
    workflow,
    setWorkflow,
    darkTheme,
  } = props

  async function workflowSearch() {
    try {
      const response = await client.workflowSearch(workflow)
      if (response) {
        saveBlobAsFile(response.data, "workflows.csv")
      }
    } catch (err: any) {
      toast.error(err.message)
    }
  }

  return (
    <>
      <div className="workflow-json-btn-group">
        <SearchIcon onClick={workflowSearch} />
      </div>
      <div
        className="workflow-json-textarea"
        style={{
          position: "relative",
          width: "100%",
          flex: 1,
        }}
      >
        <textarea
          readOnly
          value={workflow ? workflow : "asd"}
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