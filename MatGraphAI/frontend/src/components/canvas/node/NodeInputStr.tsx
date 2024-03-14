import { RefObject, useEffect } from "react"
import { AttributeIndex } from "../../../types/canvas.types"
import { useMantineColorScheme } from "@mantine/core"

interface NodeInputStrProps {
  handleStrChange: (id: string, e: React.ChangeEvent<HTMLInputElement>) => void
  handleIndexChange: (id: string, e: React.ChangeEvent<HTMLInputElement>) => void
  handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
  handleBlur: () => void
  getNewRef: () => RefObject<HTMLInputElement>
  id: string
  defaultValue: string | undefined
  showIndices: boolean
  index?: AttributeIndex | AttributeIndex[]
  autoFocus: boolean
  add: boolean
  zIndex: number

}

export default function NodeInputStr(props: NodeInputStrProps) {
  const {
    handleStrChange,
    handleIndexChange,
    handleKeyUp,
    handleBlur,
    getNewRef,
    id,
    defaultValue,
    showIndices,
    index,
    autoFocus,
    add,
    zIndex,
  } = props

  const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'
  const inputClass = darkTheme ? "input-dark-1" : "input-light-1"

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
      }}
    >
      <input
        className={`${inputClass}`}
        ref={getNewRef()}
        type="text"
        placeholder={placeholder}
        defaultValue={defaultValue}
        onChange={(e) => handleStrChange(id, e)} // write nodeName state
        onKeyUp={handleKeyUp} // confirm name with enter
        onBlur={handleBlur}
        autoFocus={autoFocus}
        style={{
          marginTop: add ? 8 : 0,
          zIndex: zIndex,
          width: 225,
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
            marginTop: add ? 8 : 0,
            marginLeft: 8,
            zIndex: zIndex,
            width: 80,
          }}
        />
      )}
    </div>
  )
}