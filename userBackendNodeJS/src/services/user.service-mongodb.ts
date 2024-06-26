import { Response, NextFunction } from "express"
import { ObjectId } from "mongodb"
import jwt from "jsonwebtoken"
import axios from "axios"
import nodemailer from 'nodemailer'
import fs from 'fs'
import path from 'path'

import UserRepository from "../repositories/user.repo-mongodb"
import WorkflowRepository from "../repositories/workflow.repo-mongodb"
import { MDB_IUser as IUser } from "../types/user.type"
import { IWorkflow } from "../types/workflow.type"
import { IGetUserAuthInfoRequest } from "../types/req"

class UserService {
    static findByMail(email: string): Promise<IUser | null> {
        return UserRepository.findByMail(email)
    }

    static findByUsername(username: string): Promise<IUser | null> {
        return UserRepository.findByUsername(username)
    }

    static findByID(id: string): Promise<IUser | null> {
        return UserRepository.findByID(id)
    }

    static createUser(
        username: string,
        email: string,
        password: string
    ): Promise<ObjectId> {
        return UserRepository.create(username, email, password)
    }

    static confirmUser(username: string): Promise<boolean> {
        return UserRepository.confirm(username)
    }

    static verifyUser(username: string): Promise<boolean> {
        return UserRepository.verify(username)
    }

    static deleteUser(id: string): Promise<boolean> {
        return UserRepository.delete(id)
    }

    static updateName(name: string, id: string): Promise<boolean> {
        return UserRepository.updateName(name, id)
    }

    static updateUsername(username: string, id: string): Promise<boolean> {
        return UserRepository.updateUsername(username, id)
    }

    static updateInstitution(
        institution: string,
        id: string
    ): Promise<boolean> {
        return UserRepository.updateInstitution(institution, id)
    }

    static updateMail(newMail: string, id: string): Promise<boolean> {
        return UserRepository.updateMail(newMail, id)
    }

    static updatePassword(newPass: string, id: string): Promise<boolean> {
        return UserRepository.updatePassword(newPass, id)
    }

    static updateImgUrl(url: string, id: string): Promise<boolean> {
        return UserRepository.updateImgUrl(url, id)
    }

    static saveWorkflow(userId: string, workflow: string): Promise<ObjectId> {
        return WorkflowRepository.saveWorkflow(userId, workflow)
    }

    static deleteWorkflow(workflowId: string): Promise<boolean> {
        return WorkflowRepository.deleteWorkflow(workflowId)
    }

    static async getWorkflowsByUserID(userId: string): Promise<IWorkflow[]> {
        const workflows = await WorkflowRepository.getWorkflowsByUserID(userId)

        const workflowsWithoutUserId = workflows.map((workflow: IWorkflow) => {
            const { userId, ...restOfWorkflow } = workflow
            return restOfWorkflow
        })

        return workflowsWithoutUserId
    }

    static async sendConfirmationMail(usermail: any) {
        try {
            const userToken = await UserService.generateAccessToken(
                usermail,
                'user-confirmation'
            )
            const htmlPath = require("os").homedir() + '/Projects/MatGraph/userBackendNodeJS/src/html/confirmation-mail.html'
            let html = fs.readFileSync(htmlPath, 'utf8')
            const confirmationLink = `https://matgraph.xyz/api/users/confirm?token=${userToken}`

            html = html.replace('{{confirmation_link}}', confirmationLink)

            const mailOptions = {
                from: '"matGraph" <registration@matgraph.xyz>',
                to: usermail,
                subject: 'Confirm Your Email',
                html: html,
            }

            const mailSuccess = await this.sendMail(mailOptions)

            return mailSuccess
        } catch (err: any) {
            if (err.message) {
                console.log("Error sending confirmation mail: ", err.message)
            }
            throw err
        }
    }

    static async sendVerificationMail(username: any, usermail: any) {
        try {
            const adminToken = await UserService.generateAccessToken(
                'admin@matgraph.xyz',
                'admin-verification'
            )
            const htmlPath = require("os").homedir() + '/Projects/MatGraph/userBackendNodeJS/src/html/verification-mail.html'
            let html = fs.readFileSync(htmlPath, 'utf8')
            const verificationLink = `https://matgraph.xyz/api/users/verify?token=${adminToken}&username=${username}`

            html = html.replace('{{username}}', username)
            html = html.replace('{{usermail}}', usermail)
            html = html.replace('{{verification_link}}', verificationLink)
    
            const mailOptions = {
                from: '"matGraph" <registration@matgraph.xyz>', // Sender address
                to: 'registration@matgraph.xyz', // List of recipients
                subject: 'New User Registration', // Subject line
                html: html,
            }

            const mailSuccess = await this.sendMail(mailOptions)

            return mailSuccess
        } catch (err: any) {
            if (err.message) {
                console.log("Error sending verification mail: ", err.message)
            }
            throw err
        }
    }

