import img_deck from '../img/deck-outline-no-button.png'
import { deckSlotPositions } from '../data/opentrons.data'
import Slot from './Slot'
import { useContext, useEffect, useState } from 'react'
import { OpentronsContext } from '../context/OpentronsContext'
import { useSpring, animated } from 'react-spring'
import { RiFocus3Line } from 'react-icons/ri'
import { MdZoomInMap, MdZoomOutMap } from 'react-icons/md'
import chroma from 'chroma-js'

interface DeckProps {
    focusMode: boolean
    setFocusMode: () => void
    split: number
    isAnimated: boolean
}

export default function Deck(props: DeckProps) {
    const { focusMode, setFocusMode, split, isAnimated } = props
    const { opentronsSetupList, chemicalSetupList } = useContext(OpentronsContext)
    const [buttonHovered, setButtonHovered] = useState(false)
    const [buttonClicked, setButtonClicked] = useState(false)

    const deckAnimation = useSpring({
        left: focusMode ? '25%' : `${split}%`,
        bottom: '2%',
        width: focusMode ? '55%' : '50%',
        config: { tension: 170, friction: 26 },
        immediate: !isAnimated
    })

    return (
        <animated.div
            className='deck'
            style={deckAnimation}
        >
            <img className='img-deck' src={img_deck} alt='OT-2 Deck' />
            {/* Header */}
            {/* <span
                className='noselect'
                style={{
                    position: 'absolute',
                    left: 5,
                    top: 10,
                    display: 'block',
                    fontSize: '120%',
                    marginLeft: 5,
                    paddingBottom: 6,
                    pointerEvents: 'none',
                    alignSelf: 'flex-start',
                }}
            >
                Header
            </span> */}

            {/* Slots */}
            {deckSlotPositions.map((slotPosition) => (
                <Slot
                    key={slotPosition.slot}
                    slot={slotPosition.slot}
                    bottom={slotPosition.bottom}
                    left={slotPosition.left}
                />
            ))}

            {/* Shadowed Deck Button */}
            <div
                onMouseEnter={() => setButtonHovered(true)}
                onMouseLeave={() => {
                    setButtonHovered(false)
                    setButtonClicked(false)
                }}
                style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    position: 'absolute',
                    width: '22%',
                    height: '6.5%',
                    top: '90%',
                    backgroundColor: '#cfcfcf',
                    borderRadius: 40,
                    cursor: 'pointer',
                    color: '#555',
                }}
            >
                {/* Shadow */}
                <div
                    style={{
                        top: '7%',
                        position: 'absolute',
                        width: '100%',
                        height: '100%',
                        borderRadius: 40,
                        backgroundColor: chroma('#cfcfcf').darken(0.5).hex(),
                    }}
                ></div>
                {/* Button */}
                <div
                    onMouseDown={() => setButtonClicked(true)}
                    onMouseUp={() => setButtonClicked(false)}
                    onClick={setFocusMode}
                    style={{
                        position: 'absolute',
                        width: '100%',
                        height: '100%',
                        borderRadius: 40,
                        backgroundColor: '#cfcfcf',
                        transform: buttonClicked ? 'translate(0, 2px)' : buttonHovered ? 'translate(0, -2px)' : 'none',
                    }}
                ></div>
            </div>
        </animated.div>
    )
}
