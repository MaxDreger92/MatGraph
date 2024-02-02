import { Position } from "../../../types/canvas.types"

interface NodeConnectorProps {
  nodeSize: number
  color: string
  active: boolean,
  position: Position
  layer: number
}

export default function NodeConnector(props: NodeConnectorProps) {
  const {
    nodeSize,
    color,
    active,
    position,
    layer,
  } = props

  return (
    <>
      <div
        // className="node-rail"
        style={{
          width: nodeSize + 2,
          height: nodeSize + 2,
        }}
      />
      <div
        className="node-connector"
        style={{
          border: `1px solid ${color}`,
          backgroundColor: active
            ? color
            : "transparent",
          top: position.y,
          left: position.x,
          pointerEvents: "none",
          zIndex: layer + 1,
        }}
      />
    </>
  )
}