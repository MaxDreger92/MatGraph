import { useEffect, useRef } from "react"

interface CanvasGridProps {
  canvasRect: DOMRect
}

export default function CanvasGrid(props: CanvasGridProps) {
  const {
    canvasRect
  } = props

  const canvasRef = useRef<HTMLCanvasElement>(null)

  const drawGrid = (ctx: CanvasRenderingContext2D) => {
    ctx.clearRect(0,0,canvasRect.width, canvasRect.height)

    const lineColor = "#ff0000"
    ctx.strokeStyle = lineColor

    const step = 10

    for (let x = 0; x <= canvasRect.width; x += step) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, canvasRect.height)
      ctx.stroke()
    }

    for (let y = 0; y <= canvasRect.height; y += step) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvasRect.width, y);
      ctx.stroke();
    }



  }

  useEffect(() => {
    const canvas = canvasRef.current
    const context = canvas?.getContext('2d')
    if (context) {
      drawGrid(context)
    }
  }, [canvasRect])

  return <canvas ref={canvasRef} width={canvasRect.width} height={canvasRect.height} />

  
}