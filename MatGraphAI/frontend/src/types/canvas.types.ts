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
  name: {value: string, index?: any}
  value: {value: ValOpPair, index?: any}
  batch_num: {value: string, index?: any}
  ratio: {value: ValOpPair, index?: any}
  concentration: {value: ValOpPair, index?: any}
  unit: {value: string, index?: any}
  std: {value: ValOpPair, index?: any}
  error: {value: ValOpPair, index?: any}
  identifier: {value: string, index?: any}
  type: "matter" | "manufacturing" | "measurement" | "parameter" | "property" | "metadata"
  position: {x: number, y: number}
  size: number
  layer: number
  isEditing: boolean
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