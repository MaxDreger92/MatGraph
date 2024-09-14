import { isOpentronsSetup } from "../schemas/opentrons_setup.schema"
import { OpentronsSetup } from "../types/opentrons.types"

export const getOpentronsSetupData = (data: any): OpentronsSetup => {
    try {
        const parsedData = JSON.parse(data)
        if (isOpentronsSetup(parsedData)) {
            return parsedData
        } else {
            throw Error
        }
    } catch (err: any) {
        throw err
    }
}

export const isLabwareInSlot = (setup: OpentronsSetup, slot: number): boolean => {
    return setup.labware.some(labware => labware.slot === slot)
}

export const getLabwareNameBySlot = (setup: OpentronsSetup, slot: number): string | undefined => {
    const labware = setup.labware.find((item) => item.slot === slot)
    return labware ? labware.name : undefined
}