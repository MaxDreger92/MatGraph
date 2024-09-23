import { createContext, useState, ReactNode, useEffect } from 'react'
import { ILabware } from '../types/labware.types'
import { ChemicalSetup, Configuration, DefaultConfiguration, OpentronsSetup } from '../types/configuration.types'
import { asList } from '../functions/functions'
import { isILabware } from '../schemas/labware.schema'
import { isChemicalSetup, isOpentronsSetup, isPartialConfiguration } from '../schemas/configuration.schema'
import { sortSetupListByName } from '../functions/configuration.functions'

interface OpentronsContextType {
    labwareList: ILabware[]
    setLabwareList: (action: ListAction, labware?: ILabware | ILabware[], loadName?: string) => void

    currentConfig: Configuration
    setCurrentConfig: (config: Partial<Configuration>) => void

    opentronsSetupList: OpentronsSetup[]
    setOpentronsSetupList: (action: ListAction, setup?: OpentronsSetup | OpentronsSetup[], index?: number) => void

    chemicalSetupList: ChemicalSetup[]
    setChemicalSetupList: (action: ListAction, setup?: ChemicalSetup | ChemicalSetup[], index?: number) => void

    selectedSlot: number | null
    setSelectedSlot: (slot: number | null) => void
}

export const OpentronsContext = createContext<OpentronsContextType>({
    labwareList: [],
    setLabwareList: () => {},

    currentConfig: DefaultConfiguration,
    setCurrentConfig: () => {},

    opentronsSetupList: [],
    setOpentronsSetupList: () => {},

    chemicalSetupList: [],
    setChemicalSetupList: () => {},

    selectedSlot: null,
    setSelectedSlot: () => {},
})

