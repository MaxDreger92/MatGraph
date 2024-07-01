import { ObjectId } from 'mongodb'
import { IWorkflow, IUpload } from '../types/workspace.types'
import { connectToDatabase } from '../mongodb';

const workflowCollection = 'workflows'
const uploadCollection = 'uploads'

class WorkspaceRepository {
    static getWorkflowCollection = async () => {
        const db = await connectToDatabase();
        return db.collection<IWorkflow>(workflowCollection);
    }

    static getUploadCollection = async () => {
        const db = await connectToDatabase();
        return db.collection<IUpload>(uploadCollection);
    }

    // ################################## Workflows
    // ##################################
    // ##################################
    static saveWorkflow = async (userId: string, workflow: string): Promise<ObjectId> => {
        const collection = await this.getWorkflowCollection();
        const newWorkflow: IWorkflow = {
            userId: new ObjectId(userId),
            workflow: workflow,
            timestamp: new Date(),
        };

        const result = await collection.insertOne(newWorkflow);
        return result.insertedId;
    }

    static deleteWorkflow = async (workflowId: string): Promise<boolean> => {
        const collection = await this.getWorkflowCollection();
        const result = await collection.deleteOne({ _id: new ObjectId(workflowId) });

        return result.deletedCount > 0;
    }

    static getWorkflowsByUserID = async (userId: string): Promise<IWorkflow[]> => {
        const collection = await this.getWorkflowCollection();
        return await collection.find({ userId: new ObjectId(userId) }).toArray();
    }

    // ################################## Uploads
    // ##################################
    // ##################################
    static getUploadsByUserID = async (userId: string): Promise<IUpload[]> => {
        const collection = await this.getUploadCollection();
        return await collection.find({ userId: new ObjectId(userId) }).toArray();
    }

    static getUploadByID = async (userId: string, uploadId: string): Promise<IUpload | null> => {
        const collection = await this.getUploadCollection();
        return await collection.findOne({
            _id: new ObjectId(uploadId),
            userId: new ObjectId(userId),
        });
    }

    static createUpload = async (userId: string, csvTable: string): Promise<IUpload> => {
        const collection = await this.getUploadCollection();
        const newUpload: IUpload = {
            userId: new ObjectId(userId),
            progress: 1,
            csvTable: csvTable,
            timestamp: new Date(),
            processing: false,
        };

        const result = await collection.insertOne(newUpload);

        newUpload._id = result.insertedId

        return newUpload
    }

    static updateUploadFields = async (
        userId: string,
        uploadId: string,
        updates: Partial<IUpload>
    ): Promise<boolean> => {
        const collection = await this.getUploadCollection();
        const result = await collection.updateOne(
            { _id: new ObjectId(uploadId), userId: new ObjectId(userId) },
            { $set: {...updates, timestamp: new Date()} }
        );
        return result.modifiedCount > 0;
    }

    static deleteUpload = async (userId: string, uploadId: string): Promise<boolean> => {
        const collection = await this.getUploadCollection();
        const result = await collection.deleteOne({ _id: new ObjectId(uploadId), userId: new ObjectId(userId) });
        return result.deletedCount > 0;
    }
}

export default WorkspaceRepository;
