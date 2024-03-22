import React, { useRef, useMemo, useEffect, useState, useCallback } from 'react'
import ReactDOM from 'react-dom'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useReactTable, ColumnDef, getCoreRowModel } from '@tanstack/react-table'
import { TableRow } from '../../types/workflow.types'
import { Label } from '../../types/workflow.types'
import { Select } from '@mantine/core'
import { getAttributesByLabel, mapNodeTypeString } from '../../common/helpers'
import { INode } from '../../types/canvas.types'
import { colorPalette } from '../../types/colors'

interface WorkflowTableProps {
    setLabelTable: React.Dispatch<React.SetStateAction<TableRow[]>>
    setAttributeTable: React.Dispatch<React.SetStateAction<TableRow[]>>
    setTableRows: React.Dispatch<React.SetStateAction<TableRow[]>>
    tableRows: TableRow[]
    progress: number
    outerTableHeight: number | null
    darkTheme: boolean
    columnsLength: number

    // ################################ for additional table
    // columns of additional table
    filteredColumns?: number[]
    // numericalNodeType of additional table
    numericalNodeType?: number

    // ################################ for csvTable
    // all additional tables
    additionalTables?: number[][]

    // ################################ for node selection
    selectedTableColumn?: number | null
    setSelectedTableColumn?: React.Dispatch<React.SetStateAction<number | null>>
}

const labelOptions = [
    { value: 'matter', label: 'Matter' },
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'measurement', label: 'Measurement' },
    { value: 'parameter', label: 'Parameter' },
    { value: 'property', label: 'Property' },
    { value: 'metadata', label: 'Metadata' },
]

