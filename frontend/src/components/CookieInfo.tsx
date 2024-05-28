import { Button } from '@mantine/core'
import { useEffect, useState } from 'react'
import { useSpring, animated } from 'react-spring'

interface CookieInfoProps {
    setCookieConsent: () => void
    darkTheme: boolean
}

export default function CookieInfo(props: CookieInfoProps) {
    const { setCookieConsent, darkTheme } = props
    const [bottomVal, setBottomVal] = useState(-175)
    const [confirmed, setConfirmed] = useState(false)

    useEffect(() => {
        if (confirmed) {
            setBottomVal(-175)
        } else {
            setBottomVal(0)
        }
    }, [confirmed])

    const springProps = useSpring({
        bottom: bottomVal,
        // config: {
        //     tension: 200,
        //     friction: 26,
        // },
    })

    return (
        <animated.div
            style={{
                display: 'flex',
                flexDirection: 'row',
                position: 'absolute',
                bottom: springProps.bottom,
                width: '100%',
                height: 175,
                filter: `drop-shadow(0px 0px 3px ${darkTheme ? '#111' : '#aaa'})`,
                backgroundColor: darkTheme ? '#1a1b1e' : '#f8f9fa',
                zIndex: 30,
                justifyContent: 'center',
                alignItems: 'center',
            }}
        >
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    paddingRight: 120,
                }}
            >
                <p style={{ paddingTop: 10, marginBottom: 0 }}>
                    <h5>Cookies</h5>
                </p>
                <p>
                    Our website uses cookies for the purpose of user authentication and to
                    ensure a secure experience.
                </p>
            </div>
            <Button
                type="submit"
                radius="xl"
                style={{
                    width: 120,
                    height: 40,
                }}
                onClick={() => {
                    setConfirmed(true)
                    setCookieConsent()
                }}
            >
                Confirm
            </Button>
        </animated.div>
    )
}
