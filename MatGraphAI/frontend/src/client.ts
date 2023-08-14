import axios, { AxiosInstance } from "axios"

const API_URL = "http://localhost:8000/"

function getCookie(name: string) {
  const cookieValue = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith(name))
    ?.split("=")[1]

  return cookieValue
}

class Client {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
    })

    this.getCurrentUser = this.getCurrentUser.bind(this)
  }

  async test() {
    try {
      const response = await this.client.get("/test")
      return response.data
    } catch (err: any) {
      throw new Error('Error: ' + err.message)
    }
  }

  async login(email: string, password: string) {
    try {
      const response = await this.client.post("/users/login", {
        email,
        password,
      }) // token json
      // const token = response.data.token; // Cookie saved in login component

      // if (token) {
      //   document.cookie = `token=${token}`
      // }
      return response
    } catch (err: any) {
      throw new Error('Error: ' + err.message)
    }
  }

  async register(name: string, email: string, password: string) {
    try {
      const response = await this.client.post("/users/register", {
        name,
        email,
        password,
      }) // message json
      return response.data
    } catch (err: any) {
      throw new Error('Error: ' + err.message)
    }
  }

  async getCurrentUser() {
    try {
      const token = getCookie("token")
      if (!token) {
        return null
      }

      const response = await this.client.get("/users/current", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }) // user json

      return response.data
    } catch (err: any) {
      if (err.response && err.response.status === 404) {
        return null
      } else {
        throw new Error('Error: ' + err.message)
      }
    }
  }

  async updateName(name: string) {
    try {
      const token = getCookie("token")
      if (!token) {
        return
      }

      const response = await this.client.patch("/users/update/name", {
        name,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      return response.data
    } catch (err: any) {
      throw new Error('Error: ' + err.message)
    }
  }

  async updateMail(newMail: string) {
    try {
      const token = getCookie("token")
      if (!token) {
        return
      }

      const response = await this.client.patch("/users/update/email", {
        newMail,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      return response.data
    } catch (err: any) {
      throw new Error('Error: ' + err.message)
    }
  }

  async updatePassword(newPass: string, oldPass: string) {
    try {
      const token = getCookie("token")
      if (!token) {
        return
      }

      const response = await this.client.patch("/users/update/password", {
        newPass,
        oldPass,
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      return response.data
    } catch (err: any) {
      throw new Error('Error: ' + err.message)
    }
  }

  async workflowSearch(workflow: string | null) {
    try {
      const jsonData = JSON.stringify({ workflow });
      const response = await this.client.get("/search/fabrication-workflow", {
        params: {
          workflow,
        },
        responseType: 'blob'
      })
      return response
    } catch (err:any) {
      throw new Error('Error: ' + err.message)
    }
  }
}

const client = new Client()

export default client
