import { MongoClient, ObjectId } from "mongodb"
import dotenv from "dotenv"
import { IWorkflow } from "../types/workflow.type"

dotenv.config()

const url = process.env.MONGODB_URI as string
const client = new MongoClient(url)
const dbName = "matgraphdb"
const workflowCollectionName = "workflows"

class WorkflowRepository {
  static async connect() {
    await client.connect()
    const db = client.db(dbName)
    return db.collection<IWorkflow>(workflowCollectionName)
  }

  static async saveWorkflow(
    userId: string,
    workflow: string
  ): Promise<ObjectId> {
    const collection = await this.connect()
    const newWorkflow: IWorkflow = {
      userId: new ObjectId(userId),
      workflow: workflow,
      timestamp: new Date(),
    }

    const result = await collection.insertOne(newWorkflow)
    return result.insertedId
  }

  static async deleteWorkflow(workflowId: string): Promise<boolean> {
    const collection = await this.connect()
    const result = await collection.deleteOne({ _id: new ObjectId(workflowId) })

    return result.deletedCount > 0 // Returns true if a document was deleted
  }

  static async getWorkflowsByUserID(userId: string): Promise<IWorkflow[]> {
    const collection = await this.connect()
    return await collection.find({ userId: new ObjectId(userId) }).toArray()
  }
}

export default WorkflowRepository
