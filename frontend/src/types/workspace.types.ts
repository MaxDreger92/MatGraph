export type Graph = {
    _id: string
    name?: string
    graph: string
    timestamp: Date
}

export type Upload = {
    _id: string
    name?: string
    progress: number
    fileId: string
    fileName: string
    context?: string | null
    csvTable: string // TableRow[]
    labelDict?: string | null // IDictionary
    attributeDict?: string | null // IDictionary
    graph?: string | null
    timestamp: Date
    processing: boolean
}

export type UploadListItem = {
    _id: string
    timestamp: Date
    processing: boolean
}

export type TempNode = {
    id: string
    attributes: { [key: string]: any }
    label: Label
    relationships: Array<{
        rel_type: string
        connection: [string, string]
    }>
}

export type GraphData = {
    nodes: GraphNode[]
    relationships: Relationship[]
}

export type GraphNode = {
    id: string
    label: Label
    name: any
    attributes: { [key: string]: ParsableAttribute }
}

export type Relationship = {
    rel_type: string
    connection: [string, string]
}

export type ParsableAttribute = Attribute | Attribute[]

export type Attribute = {
    value: string
    operator?: string
    index?: number | string | number[] | string[]
}

export type Dictionary = {
    [key: string]: any[]
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
