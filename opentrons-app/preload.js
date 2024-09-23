const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
    ipcRenderer: {
        invoke: (channel, ...args) => ipcRenderer.invoke(channel, ...args),
        on: (channel, listener) => ipcRenderer.on(channel, listener),
        removeListener: (channel, listener) => ipcRenderer.removeListener(channel, listener),
        send: (channel, ...args) => ipcRenderer.send(channel, ...args), // Added send method
    },
    fs: {
        access: (path) => ipcRenderer.invoke('fs-access', path),
        stat: (path) => ipcRenderer.invoke('fs-stat', path),
        readFile: (path, options) => ipcRenderer.invoke('fs-readFile', path, options),
        readdir: (path) => ipcRenderer.invoke('fs-readdir', path),
        writeFile: (filePath, data, options) => ipcRenderer.invoke('fs-writeFile', filePath, data, options),
    },
});
