import { useEffect, useState } from "react"
import { Configuration } from "../types/configuration.types"

interface SetupListProps {
    currentConfig: Configuration
    numSetups: number
    header: string
    type: string
    setupList: any[]
    setActiveSetup: (type: string, index: number) => void
}

export default function SetupList(props: SetupListProps) {
    const {
        currentConfig,
        numSetups,
        header,
        type,
        setupList,
        setActiveSetup,
    } = props

    const [activeIndex, setActiveIndex] = useState<number | null>()

    const handleSetActiveSetup = (index: number) => {
        setActiveSetup(type, index)
        setActiveIndex(index)
    }

    useEffect(() => {
        switch (type) {
            case 'opentrons':
                if (!currentConfig.opentronsSetup.name) {
                    setActiveIndex(null)
                }
                break
            case 'chemicals':
                if (!currentConfig.chemicalSetup.name) {
                    setActiveIndex(null)
                }
                break
            default:
                return
        }
    }, [currentConfig, type])

    return (
        <div
            style={{
                position: 'relative',
                width: `calc(100%/${numSetups})`,
                height: `calc(100% - 10px)`,
                margin: 5,
                overflow: 'hidden'
            }}
        >
            {/* Header */}
            <span
                style={{
                    display: 'block',
                    fontSize: '120%',
                    pointerEvents: 'none',
                    marginLeft: 5,
                    paddingBottom: 6,
                }}
            >
                {header}
            </span>

            {/* Setup List */}
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifySelf: 'flex-start',
                    cursor: 'pointer',
                    overflow: 'auto',
                    height: '100%'
                }}
            >
                {setupList.map((setup, index) => {
                    return (
                        <div
                            onClick={() => handleSetActiveSetup(index)}
                            style={{
                                width: '100%',
                                backgroundColor: activeIndex === index ? '#DDD' : 'transparent',
                                paddingBottom: 8,
                                borderRadius: 5,
                            }}
                        >
                            <span
                                style={{
                                    position: 'relative',
                                    top: 3,
                                    marginLeft: 5,
                                }}
                            >
                                {setup.name}
                            </span>
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
