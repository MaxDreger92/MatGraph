import { MongoClient } from 'mongodb'
import os from 'os'
import * as fs from 'fs'
import * as tls from 'tls'

const url = process.env.MONGODB_URI as string

const client = new MongoClient(url, { tls: true, tlsAllowInvalidCertificates: true })
const dbName = 'reactgraphdb'
let isConnected = false

export async function connectToDatabase() {
    if (!isConnected) {
        try {
            await client.connect()
            isConnected = true
            console.log('Successfully connected to MongoDB')
        } catch (error) {
            console.error('Error connecting to MongoDB:', error)
            throw error
        }
    } else {
        console.log('Already connected to MongoDB')
    }

    return client.db(dbName)
}
