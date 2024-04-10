import { ObjectId } from "mongodb";

export interface IWorkflow {
    _id?: ObjectId
    userId?: ObjectId
    workflow: string
    timestamp: Date
}