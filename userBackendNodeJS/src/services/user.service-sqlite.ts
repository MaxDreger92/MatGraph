import UserRepository from "../repositories/user.repo-sqlite"
import {SQL_IUser as IUser} from "../types/user.type"
import jwt from "jsonwebtoken"
import { Response, NextFunction } from "express"
import { IGetUserAuthInfoRequest } from "../types/req"

import dotenv from "dotenv"
dotenv.config()

class UserService {
  static findByMail(email: string): Promise<IUser | undefined> {
    // Additional business logic or validation can be performed here
    return UserRepository.findByMail(email)
  }

  static findByUsername(username: string): Promise<IUser | undefined> {
    return UserRepository.findByUsername(username)
  }

  static findByID(id: number): Promise<IUser | undefined> {
    return UserRepository.findByID(id)
  }

  static createUser(
    username: string,
    email: string,
    password: string
  ): Promise<boolean> {
    // Additional business logic or validation can be performed here
    return UserRepository.create(username, email, password)
  }

  static deleteUser(
    id: number
  ): Promise<boolean> {
    return UserRepository.delete(id)
  }

  static updateName(
    name: string,
    id: number
  ): Promise<boolean> {
    return UserRepository.updateName(name, id)
  }

  static updateUsername(
    username: string,
    id: number
  ): Promise<boolean> {
    return UserRepository.updateUsername(username, id)
  }

  static updateInstitution(
    institution: string,
    id: number
  ): Promise<boolean> {
    return UserRepository.updateInstitution(institution, id)
  }

  static updateMail(
    newMail: string,
    id: number
  ): Promise<boolean> {
    return UserRepository.updateMail(newMail, id)
  }

  static updatePassword(
    newPass: string,
    id: number
  ): Promise<boolean> {
    return UserRepository.updatePassword(newPass, id)
  }

  static updateImgUrl(
    url: string,
    id: number
  ): Promise<boolean> {
    return UserRepository.updateImgUrl(url, id)
  }

  static generateAccessToken(id: number) {
    return jwt.sign({ userId: id }, process.env.TOKEN_SECRET as string)
    // return jwt.sign(email, process.env.TOKEN_SECRET as string, { expiresIn: '1800s'})
  }

  static authenticateToken(
    req: IGetUserAuthInfoRequest,
    res: Response,
    next: NextFunction
  ) {
    const authHeader = req.headers["authorization"]

    const token = authHeader && authHeader.split(" ")[1]

    if (token == null) return res.sendStatus(401)

    // decodes the token to user email
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
}

export default UserService