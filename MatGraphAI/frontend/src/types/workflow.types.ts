import { Operator, Position } from "./canvas.types"

export type ParsedValOpPair = {
  value: string | string[]
  operator: Operator
}

export interface IWorkflow {
  _id: string
  workflow: string
  timestamp: Date
}

export interface ITempNode {
  id: string
  attributes: { [key: string]: any }
  type: "matter" | "manufacturing" | "measurement" | "parameter" | "property" | "metadata"
  relationships: Array<{
    rel_type: string
    connection: [string, string]
  }>
  index?: number
}

export interface IOuterDictionary {
  [key: string]: IInnerDictionary
}

export interface IInnerDictionary {
  [key: string]: string
}