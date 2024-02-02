import { RefObject, useEffect } from "react"

interface NodeInputStrProps {
  handleChange: (id: string, e: React.ChangeEvent<HTMLInputElement>) => void 
  handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
  handleBlur: () => void
  id: string
  reference: RefObject<HTMLInputElement>
  defaultValue: string | undefined
  autoFocus: boolean
  add: boolean
  zIndex: number
}

export default function NodeInputStr(props: NodeInputStrProps) {
  const {
    handleChange,
    handleKeyUp,
    handleBlur,
    id,
    reference,
    defaultValue,
    autoFocus,
    add,
    zIndex
  } = props

  const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

  return (
    <input
      ref={reference}
      type="text"
      placeholder={placeholder}
      defaultValue={defaultValue}
      onChange={(e) => handleChange(id, e)} // write nodeName state
      onKeyUp={handleKeyUp} // confirm name with enter
      onBlur={handleBlur}
      autoFocus={autoFocus}
      style={{
        marginTop: add ? 8 : 0,
        zIndex: zIndex,
        // outline: "none",
        // borderRadius: "3px",
        // border: "1px solid #333333",
        // padding: "5px",
        // backgroundColor: "#25262b",
        // color: "#c1c2c5",
        // filter: "drop-shadow(1px 1px 1px #111)",
      }}
    />
  )
}