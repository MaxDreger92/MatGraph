import { ILabware } from '../types/labware.types'
import { ChemicalEntry } from '../types/chemicals.types'

export function getLabwareData(data: any): ILabware {
    return JSON.parse(data) as ILabware
}

export const generateLabwareWells = (rows: number, cols: number): { [key: string]: ChemicalEntry | null } => {
    const wells: { [key: string]: ChemicalEntry | null } = {}
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
