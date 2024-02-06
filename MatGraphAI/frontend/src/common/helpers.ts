import { PiAddressBookDuotone } from "react-icons/pi"
import {
  INode,
  IRelationship,
  IDRelationship,
  ValOpPair,
  Operator,
  NodeAttribute,
  NodeValOpAttribute,
  NodeIndex,
} from "../types/canvas.types"
import { IGraphData, ITempNode, ExtractedAttribute, CustomAttribute, ParsableAttributes } from "../types/workflow.types"
import toast from "react-hot-toast"
import client from "../client"
import { v4 as uuidv4 } from "uuid"
import React, { useRef } from "react"
import { valueGetters } from "@mantine/core/lib/Box/style-system-props/value-getters/value-getters"

const relationshipToRelType: Record<string, string> = {
  "matter-manufacturing": "IS_MANUFACTURING_INPUT",
  "manufacturing-matter": "IS_MANUFACTURING_OUTPUT",
  "matter-measurement": "IS_MEASUREMENT_INPUT",
  "matter-property": "HAS_PROPERTY",
  "manufacturing-parameter": "HAS_PARAMETER",
  "measurement-property": "IS_MEASUREMENT_OUTPUT",
  "manufacturing-metadata": "HAS_METADATA",
  "measurement-metadata": "HAS_METADATA",
}

/**
 * Map a node type from the application's internal format to the desired output format.
 *
 * @param type Node type from the application
 * @returns Corresponding node type for the JSON structure
 */
