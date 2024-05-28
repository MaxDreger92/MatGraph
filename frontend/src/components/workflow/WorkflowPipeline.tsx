import { Button } from "@mantine/core"
import WorkflowPipelineArrow from "./WorkflowPipelineArrow"
import { useEffect, useRef, useState } from "react"
import { RxCross2 } from "react-icons/rx";

interface WorkflowPipelineProps {
  handlePipelineReset: () => void
  handleContextChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  loadNodes: () => void
  requestExtractLabels: () => Promise<void>
  requestExtractAttributes: () => Promise<void>
  requestExtractNodes: () => Promise<void>
  requestExtractGraph: () => Promise<void>
  requestImportGraph: () => Promise<void>
  progress: number,
  darkTheme: boolean
}

export default function WorkflowPipeline(props: WorkflowPipelineProps) {
  const {
    handlePipelineReset,
    handleContextChange,
    requestExtractLabels,
    requestExtractAttributes,
    requestExtractNodes,
    requestExtractGraph,
    requestImportGraph,
    progress,
    darkTheme,
  } = props
  const workflowPipelineRef = useRef<HTMLDivElement>(null)
  const [pipelineRect, setPipelineRect] = useState<DOMRect | null>(null)
  const [spaceBetween, setSpaceBetween] = useState(0)
  const [buttonWidth, setButtonWidth] = useState(155)
  const [cancelHovered, setCancelHovered] = useState(false)

  useEffect(() => {
    const resizeObserver = new ResizeObserver(() => {
      if (workflowPipelineRef.current) {
        setPipelineRect(workflowPipelineRef.current.getBoundingClientRect())
      }
    })

    const currentCanvas = workflowPipelineRef.current
    if (currentCanvas) {
      resizeObserver.observe(currentCanvas)
    }

    return () => {
      if (currentCanvas) {
        resizeObserver.unobserve(currentCanvas)
      }
    }
  }, [workflowPipelineRef])

  // calculate space between
  useEffect(() => {
    if (!pipelineRect) {
      setSpaceBetween(200)
      setButtonWidth(155)
    } else {
      const availableWidth = pipelineRect.width - 250 - 90 - 40
      if (availableWidth > 935) {
        setButtonWidth(155)
        setSpaceBetween((availableWidth - 775) / 4)
      } else {
        setButtonWidth((availableWidth - 200) / 5)
        setSpaceBetween(50)
      }
    }
  }, [pipelineRect])

  const inputClass = darkTheme ? "input-dark-2" : "input-light-2"

  return (
    <div
      ref={workflowPipelineRef}
      className="workflow-pipeline"
      style={{
        width: "100%",
        height: 80,
        display: "flex",
        flexDirection: "row",
      }}
    >
      {/* Cancel */}
      <RxCross2
        onClick={handlePipelineReset}
        onMouseEnter={() => setCancelHovered(true)}
        onMouseLeave={() => setCancelHovered(false)}
        style={{
          alignSelf: "center",
          justifySelf: "center",
          width: 30,
          height: 30,
          marginLeft: 10,
          color: cancelHovered ? "red" : "inherit",
          cursor: "pointer"
        }}
      />

      {/* Step 1 - Upload CSV -> Request label extraction */}
      <div
        style={{
          display: "flex",
          flexDirection: "row",
        }}
      >
        {/* Context label and input field */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            width: 250,
            paddingLeft: 25,
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <input
            className={`${inputClass}`}
            type="text"
            id="contextInput"
            placeholder={"Enter table context..."}
            defaultValue={undefined}
            onChange={handleContextChange} // write nodeName state
            autoFocus={true}
            style={{
              alignSelf: "center",
              justifySelf: "center",
            }}
          />
        </div>
        <Button
          type="submit"
          radius="xl"
          style={{
            alignSelf: "center",
            marginLeft: 15,
            marginBottom: 1,
            width: buttonWidth,
            height: 40,
            padding: 0,
          }}
          onClick={requestExtractLabels}
          disabled={progress !== 1}
        >
          {buttonWidth < 100 ? "1" : "Extract Labels"}
        </Button>
      </div>

      {/* Arrow */}
      <WorkflowPipelineArrow length={spaceBetween}/>

      {/* Step 2 - View extracted labels -> Request attribute extraction  */}
      <div
        style={{
          display: "flex",
        }}
      >
        <Button
          type="submit"
          radius="xl"
          style={{
            alignSelf: "center",
            marginLeft: 15,
            marginBottom: 1,
            width: buttonWidth,
            height: 40,
            padding: 0,
          }}
          onClick={requestExtractAttributes}
          disabled={progress !== 2}
        >
          {buttonWidth < 120 ? buttonWidth < 100 ? "2" : "Ext. Attributes" : "Extract Attributes"}
        </Button>
      </div>

      {/* Arrow */}
      <WorkflowPipelineArrow length={spaceBetween}/>

      {/* Step 3 - View extracted attributes -> Request node extraction */}
      <div
        style={{
          display: "flex",
        }}
      >
        <Button
          type="submit"
          radius="xl"
          style={{
            alignSelf: "center",
            marginLeft: 15,
            marginBottom: 1,
            width: buttonWidth,
            height: 40,
            padding: 0,
          }}
          onClick={requestExtractNodes}
          disabled={progress !== 3} // 134
        >
          {buttonWidth < 100 ? "3" : "Extract Nodes"}
        </Button>
      </div>

      {/* Arrow */}
      <WorkflowPipelineArrow length={spaceBetween}/>

      {/* Step 4 - View extracted nodes (in canvas) -> Request graph extraction */}
      <div
        style={{
          display: "flex",
        }}
      >
        <Button
          type="submit"
          radius="xl"
          style={{
            alignSelf: "center",
            marginLeft: 15,
            marginBottom: 1,
            width: buttonWidth,
            height: 40,
            padding: 0,
          }}
          onClick={requestExtractGraph}
          disabled={progress !== 4} // 130
        >
          {buttonWidth < 100 ? "4" : "Extract Graph"}
        </Button>
      </div>

      {/* Arrow */}
      <WorkflowPipelineArrow length={spaceBetween}/>

      {/* Step 5 - View extracted graph (in canvas) -> Request import of graph to database */}
      <div
        style={{
          display: "flex",
        }}
      >
        <Button
          type="submit"
          radius="xl"
          style={{
            alignSelf: "center",
            marginLeft: 15,
            marginBottom: 1,
            width: buttonWidth,
            height: 40,
            padding: 0,
          }}
          onClick={requestImportGraph}
          disabled={progress !== 5}
        >
          {buttonWidth < 120 ? buttonWidth < 100 ? "5" : "Save" : "Save to database"}
        </Button>
      </div>
    </div>
  )
}
