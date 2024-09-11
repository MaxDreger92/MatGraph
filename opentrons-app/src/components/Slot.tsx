import React, { useContext, useEffect, useState } from 'react';
import { useDrop } from 'react-dnd';
import { ILabware } from '../types/labware.types';
import { OpentronsContext } from '../context/OpentronsContext';
import { equipmentComponents } from '../data/opentrons.data';
import { Equipment } from '../types/opentrons.types';

interface SlotProps {
    slot: number;
    bottom: string;
    left: string;
}

export default function Slot(props: SlotProps) {
    const { slot, bottom, left } = props;
    const [renderedComponent, setRenderedComponent] = useState<React.FC<any> | null>(null)
    const [highlighted, setHighlighted] = useState(false);
    const { opentrons, updateOpentrons } = useContext(OpentronsContext);

    useEffect(() => {
        const componentKey = opentrons[slot]?.type as string;
        if (componentKey) {
            setRenderedComponent(() => equipmentComponents[componentKey]);
        } else {
            setRenderedComponent(null);
        }
    }, [slot, opentrons]);

    const [{ isOver }, drop] = useDrop({
        accept: 'LABWARE',
        drop: (item: ILabware | null) => {
            // if (item) {
            //     updateOpentrons(slot, item);
            // }
        },
        collect: (monitor) => ({
            isOver: !!monitor.isOver(),
        }),
    });

    const handleMouseDown = (event: React.MouseEvent) => {
        if (event.button === 1 && renderedComponent) {
            updateOpentrons(slot, null); // Remove the equipment from the slot
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
            {renderedComponent && React.createElement(renderedComponent, { slot })}
        </div>
    );
}
