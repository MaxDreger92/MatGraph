import { useState, CSSProperties, useEffect } from "react"
import { TbMinusVertical, TbMinus } from "react-icons/tb"
import {
  FiChevronLeft,
  FiChevronRight,
  FiChevronDown,
  FiChevronUp,
} from "react-icons/fi"
import { useSpring, animated } from "react-spring"

interface WorkflowButtonProps {
  uploadMode: boolean
  jsonView: boolean
  jsonViewWidth: number
  historyView: boolean
  historyViewWidth: number
  tableView: boolean
  tableViewHeight: number
  onSelect: (view: string) => void
}

export default function WorkflowButtons(props: WorkflowButtonProps) {
  const {
    uploadMode,
    jsonView,
    jsonViewWidth,
    historyView,
    historyViewWidth,
    tableView,
    tableViewHeight,
    onSelect,
  } = props
  const [hovered, setHovered] = useState("none")

  useEffect(() => {
    setHovered("none")
  }, [jsonView, historyView, tableView])

  const springProps = useSpring({
    jsonIconRight: jsonView ? jsonViewWidth : 0,
    historyIconLeft: historyView ? historyViewWidth : 0,
    tableIconBottom: tableView ? tableViewHeight : 0,
    config: {
      tension: 1000,
      friction: 100,
    },
  })

  const iconTopValue = springProps.tableIconBottom.to(
    (value) => `calc(0.49 * (100% - ${value}px))`
  )

  const iconStyle: CSSProperties = {
    pointerEvents: "all",
    position: "absolute",
    width: "35px",
    height: "auto",
  }

  const handleMouseLeave = () => {
    setHovered("null")
  }

  const handleMouseUpLocal = (e: React.MouseEvent) => {
    if (e.button === 2) return
    onSelect(hovered)
  }

  const renderJsonIcon = () => {
    return (
      <animated.div
        className="workflow-btn"
        style={{
          top: iconTopValue,
          right: springProps.jsonIconRight,
        }}
      >
        {hovered === "json" ? (
          jsonView ? (
            <FiChevronRight
              style={{
                ...iconStyle,
                color: hovered === "json" ? "#909296" : "#373A40",
              }}
              onClick={handleMouseUpLocal}
              onMouseEnter={() => setHovered("json")}
              onMouseLeave={handleMouseLeave}
            />
          ) : (
            <FiChevronLeft
              style={{
                ...iconStyle,
                color: hovered === "json" ? "#909296" : "#373A40",
              }}
              onClick={handleMouseUpLocal}
              onMouseEnter={() => setHovered("json")}
              onMouseLeave={handleMouseLeave}
            />
          )
        ) : (
          <TbMinusVertical
            style={{
              ...iconStyle,
              color: hovered === "json" ? "#909296" : "#373A40",
            }}
            onClick={handleMouseUpLocal}
            onMouseEnter={() => setHovered("json")}
            onMouseLeave={handleMouseLeave}
          />
        )}
      </animated.div>
    )
  }

  const renderHistoryIcon = () => {
    return (
      <animated.div
        className="workflow-btn"
        style={{
          left: springProps.historyIconLeft,
          top: iconTopValue,
        }}
      >
        {hovered === "history" ? (
          historyView ? (
            <FiChevronLeft
              style={{
                ...iconStyle,
                color: hovered === "history" ? "#909296" : "#373A40",
              }}
              onClick={handleMouseUpLocal}
              onMouseEnter={() => setHovered("history")}
              onMouseLeave={handleMouseLeave}
            />
          ) : (
            <FiChevronRight
              style={{
                ...iconStyle,
                color: hovered === "history" ? "#909296" : "#373A40",
              }}
              onClick={handleMouseUpLocal}
              onMouseEnter={() => setHovered("history")}
              onMouseLeave={handleMouseLeave}
            />
          )
        ) : (
          <TbMinusVertical
            style={{
              ...iconStyle,
              color: hovered === "history" ? "#909296" : "#373A40",
            }}
            onClick={handleMouseUpLocal}
            onMouseEnter={() => setHovered("history")}
            onMouseLeave={handleMouseLeave}
          />
        )}
      </animated.div>
    )
  }

  const renderTableIcon = () => {
    return (
      <animated.div
        className="workflow-btn"
        style={{
          bottom: springProps.tableIconBottom,
          left: "50%",
          transform: "translate(-50%,0)",
        }}
      >
        {hovered === "table" ? (
          tableView ? (
            <FiChevronDown
              style={{
                ...iconStyle,
                color: hovered === "table" ? "#909296" : "#373A40",
              }}
              onClick={handleMouseUpLocal}
              onMouseEnter={() => setHovered("table")}
              onMouseLeave={handleMouseLeave}
            />
          ) : (
            <FiChevronUp
              style={{
                ...iconStyle,
                color: hovered === "table" ? "#909296" : "#373A40",
              }}
              onClick={handleMouseUpLocal}
              onMouseEnter={() => setHovered("table")}
              onMouseLeave={handleMouseLeave}
            />
          )
        ) : (
          <TbMinus
            style={{
              ...iconStyle,
              color: hovered === "table" ? "#909296" : "#373A40",
            }}
            onClick={handleMouseUpLocal}
            onMouseEnter={() => setHovered("table")}
            onMouseLeave={handleMouseLeave}
          />
        )}
      </animated.div>
    )
  }

  return (
    <>
      {renderHistoryIcon()}
      {renderJsonIcon()}
      {uploadMode && renderTableIcon()}
    </>
  )
}
