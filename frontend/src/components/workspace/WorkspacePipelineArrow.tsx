interface WorkspacePipelineArrowProps {
  length: number
}

export default function WorkspacePipelineArrow(
  props: WorkspacePipelineArrowProps
) {
  const { length } = props

  return (
    
    <div
      style={{
        width: length,
      }}
    >
      <svg
        style={{
          position: "relative",
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
        <path
          d={`M ${15},${40} L ${length},${40}`}
          stroke="#555"
          strokeWidth="2"
          fill="none"
          markerEnd="url(#arrow)"
          pointerEvents="none"
        />
      </svg>
    </div>
  )
}
