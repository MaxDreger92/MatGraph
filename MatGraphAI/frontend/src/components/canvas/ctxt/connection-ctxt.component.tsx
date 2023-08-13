import React, { useState } from "react"
import { Planet } from "react-planet"

import CloseIcon from "@mui/icons-material/Close"
import SwapHorizIcon from "@mui/icons-material/SwapHoriz"


import { hoverColors } from "../types/colorPalette"

interface ConnectionContextProps {
  onSelect: (action: string) => void
  isOpen: boolean
}

interface ContextButtonProps {
  onSelect: (action: string) => void
  children: React.ReactNode
  action: string
}

function ContextButton(props: ContextButtonProps) {
  const { onSelect, children, action } = props
  const [hovered, setHovered] = useState(false)

  const handleClick = (e: React.MouseEvent) => {
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
      onClick={handleClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: 40,
        height: 40,
        backgroundColor: "#666666",
      }}
    >
      {styledChild}
    </div>
  )
}

export default function ConnectionContext(props: ConnectionContextProps) {
  const { onSelect, isOpen} = props

  console.log("rendered")

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
      />
      <ContextButton
        onSelect={onSelect}
        children={<CloseIcon />}
        action="delete"
      />
    </Planet>
  )
}
