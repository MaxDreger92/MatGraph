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

export interface OpentronsSetup {
    labware: Labware[]
    pipettes?: Pipette[]
}
