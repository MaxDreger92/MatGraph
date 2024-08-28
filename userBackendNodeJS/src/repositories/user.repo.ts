import { ObjectId } from "mongodb";
import { MDB_IUser as IUser } from "../types/user.type";
import { connectToDatabase } from "../mongodb";

const collectionName = "users";

class UserRepository {
    static getCollection = async () => {
        const db = await connectToDatabase();
        return db.collection<IUser>(collectionName);
    }

    static findByMail = async (email: string): Promise<IUser | null> => {
        const collection = await this.getCollection();
        return await collection.findOne({ email: email });
    }

    static findByUsername = async (username: string): Promise<IUser | null> => {
        const collection = await this.getCollection();
        return await collection.findOne({ username: username });
    }

    static findByID = async (id: string): Promise<IUser | null> => {
        const collection = await this.getCollection();
        return await collection.findOne({ _id: new ObjectId(id) });
    }

    static getUserID = async (email: string): Promise<string | null> => {
        const collection = await this.getCollection();
        const user = await collection.findOne(
            { email: email },
            { projection: { _id: 1 } }
        );

        if (!user) return null;
        return user._id.toString();
    }

    static create = async (username: string, email: string, password: string) => {
        const collection = await this.getCollection();
        const newUser: IUser = {
            name: "",
            username,
            email,
            password,
            roles: [],
            institution: "",
            imgurl: "",
            confirmed: false,
            verified: false,
        };
        const result = await collection.insertOne(newUser);
        return result.insertedId;
    }

    static confirm = async (username: string) => {
        const collection = await this.getCollection();
        const result = await collection.updateOne(
            { username: username },
            { $set: { confirmed: true } }
        );
        return result.modifiedCount > 0;
    }

    static verify = async (username: string) => {
        const collection = await this.getCollection();
        const result = await collection.updateOne(
            { username: username },
            { $set: { verified: true } }
        );
        return result.modifiedCount > 0;
    }

    static delete = async (id: string) => {
        const collection = await this.getCollection();
        const result = await collection.deleteOne({ _id: new ObjectId(id) });
        return result.deletedCount > 0;
    }

    static updateName = async (name: string, id: string) => {
        const collection = await this.getCollection();
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { name: name } }
        );
        return result.modifiedCount > 0;
    }

    static updateUsername = async (username: string, id: string) => {
        const collection = await this.getCollection();
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { username: username } }
        );
        return result.modifiedCount > 0;
    }

    static updateInstitution = async (institution: string, id: string) => {
        const collection = await this.getCollection();
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { institution: institution } }
        );
        return result.modifiedCount > 0;
    }

    static updateMail = async (newMail: string, id: string) => {
        const collection = await this.getCollection();
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { email: newMail } }
        );
        return result.modifiedCount > 0;
    }

    static updatePassword = async (newPass: string, id: string) => {
        const collection = await this.getCollection();
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { password: newPass } }
        );
        return result.modifiedCount > 0;
    }

    static updateImgUrl = async (url: string, id: string) => {
        const collection = await this.getCollection();
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { imgurl: url } }
        );
        return result.modifiedCount > 0;
    }
}

export default UserRepository;
