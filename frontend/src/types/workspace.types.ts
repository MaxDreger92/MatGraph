export interface IWorkflow {
    _id: string
    workflow: string
    timestamp: Date
}

export interface IUpload {
    _id: string
    progress: number
    fileLink?: string
    fileName?: string
    context?: string
    csvTable: string // TableRow[]
    labelDict?: string // IDictionary
    attributeDict?: string // IDictionary
    workflow?: string
    timestamp: Date
    processing: boolean
}

export type UploadListItem = {
    _id: string
    timestamp: Date
    processing: boolean
}

export interface ITempNode {
    id: string
    attributes: { [key: string]: any }
    label: Label
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
    label: Label
    name: any
    attributes: { [key: string]: ParsableAttribute }
}

export interface IRelationship {
    rel_type: string
    connection: [string, string]
}

export type ParsableAttribute = Attribute | Attribute[]

export type Attribute = {
    value: string
    operator?: string
    index?: number | string | number[] | string[]
}

export interface IDictionary {
    [key: string]: { [key: string]: string }
}

export type TableRow = {
    [key: string]: string | number | boolean
}

export type Label =
    | 'matter'
    | 'manufacturing'
    | 'measurement'
    | 'parameter'
    | 'property'
    | 'metadata'
