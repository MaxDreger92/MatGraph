import React, { useContext, useEffect, useRef, useState } from 'react'
import { OpentronsContext } from '../context/OpentronsContext'
import Labware from './Labware'
import { isLabwareInSlot } from '../functions/configuration.functions'
import { getLabwareDataFromList } from '../functions/labware.functions'
import { ILabware, IWell } from '../types/labware.types'
import DetailList from './DetailList'
import { Chemical } from '../types/configuration.types'
import ChemicalList from './ChemicalList'

interface DetailProps {}

export default function Detail(props: DetailProps) {
    const [labware, setLabware] = useState<ILabware | null>()
    const [renderedComponent, setRenderedComponent] = useState<React.FC<any> | null>(null)
    const [componentProps, setComponentProps] = useState<any>(null)
    const [itemSize, setItemSize] = useState({ width: 0, height: 0 })
    const [selectedWell, setSelectedWell] = useState<string | null>(null)
    const [chemicalsInWell, setChemicalsInWell] = useState<Chemical[]>([])
    const containerRef = useRef(null)

    const { currentConfig, labwareList, selectedSlot } = useContext(OpentronsContext)

    useEffect(() => {
        if (selectedSlot && isLabwareInSlot(currentConfig.opentronsSetup, selectedSlot)) {
            const labwareData = getLabwareDataFromList(selectedSlot, labwareList, currentConfig.opentronsSetup)
            if (!labwareData) return
            setLabware(labwareData)
            setComponentProps({ slot: selectedSlot, labware: labwareData, selectedWell, setSelectedWell })
            setRenderedComponent(() => Labware)
        } else {
            setLabware(null)
            setComponentProps(null)
            setRenderedComponent(null)
        }
    }, [selectedSlot, currentConfig, labwareList, selectedWell])

    useEffect(() => {
        if (!selectedWell) return
        if (currentConfig.chemicalSetup.opentrons.length === 0) return

        const filteredChemicals = currentConfig.chemicalSetup.opentrons.filter((chemical) => {
            return chemical.location.slot === selectedSlot && chemical.location.well === selectedWell
        })

        setChemicalsInWell(filteredChemicals)
    }, [selectedSlot, selectedWell, currentConfig.chemicalSetup])

    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                const { offsetWidth } = containerRef.current
                setItemSize({ width: offsetWidth * 0.9, height: offsetWidth * 0.56 })
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
            className='ref'
            ref={containerRef}
            style={{
                position: 'relative',
                height: `calc(96% - 10px)`,
                width: `calc(100% - 20px)`,
                backgroundColor: '#f5f5f5',
                borderRadius: '8px',
                filter: 'drop-shadow(0px 2px 5px rgba(0, 0, 0, 0.15))',
                display: selectedSlot ? 'flex' : 'none',
                flexDirection: 'column',
                alignItems: 'center',
                overflow: 'hidden',
                padding: 5,
            }}
        >
            {/* Header */}
            <span
                className='noselect'
                style={{
                    display: 'block',
                    fontSize: '120%',
                    marginLeft: 5,
                    paddingBottom: 6,
                    pointerEvents: 'none',
                    alignSelf: 'flex-start',
                }}
            >
                Details
            </span>

            {/* Content */}
            <div
                style={{
                    position: 'relative',
                    display: 'flex',
                    flexDirection: 'column',
                    backgroundColor: '#EEE',
                    borderRadius: 5,
                    overflow: 'hidden',
                    width: '100%',
                    height: '100%',
                    alignItems: 'center',
                    padding: '4%',
                    boxSizing: 'border-box',
                }}
            >
                <div // Equipment Component
                    style={{
                        position: 'relative',
                        width: `${itemSize.width}px`,
                        height: `${itemSize.height}px`,
                        flexShrink: 0,
                        display: 'flex',
                        alignItems: 'center',
                        marginTop: 20,
                    }}
                >
                    {renderedComponent && React.createElement(renderedComponent, componentProps)}
                </div>

                <div // Info
                    style={{
                        position: 'relative',
                        width: '100%',
                        marginTop: 40,
                        display: 'flex',
                        flexDirection: 'column',
                        overflowY: 'auto',
                    }}
                >
                    {labware && // Labware Info
                        !selectedWell &&
                        Object.entries(labware).map(([key, value], index) => {
                            let labwareEntry = value
                            if (key === 'wells') {
                                const firstWell = Object.values(labwareEntry)[0] as IWell
                                if (!firstWell) return null
                                labwareEntry = {
                                    depth: firstWell.depth,
                                    totalLiquidVolume: firstWell.totalLiquidVolume,
                                    shape: firstWell.shape,
                                    diameter: firstWell.diameter,
                                }
                            }
                            if (KEYS_TO_DISPLAY.includes(key)) {
                                return <DetailList label={key} value={labwareEntry} width={itemSize.width} />
                            }
                            return null
                        })}
                    {labware && selectedWell && ( // Selected Well Info
                        <DetailList label={selectedWell} value={labware.wells[selectedWell]} width={itemSize.width} />
                    )}
                    {selectedWell && chemicalsInWell && ( // Selected Well Chemicals
                        <ChemicalList wellVolume={} chemicals={chemicalsInWell} width={itemSize.width}/>
                    )}
                </div>
            </div>
        </div>
    )
}

const KEYS_TO_DISPLAY = ['brand', 'metadata', 'dimensions', 'wells', 'parameters']
