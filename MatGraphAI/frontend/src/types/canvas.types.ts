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

// export interface NumOpPair {
//   number?: number[]
//   operator?: Operator
// }

export interface INode {
  id: string
  name: NodeAttribute
  value: NodeValOpAttribute
  batch_num: NodeAttribute
  ratio: NodeValOpAttribute
  concentration: NodeValOpAttribute
  unit: NodeAttribute
  std: NodeValOpAttribute
  error: NodeValOpAttribute
  identifier: NodeAttribute
  type: "matter" | "manufacturing" | "measurement" | "parameter" | "property" | "metadata"
  position: {x: number; y: number}
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

export type NodeAttribute = {
  value: string
  index?: NodeIndex | NodeIndex[]
}

export type NodeValOpAttribute = {
  value: ValOpPair
  index?: NodeIndex | NodeIndex[]
}

export type ValOpPair = {
  value: string
  operator: Operator | string
}

export type NodeIndex = number | string