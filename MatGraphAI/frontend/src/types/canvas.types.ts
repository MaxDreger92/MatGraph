export interface Size {
  width: number
  height: number
}

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

export type Operator = "<" | "<=" | "=" | "!=" | ">=" | ">"

export interface NumOpPair {
  number?: number[]
  operator?: Operator
}

export interface ValOpPair {
  value: string
  operator: Operator | string
}

export interface INode {
  id: string
  name: string // obligatory in json for all nodes
  value: ValOpPair // obligatory in json for property/parameter nodes
  batch_num: string
  ratio: ValOpPair
  concentration: ValOpPair
  unit: string
  std: ValOpPair
  error: ValOpPair
  type: "matter" | "manufacturing" | "measurement" | "parameter" | "property" | "metadata"
  position: {x: number, y: number}
  size: number
  layer: number
  isEditing: boolean
  index?: number
}

export interface IRelationship {
  start: INode
  end: INode
  id: string
}

export interface IDRelationship {
  start: string
  end: string
}

export interface ICanvasButton {
  type: "undo" | "redo" | "reset" | "layout" | "saveWorkflow"
}