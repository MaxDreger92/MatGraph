// import ScienceIcon from '@mui/icons-material/Science';
// import InputIcon from "@mui/icons-material/Input"
// import OutputIcon from "@mui/icons-material/Output"
// import ParameterIcon from "@mui/icons-material/Tune"

import { useState } from "react"
import { Planet } from "react-planet"
import chroma from "chroma-js"

import ManufacturingIcon from "@mui/icons-material/PrecisionManufacturing"
import PropertyIcon from "@mui/icons-material/Description"
import ParameterIcon from "@mui/icons-material/Tune"
import MeasurementIcon from "@mui/icons-material/SquareFoot"
import MatterIcon from "@mui/icons-material/Diamond"

import { colorPalette } from "../types/colorPalette"
import { INode } from "../types/canvas.types"

interface CanvasContextProps {
  onSelect: (nodeType: INode["type"]) => void
  open: boolean
  colorIndex: number
}

interface ContextButtonProps {
  onSelect: (nodeType: INode["type"]) => void
  nodeType: INode["type"]
  children: React.ReactNode
  colorIndex: number
}

function ContextButton(props: ContextButtonProps) {
  const { onSelect, nodeType, children, colorIndex } = props
  const [hovered, setHovered] = useState(false)

  const colors = colorPalette[colorIndex]
  const backgroundColor = colors[nodeType]

  return (
    <div
      className="ctxt-button"
      onClick={() => onSelect(nodeType)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: "80px",
        height: "80px",
        backgroundColor,
        outline: hovered
          ? `3px solid ${chroma(backgroundColor).brighten().hex()}`
          : `3px solid ${chroma(backgroundColor).darken(0.75).hex()}`,
        outlineOffset: "-3px",
        zIndex: hovered ? 5 : 3
      }}
    >
      {children}
      {hovered &&
      <div 
        style={{
          position: "absolute",
          pointerEvents: "none",
          display: "flex",
          justifyContent: "center",
          left: -60,
        }}
      >
      </div>
      }
    </div>
  )
}

export default function CanvasContext(props: CanvasContextProps) {
  const { onSelect, open, colorIndex } = props

  return (
    <Planet
      centerContent={
        <div 
          className="ctxt-planet"
          style={{
            width: "10px",
            height: "10px",
            backgroundColor: "#808080",
            transform: "translate(-50%, -50%)"
          }}
        />
      }
      open={open}
      hideOrbit
      orbitRadius={75}
      rotation={144}
    >
      <ContextButton
        onSelect={onSelect}
        nodeType="matter"
        children={<MatterIcon style={{ color: "#1a1b1e" }} />}
        colorIndex={colorIndex}
      />
      <ContextButton
        onSelect={onSelect}
        nodeType="manufacturing"
        children={<ManufacturingIcon style={{ color: "#ececec" }} />}
        colorIndex={colorIndex}
      />
      <ContextButton
        onSelect={onSelect}
        nodeType="parameter"
        children={<ParameterIcon style={{ color: "#ececec" }} />}
        colorIndex={colorIndex}
      />
      <ContextButton
        onSelect={onSelect}
        nodeType="property"
        children={<PropertyIcon style={{ color: "#ececec" }} />}
        colorIndex={colorIndex}
      />
      <ContextButton
        onSelect={onSelect}
        nodeType="measurement"
        children={<MeasurementIcon style={{ color: "#1a1b1e" }} />}
        colorIndex={colorIndex}
      />
    </Planet>
  )
}
