import React, { ReactElement, useEffect, useRef, useState } from "react"
import { useMantineColorScheme } from "@mantine/core"

import { useSpring, animated } from 'react-spring'

import { TbBinaryTree as GraphIcon } from "react-icons/tb"
import { PiGraphFill as GraphIcon2 } from "react-icons/pi"
import ResetIcon from "@mui/icons-material/RestartAlt"
import { MdUndo as UndoIcon } from "react-icons/md"
import { MdRedo as RedoIcon } from "react-icons/md"
import { VscSave } from "react-icons/vsc";
import { FiSave } from "react-icons/fi";
import { AiOutlineSave } from "react-icons/ai";
import { MdRestartAlt as ResetIcon2 } from "react-icons/md"
import { PiDotsSixVertical as HandleIcon } from "react-icons/pi"

import { TCanvasButton, Position } from "../../types/canvas.types"
import { clamp } from "../../common/helpers"
import { Tooltip } from 'react-tooltip'

interface CanvasButtonGroupProps {
  canvasRect: DOMRect | null
  onSelect: (buttonType: TCanvasButton["type"]) => void
}

interface CanvasButtonProps {
  onSelect: (buttonType: TCanvasButton["type"]) => void
  buttonType: TCanvasButton["type"]
  children: React.ReactNode
  vertical: boolean
  tooltipText: string
  darkTheme: boolean
  iconStyle: React.CSSProperties
}

function CanvasButton(props: CanvasButtonProps) {
  const { onSelect, buttonType, children, vertical, tooltipText, darkTheme, iconStyle } = props
  const [buttonHovered, setButtonHovered] = useState<
    TCanvasButton["type"] | null
  >(null)
  const [buttonDown, setButtonDown] = useState<TCanvasButton["type"] | null>(
    null
  )

  const handleMouseUpLocal = (e: React.MouseEvent) => {
    if (e.button === 2) return
    onSelect(buttonType)
  }

  const handleMouseLeave = () => {
    setButtonHovered(null)
    setButtonDown(null)
  }

  const Icon = React.cloneElement(children as ReactElement, {style: iconStyle })

  return (
    <>
    <div
      className="canvas-btn2"
      data-tooltip-id="canvas-btn-tooltip"
      data-tooltip-content={tooltipText}
      data-tooltip-place={vertical ? "right" : "bottom"}
      data-tooltip-offset={15}
      data-tooltip-delay-hide={0}
      onClick={handleMouseUpLocal}
      onMouseEnter={() => setButtonHovered(buttonType)}
      onMouseLeave={handleMouseLeave}
      onMouseDown={() => setButtonDown(buttonType)}
      onMouseUp={() => setButtonDown(null)}
      children={Icon}
      style={{
        width: vertical ? 45 : 60,
        height: vertical ? 60 : 40,
        backgroundColor:
          buttonDown === buttonType
            ? darkTheme ? "#1a1b1e" : "#dee2e6"
            : buttonHovered === buttonType
            ? darkTheme ? "#2c2e33" : "#f1f3f5"
            : darkTheme ? "#25262b" : "#fff",
        // transform: buttonHovered === buttonType ? "scale(1.05)" : "none",
        zIndex: buttonHovered === buttonType ? 10 : 1,
        cursor: buttonHovered === buttonType ? "pointer" : "default",
      }}
    />
    <Tooltip id="canvas-btn-tooltip" className="canvas-btn-ttip"
      style={{
        backgroundColor: darkTheme ? "#2c2e33" : "#f1f3f5",
        color: darkTheme ? "#c1c2c5" : "#343a40",
      }}
    />
    </>
  )
}

