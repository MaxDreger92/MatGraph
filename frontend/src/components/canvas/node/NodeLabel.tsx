import { useEffect, useState } from 'react'
import { INode, ValOpPair } from '../../../types/canvas.types'
import { isAttrDefined } from '../../../common/workflowHelpers'

interface NodeLabelsProps {
    // isEditing: boolean
    isSelected: number
    isValueNode: boolean
    fieldsMissing: boolean
    labelRef: React.RefObject<HTMLDivElement>
    hovered: boolean
    size: number
    name: string
    valOp: ValOpPair
    type: INode['type']
    layer: number
    // hasLabelOverflow: boolean
    color: string
    onMouseUp: (e: React.MouseEvent) => void
}

export default function NodeLabel(props: NodeLabelsProps) {
    const {
        isSelected,
        isValueNode,
        fieldsMissing,
        labelRef,
        hovered,
        size,
        name,
        valOp,
        type,
        layer,
        color,
        onMouseUp,
    } = props

    const [slicedName, setSlicedName] = useState<string>('')
    const [slicedValue, setSlicedValue] = useState<string>('')
    const [isNameSliced, setIsNameSliced] = useState(false)
    const [isValueSliced, setIsValueSliced] = useState(false)
    const [labelHovered, setLabelHovered] = useState(false)
    const [labelFontSize, setLabelFontSize] = useState(16)

    // useEffect(() => {
    //     // set labelFontSize
    // }, [])

    useEffect(() => {
        if (!isAttrDefined(name)) return
        const characterFactor = (16 - labelFontSize) * 0.4 // adjusts the width of characters for sizes other than 16
        const subName = name.substring(0, size / (9.65 - characterFactor)) // 9.65 = width of 1 char in size 16
        if (subName.length < name.length) {
            setIsNameSliced(true)
            setSlicedName(subName.slice(0, -2))
        } else {
            setIsNameSliced(false)
            setSlicedName(name)
        }
    }, [name, size, labelFontSize])

    useEffect(() => {
        if (!valOp?.value || !valOp.operator) return
        const subValue = valOp.value.substring(0, (size - 20) / 8.2) // 8.2 = width of 1 char
        if (subValue.length < valOp.value.length) {
            setIsValueSliced(true)
            setSlicedValue(subValue.slice(0, -2))
        } else {
            setIsValueSliced(false)
            setSlicedValue(valOp.value)
        }
    }, [valOp, size])

    const mapOperatorSign = () => {
        let operatorCode: string
        if (!valOp?.operator) return ''
        switch (valOp.operator) {
            case '<=':
                operatorCode = '\u2264'
                break
            case '>=':
                operatorCode = '\u2265'
                break
            case '!=':
                operatorCode = '\u2260'
                break
            default:
                operatorCode = valOp.operator
                break
        }
        return operatorCode
    }

    return (
        <div className="node-label-none-wrap">
            {/* name label */}
            <div
                className="node-label"
                onMouseUp={onMouseUp}
                onMouseEnter={() => setLabelHovered(true)}
                onMouseLeave={() => setLabelHovered(false)}
                style={{
                    marginTop: isValueNode && isAttrDefined(valOp) ? 3 : 0,
                    marginBottom: isValueNode && isAttrDefined(valOp) ? -3 : 0,
                    color: ['matter', 'measurement', 'metadata', 'simulation'].includes(type)
                        ? '#1a1b1e'
                        : '#ececec',
                    zIndex: layer + 1,
                    display: 'flex',
                    flexDirection: 'row',
                    fontSize: labelFontSize,
                    // cursor: (isSelected === 1 && labelHovered) ? "text" : "inherit" //not sure about that yet
                }}
            >
                {/* name span  */}
                <span>{slicedName}</span>
                {/* additional dotspan if name is sliced  */}
                {isNameSliced && <span className="node-label-dots" children="..." />}
            </div>

            {/* value label  */}
            {isValueNode && isAttrDefined(valOp) && (
                <div
                    className="node-label node-label-value"
                    onMouseUp={onMouseUp}
                    style={{
                        position: 'static',
                        top: name && 'calc(50% + 5px)', //
                        color: ['matter', 'measurement'].includes(type) ? '#1a1b1e' : '#ececec',
                        zIndex: layer + 1,
                    }}
                >
                    {/* operator */}
                    {valOp?.operator && <span children={mapOperatorSign()} />}
                    {/* value */}
                    <span style={{ paddingLeft: 2 }}>{slicedValue}</span>
                    {/* dots */}
                    {isValueSliced && <span className="node-label-dots" children="..." />}
                </div>
            )}
        </div>
    )
}
