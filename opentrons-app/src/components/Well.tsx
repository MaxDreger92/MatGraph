import { Chemical } from '../types/configuration.types'
import { Cell, Pie, PieChart } from 'recharts'
import { chemicalColors, labelColors } from '../data/chemicals.data'
import { useRef, useState } from 'react'

interface WellProps {
    wellKey: string
    chemicals: Chemical[] | null
    size: { width: number; height: number }
    shape: { shape: string; orientation?: string; shrinkFactor?: number }
    totalVolume: number
    inDetail: boolean
}

interface LabelProps {
    cx: number
    cy: number
    midAngle: number
    innerRadius: number
    outerRadius: number
    percent: number
    index: number
}

const RADIAN = Math.PI / 180

export default function Well(props: WellProps) {
    const { wellKey, chemicals, size, shape, totalVolume, inDetail } = props
    const emptyVolume = useRef<number>(0)

    // const getRandomColors = useMemo(
    //     () => (numColors: number) => {
    //         return Array.from({ length: numColors }, () => chroma.random().hex())
    //     },
    //     []
    // )

    // const colors = useMemo(() => {
    //     if (!chemicals) return null
    //     return ['#888', ...getRandomColors(chemicals.length)]
    // }, [chemicals, getRandomColors])

    const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }: LabelProps) => {
        if (!inDetail || !chemicals) return <></>
        const labelColor = labelColors[index]
        const radius = innerRadius + (outerRadius - innerRadius) * 0.5
        const x = cx + radius * Math.cos(-midAngle * RADIAN)
        const y = cy + radius * Math.sin(-midAngle * RADIAN)

        let correctPercent = 0
        if (index === 0) {
            correctPercent = emptyVolume.current / totalVolume
        } else {
            correctPercent = chemicals[index-1].volume.value / totalVolume
        }
        const percentString = (correctPercent * 100).toFixed(2).replace(/^0\./, '.') + '%'

        return (
            <text x={x} y={y} fill={labelColor} textAnchor='middle' dominantBaseline='central' style={{backgroundColor: '#ff0000', width: 100, height: 100,}}>
                {percentString}
            </text>
        )
    }

    const getChart = () => {
        if (!chemicals) return

        let chemicalsVolume = 0
        chemicals.forEach((chemical) => (chemicalsVolume += chemical.volume.value))

        if (chemicalsVolume > totalVolume) return

        const colors: string[] = ['#888']
        chemicals.forEach((chemical) => colors.push(chemicalColors[chemical.name]))

        if (shape.shape === 'circular') {
            let adjustedEmptyVolume = totalVolume - chemicalsVolume
            emptyVolume.current = adjustedEmptyVolume
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
                        cx="50%"
                        cy="50%"
                        dataKey='value'
                        outerRadius={size.width / 2}
                        innerRadius={size.width / 4}
                        fill='#8884d8'
                        paddingAngle={3}
                        stroke='none'
                        label={size.width > 150 && size.height > 150 ? renderLabel : undefined}
                        labelLine={false}
                    >
                        {pieData.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={colors[index]}
                                filter='drop-shadow(0px 0px 3px #33333340)'
                            />
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
