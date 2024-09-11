import { MongoClient } from "mongodb";
import os from "os";

const url = process.env.MONGODB_URI as string;
const tlsCertificateKeyFile = (process.env.TLS_CERTIFICATE_KEY_FILE as string).replace(
    "~",
    os.homedir()
);
const tlsCAFile = (process.env.TLS_CA_FILE as string).replace(
    "~",
    os.homedir()
);

const options = {
    tls: true,
    tlsCertificateKeyFile: tlsCertificateKeyFile,
    tlsCAFile: tlsCAFile,
    tlsAllowInvalidCertificates: false
};

const client = new MongoClient(url, options);
const dbName = "matgraphdb";
let isConnected = false;

export async function connectToDatabase() {
    if (!isConnected) {
        await client.connect();
        isConnected = true;
    }
    return client.db(dbName);
}
