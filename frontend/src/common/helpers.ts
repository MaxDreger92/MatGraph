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

export function splitStrByLength(str: string | string[], len: number): string | string[] {
    const splitter = (s: string) => {
        const chunks = [];
        for (let i = 0; i < s.length; i += len) {
            chunks.push(s.substring(i, i + len));
        }
        return chunks;
    };

    if (Array.isArray(str)) {
        // Flatten the array of strings after splitting each one.
        return str.reduce<string[]>((acc, item) => acc.concat(splitter(item)), []);
    } else {
        const result = splitter(str);
        return result.length === 1 ? result[0] : result;
    }
}

export function getTypedIndex(index: string): string | number {
    const numericIndex = parseFloat(index)
    const typedIndex = isNaN(numericIndex) ? index : numericIndex
    return typedIndex
}