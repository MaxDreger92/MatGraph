import React, { useMemo, useEffect, useState, useCallback, useContext } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import { useReactTable, ColumnDef, getCoreRowModel } from '@tanstack/react-table'
import { TableRow } from '../../types/workflow.types'
import { Label } from '../../types/workflow.types'
import { Select } from '@mantine/core'
import { getAttributesByLabel, mapNodeTypeString } from '../../common/workflowHelpers'
import { INode } from '../../types/canvas.types'
import { colorPalette } from '../../types/colors'
import WorkflowContext from './context/WorkflowContext'

interface WorkflowTableProps {
    setLabelTable: React.Dispatch<React.SetStateAction<TableRow[]>>
    setAttributeTable: React.Dispatch<React.SetStateAction<TableRow[]>>
    setCurrentTableFn: (tableId: string, tableRows: TableRow[]) => void
    tableRows: TableRow[]
    progress: number
    currentTableId: string
    outerTableHeight: number | null
    darkTheme: boolean
    columnsLength: number

    // ################################ for csvTable
    // all additional tables
    additionalTables?: number[][]
}

const labelOptions = [
    { value: 'matter', label: 'Matter' },
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'measurement', label: 'Measurement' },
    { value: 'parameter', label: 'Parameter' },
    { value: 'property', label: 'Property' },
    { value: 'metadata', label: 'Metadata' },
    { value: 'simulation', label: 'Simulation' },
]

