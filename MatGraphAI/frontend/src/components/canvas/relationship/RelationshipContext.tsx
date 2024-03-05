import React, { useState } from "react"
import { Planet } from "react-planet"

import CloseIcon from "@mui/icons-material/Close"
import SwapHorizIcon from "@mui/icons-material/SwapHoriz"

import { hoverColors } from "../../../types/colors"

interface RelationshipContextProps {
  onSelect: (action: string) => void
  isOpen: boolean
  darkTheme: boolean
}

interface ContextButtonProps {
  onSelect: (action: string) => void
  children: React.ReactNode
  action: string
  darkTheme: boolean
}

function ContextButton(props: ContextButtonProps) {
  const { onSelect, children, action, darkTheme } = props
  const [hovered, setHovered] = useState(false)

  const handleSelect = (e: React.MouseEvent) => {
    e.stopPropagation()
    onSelect(action)
  }

  const hoverColor = hoverColors[action] || hoverColors.default

  const styledChild = React.Children.map(children, (child) =>
  React.isValidElement(child)
    ? React.cloneElement(child as React.ReactElement<any>, {
        style: { color: hovered ? hoverColor : "#1a1b1e" },
      })
    : child
  )

  return (
    <div
      className="ctxt-button"
      onMouseDown={(e: React.MouseEvent) => e.stopPropagation()}
      onMouseUp={handleSelect}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: 40,
        height: 40,
        backgroundColor: darkTheme ? "#666666" : "#fff",
        cursor: hovered ? "pointer" : "inherit",
        border: darkTheme ? "none" : "1px solid #ced4da",
        filter: `drop-shadow(1px 1px 1px ${(darkTheme ? "#111" : "#ddd")})`,
      }}
    >
      {styledChild}
    </div>
  )
}

export default function RelationshipContext(props: RelationshipContextProps) {
  const { onSelect, isOpen, darkTheme} = props

  return (
    <Planet
      centerContent={<div className="ctxt-planet" />}
      open={isOpen}
      // autoClose
      hideOrbit
      orbitRadius={40}
      rotation={90}
    >
      <ContextButton
        onSelect={onSelect}
        children={<SwapHorizIcon />}
        action="reverse"
        darkTheme={darkTheme}
      />
      <ContextButton
        onSelect={onSelect}
        children={<CloseIcon />}
        action="delete"
        darkTheme={darkTheme}
      />
    </Planet>
  )
}
