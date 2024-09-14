import React, { useContext, useState, useEffect, useRef, useCallback } from 'react'
import {useDrag} from 'react-dnd'
import { ILabware, Well } from '../types/labware.types'
import { ChemicalEntry, IChemicals } from '../types/chemicals.types'
import { OpentronsContext } from '../context/OpentronsContext'
import { transposeWells } from '../functions/labware.functions'
import chroma from 'chroma-js'
import { labwareColors } from '../data/labware.data'

interface LabwareProps {
    slot: number
    labware: ILabware
}

export default function Labware(props: LabwareProps) {
    const { slot, labware } = props
    const [labwareType, setLabwareType] = useState('tipRack')
    const [layout, setLayout] = useState({ rows: 0, cols: 0 })
    const [wells, setWells] = useState<{ [key: string]: ChemicalEntry | null }>()
    const [wellShape, setWellShape] = useState<{ shape: string; orientation?: string; shrinkFactor?: number }>({
        shape: 'circular',
    })
    const [wellSize, setWellSize] = useState<{ width: number, height: number }>({ width: 0, height: 0 })
    const [fontSize, setFontSize] = useState(10)
    const containerRef = useRef<HTMLDivElement | null>(null)

    const setupWellShape = (blueprintWell: Well) => {
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

    const setupWells = useCallback((labwareWells?: ILabware['wells']) => {
        setWells((prevWells) => {
            if (!labwareWells) {
                return {}
            }

            const transposedWells = transposeWells(labwareWells)
            const newWells: { [key: string]: ChemicalEntry | null } = {}

            for (const wellKey in transposedWells) {
                if (prevWells && prevWells[wellKey]) {
                    newWells[wellKey] = prevWells[wellKey]
                } else {
                    newWells[wellKey] = null
                }
            }

            setupWellShape(labwareWells['A1'])

            return newWells
        })
    }, [])

    const setupLayout = useCallback((ordering: string[][]) => {
        const rows = Math.max(...ordering.map((col) => col.length))
        const cols = ordering.length
        setLayout({ rows: rows, cols: cols })
    }, [])

    // Update labware
    useEffect(() => {
        setupLayout(labware.ordering)
        setupWells(labware.wells)
        setLabwareType(labware.metadata.displayCategory)
    }, [slot, labware, setupWells, setupLayout])

    const [{ isDragging }, drag] = useDrag({
        type: slot === 0 ? 'LABWARE' : '',
        collect: (monitor) => ({
            isDragging: !!monitor.isDragging(),
        }),
    })

    const combinedRef = (element: HTMLDivElement | null) => {
        containerRef.current = element
        drag(element)
    }

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
                        return { width: maxWellSize, height: maxWellSize}
                    } else if (wellShape.orientation && wellShape.shrinkFactor) {
                        const wellWidth = wellShape.orientation === 'horizontal' ? maxWellWidth : maxWellHeight * wellShape.shrinkFactor
                        const wellHeight = wellShape.orientation === 'vertical' ? maxWellHeight : maxWellWidth * wellShape.shrinkFactor

                        return { width: wellWidth, height: wellHeight }
                    } else {
                        return prevWellSize
                    }
                })

                const newFontSize = Math.min(containerWidth / (layout.cols * 2), 16)
                setFontSize(newFontSize)
            }
        }

        updateSize()
        window.addEventListener('resize', updateSize)

        return () => window.removeEventListener('resize', updateSize)
    }, [layout, wellShape])

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
                    gridTemplateColumns: `repeat(${layout.cols}, ${wellSize.width - 1}px)`,
                    gridTemplateRows: `repeat(${layout.rows}, ${wellSize.height - 1}px)`,
                    gap: '1px',
                }}
            >
                {wells &&
                    Object.entries(wells).map(([key, well], index) => (
                        <div
                            key={key}
                            style={{
                                width: `${wellSize.width - 2}px`,
                                height: `${wellSize.height - 2}px`,
                                // aspectRatio: '1',
                                backgroundColor: well ? '#ffeb3b' : chroma(labwareColors[labwareType]).darken(0.3).hex(),
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                                borderRadius: wellShape.shape === 'circular' ? '50%' : 0,
                                position: 'relative',
                                margin: 'auto',
                                fontSize: `${fontSize}px`,
                            }}
                        >
                            {well ? well.name : key}
                        </div>
                    ))}
            </div>
        </div>
    )
}
