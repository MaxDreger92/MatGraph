import { useSpring, animated } from "react-spring";

import WarningIcon from "@mui/icons-material/Warning"

interface NodeWarningProps {
  size: number,
  hovered: boolean,
  color: string,
  layer: number,
}

export default function NodeWarning(props: NodeWarningProps) {
  const {
    size,
    hovered,
    color,
    layer
  } = props

  const iconAnimProps = useSpring({
    color: hovered ? "#E15554" : color,
    config: {
      tension: hovered ? 170 : 150,
      friction: hovered ? 26 : 170,
    },
  })

  return (
    <div
      className="node-warning"
      style={{
        left: size / 2 + 10,
        top: size / 2 + 10,
        pointerEvents: "none",
      }}
    >
      <animated.div style={iconAnimProps}>
        <WarningIcon
          style={{
            position: "relative",
            fontSize: "30px",
            transform: `translate(
                ${hovered ? -58 : 0}px,
                ${hovered ? -1 : -4}px
              )`,
            transition: "transform 0.1s ease-in-out",
            zIndex: layer + 1,
          }}
        />
      </animated.div>
      {hovered && (
        <div className="node-warning-label">Fields missing!</div>
      )}
    </div>
  )
}