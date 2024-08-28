import { ObjectId } from "mongodb";

export type Graph = {
    _id?: ObjectId
    userId?: ObjectId
    name?: string
    graph: string
    timestamp: Date
}

export type Upload = {
    _id?: ObjectId
    userId: ObjectId
    progress: number
    fileId: string
    fileName: string
    context?: string | null
    csvTable: string // TableRow[]
    labelDict?: string | null // IDictionary
    attributeDict?: string | null // IDictionary
    graph?: string | null
    timestamp: Date
    processing: boolean
}