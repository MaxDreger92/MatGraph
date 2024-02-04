import { Operator, Position } from "./canvas.types"

export type ParsedValOpPair = {
  value: string | string[] | string[][]
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
}

export interface IGraphData {
  nodes: IGraphNode[]
  relationships: IRelationship[]
}

export interface IGraphNode {
  id: string
  label: "matter" | "manufacturing" | "measurement" | "parameter" | "property" | "metadata"
  name: string[]
  attributes: { [key: string]: any }
}

export interface IRelationship {
  rel_type: string
  relationship: [string, string]
}

export interface IDictionary {
  [key: string]: {[key: string]: string}
}