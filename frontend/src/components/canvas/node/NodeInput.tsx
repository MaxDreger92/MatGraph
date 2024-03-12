import { Select, useMantineColorScheme } from "@mantine/core"
import React, { useEffect, useRef, useState } from "react"

import {
  INode,
  ValOpPair,
  Operator,
  NodeAttribute,
  NodeValOpAttribute,
  AttributeIndex,
} from "../../../types/canvas.types"
import NodeInputStr from "./NodeInputStr"
import NodeInputStrOp from "./NodeInputStrOp"
import { useAutoIncrementInputRefs } from "../../../common/helpers"

interface NodeInputProps {
  isValueNode: boolean
  node: INode
  handleNodeRename: (node: INode) => void
}

export default React.memo(function NodeInput(props: NodeInputProps) {
  const { isValueNode, node, handleNodeRename } = props

  const [nodeName, setNodeName] = useState<NodeAttribute>(node.name)
  const [nodeValue, setNodeValue] = useState<NodeValOpAttribute>(node.value)
  const [nodeBatchNum, setNodeBatchNum] = useState<NodeAttribute>(
    node.batch_num
  )
  const [nodeRatio, setNodeRatio] = useState<NodeValOpAttribute>(node.ratio)
  const [nodeConcentration, setNodeConcentration] =
    useState<NodeValOpAttribute>(node.concentration)
  const [nodeUnit, setNodeUnit] = useState<NodeAttribute>(node.unit)
  const [nodeStd, setNodeStd] = useState<NodeValOpAttribute>(node.std)
  const [nodeError, setNodeError] = useState<NodeValOpAttribute>(node.error)
  const [nodeIdentifier, setNodeIdentifier] = useState<NodeAttribute>(
    node.identifier
  )

  const { getNewRef, refs } = useAutoIncrementInputRefs()

  const handleBlur = () => {
    setTimeout(() => {
      // Check if the active element is one of the refs
      if (refs.some((ref) => document.activeElement === ref.current)) {
        return
      }
      const updatedNode: INode = {
        ...node,
        name: nodeName,
        value: nodeValue,
        batch_num: nodeBatchNum,
        ratio: nodeRatio,
        concentration: nodeConcentration,
        unit: nodeUnit,
        std: nodeStd,
        error: nodeError,
        identifier: nodeIdentifier,
      }
      handleNodeRename(updatedNode)
    }, 100)
  }

  const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault()
      const updatedNode: INode = {
        ...node,
        name: nodeName,
        value: nodeValue,
        batch_num: nodeBatchNum,
        ratio: nodeRatio,
        concentration: nodeConcentration,
        unit: nodeUnit,
        std: nodeStd,
        error: nodeError,
        identifier: nodeIdentifier,
      }
      handleNodeRename(updatedNode)
    }
  }

  const handleStrChangeLocal = (
    id: string,
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const input_value = e.target.value

    switch (id) {
      case "name":
        setNodeName({ value: input_value, index: nodeName.index })
        break
      case "batch":
        setNodeBatchNum({ value: input_value, index: nodeBatchNum.index })
        break
      case "unit":
        setNodeUnit({ value: input_value, index: nodeUnit.index })
        break
      case "identifier":
        setNodeIdentifier({ value: input_value, index: nodeIdentifier.index })
        break
      default:
        break
    }
  }

  const handleValChangeLocal = (
    id: string,
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const input_value = e.target.value

    switch (id) {
      case "value":
        setNodeValue({valOp: {value: input_value, operator: nodeValue.valOp.operator}, index: nodeValue.index})
        break
      case "ratio":
        setNodeRatio({valOp: {value: input_value, operator: nodeRatio.valOp.operator}, index: nodeRatio.index})
        break
      case "concentration":
        setNodeConcentration({valOp: {value: input_value, operator: nodeConcentration.valOp.operator}, index: nodeConcentration.index})
        break
      case "std":
        setNodeStd({valOp: {value: input_value, operator: nodeStd.valOp.operator}, index: nodeStd.index})
        break
      case "error":
        setNodeError({valOp: {value: input_value, operator: nodeError.valOp.operator}, index: nodeError.index})
        break
      default:
        break
    }
  }

  const handleOpChangeLocal = (id: string, operator: string) => {
    switch (id) {
      case "value":
        setNodeValue({valOp: {value: nodeValue.valOp.value, operator: operator}, index: nodeValue.index})
        break
      case "ratio":
        setNodeRatio({valOp: {value: nodeRatio.valOp.value, operator: operator}, index: nodeRatio.index})
        break
      case "concentration":
        setNodeConcentration({valOp: {value: nodeConcentration.valOp.value, operator: operator}, index: nodeConcentration.index})
        break
      case "std":
        setNodeStd({valOp: {value: nodeStd.valOp.value, operator: operator}, index: nodeStd.index})
        break
      case "error":
        setNodeError({valOp: {value: nodeError.valOp.value, operator: operator}, index: nodeError.index})
        break
      default:
        break
    }
  }

  const handleIndexChangeLocal = (id: string, e: React.ChangeEvent<HTMLInputElement>) => {
    const input_string = e.target.value

    let input_value: string | number

    const numericValue = parseFloat(input_string)
    input_value = isNaN(numericValue) ? input_string : numericValue

    switch (id) {
      case "name":
        setNodeName({value: nodeName.value, index: input_value})
        break
      case "value":
        setNodeValue({valOp: {value: nodeValue.valOp.value, operator: nodeValue.valOp.operator}, index: input_value})
        break
      case "batch":
        setNodeBatchNum({value: nodeBatchNum.value, index: input_value})
        break
      case "ratio":
        setNodeRatio({valOp: {value: nodeRatio.valOp.value, operator: nodeRatio.valOp.operator}, index: input_value})
        break
      case "concentration":
        setNodeConcentration({valOp: {value: nodeConcentration.valOp.value, operator: nodeConcentration.valOp.operator}, index: input_value})
        break
      case "unit":
        setNodeUnit({value: nodeUnit.value, index: input_value})
        break
      case "std":
        setNodeStd({valOp: {value: nodeStd.valOp.value, operator: nodeStd.valOp.operator}, index: input_value})
        break
      case "error":
        setNodeError({valOp: {value: nodeError.valOp.value, operator: nodeError.valOp.operator}, index: input_value})
        break
      case "identifier":
        setNodeIdentifier({value: nodeIdentifier.value, index: input_value})
        break
      default:
        break
    }
  }

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'

  /**
   *
   * Matter: Identifier, Name (str), Batch (str), Ratio (strop), Concentration (strop)
   *
   * Property/Parameter: Name (str), Value (strop), Unit (str), Std (strop), Error (strop)
   *
   * Manuf, Measure, Meta: Identifier, Name (str)
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
        backgroundColor: darkTheme ? "#1a1b1e" : "#f8f9fa",
        zIndex: node.layer + 1,
      }}
    >
      <NodeInputStr
        handleStrChange={handleStrChangeLocal}
        handleIndexChange={handleIndexChangeLocal}
        handleKeyUp={handleKeyUp}
        handleBlur={handleBlur}
        getNewRef={getNewRef}
        id="name"
        defaultValue={nodeName.value}
        showIndices={node.with_indices}
        index={node.name.index}
        autoFocus={true}
        add={false}
        zIndex={node.layer + 4}
      />

      {["manufacturing", "measurement", "metadata"].includes(node.type) && (
        <NodeInputStr
          handleStrChange={handleStrChangeLocal}
          handleIndexChange={handleIndexChangeLocal}
          handleKeyUp={handleKeyUp}
          handleBlur={handleBlur}
          getNewRef={getNewRef}
          id="identifier"
          defaultValue={nodeIdentifier.value}
          showIndices={node.with_indices}
          index={node.identifier.index}
          autoFocus={false}
          add={true}
          zIndex={node.layer + 3}
        />
      )}

      {node.type === "matter" && (
        <>
          <NodeInputStr
            handleStrChange={handleStrChangeLocal}
            handleIndexChange={handleIndexChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            getNewRef={getNewRef}
            id="identifier"
            defaultValue={nodeIdentifier.value}
            showIndices={node.with_indices}
            index={nodeIdentifier.index}
            autoFocus={false}
            add={true}
            zIndex={node.layer + 3}
          />
          <NodeInputStr
            handleStrChange={handleStrChangeLocal}
            handleIndexChange={handleIndexChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            getNewRef={getNewRef}
            id="batch"
            defaultValue={nodeBatchNum.value}
            showIndices={node.with_indices}
            index={nodeBatchNum.index}
            autoFocus={false}
            add={true}
            zIndex={node.layer + 3}
          />
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleIndexChange={handleIndexChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            getNewRef={getNewRef}
            id="ratio"
            defaultOp={nodeRatio.valOp.operator}
            defaultVal={nodeRatio.valOp.value}
            showIndices={node.with_indices}
            index={nodeRatio.index}
            autoFocus={false}
            zIndex={node.layer + 2}
          />
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleIndexChange={handleIndexChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            getNewRef={getNewRef}
            id="concentration"
            defaultOp={nodeConcentration.valOp.operator}
            defaultVal={nodeConcentration.valOp.value}
            showIndices={node.with_indices}
            index={nodeConcentration.index}
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
            handleIndexChange={handleIndexChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            getNewRef={getNewRef}
            id="value"
            defaultOp={nodeValue.valOp.operator}
            defaultVal={nodeValue.valOp.value}
            showIndices={node.with_indices}
            index={nodeValue.index}
            autoFocus={
              node.name.value !== "" &&
              isValueNode &&
              node.value.valOp.value === ""
            }
            zIndex={node.layer + 3}
          />
          <NodeInputStr
            handleStrChange={handleStrChangeLocal}
            handleIndexChange={handleIndexChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            getNewRef={getNewRef}
            id="unit"
            defaultValue={nodeUnit.value}
            showIndices={node.with_indices}
            index={nodeUnit.index}
            autoFocus={false}
            add={true}
            zIndex={node.layer + 2}
          />
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleIndexChange={handleIndexChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            getNewRef={getNewRef}
            id="std"
            defaultOp={nodeStd.valOp.operator}
            defaultVal={nodeStd.valOp.value}
            showIndices={node.with_indices}
            index={nodeStd.index}
            autoFocus={false}
            zIndex={node.layer + 2}
          />
          <NodeInputStrOp
            handleOpChange={handleOpChangeLocal}
            handleValChange={handleValChangeLocal}
            handleIndexChange={handleIndexChangeLocal}
            handleKeyUp={handleKeyUp}
            handleBlur={handleBlur}
            getNewRef={getNewRef}
            id="error"
            defaultOp={nodeError.valOp.operator}
            defaultVal={nodeError.valOp.value}
            showIndices={node.with_indices}
            index={nodeError.index}
            autoFocus={false}
            zIndex={node.layer + 1}
          />
        </>
      )}
    </div>
  )
})
