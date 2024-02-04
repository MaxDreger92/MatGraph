import { PiAddressBookDuotone } from "react-icons/pi"
import {
  INode,
  IRelationship,
  IDRelationship,
  ValOpPair,
  Operator,
} from "../types/canvas.types"
import { IGraphData, ITempNode, ParsedValOpPair } from "../types/workflow.types"
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
  } else if (typeof attribute === 'object') {
    // Check if 'string' and 'operator' are defined and valid
    const isStringDefined = typeof attribute.value === 'string' && attribute.value !== "";
    const isOperatorValid = isValidOperator(attribute.operator)

    // StrOpPair is valid if both 'string' and 'operator' are valid
    return isStringDefined && isOperatorValid;
  }  
  return false;
}

function parseAttrOut(attribute: string | ValOpPair): string | string[] | ParsedValOpPair {
  let stringToParse = "";

  // Determine the string to parse based on the type of attribute
  if (typeof attribute === 'string') {
    stringToParse = attribute;
  } else if (typeof attribute.value === 'string') {
    stringToParse = attribute.value;
  }

  // Split the string by semicolons
  const splitStrings = stringToParse.split(';').map(s => s.trim()).filter(s => s !== "");
  const parsedString = splitStrings.length === 1 ? splitStrings[0] : splitStrings;

  if (typeof attribute === 'string') {
    return parsedString;
  } else {
    return {value: parsedString, operator: attribute.operator as Operator}
  }

  // Return a single string if there's only one, otherwise return the array
}

function parseStrAttr(attribute: string | string[] | undefined): string {
  if (typeof attribute === 'string') {
    return attribute
  } else if (Array.isArray(attribute)) {
    return attribute.join(';')
  }
  return ""
}

function parseValOpAttr(attribute: ParsedValOpPair | undefined): ValOpPair {
  if (!attribute) return {value: "", operator: ""}
  if (typeof attribute.value === 'string') {
    return {value: attribute.value, operator: attribute.operator}
  } else if (Array.isArray(attribute.value)) {
    return {value: attribute.value.join(';'), operator: attribute.operator}
  }
  return {value: "", operator: ""}
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

  return JSON.stringify(
    nodes.map((node) => {
      // Group all attributes under an attributes object
      const attributes: { [key: string]: any } = {};
      if (isAttrDefined(node.name)) {
        attributes.name = parseAttrOut(node.name)
      } else {
        attributes.name = "MISSING_NAME"
      }
      if (isAttrDefined(node.value)) {
        attributes.value = parseAttrOut(node.value)
      } else if (["property","parameter"].includes(node.type)) {
        attributes.value = "MISSING_VALUE"
      } 
      if (isAttrDefined(node.batch_num)) attributes.batch_num = parseAttrOut(node.batch_num);
      if (isAttrDefined(node.unit)) attributes.unit = parseAttrOut(node.unit);
      if (isAttrDefined(node.ratio)) attributes.ratio = parseAttrOut(node.ratio);
      if (isAttrDefined(node.concentration)) attributes.concentration = parseAttrOut(node.concentration);
      if (isAttrDefined(node.std)) attributes.std = parseAttrOut(node.std);
      if (isAttrDefined(node.error)) attributes.error = parseAttrOut(node.error);

      // Build relationships
      const relationships = (relationshipMap[node.id] || []).map(
        (relationship) => ({
          rel_type: determineRelationshipType(
            relationship.start.type,
            relationship.end.type
          ),
          connection: [relationship.start.id, relationship.end.id] as [
            string,
            string
          ],
        })
      );

      // Return the node object with id, type, attributes, and relationships
      return {
        id: node.id,
        type: preventMapTypes ? node.type : mapNodeType(node.type),
        attributes,
        relationships,
        ...(node.index && {index: node.index}),
      };
    }),
    null,
    2
  );
}


export function convertFromJSONFormat(workflow: string) {
  const data: ITempNode[] = JSON.parse(workflow)
  const nodes: INode[] = []
  const relationshipMap: Map<string, IDRelationship> = new Map()

  data.forEach((item) => {
    nodes.push({
      id: item.id,
      name: parseStrAttr(item.attributes.name),
      value: parseValOpAttr(item.attributes.value),
      batch_num: parseStrAttr(item.attributes.batch_num),
      ratio: parseValOpAttr(item.attributes.ratio),
      concentration: parseValOpAttr(item.attributes.concentration),
      unit: parseStrAttr(item.attributes.unit),
      std: parseValOpAttr(item.attributes.std),
      error: parseValOpAttr(item.attributes.error),
      type: item.type,
      position: { x: -100, y: -100 },
      size: 100,
      layer: 0,
      isEditing: false,
      index: item.index ? item.index : undefined
    })

    // Reconstruct relationships
    item.relationships.forEach((rel) => {
      // Create a unique key to prevent duplicate relationships
      const relationshipKey = [rel.connection[0], rel.connection[1]]
        .sort()
        .join("_")

      if (!relationshipMap.has(relationshipKey)) {
        relationshipMap.set(relationshipKey, {
          start: rel.connection[0], // Only ID is used here
          end: rel.connection[1], // Only ID is used here
        })
      }
    })
  })

  const relationships: IRelationship[] = Array.from(
    relationshipMap.values()
  ).flatMap((rel) => {
    const startNode = nodes.find((n) => n.id === rel.start)
    const endNode = nodes.find((n) => n.id === rel.end)

    if (!startNode || !endNode) {
      return []
    }

    return [
      {
        start: startNode,
        end: endNode,
        id: uuidv4().replaceAll("-", ""),
      },
    ]
  })

  return {
    nodes,
    relationships: relationships,
  }
}

export function convertFromNewJson(workflow: string) {
  const data: IGraphData = JSON.parse(workflow)
  const nodes: INode[] = []
  const relationships: IRelationship[] = []

  data.nodes.forEach((item) => {
    nodes.push({
      id: item.id,
      name: parseStrAttr(item.attributes.name),
      value: {value: parseStrAttr(item.attributes.value), operator: "="},
      batch_num: parseStrAttr(item.attributes.batch_number),
      ratio: {value: parseStrAttr(item.attributes.ratio), operator: "="},
      concentration: {value: parseStrAttr(item.attributes.concentration), operator: "="},
      unit: parseStrAttr(item.attributes.unit),
      std: {value: parseStrAttr(item.attributes.std), operator: "="},
      error: {value: parseStrAttr(item.attributes.error), operator: "="},
      type: item.label,
      position: { x: -100, y: -100 },
      size: 100,
      layer: 0,
      isEditing: false,
      index: item.index ? item.index : undefined
    })
  })

  data.relationships.forEach((relationship) => {
    const [sourceNodeId, targetNodeId] = relationship.relationship
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