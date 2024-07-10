import express from 'express'
import bcrypt from 'bcrypt'
import UserService from '../services/service'
import { IGetUserAuthInfoRequest } from '../types/req'
import { Response } from 'express'
import { v2 as cloudinary } from 'cloudinary'
import axios from 'axios'
import fileUpload from 'express-fileupload'
import FormData from 'form-data'

import { CLOUDINARY_CONFIG } from '../config'

const router = express.Router()
router.use(fileUpload())
cloudinary.config(CLOUDINARY_CONFIG)

// ################################## User
// ##################################
// ##################################
router.post('/api/users/login', async (req, res) => {
    try {
        const { email, password } = req.body
        if (!email || !password) {
            return res.status(400).json({
                message: 'Fields required!',
            })
        }

        const user = await UserService.findByMail(email)
        if (!user) {
            return res.status(401).json({
                message: 'Invalid credentials!',
            })
        }

        if (!user.verified) {
            return res.status(401).json({
                message: 'Please await account verification!',
            })
        }

        const isPasswordValid = await bcrypt.compare(password, user.password)
        if (!isPasswordValid) {
            return res.status(401).json({
                message: 'Invalid credentials!',
            })
        }

        const token = await UserService.generateAccessToken(user.email, 'login')
        return res.status(200).json({
            message: 'Login successful!',
            token: token,
        })
    } catch (err) {
        return res.status(500).send('Internal Server Error!')
    }
})

router.post('/api/users/register', async (req, res) => {
    try {
        const { username, email, password } = req.body
        if (!email || !password) {
            return res.status(400).json({
                message: 'Fields required!',
            })
        }

        const existingMail = await UserService.findByMail(email)
        if (existingMail) {
            return res.status(409).json({
                message: 'Email already in use!',
            })
        }

        if (username) {
            const existingUser = await UserService.findByUsername(username)
            if (existingUser) {
                return res.status(409).json({
                    message: 'Username already in use!',
                })
            }
        }

        const hashedPassword = await bcrypt.hash(password, 10)
        const user = await UserService.createUser(username, email, hashedPassword)
        if (!user) {
            throw Error
        }

        const mailSuccess = await UserService.sendConfirmationMail(email)
        if (!mailSuccess) {
            throw Error
        }

        return res.status(201).json({
            message: 'User created successfully!',
        })
    } catch (err) {
        return res.status(500).send('Internal Server Error!')
    }
})

router.get(
    '/api/users/confirm',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(404).json({
                    message: 'User ID not found!',
                })
            }

            const user = await UserService.findByID(userId)
            if (!user) {
                return res.status(404).json({
                    message: 'User could not be found!',
                })
            }

            const username = user.username as string
            const usermail = user.email

            const confirmed = await UserService.confirmUser(username)
            const htmlResponse = UserService.getConfirmedPage(confirmed)

            if (confirmed) {
                const mailSuccess = await UserService.sendVerificationMail(username, usermail)
                if (!mailSuccess) {
                    throw Error
                }
                return res.status(200).send(htmlResponse)
            } else {
                return res.status(500).send(htmlResponse)
            }
        } catch (err: any) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.get(
    '/api/users/verify',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const adminId = req.adminId
            if (!adminId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const username = req.query.username as string
            if (!username) {
                return res.status(404).json({
                    message: 'Username could not be resolved!',
                })
            }
            const user = await UserService.findByUsername(username)
            if (!user) {
                return res.status(404).json({
                    message: 'User could not be found!',
                })
            }

            const usermail = user.email

            const verified = await UserService.verifyUser(username)
            const htmlResponse = UserService.getVerifiedPage(verified)

            if (verified) {
                const mailSuccess = await UserService.sendVerificationConfirmation(usermail)
                if (!mailSuccess) {
                    throw Error
                }
                return res.status(200).send(htmlResponse)
            } else {
                return res.status(500).send(htmlResponse)
            }
        } catch (err) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.delete(
    '/api/users/delete',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const deleteSuccess = await UserService.deleteUser(id)
            if (deleteSuccess) {
                return res.status(200).json({
                    message: 'User deleted successfully!',
                })
            }
        } catch (err) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.get(
    '/api/users/current',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const currentUser = await UserService.findByID(id)
            if (!currentUser) {
                return res.status(404).json({
                    message: 'User not found!',
                })
            }

            return res.status(200).json({
                user: currentUser,
                message: 'User found!',
            })
        } catch (err) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.patch(
    '/api/users/update/name',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { name } = req.body

            if (typeof name !== 'string') {
                return res.status(400).json({
                    message: 'Invalid name format!',
                })
            }

            const updateSuccess = await UserService.updateName(name, id)
            if (!updateSuccess) {
                return res.status(400).json({
                    message: 'Name could not be updated!',
                })
            }

            return res.status(200).json({
                message: 'Name successfully updated!',
            })
        } catch (err) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.patch(
    '/api/users/update/username',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { username } = req.body

            if (typeof username !== 'string') {
                return res.status(400).json({
                    message: 'Invalid username format!',
                })
            }

            const existingUser = await UserService.findByUsername(username)
            if (existingUser) {
                return res.status(409).json({
                    message: 'Username already in use!',
                })
            }

            const updateSuccess = await UserService.updateUsername(username, id)
            if (!updateSuccess) {
                return res.status(400).json({
                    message: 'Username could not be updated!',
                })
            }

            return res.status(200).json({
                message: 'Username successfully updated!',
            })
        } catch (err) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.patch(
    '/api/users/update/institution',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { institution } = req.body

            if (typeof institution !== 'string') {
                return res.status(400).json({
                    message: 'Invalid institution format!',
                })
            }

            const updateSuccess = await UserService.updateInstitution(institution, id)
            if (!updateSuccess) {
                return res.status(400).json({
                    message: 'Institution could not be updated!',
                })
            }

            return res.status(200).json({
                message: 'Institution successfully updated!',
            })
        } catch (err) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.patch(
    '/api/users/update/email',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { newMail } = req.body

            const existingMail = await UserService.findByMail(newMail)
            if (existingMail) {
                return res.status(409).json({
                    message: 'Email already in use!',
                })
            }

            const updateSuccess = await UserService.updateMail(newMail, id)
            if (!updateSuccess) {
                return res.status(400).json({
                    message: 'Email could not be updated!',
                })
            }

            return res.status(200).json({
                message: 'Email successfully updated!',
            })
        } catch (err) {
            return res.status(500).send('Internal Server Error.')
        }
    }
)

