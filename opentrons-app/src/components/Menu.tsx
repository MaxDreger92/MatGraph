import { useContext, useEffect, useRef, useState } from 'react'
import EquipmentMenu from './EquipmentMenu'
import Button from './Button'
import ButtonRound from './ButtonRound'
import { OpentronsContext } from '../context/OpentronsContext'
import { getLabwareDataFromFile } from '../functions/labware.functions'
import { ILabware } from '../types/labware.types'
import { getChemicalSetupData, getOpentronsSetupData, sortSetupListByName } from '../functions/configuration.functions'
import { ChemicalSetup, DefaultConfiguration, getNamedDefaultConfig, OpentronsSetup } from '../types/configuration.types'
import SetupMenu from './SetupMenu'
import { useSpring, animated } from 'react-spring'
import Detail from './Detail'

const { ipcRenderer, fs } = window.electron

interface MenuProps {
    focusMode: boolean
    split: number
}

export default function Menu(props: MenuProps) {
    const { focusMode, split } = props
    const [menuOpen, setMenuOpen] = useState(false)
    const configPath = useRef<string | null>(null)
    const setupPath = useRef<string | null>(null)
    const labwarePath = useRef<string | null>(null)
    const chemicalsPath = useRef<string | null>(null)

    const ipcListenersRegistered = useRef(false)

    const {
        labwareList,
        setLabwareList,
        currentConfig,
        setCurrentConfig,
        opentronsSetupList,
        setOpentronsSetupList,
        chemicalSetupList,
        setChemicalSetupList,
        setSelectedSlot,
    } = useContext(OpentronsContext)

    const handleLoadConfig = async () => {
        try {
            const folderPath = await ipcRenderer.invoke('select-folder')

            if (!folderPath) {
                return
            }

            configPath.current = folderPath
            //might set conditional
            setupPath.current = folderPath.concat('/opentrons_setup')
            labwarePath.current = folderPath.concat('/labware')
            chemicalsPath.current = folderPath.concat('/chemicals')

            loadSetup(true)
            loadLabware(true)
            loadChemicals(true)
        } catch (error) {
            console.error('Error loading folder: ', error)
            return
        }
    }

    const handleLoadSetup = async () => {
        try {
            const selectedPath = await ipcRenderer.invoke('select-file-or-folder')
            if (!selectedPath) {
                return
            }
            await fs.access(selectedPath)
            setupPath.current = selectedPath

            const stats = await fs.stat(selectedPath)
            if (!stats.success || !stats.data) {
                throw Error
            }

            const isDirectory = stats.data.isDirectory
            loadSetup(isDirectory)
        } catch (err: any) {
            console.error('Error while loading setup!')
        }
    }

    const handleLoadLabware = async () => {
        try {
            const selectedPath = await ipcRenderer.invoke('select-file-or-folder')
            if (!selectedPath) {
                return
            }
            await fs.access(selectedPath)
            labwarePath.current = selectedPath

            const stats = await fs.stat(selectedPath)
            if (!stats.success || !stats.data) {
                throw Error
            }

            const isDirectory = stats.data.isDirectory
            loadLabware(isDirectory)
        } catch (err: any) {
            console.error('Error while loading setup!')
        }
    }

    const handleLoadChemicals = async () => {
        try {
            const selectedPath = await ipcRenderer.invoke('select-file-or-folder')
            if (!selectedPath) {
                return
            }
            await fs.access(selectedPath)
            chemicalsPath.current = selectedPath

            const stats = await fs.stat(selectedPath)
            if (!stats.success || !stats.data) {
                throw Error
            }

            const isDirectory = stats.data.isDirectory
            loadChemicals(isDirectory)
        } catch (err: any) {
            console.error('Error while loading setup!')
        }
    }

    const loadSetup = async (fromDirectory: boolean) => {
        try {
            if (!setupPath.current) {
                return
            }

            const filePaths: string[] = []

            if (fromDirectory) {
                const setupFiles = await fs.readdir(setupPath.current)
                if (!setupFiles.success) {
                    throw Error
                }

                const fileNames: string[] = setupFiles.data as string[]
                fileNames.forEach((fileName) => filePaths.push(`${setupPath.current}/${fileName}`))
            } else {
                filePaths.push(setupPath.current)
            }

            const newSetups: OpentronsSetup[] = []

            for (const filePath of filePaths) {
                try {
                    await fs.access(filePath)

                    const setupFile = await fs.readFile(filePath, { encoding: 'utf-8' })
                    if (!setupFile.success || !setupFile.data) {
                        throw Error('setupFile')
                    }

                    const filenameWithExtension = filePath.split('/').pop() || 'unknown'
                    const filename = filenameWithExtension.split('.').shift() || 'unknown'

                    const setupData = getOpentronsSetupData(setupFile.data, filename)

                    if (!setupData) continue

                    newSetups.push(setupData)
                } catch (err: any) {
                    if (fromDirectory) {
                        continue
                    } else {
                        throw err
                    }
                }
            }

            if (newSetups.length > 0) {
                setOpentronsSetupList('replace', newSetups)
            }
        } catch (err: any) {
            console.error(`Error while loading opentrons setup: ${err.message}`)
            return
        }
    }

    const loadChemicals = async (fromDirectory: boolean) => {
        try {
            if (!chemicalsPath.current) {
                return
            }

            const filePaths: string[] = []

            if (fromDirectory) {
                const setupFiles = await fs.readdir(chemicalsPath.current)
                if (!setupFiles.success) {
                    throw Error
                }

                const fileNames: string[] = setupFiles.data as string[]
                fileNames.forEach((fileName) => filePaths.push(`${chemicalsPath.current}/${fileName}`))
            } else {
                filePaths.push(chemicalsPath.current)
            }

            const newSetups: ChemicalSetup[] = []

            for (const filePath of filePaths) {
                try {
                    await fs.access(filePath)

                    const setupFile = await fs.readFile(filePath, { encoding: 'utf-8' })
                    if (!setupFile.success || !setupFile.data) {
                        throw Error('setupFile')
                    }

                    const filenameWithExtension = filePath.split('/').pop() || 'unknown'
                    const filename = filenameWithExtension.split('.').shift() || 'unknown'

                    const setupData = getChemicalSetupData(setupFile.data, filename)

                    if (!setupData) continue

                    newSetups.push(setupData)
                } catch (err: any) {
                    if (fromDirectory) {
                        continue
                    } else {
                        throw err
                    }
                }
            }

            if (newSetups.length > 0) {
                setChemicalSetupList('replace', newSetups)
            }
        } catch (err: any) {
            console.error(`Error while loading chemicals setup: ${err.message}`)
            return
        }
    }

    const loadLabware = async (fromDirectory: boolean) => {
        try {
            if (!labwarePath.current) {
                throw Error('Path')
            }

            const filePaths: string[] = []

            if (fromDirectory) {
                const labwareFiles = await fs.readdir(labwarePath.current)
                if (!labwareFiles.success) {
                    throw Error('readdir')
                }

                const fileNames: string[] = labwareFiles.data as string[]

                for (const fileName of fileNames) {
                    const filePath = `${labwarePath.current}/${fileName}`

                    const stats = await fs.stat(filePath)
                    if (!stats.success || !stats.data) {
                        throw Error('stat')
                    }

                    const isDirectory = stats.data.isDirectory

                    if (isDirectory) continue

                    filePaths.push(filePath)
                }
            } else {
                filePaths.push(labwarePath.current)
            }

            const newLabwares: ILabware[] = []

            for (const filePath of filePaths) {
                try {
                    await fs.access(filePath)

                    const labwareFile = await fs.readFile(filePath, { encoding: 'utf-8' })
                    if (!labwareFile.success || !labwareFile.data) {
                        throw Error('readFile')
                    }

                    const filename = filePath.split('/').pop() || 'unknown'

                    const labwareData = getLabwareDataFromFile(labwareFile.data, filename)

                    newLabwares.push(labwareData)
                } catch (err: any) {
                    throw Error(err.message)
                }
            }

            setLabwareList('replace', newLabwares)
        } catch (err: any) {
            console.error(`Error while loading labware: ${err.message}`)
            return
        }
    }

    useEffect(() => {
        if (ipcListenersRegistered.current) {
            return
        }

        ipcListenersRegistered.current = true

        const { ipcRenderer } = window.electron

        const handleResetConfigFromMenu = () => {
            handleResetConfig()
        }

        const handleLoadFromFolderFromMenu = () => {
            handleLoadConfig()
        }

        const handleLoadSetupFromMenu = () => {
            handleLoadSetup()
        }

        const handleLoadLabwareFromMenu = () => {
            handleLoadLabware()
        }

        const handleLoadChemicalsFromMenu = () => {
            handleLoadChemicals()
        }

        ipcRenderer.on('menu-reset-configuration', handleResetConfigFromMenu)
        ipcRenderer.on('menu-load-from-folder', handleLoadFromFolderFromMenu)
        ipcRenderer.on('menu-load-setup', handleLoadSetupFromMenu)
        ipcRenderer.on('menu-load-labware', handleLoadLabwareFromMenu)
        ipcRenderer.on('menu-load-chemicals', handleLoadChemicalsFromMenu)

        return () => {
            ipcRenderer.removeListener('menu-reset-configuration', handleResetConfigFromMenu)
            ipcRenderer.removeListener('menu-load-from-folder', handleLoadFromFolderFromMenu)
            ipcRenderer.removeListener('menu-load-setup', handleLoadSetupFromMenu)
            ipcRenderer.removeListener('menu-load-labware', handleLoadLabwareFromMenu)
            ipcRenderer.removeListener('menu-load-chemicals', handleLoadChemicalsFromMenu)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const handleResetConfig = () => {
        setCurrentConfig(getNamedDefaultConfig([currentConfig.opentronsSetup.name, currentConfig.chemicalSetup.name]))
    }

    const handleResetOpentronsSetup = () => {
        setCurrentConfig({opentronsSetup: DefaultConfiguration.opentronsSetup})
    }

    const handleResetChemicalSetup = () => {
        setCurrentConfig({chemicalSetup: DefaultConfiguration.chemicalSetup})
    }

    const handleSetActiveSetup = (type: string, index: number) => {
        if (type === 'opentrons') {
            if (opentronsSetupList.length <= index) return

            handleResetOpentronsSetup()

            if (index === -1) return

            // setTimeout(() => {
                setCurrentConfig({ opentronsSetup: opentronsSetupList[index] })
            // }, 10)

            console.log(opentronsSetupList[index])
            
            
            setSelectedSlot(null)
        }
        if (type === 'chemicals') {
            if (chemicalSetupList.length <= index) return
            setCurrentConfig({ chemicalSetup: chemicalSetupList[index] })
        }
    }

    const handleCreateSetup = (type: string, name: string): number | null => {
        if (type === 'opentrons') {
            const newSetup: OpentronsSetup = {
                name: name,
                labware: []
            }
            const newSetupListPreview = sortSetupListByName([...opentronsSetupList, ...[newSetup]])
            const index = newSetupListPreview.findIndex((setup) => setup.name === name)

            setOpentronsSetupList('add', newSetup)
            return index
        }
        if (type === 'chemicals') {
            const newSetup: ChemicalSetup = {
                name: name,
                opentrons: [],
                arduino: []
            }
            const newSetupListPreview = sortSetupListByName([...chemicalSetupList, ...[newSetup]])
            const index = newSetupListPreview.findIndex((setup) => setup.name === name)

            setChemicalSetupList('add', newSetup)
            return index
        }
        return null
    }

    const handleSaveSetup = async (type: string, index: number) => {
        if (type === 'opentrons') {
            if (!setupPath.current) return
            const fileName = opentronsSetupList[index].name
            const filePath = `${setupPath.current}/${fileName}.json`
            const { name, ...setupToSaveWithoutName } = currentConfig.opentronsSetup
            const jsonData = JSON.stringify(setupToSaveWithoutName, null, 2)

            try {
                const result = await fs.writeFile(filePath, jsonData);
    
                if (result.success) {
                    setOpentronsSetupList('replaceIndex', currentConfig.opentronsSetup, index)
                    console.log('File saved successfully');
                } else {
                    console.error('Failed to save file:', result.error);
                }
            } catch (error) {
                console.error('Error during save operation:', error);
            }
        }
        if (type === 'chemicals') {
            if (!chemicalsPath.current) return
            const fileName = chemicalSetupList[index].name
            const filePath = `${chemicalsPath.current}/${fileName}.json`
            const { name, ...setupToSaveWithoutName } = currentConfig.chemicalSetup
            const jsonData = JSON.stringify(setupToSaveWithoutName, null, 2)

            try {
                const result = await fs.writeFile(filePath, jsonData);
    
                if (result.success) {
                    console.log('File saved successfully');
                } else {
                    console.error('Failed to save file:', result.error);
                }
            } catch (error) {
                console.error('Error during save operation:', error);
            }
        }
    }

    const equipmentMenuAnimation = useSpring({
        left: focusMode ? `-${split}%` : '0%',
        config: focusMode ? { tension: 400, friction: 26 } : { tension: 170, friction: 26 },
    })

    const setupMenuAnimation = useSpring({
        top: focusMode ? '-25%' : '2%',
        config: focusMode ? { tension: 400, friction: 26 } : { tension: 170, friction: 26 },
    })

    const detailMenuAnimation = useSpring({
        right: focusMode ? `-${100 - split}%` : '0%',
        config: focusMode ? { tension: 400, friction: 26 } : { tension: 170, friction: 26 },
    })

    return (
        <>
            {/* Equipment */}
            <animated.div
                style={{
                    position: 'absolute',
                    left: equipmentMenuAnimation.left,
                    top: 0,
                    width: `${split}%`,
                    height: '100%',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                {labwareList.length > 0 && <EquipmentMenu />}
            </animated.div>

            {/* Setup Menu */}
            <animated.div
                style={{
                    position: 'absolute',
                    left: `${split}%`,
                    top: setupMenuAnimation.top,
                    width: '50%',
                    height: '100%',
                }}
            >
                <SetupMenu
                    opentronsSetupList={opentronsSetupList}
                    chemicalSetupList={chemicalSetupList}
                    setActiveSetup={handleSetActiveSetup}
                    currentConfig={currentConfig}
                    createSetup={handleCreateSetup}
                    saveSetup={handleSaveSetup}
                />
            </animated.div>

            {/* Detail Page */}
            <animated.div
                style={{
                    position: 'absolute',
                    right: detailMenuAnimation.right,
                    top: 0,
                    width: `${50 - split}%`,
                    height: '100%',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                }}
            >
                {<Detail />}
            </animated.div>
        </>
    )
}