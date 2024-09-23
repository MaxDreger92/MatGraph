import { isChemicalSetup, isOpentronsSetup } from "../schemas/configuration.schema"
import { ChemicalSetup, OpentronsSetup } from "../types/configuration.types"

export const sortSetupListByName = (setupList: OpentronsSetup[] | ChemicalSetup[]) => {
    const sortedSetupList = [...setupList].sort((setupA, setupB) => {

        const nameA = setupA.name.toLowerCase()
        const nameB = setupB.name.toLowerCase()

        if (nameA < nameB) return -1
        if (nameA > nameB) return 1
        return 0
    }) as OpentronsSetup[] | ChemicalSetup[]
    return sortedSetupList
}

export const getOpentronsSetupData = (data: any, name: string): OpentronsSetup | null => {
    try {
        const parsedData = JSON.parse(data)
        if (isOpentronsSetup(parsedData)) {
            const opentronsSetup = parsedData as OpentronsSetup
            opentronsSetup.name = name
            return opentronsSetup
        } else {
            throw Error
        }
    } catch (err: any) {
        return null
    }
}

export const getChemicalSetupData = (data: any, name: string): ChemicalSetup | null => {
    try {
        const parsedData = JSON.parse(data)
        if (isChemicalSetup(parsedData)) {
            const chemicalSetup = parsedData as ChemicalSetup
            chemicalSetup.name = name
            return chemicalSetup
        } else {
            throw Error
        }
    } catch (err: any) {
        return null
    }
}

export const isLabwareInSlot = (setup: OpentronsSetup, slot: number): boolean => {
    return setup.labware.some(labware => labware.slot === slot)
}

export const getLabwareNameBySlot = (setup: OpentronsSetup, slot: number): string | undefined => {
    const labware = setup.labware.find((item) => item.slot === slot)
    return labware ? labware.name : undefined
}