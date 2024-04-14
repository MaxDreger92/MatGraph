import { Response, NextFunction } from "express"
import dotenv from "dotenv"
import { ObjectId } from "mongodb"
import jwt from "jsonwebtoken"

import UserRepository from "../repositories/user.repo-mongodb"
import WorkflowRepository from "../repositories/workflow.repo-mongodb"
import {MDB_IUser as IUser} from "../types/user.type"
import { IWorkflow } from "../types/workflow.type"
import { IGetUserAuthInfoRequest } from "../types/req"

dotenv.config()

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

  static deleteUser(
    id: string
  ): Promise<boolean> {
    return UserRepository.delete(id)
  }

  static updateName(
    name: string,
    id: string
  ): Promise<boolean> {
    return UserRepository.updateName(name, id)
  }

  static updateUsername(
    username: string,
    id: string
  ): Promise<boolean> {
    return UserRepository.updateUsername(username, id)
  }

  static updateInstitution(
    institution: string,
    id: string
  ): Promise<boolean> {
    return UserRepository.updateInstitution(institution, id)
  }

  static updateMail(
    newMail: string,
    id: string
  ): Promise<boolean> {
    return UserRepository.updateMail(newMail, id)
  }

  static updatePassword(
    newPass: string,
    id: string
  ): Promise<boolean> {
    return UserRepository.updatePassword(newPass, id)
  }

  static updateImgUrl(
    url: string,
    id: string
  ): Promise<boolean> {
    return UserRepository.updateImgUrl(url, id)
  }

  static async generateAccessToken(email: string) {
    const userId = await UserRepository.getUserID(email)
    const token = jwt.sign({ userId: userId }, process.env.TOKEN_SECRET as string)
    return token
  }

  static authenticateToken(
    req: IGetUserAuthInfoRequest,
    res: Response,
    next: NextFunction
  ) {
    const authHeader = req.headers["authorization"]

    const token = authHeader && authHeader.split(" ")[1]

    if (token == null) return res.sendStatus(401)

    // decodes the token to userId
    jwt.verify(
      token,
      process.env.TOKEN_SECRET as string,
      (err: Error | null, payload: any) => {
        if (err) return res.sendStatus(403)

        req.userId = payload.userId

        next()
      }
    )
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
      const {userId, ...restOfWorkflow} = workflow
      return restOfWorkflow
    })

    return workflowsWithoutUserId
  }
}

export default UserService
