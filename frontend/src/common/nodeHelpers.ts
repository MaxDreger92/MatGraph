import { INode } from "../types/canvas.types"
import { isAttrDefined, relationshipToRelType } from "./workflowHelpers"

/**
 * Determine if a relationship between two nodes is allowed.
 *
 * @param start Starting node
 * @param end Ending node
 * @returns true if the relationship is legitimate, false otherwise
 */
export function isRelationshipLegitimate(start: INode, end: INode): boolean {
    const allowedRelationships: Array<[string, string]> = [
        ['matter', 'manufacturing'], // IS_MANUFACTURING_INPUT
        ['manufacturing', 'matter'], // IS_MANUFACTURING_OUTPUT
        ['matter', 'measurement'], // IS_MEASUREMENT_INPUT
        ['matter', 'property'], // HAS_PROPERTY
        ['manufacturing', 'parameter'], // HAS_PARAMETER
        ['measurement', 'parameter'], //HAS_PARAMETER
        ['measurement', 'property'], // HAS_MEASUREMENT_OUTPUT
        ['manufacturing', 'metadata'], // HAS_METADATA
        ['measurement', 'metadata'], // HAS_METADATA
        ['matter', 'matter'], // HAS_PART
        ['manufacturing', 'manufacturing'], // HAS_PART
        ['measurement', 'measurement'], // HAS_PART
    ]

    // Check if the [start.type, end.type] tuple exists in the allowed relationships array
    return allowedRelationships.some(
        (relationship) => relationship[0] === start.type && relationship[1] === end.type
    )
}

/**
 * Gets a list of possible end types for a given start type.
 *
 * @param startType Starting node's type
 * @returns Array of possible end node types for the given start type
 */
export function possibleRelationships(startType: string | undefined): string[] {
    if (!startType)
        return ['matter', 'manufacturing', 'parameter', 'property', 'measurement', 'metadata', 'simulation']

    // Filter the keys to find matches and extract the endType
    return Object.keys(relationshipToRelType)
        .filter((key) => key.startsWith(`${startType}-`))
        .map((key) => key.split('-')[1])
}

/**
 * Checks if a given node type can connect to another node.
 *
 * @param nodeType Type of the node
 * @returns true if the node can connect to another node, false otherwise
 */
export function isConnectableNode(nodeType: string | undefined): boolean {
    if (!nodeType) return false

    // Check if there's a key that starts with the given nodeType followed by a '-'
    return Object.keys(relationshipToRelType).some((key) => key.startsWith(`${nodeType}-`))
}

export const calculateNodeOptimalSize = (
    nodeSize: number,
    nodeName: INode['name'],
    nodeValue: INode['value'],
    nodeType: INode['type']
) => {
    if (!isAttrDefined(nodeName.value)) {
        return nodeSize
    }

    const characterFactor = 16 - calculateLabelFontSize(nodeSize)

    const nameMinimumSize = nodeName.value.length * (11 - characterFactor)
    let nodeMinimumSize = nameMinimumSize

    if (getIsValueNode(nodeType) && isAttrDefined(nodeValue.valOp)) {
        const valueMinimumSize = nodeValue.valOp.value.length * (9 - characterFactor) + 20
        nodeMinimumSize = Math.max(nodeMinimumSize, valueMinimumSize)
    }

    return nodeMinimumSize > nodeSize ? nodeMinimumSize : nodeSize
}

const calculateLabelFontSize = (nodeSize: number) => {
    const fontSize = 16 + Math.floor((nodeSize - 100) / 70)
    return fontSize
}

export const getIsValueNode = (nodeType: INode['type']) => {
    return ['property', 'parameter'].includes(nodeType)
}