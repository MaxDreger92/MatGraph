import { MongoClient } from "mongodb";
import os from "os";
import * as fs from "fs";
import * as tls from "tls"

const url = process.env.MONGODB_URI as string;
const tlsCertificateFilePath = (process.env.TLS_CERTIFICATE_FILE as string).replace("~", os.homedir());
const tlsKeyFilePath = (process.env.TLS_KEY_FILE as string).replace("~", os.homedir());
const tlsCAFilePath = (process.env.TLS_CA_FILE as string).replace("~", os.homedir());

const tlsCertificateFile = fs.readFileSync(tlsCertificateFilePath);
const tlsKeyFile = fs.readFileSync(tlsKeyFilePath);
const tlsCAFile = fs.readFileSync(tlsCAFilePath);

console.log("Key File Content:\n", tlsKeyFile)

const secureContext = tls.createSecureContext({
    ca: tlsCAFile,
    cert: tlsCertificateFile,
    key: tlsKeyFile
})

const client = new MongoClient(url, {tls:true, tlsAllowInvalidCertificates: true, secureContext});
const dbName = "reactgraphdb";
let isConnected = false;

export async function connectToDatabase() {
    if (!isConnected) {
        try {
            // Attempt to connect to the MongoDB server
            await client.connect();
            isConnected = true;
            console.log("Successfully connected to MongoDB"); // Log success message if connection works
        } catch (error) {
            // Log any connection errors
            console.error("Error connecting to MongoDB:", error);
            throw error; // Rethrow the error after logging it
        }
    } else {
        console.log("Already connected to MongoDB");
    }
    
    return client.db(dbName);
}
