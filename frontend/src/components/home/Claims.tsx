import { useEffect, useState } from 'react'
import { useTransition, animated } from 'react-spring'

export default function Claims() {
    const [index, setIndex] = useState(0)

    useEffect(() => {
        const startIndex = Math.floor(Math.random() * CLAIMS.length) % CLAIMS.length
        console.log(startIndex)
        setIndex(startIndex)
    }, [])

    useEffect(() => {
        const timer = setTimeout(() => {
            setIndex((state) => (state + 1) % CLAIMS.length)
        }, 7000)
        return () => clearTimeout(timer) // Clear the timeout if the component unmounts
    }, [index])

    const transitions = useTransition(index, {
        keys: index,
        from: { opacity: 0, transform: 'translateX(100%)' },
        enter: { opacity: 1, transform: 'translateX(0%)' },
        leave: { opacity: 0, transform: 'translateX(-100%)' },
        config: { tension: 150, friction: 20 },
    })

    return (
        <>
            {transitions((style, i) => (
                <animated.div style={{ ...style, position: 'absolute', width: '100%' }}>
                    <div
                        className="unselectable"
                        style={{
                            fontFamily: 'poppins-regular',
                            fontSize: 52,
                            transform: 'translate(0, -40px)',
                            textAlign: 'center',
                        }}
                    >
                        {CLAIMS[i]}
                    </div>
                </animated.div>
            ))}
        </>
    )
}

const CLAIMS: string[] = [
    'Reliable ontology-based data mapping and deep embedding',
    'Graph database naturally fits the semantics of materials science research data',
    'Visualize and interact through customizable workflow graphs, that bring your data to life',
    'Ultrafast and highly sophisticated vector-based database search',
]
