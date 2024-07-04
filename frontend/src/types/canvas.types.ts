export type Size = {
    width: number
    height: number
}

export type Position = {
    x: number
    y: number
}

export type Vector2D = {
    x: number
    y: number
}

export type Rect = {
    top: number
    right?: number
    bottom?: number
    left: number
    width: number
    height: number
}

export type Operator = '<' | '<=' | '=' | '!=' | '>=' | '>'

export type TNode = {
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
    withIndices: boolean
    position: Position
    size: number
    optimalSize: number
    layer: number
    isEditing: boolean
}

export type TRelationship = {
    start: TNode
    end: TNode
    id: string
}

export type IDRelationship = {
    start: string
    end: string
}

export type TCanvasButton = {
    type: 'undo' | 'redo' | 'reset' | 'layout' | 'saveWorkflow'
}

export type NodeAttribute = {
    value: string
    index?: string
}

export type NodeValOpAttribute = {
    valOp: ValOpPair
    index?: string
}

export type ValOpPair = {
    value: string
    operator: Operator | string
}

export type NodeType =
    | 'matter'
    | 'manufacturing'
    | 'measurement'
    | 'parameter'
    | 'property'
    | 'metadata'
    | 'simulation'

export type IndexDictionary = {
    [index: number]: string[]
}
