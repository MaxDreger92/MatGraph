import { useContext, useState } from 'react'
import Labwares from './EquipmentMenu'
import Button from './Button'
import { OpentronsContext } from '../context/OpentronsContext'
import { generateLabwareWells, getLabwareData } from '../functions/labware.functions'
import { Equipment } from '../types/opentrons.types'

const { ipcRenderer, fs } = window.electron;

interface MenuProps {}

export default function Menu(props: MenuProps) {
    const [configTabOpen, setConfigTabOpen] = useState(false)
    const [folderPath, setFolderPath] = useState()

    const { updateOpentrons } = useContext(OpentronsContext)

    const handleOpenConfigTab = () => {
        setConfigTabOpen((prevConfig) => !prevConfig)
    }

    const handleLoadFolder = async () => {
        try {
            const folderPath = await ipcRenderer.invoke('select-folder')

            if (!folderPath) {
                throw Error
            }

            loadOpentronsSetup(folderPath)
            
        } catch (error) {
            console.error('Error loading folder: ', error)
            return
        }
    }

    const handleLoadLabware = () => {
        // Add logic for loading labware files (if needed)
    }

    const handleLoadChemicals = () => {
        // Add logic for loading chemicals files (if needed)
    }

    const loadOpentronsSetup = async (folderPath: string) => {
        try {
            const pathOpentrons = `${folderPath}/opentrons_setup.json`

            await fs.access(pathOpentrons)

            const fileOpentrons = await fs.readFile(pathOpentrons, { encoding: 'utf-8' })
            if (!fileOpentrons.success) {
                throw new Error(`Reading file at path ${pathOpentrons} was unsuccessful`);
            }
            
            const opentronsData = JSON.parse(fileOpentrons.data as string)

            if (opentronsData.labware) {
                for (const labware of opentronsData.labware) {
                    const pathLabware = `${folderPath}/labware/${labware.filename}`

                    try {
                        await fs.access(pathLabware)

                        const fileLabware = await fs.readFile(pathLabware, { encoding: 'utf-8' })
                        if (!fileLabware.success) {
                            throw new Error(`Reading file at path ${pathLabware} was unsuccessful`);
                        }
                        const labwareData = getLabwareData(fileLabware.data as string)

                        const equipment: Equipment = {
                            type: 'labware',
                            data: labwareData
                        }
                        updateOpentrons(labware.slot, equipment)
                    } catch (err) {
                        console.error(`Error accessing or reading labware file: ${pathLabware}`, err)
                    }
                } 
            }
        } catch (error: any) {
            console.error(`Error while loading opentrons setup: ${error.message}`);
            return
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
                    backgroundColor: configTabOpen ? '#f5f5f5' : 'transparent',
                    filter: configTabOpen ? 'drop-shadow(0px 2px 5px rgba(0, 0, 0, 0.15))' : 'none',
                    borderRadius: 10,
                }}
            >
                <Button label='Load Configuration' fn={handleOpenConfigTab} active={configTabOpen} />
                {configTabOpen && (
                    <>
                        <Button label='Load Folder' fn={handleLoadFolder} />
                        <Button label='Load Labware' fn={handleLoadLabware} />
                        <Button label='Load Chemicals' fn={handleLoadChemicals} />
                    </>
                )}
            </div>
            <Labwares />
        </div>
    )
}
