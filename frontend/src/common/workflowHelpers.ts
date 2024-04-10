<<<<<<<< HEAD:MatGraphAI/frontend/src/common/workflowHelpers.ts
import { PiAddressBookDuotone } from 'react-icons/pi'
import {
    INode,
    IRelationship,
    IDRelationship,
    ValOpPair,
    Operator,
    NodeAttribute,
    NodeValOpAttribute,
    AttributeIndex,
    CustomRef,
} from '../types/canvas.types'
import {
    IGraphData,
    ITempNode,
    ExtractedAttribute,
    CustomAttribute,
    ParsableAttributes,
    Label,
} from '../types/workflow.types'
import toast from 'react-hot-toast'
import client from '../client'
import { v4 as uuidv4 } from 'uuid'
import React, { useRef } from 'react'
import { valueGetters } from '@mantine/core/lib/Box/style-system-props/value-getters/value-getters'

const labelAttributes = {
    matter: ['name', 'identifier', 'batch_number', 'ratio', 'concentration'],
    manufacturing: ['name', 'identifier'],
    measurement: ['name', 'identifier'],
    parameter: ['name', 'value', 'unit', 'std', 'error'],
    property: ['name', 'value', 'unit', 'std', 'error'],
    metadata: ['name', 'identifier'],
}

export function getAttributesByLabel(label: Label): string[] {
    return labelAttributes[label]
}

export const relationshipToRelType: Record<string, string> = {
    'matter-manufacturing': 'IS_MANUFACTURING_INPUT',
    'manufacturing-matter': 'IS_MANUFACTURING_OUTPUT',
    'matter-measurement': 'IS_MEASUREMENT_INPUT',
    'matter-property': 'HAS_PROPERTY',
    'manufacturing-parameter': 'HAS_PARAMETER',
    'measurement-property': 'IS_MEASUREMENT_OUTPUT',
    'manufacturing-metadata': 'HAS_METADATA',
    'measurement-metadata': 'HAS_METADATA',
}

/**
 * Map a node type from the application's internal format to the desired output format.
 *
 * @param type Node type from the application
 * @returns Corresponding node type for the JSON structure
 */
function mapNodeType(type: string): string {
    switch (type) {
        case 'matter':
            return 'EMMOMatter'
        case 'manufacturing':
            return 'EMMOProcess'
        case 'measurement':
            return 'EMMOProcess'
        case 'parameter':
            return 'EMMOQuantity'
        case 'property':
            return 'EMMOQuantity'
        case 'metadata':
            return 'EMMOData'
        default:
            return 'UnknownType'
    }
}

export function mapNodeTypeNumerical(type: string): number {
    switch (type) {
        case 'matter':
            return 0
        case 'manufacturing':
            return 1
        case 'measurement':
            return 2
        case 'parameter':
            return 3
        case 'property':
            return 4
        case 'metadata':
            return 5
        default:
            return 69
    }
}

export function mapNodeTypeString(type: number): string {
    switch (type) {
        case 0:
            return 'matter'
        case 1:
            return 'manufacturing'
        case 2:
            return 'measurement'
        case 3:
            return 'parameter'
        case 4:
            return 'property'
        case 5:
            return 'metadata'
        default:
            return 'unknownType'
    }
}

/**
 * Determines the relationship type based on the start and end node types.
 *
 * @param startType Starting node's type
 * @param endType Ending node's type
 * @returns Corresponding relationship type for the relationship
 */
function determineRelationshipType(startType: string, endType: string): string {
    return relationshipToRelType[`${startType}-${endType}`] || 'UNKNOWN_RELATIONSHIP'
}

function isValidOperator(operator: string): boolean {
    return (
        operator === '<' ||
        operator === '<=' ||
        operator === '=' ||
        operator === '!=' ||
        operator === '>=' ||
        operator === '>'
    )
}

export function isAttrDefined(attribute: string | ValOpPair): boolean {
    if (typeof attribute === 'string') {
        return attribute !== ''
    } else if (typeof attribute === 'object' && 'value' in attribute) {
        // Check if 'string' and 'operator' are defined and valid
        const isStringDefined = typeof attribute.value === 'string' && attribute.value !== ''
        const isOperatorValid = isValidOperator(attribute.operator)

        // StrOpPair is valid if both 'string' and 'operator' are valid
        return isStringDefined && isOperatorValid
    }
    return false
}