export default function WorkflowTable(props: WorkflowTableProps) {
    const {
        setLabelTable,
        setAttributeTable,
        setCurrentTableFn,
        tableRows,
        progress,
        currentTableId,
        outerTableHeight,
        darkTheme,
        columnsLength,
        additionalTables,
    } = props

    const tableRef = React.createRef<HTMLDivElement>()

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

    const [tableActive, setTableActive] = useState<number | null>(null)
    const [dragging, setDragging] = useState(false)

    const { setHighlightedColumnIndex, selectedColumnIndex, setSelectedColumnIndex } =
        useContext(WorkflowContext)

    useEffect(() => {
        if (progress === 2) {
            setTableActive(currentTableId === 'labelTable' ? 1 : -1)
        } else if (progress === 3) {
            setTableActive(currentTableId === 'attributeTable' ? 2 : -1)
        } else if (progress > 3) {
            setTableActive(currentTableId === 'csvTable' ? 0 : -1)
        } else {
            setTableActive(-1)
        }
    }, [progress, currentTableId])

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

    useEffect(() => {
        if (!(tableActive === 0)) return

        if (!hovered) {
            setHighlightedColumnIndex(null)
            return
        }

        setHighlightedColumnIndex(hovered.column)
    }, [hovered, progress, setHighlightedColumnIndex, currentTableId, tableActive])

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
        overscan: 1,
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
        if (tableActive === 1 && row === 0) {
            if (
                typeof cellData === 'string' &&
                labelOptions.some((option) => option.value === (cellData.toLowerCase() as Label))
            ) {
                setSelectData(labelOptions)
                setSelected({ row: row, column: columnId })
            }
        } else if (tableActive === 2 && row === 1) {
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
        setSelectedColumnIndex(columnIndex)
    }

    const handleSelectChange = (value: string | null, rowIndex: number, columnId: string) => {
        if (!value) return
        const updatedTableRows = tableRows.map((row, index) => {
            if (index === rowIndex) {
                return { ...row, [columnId]: value }
            }
            return { ...row }
        })
        let tableId = ''
        if (rowIndex === 0) {
            setLabelTable(updatedTableRows)
            tableId = 'labelTable'
        } else {
            setAttributeTable(updatedTableRows)
            tableId = 'attributeTable'
        }
        setCurrentTableFn(tableId, updatedTableRows)
    }

    const handleDragStart = (
        e: React.DragEvent<HTMLDivElement>,
        columnContent: string,
        columnIndex: number
    ): void => {
        setDragging(true)

        const dragData = { columnContent, columnIndex }

        const dragDataString = JSON.stringify(dragData)

        e.dataTransfer.setData('text/plain', dragDataString)
    }

    const handleBlur = () => {
        resetSelections()
    }

    const resetSelections = () => {
        setSelectedColumnIndex(null)
    }

    const capitalizeFirstLetter = (item: string | number | boolean) => {
        if (!(typeof item === 'string')) return item
        return item.charAt(0).toUpperCase() + item.slice(1)
    }

    const getRowColor = (rowIndex: number, columnIndex: number): string => {
        if (tableActive === 1 || tableActive === 2) {
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
        } else if (
            (columnIndex === hovered?.column || columnIndex === selectedColumnIndex) &&
            tableActive === 0
        ) {
            return darkTheme ? '#25262b' : '#e9ecef'
        } else {
            return darkTheme ? '#212226' : '#f8f9fa'
        }
    }

    const getHeaderBackgroundColor = (columnIndex: number): string => {
        if (columnIndex in highlightedColumns && currentTableId === 'csvTable') {
            const colorIndex = darkTheme ? 0 : 1
            const colors = colorPalette[colorIndex]
            let nodeType = mapNodeTypeString(highlightedColumns[columnIndex])

            return colors[nodeType]
        } else if (
            (columnIndex === hovered?.column || columnIndex === selectedColumnIndex) &&
            tableActive === 0
        ) {
            return darkTheme ? '#373A40' : '#dee2e6'
        } else {
            return darkTheme ? '#25262b' : '#f1f3f5'
        }
    }

    const getHeaderTextColor = (columnIndex: number): string => {
        if (!(columnIndex in highlightedColumns) || currentTableId !== 'csvTable') {
            return darkTheme ? '#a6a7ab' : '#040404'
        }

        let numNodeType = highlightedColumns[columnIndex]

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
            ref={tableRef}
            className="workflow-table"
            tabIndex={0}
            onBlur={() => handleBlur()}
            style={{
                position: 'relative',
                top: 0,
                display: 'flex',
                flexDirection: 'column',
                height: innerTableHeight,
                width: `calc(100% + 15px)`,
                overflowX: 'auto',
                overflowY:
                    tableActive === 1 || tableActive === 2
                        ? 'hidden'
                        : 'auto',
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
                            onMouseLeave={() => {
                                setHovered(null)
                            }}
                            onMouseUp={
                                tableActive === 0
                                    ? () => handleHeaderClick(columnVirtual.index)
                                    : undefined
                            }
                            draggable={tableActive === 0}
                            onDragStart={(e) => handleDragStart(e, header, columnVirtual.index)}
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
                                cursor:
                                    tableActive === 0
                                        ? 'grab'
                                        : 'text',
                                // paddingLeft: '.5rem',
                            }}
                        >
                            <div
                                className='unselectable'
                                style={{
                                    position: 'absolute',
                                    top: -12,
                                    display: 'flex',
                                    fontWeight: 'bold',
                                    pointerEvents: 'none',
                                    paddingLeft: 4,
                                }}
                            >
                                {columnVirtual.index}
                            </div>
                            <div
                                style={{
                                    position: 'absolute',
                                    width: "100%",
                                    height: '100%',
                                    padding: '11px 0 0 11px'
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
                    <div key={rowVirtual.key}>
                        <div
                            style={{
                                position: 'absolute',
                                top: `${rowVirtual.start}px`,
                                height: `${rowVirtual.size}px`,
                                width: '100%',
                                cursor:
                                    ((tableActive === 1 || tableActive === 2) &&
                                    rowVirtual.index === tableRows.length - 1)
                                        ? 'pointer'
                                        : tableActive === 0
                                            ? 'grab' 
                                            : 'text',
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
                                            draggable={
                                                tableActive === 0
                                            }
                                            onDragStart={(e) =>
                                                handleDragStart(
                                                    e,
                                                    cellData.toString(),
                                                    columnVirtual.index
                                                )
                                            }
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
                                                        : `1px solid ${getBorderColor()}`,
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
                                                    height: '100%',
                                                    width: '100%',
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
                                                            position: 'absolute',
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
                                return <div key={columnVirtual.key} /> // Or handle the undefined case appropriately
                            })}
                        </div>
                        {(tableActive === 1 || tableActive === 2) &&
                            rowVirtual.index === tableRows.length - 1 && (
                                <div
                                    style={{
                                        position: 'absolute',
                                        width: '100%',
                                        top: `${rowVirtual.start}px`,
                                        height: `${rowVirtual.size}px`,
                                        outline:
                                            progress > 1 &&
                                            rowVirtual.index === tableRows.length - 1
                                                ? '1px dashed #1971c2'
                                                : 'none',
                                        outlineOffset: -1,
                                        pointerEvents: 'none',
                                    }}
                                />
                            )
                        }
                    </div>
                ))}
            </div>
        </div>
    )
}
