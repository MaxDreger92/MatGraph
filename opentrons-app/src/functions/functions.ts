// data must be defined!!
export const asList = (data: unknown) => {
    if (Array.isArray(data)) {
        return data
    } else {
        return [data]
    }
}