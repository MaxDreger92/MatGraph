export function clamp(value: number, min: number, max: number) {
    return Math.min(Math.max(value, min), max)
}

export function splitStrBySemicolon(str: string): string | string[] {
    const splitStrings = str
        .split(';')
        .map((s) => s.trim())
        .filter((s) => s !== '')
    return splitStrings.length === 1 ? splitStrings[0] : splitStrings
}

export function tryNumeric(str: string): string | number {
    const numeric = parseFloat(str)
    const typed = isNaN(numeric) ? str : numeric
    return typed
}

export const ensureArray = (item: any): any[] => {
    if (Array.isArray(item)) {
        return item
    } else {
        return [item]
    }
}