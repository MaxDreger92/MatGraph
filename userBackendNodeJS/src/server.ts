import dotenv from "dotenv"
dotenv.config({ override: true })

import express from "express"
import userRouter from "./controllers/controller"
import cors from "cors"
import bodyParser from 'body-parser';

const app = express()
const port = process.env.PORT || 8080 // Set the desired port number

// Middleware
app.use(bodyParser.json({ limit: '50mb' }))
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }))

app.use(express.json())

app.use(cors())

app.set("trust proxy", true)

// API routes
app.use(userRouter) // Mount the user routes

app.get("/api/users/test", (req, res) => {
    try {
        res.send("jello")
    } catch (err: any) {
        return res.status(500).send(err.message)
    }
})

// // Start the server (local)
app.listen(port, () => {
    console.log(`Server is running on port ${port}`)
})
