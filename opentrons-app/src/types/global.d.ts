export {}

declare global {
    interface Window {
        electron: {
            ipcRenderer: {
                invoke: (channel: string, ...args: any[]) => Promise<any>
                on: (channel: string, listener: (event: any, ...args: any[]) => void) => void
                removeListener: (channel: string, listener: (event: any, ...args: any[]) => void) => void
                send: (channel: string, ...args: any[]) => void // Added send method
            }
            fs: {
                access: (path: string) => Promise<{ success: boolean; error?: string }>
                stat: (path: string) => Promise<{
                    success: boolean
                    data?: {
                        isFile: boolean
                        isDirectory: boolean
                        size: number
                        createdAt: Date
                        modifiedAt: Date
                    }
                    error?: string
                }>
                readFile: (
                    path: string,
                    options: { encoding?: string | null; flag?: string } | string
                ) => Promise<{ success: boolean; data?: string; error?: string }>
                readdir: (path: string) => Promise<{ success: boolean; data?: string[]; error?: string }>
                writeFile: (
                    filePath: string,
                    data: string,
                    options?: { encoding?: string | null; mode?: number | string; flag?: string }
                ) => Promise<{ success: boolean; error?: string }>
            }
        }
    }
}

declare module 'react-icons/hi' {
    export * from 'react-icons'
}
declare module 'react-icons/ri' {
    export * from 'react-icons'
}
declare module 'react-icons/md' {
    export * from 'react-icons'
}
declare module 'react-icons/io5' {
    export * from 'react-icons'
}
declare module 'react-icons/vsc' {
    export * from 'react-icons'
}
