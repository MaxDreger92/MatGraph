import React, { useRef, useMemo, useEffect, useState } from "react"
import { useVirtualizer } from "@tanstack/react-virtual"
import {
  useReactTable,
  ColumnDef,
  getCoreRowModel,
} from "@tanstack/react-table"
import { TableRow } from "../../types/workflow.types"
import { Label } from "../../types/workflow.types"
import { Select } from "@mantine/core"
import { getAttributesByLabel } from "../../common/helpers"

interface WorkflowTableProps {
  setLabelTable: React.Dispatch<React.SetStateAction<TableRow[]>>
  setAttributeTable: React.Dispatch<React.SetStateAction<TableRow[]>>
  setTableRows: React.Dispatch<React.SetStateAction<TableRow[]>>
  tableRows: TableRow[]
  progress: number
  drawerRect: DOMRect | null
}

const labelOptions = [
  { value: "matter", label: "Matter" },
  { value: "manufacturing", label: "Manufacturing" },
  { value: "measurement", label: "Measurement" },
  { value: "parameter", label: "Parameter" },
  { value: "property", label: "Property" },
  { value: "metadata", label: "Metadata" },
]

export default function WorkflowTable(props: WorkflowTableProps) {
  const {
    setLabelTable,
    setAttributeTable,
    setTableRows,
    tableRows,
    progress,
    drawerRect,
  } = props
  const [selected, setSelected] = useState<{
    row: number
    column: string
  } | null>(null)
  const [hovered, setHovered] = useState<{
    row: number
    column: number
  } | null>(null)

  const tableRef = useRef<HTMLDivElement>(null)
  const tableRowsRef = useRef<HTMLDivElement>(null)
  const [tableRect, setTableRect] = useState<DOMRect | null>(null)
  const [tableDivHeight, setTableDivHeight] = useState<number | null>(null)

  const [selectData, setSelectData] = useState<
    { value: string; label: string }[]
  >([])

  useEffect(() => {
    if (tableRef.current && typeof ResizeObserver === "function") {
      const observer = new ResizeObserver((entries) => {
        const [entry] = entries
        setTableRect(entry.contentRect)
      })

      observer.observe(tableRef.current)

      return () => observer.disconnect()
    }
  }, [tableRef, tableRows])

  useEffect(() => {
    // 50 + 45 * tableRows
    if (drawerRect) {
      const rowHeight = 52 + 45 * tableRows.length
      const divHeight = drawerRect.height - 90
      setTableDivHeight(Math.min(rowHeight, divHeight))
      return
    }
    setTableDivHeight(null)
  }, [tableRows, drawerRect])

  const handleCellClick = (
    cellData: string | number | boolean,
    row: number,
    columnId: string
  ): void => {
    if (progress === 2 && row === 0) {
      if (
        typeof cellData === "string" &&
        labelOptions.some((option) => option.value === (cellData.toLowerCase() as Label))
      ) {
        setSelectData(labelOptions)
        setSelected({ row: row, column: columnId })
      }
    } else if (progress === 3 && row === 1) {
      const labelKey = tableRows[0][columnId]
      if (
        typeof labelKey === "string" &&
        labelOptions.some((option) => option.value === (labelKey.toLowerCase() as Label))
      ) {
        const attributes = getAttributesByLabel(labelKey.toLowerCase() as Label)
        if (attributes && typeof cellData === "string" && attributes.includes(cellData.toLowerCase())) {
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

  const handleSelectChange = (
    value: string | null,
    rowIndex: number,
    columnId: string
  ) => {
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
    overscan: 15,
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

  function capitalizeFirstLetter(item: string | number | boolean) {
    if (!(typeof item === "string")) return item
    return item.charAt(0).toUpperCase() + item.slice(1)
  }

  // Render your table
  return (
    <div
      key={tableRows.length}
      ref={tableRef}
      className="workflow-table"
      style={{
        position: "relative",
        display: "flex",
        flexDirection: "column",
        height: tableDivHeight ? tableDivHeight : `calc(100% - 90px)`,
        width: `calc(100% - 20px)`,
        left: 10,
        overflow: "auto",
        border: "1px solid #333",
        backgroundColor: "#212226",
      }}
    >
      {/* Header */}
      <div
        style={{
          position: "sticky",
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
                display: "inline-block",
                position: "absolute",
                left: `${columnVirtual.start}px`,
                width: `${columnVirtual.size}px`,
                height: "50px",
                borderBottom: "1px solid #333",
                textAlign: "left",
                lineHeight: "50px",
                backgroundColor: "#25262b",
                color: "#a6a7ab",
                borderRight: "1px solid #333",
                paddingLeft: ".5rem",
              }}
            >
              {header}
            </div>
          )
        })}
      </div>

      {/* Rows */}
      <div
        ref={tableRowsRef}
        style={{
          position: "relative",
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
                position: "absolute",
                top: `${rowVirtual.start}px`,
                height: `${rowVirtual.size}px`,
                width: "100%",
                cursor:
                  progress > 1 && rowVirtual.index === tableRows.length - 1
                    ? "pointer"
                    : "default",
              }}
            >
              {columnVirtualizer.getVirtualItems().map((columnVirtual) => {
                const column = columns[columnVirtual.index]
                const columnId = column.id // Assuming columnId is always defined based on your column setup
                if (typeof columnId !== "undefined") {
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
                        display: "inline-block",
                        position: "absolute",
                        left: `${columnVirtual.start}px`,
                        width: `${columnVirtual.size}px`,
                        height: "100%",
                        backgroundColor:
                          progress > 1 &&
                          rowVirtual.index === tableRows.length - 1 &&
                          hovered &&
                          hovered.row === rowVirtual.index &&
                          hovered.column === columnVirtual.index &&
                          !selected
                            ? "rgba(24,100,171,0.2)"
                            : "#212226",
                        color: "#a6a7ab",
                        // borderRight: columnVirtual.index + 1 === Object.keys(tableRows[0]).length ? "none" : "1px solid #333",
                        borderRight: "1px solid #333",
                        borderBottom:
                          rowVirtual.index + 1 === tableRows.length
                            ? "none"
                            : "1px solid #333",
                        // borderBottom: "1px solid #333",
                        paddingTop: 10,
                        paddingLeft: ".5rem",
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
                          position: "relative",
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
                                "&:focus": {
                                  outline: "none",
                                  boxShadow: "none",
                                },
                                backgroundColor: "transparent",
                                fontFamily: "inherit",
                                fontSize: "inherit",
                                transform: "translate(-4px,0)",
                              },
                            }}
                            style={{
                              transform: "translate(calc(-0.5rem), -6px)",
                              width: "calc(100% + 8px)",
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
                  position: "absolute",
                  width: "100%",
                  top: `${rowVirtual.start}px`,
                  height: `${rowVirtual.size}px`,
                  outline:
                    progress > 1 && rowVirtual.index === tableRows.length - 1
                      ? "1px dashed #1971c2"
                      : "none",
                  outlineOffset: -1,
                  pointerEvents: "none",
                }}
              />
            )}
          </>
        ))}
      </div>

      {/* Shadow */}
      <div
        style={{
          position: "fixed",
          width: `calc(100% - 22px)`,
          height: tableRect ? `${tableRect.height}px` : "100%",
          boxShadow: "inset 0px 0px 4px rgba(0, 0, 0, 0.3)",
          zIndex: 3,
          pointerEvents: "none",
          // backgroundColor: "rgba(240,100,0,0.5)",
        }}
      />
    </div>
  )
}
