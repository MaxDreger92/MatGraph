import { MongoClient, ObjectId } from "mongodb"
import dotenv from "dotenv"

import {MDB_IUser as IUser} from "../types/user.type"

dotenv.config()

const url = process.env.MONGODB_URI as string
const client = new MongoClient(url)
const dbName = "reactgraphdb"
const collectionName = "users"

class UserRepository {
  static async connect() {
    await client.connect()
    const db = client.db(dbName)
    return db.collection<IUser>(collectionName)
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
    const user = await collection.findOne({ email: email }, { projection: { _id: 1 } })

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
    }
    const result = await collection.insertOne(newUser)
    return result.insertedId
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
