import React, { useRef, useState, useEffect, useContext } from 'react'
import { OpentronsContext } from '../context/OpentronsContext'
import Labware from './Labware'

interface EquipmentMenuProps {}

export default function EquipmentMenu(props: EquipmentMenuProps) {
    const containerRef = useRef(null)
    const [itemSize, setItemSize] = useState({ width: 0, height: 0 })
    const { labwareList } = useContext(OpentronsContext)

    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                const { offsetWidth } = containerRef.current
                setItemSize({ width: offsetWidth * 0.7, height: offsetWidth * 0.45 })
            }
        }

        updateSize()

        const resizeObserver = new ResizeObserver(() => {
            updateSize()
        })

        const currentRef = containerRef.current
        if (currentRef) {
            resizeObserver.observe(currentRef)
        }

        return () => {
            if (currentRef) {
                resizeObserver.unobserve(currentRef)
            }
        }
    }, [])

    return (
        <div
            ref={containerRef}
            className='equipments'
            style={{
                position: 'relative',
                height: '85.1%',
                width: '90%',
                backgroundColor: '#f5f5f5',
                borderRadius: '8px',
                filter: 'drop-shadow(0px 2px 5px rgba(0, 0, 0, 0.15))',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                overflow: 'auto',
            }}
        >
            {Object.entries(labwareList).map(([key, labware], index) => (
                <div
                    key={key}
                    style={{
                        position: 'relative',
                        left: 0,
                        width: `${itemSize.width}px`,
                        height: `${itemSize.height}px`,
                        marginTop: index > 0 ? '5%' : '10%',
                        flexShrink: 0,
                    }}
                >
                    <Labware slot={0} labware={labware}/>
                </div>
            ))}
        </div>
    )
}
