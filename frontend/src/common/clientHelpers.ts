import client from '../client'
import toast from 'react-hot-toast'
import { UploadListItem, Graph, Upload, Dictionary } from '../types/workspace.types'

// ################################## Uploads
// ##################################
// ##################################
export const fetchUpload = async (uploadId: string, setUpload?: any): Promise<Upload | void> => {
    try {
        const data = await client.getUpload(uploadId)
        if (!data || !data.upload) {
            toast.error('Error while retrieving upload process!')
            return
        }

        if (setUpload) {
            setUpload(data.upload)
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

        if (!data.uploads) return []
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

export const deleteUpload = async (
    uploadId: string,
): Promise<boolean | void> => {
    try {
        const response = await client.deleteUpload(uploadId)

        if (!response || !response.data.deleteSuccess) {
            toast.error('Upload process could not be deleted')
            return
        }

        return response.data.deleteSuccess
    } catch (err: any) {
        toast.error(err.message)
    }
}

// ################################## Graphs
// ##################################
// ##################################
export const saveGraph = async (graph: string): Promise<void> => {
    try {
        const response = await client.saveGraph(graph)

        if (response) {
            toast.success(response.data.message)
        }
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const updateGraph = async (graphId: string, updates: Partial<Graph>): Promise<void> => {
    try {
        const response = await client.updateGraph(graphId, updates)

        if (response) {
            toast.success(response.data.message)
        }
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const deleteGraph = async (graphId: string): Promise<void> => {
    try {
        const response = await client.deleteGraph(graphId)

        if (response) {
            toast.success(response.data.message)
        }
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const fetchGraphs = async (): Promise<Graph[] | void> => {
    try {
        const response = await client.getGraphs()

        if (!response || !response.data.graphs || !response.data.message) {
            toast.error('Error while retrieving graphs!')
            return
        }

        return response.data.graphs as Graph[]
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
    fileId: string,
    labelDict: Dictionary
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractAttributes(
            uploadId,
            context,
            fileId,
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
    fileId: string,
    attributeDict: Dictionary
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractNodes(
            uploadId,
            context,
            fileId,
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
    fileId: string,
    graph: string
): Promise<boolean | void> => {
    try {
        const response = await client.requestExtractGraph(uploadId, context, fileId, graph)
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
    fileId: string,
    graph: string
): Promise<boolean | void> => {
    try {
        const response = await client.requestImportGraph(uploadId, context, fileId, graph)
        if (!response || !response.data.processing) {
            toast.error('Process could not be started')
            return
        }

        return response.data.processing as boolean
    } catch (err: any) {
        toast.error(err.message)
    }
}

export const cancelTask = async (
    uploadId: string,
): Promise<boolean | void> => {
    try {
        const response = await client.cancelTask(uploadId)
        if (!response || !response.data.cancelled) {
            toast.error('Task could not be cancelled! \n Upload process might be corrupted')
        } else {
            toast.success('Task successfully cancelled!')
        }
    } catch (err: any) {
        toast.error('Task could not be cancelled! \n Upload process might be corrupted')
    }
}