function parseAttrOut(
    attribute: string | ValOpPair,
    index?: AttributeIndex | AttributeIndex[]
): ParsableAttributes {
    let stringToParse = ''

    // Determine the string to parse based on the type of attribute
    if (typeof attribute === 'string') {
        stringToParse = attribute
    } else if ('value' in attribute && typeof attribute.value === 'string') {
        stringToParse = attribute.value
    }

    // Split the string by semicolons
    const splitStrings = stringToParse
        .split(';')
        .map((s) => s.trim())
        .filter((s) => s !== '')
    const parsedString = splitStrings.length === 1 ? splitStrings[0] : splitStrings

    if (index === undefined) {
        if (typeof attribute === 'string') {
            return { value: parsedString } as CustomAttribute
        } else {
            return {
                value: parsedString,
                operator: attribute.operator as Operator,
            } as CustomAttribute
        }
    } else {
        if (typeof parsedString === 'string' && !Array.isArray(index)) {
            return { value: parsedString, index: index } as ExtractedAttribute
        } else {
            if (Array.isArray(parsedString) && Array.isArray(index)) {
                return parsedString.map((s, i) => ({
                    value: s,
                    index: index[i],
                })) as ExtractedAttribute[]
            } else {
                return { value: 'ERROR_PARSING_EXTRACTED_ATTR' } as CustomAttribute
            }
        }
    }
}

function parseAttr(
    attribute: ParsableAttributes | undefined,
    isValOp: boolean
): NodeAttribute | NodeValOpAttribute {
    if (attribute === undefined) {
        if (isValOp) {
            return { valOp: { value: '', operator: '' } } as NodeValOpAttribute
        } else {
            return { value: '' } as NodeAttribute
        }
    }

    if (Array.isArray(attribute) || 'index' in attribute) {
        return parseExtractedAttribute(attribute, isValOp)
    } else {
        return parseCustomAttribute(attribute, isValOp)
    }
}

function parseExtractedAttribute(
    attribute: ExtractedAttribute | ExtractedAttribute[],
    isValOp: boolean
): NodeAttribute | NodeValOpAttribute {
    if (Array.isArray(attribute)) {
        let values: string[] = []
        let indices: AttributeIndex[] = []
        attribute.forEach((item) => {
            values.push(item.value)
            indices.push(item.index)
        })
        const finalIndex = indices.length > 1 ? indices : indices[0]
        if (isValOp) {
            return {
                valOp: { value: values.join(';'), operator: '=' as Operator },
                index: finalIndex,
            } as NodeValOpAttribute
        } else {
            return { value: values.join(';'), index: finalIndex } as NodeAttribute
        }
    } else {
        if (isValOp) {
            return {
                valOp: { value: attribute.value, operator: '=' as Operator },
                index: attribute.index,
            } as NodeValOpAttribute
        } else {
            return { value: attribute.value, index: attribute.index } as NodeAttribute
        }
    }
}

function parseCustomAttribute(
    attribute: CustomAttribute,
    isValOp: boolean
): NodeAttribute | NodeValOpAttribute {
    if (Array.isArray(attribute.value)) {
        if (isValOp) {
            const op = attribute.operator ? attribute.operator : ('=' as Operator)
            return {
                valOp: { value: attribute.value.join(';'), operator: op },
            } as NodeValOpAttribute
        } else {
            return { value: attribute.value.join(';') } as NodeAttribute
        }
    } else {
        if (isValOp) {
            const op = attribute.operator ? attribute.operator : ('=' as Operator)
            return {
                valOp: { value: attribute.value, operator: op },
            } as NodeValOpAttribute
        } else {
            return { value: attribute.value } as NodeAttribute
        }
    }
}

export function convertToJSONFormat(
    nodes: INode[],
    relationships: IRelationship[],
    preventMapTypes?: boolean
): string {
    // Convert relationships into a map for easier lookup
    const relationshipMap = relationships.reduce((acc, relationship) => {
        // Capture relationships where the node is the start point
        if (!acc[relationship.start.id]) {
            acc[relationship.start.id] = []
        }
        acc[relationship.start.id].push(relationship)

        // Capture relationships where the node is the end point
        if (!acc[relationship.end.id]) {
            acc[relationship.end.id] = []
        }
        acc[relationship.end.id].push(relationship)

        return acc
    }, {} as Record<string, IRelationship[]>)

    const processedNodes = nodes.map((node) => {
        // Group all attributes under an attributes object
        const attributes: { [key: string]: ParsableAttributes } = {}
        if (isAttrDefined(node.name.value)) {
            attributes.name = parseAttrOut(node.name.value, node.name.index)
        } else {
            attributes.name = { value: 'MISSING_NAME' }
        }
        if (isAttrDefined(node.value.valOp)) {
            attributes.value = parseAttrOut(node.value.valOp, node.value.index)
        } else if (['property', 'parameter'].includes(node.type)) {
            attributes.value = { value: 'MISSING_VALUE_OR_OPERATOR' }
        }
        if (isAttrDefined(node.batch_num.value))
            attributes.batch_num = parseAttrOut(node.batch_num.value, node.batch_num.index)
        if (isAttrDefined(node.unit.value))
            attributes.unit = parseAttrOut(node.unit.value, node.unit.index)
        if (isAttrDefined(node.ratio.valOp))
            attributes.ratio = parseAttrOut(node.ratio.valOp, node.ratio.index)
        if (isAttrDefined(node.concentration.valOp))
            attributes.concentration = parseAttrOut(
                node.concentration.valOp,
                node.concentration.index
            )
        if (isAttrDefined(node.std.valOp))
            attributes.std = parseAttrOut(node.std.valOp, node.std.index)
        if (isAttrDefined(node.error.valOp))
            attributes.error = parseAttrOut(node.error.valOp, node.error.index)
        if (isAttrDefined(node.identifier.value))
            attributes.identifier = parseAttrOut(node.identifier.value, node.identifier.index)

        // Return the node object with id, type, attributes, and relationships
        return {
            id: node.id,
            name: attributes.name,
            label: preventMapTypes ? node.type : mapNodeType(node.type),
            attributes,
        }
    })

    const processedRelationships = relationships.map((relationship) => ({
        rel_type: determineRelationshipType(relationship.start.type, relationship.end.type), // Assume this function is defined elsewhere
        connection: [relationship.start.id, relationship.end.id],
    }))

    const finalStructure = {
        nodes: processedNodes,
        relationships: processedRelationships,
    }

    return JSON.stringify(finalStructure, null, 2)
}

