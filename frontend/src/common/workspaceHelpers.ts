import {
    TNode,
    TRelationship,
    ValOpPair,
    NodeAttribute,
    NodeValOpAttribute,
} from '../types/canvas.types'
import { GraphData, ParsableAttribute, Label, TableRow, Dictionary } from '../types/workspace.types'
import { v4 as uuidv4 } from 'uuid'
import { tryNumeric, splitStrBySemicolon, ensureArray } from './helpers'
import Papa from 'papaparse'

const labelAttributes = {
    matter: ['name', 'identifier', 'batch number', 'ratio', 'concentration'],
    manufacturing: ['name', 'identifier'],
    measurement: ['name', 'identifier'],
    parameter: ['name', 'value', 'unit', 'standard deviation', 'error'],
    property: ['name', 'value', 'unit', 'standard deviation', 'error'],
    metadata: ['metadata_type', 'value'],
}

export const getAttributesByLabel = (label: Label): string[] => {
    return labelAttributes[label]
}

export const relationshipToRelType: Record<string, string> = {
    'matter-manufacturing': 'IS_MANUFACTURING_INPUT',
    'manufacturing-matter': 'IS_MANUFACTURING_OUTPUT',
    'matter-measurement': 'IS_MEASUREMENT_INPUT',
    'matter-property': 'HAS_PROPERTY',
    'manufacturing-parameter': 'HAS_PARAMETER',
    'measurement-parameter': 'HAS_PARAMETER',
    'measurement-property': 'HAS_MEASUREMENT_OUTPUT',
    'manufacturing-metadata': 'HAS_METADATA',
    'measurement-metadata': 'HAS_METADATA',
    'matter-matter': 'HAS_PART',
    'manufacturing-manufacturing': 'HAS_PART',
    'measurement-measurement': 'HAS_PART',
}