export const OpentronsContextProvider = ({ children }: { children: ReactNode }) => {
    const [labwareList, setLabwareList] = useState<ILabware[]>([])
    const [currentConfig, setCurrentConfig] = useState<Configuration>(DefaultConfiguration)
    const [opentronsSetupList, setOpentronsSetupList] = useState<OpentronsSetup[]>([])
    const [chemicalSetupList, setChemicalSetupList] = useState<ChemicalSetup[]>([])
    const [selectedSlot, setSelectedSlot] = useState<number | null>(null)

    const handleSetLabwareList = (action: ListAction, labware?: ILabware | ILabware[], loadName?: string) => {
        setLabwareList((prevList) => {
            switch (action) {
                case 'add':
                    if (isILabware(labware)) {
                        const newList = [...prevList]
                        const labwareAsList = asList(labware)
                        for (const listItem of labwareAsList) {
                            const existingLabwareIndex = labwareList.findIndex(
                                (lw) => lw.parameters.loadName === listItem.parameters.loadName
                            )
                            if (existingLabwareIndex === -1) {
                                newList.push(listItem)
                            }
                        }
                        return newList
                    }
                    return prevList
                case 'remove':
                    if (loadName) {
                        return prevList.filter((lw) => lw.parameters.loadName !== loadName)
                    }
                    return prevList
                case 'replace':
                    if (isILabware(labware)) {
                        return asList(labware)
                    }
                    return prevList
                default:
                    return prevList
            }
        })
    }

    const handleSetCurrentConfig = (config: Partial<Configuration>) => {
        if (!isPartialConfiguration(config)) return

        setCurrentConfig((prevConfig) => {
            if (!config.opentronsSetup && !config.chemicalSetup) {
                return DefaultConfiguration
            } else {
                return {
                    ...prevConfig,
                    ...config,
                    opentronsSetup: {
                        ...prevConfig.opentronsSetup,
                        ...config.opentronsSetup,
                    },
                    chemicalSetup: {
                        ...prevConfig.chemicalSetup,
                        ...config.chemicalSetup,
                    },
                }
            }
        })
    }

    const handleSetOpentronsSetupList = (
        action: ListAction,
        setup?: OpentronsSetup | OpentronsSetup[],
        index?: number
    ) => {
        setOpentronsSetupList((prevList) => {
            switch (action) {
                case 'add':
                    if (isOpentronsSetup(setup)) {
                        const setupsAsList = asList(setup)
                        return sortSetupListByName([...prevList, ...setupsAsList]) as OpentronsSetup[]
                    }
                    return prevList
                case 'remove':
                    if (typeof index === 'number' && index >= 0 && index < prevList.length) {
                        return prevList.filter((_, i) => i !== index)
                    }
                    return prevList
                case 'replace':
                    if (isOpentronsSetup(setup)) {
                        return sortSetupListByName(asList(setup)) as OpentronsSetup[]
                    }
                    return prevList
                case 'replaceIndex':
                    if (
                        isOpentronsSetup(setup) &&
                        !Array.isArray(setup) &&
                        typeof index === 'number' &&
                        index >= 0 &&
                        index < prevList.length
                    ) {
                        const newList = [...prevList]
                        newList[index] = setup
                        return newList
                    }
                    return prevList
                default:
                    return prevList
            }
        })
    }

    const handleSetChemicalSetupList = (
        action: ListAction,
        setup?: ChemicalSetup | ChemicalSetup[],
        index?: number
    ) => {
        setChemicalSetupList((prevList) => {
            switch (action) {
                case 'add':
                    if (isChemicalSetup(setup)) {
                        const setupsAsList = asList(setup)
                        return [...prevList, ...setupsAsList]
                    }
                    return prevList
                case 'remove':
                    if (typeof index === 'number' && index >= 0 && index < prevList.length) {
                        return prevList.filter((_, i) => i !== index)
                    }
                    return prevList
                case 'replace':
                    if (isChemicalSetup(setup)) {
                        return asList(setup)
                    }
                    return prevList
                case 'replaceIndex':
                    if (
                        isChemicalSetup(setup) &&
                        !Array.isArray(setup) &&
                        typeof index === 'number' &&
                        index >= 0 &&
                        index < prevList.length
                    ) {
                        const newList = [...prevList]
                        newList[index] = setup
                        return newList
                    }
                    return prevList
                default:
                    return prevList
            }
        })
    }

    const isOpentronsSetupEmpty = (opentronsSetup: OpentronsSetup): boolean => {
        return (
            (!opentronsSetup.labware || opentronsSetup.labware.length === 0) &&
            (!opentronsSetup.pipettes || opentronsSetup.pipettes.length === 0)
        )
    }

    const isChemicalSetupEmpty = (chemicalSetup: ChemicalSetup): boolean => {
        return (
            (!chemicalSetup.opentrons || chemicalSetup.opentrons.length === 0) &&
            (!chemicalSetup.arduino || chemicalSetup.arduino.length === 0)
        )
    }

    useEffect(() => {
        const isEmptyConfig =
            isOpentronsSetupEmpty(currentConfig.opentronsSetup) && isChemicalSetupEmpty(currentConfig.chemicalSetup)

        if (isEmptyConfig) {
            window.electron.ipcRenderer.send('config-empty')
        } else {
            window.electron.ipcRenderer.send('config-not-empty')
        }
    }, [currentConfig])

    const handleSetSelectedSlot = (slot: number | null) => {
        if (slot === 0) return
        setSelectedSlot(slot)
    }

    return (
        <OpentronsContext.Provider
            value={{
                labwareList,
                setLabwareList: handleSetLabwareList,
                currentConfig,
                setCurrentConfig: handleSetCurrentConfig,
                opentronsSetupList,
                setOpentronsSetupList: handleSetOpentronsSetupList,
                chemicalSetupList,
                setChemicalSetupList: handleSetChemicalSetupList,
                selectedSlot: selectedSlot,
                setSelectedSlot: handleSetSelectedSlot
            }}
        >
            {children}
        </OpentronsContext.Provider>
    )
}

const listActions = ['add', 'remove', 'replace', 'replaceIndex']

type ListAction = (typeof listActions)[number]
