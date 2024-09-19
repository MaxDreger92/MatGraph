import { ILabware } from '../types/labware.types'
import { isILabware } from '../schemas/labware.schema'
import { Chemical } from '../types/configuration.types'

export const createOpentronsSetupLabware = (slot: number, labware: ILabware) => {
    if (!isILabware(labware)) return 
    return {
        slot: slot,
        name: labware.parameters.loadName,
        filename: labware.filename,
        namespace: labware.namespace,
        version: labware.version,
        intent: 'setup'
    }
}

export const findLabwareByName = (labwareList: ILabware[], key: string): ILabware | undefined => {
    let labware = labwareList.find((item) => key === item.parameters.loadName)
    if (!labware) {
        labware = labwareList.find((item) => key === item.metadata.displayName)
    }
    return labware
}

export const getLabwareData = (data: any, filename: string): ILabware => {
    try {
        const parsedData = {...JSON.parse(data), filename}
        if (isILabware(parsedData)) {
            return parsedData
        } else {
            throw Error
        }
    } catch (err: any) {
        throw Error
    }
}

export const generateLabwareWells = (rows: number, cols: number): { [key: string]: Chemical[] | null } => {
    const wells: { [key: string]: Chemical[] | null } = {}
    const rowLabels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.slice(0, rows)

    rowLabels.split('').forEach((row) => {
        for (let col = 1; col <= cols; col++) {
            const slotId = `${row}${col}`
            wells[slotId] = null
        }
    })

    return wells
}

export const transposeOrdering = (ordering: string[][]): string[][] => {
    const rows = ordering.length
    const cols = ordering[0].length

    const transposed: string[][] = Array.from({ length: cols }, () => new Array<string>(rows))

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            transposed[j][i] = ordering[i][j]
        }
    }

    return transposed
}

export const transposeWells = (wells: ILabware['wells']): ILabware['wells'] => {
    const wellKeys = Object.keys(wells)

    const sortedKeys = wellKeys.sort((a, b) => {
        const [aRow, aCol] = [a.charAt(0), parseInt(a.slice(1), 10)]
        const [bRow, bCol] = [b.charAt(0), parseInt(b.slice(1), 10)]

        if (aRow < bRow) return -1
        if (aRow > bRow) return 1

        return aCol - bCol
    })

    const sortedWells: ILabware['wells'] = {}
    sortedKeys.forEach((key) => {
        sortedWells[key] = wells[key]
    })

    return sortedWells
}
