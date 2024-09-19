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
}

export default function Labware(props: LabwareProps) {
    const { slot, labware } = props
    const [labwareType, setLabwareType] = useState('tipRack')
    const [layout, setLayout] = useState({ rows: 0, cols: 0 })
    const [wells, setWells] = useState<{ [key: string]: Chemical[] | null }>()
    const [wellShape, setWellShape] = useState<{ shape: string; orientation?: string; shrinkFactor?: number }>({
        shape: 'circular',
    })
    const [wellSize, setWellSize] = useState<{ width: number; height: number }>({ width: 0, height: 0 })
    const [fontSize, setFontSize] = useState(10)
    const containerRef = useRef<HTMLDivElement | null>(null)

    const { currentConfig } = useContext(OpentronsContext)

    const [{ isDragging }, drag] = useDrag({
        type: slot === 0 ? 'LABWARE' : '',
        item: labware,
        collect: (monitor) => ({
            isDragging: !!monitor.isDragging(),
        }),
    })

    const combinedRef = (element: HTMLDivElement | null) => {
        containerRef.current = element
        drag(element)
    }

    // calc sizes
    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                const containerWidth = containerRef.current.offsetWidth
                const containerHeight = containerRef.current.offsetHeight

                setWellSize((prevWellSize) => {
                    const maxWellWidth = containerWidth / layout.cols
                    const maxWellHeight = containerHeight / layout.rows
                    if (wellShape.shape === 'circular') {
                        const maxWellSize = Math.min(maxWellWidth, maxWellHeight)
                        return { width: maxWellSize - 2, height: maxWellSize -2 }
                    } else if (wellShape.orientation && wellShape.shrinkFactor) {
                        let wellWidth =
                            wellShape.orientation === 'horizontal'
                                ? maxWellWidth
                                : maxWellHeight * wellShape.shrinkFactor
                        let wellHeight =
                            wellShape.orientation === 'vertical' ? maxWellHeight : maxWellWidth * wellShape.shrinkFactor
                        if (wellWidth > maxWellWidth) {
                            wellWidth *= maxWellWidth / wellWidth
                        }
                        if (wellHeight > maxWellHeight) {
                            wellHeight *= (maxWellHeight / wellHeight)
                        }
                        return { width: wellWidth - 2, height: wellHeight - 2 }
                    } else {
                        return prevWellSize
                    }
                })

                const newFontSize = Math.min(containerWidth / (layout.cols * 2.8), 13)
                setFontSize(newFontSize)
            }
        }

        updateSize()
        window.addEventListener('resize', updateSize)

        return () => window.removeEventListener('resize', updateSize)
    }, [layout, wellShape])

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

            const chemicalsInSlot = currentConfig.chemicalSetup.opentrons.filter(
                (chemical) => chemical.location.slot === slot
            )

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

    const getWellLabel = (chemicals: Chemical[] | null, key: string): string => {
        if (!chemicals) {
            return key
        }

        let label = chemicals[0].name
        return chemicals.length > 1 ? label.concat('...') : label
    }

    const showChart = (): boolean => {
        return wellSize.width + wellSize.height > 96
    }

    return (
        <div
            ref={combinedRef}
            className='labware'
            style={{
                display: 'flex',
                backgroundColor: labwareColors[labwareType],
            }}
        >
            <div
                className='grid-container'
                style={{
                    display: 'grid',
                    gridTemplateColumns: `repeat(${layout.cols}, ${wellSize.width + 1}px)`,
                    gridTemplateRows: `repeat(${layout.rows}, ${wellSize.height + 1}px)`,
                    gap: '1px',
                }}
            >
                {wells &&
                    Object.entries(wells).map(([wellKey, chemicals], index) => (
                        <div
                        className='isItThis'
                            key={wellKey}
                            style={{
                                width: `${wellSize.width}px`,
                                height: `${wellSize.height}px`,
                                backgroundColor:
                                    chemicals ? chroma(labwareColors[labwareType]).brighten(1).hex()
                                        : chroma(labwareColors[labwareType]).darken(0.3).hex(),
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                                borderRadius: wellShape.shape === 'circular' ? '50%' : 0,
                                position: 'relative',
                                margin: 'auto',
                                fontSize: `${fontSize}px`,
                                color: '#333',
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
                    ))}
            </div>
        </div>
    )
}