    static async sendVerificationConfirmation(usermail: any) {
        try {
            const htmlPath = require("os").homedir() + '/Projects/MatGraph/userBackendNodeJS/src/html/verified-mail.html'
            let html = fs.readFileSync(htmlPath, 'utf8')
    
            const mailOptions = {
                from: '"matGraph" <registration@matgraph.xyz>', // Sender address
                to: usermail, // List of recipients
                subject: 'Verification complete!', // Subject line
                html: html,
            }

            const mailSuccess = await this.sendMail(mailOptions)

            return mailSuccess
        } catch (err: any) {
            if (err.message) {
                console.log("Error sending verification mail: ", err.message)
            }
            throw err
        }
    }

    static async sendMail(options: any): Promise<boolean> {
        return new Promise((resolve, reject) => {
            const transporter = nodemailer.createTransport({
                host: 'smtp.sendgrid.net',
                port: 587,
                auth: {
                    user: 'apikey',
                    pass: process.env.SENDGRID_API_KEY,
                }
            })
    
            transporter.sendMail(options, function (err, info) {
                if (err) {
                    console.log('Error sending mail:', err)
                    resolve(false)
                } else {
                    console.log('Mail sent:', info.response)
                    resolve(true)
                }
            })
        })
    }

    static getConfirmedPage(confirmed: boolean) {
        let pagePath = ''
        let html = ''
        if (confirmed) {
            pagePath = require("os").homedir() + '/Projects/MatGraph/userBackendNodeJS/src/html/email-confirmed.html'
        } else {
            pagePath = require("os").homedir() + '/Projects/MatGraph/userBackendNodeJS/src/html/confirmation-error.html'
        }
        html = fs.readFileSync(pagePath, 'utf8')
        return html
    }

    static getVerifiedPage(verified: boolean) {
        let pagePath = ''
        let html = ''
        if (verified) {
            pagePath = require("os").homedir() + '/Projects/MatGraph/userBackendNodeJS/src/html/user-verified.html'
        } else {
            pagePath = require("os").homedir() + '/Projects/MatGraph/userBackendNodeJS/src/html/verification-error.html'
        }
        html = fs.readFileSync(pagePath, 'utf8')
        return html
    }

    static async generateAccessToken(
        email: string,
        purpose: string = "default-purpose"
    ) {
        const userId = await UserRepository.getUserID(email)
        const token = jwt.sign(
            { userId: userId, purpose: purpose },
            process.env.TOKEN_SECRET as string
        )
        return token
    }

    static authenticateToken(
        req: IGetUserAuthInfoRequest,
        res: Response,
        next: NextFunction
    ) {
        const authHeader = req.headers["authorization"]

        let token = authHeader && authHeader.split(" ")[1]

        if (!token) {
            token = req.query.token as string
        }

        if (!token) return res.sendStatus(401)

        // decodes the token to userId
        jwt.verify(
            token,
            process.env.TOKEN_SECRET as string,
            async (err: Error | null, payload: any) => {
                if (err) {
                    return res.sendStatus(403)
                }
                try {
                    if (payload.purpose === "admin-verification") {
                        const admin = await UserRepository.findByID(
                            payload.userId
                        )
                        if (!admin || admin.username !== "admin") {
                            return res.status(403).json({
                                message: "Needs to be admin for this action.",
                            })
                        }
                        req.adminId = payload.userId
                    } else if (payload.purpose === "user-confirmation") {
                        const user = await UserRepository.findByID(
                            payload.userId
                        )
                        if (!user) {
                            return res.status(404).json({
                                message: "User not found.",
                            })
                        }
                        req.userId = payload.userId
                    } else {
                        req.userId = payload.userId
                    }
                    next()
                } catch (error) {
                    return res
                        .status(500)
                        .json({ message: "Internal Server Error" })
                }
            }
        )
    }

    static async getGoogleAccessToken() {
        try {
            const response = await axios.post(
                "https://oauth2.googleapis.com/token",
                null,
                {
                    params: {
                        client_id: process.env.GOOGLE_CLIENT_ID,
                        client_secret: process.env.GOOGLE_CLIENT_SECRET,
                        refresh_token: process.env.GOOGLE_REFRESH_TOKEN,
                        grant_type: "refresh_token",
                    },
                }
            )
            return response.data.access_token
        } catch (err: any) {
            console.log("Error fetching access token: ", err.response.data)
            throw err
        }
    }
}

export default UserService
