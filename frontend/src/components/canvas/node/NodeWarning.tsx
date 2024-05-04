import { useSpring, animated } from 'react-spring'

import WarningIcon from '@mui/icons-material/Warning'
import { MutableRefObject, useRef, useState } from 'react'
import { useMantineColorScheme } from '@mantine/core'

interface NodeWarningProps {
    size: number
    hovered: boolean
    color: string
    message: string
}

export default function NodeWarning(props: NodeWarningProps) {
    const { size, hovered, color, message } = props

    const warningLabelRef = useRef<HTMLDivElement>(null)
    const [labelStart, setLabelStart] = useState(0)

    const iconAnimProps = useSpring({
        color: hovered ? '#E15554' : color,
        config: {
            tension: hovered ? 170 : 150,
            friction: hovered ? 26 : 170,
        },
    })

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'

    return (
        <div
            className="node-warning unselectable"
            style={{
                left: size / 2 + 10,
                top: size / 2 + 10,
                pointerEvents: 'none',
            }}
        >
            <div
                ref={warningLabelRef}
                style={{
                    width: 'auto',
                    height: 50,
                    whiteSpace: 'nowrap',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    margin: '2px 10px 2px 10px',
                }}
            >

                <animated.div style={iconAnimProps}>
                    <WarningIcon
                        style={{
                            position: 'relative',
                            fontSize: '30px',
                            transform: `translate(0,${hovered ? -1 : -3}px)`,
                            opacity: 1,
                            zIndex: 5,
                        }}
                    />
                </animated.div>
                {hovered && (
                    <>
                    <div
                        style={{
                            width: '100%',
                            height: '100%',
                            position: 'absolute',
                            backgroundColor: darkTheme ? '#25262b' : '#fff',
                            opacity: 0,
                            transform: 'translateX(100px)',
                            transition: 'opacity 0.1s ease-in-out',
                            animation: 'fade-in-slide-up 0.1s forwards',
                            filter: `drop-shadow(1px 1px 1px ${darkTheme ? '#111' : '#868e96'})`,
                            borderRadius: 3,
                            border: `1px solid ${darkTheme ? '#333' : '#ced4da'}`,
                            left: 0,
                        }}
                    />
                    <span
                    style={{
                        position: 'relative',
                        paddingLeft: 5,
                        color: '#c1c2c5'
                    }}
                >
                    {message}
                </span>
                </>
                )}

            </div>
        </div>
    )
}
