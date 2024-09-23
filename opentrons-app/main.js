const { isDisabled } = require('@testing-library/user-event/dist/cjs/utils/index.js')
const { app, BrowserWindow, ipcMain, dialog, Menu } = require('electron')
const fs = require('fs')
const path = require('node:path')

app.setName('ot2-App')

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

    // Remove or comment out this line if you don't want the DevTools to open automatically
    // mainWindow.webContents.openDevTools()
}

function buildMenu() {
    const menuTemplate = [
        {
            label: app.name,
            submenu: [
                { role: 'about' },
                { type: 'separator' },
                { role: 'services' },
                { type: 'separator' },
                { role: 'hide' },
                { role: 'hideOthers' },
                { role: 'unhide' },
                { type: 'separator' },
                { role: 'quit' },
            ],
        },
        {
            label: 'Configuration && Setup',
            submenu: [
                {
                    label: 'Load File/Folder',
                    submenu: [
                        {
                            label: 'Config',
                            click() {
                                BrowserWindow.getAllWindows()[0].webContents.send('menu-load-from-folder')
                            },
                        },
                        {
                            label: 'Opentrons Setup',
                            click() {
                                BrowserWindow.getAllWindows()[0].webContents.send('menu-load-setup')
                            },
                        },
                        {
                            label: 'Labware',
                            click() {
                                BrowserWindow.getAllWindows()[0].webContents.send('menu-load-labware')
                            },
                        },
                        {
                            label: 'Chemicals',
                            click() {
                                BrowserWindow.getAllWindows()[0].webContents.send('menu-load-chemicals')
                            },
                        },
                    ],
                },
                { type: 'separator' },
                {
                    label: 'Reset Current Configuration',
                    enabled: !configIsEmpty,
                    click() {
                        BrowserWindow.getAllWindows()[0].webContents.send('menu-reset-configuration')
                    },
                },
            ],
        },
        {
            label: 'View',
            submenu: [
                { role: 'reload' },
                { role: 'forceReload' },
                { type: 'separator' },
                { role: 'toggleDevTools' }, // This restores the Option+Command+I shortcut
                { type: 'separator' },
                { role: 'resetZoom' },
                { role: 'zoomIn' },
                { role: 'zoomOut' },
                { type: 'separator' },
                { role: 'togglefullscreen' },
            ],
        },
        {
            label: 'Window',
            role: 'windowMenu',
        },
        {
            label: 'Help',
            role: 'help',
            submenu: [
                {
                    label: 'Learn More',
                    click: async () => {
                        const { shell } = require('electron')
                        await shell.openExternal('https://electronjs.org')
                    },
                },
            ],
        },
    ]

    const menu = Menu.buildFromTemplate(menuTemplate)
    Menu.setApplicationMenu(menu)
}

app.whenReady()
    .then(() => {
        createWindow()
        buildMenu()

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

let configIsEmpty = true

ipcMain.on('config-empty', () => {
    configIsEmpty = true;
    buildMenu();
});

ipcMain.on('config-not-empty', () => {
    configIsEmpty = false;
    buildMenu();
});

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

ipcMain.handle('fs-writeFile', async (event, filePath, data, options) => {
    try {
        await fs.promises.writeFile(filePath, data, { encoding: 'utf-8', ...options })
        return { success: true }
    } catch (error) {
        return { success: false, error: error.message }
    }
})
