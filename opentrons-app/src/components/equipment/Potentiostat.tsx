import React, { useState } from 'react'
import { useDrag } from 'react-dnd'
import { ILabware } from '../../types/labware.types'

type Slot = {
    name: string
}

type PotentiostatSlots = {
    A: { 1: Slot | null; 2: Slot | null; 3: Slot | null }
    B: { 1: Slot | null; 2: Slot | null; 3: Slot | null; 4: Slot | null; 5: Slot | null }
    C: { 1: Slot | null; 2: Slot | null; 3: Slot | null; 4: Slot | null }
    D: { 1: Slot | null; 2: Slot | null; 3: Slot | null; 4: Slot | null; 5: Slot | null }
    E: { 1: Slot | null; 2: Slot | null; 3: Slot | null }
}

const initialPotentiostat: PotentiostatSlots = {
    A: { 1: null, 2: null, 3: null },
    B: { 1: null, 2: null, 3: null, 4: null, 5: null },
    C: { 1: null, 2: null, 3: null, 4: null },
    D: { 1: null, 2: null, 3: null, 4: null, 5: null },
    E: { 1: null, 2: null, 3: null },
}

interface PotentiostatProps {}

function Potentiostat(props: PotentiostatProps) {
    const [slots, setSlots] = useState(initialPotentiostat)

    const [{ isDragging }, drag] = useDrag({
        type: 'POTENTIOSTAT',
        collect: (monitor) => ({
            isDragging: !!monitor.isDragging(),
        }),
    })

    const addEmptySlot = (pre: boolean, row: number, col: number): boolean => {
        if (pre) {
            if ((row === 0 || row === 4) && col === 0) {
                return true
            }
        } else {
            if ((row === 2 && col === 3) || ((row === 0 || row === 4) && col === 2)) {
                return true
            }
        }
        return false
    }

    return (
        <div
            ref={drag}
            className='equipment'
            style={{
                backgroundColor: '#bebebe',
            }}
        >
            <div
                style={{
                    display: 'grid',
                    gridTemplateRows: 'repeat(5, 1fr)',
                    gridTemplateColumns: 'repeat(5, 1fr)',
                    gap: '2px',
                    width: '60%',
                    padding: '2% 10%',
                }}
            >
                {Object.entries(slots).map(([row, rowSlots], rowIndex) =>
                    Object.entries(rowSlots).map(([col, slot], colIndex) => {
                        return (
                            <>
                                {addEmptySlot(true, rowIndex, colIndex) && (
                                    <div key={`empty${row}-${col}`} className='empty-slot'></div>
                                )}
                                <div
                                    key={`${row}-${col}`}
                                    style={{
                                        width: '100%',
                                        paddingTop: '100%',
                                        display: 'flex',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                        borderRadius: '50%',
                                        position: 'relative',
                                        margin: 'auto',
                                    }}
                                >
                                    <div
                                        style={{
                                            position: 'absolute',
                                            top: 0,
                                            left: 0,
                                            width: '100%',
                                            height: '100%',
                                            display: 'flex',
                                            justifyContent: 'center',
                                            alignItems: 'center',
                                            borderRadius: '50%',
                                            backgroundColor: slot ? '#ffeb3b' : '#cdcdcd',
                                        }}
                                    >
                                        {slot ? slot.name : `${row}${col}`}
                                    </div>
                                </div>
                                {addEmptySlot(false, rowIndex, colIndex) && (
                                    <div key={`empty${row}-${col}`} className='empty-slot'></div>
                                )}
                            </>
                        )
                    })
                )}
            </div>
        </div>
    )
}
