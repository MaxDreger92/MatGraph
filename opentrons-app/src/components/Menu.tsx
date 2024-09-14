import { useContext, useRef, useState } from 'react'
import EquipmentMenu from './EquipmentMenu'
import Button from './Button'
import ButtonRound from './ButtonRound'
import { OpentronsContext } from '../context/OpentronsContext'
import { generateLabwareWells, getLabwareData } from '../functions/labware.functions'
import { OpentronsSetup } from '../types/opentrons.types'
import { ILabware } from '../types/labware.types'
import { getOpentronsSetupData } from '../functions/opentrons.functions'

const { ipcRenderer, fs } = window.electron

interface MenuProps {}

export default function Menu(props: MenuProps) {
    const [menuOpen, setMenuOpen] = useState(false)
    const [activeSetup, setActiveSetup] = useState<number | null>(null)
    const configPath = useRef<string | null>(null)
    const setupPath = useRef<string | null>(null)
    const labwarePath = useRef<string | null>(null)
    const chemicalsPath = useRef<string | null>(null)

    const {
        opentronsSetupList,
        setOpentronsSetupList,
        patchCurrentOpentronsSetup,
        setCurrentOpentronsSetup,
        labwareList,
        setLabwareList,
    } = useContext(OpentronsContext)

    const handleOpenMenu = () => {
        setMenuOpen((prev) => !prev)
    }

    const handleLoadConfig = async () => {
        try {
            const folderPath = await ipcRenderer.invoke('select-folder')

            if (!folderPath) {
                throw Error
            }

            configPath.current = folderPath
            //might set conditional
            setupPath.current = folderPath.concat('/opentrons_setup')
            labwarePath.current = folderPath.concat('/labware')
            chemicalsPath.current = folderPath.concat('/chemicals')

            loadSetup(true)
            loadLabware(true)
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
            // loadChemicals(isDirectory)
        } catch (err: any) {
            console.error('Error while loading setup!')
        }
    }

    const loadSetup = async (fromDirectory: boolean) => {
        try {
            if (!setupPath.current) {
                throw Error
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

                    console.log('getting opentrons setup data in')
                    const setupData = getOpentronsSetupData(setupFile.data)
                    console.log('getting opentrons setup data out')
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
                console.log(newSetups.length)
                setOpentronsSetupList(newSetups, true)
            }
        } catch (err: any) {
            console.error(`Error while loading opentrons setup: ${err.message}`)
            return
        }
    }

    const loadLabware = async (fromDirectory: boolean) => {
        try {
            if (!labwarePath.current) {
                throw Error('Path')
            }

            console.log(labwarePath.current)

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

                    const labwareData = getLabwareData(labwareFile.data)

                    newLabwares.push(labwareData)
                } catch (err: any) {
                    throw Error(err.message)
                }
            }

            setLabwareList(newLabwares)
        } catch (err: any) {
            console.error(`Error while loading labware: ${err.message}`)
            return
        }
    }

    const handleSetActiveSetup = (index: number) => {
        if (labwareList.length > index) {
            setCurrentOpentronsSetup(index)
            setActiveSetup(index)
        }
    }

    return (
        <div
            style={{
                position: 'absolute',
                left: 0,
                width: '25%',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
            }}
        >
            <div
                style={{
                    position: 'absolute',
                    top: '1.3%',
                    left: '5%',
                    display: 'flex',
                    flexDirection: 'column',
                    paddingBottom: 10,
                    zIndex: 10,
                    backgroundColor: menuOpen ? '#f5f5f5' : 'transparent',
                    filter: menuOpen ? 'drop-shadow(0px 2px 5px rgba(0, 0, 0, 0.15))' : 'none',
                    borderRadius: 10,
                }}
            >
                <Button label='Load Configuration' fn={handleOpenMenu} active={menuOpen} />
                {menuOpen && (
                    <>
                        <Button label='From Folder' fn={handleLoadConfig} />
                        <Button label='Setup' fn={handleLoadSetup} />
                        <Button label='Labware' fn={handleLoadLabware} />
                        <Button label='Chemicals' fn={handleLoadChemicals} />
                    </>
                )}
            </div>
            <div
                style={{
                    position: 'absolute',
                    display: 'flex',
                    flexDirection: 'row',
                    gap: '8px',
                    top: '4%',
                    marginLeft: '300%',
                }}
            >
                {opentronsSetupList.map((setup, index) => (
                    <ButtonRound key={index} label={index + 1} fn={handleSetActiveSetup} active={index === activeSetup} argumentList={[index]}/>
                ))}
            </div>
            <EquipmentMenu />
        </div>
    )
}
