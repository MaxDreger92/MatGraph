import { useState, useEffect } from "react"
import { useMantineColorScheme } from "@mantine/core"

import { IRelationship, Position } from "../../../types/canvas.types"
import RelationshipContext from "./RelationshipContext"

interface RelationshipProps {
  relationship: IRelationship
  isSelected: boolean
  handleRelationshipAction: (relationshipID: IRelationship["id"], action: string) => void
}

interface TempRelationshipProps {
  startPosition: { x: number; y: number }
  endPosition: { x: number; y: number } | null
  canvasRect: DOMRect | null
}

// Temporary relationship from relationship start node to
// mouse cursor or the canvas nav menu onMouseUp.
// Extinguished on completion of node relationship
export function TempRelationship(props: TempRelationshipProps) {
  const { startPosition, endPosition, canvasRect } = props
  const [end, setEnd] = useState({ x: startPosition.x, y: startPosition.y })

  useEffect(() => {
    if (endPosition) {
      setEnd(endPosition)
      return
    }
    const moveHandler = (e: MouseEvent) => {
      if (!canvasRect) return
      const x = e.clientX
      const y = e.clientY - canvasRect.top
      setEnd({ x, y })
    }

    document.addEventListener("mousemove", moveHandler)
    return () => {
      document.removeEventListener("mousemove", moveHandler)
    }
  }, [endPosition, canvasRect])

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'

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
          fill={darkTheme ? "#555" : "#868e96"}
          markerWidth="8"
          markerHeight="8"
          orient="auto-start-reverse"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" />
        </marker>
      </defs>
      <path // temporary relationship path
        d={`M ${startPosition.x},${startPosition.y} L ${end.x},${end.y}`}
        stroke={darkTheme ? "#555" : "#868e96"}
        strokeWidth="2"
        fill="none"
        markerEnd="url(#arrow)"
        pointerEvents="none"
      />
    </svg>
  )
}

export default function Relationship(props: RelationshipProps) {
  const { relationship, isSelected, handleRelationshipAction } = props
  const [start, setStart] = useState<Position>({x: 0, y: 0})
  const [end, setEnd] = useState<Position>({x: 0, y: 0})
  const [mid, setMid] = useState<Position>({x: 0, y: 0})

  const handleClickLocal = (e: React.MouseEvent) => {
    e.stopPropagation()
    handleRelationshipAction(relationship.id, "click")
  }

  const handleRelationshipActionLocal = (action: string) => {
    handleRelationshipAction(relationship.id, action)
  }

  useEffect(() => {
    const start = relationship.start
    const end = relationship.end
  
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
  
    // calc relationshipPos for placement of relationship ctxt menu
    // should be exactly half way between both node borders
    const relationshipPos = {
      x: (startX + endX + normX * 2) / 2,
      y: (startY + endY + normY * 2) / 2,
    }
    setMid(relationshipPos)
  }, [relationship])

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'

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
          (outline to actual relationship path) */}
          <marker
            id="arrowSelect"
            viewBox="0 0 10 10"
            refX="7"
            refY="5"
            fill={darkTheme ? "#6f6f6f" : "#e9ecef"}
            markerWidth="4"
            markerHeight="8"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" />
          </marker>
          {/* Arrowhead for actual relationship path */}
          <marker
            id="arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            fill={darkTheme ? "#555" : "#222"}
            markerWidth="8"
            markerHeight="8"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" />
          </marker>
        </defs>
        {isSelected && (
            <path // relationship outline on selection
              d={`M ${start.x},${start.y} L ${end.x},${end.y}`}
              stroke={darkTheme ? "#6f6f6f" : "#e9ecef"}
              strokeWidth="6"
              fill="none"
              markerEnd="url(#arrowSelect)"
              pointerEvents="none"
            />
        )}
        <path // actual relationship (always visible)
          // d={`M ${isLayouting ? springProps.startX : start.x},${isLayouting ? springProps.startY : start.y} L ${isLayouting ? springProps.endX : end.x},${isLayouting ? springProps.endY : end.y}`}
          d={`M ${start.x},${start.y} L ${end.x},${end.y}`}
          stroke={darkTheme ? "#555" : "#222"}
          strokeWidth="2"
          fill="none"
          markerEnd="url(#arrow)"
          pointerEvents="none"
        />
        <path // relationship clickable area (for better ux)
          d={`M ${start.x},${start.y} L ${end.x},${end.y}`}
          fill="none"
          strokeWidth="20"
          stroke="transparent"
          pointerEvents="auto"
          onClick={handleClickLocal}
        />
      </svg>
      {isSelected && ( // relationship context menu
        <div style={{position: "relative", left: mid.x, top: mid.y}}>
          <RelationshipContext
            onSelect={handleRelationshipActionLocal}
            isOpen={isSelected}
            darkTheme={darkTheme}
          />
        </div>
      )}
    </div>
  )
}