import { useState, useEffect } from "react"

import { IConnection, Position } from "../../../types/canvas.types"
import ConnectionContext from "./ConnectionContext"

interface ConnectionProps {
  connection: IConnection
  isSelected: boolean
  handleConnectionAction: (connectionID: IConnection["id"], action: string) => void
}

interface TempConnectionProps {
  startPosition: { x: number; y: number }
  endPosition: { x: number; y: number } | null
  canvasRect: DOMRect | null
}

// Temporary connection from connection start node to
// mouse cursor or the canvas nav menu onMouseUp.
// Extinguished on completion of node connection
export function TempConnection(props: TempConnectionProps) {
  const { startPosition, endPosition, canvasRect } = props
  const [end, setEnd] = useState({ x: startPosition.x, y: startPosition.y })

  useEffect(() => {
    if (endPosition) {
      setEnd(endPosition)
      return
    }
    const moveHandler = (e: MouseEvent) => {
      if (!canvasRect) return
      const x = e.clientX - canvasRect.left
      const y = e.clientY - canvasRect.top
      setEnd({ x, y })
    }

    document.addEventListener("mousemove", moveHandler)
    return () => {
      document.removeEventListener("mousemove", moveHandler)
    }
  }, [endPosition, canvasRect])

  return (
    <svg
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
      }}
    >
      <defs>
        <marker
          id="arrow"
          viewBox="0 0 10 10"
          refX="9"
          refY="5"
          fill="#555"
          markerWidth="8"
          markerHeight="8"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" />
        </marker>
      </defs>
      <path // temporary connection path
        d={`M ${startPosition.x},${startPosition.y} L ${end.x},${end.y}`}
        stroke="#555"
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrow)"
        pointerEvents="none"
      />
    </svg>
  )
}

export default function Connection(props: ConnectionProps) {
  const { connection, isSelected, handleConnectionAction } = props
  const [start, setStart] = useState<Position>({x: 0, y: 0})
  const [end, setEnd] = useState<Position>({x: 0, y: 0})
  const [mid, setMid] = useState<Position>({x: 0, y: 0})

  const handleClickLocal = (e: React.MouseEvent) => {
    e.stopPropagation()
    handleConnectionAction(connection.id, "click")
  }

  const handleConnectionActionLocal = (action: string) => {
    handleConnectionAction(connection.id, action)
  }

  useEffect(() => {
    const start = connection.start
    const end = connection.end
  
    const dx = end.position.x - start.position.x
    const dy = end.position.y - start.position.y
    const len = Math.sqrt(dx * dx + dy * dy)
    const normX = dx / len
    const normY = dy / len
  
    const startX = start.position.x + normX * (start.size / 2 + 4)
    const startY = start.position.y + normY * (start.size / 2 + 4)
    const endX = end.position.x - normX * (end.size / 2 + 6)
    const endY = end.position.y - normY * (end.size / 2 + 6)

    setStart({x: startX, y: startY})
    setEnd({x: endX, y: endY})
  
    // calc connectionPos for placement of connection ctxt menu
    // should be exactly half way between both node borders
    const connectionPos = {
      x: (startX + endX + normX * 2) / 2,
      y: (startY + endY + normY * 2) / 2,
    }
    setMid(connectionPos)
  }, [connection])
  

  return (
    <div>
      <svg
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          pointerEvents: "none",
        }}
      >
        <defs>
          {/* Bigger arrowhead for selection path
          (outline to actual connection path) */}
          <marker
            id="arrowSelect"
            viewBox="0 0 10 10"
            refX="7"
            refY="5"
            fill="#6f6f6f"
            markerWidth="4"
            markerHeight="8"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" />
          </marker>
          {/* Arrowhead for actual connection path */}
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            fill="#555"
            markerWidth="8"
            markerHeight="8"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" />
          </marker>
        </defs>
        {isSelected && (
            <path // connection outline on selection
              d={`M ${start.x},${start.y} L ${end.x},${end.y}`}
              stroke="#6f6f6f"
              strokeWidth="6"
              fill="none"
              markerEnd="url(#arrowSelect)"
              pointerEvents="none"
            />
        )}
        <path // actual connection (always visible)
          // d={`M ${isLayouting ? springProps.startX : start.x},${isLayouting ? springProps.startY : start.y} L ${isLayouting ? springProps.endX : end.x},${isLayouting ? springProps.endY : end.y}`}
          d={`M ${start.x},${start.y} L ${end.x},${end.y}`}
          stroke="#555"
          strokeWidth="2"
          fill="none"
          markerEnd="url(#arrow)"
          pointerEvents="none"
        />
        <path // connection clickable area (for better ux)
          d={`M ${start.x},${start.y} L ${end.x},${end.y}`}
          fill="none"
          strokeWidth="20"
          stroke="transparent"
          pointerEvents="auto"
          onClick={handleClickLocal}
        />
      </svg>
      {isSelected && ( // Connection context menu
        <div style={{position: "relative", left: mid.x, top: mid.y}}>
          <ConnectionContext
            onSelect={handleConnectionActionLocal}
            isOpen={isSelected}
          />
        </div>
      )}
    </div>
  )
}