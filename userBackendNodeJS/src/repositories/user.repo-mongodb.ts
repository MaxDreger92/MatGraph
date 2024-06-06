import { MongoClient, ObjectId } from "mongodb"
import { MDB_IUser as IUser } from "../types/user.type"

const url = process.env.MONGODB_URI as string
const tlsCertificateKeyFile = (process.env.TLS_CERTIFICATE_KEY_FILE as string).replace(
    "~",
    require("os").homedir()
)
const tlsCAFile = (process.env.TLS_CA_FILE as string).replace(
    "~",
    require("os").homedir()
)

const options = {
    tls: true,
    tlsCertificateKeyFile: tlsCertificateKeyFile,
    tlsCAFile: tlsCAFile,
    tlsAllowInvalidCertificates: false
}
const client = new MongoClient(url, options)
const dbName = "matgraphdb"
const collectionName = "users"

class UserRepository {
    static async connect() {
        try {
            await client.connect()
            const db = client.db(dbName)
            return db.collection<IUser>(collectionName)
        } catch (err) {
            console.error("Connection error:", err)
            process.exit(1)
        }
    }

    static async findByMail(email: string): Promise<IUser | null> {
        const collection = await this.connect()
        return await collection.findOne({ email: email })
    }

    static async findByUsername(username: string): Promise<IUser | null> {
        const collection = await this.connect()
        return await collection.findOne({ username: username })
    }

    static async findByID(id: string): Promise<IUser | null> {
        const collection = await this.connect()
        const user = await collection.findOne({ _id: new ObjectId(id) })
        return user
    }

    static async getUserID(email: string): Promise<string | null> {
        const collection = await this.connect()
        const user = await collection.findOne(
            { email: email },
            { projection: { _id: 1 } }
        )

        if (!user) return null
        return user._id.toString()
    }

    static async create(username: string, email: string, password: string) {
        const collection = await this.connect()
        const newUser: IUser = {
            name: "",
            username,
            email,
            password,
            roles: [],
            institution: "",
            imgurl: "",
            verified: false,
        }
        const result = await collection.insertOne(newUser)
        return result.insertedId
    }

    static async verify(username: string) {
        const collection = await this.connect()
        const result = await collection.updateOne(
            { username: username },
            { $set: { verified: true } }
        )
        return result.modifiedCount > 0
    }

    static async delete(id: string) {
        const collection = await this.connect()
        const result = await collection.deleteOne({ _id: new ObjectId(id) })
        return result.deletedCount > 0
    }

    static async updateName(name: string, id: string) {
        const collection = await this.connect()
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { name: name } }
        )
        return result.modifiedCount > 0
    }

    static async updateUsername(username: string, id: string) {
        const collection = await this.connect()
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { username: username } }
        )
        return result.modifiedCount > 0
    }

    static async updateInstitution(institution: string, id: string) {
        const collection = await this.connect()
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { institution: institution } }
        )
        return result.modifiedCount > 0
    }

    static async updateMail(newMail: string, id: string) {
        const collection = await this.connect()
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { email: newMail } }
        )
        return result.modifiedCount > 0
    }

    static async updatePassword(newPass: string, id: string) {
        const collection = await this.connect()
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { password: newPass } }
        )
        return result.modifiedCount > 0
    }

    static async updateImgUrl(url: string, id: string) {
        const collection = await this.connect()
        const result = await collection.updateOne(
            { _id: new ObjectId(id) },
            { $set: { imgurl: url } }
        )
        return result.modifiedCount > 0
    }
}

export default UserRepository
