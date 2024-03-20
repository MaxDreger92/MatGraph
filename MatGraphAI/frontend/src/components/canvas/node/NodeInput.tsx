import { useMantineColorScheme } from '@mantine/core'
import React, { useState, useContext } from 'react'
import RefContext from '../../workflow/context/RefContext'

import { INode, NodeAttribute, NodeValOpAttribute } from '../../../types/canvas.types'
import NodeInputStr from './NodeInputStr'
import NodeInputStrOp from './NodeInputStrOp'

interface NodeInputProps {
    isValueNode: boolean
    node: INode
    handleUpdateNode: (node: INode) => void
}

export default React.memo(function NodeInput(props: NodeInputProps) {
    const { isValueNode, node, handleUpdateNode } = props

    const [nodeName, setNodeName] = useState<NodeAttribute>(node.name)
    const [nodeValue, setNodeValue] = useState<NodeValOpAttribute>(node.value)
    const [nodeBatchNum, setNodeBatchNum] = useState<NodeAttribute>(node.batch_num)
    const [nodeRatio, setNodeRatio] = useState<NodeValOpAttribute>(node.ratio)
    const [nodeConcentration, setNodeConcentration] = useState<NodeValOpAttribute>(
        node.concentration
    )
    const [nodeUnit, setNodeUnit] = useState<NodeAttribute>(node.unit)
    const [nodeStd, setNodeStd] = useState<NodeValOpAttribute>(node.std)
    const [nodeError, setNodeError] = useState<NodeValOpAttribute>(node.error)
    const [nodeIdentifier, setNodeIdentifier] = useState<NodeAttribute>(node.identifier)

    const [showIndexChoice, setShowIndexChoice] = useState<string>('')

    const { refs, getNewDivRef } = useContext(RefContext)

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'

    const updateNode = () => {
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
        handleUpdateNode(updatedNode)
    }

    const handleBlur = () => {
        setTimeout(() => {
            // Check if the active element is one of the refs
            if (refs.some((ref) => document.activeElement === ref.current)) {
                return
            }
            updateNode()
        }, 100)
    }

    const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault()
            updateNode()
        }
    }

    const handleStrChangeLocal = (id: string, value: string) => {
        switch (id) {
            case 'name':
                setNodeName({ value: value, index: nodeName.index })
                break
            case 'batch':
                setNodeBatchNum({ value: value, index: nodeBatchNum.index })
                break
            case 'unit':
                setNodeUnit({ value: value, index: nodeUnit.index })
                break
            case 'identifier':
                setNodeIdentifier({ value: value, index: nodeIdentifier.index })
                break
            default:
                break
        }
    }

    const handleValChangeLocal = (id: string, value: string) => {
        switch (id) {
            case 'value':
                setNodeValue({
                    valOp: { value: value, operator: nodeValue.valOp.operator },
                    index: nodeValue.index,
                })
                break
            case 'ratio':
                setNodeRatio({
                    valOp: { value: value, operator: nodeRatio.valOp.operator },
                    index: nodeRatio.index,
                })
                break
            case 'concentration':
                setNodeConcentration({
                    valOp: { value: value, operator: nodeConcentration.valOp.operator },
                    index: nodeConcentration.index,
                })
                break
            case 'std':
                setNodeStd({
                    valOp: { value: value, operator: nodeStd.valOp.operator },
                    index: nodeStd.index,
                })
                break
            case 'error':
                setNodeError({
                    valOp: { value: value, operator: nodeError.valOp.operator },
                    index: nodeError.index,
                })
                break
            default:
                break
        }
    }

    const handleOpChangeLocal = (id: string, operator: string) => {
        switch (id) {
            case 'value':
                setNodeValue({
                    valOp: { value: nodeValue.valOp.value, operator: operator },
                    index: nodeValue.index,
                })
                break
            case 'ratio':
                setNodeRatio({
                    valOp: { value: nodeRatio.valOp.value, operator: operator },
                    index: nodeRatio.index,
                })
                break
            case 'concentration':
                setNodeConcentration({
                    valOp: { value: nodeConcentration.valOp.value, operator: operator },
                    index: nodeConcentration.index,
                })
                break
            case 'std':
                setNodeStd({
                    valOp: { value: nodeStd.valOp.value, operator: operator },
                    index: nodeStd.index,
                })
                break
            case 'error':
                setNodeError({
                    valOp: { value: nodeError.valOp.value, operator: operator },
                    index: nodeError.index,
                })
                break
            default:
                break
        }
    }

    const handleIndexChangeLocal = (id: string, index: string) => {
        // console.log("Setting new index: " + id + " " + index)

        let input_value: string | number

        const numericValue = parseFloat(index)
        input_value = isNaN(numericValue) ? index : numericValue

        switch (id) {
            case 'name':
                setNodeName({ value: nodeName.value, index: input_value })
                break
            case 'value':
                setNodeValue({
                    valOp: { value: nodeValue.valOp.value, operator: nodeValue.valOp.operator },
                    index: input_value,
                })
                break
            case 'batch':
                setNodeBatchNum({ value: nodeBatchNum.value, index: input_value })
                break
            case 'ratio':
                setNodeRatio({
                    valOp: { value: nodeRatio.valOp.value, operator: nodeRatio.valOp.operator },
                    index: input_value,
                })
                break
            case 'concentration':
                setNodeConcentration({
                    valOp: {
                        value: nodeConcentration.valOp.value,
                        operator: nodeConcentration.valOp.operator,
                    },
                    index: input_value,
                })
                break
            case 'unit':
                setNodeUnit({ value: nodeUnit.value, index: input_value })
                break
            case 'std':
                setNodeStd({
                    valOp: { value: nodeStd.valOp.value, operator: nodeStd.valOp.operator },
                    index: input_value,
                })
                break
            case 'error':
                setNodeError({
                    valOp: { value: nodeError.valOp.value, operator: nodeError.valOp.operator },
                    index: input_value,
                })
                break
            case 'identifier':
                setNodeIdentifier({ value: nodeIdentifier.value, index: input_value })
                break
            default:
                break
        }
    }

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
            ref={getNewDivRef()}
            tabIndex={0}
            className="node-input"
            onClick={(e) => e.stopPropagation()}
            onMouseUp={(e) => e.stopPropagation()}
            onBlur={handleBlur}
            style={{
                display: 'flex',
                flexDirection: 'column',
                borderRadius: 3,
                backgroundColor: darkTheme ? '#1a1b1e' : '#f8f9fa',
                zIndex: node.layer + 1,
                cursor: 'default',
            }}
        >
            <NodeInputStr
                handleStrChange={handleStrChangeLocal}
                handleIndexChange={handleIndexChangeLocal}
                handleKeyUp={handleKeyUp}
                handleBlur={handleBlur}
                id="name"
                defaultValue={nodeName.value}
                showIndices={node.with_indices}
                showIndexChoice={showIndexChoice}
                setShowIndexChoice={setShowIndexChoice}
                index={nodeName.index}
                autoFocus={true}
                add={false}
                zIndex={node.layer + 4}
            />

            {['manufacturing', 'measurement', 'metadata'].includes(node.type) && (
                <NodeInputStr
                    handleStrChange={handleStrChangeLocal}
                    handleIndexChange={handleIndexChangeLocal}
                    handleKeyUp={handleKeyUp}
                    handleBlur={handleBlur}
                    id="identifier"
                    defaultValue={nodeIdentifier.value}
                    showIndices={node.with_indices}
                    index={nodeIdentifier.index}
                    showIndexChoice={showIndexChoice}
                    setShowIndexChoice={setShowIndexChoice}
                    autoFocus={false}
                    add={true}
                    zIndex={node.layer + 3}
                />
            )}

            {node.type === 'matter' && (
                <>
                    <NodeInputStr
                        handleStrChange={handleStrChangeLocal}
                        handleIndexChange={handleIndexChangeLocal}
                        handleKeyUp={handleKeyUp}
                        handleBlur={handleBlur}
                        id="identifier"
                        defaultValue={nodeIdentifier.value}
                        showIndices={node.with_indices}
                        index={nodeIdentifier.index}
                        showIndexChoice={showIndexChoice}
                        setShowIndexChoice={setShowIndexChoice}
                        autoFocus={false}
                        add={true}
                        zIndex={node.layer + 3}
                    />
                    <NodeInputStr
                        handleStrChange={handleStrChangeLocal}
                        handleIndexChange={handleIndexChangeLocal}
                        handleKeyUp={handleKeyUp}
                        handleBlur={handleBlur}
                        id="batch"
                        defaultValue={nodeBatchNum.value}
                        showIndices={node.with_indices}
                        index={nodeBatchNum.index}
                        showIndexChoice={showIndexChoice}
                        setShowIndexChoice={setShowIndexChoice}
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
                        id="ratio"
                        defaultOp={nodeRatio.valOp.operator}
                        defaultVal={nodeRatio.valOp.value}
                        showIndices={node.with_indices}
                        index={nodeRatio.index}
                        showIndexChoice={showIndexChoice}
                        setShowIndexChoice={setShowIndexChoice}
                        autoFocus={false}
                        zIndex={node.layer + 2}
                    />
                    <NodeInputStrOp
                        handleOpChange={handleOpChangeLocal}
                        handleValChange={handleValChangeLocal}
                        handleIndexChange={handleIndexChangeLocal}
                        handleKeyUp={handleKeyUp}
                        handleBlur={handleBlur}
                        id="concentration"
                        defaultOp={nodeConcentration.valOp.operator}
                        defaultVal={nodeConcentration.valOp.value}
                        showIndices={node.with_indices}
                        index={nodeConcentration.index}
                        showIndexChoice={showIndexChoice}
                        setShowIndexChoice={setShowIndexChoice}
                        autoFocus={false}
                        zIndex={node.layer + 1}
                    />
                </>
            )}

            {['parameter', 'property'].includes(node.type) && (
                <>
                    <NodeInputStrOp
                        handleOpChange={handleOpChangeLocal}
                        handleValChange={handleValChangeLocal}
                        handleIndexChange={handleIndexChangeLocal}
                        handleKeyUp={handleKeyUp}
                        handleBlur={handleBlur}
                        id="value"
                        defaultOp={nodeValue.valOp.operator}
                        defaultVal={nodeValue.valOp.value}
                        showIndices={node.with_indices}
                        index={nodeValue.index}
                        showIndexChoice={showIndexChoice}
                        setShowIndexChoice={setShowIndexChoice}
                        autoFocus={
                            node.name.value !== '' && isValueNode && node.value.valOp.value === ''
                        }
                        zIndex={node.layer + 3}
                    />
                    <NodeInputStr
                        handleStrChange={handleStrChangeLocal}
                        handleIndexChange={handleIndexChangeLocal}
                        handleKeyUp={handleKeyUp}
                        handleBlur={handleBlur}
                        id="unit"
                        defaultValue={nodeUnit.value}
                        showIndices={node.with_indices}
                        index={nodeUnit.index}
                        showIndexChoice={showIndexChoice}
                        setShowIndexChoice={setShowIndexChoice}
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
                        id="std"
                        defaultOp={nodeStd.valOp.operator}
                        defaultVal={nodeStd.valOp.value}
                        showIndices={node.with_indices}
                        index={nodeStd.index}
                        showIndexChoice={showIndexChoice}
                        setShowIndexChoice={setShowIndexChoice}
                        autoFocus={false}
                        zIndex={node.layer + 2}
                    />
                    <NodeInputStrOp
                        handleOpChange={handleOpChangeLocal}
                        handleValChange={handleValChangeLocal}
                        handleIndexChange={handleIndexChangeLocal}
                        handleKeyUp={handleKeyUp}
                        handleBlur={handleBlur}
                        id="error"
                        defaultOp={nodeError.valOp.operator}
                        defaultVal={nodeError.valOp.value}
                        showIndices={node.with_indices}
                        index={nodeError.index}
                        showIndexChoice={showIndexChoice}
                        setShowIndexChoice={setShowIndexChoice}
                        autoFocus={false}
                        zIndex={node.layer + 1}
                    />
                </>
            )}
        </div>
    )
})
