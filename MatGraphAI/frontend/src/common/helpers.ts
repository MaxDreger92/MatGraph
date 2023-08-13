import {
  INode,
  IConnection
} from "../components/canvas/types/canvas.types"

/**
 * Map a node type from the application's internal format to the desired output format.
 * 
 * @param type Node type from the application
 * @returns Corresponding node type for the JSON structure
 */
function mapNodeType(type: string): string {
  switch (type) {
    case 'matter':
      return 'EMMOMatter';
    case 'manufacturing':
      return 'EMMOProcess';
    case 'measurement':
      return 'EMMOProcess';
    case 'parameter':
      return 'EMMOQuantity';
    case 'property':
      return 'EMMOQuantity';
    default:
      return 'UnknownType';
  }
}

/**
 * Determines the relationship type based on the start and end node types.
 * 
 * @param startType Starting node's type
 * @param endType Ending node's type
 * @returns Corresponding relationship type for the connection
 */
function determineRelationshipType(startType: string, endType: string): string {
  const connectionToRelType: Record<string, string> = {
    'matter-manufacturing': 'IS_MANUFACTURING_INPUT',
    'manufacturing-matter': 'IS_MANUFACTURING_OUTPUT',
    'matter-measurement': 'IS_MEASUREMENT_INPUT',
    'matter-property': 'HAS_PROPERTY',
    'manufacturing-parameter': 'HAS_PARAMETER',
    'measurement-property': 'IS_MEASUREMENT_OUTPUT'
  };

  return connectionToRelType[`${startType}-${endType}`] || 'UNKNOWN_RELATIONSHIP';
}

export function convertToJSONFormat(nodes: INode[], connections: IConnection[]): string {
  // Convert connections into a map for easier lookup, and include the entire connection
  const connectionMap = connections.reduce((acc, connection) => {
    // Capture relationships where the node is the start point
    if (!acc[connection.start.id]) {
      acc[connection.start.id] = [];
    }
    acc[connection.start.id].push(connection);

    // Capture relationships where the node is the end point
    if (!acc[connection.end.id]) {
      acc[connection.end.id] = [];
    }
    acc[connection.end.id].push(connection);

    return acc;
  }, {} as Record<string, IConnection[]>);

  return JSON.stringify(nodes.map(node => {
    const relationships = (connectionMap[node.id] || []).map(connection => ({
      rel_type: determineRelationshipType(connection.start.type, connection.end.type),
      connection: [connection.start.id, connection.end.id] as [string, string]
    }));
    return {
      id: node.id,
      name: node.name || '',
      type: mapNodeType(node.type),
      relationships
    };
  }), null, 2);
}


/**
 * Determine if a connection between two nodes is allowed.
 * 
 * @param start Starting node
 * @param end Ending node
 * @returns true if the connection is legitimate, false otherwise
 */
export function isConnectionLegitimate(start: INode, end: INode): boolean {
  const allowedConnections: Array<[string, string]> = [
    ['matter', 'manufacturing'], // IS_MANUFACTURING_INPUT
    ['manufacturing', 'matter'], // IS_MANUFACTURING_OUTPUT
    ['matter', 'measurement'], // IS_MEASUREMENT_INPUT
    ['matter', 'property'], // HAS_PROPERTY
    ['manufacturing', 'parameter'], // HAS_PARAMETER
    ['measurement', 'property'], // IS_MEASUREMENT_OUTPUT
  ];

  // Check if the [start.type, end.type] tuple exists in the allowed connections array
  return allowedConnections.some(connection => 
    connection[0] === start.type && connection[1] === end.type
  );
}

export function saveToFile(data: string, type: "json" | "csv", filename: string) {
  // Convert the data to a JSON string
  //const jsonString = JSON.stringify(data, null, 2);  // 2 spaces for indentation

  // Create a blob with the JSON string
  const blob = new Blob([data], { type: `application/${type}` });

  // Create a URL for the blob
  const url = URL.createObjectURL(blob);

  // Create an anchor element and set its href to the blob's URL
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;

  // Simulate a click on the anchor element
  document.body.appendChild(a);
  a.click();

  // Clean up by removing the anchor element and revoking the blob URL
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}