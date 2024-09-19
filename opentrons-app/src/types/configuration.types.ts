export const DefaultConfiguration: Configuration = {
    opentronsSetup: {
        labware: [],
        pipettes: []
    },
    chemicalSetup: {
        opentrons: [],
        arduino: []
    }
}

export interface Configuration {
    opentronsSetup: OpentronsSetup
    chemicalSetup: ChemicalSetup
}

export interface OpentronsSetup {
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