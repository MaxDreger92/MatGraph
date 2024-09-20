import { useEffect, useRef, useState } from 'react'
import { ChemicalSetup, Configuration, OpentronsSetup } from '../types/configuration.types'
import SetupList from './SetupList'

interface SetupMenuProps {
    opentronsSetupList: OpentronsSetup[]
    chemicalSetupList: ChemicalSetup[]
    setActiveSetup: (type: string, index: number) => void
    currentConfig: Configuration
}

export default function SetupMenu(props: SetupMenuProps) {
    const { opentronsSetupList, chemicalSetupList, setActiveSetup, currentConfig } = props

    const [setupMenuSize, setSetupMenuSize] = useState<{ width: number; height: number }>({ width: 0, height: 0 })
    const containerRef = useRef(null)

    const handleSetActiveSetup = (type: string, index: number) => {
        setActiveSetup(type, index)
    }

    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                const { offsetWidth, offsetHeight } = containerRef.current
                const height = Math.min(offsetHeight - offsetWidth - 40, offsetHeight * 0.22)
                setSetupMenuSize({ width: offsetWidth, height: height })
            }
        }

        updateSize()

        const resizeObserver = new ResizeObserver(() => {
            updateSize()
        })

        const currentRef = containerRef.current
        if (currentRef) {
            resizeObserver.observe(currentRef)
        }

        return () => {
            if (currentRef) {
                resizeObserver.unobserve(currentRef)
            }
        }
    }, [])

    return (
        <div
            ref={containerRef}
            style={{
                position: 'relative',
                width: '100%',
                height: '100%',
            }}
        >
            <div
                className='setup-list'
                style={{
                    position: 'relative',
                    width: setupMenuSize.width,
                    height: setupMenuSize.height,
                    backgroundColor: '#f5f5f5',
                    borderRadius: '8px',
                    filter: 'drop-shadow(0px 2px 5px rgba(0, 0, 0, 0.15))',
                    display: 'flex',
                    flexDirection: 'row',
                }}
            >
                <SetupList
                    numSetups={2}
                    header='Opentrons Setup'
                    type='opentrons'
                    setupList={opentronsSetupList}
                    setActiveSetup={handleSetActiveSetup}
                    currentConfig={currentConfig}
                />
                <SetupList
                    numSetups={2}
                    header='Chemicals'
                    type='chemicals'
                    setupList={chemicalSetupList}
                    setActiveSetup={handleSetActiveSetup}
                    currentConfig={currentConfig}
                />
            </div>
        </div>
    )
}
