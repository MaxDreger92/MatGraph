import { ObjectId } from "mongodb";

export type Workflow = {
    _id?: ObjectId
    userId?: ObjectId
    workflow: string
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
    workflow?: string
    timestamp: Date
    processing: boolean
}