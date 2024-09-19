import React, { useContext, useEffect, useState } from 'react';
import { useDrop } from 'react-dnd';
import { ILabware } from '../types/labware.types';
import { OpentronsContext } from '../context/OpentronsContext';
import { getLabwareNameBySlot, isLabwareInSlot } from '../functions/configuration.functions';
import Labware from './Labware';
import { createOpentronsSetupLabware, findLabwareByName } from '../functions/labware.functions';
import { Configuration } from '../types/configuration.types';

interface SlotProps {
    slot: number;
    bottom: string;
    left: string;
}

export default function Slot(props: SlotProps) {
    const { slot, bottom, left } = props;
    const [renderedComponent, setRenderedComponent] = useState<React.FC<any> | null>(null)
    const [componentProps, setComponentProps] = useState<any>(null);
    const [highlighted, setHighlighted] = useState(false);
    const { currentConfig, setCurrentConfig, labwareList } = useContext(OpentronsContext);

    useEffect(() => {
        if (isLabwareInSlot(currentConfig.opentronsSetup, slot)) {
            const labwareName = getLabwareNameBySlot(currentConfig.opentronsSetup, slot)
            if (!labwareName) return
            const labwareData = findLabwareByName(labwareList, labwareName)
            if (!labwareData) return

            setComponentProps({slot, labware: labwareData})
            setRenderedComponent(() => Labware)
        } else {
            setComponentProps(null)
            setRenderedComponent(null)
        }
    }, [slot, currentConfig, labwareList]);

    const [{ isOver }, drop] = useDrop({
        accept: 'LABWARE',
        drop: (item: ILabware) => {
            const newLabware = createOpentronsSetupLabware(slot, item);
            if (!newLabware) return;

            const currentLabwareSetup = currentConfig.opentronsSetup.labware
            const updatedLabwareSetup = [...currentLabwareSetup.filter((lw) => lw.slot !== slot), newLabware]
    
            setCurrentConfig({
                opentronsSetup: {
                    labware: updatedLabwareSetup
                }
            });
        },
        collect: (monitor) => ({
            isOver: !!monitor.isOver(),
        }),
    });
    
    

    const handleMouseDown = (event: React.MouseEvent) => {
        if (event.button === 1 && renderedComponent) {
            const currentLabwareSetup = currentConfig.opentronsSetup.labware
            const updatedLabwareSetup = currentLabwareSetup.filter((lw) => lw.slot !== slot)

            setCurrentConfig({
                opentronsSetup: {
                    labware: updatedLabwareSetup
                }
            })
        }
    };

    return (
        <div
            key={slot}
            ref={drop}
            className="slot"
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
                border: isOver ? '3px solid #ff9519' : 'none',
            }}
        >
            {highlighted && renderedComponent === null && (
                <div
                    style={{
                        position: 'absolute',
                        width: '80%',
                        height: '80%',
                        borderRadius: '3%',
                        border: '3px solid #ff9519',
                    }}
                ></div>
            )}
            {renderedComponent && React.createElement(renderedComponent, componentProps)}
        </div>
    );
}
