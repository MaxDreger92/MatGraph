import React, { useRef, useMemo, useEffect, useState, useCallback } from 'react'
import ReactDOM from 'react-dom'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useReactTable, ColumnDef, getCoreRowModel } from '@tanstack/react-table'
import { TableRow } from '../../types/workspace.types'
import { Label } from '../../types/workspace.types'
import { Select } from '@mantine/core'
import { getAttributesByLabel, mapNodeTypeString } from '../../common/workspaceHelpers'
import { TNode } from '../../types/canvas.types'
import { colorPalette } from '../../types/colors'

interface WorkspacePartialTableProps {
    tableRows: TableRow[]
    // progress: number
    outerTableHeight: number | null
    darkTheme: boolean
    columnsLength: number

    // ################################ for additional table
    // columns of additional table
    filteredColumns: number[]
    // numericalNodeType of additional table
    numericalNodeType: number
}

export default function WorkspacePartialTable(props: WorkspacePartialTableProps) {
    const {
        tableRows,
        // progress,
        outerTableHeight,
        darkTheme,
        columnsLength,
        filteredColumns,
        numericalNodeType,
    } = props

    const tableRef = useRef<HTMLDivElement>(null)

    const [innerTableHeight, setInnerTableHeight] = useState<number | string>('')

    useEffect(() => {
        // 52 + 45 * tableRows
        if (outerTableHeight) {
            const rowHeight = 52 + 45 * tableRows.length
            const divHeight = outerTableHeight - 90
            setInnerTableHeight(Math.min(rowHeight, divHeight))
            return
        }
        setInnerTableHeight(`calc(100% - 90px)`)
    }, [tableRows, outerTableHeight])

    // Define columns
    const columns: ColumnDef<TableRow>[] = useMemo(() => {
        if (tableRows.length === 0) {
            return []
        }
        return Object.keys(tableRows[0]).map((key) => ({
            // Directly use a string or JSX for headers that don't need context
            header: String(key),
            accessorFn: (row) => row[key],
            id: key,
        }))
    }, [tableRows])

    const tableInstance = useReactTable({
        data: tableRows,
        columns,
        state: {
            // Your state here if needed
        },
        onStateChange: () => {
            // Handle state changes if needed
        },
        getCoreRowModel: getCoreRowModel(), // Adjusted usage
    })

    // Setup virtualizers for both rows and columns
    const rowVirtualizer = useVirtualizer({
        count: tableRows.length,
        getScrollElement: () => tableRef.current,
        estimateSize: () => 45, // Adjust based on your row height
        overscan: 10,
    })

    const columnVirtualizer = useVirtualizer({
        horizontal: true,
        count: columns.length,
        getScrollElement: () => tableRef.current,
        estimateSize: (index) => {
            const key = columns[index].id
            if (key) {
                return Math.max(key.length * 10, 160)
            }
            return 160
        },
        overscan: 1,
    })

    const capitalizeFirstLetter = (item: string | number | boolean) => {
        if (!(typeof item === 'string')) return item
        return item.charAt(0).toUpperCase() + item.slice(1)
    }

    const getAdditionalColumnNum = (index: number): number | string => {
        if (!(filteredColumns && filteredColumns.length > 0)) return 'isNaN'

        return filteredColumns[index]
    }

    const getRowColor = (): string => {
        return darkTheme ? '#212226' : 'f8f9fa'
    }

    const getHeaderBackgroundColor = (): string => {
        const colorIndex = darkTheme ? 0 : 1
        const colors = colorPalette[colorIndex]
        return colors[mapNodeTypeString(numericalNodeType)]
    }

    const getHeaderTextColor = (): string => {
        let numNodeType = numericalNodeType

        if ([0, 2, 5].includes(numNodeType)) {
            return '#1a1b1e'
        }
        return '#ececec'
    }

    const getBorderColor = (): string => {
        return darkTheme ? '#333' : '#ced4da'
    }

    // Render your table
    return (
        <div
            key={tableRows.length}
            ref={tableRef}
            className="workspace-table"
            tabIndex={0}
            style={{
                position: 'relative',
                top: 0,
                display: 'flex',
                flexDirection: 'column',
                height: innerTableHeight,
                width: `calc(100% + 15px)`,
                overflow: 'auto',
                backgroundColor: darkTheme ? '#212226' : '#fff',
            }}
        >
            {/* Header */}
            <div
                style={{
                    position: 'sticky',
                    width: `${columnVirtualizer.getTotalSize()}px`,
                    top: 0,
                    zIndex: 2,
                }}
            >
                {columnVirtualizer.getVirtualItems().map((columnVirtual) => {
                    // Access the header as a direct value
                    const header = String(columns[columnVirtual.index].header)
                    return (
                        <div
                            key={columnVirtual.key}
                            style={{
                                display: 'inline-block',
                                position: 'absolute',
                                left: `${columnVirtual.start}px`,
                                width: `${columnVirtual.size}px`,
                                height: '50px',
                                borderBottom: `1px solid ${getBorderColor()}`,
                                textAlign: 'left',
                                lineHeight: '50px',
                                backgroundColor: getHeaderBackgroundColor(), // add hover to signalize interaction possibility
                                color: getHeaderTextColor(),
                                borderRight: `1px solid ${getBorderColor()}`,
                            }}
                        >
                            <div
                                style={{
                                    position: 'absolute',
                                    top: -12,
                                    left: 4,
                                    display: 'flex',
                                    width: 'calc(100% - 12px)',
                                    fontWeight: 'bold',
                                }}
                            >
                                {getAdditionalColumnNum(columnVirtual.index)}
                            </div>

                            <div
                                style={{
                                    position: 'absolute',
                                    top: 11,
                                    left: 11,
                                }}
                            >
                                {header}
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Rows */}
            <div
                style={{
                    position: 'relative',
                    height: `${rowVirtualizer.getTotalSize()}px`,
                    width: `${columnVirtualizer.getTotalSize()}px`,
                    top: 50,
                    zIndex: 1,
                }}
            >
                {rowVirtualizer.getVirtualItems().map((rowVirtual) => (
                    <>
                        <div
                            key={rowVirtual.key}
                            style={{
                                position: 'absolute',
                                top: `${rowVirtual.start}px`,
                                height: `${rowVirtual.size}px`,
                                width: '100%',
                            }}
                        >
                            {columnVirtualizer.getVirtualItems().map((columnVirtual) => {
                                const column = columns[columnVirtual.index]
                                const columnId = column.id // Assuming columnId is always defined based on your column setup
                                if (typeof columnId !== 'undefined') {
                                    const cellData = tableRows[rowVirtual.index][columnId] // Safely access cell data using columnId
                                    return (
                                        <div
                                            key={columnVirtual.key}
                                            style={{
                                                display: 'inline-block',
                                                position: 'absolute',
                                                left: `${columnVirtual.start}px`,
                                                width: `${columnVirtual.size}px`,
                                                height: '100%',
                                                backgroundColor: getRowColor(),
                                                color: darkTheme ? '#a6a7ab' : '#040404',
                                                borderRight:
                                                    columnVirtual.index + 1 === columnsLength
                                                        ? 'none'
                                                        : '1px solid #333',

                                                borderBottom:
                                                    rowVirtual.index + 1 === tableRows.length
                                                        ? 'none'
                                                        : `1px solid ${getBorderColor()}`,

                                                paddingTop: 10,
                                                paddingLeft: '.5rem',
                                            }}
                                        >
                                            <div
                                                style={{
                                                    position: 'relative',
                                                }}
                                            >
                                                {capitalizeFirstLetter(cellData)}
                                            </div>
                                        </div>
                                    )
                                }
                                return null // Or handle the undefined case appropriately
                            })}
                        </div>
                    </>
                ))}
            </div>
        </div>
    )
}
