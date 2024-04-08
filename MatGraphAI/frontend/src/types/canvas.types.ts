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
  type: NodeType
  with_indices: boolean
  position: Position
  size: number
  optimalSize: number
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
  index?: AttributeIndex | AttributeIndex[]
}

export type NodeValOpAttribute = {
  valOp: ValOpPair
  index?: AttributeIndex | AttributeIndex[]
}

export type ValOpPair = {
  value: string
  operator: Operator | string
}

export type AttributeIndex = number | string

export type NodeType = "matter" | "manufacturing" | "measurement" | "parameter" | "property" | "metadata"

export type IndexDictionary = {
    [index: number]: string[]
}