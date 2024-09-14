const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
    ipcRenderer: {
        invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
    },
    fs: {
        access: (path) => ipcRenderer.invoke('fs-access', path),
        stat: (path) => ipcRenderer.invoke('fs-stat', path),
        readFile: (path, options) => ipcRenderer.invoke('fs-readFile', path, options),
        readdir: (path) => ipcRenderer.invoke('fs-readdir', path),
    },
});
