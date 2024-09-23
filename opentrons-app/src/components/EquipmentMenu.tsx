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
                height: `calc(96% - 10px)`,
                width: `calc(100% - 20px)`,
                backgroundColor: '#f5f5f5',
                borderRadius: '8px',
                filter: 'drop-shadow(0px 2px 5px rgba(0, 0, 0, 0.15))',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                overflow: 'hidden',
                padding: 5,
            }}
        >
            {/* Header */}
            <span
                className='noselect'
                style={{
                    display: 'block',
                    fontSize: '120%',
                    marginLeft: 5,
                    paddingBottom: 6,
                    pointerEvents: 'none',
                    alignSelf: 'flex-start',
                }}
            >
                Labware
            </span>
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifySelf: 'flex-start',
                    backgroundColor: '#EEE',
                    borderRadius: 5,
                    overflow: 'auto',
                    width: '100%',
                    height: '100%',
                    alignItems: 'center',

                }}
            >
                {Object.entries(labwareList).map(([key, labware], index) => (
                    <div
                        key={key}
                        style={{
                            position: 'relative',
                            left: '2%',
                            width: `${itemSize.width}px`,
                            height: `${itemSize.height}px`,
                            marginTop: index > 0 ? '5%' : '10%',
                            flexShrink: 0,
                        }}
                    >
                        <Labware slot={0} labware={labware} />
                    </div>
                ))}
            </div>
        </div>
    )
}
