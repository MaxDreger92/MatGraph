import { useState } from "react"
import { IWorkflow } from "../../types/workflow.types"
import { IRelationship, INode } from "../../types/canvas.types"
import { convertFromJsonFormat } from "../../common/helpers"
import { RiDeleteBin2Line } from "react-icons/ri"

// import jsonData from '../../alt/testGraph.json'

interface WorkflowHistoryProps {
  uploadMode: boolean
  workflows: IWorkflow[] | undefined
  deleteWorkflow: (workflowId: string) => void
  setNodes: React.Dispatch<React.SetStateAction<INode[]>>
  setRelationships: React.Dispatch<React.SetStateAction<IRelationship[]>>
  setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
  canvasWidth: number
  canvasHeight: number
}

export default function WorkflowHistory(props: WorkflowHistoryProps) {
  const {
    uploadMode,
    workflows,
    deleteWorkflow,
    setNodes,
    setRelationships,
    setNeedLayout,
    canvasWidth,
    canvasHeight,
  } = props
  const [hovered, setHovered] = useState<number | undefined>()
  const [trashHovered, setTrashHovered] = useState(false)

  // const loadJson = () => {
  //   setNodesAndRelationships(JSON.stringify(jsonData))
  // }

  const setNodesAndRelationships = (workflow: string) => {
    const { nodes, relationships } = convertFromJsonFormat(workflow, uploadMode)
    setNodes(nodes)
    setRelationships(relationships)
    setNeedLayout(true)
  }

  const handleDeleteWorkflow = (e: React.MouseEvent, index: number) => {
    e.stopPropagation()
    if (!workflows) return
    deleteWorkflow(workflows[index]._id)
  }

  return (
    <div
      className="workflow-list"
      style={{
        paddingTop: 15,
        paddingLeft: 10,
        paddingRight: 10,
      }}
    >
      {/* <div
        style={{
          height: 50,
          width: "100%",
          backgroundColor: '#ff0000'
        }}
        onClick={loadJson}
      >
      </div> */}
      
      {workflows &&
        workflows.map((workflow, index) => (
          <div
            key={index}
            style={{
              position: "relative",
              width: "100%",
              height: 50,
              backgroundColor: hovered === index ? "#373A40" : "transparent",
              justifyContent: "center",
              display: "flex",
              flexDirection: "column",
              marginBottom: 10,
              paddingLeft: 10,
              borderRadius: "5px",
              cursor: "pointer",
            }}
            onMouseEnter={() => setHovered(index)}
            onMouseLeave={() => setHovered(undefined)}
            onClick={() => setNodesAndRelationships(workflow.workflow)}
          >
            {hovered === index && (
              <RiDeleteBin2Line
                style={{
                  position: "absolute",
                  right: "5%",
                  fontSize: 20,
                  top: 14,
                  color: trashHovered ? "#ff0000" : "#909296"
                }}
                onMouseEnter={() => setTrashHovered(true)}
                onMouseLeave={() => setTrashHovered(false)}
                onClick={(e) => handleDeleteWorkflow(e, index)}
              />
            )}
            <span
              style={{
                textAlign: "left",
                color: "inherit",
                fontSize: 16,
                fontWeight: "bold",
                userSelect: "none",
              }}
            >
              Workflow {index + 1}
            </span>
            <span
              style={{
                textAlign: "left",
                color: "inherit",
                fontSize: 14,
                userSelect: "none",
              }}
            >
              {new Date(workflow.timestamp).toLocaleString()}
            </span>
          </div>
        ))}
    </div>
  )
}
