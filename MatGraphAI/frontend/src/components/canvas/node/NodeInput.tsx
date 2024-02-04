import { Select } from "@mantine/core"
import { useEffect, useRef, useState } from "react"

import { INode, ValOpPair, Operator } from "../../../types/canvas.types"
import NodeInputStr from "./NodeInputStr"
import NodeInputStrOp from "./NodeInputStrOp"
import { useAutoIncrementRefs } from "../../../common/helpers"

interface NodeInputProps {
  isValueNode: boolean
  node: INode
  handleNodeRename: (node: INode) => void
}

export default function NodeInput(props: NodeInputProps) {
  const {
    isValueNode,
    node,
    handleNodeRename,
  } = props

  const [nodeName, setNodeName] = useState<string>(node.name.value)
  const [nodeValue, setNodeValue] = useState<ValOpPair>(node.value.value)
  const [nodeBatchNum, setNodeBatchNum] = useState<string>(node.batch_num.value)
  const [nodeRatio, setNodeRatio] = useState<ValOpPair>(node.ratio.value)
  const [nodeConcentration, setNodeConcentration] = useState<ValOpPair>(node.concentration.value)
  const [nodeUnit, setNodeUnit] = useState<string>(node.unit.value)
  const [nodeStd, setNodeStd] = useState<ValOpPair>(node.std.value)
  const [nodeError, setNodeError] = useState<ValOpPair>(node.error.value)
  const [nodeIdentfier, setNodeIdentifier] = useState<string>(node.identifier.value)

  const { getNewRef, refs } = useAutoIncrementRefs()

  const handleBlur = () => {
    setTimeout(() => {
      // Check if the active element is one of the refs
      if (refs.some(ref => document.activeElement === ref.current)) {
        return;
      }
      const updatedNode: INode = {
        ...node,
        name: {value: nodeName, index: node.name.index},
        value: {value: nodeValue, index: node.value.index},
        batch_num: {value: nodeBatchNum, index: node.batch_num.index},
        ratio: {value: nodeRatio, index: node.ratio.index},
        concentration: {value: nodeConcentration, index: node.concentration.index},
        unit: {value: nodeUnit, index: node.unit.index},
        std: {value: nodeStd, index: node.std.index},
        error: {value: nodeError, index: node.error.index},
        identifier: {value: nodeIdentfier, index: node.identifier.index}
      }
      handleNodeRename(updatedNode);
    }, 100);
  };
  
  

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      const updatedNode: INode = {
        ...node,
        name: {value: nodeName, index: node.name.index},
        value: {value: nodeValue, index: node.value.index},
        batch_num: {value: nodeBatchNum, index: node.batch_num.index},
        ratio: {value: nodeRatio, index: node.ratio.index},
        concentration: {value: nodeConcentration, index: node.concentration.index},
        unit: {value: nodeUnit, index: node.unit.index},
        std: {value: nodeStd, index: node.std.index},
        error: {value: nodeError, index: node.error.index},
        identifier: {value: nodeIdentfier, index: node.identifier.index}
      }
      handleNodeRename(updatedNode);
    }
  }

  const handleStrChangeLocal = (
    id: string,
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value

    switch (id) {
      case "name":
        setNodeName(value)
        break
      case "batch":
        setNodeBatchNum(value)
        break
      case "unit":
        setNodeUnit(value)
        break
      case "identifier":
        setNodeIdentifier(value)
        break
      default:
        break
    }
  }

  const handleValChangeLocal = (
    id: string,
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value

    switch (id) {
      case "value":
        const valOp = nodeValue.operator
        setNodeValue({ value: value, operator: valOp })
        break
      case "ratio":
        const ratOp = nodeRatio.operator
        setNodeRatio({ value: value, operator: ratOp })
        break
      case "concentration":
        const conOp = nodeConcentration.operator
        setNodeConcentration({ value: value, operator: conOp })
        break
      case "std":
        const stdOp = nodeStd.operator
        setNodeStd({ value: value, operator: stdOp })
        break
      case "error":
        const errOp = nodeError.operator
        setNodeError({ value: value, operator: errOp })
        break
      default:
        break
    }
  }

  const handleOpChangeLocal = (id: string, operator: string) => {
    switch (id) {
      case "value":
        const val = nodeValue.value
        setNodeValue({ value: val, operator: operator })
        break
      case "ratio":
        const rat = nodeRatio.value
        setNodeRatio({ value: rat, operator: operator })
        break
      case "concentration":
        const con = nodeConcentration.value
        setNodeConcentration({ value: con, operator: operator })
        break
      case "std":
        const std = nodeStd.value
        setNodeStd({ value: std, operator: operator })
        break
      case "error":
        const err = nodeError.value
        setNodeError({ value: err, operator: operator })
        break
      default:
        break
    }
  }

  /**
   *
   * Matter: Id, Name (str), Batch (str), Ratio (strop), Concentration (strop)
   *
   * Property/Parameter: Id, Name (str), Value (strop), Unit (str), Std (strop), Error (strop)
   *
   * Manuf, Measure, Meta: Id, Name (str)
   *
   */

  return (
    <div
      className="node-input"
      onClick={(e) => e.stopPropagation()}
      onMouseUp={(e) => e.stopPropagation()}
      style={{
        display: "flex",
        flexDirection: "column",
        borderRadius: 3,
        backgroundColor: "#1a1b1e",
        zIndex: node.layer + 1,
      }}
    >
      <NodeInputStr
        handleChange={handleStrChangeLocal}
        handleKeyUp={handleKeyUp}
        handleBlur={handleBlur}
        id="name"
        reference={getNewRef()}
        defaultValue={nodeName}
        autoFocus={true}
        add={false}
        zIndex={node.layer + 4}
      />

      {["manufacturing", "measurement", "metadata"].includes(node.type) && (
        <NodeInputStr
          handleChange={handleStrChangeLocal}
          handleKeyUp={handleKeyUp}
          handleBlur={handleBlur}
          id="identifier"
          reference={getNewRef()}
          defaultValue={nodeIdentfier}
          autoFocus={false}
          add={true}
          zIndex={node.layer + 3}
        />
      )}

      {node.type === "matter" && (
        <>
          <NodeInputStr
            handleChange={handleStrChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            id="identifier"
            reference={getNewRef()}
            defaultValue={nodeIdentfier}
            autoFocus={false}
            add={true}
            zIndex={node.layer + 3}
          />
          <NodeInputStr
            handleChange={handleStrChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            id="batch"
            reference={getNewRef()}
            defaultValue={nodeBatchNum}
            autoFocus={false}
            add={true}
            zIndex={node.layer + 3}
          />
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            id="ratio"
            opReference={getNewRef()}
            valReference={getNewRef()}
            defaultOp={nodeRatio.operator}
            defaultVal={nodeRatio.value}
            autoFocus={false}
            zIndex={node.layer + 2}
          />
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            id="concentration"
            opReference={getNewRef()}
            valReference={getNewRef()}
            defaultOp={nodeConcentration.operator}
            defaultVal={nodeConcentration.value}
            autoFocus={false}
            zIndex={node.layer + 1}
          />
        </>
      )}

      {["parameter", "property"].includes(node.type) && (
        <>
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            id="value"
            opReference={getNewRef()}
            valReference={getNewRef()}
            defaultOp={nodeValue.operator}
            defaultVal={nodeValue.value}
            autoFocus={(node.name.value !== '' && isValueNode && node.value.value.value === '')}
            zIndex={node.layer + 3}
          />
          <NodeInputStr
            handleChange={handleStrChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            id="unit"
            reference={getNewRef()}
            defaultValue={nodeUnit}
            autoFocus={false}
            add={true}
            zIndex={node.layer + 2}
          />
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            id="std"
            opReference={getNewRef()}
            valReference={getNewRef()}
            defaultOp={nodeStd.operator}
            defaultVal={nodeStd.value}
            autoFocus={false}
            zIndex={node.layer + 2}
          />
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            id="error"
            opReference={getNewRef()}
            valReference={getNewRef()}
            defaultOp={nodeError.operator}
            defaultVal={nodeError.value}
            autoFocus={false}
            zIndex={node.layer + 1}
          />
        </>
      )}
    </div>
  )
}
