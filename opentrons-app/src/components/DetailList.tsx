import { useEffect, useState } from "react"

interface DetailListProps {
    label: string
    value: any
    width: number
}

export default function DetailList(props: DetailListProps) {
    const {
        label,
        value,
        width,
    } = props
    const [capitalizedLabel, setCapitalizedLabel] = useState(label)

    useEffect(() => {
        const newCapitalized = label.charAt(0).toUpperCase() + label.slice(1)
        setCapitalizedLabel(newCapitalized)
    }, [label])

    return (
        <>
            {capitalizedLabel}
            <div
                style={{
                    position: 'relative',
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    marginBottom: 25,
                    boxSizing: 'border-box',
                    marginTop: 10,
                }}
            >
                {Object.entries(value).map(([label, value], index) => {
                    if (typeof value === 'string' || typeof value === 'number') {
                        return (
                            <DetailListElement
                                containerWidth={width}
                                label={label}
                                value={value}
                            />
                        )
                    }
                    return null
                })}
            </div>
        </>
    )
}

interface DetailListElementProps {
    containerWidth: number
    label: string
    value: unknown
}

function DetailListElement(props: DetailListElementProps) {
    const { containerWidth, label, value } = props
    const [hasLinebreak, setHasLinebreak] = useState(false)
    const [printValue, setPrintValue] = useState<number | string>('')

    useEffect(() => {
        if (typeof value === 'number' || typeof value === 'string') {
            setPrintValue(value)
        } else {
            setPrintValue('')
        }
    }, [value])

    useEffect(() => {
        if (containerWidth < 420) {
            setHasLinebreak(true)
        } else {
            setHasLinebreak(false)
        }
    }, [containerWidth])

    return (
        <div
            style={{
                position: 'relative',
                display: 'flex',
                flexDirection: hasLinebreak ? 'column' : 'row',
                width: '100%',
                height: hasLinebreak && printValue ? 70 : 35,
                fontSize: 14,
                backgroundColor: '#e3e3e3',
                marginBottom: hasLinebreak ? 5 : 0,
            }}
        >
            <div
                style={{
                    display: 'flex',
                    flexShrink: 0,
                    width: 190,
                    height: hasLinebreak ? '50%' : '100%',
                    left: 0,
                    paddingLeft: 5,
                    boxSizing: 'border-box',
                    alignItems: 'center',
                    fontWeight: hasLinebreak ? 500 : 400,
                }}
            >
                {label}
            </div>
            <div
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    height: hasLinebreak ? '50%' : '100%',
                    width: '100%',
                    backgroundColor: '#DDD',
                    paddingLeft: hasLinebreak ? 10 : 5,
                    boxSizing: 'border-box',
                    color: hasLinebreak ? '#555' : 'inherit',
                }}
            >
                {printValue}
            </div>
        </div>
    )
}