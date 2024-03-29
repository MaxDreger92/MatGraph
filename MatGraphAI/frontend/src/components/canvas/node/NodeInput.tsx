import { useMantineColorScheme } from '@mantine/core'
import React, { useState, useContext, useEffect, useRef, useCallback } from 'react'
import RefContext from '../../workflow/context/RefContext'

import { CustomRef, INode, NodeAttribute, NodeValOpAttribute } from '../../../types/canvas.types'
import NodeInputStr from './NodeInputStr'
import NodeInputStrOp from './NodeInputStrOp'

interface NodeInputProps {
    isValueNode: boolean
    node: INode
    handleNodeUpdate: (node: INode, endEditing?: boolean) => void
}

export default React.memo(function NodeInput(props: NodeInputProps) {
    const { isValueNode, node, handleNodeUpdate } = props

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

    const { refs, getNewDivRef, resetRefs } = useContext(RefContext)

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'

    // useEffect(() => {
    //     const updateActiveElement = () => {
    //         activeElementRef.current = document.activeElement
    //     }

    //     document.addEventListener('focus', updateActiveElement, true)

    //     return () => {
    //         document.removeEventListener('focus', updateActiveElement, true)
    //     }
    // }, [])

    const updateNode = useCallback(() => {
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
        console.log(updatedNode.name.value)
        handleNodeUpdate(updatedNode, true)
    }, [
        node,
        nodeName,
        nodeValue,
        nodeBatchNum,
        nodeRatio,
        nodeConcentration,
        nodeUnit,
        nodeStd,
        nodeError,
        nodeIdentifier,
        handleNodeUpdate,
    ])

    // Update node through changed refs (removal of ref in other component)
    useEffect(() => {
        setTimeout(() => {
            if (refs.some((ref) => document.activeElement === ref.current)) {
                return
            }
            updateNode()
        }, 100)
    }, [refs, updateNode])

    // Update node through blur event
    const handleBlur = () => {
        setTimeout(() => {
            // Check if the active element is one of the refs
            if (refs.some((ref) => document.activeElement === ref.current)) {
                return
            }
            updateNode()
        }, 100)
    }

    // Update node through Enter key
    const handleKeyUp = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            e.preventDefault()
            updateNode()
        }
    }

    useEffect(() => {
        console.log(nodeName.value)
    }, [nodeName])

    const handleUpdateLocal = (id: string, value?: string, operator?: string, index?: string) => {
        let typed_index: string | number | null = null

        if (index !== undefined) {
            const numericValue = parseFloat(index)
            typed_index = isNaN(numericValue) ? index : numericValue
        }

        switch (id) {
            case 'name':
                setNodeName({
                    value: value ?? nodeName.value,
                    index: typed_index ?? nodeName.index,
                })
                break
            case 'batch':
                setNodeBatchNum({
                    value: value ?? nodeBatchNum.value,
                    index: typed_index ?? nodeBatchNum.index,
                })
                break
            case 'unit':
                setNodeUnit({
                    value: value ?? nodeUnit.value,
                    index: typed_index ?? nodeUnit.index,
                })
                break
            case 'identifier':
                setNodeIdentifier({
                    value: value ?? nodeIdentifier.value,
                    index: typed_index ?? nodeIdentifier.index,
                })
                break
            case 'value':
                setNodeValue({
                    valOp: {
                        value: value ?? nodeValue.valOp.value,
                        operator: operator ?? nodeValue.valOp.operator,
                    },
                    index: typed_index ?? nodeValue.index,
                })
                break
            case 'ratio':
                setNodeRatio({
                    valOp: {
                        value: value ?? nodeRatio.valOp.value,
                        operator: operator ?? nodeRatio.valOp.operator,
                    },
                    index: typed_index ?? nodeRatio.index,
                })
                break
            case 'concentration':
                setNodeConcentration({
                    valOp: {
                        value: value ?? nodeConcentration.valOp.value,
                        operator: operator ?? nodeConcentration.valOp.operator,
                    },
                    index: typed_index ?? nodeConcentration.index,
                })
                break
            case 'std':
                setNodeStd({
                    valOp: {
                        value: value ?? nodeStd.valOp.value,
                        operator: operator ?? nodeStd.valOp.operator,
                    },
                    index: typed_index ?? nodeStd.index,
                })
                break
            case 'error':
                setNodeError({
                    valOp: {
                        value: value ?? nodeError.valOp.value,
                        operator: operator ?? nodeError.valOp.operator,
                    },
                    index: typed_index ?? nodeError.index,
                })
                break
            default:
                break
        }

        if (typed_index) {
            const updatedNode = { ...node }

            switch (id) {
                case 'name':
                    updatedNode.name.index = typed_index
                    break
                case 'value':
                    updatedNode.value.index = typed_index
                    break
                case 'batch':
                    updatedNode.batch_num.index = typed_index
                    break
                case 'ratio':
                    updatedNode.ratio.index = typed_index
                    break
                case 'concentration':
                    updatedNode.concentration.index = typed_index
                    break
                case 'unit':
                    updatedNode.unit.index = typed_index
                    break
                case 'std':
                    updatedNode.std.index = typed_index
                    break
                case 'error':
                    updatedNode.error.index = typed_index
                    break
                case 'identifier':
                    updatedNode.identifier.index = typed_index
                    break
                default:
                    break
            }

            handleNodeUpdate(updatedNode)
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
                handleUpdate={handleUpdateLocal}
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
                    handleUpdate={handleUpdateLocal}
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
                        handleUpdate={handleUpdateLocal}
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
                        handleUpdate={handleUpdateLocal}
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
                        handleUpdate={handleUpdateLocal}
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
                        handleUpdate={handleUpdateLocal}
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
                        handleUpdate={handleUpdateLocal}
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
                        handleUpdate={handleUpdateLocal}
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
                        handleUpdate={handleUpdateLocal}
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
                        handleUpdate={handleUpdateLocal}
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
