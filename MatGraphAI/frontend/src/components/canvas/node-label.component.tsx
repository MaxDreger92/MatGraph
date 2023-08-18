import { useEffect, useRef, useState } from "react"
import { INode } from "./types/canvas.types"

interface NodeLabelsProps {
  // isEditing: boolean
  isSelected: number
  isValueNode: boolean
  fieldsMissing: boolean
  nodeLabelRef: React.RefObject<HTMLDivElement>
  nodeHovered: boolean
  nodeSize: number
  nodeDotName: string | undefined
  nodeDotValue: number | undefined
  nodeDotOperator: INode["operator"] | undefined
  nodeType: INode["type"]
  nodeLayer: number
  hasLabelOverflow: boolean
  nodeColor: string
  onMouseUp: (e: React.MouseEvent) => void
}

export default function NodeLabel(props: NodeLabelsProps) {
  const {
    // isEditing,
    isSelected,
    isValueNode,
    fieldsMissing,
    nodeLabelRef,
    nodeHovered,
    nodeSize,
    nodeDotName,
    nodeDotValue,
    nodeDotOperator,
    nodeType,
    nodeLayer,
    hasLabelOverflow,
    nodeColor,
    onMouseUp,
  } = props

  const mapOperatorSign = () => {
    let operatorCode: string
    if (!nodeDotOperator) return ""
    switch (nodeDotOperator) {
      case "<=":
        operatorCode = "\u2264"
        break
      case ">=":
        operatorCode = "\u2265"
        break
      case "!=":
        operatorCode = "\u2260"
        break
      default:
        operatorCode = nodeDotOperator
        break
    }
    return operatorCode
  }

  const nodeNameString = () => {
    if (!nodeDotName) return ""
    if ((!nodeHovered && isSelected !== 1) || fieldsMissing) {
      const subName = nodeDotName.substring(0, nodeSize / 7 - 8)
      if (subName.length < nodeDotName.length) {
        return subName + "..."
      }
    }
    return nodeDotName
  }

  const nodeValueString = () => {
    if (!nodeDotValue) return ""
    const operator = nodeDotOperator ? mapOperatorSign() + " " : ""
    if((!nodeHovered && isSelected !== 1) || fieldsMissing) {
      const subValue = nodeDotValue.toString().substring(0, nodeSize / 7 - 9)
      if (subValue.length < nodeDotValue.toString().length) {
        return operator + subValue + "..."
      }
    }
    return operator + nodeDotValue
  }

  return (
    <div
      className="node-label-wrap"
      ref={nodeLabelRef}
      style={{
        backgroundColor: hasLabelOverflow && (nodeHovered || isSelected > 0)
          ? nodeColor
          : "transparent",
      }}
    >
      <span
        className="node-label"
        onMouseUp={onMouseUp}
        style={{
          marginTop: isValueNode && nodeDotValue !== undefined ? 3 : 0,
          marginBottom:
            isValueNode && nodeDotValue !== undefined ? -3 : 0,
          color: ["matter", "measurement"].includes(nodeType)
            ? "#1a1b1e"
            : "#ececec",
          zIndex: nodeLayer + 1,
        }}
      >
        {nodeNameString()}
      </span>
      {nodeDotValue !== undefined && (
        <span
          className="node-label node-label-value"
          onMouseUp={onMouseUp}
          style={{
            position: "static",
            top: nodeDotName && "calc(50% + 5px)", //might be a problem
            color: ["matter", "measurement"].includes(nodeType)
              ? "#1a1b1e"
              : "#ececec",
            zIndex: nodeLayer + 1
          }}
        >
          {nodeValueString()}
        </span>
      )}
    </div>
  )
}

interface NodeLabelOutlineProps {}

export function NodeLabelOutline(props: NodeLabelOutlineProps) {}