export default function CanvasButtonGroup(props: CanvasButtonGroupProps) {
  const { canvasRect, onSelect } = props
  const [initialized, setInitialized] = useState(false)
  const [positioned, setPositioned] = useState(true)
  const [position, setPosition] = useState<Position>({ x: 12, y: 77 })
  const [manualPosition, setManualPosition] = useState<Position>({ x: 12, y: 77 })
  const [vertical, setVertical] = useState(true)
  const [left, setLeft] = useState(true)
  const [moveable, setMoveable] = useState(false)
  const [btnAnimated, setBtnAnimated] = useState(true)
  const [handleHovered, setHandleHovered] = useState(false)
  const buttonsRef = useRef<HTMLDivElement>(null)
  const [isResizing, setIsResizing] = useState(false)
  const resizeObserver = useRef<ResizeObserver | null>(null)
  const canvasBtnRef = useRef<HTMLDivElement>(null);

  // useEffect(() => {
  //   resizeObserver.current = new ResizeObserver(() => {
  //     setIsResizing(true)
  //   })

  //   if (canvasBtnRef.current) {
  //     resizeObserver.current.observe(canvasBtnRef.current)
  //   }

  //   return () => {
  //     if (resizeObserver.current) {
  //       resizeObserver.current.disconnect()
  //     }
  //   }
  // }, [canvasRect])

  // load position from local storage
  useEffect(() => {
    const positioned = localStorage.getItem("canvasBtnPositioned")
    const position = localStorage.getItem("canvasBtnPosition")
    const vertical = localStorage.getItem("canvasBtnVertical")
    const left = localStorage.getItem("canvasBtnLeft")

    if (positioned) setPositioned(JSON.parse(positioned))
    if (position) {
      setManualPosition(JSON.parse(position))
      // setPosition(JSON.parse(position))
    }
    if (vertical) setVertical(JSON.parse(vertical))
    if (left) setLeft(JSON.parse(left))
    
    const timer = setTimeout(() => {
      setInitialized(true)
    }, 100)

    return () => clearTimeout(timer)
  }, [])

  // save position to local storage
  useEffect(() => {
    localStorage.setItem("canvasBtnPositioned", JSON.stringify(positioned))
    localStorage.setItem("canvasBtnPosition", JSON.stringify(manualPosition))
    localStorage.setItem("canvasBtnVertical", JSON.stringify(vertical))
    localStorage.setItem("canvasBtnLeft", JSON.stringify(left))
  }, [positioned, manualPosition, vertical, left])

  // automatic positioning (!positioned)
  useEffect(() => {
    if (!canvasRect || !buttonsRef.current || positioned) return

    setPosition({
      x: canvasRect.left + canvasRect.width / 2 - buttonsRef.current.offsetWidth / 2 - 22,
      y: 77,
    })

    setVertical(false)
    setLeft(false)
  }, [positioned, canvasRect, initialized])

  // manual positioning (sets positioned)
  const moveButtons = (e: React.MouseEvent) => {
    if (!moveable || !canvasRect) return

    const mouseX = e.clientX
    const mouseY = e.clientY

    let btnX, btnY

    if (mouseX <= canvasRect.left + 90) { // left
      setVertical(true)
      setLeft(true)
      btnX = canvasRect.left + 12
      btnY = clamp(mouseY - 19, 77, canvasRect.bottom - 350)
    } else if (mouseX <= (canvasRect.right - 90)) { // top
      setVertical(false)
      setLeft(false)
      btnX = clamp(mouseX - 15,canvasRect.left + 91, canvasRect.left + canvasRect.width - 350)
      btnY = 77
    } else { // right
      setVertical(true)
      setLeft(false)
      btnX = canvasRect.right - 69
      btnY = clamp(mouseY - 19, 77, canvasRect.bottom - 350)
    }

    setPositioned(true)
    setManualPosition({ x: btnX, y: btnY })
    setPosition({ x: btnX, y: btnY })
  }

  // manual positioning automatic fixes
  useEffect(() => {
    if (!(canvasRect && buttonsRef.current && positioned && initialized) || moveable) return

    if (vertical && left) {
      setPosition({
        x: canvasRect.left + 12,
        y: clamp(manualPosition.y, 77, canvasRect.bottom - 350)
      })
    } else if (vertical) {
      setPosition({
        x: canvasRect.right - 69,
        y: clamp(manualPosition.y, 77, canvasRect.bottom - 350)
      })
    } else {
      setPosition({
        x: clamp(manualPosition.x, canvasRect.left + 91, canvasRect.right - 350),
        y: manualPosition.y
      })
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canvasRect, positioned, initialized])

  // reset button positioning (sets !positioned)
  const resetButtons = () => {
    if (!canvasRect || !buttonsRef.current) return

    // let width
    // if (vertical) {
    //   width = buttonsRef.current.offsetHeight / 2
    // } else {
    //   width = buttonsRef.current.offsetWidth / 2
    // }
    setPositioned(false)

    // setPosition({
    //   x: canvasRect.width / 2 - width - 22,
    //   y: 12,
    // })
    setVertical(false)
    setLeft(false)
  }

  useEffect(() => {
    if (!moveable) {
      const timer = setTimeout(() => {
        setBtnAnimated(true)
      }, 700)
  
      return () => clearTimeout(timer)
    }
  }, [moveable])

  const springProps = useSpring({
    top: position.y,
    left: position.x,
    config: {
      tension: 1000,
      friction: 100,
    }
  })

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'

  const iconStyle = { color: darkTheme ? "#a6a7ab" : "#222"}

  return (
    <div
      ref={canvasBtnRef}
      className="canvas-btn-window"
      style={{
        width: "100%",
        height: "100%",
        cursor: moveable ? "grabbing" : handleHovered ? "grab" : "inherit",
      }}
      onMouseMove={moveButtons}
      // onMouseLeave={() => setMoveable(false)}
      onMouseUp={(e: React.MouseEvent) => {
        if (moveable) e.stopPropagation()
        setMoveable(false)
      }}
    >
      {initialized && (
        <animated.div
          className="canvas-btn-wrap"
          style={{
            backgroundColor: darkTheme ? "#25262b" : "#fff",
            border: `1px solid ${(darkTheme ? "#333333" : "#ced4da")}`,
            pointerEvents: "all",
            // transform: `translate(${position.x}px,${position.y}px)`,
            top: btnAnimated ? springProps.top : position.y,
            left: btnAnimated ? springProps.left : position.x,
            // top: position.y,
            // left: position.x,
            flexDirection: vertical ? "column" : "row",
            // visibility: initialized ? "visible" : "hidden",
          }}
          ref={buttonsRef}
        >
          <div
            className="canvas-btn-handle"
            style={{
              margin: vertical ? "-5px 0 0 0" : "0 0 0 -5px",
            }}
            onMouseEnter={() => setHandleHovered(true)}
            onMouseLeave={() => setHandleHovered(false)}
            onMouseUp={(e: React.MouseEvent) => {
              e.stopPropagation()
              setMoveable(false)
            }}
            onMouseDown={(e: React.MouseEvent) => {
              e.stopPropagation()
              setMoveable(true)
              setBtnAnimated(false)
            }}
            onDoubleClick={resetButtons}
            children={
              <HandleIcon
                className="canvas-btn-handle-icon"
                style={{
                  color: darkTheme ? "#a6a7ab" : "#040404",
                  transform: vertical ? "rotate(90deg)" : "none",
                }}
              />
            }
          />
          <div
            className="canvas-btn-divider"
            style={{
              margin: vertical ? "0 -5px 5px -5px" : "-5px 5px -5px 0",
              width: vertical ? 55 : 1,
              height: vertical ? 1 : 50,
              backgroundColor: darkTheme ? "#333" : "#ced4da"
            }}
          />
          {BUTTON_TYPES.map((button) => (
            <CanvasButton
              key={button.type}
              onSelect={onSelect}
              buttonType={button.type}
              children={button.icon}
              vertical={vertical}
              tooltipText={button.tooltip}
              darkTheme={darkTheme}
              iconStyle={iconStyle}
            />
          ))}
        </animated.div>
      )}
    </div>
  )
}

const BUTTON_TYPES: { type: TCanvasButton["type"]; icon: JSX.Element; tooltip: string }[] = [
  { type: "undo", icon: <UndoIcon className="canvas-btn-icon" />, tooltip: "Undo" },
  { type: "reset", icon: <ResetIcon2 className="canvas-btn-icon" />, tooltip: "Reset Canvas" },
  { type: "redo", icon: <RedoIcon className="canvas-btn-icon" />, tooltip: "Redo" },
  { type: "layout", icon: <GraphIcon2 className="canvas-btn-icon" />, tooltip: "Layout Nodes" },
  { type: "saveGraph", icon: <VscSave className="canvas-btn-save-icon" />, tooltip: "Save Graph" },
];

