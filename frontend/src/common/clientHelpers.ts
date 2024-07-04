import client from '../client'
import toast from 'react-hot-toast'
import { UploadListItem, Workflow, Upload, Dictionary } from '../types/workspace.types'

// ################################## Uploads
// ##################################
// ##################################
export const fetchUpload = async (uploadId: string): Promise<Upload | void> => {
    try {
        const data = await client.getUpload(uploadId)
        if (!data || !data.upload) {
            toast.error('Error while retrieving upload process!')
            return
        }

        return data.upload as Upload
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const fetchUploads = async (): Promise<Upload[] | void> => {
    try {
        const data = await client.getUploads()

        if (!data || !data.message) {
            toast.error('Error while retrieving upload processes!')
            return
        }

        return data.uploads as Upload[]
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const createUpload = async (csvTable: string): Promise<Upload | void> => {
    try {
        const response = await client.createUpload(csvTable)

        if (!response || !response.data.message) {
            toast.error('Error while saving upload process!')
            return
        }

        return response.data.upload as Upload
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const updateUpload = async (
    uploadId: string,
    updates: Partial<Upload>
): Promise<boolean | void> => {
    try {
        const response = await client.updateUpload(uploadId, updates)

        if (!response || !response.data.updateSuccess) {
            toast.error('Upload process could not be updated')
            return
        }

        return response.data.updateSuccess
    } catch (err: any) {
        toast.error(err.message)
    }
}

// ################################## Workflows
// ##################################
// ##################################
export const saveWorkflowToHistory = async (workflow: string): Promise<void> => {
    try {
        const response = await client.saveWorkflow(workflow)

        if (response) {
            toast.success(response.data.message)
        }
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const deleteWorkflowFromHistory = async (workflowId: string): Promise<void> => {
    try {
        const response = await client.deleteWorkflow(workflowId)

        if (response) {
            toast.success(response.data.message)
        }
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const fetchWorkflows = async (): Promise<Workflow[] | void> => {
    try {
        const response = await client.getWorkflows()

        if (!response || !response.data.workflows || !response.data.message) {
            toast.error('Error while retrieving workflows!')
            return
        }

        return response.data.workflows as Workflow[]
    } catch (err: any) {
        toast.error(err.message)
    }
}

// ################################## Django API
// ##################################
// ##################################

export const requestFileUpload = async (
    file: File,
    csvTable: string
): Promise<Upload | void> => {
    try {   
        const response = await client.requestFileUpload(file, csvTable)
        if (!response || !response.data.upload) {
            toast.error('File could not be uploaded!')
            return
        }

        return response.data.upload as Upload
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const requestExtractLabels = async (
    uploadId: string,
    context: string,
    fileId: string
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractLabels(uploadId, context, fileId)
        if (!response || !response.data.processing) {
            toast.error('Process could not be started!')
            return
        }

        return response.data.processing as boolean
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const requestExtractAttributes = async (
    uploadId: string,
    context: string,
    fileLink: string,
    fileName: string,
    labelDict: Dictionary
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractAttributes(
            uploadId,
            context,
            fileLink,
            fileName,
            labelDict
        )
        if (!response || !response.data.processing) {
            toast.error('Process could not be started!')
            return
        }

        return response.data.processing as boolean
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const requestExtractNodes = async (
    uploadId: string,
    context: string,
    fileLink: string,
    fileName: string,
    attributeDict: Dictionary
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractNodes(
            uploadId,
            context,
            fileLink,
            fileName,
            attributeDict
        )
        if (!response || !response.data.processing) {
            toast.error('Process could not be started')
            return
        }

        return response.data.processing as boolean
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const requestExtractGraph = async (
    uploadId: string,
    context: string,
    fileLink: string,
    fileName: string,
    workflow: string
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractGraph(uploadId, context, fileLink, fileName, workflow)
        if (!response || !response.data.processing) {
            toast.error('Process could not be started')
            return
        }

        return response.data.processing as boolean
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const requestImportGraph = async (
    uploadId: string,
    context: string,
    fileLink: string,
    fileName: string,
    workflow: string
): Promise<boolean | void> => {
    try {
        const response = await client.requestImportGraph(uploadId, context, fileLink, fileName, workflow)
        if (!response || !response.data.processing) {
            toast.error('Process could not be started')
            return
        }

        return response.data.processing as boolean
    } catch (err: any) {
        toast.error(err.message)
    }
}
