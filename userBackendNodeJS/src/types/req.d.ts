import { Request } from "express"

export interface IGetUserAuthInfoRequest extends Request {
  userId?: any
}
