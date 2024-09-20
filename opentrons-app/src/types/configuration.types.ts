export const DefaultConfiguration: Configuration = {
    opentronsSetup: {
        name: '',
        labware: [],
        pipettes: []
    },
    chemicalSetup: {
        name: '',
        opentrons: [],
        arduino: []
    }
}

export interface Configuration {
    opentronsSetup: OpentronsSetup
    chemicalSetup: ChemicalSetup
}

export interface OpentronsSetup {
    name?: string
    labware: Labware[]
    pipettes?: Pipette[]
}

interface Labware {
    slot: number
    name: string
    filename: string
    namespace: string
    version: number
    intent: string
}

interface Pipette {
    mount: string
    name: string
    intent: string
}

export interface ChemicalSetup {
    name?: string
    opentrons: Chemical[]
    arduino: Chemical[]
}

export interface Chemical {
    location: Location
    name: string
    volume: Volume
}

interface Location {
    slot: number 
    well: string 
}

interface Volume {
    value: number 
    unit: string 
}