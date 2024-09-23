import chroma from 'chroma-js'
import { Chemical } from '../types/configuration.types'
import { Cell, Pie, PieChart } from 'recharts'
import { useCallback, useEffect, useMemo, useState } from 'react'

interface WellProps {
    wellKey: string
    chemicals: Chemical[] | null
    size: { width: number; height: number }
    shape: { shape: string; orientation?: string; shrinkFactor?: number }
    totalVolume: number
}

export default function Well(props: WellProps) {
    const { wellKey, chemicals, size, shape, totalVolume } = props

    const getRandomColors = useMemo(
        () => (numColors: number) => {
            return Array.from({ length: numColors }, () => chroma.random().hex())
        },
        []
    )

    const colors = useMemo(() => {
        if (!chemicals) return null
        return ['#888', ...getRandomColors(chemicals.length)]
    }, [chemicals, getRandomColors])

    const getChart = () => {
        if (!chemicals || !colors) return

        let chemicalsVolume = 0
        chemicals.forEach((chemical) => (chemicalsVolume += chemical.volume.value))

        if (chemicalsVolume > totalVolume) return

        if (shape.shape === 'circular') {
            let adjustedEmptyVolume = totalVolume - chemicalsVolume
            while (adjustedEmptyVolume / 10 > chemicalsVolume) {
                adjustedEmptyVolume /= 10
            }

            const emptyPie: { name: string; value: number }[] = [
                {
                    name: 'empty',
                    value: adjustedEmptyVolume,
                },
            ]

            const pieData = [
                ...emptyPie,
                ...chemicals.map((chemical) => ({
                    name: chemical.name,
                    value: chemical.volume.value,
                })),
            ]

            return (
                <PieChart width={size.width} height={size.height}>
                    <Pie
                        data={pieData}
                        dataKey='value'
                        outerRadius={size.width / 2}
                        innerRadius={size.width / 4}
                        fill='#8884d8'
                        paddingAngle={3}
                        stroke='none'
                    >
                        {pieData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={colors[index]} />
                        ))}
                    </Pie>
                </PieChart>
            )
        } else {
            let adjustedTotalVolume = totalVolume
            while (adjustedTotalVolume / 10 > chemicalsVolume) {
                adjustedTotalVolume /= 10
            }
            const chemicalsToMap =
                shape.orientation === 'horizontal' ? [...chemicals] : [...chemicals.slice(0).reverse()]

            return chemicalsToMap.map((chemical, index) => {
                const percentage = chemical.volume.value / adjustedTotalVolume

                return (
                    <div
                        key={`chemical-${index}`}
                        style={{
                            position: 'relative',
                            bottom: 0,
                            left: 0,
                            width: shape.orientation === 'vertical' ? size.width : `${percentage * size.width}px`,
                            height: shape.orientation === 'horizontal' ? size.height : `${percentage * size.height}px`,
                            backgroundColor: colors[index + 1],
                        }}
                    ></div>
                )
            })
        }
    }

    return (
        <div
            style={{
                position: 'relative',
                width: size.width,
                height: size.height,
                display: 'flex',
                justifyContent: shape.orientation === 'vertical' ? 'flex-end' : 'flex-start',
                alignItems: 'center',
                flexDirection: shape.orientation === 'vertical' ? 'column' : 'row',
            }}
        >
            {chemicals && getChart()}
            <div
                style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                {wellKey}
            </div>
        </div>
    )
}
