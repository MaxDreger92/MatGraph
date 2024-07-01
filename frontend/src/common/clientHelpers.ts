import client from '../client'
import toast from 'react-hot-toast'
import { UploadListItem, IWorkflow, IUpload, IDictionary } from '../types/workspace.types'

// ################################## Uploads
// ##################################
// ##################################
export const fetchUpload = async (uploadId: string): Promise<IUpload | void> => {
    try {
        const response = await client.getUploadData(uploadId)
        if (!response || !response.data.upload) {
            toast.error('Error while retrieving upload process!')
            return
        }

        return response.data.upload as IUpload
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const fetchUploadList = async (): Promise<UploadListItem[] | void> => {
    try {
        const response = await client.getUploadList()

        if (!response || !response.data.message) {
            toast.error('Error while retrieving upload processes!')
            return
        }

        return response.data.uploadList as UploadListItem[]
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const createUpload = async (csvTable: string): Promise<IUpload | void> => {
    try {
        const response = await client.createUpload(csvTable)

        if (!response || !response.data.message) {
            toast.error('Error while saving upload process!')
            return
        }

        return response.data.upload as IUpload
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const updateUpload = async (
    uploadId: string,
    updates: Partial<IUpload>
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

export const fetchWorkflows = async (): Promise<IWorkflow[] | void> => {
    try {
        const response = await client.getWorkflows()

        if (!response || !response.data.workflows || !response.data.message) {
            toast.error('Error while retrieving workflows!')
            return
        }

        return response.data.workflows as IWorkflow[]
    } catch (err: any) {
        toast.error(err.message)
    }
}

// ################################## Django API
// ##################################
// ##################################

export const requestExtractLabels = async (
    file: File,
    context: string
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractLabels(file, context)
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
    context: string,
    fileLink: string,
    fileName: string,
    labelDict: IDictionary
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractAttributes(
            labelDict,
            context,
            fileLink,
            fileName
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
    context: string,
    fileLink: string,
    fileName: string,
    attributeDict: IDictionary
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractNodes(
            attributeDict,
            context,
            fileLink,
            fileName
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
    context: string,
    fileLink: string,
    fileName: string,
    workflow: string
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractGraph(workflow, context, fileLink, fileName)
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
    context: string,
    fileLink: string,
    fileName: string,
    workflow: string
): Promise<boolean | void> => {
    try {
        const response = await client.requestImportGraph(workflow, context, fileLink, fileName)
        if (!response || !response.data.processing) {
            toast.error('Process could not be started')
            return
        }

        return response.data.processing as boolean
    } catch (err: any) {
        toast.error(err.message)
    }
}
