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

export function getTypedIndex(index: string): string | number {
    const numericIndex = parseFloat(index)
    const typedIndex = isNaN(numericIndex) ? index : numericIndex
    return typedIndex
}