const mapNodeType = (type: string): string => {
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

export const mapNodeTypeNumerical = (type: string): number => {
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

export const mapNodeTypeString = (type: number): string => {
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

const determineRelationshipType = (startType: string, endType: string): string => {
    return relationshipToRelType[`${startType}-${endType}`] || 'UNKNOWN_RELATIONSHIP'
}

export const isValidOperator = (operator: string): boolean => {
    return (
        operator === '<' ||
        operator === '<=' ||
        operator === '=' ||
        operator === '!=' ||
        operator === '>=' ||
        operator === '>'
    )
}

export const isAttrDefined = (attribute?: string | ValOpPair): boolean => {
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

const parseAttrOut = (
    attributeValue: string | ValOpPair,
    attributeIndex?: string,
    withIndices?: boolean
): ParsableAttribute => {
    if (typeof attributeValue === 'string') {
        if (withIndices && attributeIndex && attributeIndex !== '') {
            return parseIdxValAttrOut(attributeValue, attributeIndex)
        } else {
            return parseValAttrOut(attributeValue)
        }
    } else {
        if (withIndices && attributeIndex && attributeIndex !== '') {
            return parseIdxValOpAttrOut(
                attributeValue.value,
                attributeValue.operator,
                attributeIndex
            )
        } else {
            return parseValOpAttrOut(attributeValue.value, attributeValue.operator)
        }
    }
}

// Value = string, no index
const parseValAttrOut = (value: string): ParsableAttribute => {
    const parsedValue = splitStrBySemicolon(value)

    if (Array.isArray(parsedValue)) {
        return parsedValue.map((value) => ({
            value: value,
        }))
    } else {
        return { value: parsedValue }
    }
}

// Value = string, with index
const parseIdxValAttrOut = (value: string, index: string): ParsableAttribute => {
    const parsedValue = splitStrBySemicolon(value)
    const parsedIndex = splitStrBySemicolon(index)

    if (Array.isArray(parsedValue)) {
        if (Array.isArray(parsedIndex) && parsedValue.length === parsedIndex.length) {
            const rawIndices = parsedIndex
            return parsedValue.map((val, i) => {
                const typedIndex = tryNumeric(rawIndices[i])
                return { value: val, index: typedIndex }
            })
        } else {
            return parsedValue.map((value) => ({
                value: value,
                index: 'ARRAY_LENGTH_MISMATCH',
            }))
        }
    } else if (Array.isArray(parsedIndex)) {
        return { value: parsedValue, index: 'ARRAY_LENGTH_MISMATCH' }
    } else {
        const typedIndex = tryNumeric(parsedIndex)
        return { value: parsedValue, index: typedIndex }
    }
}

// Value = value(string) + operator(string), no index
const parseValOpAttrOut = (value: string, operator: string): ParsableAttribute => {
    const parsedValue = splitStrBySemicolon(value)

    if (Array.isArray(parsedValue)) {
        return parsedValue.map((value) => ({
            value: value,
            operator: operator,
        }))
    } else {
        return { value: parsedValue, operator: operator }
    }
}

// Value = value(string) + operator(string), with index
const parseIdxValOpAttrOut = (
    value: string,
    operator: string,
    index: string
): ParsableAttribute => {
    const parsedValue = splitStrBySemicolon(value)
    const parsedIndex = splitStrBySemicolon(index)

    if (Array.isArray(parsedValue)) {
        if (Array.isArray(parsedIndex) && parsedValue.length === parsedIndex.length) {
            const rawIndices = parsedIndex
            return parsedValue.map((val, i) => {
                const typedIndex = tryNumeric(rawIndices[i])
                return { value: val, operator: operator, index: typedIndex }
            })
        } else {
            return parsedValue.map((value) => ({
                value: value,
                operator: operator,
                index: 'ARRAY_LENGTH_MISMATCH',
            }))
        }
    } else if (Array.isArray(parsedIndex)) {
        return { value: parsedValue, operator: operator, index: 'ARRAY_LENGTH_MISMATCH' }
    } else {
        const typedIndex = tryNumeric(parsedIndex)
        return { value: parsedValue, operator: operator, index: typedIndex }
    }
}

const parseAttr = (
    attribute: ParsableAttribute | undefined,
    isValOp: boolean
): NodeAttribute | NodeValOpAttribute => {
    if (attribute === undefined) {
        if (isValOp) {
            return { valOp: { value: '', operator: '' } } as NodeValOpAttribute
        } else {
            return { value: '' } as NodeAttribute
        }
    }

    if (Array.isArray(attribute)) {
        let values: string[] = []
        let indices: string[] = []

        attribute.forEach((item) => {
            values.push(item.value)

            if (item.index) {
                indices.push(item.index.toString())
            }
        })

        const joinedValues = values.join(';')
        let joinedIndices = ''
        if (values.length === indices.length) {
            joinedIndices = indices.join(';')
        }

        if (isValOp) {
            const operator = attribute[0].operator ?? '='
            return { valOp: { value: joinedValues, operator: operator }, index: joinedIndices }
        } else {
            return { value: joinedValues, index: joinedIndices }
        }
    } else {
        if (isValOp) {
            return {
                valOp: { value: attribute.value ?? '', operator: attribute.operator ?? '=' },
                index: (attribute.index ?? '').toString(),
            }
        } else {
            return { value: attribute.value ?? '', index: (attribute.index ?? '').toString() }
        }
    }
}

export const convertToJSONFormat = (
    nodes: TNode[],
    relationships: TRelationship[],
    preventMapTypes?: boolean
): string => {
    const processedNodes = nodes.map((node) => {
        const attributes: { [key: string]: ParsableAttribute } = {}
        if (isAttrDefined(node.name.value)) {
            attributes.name = parseAttrOut(node.name.value, node.name.index, node.withIndices)
        } else {
            attributes.name = { value: 'MISSING_NAME' }
        }
        if (isAttrDefined(node.value.valOp)) {
            attributes.value = parseAttrOut(node.value.valOp, node.value.index, node.withIndices)
        } else if (['property', 'parameter'].includes(node.type)) {
            attributes.value = { value: 'MISSING_VALUE_OR_OPERATOR' }
        }
        if (isAttrDefined(node.batch_num.value))
            attributes.batch_num = parseAttrOut(
                node.batch_num.value,
                node.batch_num.index,
                node.withIndices
            )
        if (isAttrDefined(node.unit.value))
            attributes.unit = parseAttrOut(node.unit.value, node.unit.index, node.withIndices)
        if (isAttrDefined(node.ratio.valOp))
            attributes.ratio = parseAttrOut(node.ratio.valOp, node.ratio.index, node.withIndices)
        if (isAttrDefined(node.concentration.valOp))
            attributes.concentration = parseAttrOut(
                node.concentration.valOp,
                node.concentration.index,
                node.withIndices
            )
        if (isAttrDefined(node.std.valOp))
            attributes.std = parseAttrOut(node.std.valOp, node.std.index, node.withIndices)
        if (isAttrDefined(node.error.valOp))
            attributes.error = parseAttrOut(node.error.valOp, node.error.index, node.withIndices)
        if (isAttrDefined(node.identifier.value))
            attributes.identifier = parseAttrOut(
                node.identifier.value,
                node.identifier.index,
                node.withIndices
            )

        return {
            id: node.id,
            name: attributes.name,
            label: preventMapTypes ? node.type : mapNodeType(node.type),
            attributes,
        }
    })

    const processedRelationships = relationships.map((relationship) => ({
        rel_type: determineRelationshipType(relationship.start.type, relationship.end.type),
        connection: [relationship.start.id, relationship.end.id],
    }))

    const finalStructure = {
        nodes: processedNodes,
        relationships: processedRelationships,
    }

    return JSON.stringify(finalStructure, null, 2)
}

export const convertFromJsonFormat = (graph: string, uploadMode: boolean) => {
    const data: GraphData = JSON.parse(graph)
    const nodes: TNode[] = []
    const relationships: TRelationship[] = []

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
            withIndices: uploadMode,
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

export const getNodeIndices = (node: TNode): number[] => {
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

export const splitDict = (dict: Dictionary, rows: number): [Dictionary, Dictionary] => {
    const dict1: Dictionary = {};
    const dict2: Dictionary = {};

    Object.entries(dict).forEach(([header, properties]) => {
        dict1[header] = {};
        dict2[header] = {};

        const propertyEntries = Object.entries(properties);
        const firstPart = propertyEntries.slice(0, rows);
        const secondPart = propertyEntries.slice(rows);

        firstPart.forEach(([key, value]) => {
            dict1[header][key] = value;
        });

        secondPart.forEach(([key, value]) => {
            dict2[header][key] = value;
        });
    });

    Object.keys(dict1).forEach(header => {
        if (Object.keys(dict1[header]).length === 0) {
            delete dict1[header];
        }
    });
    Object.keys(dict2).forEach(header => {
        if (Object.keys(dict2[header]).length === 0) {
            delete dict2[header];
        }
    });

    return [dict1, dict2];
}

export const joinDict = (dict1: Dictionary, dict2: Dictionary): Dictionary => {
    const combinedDict: Dictionary = {};

    const allHeaders = new Set([...Object.keys(dict1), ...Object.keys(dict2)]);

    allHeaders.forEach(header => {
        combinedDict[header] = {};

        if (dict1[header]) {
            Object.assign(combinedDict[header], dict1[header]);
        }

        if (dict2[header]) {
            Object.assign(combinedDict[header], dict2[header]);
        }
    });

    return combinedDict;
}

export const dictToArray = (dict: Dictionary): TableRow[] => {
    const combinedRows: { [property: string]: TableRow } = {}

    Object.entries(dict).forEach(([header, properties]) => {
        Object.entries(properties).forEach(([property, value]) => {
            if (!combinedRows[property]) {
                combinedRows[property] = {}
            }
            combinedRows[property][header] = value
        })
    })

    return Object.values(combinedRows)
}

export const arrayToDict = (tableRows: TableRow[]): Dictionary => {
    const dict: Dictionary = {}

    const headers = Object.keys(tableRows[0])

    headers.forEach((header) => {
        dict[header] = {}
    })

    tableRows.forEach((row, rowIndex) => {
        Object.entries(row).forEach(([header, value]) => {
            const stringValue = String(value)

            let key = 'Default_Key'

            if (rowIndex === 0) {
                key = 'Label'
            } else if (rowIndex === 1) {
                key = 'Attribute'
            } else {
                key = `Row${rowIndex + 1}`
            }


            dict[header][key] = stringValue
        })
    })

    return dict
}

export const getAdditionalTables = (selectedNodes: TNode[]): number[][] => {
    const newAdditionalTables = selectedNodes.reduce<number[][]>((acc, node) => {
        let indices: number[] = []
    
        const addIndices = (attr: NodeAttribute | NodeValOpAttribute) => {
            if (!attr.index) return
            const strIndices = ensureArray(splitStrBySemicolon(attr.index)) as string[]
            strIndices.forEach((str) => {
                const typed = tryNumeric(str)
                if (typeof typed === 'number') {
                    indices.push(typed)
                }
            })
        }
    
        const numericalNodeType = mapNodeTypeNumerical(node.type)
        indices.push(numericalNodeType)
    
        addIndices(node.name)
        addIndices(node.value)
        addIndices(node.batch_num)
        addIndices(node.ratio)
        addIndices(node.concentration)
        addIndices(node.unit)
        addIndices(node.std)
        addIndices(node.error)
        addIndices(node.identifier)
    
        if (indices.length > 1) {
            acc.push(indices)
        }
        return acc
    }, [])

    return newAdditionalTables
}

export const filterCsvTable = (csvTable: TableRow[], additionalTables: number[][]): TableRow[][] => {
    const filteredTables: TableRow[][] = []

    additionalTables.forEach((additionalTable: number[]) => {
        const filteredTable: TableRow[] = []
        const rowIndexMap: Map<string, number> = new Map()
        const columnsToInclude = additionalTable.slice(1)

        columnsToInclude.forEach((columnIndex: number) => {
            const columnName = Object.keys(csvTable[0])[columnIndex]
            csvTable.forEach((row: TableRow) => {
                const rowKey = JSON.stringify(row)
                if (!rowIndexMap.has(rowKey)) {
                    filteredTable.push({})
                    rowIndexMap.set(rowKey, filteredTable.length - 1)
                }
                const rowIndex = rowIndexMap.get(rowKey)!
                filteredTable[rowIndex][columnName] = row[columnName]
            })
        })
        filteredTables.push(filteredTable)
    })

    return filteredTables
}

export const getTableFromFile = (file: File): Promise<TableRow[]> => {
    return new Promise((resolve, reject) => {
        Papa.parse(file, {
            header: true,
            dynamicTyping: true,
            complete: (result) => {
                try {
                    const safeData = result.data as { [key: string]: unknown }[]
                    const typedData = safeData.map((row) => {
                        const typedRow: TableRow = {}
                        Object.entries(row).forEach(([key, value]) => {
                            if (
                                typeof value === 'string' ||
                                typeof value === 'number' ||
                                typeof value === 'boolean'
                            ) {
                                typedRow[key] = value
                            } else {
                                if (value !== null) {
                                    typedRow[key] = String(value)
                                } else {
                                    typedRow[key] = ''
                                }
                            }
                        })
                        return typedRow
                    })
                    resolve(typedData)
                } catch (error) {
                    reject(error)
                }
            },
            skipEmptyLines: true,
            error: (error) => {
                reject(error)
            },
        })
    })
}

export const saveToFile = (data: string, type: 'json' | 'csv', filename: string) => {
    const blob = new Blob([data], { type: `application/${type}` })

    const url = URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = filename

    document.body.appendChild(a)
    a.click()

    document.body.removeChild(a)
    URL.revokeObjectURL(url)
}

export const saveBlobAsFile = (blob: Blob, filename: string) => {
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

export const fileToDataUri = (file: File): Promise<string> => {
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