router.patch(
    '/api/users/update/password',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const user = await UserService.findByID(id)
            if (!user) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { newPass, oldPass } = req.body

            const isPasswordValid = await bcrypt.compare(oldPass, user.password)
            if (!isPasswordValid) {
                return res.status(401).json({
                    message: 'Invalid password!',
                })
            }

            const newHashedPass = await bcrypt.hash(newPass, 10)
            const updateSuccess = await UserService.updatePassword(newHashedPass, id)
            if (!updateSuccess) {
                return res.status(400).json({
                    message: 'Password could not be updated!',
                })
            }

            return res.status(200).json({
                message: 'Password successfully updated!',
            })
        } catch (err) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.post(
    '/api/users/authpass',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const user = await UserService.findByID(id)
            if (!user) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { password } = req.body

            const isPasswordValid = await bcrypt.compare(password, user.password)
            if (!isPasswordValid) {
                return res.status(401).json({
                    message: 'Invalid password!',
                })
            } else {
                return res.status(200).json({
                    message: 'Password authenticated!',
                })
            }
        } catch (err) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.post(
    '/api/users/authtoken',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            return res.status(200).json({
                message: 'Token authenticated!',
            })
        } catch (err: any) {
            return res.status(500).send('Internal Server Error!')
        }
    }
)

router.post(
    '/api/users/update/img',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const id = req.userId
            if (!id) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }
            if (!req.files || Object.keys(req.files).length === 0) {
                return res.status(400).json({
                    message: 'Img file could not be found!',
                })
            }

            const signParams = {
                timestamp: Math.round(new Date().getTime() / 1000),
                eager: 'g_face,c_crop,ar_1:1,z_0.9/w_400,h_400',
                public_id: `users/avatars/${req.userId}`,
            }
            const signature = cloudinary.utils.api_sign_request(
                signParams,
                CLOUDINARY_CONFIG.api_secret
            )
            if (typeof signature !== 'string') {
                throw new Error('Error generating Cloudinary signature!')
            }

            const imgFile: any = req.files.image

            const formData = new FormData()
            formData.append('file', imgFile.data, {
                filename: imgFile.name,
                contentType: imgFile.mimetype,
            })
            formData.append('timestamp', signParams.timestamp.toString())
            formData.append('eager', signParams.eager)
            formData.append('public_id', signParams.public_id)
            formData.append('signature', signature)
            formData.append('api_key', CLOUDINARY_CONFIG.api_key)

            const cloudinaryRes = await axios.post(
                `https://api.cloudinary.com/v1_1/${CLOUDINARY_CONFIG.cloud_name}/image/upload`,
                formData,
                {
                    headers: {
                        ...formData.getHeaders(),
                    },
                }
            )

            const imgurl: string = cloudinaryRes.data.eager[0].secure_url

            const updateSuccess = UserService.updateImgUrl(imgurl, id)
            if (!updateSuccess) {
                return res.status(400).json({
                    message: 'User image could not be updated!',
                })
            }
            return res.status(200).json({
                message: 'User image successfully updated!',
            })
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
                return res.status(err.response.status).json({
                    message: err.message,
                })
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