export default function WorkflowTable(props: WorkflowTableProps) {
    const {
        setLabelTable,
        setAttributeTable,
        setTableRows,
        tableRows,
        progress,
        outerTableHeight,
        darkTheme,
        columnsLength,
        filteredColumns,
        numericalNodeType,
        additionalTables,
        selectedTableColumn,
        setSelectedTableColumn,
    } = props

    const partialTable = numericalNodeType !== undefined
    const tableRef = useRef<HTMLDivElement>(null)

    const [selected, setSelected] = useState<{
        row: number
        column: string
    } | null>(null)
    const [hovered, setHovered] = useState<{
        row: number
        column: number
    } | null>(null)

    const [innerTableHeight, setInnerTableHeight] = useState<number | string>('')
    const [selectData, setSelectData] = useState<{ value: string; label: string }[]>([])
    const [highlightedColumns, setHighlightedColumns] = useState<{
        [key: number]: number
    }>({})

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

    useEffect(() => {
        if (!additionalTables) return

        const columns: { [key: number]: number } = {}

        additionalTables.map((table) => {
            return table.slice(1).map((column) => (columns[column] = table[0]))
        })

        setHighlightedColumns(columns)
    }, [additionalTables])

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

    const handleCellClick = (
        cellData: string | number | boolean,
        row: number,
        columnId: string
    ): void => {
        if (progress === 2 && row === 0) {
            if (
                typeof cellData === 'string' &&
                labelOptions.some((option) => option.value === (cellData.toLowerCase() as Label))
            ) {
                setSelectData(labelOptions)
                setSelected({ row: row, column: columnId })
            }
        } else if (progress === 3 && row === 1) {
            const labelKey = tableRows[0][columnId]
            if (
                typeof labelKey === 'string' &&
                labelOptions.some((option) => option.value === (labelKey.toLowerCase() as Label))
            ) {
                const attributes = getAttributesByLabel(labelKey.toLowerCase() as Label)
                if (
                    attributes &&
                    typeof cellData === 'string' &&
                    attributes.includes(cellData.toLowerCase())
                ) {
                    const newAttributeOptions = attributes.map((attr) => ({
                        value: attr,
                        label: capitalizeFirstLetter(attr).toString(),
                    }))
                    setSelectData(newAttributeOptions)
                    setSelected({ row: row, column: columnId })
                }
            }
        }
    }

    const handleHeaderClick = (columnIndex: number) => {
        if (setSelectedTableColumn) {
            setSelectedTableColumn(columnIndex)
        }
    }

    const handleSelectChange = (value: string | null, rowIndex: number, columnId: string) => {
        if (!value) return
        const updatedTableRows = tableRows.map((row, index) => {
            if (index === rowIndex) {
                return { ...row, [columnId]: value }
            }
            return { ...row }
        })
        setTableRows(updatedTableRows)
        if (rowIndex === 0) {
            setLabelTable(updatedTableRows)
        } else {
            setAttributeTable(updatedTableRows)
        }
    }

    const resetSelections = () => {
        setSelected(null)
        setSelectData([])
        if (setSelectedTableColumn) {
            setSelectedTableColumn(null)
        }
    }

    const capitalizeFirstLetter = (item: string | number | boolean) => {
        if (!(typeof item === 'string')) return item
        return item.charAt(0).toUpperCase() + item.slice(1)
    }

    const getAdditionalColumnNum = (index: number): number | string => {
        if (!(filteredColumns && filteredColumns.length > 0)) return 'isNaN'

        return filteredColumns[index]
    }

    const getRowColor = (rowIndex: number, columnIndex: number): string => {
        if (progress > 1 && progress < 4) {
            if (
                rowIndex === tableRows.length - 1 &&
                hovered &&
                hovered.row === rowIndex &&
                hovered.column === columnIndex &&
                !selected
            ) {
                return 'rgba(24,100,171,0.2)'
            } else {
                return darkTheme ? '#212226' : '#f8f9fa'
            }
        } else if (progress > 3 && !partialTable) {
            if (columnIndex === hovered?.column || columnIndex === selectedTableColumn) {
                return darkTheme ? '#25262b' : '#ff0000'
            }
        }
        return darkTheme ? '#212226' : 'f8f9fa'
    }

    const getHeaderBackgroundColor = (columnIndex: number): string => {
        if (!partialTable && !(columnIndex in highlightedColumns)) {
            return darkTheme ? '#25262b' : '#f1f3f5'
        }

        const colorIndex = darkTheme ? 0 : 1
        const colors = colorPalette[colorIndex]
        let nodeType = ''

        if (partialTable) {
            nodeType = mapNodeTypeString(numericalNodeType)
        } else {
            nodeType = mapNodeTypeString(highlightedColumns[columnIndex])
        }

        return colors[nodeType]
    }

    const getHeaderTextColor = (columnIndex: number): string => {
        if (!partialTable && !(columnIndex in highlightedColumns)) {
            return darkTheme ? '#a6a7ab' : '#040404'
        }

        let numNodeType = 69

        if (partialTable) {
            numNodeType = numericalNodeType
        } else {
            numNodeType = highlightedColumns[columnIndex]
        }

        if ([0, 2, 5].includes(numNodeType)) {
            return '#1a1b1e'
        }
        return '#ececec'
    }

    const getBorderColor = (): string => {
        // if (!partialTable) {
        // 	const defaultBorderColor = darkTheme ? "#333" : "#ced4da"
        // 	return defaultBorderColor
        // }
        // const colorIndex = darkTheme ? 0 : 1
        // const colors = colorPalette[colorIndex]
        // const stringNodeType = mapNodeTypeString(numericalNodeType)
        // const specialBorderColor = colors[stringNodeType]
        // return specialBorderColor

        return darkTheme ? '#333' : '#ced4da'
    }

    // Render your table
    return (
        <div
            key={tableRows.length}
            ref={tableRef}
            className="workflow-table"
            tabIndex={0}
            onBlur={resetSelections}
            style={{
                position: 'relative',
                top: partialTable ? 0 : 0,
                display: 'flex',
                flexDirection: 'column',
                height: innerTableHeight,
                width: `calc(100% + 15px)`,
                overflow: 'auto',
                // border: partialTable ? `1px solid ${tableColors["borderColor"]}` : "none",
                backgroundColor: darkTheme ? '#212226' : '#fff',
                // zIndex: 0,
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
                            onMouseEnter={() =>
                                setHovered({
                                    row: -1,
                                    column: columnVirtual.index,
                                })
                            }
                            onMouseLeave={() => setHovered(null)}
                            onClick={
                                progress > 3
                                    ? () => handleHeaderClick(columnVirtual.index)
                                    : undefined
                            }
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
                                backgroundColor: getHeaderBackgroundColor(columnVirtual.index), // add hover to signalize interaction possibility
                                color: getHeaderTextColor(columnVirtual.index),
                                borderRight: `1px solid ${getBorderColor()}`,
                                cursor: progress > 3 ? 'pointer' : 'default',
                                // paddingLeft: '.5rem',
                            }}
                        >
                            {!partialTable &&
                                (columnVirtual.index === hovered?.column ||
                                    columnVirtual.index === selectedTableColumn) &&
                                progress > 3 && (
                                    <div
                                        style={{
                                            position: 'absolute',
                                            width: '100%',
                                            height: '100%',
                                            backgroundColor: darkTheme ? '#373A40' : '#ff0000',
                                        }}
                                    />
                                )}
                            {partialTable && (
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
                            )}

                            {!partialTable && (
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
                                    {columnVirtual.index}
                                </div>
                            )}

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
                                cursor:
                                    progress > 1 && rowVirtual.index === tableRows.length - 1
                                        ? 'pointer'
                                        : 'default',
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
                                            onMouseEnter={() =>
                                                setHovered({
                                                    row: rowVirtual.index,
                                                    column: columnVirtual.index,
                                                })
                                            }
                                            onMouseLeave={() => setHovered(null)}
                                            style={{
                                                display: 'inline-block',
                                                position: 'absolute',
                                                left: `${columnVirtual.start}px`,
                                                width: `${columnVirtual.size}px`,
                                                height: '100%',
                                                backgroundColor: getRowColor(
                                                    rowVirtual.index,
                                                    columnVirtual.index
                                                ),
                                                color: darkTheme ? '#a6a7ab' : '#040404',
                                                borderRight:
                                                    columnVirtual.index + 1 === columnsLength
                                                        ? 'none'
                                                        : '1px solid #333',
                                                // borderRight: `1px solid ${tableColors["borderColor"]}`,
                                                borderBottom:
                                                    rowVirtual.index + 1 === tableRows.length
                                                        ? 'none'
                                                        : `1px solid ${getBorderColor()}`,
                                                // borderBottom: "1px solid #333",
                                                paddingTop: 10,
                                                paddingLeft: '.5rem',
                                            }}
                                        >
                                            <div
                                                onClick={
                                                    progress > 1
                                                        ? () =>
                                                              handleCellClick(
                                                                  cellData,
                                                                  rowVirtual.index,
                                                                  columnId
                                                              )
                                                        : undefined
                                                }
                                                style={{
                                                    position: 'relative',
                                                }}
                                            >
                                                {selected?.row === rowVirtual.index &&
                                                selected?.column === columnId ? (
                                                    <Select
                                                        defaultValue={cellData.toString()}
                                                        data={selectData}
                                                        withinPortal={true}
                                                        initiallyOpened={true}
                                                        onChange={(value) =>
                                                            handleSelectChange(
                                                                value,
                                                                rowVirtual.index,
                                                                columnId
                                                            )
                                                        }
                                                        onDropdownClose={() => setSelected(null)}
                                                        onBlur={() => setSelected(null)}
                                                        autoFocus={true}
                                                        maxDropdownHeight={800}
                                                        styles={{
                                                            input: {
                                                                borderWidth: 0,
                                                                '&:focus': {
                                                                    outline: 'none',
                                                                    boxShadow: 'none',
                                                                },
                                                                backgroundColor: 'transparent',
                                                                fontFamily: 'inherit',
                                                                fontSize: 'inherit',
                                                                transform: 'translate(-4px,0)',
                                                            },
                                                        }}
                                                        style={{
                                                            transform:
                                                                'translate(calc(-0.5rem), -6px)',
                                                            width: 'calc(100% + 8px)',
                                                            height: 200,
                                                        }}
                                                    />
                                                ) : (
                                                    capitalizeFirstLetter(cellData)
                                                )}
                                            </div>
                                        </div>
                                    )
                                }
                                return null // Or handle the undefined case appropriately
                            })}
                        </div>
                        {progress > 1 && rowVirtual.index === tableRows.length - 1 && (
                            <div
                                style={{
                                    position: 'absolute',
                                    width: '100%',
                                    top: `${rowVirtual.start}px`,
                                    height: `${rowVirtual.size}px`,
                                    outline:
                                        progress > 1 && rowVirtual.index === tableRows.length - 1
                                            ? '1px dashed #1971c2'
                                            : 'none',
                                    outlineOffset: -1,
                                    pointerEvents: 'none',
                                }}
                            />
                        )}
                    </>
                ))}
            </div>

            {/* Shadow */}
            {/* <div
				style={{
					position: "fixed",
					width: `calc(100% - 22px)`,
					height: tableRect ? `${tableRect.height}px` : "100%",
					boxShadow: "inset 0px 0px 4px rgba(0, 0, 0, 0.3)",
					zIndex: 3,
					pointerEvents: "none",
					// backgroundColor: "rgba(240,100,0,0.5)",
				}}
			/> */}
        </div>
    )
}
