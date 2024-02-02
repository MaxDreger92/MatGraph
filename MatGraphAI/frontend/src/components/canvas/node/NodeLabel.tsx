import { useEffect, useState } from "react"
import { INode, ValOpPair } from "../../../types/canvas.types"
import { isAttrDefined } from "../../../common/helpers"

interface NodeLabelsProps {
  // isEditing: boolean
  isSelected: number
  isValueNode: boolean
  fieldsMissing: boolean
  labelRef: React.RefObject<HTMLDivElement>
  hovered: boolean
  size: number
  name: string
  value: ValOpPair
  type: INode["type"]
  layer: number
  // hasLabelOverflow: boolean
  color: string
  onMouseUp: (e: React.MouseEvent) => void
}

export default function NodeLabel(props: NodeLabelsProps) {
  const [slicedName, setSlicedName] = useState<string>("")
  const [slicedValue, setSlicedValue] = useState<string>("")
  const [isNameSliced, setIsNameSliced] = useState(false)
  const [isValueSliced, setIsValueSliced] = useState(false)
  const [labelHovered, setLabelHovered] = useState(false)
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
    type,
    layer,
    // hasLabelOverflow,
    color,
    onMouseUp,
  } = props

  useEffect(() => {
    if (!isAttrDefined(name)) return
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
    if (!value?.value || !value.operator) return
    const subValue = value.value.substring(0, (size - 20) / 8.2) // 8.2 = width of 1 char
    if (subValue.length < value.value.length) {
      setIsValueSliced(true)
      setSlicedValue(subValue.slice(0,-2))
    } else {
      setIsValueSliced(false)
      setSlicedValue(value.value)
    }
  }, [value, size])

  const mapOperatorSign = () => {
    let operatorCode: string
    if (!value?.operator) return ""
    switch (value.operator) {
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
        operatorCode = value.operator
        break
    }
    return operatorCode
  }


  return (
    <div
      className="node-label-none-wrap"
    >
      {/* name label */}
      <div
        className="node-label"
        onMouseUp={onMouseUp}
        onMouseEnter={() => setLabelHovered(true)}
        onMouseLeave={() => setLabelHovered(false)}
        style={{
          marginTop: isValueNode && isAttrDefined(value) ? 3 : 0,
          marginBottom: isValueNode && isAttrDefined(value) ? -3 : 0,
          color: ["matter", "measurement", "metadata"].includes(type)
            ? "#1a1b1e"
            : "#ececec",
          zIndex: layer + 1,
          display: "flex",
          flexDirection: "row",
          // cursor: (isSelected === 1 && labelHovered) ? "text" : "inherit" //not sure about that yet
        }}
      >
        {/* name span  */}
        <span>
          {slicedName}
        </span>
        {/* additional dotspan if name is sliced  */}
        {isNameSliced &&
          <span className="node-label-dots" children="..." />
        }
      </div>

        {/* value label  */}
      {(isValueNode && isAttrDefined(value)) && (
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
          {value?.operator && 
            <span children={mapOperatorSign()}/>
          }
          {/* value */}
          <span style={{paddingLeft: 2}}>
            {slicedValue}
          </span>
          {/* dots */}
          {isValueSliced &&
            <span className="node-label-dots" children="..." />
          }
        </div>
      )}
    </div>
  )
}