// ################################## Graphs
// ##################################
// ##################################
router.post(
    '/api/users/graphs/',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { graph } = req.body

            if (graph) {
                console.log('graph is da')
            }

            const saveSuccess = await UserService.saveGraph(userId, graph)
            if (!saveSuccess) {
                return res.status(400).json({
                    message: 'Graph could not be saved!',
                })
            }

            return res.status(201).json({
                message: 'Graph saved successfully!',
            })
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
                return res.status(err.response.status).json({
                    message: err.message,
                })
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

router.delete(
    '/api/users/graphs/:graphId',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { graphId } = req.params

            const deleteSuccess = await UserService.deleteGraph(graphId)
            if (!deleteSuccess) {
                return res.status(400).json({
                    message: 'Graph could not be deleted!',
                })
            }

            return res.status(200).json({
                message: 'Graph deleted successfully!',
            })
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
                return res.status(err.response.status).json({
                    message: err.message,
                })
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

router.get(
    '/api/users/graphs',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const graphs = await UserService.getGraphsByUserID(userId)

            return res.status(200).json({
                message: 'Graphs retrieved successfully!',
                graphs: graphs,
            })
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
                return res.status(err.response.status).json({
                    message: err.message,
                })
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

// ################################## Uploads
// ##################################
// ##################################
router.get(
    '/api/users/uploads/list',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const uploads = await UserService.getUploadsByUserID(userId)

            if (uploads.length === 0) {
                return res.status(200).json({
                    message: 'No upload processes found!'
                })
            }

            return res.status(200).json({
                message: 'Upload list retrieved successfully!',
                uploads: uploads,
            })
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

router.get(
    '/api/users/uploads/:uploadId',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { uploadId } = req.params

            const upload = await UserService.getUploadByID(userId, uploadId)

            if (upload) {
                console.log(upload.processing)
            }

            return res.status(200).json({
                message: 'Upload retrieved successfully!',
                upload: upload,
            })
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

router.post(
    '/api/users/uploads/create',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { csvTable, fileId } = req.body

            const upload = await UserService.createUpload(userId, csvTable, fileId)
            if (!upload) {
                return res.status(400).json({
                    message: 'Upload process could not be saved!',
                })
            }

            return res.status(201).json({
                upload: upload,
                message: 'Upload process saved successfully!',
            })
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

router.patch(
    '/api/users/uploads/:uploadId',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { uploadId } = req.params
            const updates = req.body

            const updateSuccess = await UserService.updateUploadFields(userId, uploadId, updates)

            if (updateSuccess) {
                return res.status(200).json({
                    updateSuccess: true,
                    message: 'Upload process updated successfully!',
                })
            } else {
                return res.status(404).json({
                    updateSuccess: false,
                    message: 'Upload process not found!',
                })
            }
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
                return res.status(err.response.status).json({
                    message: err.message,
                })
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

router.delete(
    '/api/users/uploads/:uploadId',
    UserService.authenticateToken,
    async (req: IGetUserAuthInfoRequest, res: Response) => {
        try {
            const userId = req.userId
            if (!userId) {
                return res.status(401).json({
                    message: 'Unauthorized access!',
                })
            }

            const { uploadId } = req.params

            const deleteSuccess = await UserService.deleteUpload(userId, uploadId)
            if (!deleteSuccess) {
                return res.status(400).json({
                    deleteSuccess: false,
                    message: 'Upload process could not be deleted!',
                })
            }

            return res.status(200).json({
                deleteSuccess: true,
                message: 'Upload process deleted successfully!',
            })
        } catch (err: any) {
            if (err.response) {
                console.error('error: ', err.response.data)
                return res.status(err.response.status).json({
                    message: err.message,
                })
            }
            return res.status(500).json('Internal server error!')
        }
    }
)

// Additional API endpoints for updating, deleting users, etc.

export default router
