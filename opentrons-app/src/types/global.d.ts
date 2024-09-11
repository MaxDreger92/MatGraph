export {}

declare global {
    interface Window {
        electron: {
            ipcRenderer: {
                invoke: (channel: string, ...args: any[]) => Promise<any>;
                on: (channel: string, listener: (event: any, ...args: any[]) => void) => void;
            };
            fs: {
                access: (path: string) => Promise<{ success: boolean; error?: string }>;
                readFile: (
                    path: string,
                    options: { encoding?: string | null; flag?: string } | string
                ) => Promise<{ success: boolean; data?: string; error?: string }>;
            };
        };
    }
}
