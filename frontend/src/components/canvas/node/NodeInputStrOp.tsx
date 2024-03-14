import { Select, useMantineColorScheme } from "@mantine/core"
import React, { RefObject, useEffect, useRef, useState } from "react"
import { AttributeIndex, Operator } from "../../../types/canvas.types"

interface NodeInputStrOpProps {
  handleOpChange: (id: string, operator: string) => void
  handleValChange: (id: string, e: React.ChangeEvent<HTMLInputElement>) => void
  handleIndexChange: (id: string, e: React.ChangeEvent<HTMLInputElement>) => void
  handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
  handleBlur: () => void
  getNewRef: () => RefObject<HTMLInputElement>
  id: string
  defaultOp: string
  defaultVal: string
  showIndices: boolean
  index?: AttributeIndex | AttributeIndex[]
  autoFocus: boolean
  zIndex: number
}

export default function NodeInputStrOp(props: NodeInputStrOpProps) {
  const {
    handleOpChange,
    handleValChange,
    handleIndexChange,
    handleKeyUp,
    handleBlur,
    getNewRef,
    id,
    defaultOp,
    defaultVal,
    showIndices,
    index,
    autoFocus,
    zIndex
  } = props
  const [selectOpen, setSelectOpen] = useState(false)

  const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'
  const inputClass = darkTheme ? "input-dark-1" : "input-light-1"

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
        // className={`${inputClass}`}
        ref={getNewRef()}
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
        styles={{
          input: {
            height: 40,
            border: darkTheme ? "1px solid #333" : "1px solid #ced4da",
            filter: darkTheme
              ? "drop-shadow(1px 1px 1px #111)"
              : "drop-shadow(1px 1px 1px #ddd)"
          }
        }}
        style={{
          width:60,
          borderRight: "none",
          zIndex: selectOpen ? zIndex + 10 : zIndex,
          // filter: "drop-shadow(1px 1px 1px #111)",
          // border: "1px solid #333",
          borderRadius: 5,
        }}
      />
      <input
        className={`${inputClass}`}
        ref={getNewRef()}
        type="text"
        placeholder={placeholder}
        defaultValue={defaultVal}
        onChange={(e) => handleValChange(id, e)}
        onKeyUp={handleKeyUp}
        onBlur={handleBlur}
        autoFocus={autoFocus}
        style={{
          width: 157,
          marginLeft: 8,
          zIndex: zIndex,
        }}
      />
      {showIndices && (
        <input
          className={`${inputClass}`}
          ref={getNewRef()}
          type="text"
          placeholder="Idx"
          defaultValue={index !== undefined ? index.toString() : ""}
          onChange={(e) => handleIndexChange(id, e)}
          onKeyUp={handleKeyUp}
          onBlur={handleBlur}
          style={{
            marginLeft: 8,
            zIndex: zIndex,
            width: 80,
          }}
        />
      )}
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