export function convertFromJsonFormat(workflow: string, uploadMode: boolean) {
    const data: IGraphData = JSON.parse(workflow)
    const nodes: INode[] = []
    const relationships: IRelationship[] = []

    data.nodes.forEach((item) => {
        nodes.push({
            id: item.id,
            name: parseAttr(item.attributes.name, false) as NodeAttribute,
            value: parseAttr(item.attributes.value, true) as NodeValOpAttribute,
            batch_num: parseAttr(item.attributes.batch_number, false) as NodeAttribute,
            ratio: parseAttr(item.attributes.ratio, true) as NodeValOpAttribute,
            concentration: parseAttr(item.attributes.concentration, true) as NodeValOpAttribute,
            unit: parseAttr(item.attributes.unit, false) as NodeAttribute,
            std: parseAttr(item.attributes.std, true) as NodeValOpAttribute,
            error: parseAttr(item.attributes.error, true) as NodeValOpAttribute,
            identifier: parseAttr(item.attributes.identifier, false) as NodeAttribute,
            type: item.label,
            with_indices: uploadMode,
            position: { x: -100, y: -100 },
            size: 100,
            optimalSize: 100,
            layer: 0,
            isEditing: false,
        })
    })

    data.relationships.forEach((rel) => {
        const [sourceNodeId, targetNodeId] = [rel.connection[0], rel.connection[1]]
        const start = nodes.find((node) => node.id === sourceNodeId)
        const end = nodes.find((node) => node.id === targetNodeId)

        if (start && end) {
            const id = uuidv4().replaceAll('-', '')
            relationships.push({ start, end, id })
        }
    })

    return {
        nodes,
        relationships: relationships,
    }
}

export const getNodeIndices = (node: INode): number[] => {
    let indices: number[] = []

    indices.push(...getNumericAttributeIndices(node.name))
    indices.push(...getNumericAttributeIndices(node.value))
    indices.push(...getNumericAttributeIndices(node.batch_num))
    indices.push(...getNumericAttributeIndices(node.ratio))
    indices.push(...getNumericAttributeIndices(node.concentration))
    indices.push(...getNumericAttributeIndices(node.unit))
    indices.push(...getNumericAttributeIndices(node.std))
    indices.push(...getNumericAttributeIndices(node.error))
    indices.push(...getNumericAttributeIndices(node.identifier))

    return indices
}

export const getNumericAttributeIndices = (attribute: NodeAttribute | NodeValOpAttribute) => {
    let indices: number[] = []

    if (attribute.index !== undefined) {
        if (typeof attribute.index === 'number') {
            indices.push(attribute.index)
        } else if (Array.isArray(attribute.index)) {
            const numericIndices: any[] = attribute.index.filter(
                (index) => typeof index === 'number'
            )
            indices.push(...numericIndices)
        }
    }

    return indices
}

export function saveToFile(data: string, type: 'json' | 'csv', filename: string) {
    // Convert the data to a JSON string
    //const jsonString = JSON.stringify(data, null, 2);  // 2 spaces for indentation

    // Create a blob with the JSON string
    const blob = new Blob([data], { type: `application/${type}` })

    // Create a URL for the blobn
    const url = URL.createObjectURL(blob)

    // Create an anchor element and set its href to the blob's URL
    const a = document.createElement('a')
    a.href = url
    a.download = filename

    // Simulate a click on the anchor element
    document.body.appendChild(a)
    a.click()

    // Clean up by removing the anchor element and revoking the blob URL
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
}

export function saveBlobAsFile(blob: Blob, filename: string) {
    if (!(blob instanceof Blob)) {
        console.error('Provided data is not a Blob')
        return
    }
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    window.URL.revokeObjectURL(url)
}

export function fileToDataUri(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = (event) => {
            resolve(event.target?.result as string)
        }
        reader.onerror = (err) => {
            reject(err)
        }
        reader.readAsDataURL(file)
    })
}


========
export function clamp(value: number, min: number, max: number) {
    return Math.min(Math.max(value, min), max)
}
>>>>>>>> bc5ef8e7b (Reduces rerenders of nodes massively):MatGraphAI/frontend/src/common/helpers.ts
