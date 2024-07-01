import axios, { AxiosInstance } from 'axios'
import { IDictionary } from './types/workspace.types'
import { IUpload } from './types/workspace.types'

const LOCAL = true

const API_URL = 'https://matgraph.xyz/api/'
const LOCAL_API_URL = 'http://localhost:8000/api/'
const LOCAL_USER_API_URL = 'http://localhost:8080/api/'

export function getCookie(name: string) {
    const cookieValue = document.cookie
        .split('; ')
        .find((cookie) => cookie.startsWith(name))
        ?.split('=')[1]

    return cookieValue
}

class Client {
    private userClient: AxiosInstance
    private dataClient: AxiosInstance

    constructor() {

        if (LOCAL) {
            this.userClient = axios.create({
                baseURL: LOCAL_USER_API_URL,
            })
        } else {
            this.userClient = axios.create({
                baseURL: API_URL,
            })
        }

        if (LOCAL) {
            this.dataClient = axios.create({
                baseURL: LOCAL_API_URL,
            })
        } else {
            this.dataClient = axios.create({
                baseURL: API_URL,
            })
        }

        this.getCurrentUser = this.getCurrentUser.bind(this)
    }

    // ################################## API 
    // ##################################
    // ##################################
    apiActiveStatus = async () => {
        try{
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.dataClient.get(
                'data/api-active-status',
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                },
            )

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while testing API active status!')
        }
    }

    // ################################## User
    // ##################################
    // ##################################
    async login(email: string, password: string) {
        try {
            const response = await this.userClient.post('users/login', {
                email,
                password,
            })

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while logging in!')
        }
    }

    async register(username: string, email: string, password: string) {
        try {
            const response = await this.userClient.post('users/register', {
                username,
                email,
                password,
            })
            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while registering!')
        }
    }

    async getCurrentUser() {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.get('users/current', {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            }) // user json

            return response.data.user
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            } else if (err.message) {
                throw err
            } else {
                throw new Error('Unexpected error while retrieving user!')
            }
        }
    }

    async updateName(name: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.patch(
                'users/update/name',
                {
                    name,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while updating name!')
        }
    }

    async updateUsername(username: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.patch(
                'users/update/username',
                {
                    username,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            return response
        } catch (err: any) {
            if (err.response) {
                if (err.response.status === 409) {
                    throw new Error('Username already in use!')
                }
                if (err.response.data?.message) {
                    err.message = err.response.data.message
                    throw err
                }
            }
            throw new Error('Unexpected error while updating username!')
        }
    }

    async updateInstitution(institution: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.patch(
                'users/update/institution',
                {
                    institution,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            return response
        } catch (err: any) {
            if (err.response) {
                if (err.response.data?.message) {
                    err.message = err.response.data.message
                    throw err
                }
            }
            throw new Error('Unexpected error while updating institution!')
        }
    }

    async updateMail(newMail: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.patch(
                'users/update/email',
                {
                    newMail,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            return response
        } catch (err: any) {
            if (err.response) {
                if (err.response.status === 409) {
                    throw new Error('Email is already in use!')
                }
                if (err.response.data?.message) {
                    err.message = err.response.data.message
                    throw err
                }
            }
            throw new Error('Unexpected error while updating mail!')
        }
    }

    async updatePassword(newPass: string, oldPass: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.patch(
                'users/update/password',
                {
                    newPass,
                    oldPass,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while updating password!')
        }
    }

    async authenticatePassword(password: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.post(
                'users/authpass',
                {
                    password,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while authenticating!')
        }
    }

    async updateUserImg(img: File) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const formData = new FormData()
            formData.append('image', img)

            const response = await this.userClient.post('users/update/img', formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            } else if (err.message) {
                throw err
            }
            throw new Error('Unexpected error while updating user image!')
        }
    }

    // ################################## Uploads
    // ##################################
    // ##################################
    async getUploadList() {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.get('users/uploads/list', {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while retrieving the upload list!')
        }
    }

    async getUploadData(uploadId: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.get(`users/uploads/${uploadId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            if (!response || !response.data)

            return response.data
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while retrieving upload data!')
        }
    }

    async createUpload(csvTable: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.post(`users/uploads/create`, {
                csvTable,
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while saving the upload process!')
        }
    }

    async updateUpload(uploadId: string, updates: Partial<IUpload>) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.patch(`users/uploads/${uploadId}`, {
                updates, 
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while updating upload data!')
        }
    }

    async deleteUpload(uploadId: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.delete(`users/uploads/${uploadId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while updating upload data!')
        }
    }

    // ################################## Workflows
    // ##################################
    // ##################################
    async saveWorkflow(workflow: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.post(
                'users/workflows',
                {
                    workflow,
                },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                }
            )

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while saving workflow!')
        }
    }

    async deleteWorkflow(workflowId: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.delete(`users/workflows/${workflowId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while deleting workflow!')
        }
    }

    async getWorkflows() {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.userClient.get(`users/workflows`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error while retrieving workflows!')
        }
    }

    // ################################## Django API
    // ##################################
    // ##################################
    async workflowSearch(workflow: string | null) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.dataClient.get('match/fabrication-workflow', {
                params: {
                    workflow,
                },
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                responseType: 'blob',
            })
            return response
        } catch (err: any) {
            if (err.response?.data?.message) {
                err.message = err.response.data.message
                throw err
            }
            throw new Error('Unexpected error in workflow query.')
        }
    }

    // (file,context) => label_dict, file_link, file_name
    async requestExtractLabels(file: File, context: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            let formData = new FormData();
            formData.append('file', file);
            formData.append('context', context);

            const response = await this.dataClient.post('import/label-extract', formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!response) {
                throw new Error()
            }

            return response
        } catch (err) {
            throw new Error('Unexpected error while extracting labels!')
        }
    }

    // (label_dict, context, file_link, file_name) => attribute_dict
    async requestExtractAttributes(dict: IDictionary, context: string, link: string, name: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.dataClient.post('import/attribute-extract', {
                params: {
                    label_dict: dict,
                    context: context,
                    file_link: link,
                    file_name: name,
                },
            }, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            if (!response) {
                throw new Error()
            }

            return response
        } catch (err: any) {
            throw new Error('Unexpected error while extracting atributes!')
        }
    }

    // (attribute_dict, context, file_link, file_name) => node_json
    async requestExtractNodes(dict: IDictionary, context: string, link: string, name: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.dataClient.post('import/node-extract', {
                params: {
                    attribute_dict: dict,
                    context: context,
                    file_link: link,
                    file_name: name,
                },
            }, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            if (!response) {
                throw new Error()
            }

            return response
        } catch (err: any) {
            throw new Error('Unexpected error while extracting nodes!')
        }
    }

    // (node_json, context, file_link, file_name) => graph_json
    async requestExtractGraph(nodeJson: string, context: string, link: string, name: string) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.dataClient.post('import/graph-extract', {
                params: {
                    node_json: nodeJson,
                    context: context,
                    file_link: link,
                    file_name: name,
                },
            }, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            if (!response) {
                throw new Error()
            }

            return response
        } catch (err: any) {
            throw new Error('Unexpected error while extracting graph!')
        }
    }

    // (graph_json, context, file_link, file_name) => success
    async requestImportGraph(
        graphJson: string,
        context: string, // Change 'context' parameter name
        fileLink: string, // Change 'fileLink' parameter name
        fileName: string // Change 'fileName' parameter name
    ) {
        try {
            const token = getCookie('token')
            if (!token) {
                throw new Error('Token could not be retrieved!')
            }

            const response = await this.dataClient.post('import/graph-import', {
                params: {
                    graph_json: graphJson,
                    context: context, // Use the corrected parameter name
                    file_link: fileLink, // Use the corrected parameter name
                    file_name: fileName, // Use the corrected parameter name
                },
            }, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })

            if (!response) {
                throw new Error()
            }

            return response
        } catch (err: any) {
            throw new Error('Unexpected error while importing graph!')
        }
    }
}

const client = new Client()

export default client
