import { ObjectId } from 'mongodb'
import { Graph, Upload } from '../types/workspace.types'
import { connectToDatabase } from '../mongodb';

const graphCollection = 'graphs'
const uploadCollection = 'uploads'

class WorkspaceRepository {
    static getGraphCollection = async () => {
        const db = await connectToDatabase();
        return db.collection<Graph>(graphCollection);
    }

    static getUploadCollection = async () => {
        const db = await connectToDatabase();
        return db.collection<Upload>(uploadCollection);
    }

    // ################################## Graphs
    // ##################################
    // ##################################
    static saveGraph = async (userId: string, graph: string): Promise<ObjectId> => {
        const collection = await this.getGraphCollection();
        const newGraph: Graph = {
            userId: new ObjectId(userId),
            graph: graph,
            timestamp: new Date(),
        };

        const result = await collection.insertOne(newGraph);
        return result.insertedId;
    }

    static updateGraph = async (
        userId: string,
        graphId: string,
        updates: Partial<Graph>
    ): Promise<boolean> => {
        const collection = await this.getGraphCollection()
        const result = await collection.updateOne(
            { _id: new ObjectId(graphId), userId: new ObjectId(userId) },
            { $set: {...updates, timestamp: new Date()} }
        )
        return result.modifiedCount > 0
    }

    static deleteGraph = async (userId: string, graphId: string): Promise<boolean> => {
        const collection = await this.getGraphCollection();
        const result = await collection.deleteOne({ _id: new ObjectId(graphId), userId: new ObjectId(userId) });

        return result.deletedCount > 0;
    }

    static getGraphsByUserID = async (userId: string): Promise<Graph[]> => {
        const collection = await this.getGraphCollection();
        return await collection.find({ userId: new ObjectId(userId) }).toArray();
    }

    // ################################## Uploads
    // ##################################
    // ##################################
    static getUploadsByUserID = async (userId: string): Promise<Upload[]> => {
        const collection = await this.getUploadCollection();
        return await collection.find({ userId: new ObjectId(userId) }).toArray();
    }

    static getUploadByID = async (userId: string, uploadId: string): Promise<Upload | null> => {
        const collection = await this.getUploadCollection();
        return await collection.findOne({
            _id: new ObjectId(uploadId),
            userId: new ObjectId(userId),
        });
    }

    static createUpload = async (userId: string, csvTable: string, fileId: string, fileName="no_name.csv"): Promise<Upload> => {
        const collection = await this.getUploadCollection();
        const newUpload: Upload = {
            userId: new ObjectId(userId),
            progress: 1,
            csvTable: csvTable,
            fileId: fileId,
            fileName: fileName,
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
        updates: Partial<Upload>
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
