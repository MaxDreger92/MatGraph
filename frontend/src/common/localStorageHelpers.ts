export const setLocalStorageItem = (key: string, value: any) => {
    localStorage.setItem(key, JSON.stringify(value))
}

export const getLocalStorageItem = (key: string) => {
    const rawValue = localStorage.getItem(key)
    if (!rawValue) return
    return JSON.parse(rawValue)
}