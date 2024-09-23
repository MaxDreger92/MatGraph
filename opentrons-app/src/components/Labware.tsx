import React, { useContext, useState, useEffect, useRef, useCallback } from 'react'
import { useDrag } from 'react-dnd'
import { ILabware, IWell } from '../types/labware.types'
import { OpentronsContext } from '../context/OpentronsContext'
import { generateLabwareWells, transposeWells } from '../functions/labware.functions'
import chroma from 'chroma-js'
import { labwareColors } from '../data/labware.data'
import { Chemical } from '../types/configuration.types'
import Well from './Well'

interface LabwareProps {
    slot: number
    labware: ILabware
    selectedWell?: string | null
    setSelectedWell?: React.Dispatch<React.SetStateAction<string | null>>
}

export default function Labware(props: LabwareProps) {
    const { slot, labware, selectedWell, setSelectedWell } = props
    const [labwareType, setLabwareType] = useState('tipRack')
    const [layout, setLayout] = useState({ rows: 0, cols: 0 })
    const [wells, setWells] = useState<{ [key: string]: Chemical[] | null }>()
    const [wellShape, setWellShape] = useState<{ shape: string; orientation?: string; shrinkFactor?: number }>({
        shape: 'circular',
    })
    const [wellSize, setWellSize] = useState<{ width: number; height: number }>({ width: 0, height: 0 })
    const [fontSize, setFontSize] = useState(10)

    const [isHovered, setIsHovered] = useState(false)
    const [highlightedWell, setHighlightedWell] = useState<string | null>(null)

    const wellBoundsRef = useRef<HTMLDivElement | null>(null)
    const labwareDraggableRef = useRef<HTMLDivElement | null>(null)

    const { currentConfig, selectedSlot, setSelectedSlot } = useContext(OpentronsContext)

    const [{ isDragging }, drag] = useDrag({
        type: slot === 0 ? 'LABWARE' : '',
        item: labware,
        collect: (monitor) => ({
            isDragging: !!monitor.isDragging(),
        }),
    })

    useEffect(() => {
        if (labwareDraggableRef.current) {
            drag(labwareDraggableRef.current)
        }
    }, [drag])

    const updateSize = useCallback(() => {
        if (wellBoundsRef.current) {
            const wellBoundsWidth = wellBoundsRef.current.offsetWidth
            const wellBoundsHeight = wellBoundsRef.current.offsetHeight

            setWellSize((prevWellSize) => {
                const maxWellWidth = wellBoundsWidth / layout.cols
                const maxWellHeight = wellBoundsHeight / layout.rows
                if (wellShape.shape === 'circular') {
                    const maxWellSize = Math.min(maxWellWidth, maxWellHeight)
                    return { width: maxWellSize - 2, height: maxWellSize - 2 }
                } else if (wellShape.orientation && wellShape.shrinkFactor) {
                    let wellWidth =
                        wellShape.orientation === 'horizontal' ? maxWellWidth : maxWellHeight * wellShape.shrinkFactor
                    let wellHeight =
                        wellShape.orientation === 'vertical' ? maxWellHeight : maxWellWidth * wellShape.shrinkFactor
                    if (wellWidth > maxWellWidth) {
                        wellWidth *= maxWellWidth / wellWidth
                    }
                    if (wellHeight > maxWellHeight) {
                        wellHeight *= maxWellHeight / wellHeight
                    }
                    return { width: wellWidth - 2, height: wellHeight - 2 }
                } else {
                    return prevWellSize
                }
            })

            const newFontSize = Math.min(wellBoundsWidth / (layout.cols * 2.8), 13)
            setFontSize(newFontSize)
        }
    }, [layout, wellShape])

    useEffect(() => {
        if (!wellBoundsRef.current) return

        updateSize()

        const resizeObserver = new ResizeObserver(() => {
            updateSize()
        })

        resizeObserver.observe(wellBoundsRef.current)

        return () => {
            resizeObserver.disconnect()
        }
    }, [wellBoundsRef, updateSize])

    useEffect(() => {
        updateSize()
    }, [updateSize])

    const setupWellShape = (blueprintWell: IWell) => {
        setWellShape((prevShape) => {
            const shape = blueprintWell.shape
            const newWellShape: { shape: string; orientation?: string; shrinkFactor?: number } = { shape: shape }

            if (shape === 'rectangular' && blueprintWell.xDimension && blueprintWell.yDimension) {
                const orientation = blueprintWell.xDimension - blueprintWell.yDimension > 0 ? 'horizontal' : 'vertical'
                const shrinkFactor =
                    Math.min(blueprintWell.xDimension, blueprintWell.yDimension) /
                    Math.max(blueprintWell.xDimension, blueprintWell.yDimension)

                newWellShape.orientation = orientation
                newWellShape.shrinkFactor = shrinkFactor
            }

            return newWellShape
        })
    }

    const setupWells = useCallback(() => {
        const updatedWells = generateLabwareWells(layout.rows, layout.cols)
        setWells((prevWells) => {
            if (!prevWells) {
                return updatedWells
            }

            Object.keys(prevWells).forEach((key) => {
                if (updatedWells[key] && prevWells[key] !== null) {
                    updatedWells[key] = prevWells[key]
                }
            })

            return updatedWells
        })
    }, [layout])

    const setupLayout = useCallback((ordering: string[][]) => {
        const rows = Math.max(...ordering.map((col) => col.length))
        const cols = ordering.length
        setLayout((prevLayout) => {
            if (prevLayout.rows !== rows || prevLayout.cols !== cols) {
                return { rows, cols }
            }
            return prevLayout
        })
    }, [])

    // On labware update
    useEffect(() => {
        setupLayout(labware.ordering)
        setupWells()
        setupWellShape(labware.wells['A1'])
        setLabwareType(labware.metadata.displayCategory)
    }, [slot, labware, setupWells, setupLayout])

    // On chemicalSetup update
    useEffect(() => {
        setWells((prevWells) => {
            if (!prevWells || Object.entries(prevWells).length === 0) return prevWells

            const updatedWells = generateLabwareWells(layout.rows, layout.cols)

            const chemicalsInSlot = currentConfig.chemicalSetup.opentrons.filter((chemical) => {
                return chemical.location.slot === slot
            })

            if (chemicalsInSlot.length === 0) {
                return updatedWells
            }

            chemicalsInSlot.forEach((chemical) => {
                const well = chemical.location.well
                if (updatedWells[well] === undefined) return

                if (updatedWells[well] === null) {
                    updatedWells[well] = []
                }

                updatedWells[well]?.push(chemical)
            })

            return updatedWells
        })
    }, [currentConfig.chemicalSetup, slot, layout])

    useEffect(() => {
        if (!setSelectedWell) return
        setSelectedWell(null)
    }, [selectedSlot, setSelectedWell])

    const getWellLabel = (chemicals: Chemical[] | null, key: string): string => {
        if (!chemicals) {
            return key
        }

        let label = chemicals[0].name
        return chemicals.length > 1 ? label.concat('...') : label
    }

    const handleSelectWell = useCallback(
        (wellKey: string | null) => {
            if (setSelectedWell) {
                if (selectedWell === wellKey) {
                    setSelectedWell(null)
                    return
                }
                setSelectedWell(wellKey)
            }
        },
        [selectedWell, setSelectedWell]
    )

    const handleWellClick = (e: React.MouseEvent, wellKey: string) => {
        if (!setSelectedWell) return
        e.stopPropagation()
        handleSelectWell(wellKey)
    }

    const showChart = (): boolean => {
        return wellSize.width + wellSize.height > 96
    }

    const getEdgeBackgroundGradient = () => {
        const gradient = `linear-gradient(
            to left,
            ${chroma(labwareColors[labwareType]).darken(0.6).hex()} 0%,
            ${chroma(labwareColors[labwareType]).darken(0.3).hex()} 2%,
            ${chroma(labwareColors[labwareType]).darken(0.3).hex()} 98%,
            ${chroma(labwareColors[labwareType]).darken(0.6).hex()} 100%
        )`
        return gradient
    }

    const isHighlighted = (wellKey: string): boolean => {
        return !!setSelectedWell && (highlightedWell === wellKey || selectedWell === wellKey)
    }

    return (
        <div // Overall deck slot bounds, hoverable
            ref={labwareDraggableRef}
            className='labware-component'
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            style={{
                position: 'absolute',
                display: 'flex',
                width: '100%',
                height: '100%',
                justifyContent: 'center',
                alignItems: 'center',
                cursor: slot === 0 ? (isDragging ? 'grabbing' : 'grab') : 'pointer',
            }}
        >
            <div // Shadow, 3d-effect
                style={{
                    top: selectedSlot === slot || isHovered ? '5%' : '3.5%',
                    position: 'absolute',
                    width: '100%',
                    height: '100%',
                    borderRadius: '2% / 3.2%',
                    backgroundColor: '#BBBBBB80',
                }}
            ></div>
            <div // 3d-edge (bottom side)
                style={{
                    top: '3%',
                    position: 'absolute',
                    width: '100%',
                    height: '100%',
                    borderRadius: '2% / 3.2%',
                    background: getEdgeBackgroundGradient(),
                    border: `1px solid #BBB`,
                    filter: `drop-shadow(0px 1px 2px #BBB)`,
                }}
            ></div>
            <div // Labware surface, transformed by isHovered, clickable to select labware
                onClick={() => {
                    setSelectedSlot(slot)
                    handleSelectWell(null)
                }}
                className='labware'
                style={{
                    display: 'flex',
                    backgroundColor: labwareColors[labwareType],
                    transform: selectedSlot === slot || isHovered ? 'translate(0, -3%)' : 'none',
                    padding: '2% 1.5%', // insets well bounds
                    boxSizing: 'border-box',

                }}
            >
                <div // Wells bounds, wells grid
                    ref={wellBoundsRef}
                    className='grid-container'
                    style={{
                        width: '100%',
                        height: '100%',
                        display: 'grid',
                        gridTemplateColumns: `repeat(${layout.cols}, ${wellSize.width + 1}px)`,
                        gridTemplateRows: `repeat(${layout.rows}, ${wellSize.height + 1}px)`,
                        gap: '1px',
                        justifyContent: 'center',
                        alignContent: 'center',
                    }}
                >
                    {wells &&
                        Object.entries(wells).map(([wellKey, chemicals], index) => (
                            <div
                                key={wellKey}
                                style={{
                                    width: `${wellSize.width}px`,
                                    height: `${wellSize.height}px`,
                                    backgroundColor: chemicals
                                        ? chroma(labwareColors[labwareType]).brighten(1).hex()
                                        : isHighlighted(wellKey)
                                        ? chroma(labwareColors[labwareType]).brighten(0.3).hex()
                                        : chroma(labwareColors[labwareType]).darken(0.5).hex(),
                                    display: 'flex',
                                    justifyContent: 'center',
                                    alignItems: 'center',
                                    borderRadius: wellShape.shape === 'circular' ? '50%' : 0,
                                    position: 'relative',
                                    margin: 'auto',
                                    fontSize: `${fontSize}px`,
                                    overflow: 'hidden',
                                    border: isHighlighted(wellKey) ? '2px solid #ff9519' : 'none',
                                    zIndex: isHighlighted(wellKey) ? 1000 : 1,
                                    transform: isHighlighted(wellKey) ? 'translate(-1.5px,-1.5px)' : 'none'
                                    // color:
                                    //     isHighlighted(wellKey)
                                    //         ? '#EEE'
                                    //         : 'inherit',
                                }}
                            >
                                {!chemicals && (
                                    <div
                                        style={{
                                            left: 0.5,
                                            top: `${Math.min(wellSize.height * 0.05, 3)}px`,
                                            position: 'absolute',
                                            width: '100%',
                                            height: '100%',
                                            borderRadius: wellShape.shape === 'circular' ? '50%' : 0,
                                            backgroundColor: isHighlighted(wellKey) ? chroma(labwareColors[labwareType]).brighten(0.6).hex() : chroma(labwareColors[labwareType]).darken(0.3).hex(),
                                            zIndex: 0,
                                        }}
                                    ></div>
                                )}
                                <div
                                    onClick={(e: React.MouseEvent) => handleWellClick(e, wellKey)}
                                    onMouseEnter={() => setHighlightedWell(wellKey)}
                                    onMouseLeave={() => setHighlightedWell(null)}
                                    style={{
                                        width: '100%',
                                        height: '100%',
                                        zIndex: 1,
                                        display: 'inherit',
                                        justifyContent: 'inherit',
                                        alignItems: 'inherit'
                                    }}
                                >
                                    {showChart() ? (
                                        <Well
                                            wellKey={wellKey}
                                            chemicals={chemicals}
                                            size={wellSize}
                                            shape={wellShape}
                                            totalVolume={labware.wells['A1'].totalLiquidVolume}
                                        />
                                    ) : (
                                        wellKey
                                    )}
                                </div>
                            </div>
                        ))}
                </div>
            </div>
            <div
                style={{
                    top: '-3%',
                    position: 'absolute',
                    height: '105%',
                    width: '100%',
                    border: !setSelectedWell && (selectedSlot === slot || isHovered) ? '2px solid #ff9519' : 'none',
                    pointerEvents: 'none',
                    borderRadius: '2% / 3.2%',
                }}
            ></div>
        </div>
    )
}
