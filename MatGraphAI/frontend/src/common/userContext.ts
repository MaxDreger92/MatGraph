import { createContext } from "react"
import {MDB_IUser, SQL_IUser} from "../types/user.type"

const initialSQLUser: SQL_IUser = {
  id: -1,
  name: "",
  username: "",
  email: "",
  password: "",
  roles: [""],
  institution: "",
  imgurl: "",
}

const initialMDBUser: MDB_IUser = {
  name: "",
  username: "",
  email: "",
  password: "",
  roles: [""],
  institution: "",
  imgurl: "",
}

const userContext = createContext<MDB_IUser | null | undefined>(initialMDBUser)

export { userContext }
export { initialMDBUser }