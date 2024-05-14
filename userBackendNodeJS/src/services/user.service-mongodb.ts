import { Response, NextFunction } from "express"
import { ObjectId } from "mongodb"
import jwt from "jsonwebtoken"

import UserRepository from "../repositories/user.repo-mongodb"
import WorkflowRepository from "../repositories/workflow.repo-mongodb"
import {MDB_IUser as IUser} from "../types/user.type"
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

  static verifyUser(
    username: string
  ): Promise<boolean> {
    return UserRepository.verify(username)
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

  static async generateAccessToken(email: string, purpose: string = 'default-purpose') {
    const userId = await UserRepository.getUserID(email)
    const token = jwt.sign({ userId: userId, purpose: purpose }, process.env.TOKEN_SECRET as string)
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
        if (err) return res.sendStatus(403)

        try {
            if (payload.purpose === 'verify-user') {
                const admin = await UserRepository.findByID(payload.userId);
                if (!admin || admin.username !== 'admin') {
                    return res.status(403).json({message: "Needs to be admin for this action."});
                }
                req.adminId = payload.userId
            } else {
                req.userId = payload.userId;
            }

            next();
        } catch (error) {
            return res.status(500).json({message: "Internal Server Error"});
        }
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