function mapNodeType(type: string): string {
  switch (type) {
    case "matter":
      return "EMMOMatter"
    case "manufacturing":
      return "EMMOProcess"
    case "measurement":
      return "EMMOProcess"
    case "parameter":
      return "EMMOQuantity"
    case "property":
      return "EMMOQuantity"
    case "metadata":
      return "EMMOData"
    default:
      return "UnknownType"
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
  return (
    relationshipToRelType[`${startType}-${endType}`] || "UNKNOWN_RELATIONSHIP"
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
    return ["matter", "manufacturing", "parameter", "property", "measurement", "metadata"]

  // Filter the keys to find matches and extract the endType
  return Object.keys(relationshipToRelType)
    .filter((key) => key.startsWith(`${startType}-`))
    .map((key) => key.split("-")[1])
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
  return Object.keys(relationshipToRelType).some((key) =>
    key.startsWith(`${nodeType}-`)
  )
}

function isValidOperator(operator: string): boolean {
  return operator === "<" || operator === "<=" ||
  operator === "=" || operator === "!=" ||
  operator === ">=" || operator === ">"
}

export function isAttrDefined(attribute: string | ValOpPair): boolean {
  if (typeof attribute === 'string') {
    return attribute !== "";
  } else if (typeof attribute === 'object' && 'value' in attribute) {
    // Check if 'string' and 'operator' are defined and valid
    const isStringDefined = typeof attribute.value === 'string' && attribute.value !== "";
    const isOperatorValid = isValidOperator(attribute.operator)

    // StrOpPair is valid if both 'string' and 'operator' are valid
    return isStringDefined && isOperatorValid;
  }  
  return false;
}

function parseAttrOut(attribute: string | ValOpPair, index?: NodeIndex | NodeIndex[]): ParsableAttributes {
  let stringToParse = "";

  // Determine the string to parse based on the type of attribute
  if (typeof attribute === 'string') {
    stringToParse = attribute;
  } else if ('value' in attribute && typeof attribute.value === 'string') {
    stringToParse = attribute.value;
  }

  // Split the string by semicolons
  const splitStrings = stringToParse.split(';').map(s => s.trim()).filter(s => s !== "");
  const parsedString = splitStrings.length === 1 ? splitStrings[0] : splitStrings;

  if (index === undefined) {
    if (typeof attribute === 'string') {
      return { value: parsedString } as CustomAttribute
    } else {
      return {value: parsedString, operator: attribute.operator as Operator} as CustomAttribute 
    }
  } else {
    if (typeof parsedString === 'string' && !Array.isArray(index)) {
      return { value: parsedString, index: index } as ExtractedAttribute
    } else {
      if (Array.isArray(parsedString) && Array.isArray(index)) {
        return parsedString.map((s, i) => ({ value: s, index: index[i] })) as ExtractedAttribute[]
      } else {
        return { value: "ERROR_PARSING_EXTRACTED_ATTR" } as CustomAttribute
      }
    }
  }
}

// function parseAttr(attribute: any, valOp: boolean): { value: any, index?: any[] } {
//   // Function to process the attribute when it's not an {value, operator} object
//   const processAttributeValue = (attr: any) => {
//     if (typeof attr === 'string') {
//       return { value: attr };
//     } else if (Array.isArray(attr)) {
//       if (typeof attr[0] === 'string') {
//         return { value: attr.join(';') };
//       } else {
//         let values: string[] = [];
//         let indices: any[] = [];
//         attr.forEach(item => {
//           if (typeof item.value === 'string') {
//             values.push(item.value);
//             if (item.index !== undefined) {
//               indices.push(item.index);
//             }
//           }
//         });
//         return { value: values.join(';'), index: indices.length > 0 ? indices : undefined };
//       }
//     } else {
//       return { value: '', index: undefined };
//     }
//   };

//   // Check for the additional case where attribute is an object with {value, operator}
//   if (typeof attribute === 'object' && !Array.isArray(attribute) && attribute !== null) {
//     const processedValue = processAttributeValue(attribute.value);
//     const op = attribute.operator ? attribute.operator : '='
//     return {
//       value: { value: processedValue.value, operator: op },
//       index: processedValue.index
//     }
//   } else if (attribute !== undefined) {
//     // Process attribute using the previously defined logic
//     return processAttributeValue(attribute);
//   }
//   if (valOp) {
//     return {value: {value: "", operator: ""}}
//   }
//   return {value: ""}
// }

function parseAttr(attribute: ParsableAttributes | undefined, isValOp: boolean): NodeAttribute | NodeValOpAttribute {
  if (attribute === undefined) {
    if (isValOp) {
      return { value: {value: '', operator: ''} } as NodeValOpAttribute
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

function parseExtractedAttribute(attribute: ExtractedAttribute | ExtractedAttribute[], isValOp: boolean): NodeAttribute | NodeValOpAttribute {
  // if (Array.isArray(attribute)) {
  //   console.log("Array: ")
  //   attribute.forEach(item => {
  //     console.log(item.index)
  //   })
  //   console.log("ArrayEnd")
  // } else {
  //   console.log(attribute.index)
  // }
  if (Array.isArray(attribute)) {
    let values: string[] = []
    let indices: NodeIndex[] = []
    attribute.forEach(item => {
      values.push(item.value)
      indices.push(item.index)
    })
    const finalIndex = indices.length > 1 ? indices : indices[0]
    if (isValOp) {
      return { value: {value: values.join(';'), operator: '=' as Operator}, index: finalIndex } as NodeValOpAttribute
    } else {
      return { value: values.join(';'), index: finalIndex} as NodeAttribute
    }
  } else {
    if (isValOp) {
      return { value: {value: attribute.value, operator: '=' as Operator}, index: attribute.index } as NodeValOpAttribute
    } else {
      return { value: attribute.value, index: attribute.index} as NodeAttribute
    }
  }
}

function parseCustomAttribute(attribute: CustomAttribute, isValOp: boolean): NodeAttribute | NodeValOpAttribute {
  if (Array.isArray(attribute.value)) {
    if (isValOp) {
      const op = attribute.operator ? attribute.operator : '=' as Operator
      return { value: {value: attribute.value.join(';'), operator: op} } as NodeValOpAttribute
    } else {
      return { value: attribute.value.join(';') } as NodeAttribute
    }
  } else {
    if (isValOp) {
      const op = attribute.operator ? attribute.operator : '=' as Operator
      return { value: {value: attribute.value, operator: op} } as NodeValOpAttribute
    } else {
      return { value: attribute.value } as NodeAttribute
    }
  }
}

export function convertToJSONFormat(
  nodes: INode[],
  relationships: IRelationship[],
  preventMapTypes?: boolean,
): string {
  // Convert relationships into a map for easier lookup
  const relationshipMap = relationships.reduce((acc, relationship) => {
    // Capture relationships where the node is the start point
    if (!acc[relationship.start.id]) {
      acc[relationship.start.id] = [];
    }
    acc[relationship.start.id].push(relationship);

    // Capture relationships where the node is the end point
    if (!acc[relationship.end.id]) {
      acc[relationship.end.id] = [];
    }
    acc[relationship.end.id].push(relationship);

    return acc;
  }, {} as Record<string, IRelationship[]>);

  const processedNodes =
    nodes.map((node) => {
      // Group all attributes under an attributes object
      const attributes: { [key: string]: ParsableAttributes } = {};
      if (isAttrDefined(node.name.value)) {
        attributes.name = parseAttrOut(node.name.value, node.name.index)
      } else {
        attributes.name = { value: "MISSING_NAME" }
      }
      if (isAttrDefined(node.value.value)) {
        attributes.value = parseAttrOut(node.value.value, node.value.index)
      } else if (["property","parameter"].includes(node.type)) {
        attributes.value = { value: "MISSING_VALUE_OR_OPERATOR" }
      } 
      if (isAttrDefined(node.batch_num.value)) attributes.batch_num = parseAttrOut(node.batch_num.value, node.batch_num.index);
      if (isAttrDefined(node.unit.value)) attributes.unit = parseAttrOut(node.unit.value, node.unit.index);
      if (isAttrDefined(node.ratio.value)) attributes.ratio = parseAttrOut(node.ratio.value, node.ratio.index);
      if (isAttrDefined(node.concentration.value)) attributes.concentration = parseAttrOut(node.concentration.value, node.concentration.index);
      if (isAttrDefined(node.std.value)) attributes.std = parseAttrOut(node.std.value, node.std.index);
      if (isAttrDefined(node.error.value)) attributes.error = parseAttrOut(node.error.value, node.error.index);
      if (isAttrDefined(node.identifier.value)) attributes.identifier = parseAttrOut(node.identifier.value, node.identifier.index)

      // Return the node object with id, type, attributes, and relationships
      return {
        id: node.id,
        name: attributes.name,
        label: preventMapTypes ? node.type : mapNodeType(node.type),
        attributes,
      };
    })

  const processedRelationships = relationships.map((relationship) => ({
    rel_type: determineRelationshipType(relationship.start.type, relationship.end.type), // Assume this function is defined elsewhere
    connection: [relationship.start.id, relationship.end.id],
  }))

  const finalStructure = {
    nodes: processedNodes,
    relationships: processedRelationships,
  };

  return JSON.stringify(finalStructure, null, 2);
}

export function convertFromJsonFormat(workflow: string) {
  const data: IGraphData = JSON.parse(workflow)
  const nodes: INode[] = []
  const relationships: IRelationship[] = []

  console.log('read everything')

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
      position: { x: -100, y: -100 },
      size: 100,
      layer: 0,
      isEditing: false,
    })
  })

  data.relationships.forEach((rel) => {
    const [sourceNodeId, targetNodeId] = [rel.connection[0], rel.connection[1]]
    const start = nodes.find((node) => node.id === sourceNodeId)
    const end = nodes.find((node) => node.id === targetNodeId)

    if (start && end) {
      const id = uuidv4().replaceAll("-", "")
      relationships.push({ start, end, id })
    }
  })

  return {
    nodes,
    relationships: relationships,
  }
}

/**
 * Determine if a relationship between two nodes is allowed.
 *
 * @param start Starting node
 * @param end Ending node
 * @returns true if the relationship is legitimate, false otherwise
 */
export function isRelationshipLegitimate(start: INode, end: INode): boolean {
  const allowedRelationships: Array<[string, string]> = [
    ["matter", "manufacturing"], // IS_MANUFACTURING_INPUT
    ["manufacturing", "matter"], // IS_MANUFACTURING_OUTPUT
    ["matter", "measurement"], // IS_MEASUREMENT_INPUT
    ["matter", "property"], // HAS_PROPERTY
    ["manufacturing", "parameter"], // HAS_PARAMETER
    ["measurement", "property"], // IS_MEASUREMENT_OUTPUT
    ["manufacturing", "metadata"], // HAS_METADATA
    ["measurement", "metadata"], // HAS_METADATA
  ]

  // Check if the [start.type, end.type] tuple exists in the allowed relationships array
  return allowedRelationships.some(
    (relationship) => relationship[0] === start.type && relationship[1] === end.type
  )
}

// export async function saveToHistory(workflow: string) {
//   // create timestamp
//   // save to history -> backend (workflow + timestamp)
//   try {
//     const response = await client.saveWorkflow(workflow)

//     if (response) {
//       toast.success(response.data.message)
//     }
//   } catch (err: any) {
//     toast.error(err.message)
//   }
// }

export function saveToFile(
  data: string,
  type: "json" | "csv",
  filename: string
) {
  // Convert the data to a JSON string
  //const jsonString = JSON.stringify(data, null, 2);  // 2 spaces for indentation

  // Create a blob with the JSON string
  const blob = new Blob([data], { type: `application/${type}` })

  // Create a URL for the blobn
  const url = URL.createObjectURL(blob)

  // Create an anchor element and set its href to the blob's URL
  const a = document.createElement("a")
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
    console.error("Provided data is not a Blob")
    return
  }
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement("a")
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

export function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

export function useAutoIncrementRefs() {
  const refs = useRef<React.RefObject<HTMLInputElement>[]>([])
  const getNewRef = () => {
    const newRef = React.createRef<HTMLInputElement>()
    refs.current.push(newRef)
    return newRef
  }

  return { getNewRef, refs: refs.current }
}