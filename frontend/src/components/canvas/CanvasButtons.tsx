import React, { useEffect, useRef, useState } from "react"

import { TbBinaryTree as GraphIcon } from "react-icons/tb"
import { PiGraph as GraphIcon2 } from "react-icons/pi"
import ResetIcon from "@mui/icons-material/RestartAlt"
import { MdUndo as UndoIcon } from "react-icons/md"
import { MdRedo as RedoIcon } from "react-icons/md"
import { VscSaveAs, VscSave } from "react-icons/vsc";
import { RiSave3Line } from "react-icons/ri";
import { MdRestartAlt as ResetIcon2 } from "react-icons/md"
import { PiDotsSixVertical as HandleIcon } from "react-icons/pi"

import { ICanvasButton, Position } from "../../types/canvas.types"
import { clamp } from "../../common/helpers"
import { Tooltip } from 'react-tooltip'

interface CanvasButtonGroupProps {
  canvasRect: DOMRect | null
  onSelect: (buttonType: ICanvasButton["type"]) => void
}

interface CanvasButtonProps {
  onSelect: (buttonType: ICanvasButton["type"]) => void
  buttonType: ICanvasButton["type"]
  children: React.ReactNode
  vertical: boolean
  tooltipText: string
}

function CanvasButton(props: CanvasButtonProps) {
  const { onSelect, buttonType, children, vertical, tooltipText } = props
  const [buttonHovered, setButtonHovered] = useState<
    ICanvasButton["type"] | null
  >(null)
  const [buttonDown, setButtonDown] = useState<ICanvasButton["type"] | null>(
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
      children={children}
      style={{
        width: vertical ? 45 : 60,
        height: vertical ? 60 : 40,
        backgroundColor:
          buttonDown === buttonType
            ? "#1a1b1e"
            : buttonHovered === buttonType
            ? "#2c2e33"
            : "#25262b",
        // transform: buttonHovered === buttonType ? "scale(1.05)" : "none",
        zIndex: buttonHovered === buttonType ? 10 : 1,
        cursor: buttonHovered === buttonType ? "pointer" : "default",
      }}
    />
    <Tooltip id="canvas-btn-tooltip" className="canvas-btn-ttip"/>
    </>
  )
}

