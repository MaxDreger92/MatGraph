import React, { createContext, useState, ReactNode } from 'react'
import { OpentronsSetup } from '../types/opentrons.types'
import { ILabware } from '../types/labware.types'

interface OpentronsContextType {
    opentronsSetupList: OpentronsSetup[]
    setOpentronsSetupList: (setups: OpentronsSetup[], replace: boolean) => void
    currentOpentronsSetup: OpentronsSetup
    patchCurrentOpentronsSetup: (slot: number, labware: ILabware | null) => void
    setCurrentOpentronsSetup: (index: number) => void
    labwareList: ILabware[]
    setLabwareList: (labwareList: ILabware[]) => void
}

export const OpentronsContext = createContext<OpentronsContextType>({
    opentronsSetupList: [],
    setOpentronsSetupList: () => {},
    currentOpentronsSetup: {
        labware: []
    },
    patchCurrentOpentronsSetup: () => {},
    setCurrentOpentronsSetup: () => {},
    labwareList: [],
    setLabwareList: () => {},
})

export const OpentronsContextProvider = ({ children }: { children: ReactNode }) => {
    const [opentronsSetupList, setOpentronsSetupList] = useState<OpentronsSetup[]>([])
    const [currentOpentronsSetup, setCurrentOpentronsSetup] = useState<OpentronsSetup>({labware:[]})
    const [labwareList, setLabwareList] = useState<ILabware[]>([])

    const handleSetOpentronsSetupList = (setups: OpentronsSetup[], replace: boolean) => {
        if (replace) {
            if (setups.length > 0) {
                setOpentronsSetupList(setups)
                setCurrentOpentronsSetup(setups[0])
            }
        } else {
            setOpentronsSetupList((prevSetups) => {
                setups.forEach((setup) => prevSetups.push(setup))

                return prevSetups
            })
        }
    }

    const handleSetCurrentOpentronsSetup = (index: number) => {
        setCurrentOpentronsSetup(opentronsSetupList[index])
    }

    const patchCurrentOpentronsSetup = (slot: number, labware: ILabware | null) => {
        setCurrentOpentronsSetup((prevConfig) => {
            const updatedConfig = {
                ...prevConfig,
                [slot]: labware,
            }

            return updatedConfig
        })
    }

    const handleSetLabwareList = (labwareList: ILabware[]) => {
        setLabwareList(labwareList)
    }

    return (
        <OpentronsContext.Provider
            value={{
                opentronsSetupList: opentronsSetupList,
                setOpentronsSetupList: handleSetOpentronsSetupList,
                currentOpentronsSetup,
                patchCurrentOpentronsSetup,
                setCurrentOpentronsSetup: handleSetCurrentOpentronsSetup,
                labwareList,
                setLabwareList: handleSetLabwareList,
            }}
        >
            {children}
        </OpentronsContext.Provider>
    )
}
