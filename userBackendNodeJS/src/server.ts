import dotenv from 'dotenv'
dotenv.config({ path: '../.env' })

import express from "express"
import userRouter from "./controllers/user.controller-mongodb"
import cors from "cors"

const app = express()
const port = process.env.PORT || 8080 // Set the desired port number

// Middleware
app.use(express.json())

app.use(cors())

app.set('trust proxy', true)

// API routes
app.use(userRouter) // Mount the user routes

app.get("/api/users/test", (req, res) => {
  try {res.send("jello")}
  catch (err: any) {
    return res.status(500).send(err.message)
  }
})

// // Start the server (local)
app.listen(port, () => {
  console.log(`Server is running on port ${port}`)
})
