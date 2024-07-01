import { ObjectId } from "mongodb";

export interface IWorkflow {
    _id?: ObjectId
    userId?: ObjectId
    workflow: string
    timestamp: Date
}

export interface IUpload {
    _id?: ObjectId
    userId?: ObjectId
    progress?: number
    fileLink?: string
    fileName?: string
    context?: string
    csvTable?: string // TableRow[]
    labelDict?: string // IDictionary
    attributeDict?: string // IDictionary
    workflow?: string
    timestamp: Date
    processing: boolean
}