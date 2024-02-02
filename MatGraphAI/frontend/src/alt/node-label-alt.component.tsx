import { useEffect, useRef, useState } from "react"
import { INode } from "./types/canvas.types"

interface NodeLabelsProps {
  // isEditing: boolean
  isSelected: number
  isValueNode: boolean
  fieldsMissing: boolean
  labelRef: React.RefObject<HTMLDivElement>
  hovered: boolean
  size: number
  name: string | undefined
  value: number | undefined
  operator: INode["operator"] | undefined
  type: INode["type"]
  layer: number
  hasLabelOverflow: boolean
  color: string
  onMouseUp: (e: React.MouseEvent) => void
}

export default function NodeLabel(props: NodeLabelsProps) {
  const [slicedName, setSlicedName] = useState<string>("")
  const [slicedValue, setSlicedValue] = useState<string>("")
  const [isNameSliced, setIsNameSliced] = useState(false)
  const [isValueSliced, setIsValueSliced] = useState(false)
  const {
    // isEditing,
    isSelected,
    isValueNode,
    fieldsMissing,
    labelRef,
    hovered,
    size,
    name,
    value,
    operator,
    type,
    layer,
    hasLabelOverflow,
    color,
    onMouseUp,
  } = props

  useEffect(() => {
    if (!name) return
    const subName = name.substring(0, size / 9.65) // 9.65 = width of 1 char
    if (subName.length < name.length) {
      setIsNameSliced(true)
      setSlicedName(subName.slice(0, -2))
    } else {
      setIsNameSliced(false)
      setSlicedName(name)
    }
  }, [name, size])

  useEffect(() => {
    if (!value) return
    const valueString = value.toString()
    const subValue = valueString.substring(0, (size - 20) / 8.2) // 8.2 = width of 1 char
    if (subValue.length < valueString.length) {
      setIsValueSliced(true)
      setSlicedValue(subValue.slice(0,-2))
    } else {
      setIsValueSliced(false)
      setSlicedValue(valueString)
    }
  }, [value, size])

  const mapOperatorSign = () => {
    let operatorCode: string
    if (!operator) return ""
    switch (operator) {
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
        operatorCode = operator
        break
    }
    return operatorCode
  }


  return (
    <div
      className="node-label-wrap"
      ref={labelRef}
      style={{
        backgroundColor:
          hasLabelOverflow && (hovered || isSelected === 1)
            ? color
            : "transparent",
      }}
    >
      <div // name label
        className="node-label"
        onMouseUp={onMouseUp}
        style={{
          marginTop: isValueNode && value !== undefined ? 3 : 0,
          marginBottom: isValueNode && value !== undefined ? -3 : 0,
          color: ["matter", "measurement"].includes(type)
            ? "#1a1b1e"
            : "#ececec",
          zIndex: layer + 1,
          display: "flex",
          flexDirection: "row"
        }}
      >
        <span>
          {(hovered || isSelected === 1) && !fieldsMissing
            ? name
            : slicedName}
        </span>
        {(isNameSliced && ((!hovered && isSelected !== 1) || fieldsMissing)) &&
          <span className="node-label-dots" children="..." />
        }
      </div>

      {(isValueNode && value !== undefined) && (
        <div
          className="node-label node-label-value"
          onMouseUp={onMouseUp}
          style={{
            position: "static",
            top: name && "calc(50% + 5px)", //
            color: ["matter", "measurement"].includes(type)
              ? "#1a1b1e"
              : "#ececec",
            zIndex: layer + 1,
          }}
        >
          {/* operator */}
          {operator && 
            <span children={mapOperatorSign()}/>
          }
          {/* value */}
          <span>
            {(hovered || isSelected === 1) && !fieldsMissing
              ? value
              : slicedValue}
          </span>
          {/* dots */}
          {(isValueSliced && ((!hovered && isSelected !== 1) || fieldsMissing)) &&
            <span className="node-label-dots" children="..." />
          }
        </div>
      )}
    </div>
  )
}

interface NodeLabelOutlineProps {
  width?: number
  height?: number
  color: string
  layer: number
}

export function NodeLabelOutline(props: NodeLabelOutlineProps) {
  const { width, height, color, layer } = props

  return (
    <div
      style={{
        position: "absolute",
        width: width ? width - 2 : 0,
        height: height,
        maxWidth: "none",
        borderRadius: 3,
        outlineColor: color,
        outlineStyle: "solid",
        outlineWidth: 4,
        zIndex: layer - 1,
      }}
    />
  )
}
