export interface Position {
  x: number
  y: number
}

export interface Vector2D {
  x: number
  y: number
}

export interface Rect {
  top: number
  right?: number
  bottom?: number
  left: number
  width: number
  height: number
}

export interface INode {
  id: string
  name?: string
  value?: number
  operator?: "<" | ">" | "="
  type: "matter" | "manufacturing" | "measurement" | "parameter" | "property"
  position: {x: number, y: number}
  size: number
  layer: number
  isEditing: boolean
}

export interface IConnection {
  start: INode
  end: INode
  id: string
}

export interface IDConnection {
  start: string
  end: string
}

interface RelationshipJSON {
  rel_type: string;
  connection: [string, string];
}

export interface NodeJSON {
  id: string;
  type: string;
  name: string;
  relationships: RelationshipJSON[];
}
