import { Select } from "@mantine/core"
import React, { RefObject, useEffect, useRef, useState } from "react"
import { Operator } from "../../../types/canvas.types"

interface NodeInputStrOpProps {
  handleOpChange: (id: string, operator: string) => void
  handleValChange: (id: string, e: React.ChangeEvent<HTMLInputElement>) => void
  handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
  handleBlur: () => void
  id: string
  opReference: RefObject<HTMLInputElement>
  valReference: RefObject<HTMLInputElement>
  defaultOp: string
  defaultVal: string
  autoFocus: boolean
  zIndex: number
}

export default function NodeInputStrOp(props: NodeInputStrOpProps) {
  const {
    handleOpChange,
    handleValChange,
    handleKeyUp,
    handleBlur,
    id,
    opReference,
    valReference,
    defaultOp,
    defaultVal,
    autoFocus,
    zIndex
  } = props
  const [selectOpen, setSelectOpen] = useState(false)

  const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

  const toggleSelectOpen = () => {
    if (selectOpen) {
      setTimeout(() => {
        setSelectOpen(false)
      }, 100)
    } else {
      setSelectOpen(true)
    }
  }

  const handleOpChangeLocal = (e: string | null) => {
    if (e === null) {
      handleOpChange(id, "")
    } else if (typeof e === 'string') {
      handleOpChange(id, e)
    }
  }
  

  return (
    <>
    <div
      style={{
        display: "flex",
        flexDirection: "row",
        marginTop: 8,
      }}
    >
      {/* {selectOpen && (
        <div
          onClick={(e) => e.stopPropagation()}
          onMouseUp={(e) => e.stopPropagation()}
          style={{
            backgroundColor: "transparent",
            width: 60,
            height: 280,
            position: "absolute",
            zIndex: zIndex,
          }}
        />
      )} */}
      <Select
        ref={opReference}
        onChange={handleOpChangeLocal}
        onKeyUp={handleKeyUp}
        onBlur={handleBlur}
        placeholder="---"
        defaultValue={defaultOp}
        data={SELECT_DATA}
        allowDeselect
        onDropdownOpen={toggleSelectOpen}
        onDropdownClose={toggleSelectOpen}
        maxDropdownHeight={Infinity}
        style={{
          width: "25%",
          borderRight: "none",
          zIndex: selectOpen ? zIndex + 10 : zIndex,
          filter: "drop-shadow(1px 1px 1px #111",
        }}
      />
      <input
        ref={valReference}
        type="text"
        placeholder={placeholder}
        defaultValue={defaultVal}
        onChange={(e) => handleValChange(id, e)}
        onKeyUp={handleKeyUp}
        onBlur={handleBlur}
        autoFocus={autoFocus}
        style={{
          width: "calc(75% - 8px)",
          marginLeft: 8,
          zIndex: zIndex,
        }}
      />
    </div>

    </>
  )
}

const SELECT_DATA: { value: string; label: string }[] = [
  { value: "<", label: "<" },
  { value: "<=", label: "\u2264" },
  { value: "=", label: "=" },
  { value: "!=", label: "\u2260" },
  { value: ">=", label: "\u2265" },
  { value: ">", label: ">" },
]