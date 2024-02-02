// import ScienceIcon from '@mui/icons-material/Science';
// import InputIcon from "@mui/icons-material/Input"
// import OutputIcon from "@mui/icons-material/Output"
// import ParameterIcon from "@mui/icons-material/Tune"

import React, { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react"
import { Planet } from "react-planet"
import chroma, { hsl } from "chroma-js"
import { useSpring, animated } from "react-spring"

import ManufacturingIcon from "@mui/icons-material/PrecisionManufacturing"
import PropertyIcon from "@mui/icons-material/Description"
import ParameterIcon from "@mui/icons-material/Tune"
import MeasurementIcon from "@mui/icons-material/SquareFoot"
import MatterIcon from "@mui/icons-material/Diamond"
import MetadataIcon from '@mui/icons-material/DataObject';

import { Position } from "../../types/canvas.types"
import { colorPalette } from "../../types/colors"
import { INode } from "../../types/canvas.types"
import { possibleConnections } from "../../common/helpers"

interface CanvasContextProps {
  onSelect: (nodeType: INode["type"]) => void
  open: boolean
  colorIndex: number
  contextRestrict?: INode["type"]
  position: Position
}

interface ContextButtonProps {
  onSelect: (nodeType: INode["type"]) => void
  nodeType: INode["type"]
  children: React.ReactNode
  fontColor: string
  fontSize: number
  colorIndex: number
  centerPosition: Position
  hovered: INode["type"] | null
  setHovered: React.Dispatch<React.SetStateAction<INode["type"] | null>>
  extendedHover: INode["type"] | null
  setExtendedHover: React.Dispatch<React.SetStateAction<INode["type"] | null>>
  moveOnHover: boolean
}

function ContextButton(props: ContextButtonProps) {
  const {
    onSelect,
    nodeType,
    children,
    fontColor,
    fontSize,
    colorIndex,
    centerPosition,
    hovered,
    setHovered,
    extendedHover,
    setExtendedHover,
    moveOnHover,
  } = props
  const timerIdRef = useRef<NodeJS.Timeout | null>(null)
  const buttonRef = useRef<HTMLDivElement>(null)
  const [extendedHoverPos, setExtendedHoverPos] = useState<Position>({x:0,y:0})
  const [scale, setScale] = useState(1)
  const [inverseScale, setInverseScale] = useState(1)
  const [outlineWidth, setOutlineWidth] = useState(3)

  useLayoutEffect(() => {
    // use timeout to wait for dom manipulations
    setTimeout(() => {
      if (buttonRef.current && moveOnHover) {
        // get button
        const rect = buttonRef.current.getBoundingClientRect()

        // get absolute middle of button
        const bx = rect.left + (rect.width / 2)
        const by = rect.top - 15

        // substract parent to get relative displaced position of button
        const dx = bx - centerPosition.x
        const dy = by - centerPosition.y

        // get angle
        const theta = Math.atan2(dy,dx)

        // calculate hoverScale based on length of nodeType
        const hScale = Math.max(nodeType.length * 0.13 , 1.2)

        // get total x and y displacement
        const dist = (hScale - 1.2) * 45
        // const dist = 0
        const nx = dist * Math.cos(theta) * -1
        const ny = dist * Math.sin(theta) * -1
        
        setExtendedHoverPos({x:nx,y:ny})

      }
    }, 450)
  }, [buttonRef, centerPosition, nodeType, moveOnHover])

  useEffect(() => {
    if (hovered === nodeType) {
      if (extendedHover === nodeType) {
        const hScale = Math.max(nodeType.length * 0.12 , 1.2)
        setScale(hScale)
        setInverseScale(1/(hScale-.1))
        setOutlineWidth(3/hScale)
      } else {
        setScale(1.2)
        setInverseScale(0.91)
        setOutlineWidth(3/1.2)
      }
    } else {
      setScale(1)
      setInverseScale(1)
      setOutlineWidth(3)
    }
  }, [hovered, extendedHover, nodeType])

  // delayedHover timer
  useEffect(() => {
    if (hovered === nodeType && !extendedHover) {
      timerIdRef.current = setTimeout(() => {
        setExtendedHover(nodeType)
      }, 500)
    } else if (hovered !== nodeType && extendedHover === nodeType) {
      clearTimeout(timerIdRef.current!)
      setExtendedHover(null)
    }
    return () => {
      clearTimeout(timerIdRef.current!)
    }
  }, [hovered, nodeType, extendedHover, setExtendedHover])

  // animation properties
  const buttonAnim = useSpring({
    scale: scale,
    x: extendedHover === nodeType ? -extendedHoverPos.x : 0,
    y: extendedHover === nodeType ? -extendedHoverPos.y : 0,
    config: {
      tension: extendedHover ? 500 : 1100,
      friction: extendedHover ? 75 : 26,
    }
  });

  const spanAnim = useSpring({
    scale: extendedHover === nodeType ? inverseScale : 0,
    opacity: extendedHover === nodeType ? 1 : 0
  })

  const iconAnim = useSpring({
    scale: inverseScale,
    transform: `translateY(${extendedHover === nodeType ? `-${52*inverseScale}%` : '0%'})`,
  });
  

  // mouseup on context button
  const handleMouseUpLocal = (e: React.MouseEvent) => {
    if (e.button === 2) return
    onSelect(nodeType)
  }

  // capitalize first letter in string
  const capitalizeFirstLetter = (str: string) => {
    return str.charAt(0).toUpperCase() + str.slice(1)
  }

  // color stuff
  const colors = colorPalette[colorIndex]
  const backgroundColor = colors[nodeType]
  const brightenedColor = useMemo(() =>
    chroma(backgroundColor).brighten(1).hex(), [backgroundColor]
  )
  const darkenedColor = useMemo(() =>
    chroma(backgroundColor).darken(0.5).hex(), [backgroundColor]
  )
  const outlineColor = hovered === nodeType ? brightenedColor : darkenedColor;

  return (
    <div style={{position: "relative", zIndex: hovered === nodeType ? 5 : 3}}>
    <animated.div 
      className="ctxt-button"
      onMouseUp={handleMouseUpLocal}
      onMouseEnter={() => setHovered(nodeType)}
      onMouseLeave={() => setHovered(null)}
      ref={buttonRef}
      style={{
        display: "flex",
        flexDirection: "column",
        position: "relative",
        width: 80,
        height: 80,
        backgroundColor,
        outline: `${outlineWidth}px solid ${outlineColor}`,
        outlineOffset: `-${outlineWidth}px`,
        zIndex: hovered === nodeType ? 5 : 3,
        cursor: hovered === nodeType ? "pointer" : "inherit",
        ...buttonAnim,
      }}
    >
      <animated.div
        style={{
          position: "absolute",
          ...iconAnim,
        }}
        children={children}
      />
      <animated.span className="ctxt-label"
        style={{
          position: "absolute",
          top: 36 ,
          color: fontColor,
          ...spanAnim
        }}
      >
        {capitalizeFirstLetter(nodeType)}
      </animated.span>
    </animated.div>
    </div>
  )
}

export default function CanvasContext(props: CanvasContextProps) {
  const { onSelect, open, colorIndex, contextRestrict, position } = props
  const [hovered, setHovered] = useState<INode["type"] | null>(null)
  const [extendedHover, setExtendedHover] = useState<INode["type"] | null>(null)

  // get all buttons, that should be rendered
  const buttonsToRender = useMemo(() => {
    const buttonList = possibleConnections(contextRestrict)
    return BUTTON_TYPES.filter(button => 
      buttonList.includes(button.type) || !contextRestrict
    );
  }, [contextRestrict])

  return (
    <>
      <Planet
        centerContent={
          <div 
            className="ctxt-planet"
            // ref={contextRef}
            style={{
              width: "0px",
              height: "0px",
              backgroundColor: "#808080",
              transform: "translate(-50%, -50%)"
            }}
          />
        }
        open={open}
        hideOrbit
        orbitRadius={buttonsToRender.length > 1 ? 95 : 1}
        rotation={ROTATIONS[buttonsToRender.length] || 0}
      >
        {buttonsToRender.map(button => (
          <ContextButton
            key={button.type}
            onSelect={onSelect}
            nodeType={button.type}
            children={button.icon}
            fontColor={button.fColor}
            fontSize={button.fSize}
            colorIndex={colorIndex}
            centerPosition={position}
            hovered={hovered}
            setHovered={setHovered}
            extendedHover={extendedHover}
            setExtendedHover={setExtendedHover}
            moveOnHover={buttonsToRender.length > 3}
          />
        ))}
      </Planet>

    </>
  )
}

const BUTTON_TYPES: { type: INode["type"], icon: JSX.Element, fColor: string, fSize: number }[] = [
  { type: 'matter', icon: <MatterIcon style={{ color: "#1a1b1e" }} />, fColor: "#1a1b1e", fSize: 11 },
  { type: 'manufacturing', icon: <ManufacturingIcon style={{ color: "#ececec" }} />, fColor: "#ececec", fSize: 10 },
  { type: 'parameter', icon: <ParameterIcon style={{ color: "#ececec" }} />, fColor: "#ececec", fSize: 11 },
  { type: 'property', icon: <PropertyIcon style={{ color: "#ececec" }} />, fColor: "#ececec", fSize: 11 },
  { type: 'metadata', icon: <MetadataIcon style={{ color: "#1a1b1e" }} />, fColor: "#1a1b1e", fSize: 11 },
  { type: 'measurement', icon: <MeasurementIcon style={{ color: "#1a1b1e" }} />, fColor: "#1a1b1e", fSize: 11 },
];

const ROTATIONS: { [key: number]: number } = {
  1: 0,
  2: 90,
  3: 120,
  5: 144,
  6: 120,
};
