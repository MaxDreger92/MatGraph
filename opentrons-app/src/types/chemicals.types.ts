export interface IChemicals {
    opentrons: ChemicalEntry[] 
}

export interface ChemicalEntry {
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
