import { useVirtualizer } from '@tanstack/react-virtual'
import { ColumnDef, useReactTable, getCoreRowModel } from '@tanstack/react-table'
import { TableRow } from '../../types/workflow.types'
import React, { useEffect, useMemo } from 'react'

interface UserTableProps {
    tableRows: TableRow[]
}

export default function UserTable(props: UserTableProps) {
    const { tableRows } = props

    const tableRef = React.createRef<HTMLDivElement>()

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
        getCoreRowModel: getCoreRowModel(),
    })

    const rowVirtualizer = useVirtualizer({
        count: tableRows.length,
        getScrollElement: () => tableRef.current,
        estimateSize: () => 50,
        overscan: tableRows.length,
    })

    useEffect(() => {
        console.log(rowVirtualizer.getTotalSize())
    }, [rowVirtualizer])

    return (
        <div
            ref={tableRef}
            className="user-table"
            style={{
                position: 'absolute',
                display: 'flex',
                flexDirection: 'column',
                height: 300,
                width: 1000,
                overflow: 'auto',
                // border: '1px solid #333',
                // justifyContent: 'center',
                alignItems: 'center',
                margin: 'auto',
            }}
        >
            {/* Header */}
            <div
                style={{
                    position: 'sticky',
                    width: 980,
                    height: 50,
                    flexShrink: 0,
                    top: 0,
                    zIndex: 2,
                    backgroundColor: '#25262b',
                }}
            >
                {columns.map((column, index) => {
                    const header = String(columns[index].header)
                    return (
                        <div
                            key={column.id}
                            style={{
                                display: 'inline-block',
                                position: 'absolute',
                                left: index > 1 ? index * 160 + 180 : index * 250,
                                width: index < 2 ? 250 : 160,
                                height: 50,
                                textAlign: 'left',
                                lineHeight: '50px',
                                borderBottom: '2px solid #333',
                                borderRight: index + 1 < Object.keys(tableRows[0]).length ? '1px solid #333' : 'none',
                            }}
                        >
                            <div
                                style={{
                                    position: 'absolute',
                                    width: '100%',
                                    height: '100%',
                                    padding: '11px 0 0 11px',
                                }}
                            >
                                {header}
                            </div>
                        </div>
                    )
                })}
            </div>

            {/* Content */}
            <div
                style={{
                    position: 'relative',
                    height: `${rowVirtualizer.getTotalSize()}px`,
                    width: 980,
                    top: 0,
                    zIndex: 1,
                }}
            >
                {rowVirtualizer.getVirtualItems().map((virtualItem) => (
                    <div
                        key={virtualItem.key}
                        style={{
                            position: 'absolute',
                            // top: `${virtualItem.start}px`,
                            top: 0,
                            left: 0,
                            height: `${virtualItem.size}px`,
                            width: '100%',
                            transform: `translateY(${virtualItem.start}px)`,
                            display: 'flex',
                            borderBottom: virtualItem.index + 1 < tableRows.length ? '1px solid #333' : 'none',
                            backgroundColor: '#212226',
                        }}
                    >
                        {columns.map((column, index) => (
                            <div
                                key={column.id}
                                style={{
                                    width: index < 2 ? 250 : 160,
                                    padding: '11px 0 0 11px',
                                    borderRight: index + 1 < Object.keys(tableRows[0]).length ? '1px solid #333' : 'none',
                                }}
                            >
                                {String(tableRows[virtualItem.index][column.id as keyof TableRow])}
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    )
}
