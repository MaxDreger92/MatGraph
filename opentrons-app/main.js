const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const fs = require('fs')
const path = require('node:path')

const preloadPath = path.join(__dirname, 'preload.js')

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 900,
        webPreferences: {
            contextIsolation: true,
            nodeIntegration: false,
            preload: preloadPath,
        },
    })

    const startUrl = process.env.ELECTRON_START_URL || `file://${path.join(__dirname, 'build', 'index.html')}`
    mainWindow.loadURL(startUrl)

    mainWindow.webContents.openDevTools()
}

app.whenReady()
    .then(() => {
        createWindow()

        app.on('activate', () => {
            if (BrowserWindow.getAllWindows().length === 0) {
                createWindow()
            }
        })
    })
    .catch((error) => {
        console.error('Error during app initialization:', error)
    })

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit()
    }
})

ipcMain.handle('fs-access', async (event, path) => {
    try {
        await fs.promises.access(path)
        return { success: true }
    } catch (error) {
        return { success: false, error: error.message }
    }
})

ipcMain.handle('fs-stat', async (event, path) => {
    try {
        const stats = await fs.promises.stat(path)
        return {
            success: true,
            data: {
                isFile: stats.isFile(),
                isDirectory: stats.isDirectory(),
                size: stats.size,
                createdAt: stats.birthtime,
                modifiedAt: stats.mtime,
            },
        }
    } catch (error) {
        return { success: false, error: error.message }
    }
})

ipcMain.handle('fs-readFile', async (event, filePath, options) => {
    try {
        const data = await fs.promises.readFile(filePath, { encoding: 'utf-8', ...options })
        return { success: true, data: data }
    } catch (error) {
        return { success: false, error: error.message }
    }
})

ipcMain.handle('fs-readdir', async (event, dirPath) => {
    try {
        const files = await fs.promises.readdir(dirPath)
        return { success: true, data: files }
    } catch (error) {
        return { success: false, error: error.message }
    }
})

ipcMain.handle('select-folder', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
        properties: ['openDirectory'],
    })
    return canceled ? null : filePaths[0]
})

ipcMain.handle('select-file-or-folder', async () => {
    const { canceled, filePaths } = await dialog.showOpenDialog({
        properties: ['openFile', 'openDirectory'],
    })
    return canceled ? null : filePaths[0]
})
