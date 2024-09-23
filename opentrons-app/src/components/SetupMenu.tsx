import { useEffect, useRef, useState } from 'react'
import { ChemicalSetup, Configuration, OpentronsSetup } from '../types/configuration.types'
import SetupList from './SetupList'

interface SetupMenuProps {
    opentronsSetupList: OpentronsSetup[]
    chemicalSetupList: ChemicalSetup[]
    setActiveSetup: (type: string, index: number) => void
    currentConfig: Configuration
    createSetup: (type: string, name: string) => void
    saveSetup: (type: string, index: number) => void
}

export default function SetupMenu(props: SetupMenuProps) {
    const { opentronsSetupList, chemicalSetupList, setActiveSetup, currentConfig, createSetup, saveSetup } = props

    const [setupMenuSize, setSetupMenuSize] = useState<{ width: number; height: number }>({ width: 0, height: 0 })
    const containerRef = useRef(null)

    const handleSetActiveSetup = (type: string, index: number) => {
        setActiveSetup(type, index)
    }

    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                const { offsetWidth, offsetHeight } = containerRef.current
                const height = Math.min(offsetHeight - offsetWidth - (offsetHeight * 0.04), offsetHeight * 0.22)
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
                width: `calc(100% - 10px)`,
                height: '100%',
            }}
        >
            {(opentronsSetupList.length > 0 || chemicalSetupList.length > 0) && <div
                className='setup-list'
                style={{
                    position: 'relative',
                    width: setupMenuSize.width,
                    height: setupMenuSize.height + 2,
                    backgroundColor: '#f5f5f5',
                    borderRadius: '8px',
                    filter: 'drop-shadow(0px 2px 5px rgba(0, 0, 0, 0.15))',
                    display: 'flex',
                    flexDirection: 'row',
                    padding: 5,
                }}
            >
                <SetupList
                    numSetups={2}
                    header='Opentrons Setup'
                    type='opentrons'
                    setupList={opentronsSetupList}
                    setActiveSetup={handleSetActiveSetup}
                    currentConfig={currentConfig}
                    createSetup={createSetup}
                    saveSetup={saveSetup}
                />
                <div style={{ width: 5 }}></div>
                <SetupList
                    numSetups={2}
                    header='Chemicals'
                    type='chemicals'
                    setupList={chemicalSetupList}
                    setActiveSetup={handleSetActiveSetup}
                    currentConfig={currentConfig}
                    createSetup={createSetup}
                    saveSetup={saveSetup}
                />
            </div>}
        </div>
    )
}