export default function CanvasButtonGroup(props: CanvasButtonGroupProps) {
  const { canvasRect, onSelect } = props
  const [initialized, setInitialized] = useState(false)
  const [positioned, setPositioned] = useState(false)
  const [position, setPosition] = useState<Position>({ x: 12, y: 12 })
  const [vertical, setVertical] = useState(false)
  const [left, setLeft] = useState(false)
  const [moveable, setMoveable] = useState(false)
  const [handleHovered, setHandleHovered] = useState(false)
  const buttonsRef = useRef<HTMLDivElement>(null)
  const [isResizing, setIsResizing] = useState(false)
  const resizeObserver = useRef<ResizeObserver | null>(null)
  const canvasBtnRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    resizeObserver.current = new ResizeObserver(() => {
      setIsResizing(true)
    })

    if (canvasBtnRef.current) {
      resizeObserver.current.observe(canvasBtnRef.current)
    }

    return () => {
      if (resizeObserver.current) {
        resizeObserver.current.disconnect()
      }
    }
  }, [canvasRect])

  // load position from local storage
  useEffect(() => {
    const positioned = localStorage.getItem("canvasBtnPositioned")
    const position = localStorage.getItem("canvasBtnPosition")
    const vertical = localStorage.getItem("canvasBtnVertical")
    const left = localStorage.getItem("canvasBtnLeft")

    if (!position || !vertical || !positioned || !left) return

    setPositioned(JSON.parse(positioned))
    setPosition(JSON.parse(position))
    setVertical(JSON.parse(vertical))
    setLeft(JSON.parse(left))

    setInitialized(true)
  }, [])

  // save position to local storage
  useEffect(() => {
    localStorage.setItem("canvasBtnPositioned", JSON.stringify(positioned))
    localStorage.setItem("canvasBtnPosition", JSON.stringify(position))
    localStorage.setItem("canvasBtnVertical", JSON.stringify(vertical))
    localStorage.setItem("canvasBtnLeft", JSON.stringify(left))
  }, [positioned, position, vertical, left])

  // automatic positioning (!positioned)
  useEffect(() => {
    if (!canvasRect || !buttonsRef.current || positioned) return

    setPosition({
      x: canvasRect.width / 2 - buttonsRef.current.offsetWidth / 2 - 22,
      y: 12,
    })
    setVertical(false)
    setLeft(false)
    setInitialized(true)
    // setIsResizing(false)
  }, [positioned, canvasRect])

  // manual positioning (sets positioned)
  const moveButtons = (e: React.MouseEvent) => {
    if (!moveable || !canvasRect) return

    const mouseX = e.clientX - canvasRect.left
    const mouseY = e.clientY - canvasRect.top

    let btnX, btnY

    if (mouseX <= 90) { // left
      setVertical(true)
      setLeft(true)
      btnX = 12
      btnY = clamp(mouseY - 19, 12, Infinity)
    } else if (mouseX <= (canvasRect.width - 90)) { // top
      setVertical(false)
      setLeft(false)
      btnX = clamp(mouseX - 15, 91, canvasRect.width - 290)
      btnY = 12
    } else { // right
      setVertical(true)
      setLeft(false)
      btnX = canvasRect.width - 69
      btnY = clamp(mouseY - 19, 12, Infinity)
    }

    setPositioned(true)
    setPosition({ x: btnX, y: btnY })
  }

  // manual positioning automatic fixes
  useEffect(() => {
    if (!canvasRect || !buttonsRef.current || !positioned || moveable) return

    if (vertical && left) {
      setPosition({
        x: 12,
        y: position.y
      })
    } else if (vertical) {
      setPosition({
        x: canvasRect.width - 69,
        y: position.y
      })
    } else {
      setPosition({
        x: clamp(position.x, 91, canvasRect.right - 290),
        y: position.y
      })
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canvasRect, positioned])

  // reset button positioning (sets !positioned)
  const resetButtons = () => {
    if (!canvasRect || !buttonsRef.current) return

    let width
    if (vertical) {
      width = buttonsRef.current.offsetHeight / 2
    } else {
      width = buttonsRef.current.offsetWidth / 2
    }
    setPositioned(false)

    setPosition({
      x: canvasRect.width / 2 - width - 22,
      y: 12,
    })
    setVertical(false)
    setLeft(false)
  }

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
        <div
          className="canvas-btn-wrap"
          style={{
            pointerEvents: "all",
            // transform: `translate(${position.x}px,${position.y}px)`,
            top: position.y,
            left: position.x,
            flexDirection: vertical ? "column" : "row",
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
            }}
            onDoubleClick={resetButtons}
            children={
              <HandleIcon
                className="canvas-btn-handle-icon"
                style={{
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
            />
          ))}
        </div>
      )}
    </div>
  )
}

const BUTTON_TYPES: { type: ICanvasButton["type"]; icon: JSX.Element; tooltip: string }[] = [
  { type: "undo", icon: <UndoIcon className="canvas-btn-icon" />, tooltip: "Undo" },
  { type: "reset", icon: <ResetIcon2 className="canvas-btn-icon" />, tooltip: "Reset Canvas" },
  { type: "redo", icon: <RedoIcon className="canvas-btn-icon" />, tooltip: "Redo" },
  { type: "layout", icon: <GraphIcon2 className="canvas-btn-icon"/>, tooltip: "Layout Nodes" },
  { type: "saveWorkflow", icon: <VscSave className="canvas-btn-icon" style={{width:25, height:25}}/>, tooltip: "Save Workflow" },
]
