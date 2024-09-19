export interface IWell {
    depth: number
    totalLiquidVolume: number
    shape: string
    diameter?: number 
    xDimension?: number
    yDimension?: number
    x: number
    y: number
    z: number
}

interface Metadata {
    displayName: string
    displayCategory: string
    displayVolumeUnits: string
    tags: string[]
}

interface Dimensions {
    xDimension: number
    yDimension: number
    zDimension: number
}

interface GroupMetadata {
    wellBottomShape?: string
}

interface Group {
    metadata: GroupMetadata
    wells: string[]
}

interface LabwareParameters {
    format: string
    quirks: string[]
    isMagneticModuleCompatible: boolean
    loadName: string
    tipLength?: number 
}

interface CornerOffsetFromSlot {
    x: number
    y: number
    z: number
}

interface Brand {
    brand: string
    brandId: string[]
}

export interface ILabware {
    ordering: string[][]
    brand: Brand
    metadata: Metadata
    dimensions: Dimensions
    wells: Record<string, IWell> 
    groups: Group[]
    parameters: LabwareParameters
    namespace: string
    version: number
    schemaVersion: number
    cornerOffsetFromSlot: CornerOffsetFromSlot
    filename: string
}
