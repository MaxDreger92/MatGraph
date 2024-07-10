export type Graph = {
    _id: string
    data: string
    timestamp: Date
}

export type Upload = {
    _id: string
    name?: string
    progress: number
    fileId?: string
    context?: string
    csvTable: string // TableRow[]
    labelDict?: string // IDictionary
    attributeDict?: string // IDictionary
    graph?: string
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
