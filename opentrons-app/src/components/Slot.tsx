import React, { useContext, useEffect, useState } from 'react'
import { useDrop } from 'react-dnd'
import { ILabware } from '../types/labware.types'
import { OpentronsContext } from '../context/OpentronsContext'
import { getLabwareNameBySlot, isLabwareInSlot } from '../functions/configuration.functions'
import Labware from './Labware'
import { createOpentronsSetupLabware, findLabwareByName, getLabwareDataFromList } from '../functions/labware.functions'
import { Configuration } from '../types/configuration.types'

interface SlotProps {
    slot: number
    bottom: string
    left: string
}

export default function Slot(props: SlotProps) {
    const { slot, bottom, left } = props
    const [renderedComponent, setRenderedComponent] = useState<React.FC<any> | null>(null)
    const [componentProps, setComponentProps] = useState<any>(null)
    const [highlighted, setHighlighted] = useState(false)
    const { currentConfig, setCurrentConfig, labwareList, selectedSlot } = useContext(OpentronsContext)

    useEffect(() => {
        if (isLabwareInSlot(currentConfig.opentronsSetup, slot)) {
            const labwareData = getLabwareDataFromList(slot, labwareList, currentConfig.opentronsSetup)
            if (labwareData) {
                setComponentProps({ slot, labware: labwareData })
                setRenderedComponent(() => Labware)
                return
            }
        }
        setComponentProps(null)
        setRenderedComponent(null)
    }, [slot, currentConfig, labwareList])

    const [{ isOver }, drop] = useDrop({
        accept: 'LABWARE',
        drop: (item: ILabware) => {
            const newLabware = createOpentronsSetupLabware(slot, item)
            if (!newLabware) return

            const currentLabwareSetup = currentConfig.opentronsSetup.labware
            const updatedLabwareSetup = [...currentLabwareSetup.filter((lw) => lw.slot !== slot), newLabware]

            setCurrentConfig({
                opentronsSetup: {
                    name: currentConfig.opentronsSetup.name,
                    labware: updatedLabwareSetup,
                },
            })
        },
        collect: (monitor) => ({
            isOver: !!monitor.isOver(),
        }),
    })

    const handleMouseDown = (event: React.MouseEvent) => {
        if ((event.button === 1 || event.button === 2) && renderedComponent) {
            const currentLabwareSetup = currentConfig.opentronsSetup.labware
            const updatedLabwareSetup = currentLabwareSetup.filter((lw) => lw.slot !== slot)

            setCurrentConfig({
                opentronsSetup: {
                    name: currentConfig.opentronsSetup.name,
                    labware: updatedLabwareSetup,
                },
            })
        }
    }

    return (
        <div
            key={slot}
            ref={drop}
            className='slot'
            onMouseOver={() => setHighlighted(true)}
            onMouseOut={() => setHighlighted(false)}
            onMouseDown={handleMouseDown}
            style={{
                position: 'absolute',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                width: '26%',
                height: '18%',
                bottom: bottom,
                left: left,
                // border: isOver ? '3px solid #ff9519' : 'none',
            }}
        >
            {highlighted && renderedComponent === null && (
                <div
                    style={{
                        position: 'absolute',
                        width: '99%',
                        height: '98%',
                        borderRadius: '2% / 3.2%',
                        border: '2px solid #ff9519',
                    }}
                ></div>
            )}
            {/* {selectedSlot === slot && renderedComponent && (
                <div
                    style={{
                        position: 'absolute',
                        height: '95%',
                        width: '95%',
                        filter: 'drop-shadow(1px 5px 3px #00000045)',
                        backgroundColor: '#DDD',
                    }}
                ></div>
            )} */}
            <div
                style={{
                    position: 'absolute',
                    top: '3%',
                    height: '92%',
                    width: '96%',
                }}
            >
                {renderedComponent && React.createElement(renderedComponent, componentProps)}
            </div>
        </div>
    )
}
