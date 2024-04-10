import sqlite3 from "sqlite3"
import {SQL_IUser as IUser} from "../types/user.type"

// Create a new SQLite database connection
// const db = new sqlite3.Database(":memory:")
const db = new sqlite3.Database("./users.db")

// Create the users table if it doesn't exist
db.run(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    roles TEXT,
    image TEXT,
    institution TEXT,
    imgurl TEXT
  )
`)

class UserRepository {
  static findByMail(email: string): Promise<IUser | undefined> {
    return new Promise((resolve, reject) => {
      db.get("SELECT * FROM users WHERE email = ?", [email], (err, row) => {
        if (err) {
          reject(err)
        } else {
          resolve(row as IUser | undefined)
        }
      })
    })
  }

  static findByUsername(username: string): Promise<IUser | undefined> {
    return new Promise((resolve, reject) => {
      db.get("SELECT * FROM users WHERE username = ?", [username], (err, row) => {
        if (err) {
          reject(err)
        } else {
          resolve(row as IUser | undefined)
        }
      })
    })
  }

  static findByID(id: number): Promise<IUser | undefined> {
    return new Promise((resolve, reject) => {
      db.get("SELECT * FROM users WHERE id = ?", [id], (err,row) => {
        if (err) {
          reject(err)
        } else {
          resolve(row as IUser | undefined)
        }
      })
    })
  }

  static create(username: string, email: string, password: string): Promise<boolean> {
    return new Promise((resolve, reject) => {
      db.run(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        [username, email, password],
        function (err) {
          if (err) {
            reject(err)
          } else {
            resolve(true)
          }
        }
      )
    })
  }

  static delete(id: number): Promise<boolean> {
    return new Promise ((resolve, reject) => {
      db.run(
        "DELETE FROM users WHERE id = ?", [id],
        function (err) {
          if (err) {
            reject(err)
          } else {
            resolve(true)
          }
        }
      )
    })
  }

  static updateName(name: string, id: number): Promise<boolean> {
    return new Promise((resolve, reject) => {
      db.run(
        "UPDATE users SET name = ? WHERE id = ?",
        [name, id],
        function (err) {
          if (err) {
            reject(err)
          } else {
            resolve(true)
          }
        }
      )
    })
  }

  static updateUsername(username: string, id: number): Promise<boolean> {
    return new Promise((resolve, reject) => {
      db.run(
        "UPDATE users SET username = ? WHERE id = ?",
        [username, id],
        function (err) {
          if (err) {
            reject(err)
          } else {
            resolve(true)
          }
        }
      )
    })
  }

  static updateInstitution(institution: string, id: number): Promise<boolean> {
    return new Promise((resolve, reject) => {
      db.run(
        "UPDATE users SET institution = ? WHERE id = ?",
        [institution, id],
        function (err) {
          if (err) {
            reject(err)
          } else {
            resolve(true)
          }
        }
      )
    })
  }

  static updateMail(newMail: string, id: number): Promise<boolean> {
    return new Promise((resolve, reject) => {
      db.run(
        "UPDATE users SET email = ? WHERE id = ?",
        [newMail, id],
        function (err) {
          if (err) {
            reject(err)
          } else {
            resolve(true)
          }
        }
      )
    })
  }

  static updatePassword(newPass: string, id: number): Promise<boolean> {
    return new Promise((resolve, reject) => {
      db.run(
        "UPDATE users SET password = ? WHERE id = ?",
        [newPass, id],
        function (err) {
          if (err) {
            reject(err)
          } else {
            resolve(true)
          }
        }
      )
    })
  }

  static updateImgUrl(url: string, id: number): Promise<boolean> {
    return new Promise((resolve, reject) => {
      db.run(
        "UPDATE users SET imgurl = ? WHERE id = ?",
        [url, id],
        function (err) {
          if (err) {
            reject(err)
          } else {
            resolve(true)
          }
        }
      )
    })
  }
}

export default UserRepository
