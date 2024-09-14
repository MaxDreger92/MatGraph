export {}

declare global {
    interface Window {
        electron: {
            ipcRenderer: {
                invoke: (channel: string, ...args: any[]) => Promise<any>
                on: (channel: string, listener: (event: any, ...args: any[]) => void) => void
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
            }
        }
    }
}
