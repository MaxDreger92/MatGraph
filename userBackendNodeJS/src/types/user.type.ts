export interface SQL_IUser {
  id: number
  name?: string | undefined
  username: string | undefined
  email: string
  password: string
  roles?: Array<string> | undefined
  institution?: string | undefined
  imgurl?: string | undefined
}

export interface MDB_IUser {
  name?: string | undefined
  username: string | undefined
  email: string
  password: string
  roles?: Array<string> | undefined
  institution?: string | undefined
  imgurl?: string | undefined
  confirmed: boolean
  verified: boolean
}
