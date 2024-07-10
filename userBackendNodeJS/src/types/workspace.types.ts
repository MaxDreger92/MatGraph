import { ObjectId } from "mongodb";

export type Graph = {
    _id?: ObjectId
    userId?: ObjectId
    graph: string
    timestamp: Date
}

export type Upload = {
    _id?: ObjectId
    userId?: ObjectId
    progress?: number
    fileId?: string
    context?: string
    csvTable?: string // TableRow[]
    labelDict?: string // IDictionary
    attributeDict?: string // IDictionary
    graph?: string
    timestamp: Date
    processing: boolean
}