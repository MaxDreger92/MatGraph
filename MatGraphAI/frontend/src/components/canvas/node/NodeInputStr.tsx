import { RefObject, useContext, useEffect } from "react"
import { AttributeIndex } from "../../../types/canvas.types"
import { useMantineColorScheme } from "@mantine/core"
import CloseIcon from "@mui/icons-material/Close"
import RefContext from "../../workflow/context/RefContext"

interface NodeInputStrProps {
  handleStrChange: (id: string, e: React.ChangeEvent<HTMLInputElement>) => void
  handleIndexChange: (id: string, e: React.ChangeEvent<HTMLInputElement>) => void
  handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
  handleBlur: () => void
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
    id,
    defaultValue,
    showIndices,
    index,
    autoFocus,
    add,
    zIndex,
  } = props

  const { getNewInputRef, getNewSvgRef } = useContext(RefContext)

  const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'
  const inputClass = darkTheme ? "input-dark-1" : "input-light-1"

  // const deleteIndexLocal = () => {
  //   if (index = )
  // }

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "row",
      }}
    >
      <input
        className={`${inputClass}`}
        ref={getNewInputRef()}
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
        <div style={{position: "relative", display: "flex"}}>
          <input
            className={`${inputClass}`}
            ref={getNewInputRef()}
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
              width: 110,
            }}
          />
          <CloseIcon
            ref={getNewSvgRef()}
            style={{
              position: "absolute",
              right: 0,
              transform: add ? "translate(0, 4px)" : "none",
              alignSelf: "center",
              zIndex: zIndex,
              color: darkTheme ? "#333" : "#ced4da",
              cursor: "pointer"
            }}
          />
        </div>
      )}
    </div>
  )
}