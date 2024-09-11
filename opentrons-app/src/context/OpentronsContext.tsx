import React, { createContext, useState, ReactNode } from 'react'
import { Equipment } from '../types/opentrons.types'
import { ILabware } from '../types/labware.types'

interface OpentronsContextType {
    opentrons: { [slot: number]: Equipment | null }
    updateOpentrons: (slot: number, equipment: Equipment | null) => void
    labwares: ILabware[]
    updateLabwares: (labwares: ILabware[]) => void
}

export const OpentronsContext = createContext<OpentronsContextType>({
    opentrons: {},
    updateOpentrons: () => {},
    labwares: [],
    updateLabwares: () => {}
})

export const OpentronsContextProvider = ({ children }: { children: ReactNode }) => {
    const [opentrons, setOpentrons] = useState<{ [slot: number]: Equipment | null }>({})
    const [labwares, setLabwares] = useState<ILabware[]>([])

    const updateOpentrons = (
        slot: number, 
        equipment: Equipment | null
    ) => {
        setOpentrons((prevConfig) => {
            const updatedConfig = {
                ...prevConfig,
                [slot]: equipment
            };
    
            // console.log('Opentrons:', JSON.stringify(updatedConfig, null, 2));
    
            return updatedConfig;
        });
    };

    const updateLabwares = (labwares: ILabware[]) => {
        // setLabwares((prevLabwares) => {

        // })
    }

    return (
        <OpentronsContext.Provider
            value={{ opentrons, updateOpentrons, labwares, updateLabwares }}
        >
            {children}
        </OpentronsContext.Provider>
    )
}
