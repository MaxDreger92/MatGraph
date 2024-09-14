import { useEffect, useState } from 'react'

interface ButtonProps {
    label: string | number
    fn: (...args: any[]) => void
    active?: boolean
    argumentList?: any[] 
}

export default function ButtonRound(props: ButtonProps) {
    const { label, fn, active, argumentList } = props
    const [btnHovered, setBtnHovered] = useState(false)

    useEffect(() => {
        if (active) {
            setBtnHovered(true)
        } else if (active === false) {
            setBtnHovered(false)
        }
    }, [active])

    const handleButton = () => {
        if (argumentList) {
            fn.apply(null, argumentList)
        } else {
            fn()
        }
    }

    const handleMouseEnter = () => {
        setBtnHovered(true)
    }

    const handleMouseLeave = () => {
        if (!active) {
            setBtnHovered(false)
        }
    }

    return (
        <div
            onClick={handleButton}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                width: 50,
                height: 50,
                filter: 'drop-shadow(0px 2px 5px rgba(0, 0, 0, 0.15))',
                backgroundColor: btnHovered ? '#e3e3e3' : '#f5f5f5',
                margin: '5px 5px',
                borderRadius: '50%',
                cursor: 'pointer',
            }}
        >
            {label}
        </div>
    )
}
