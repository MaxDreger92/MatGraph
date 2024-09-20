import img_deck from '../img/deck-outline-new.png'
import { deckSlotPositions } from '../data/opentrons.data'
import Slot from './Slot'
import { useContext } from 'react'
import { OpentronsContext } from '../context/OpentronsContext'

interface DeckProps {}

export default function Deck(props: DeckProps) {
    const { opentronsSetupList, chemicalSetupList } = useContext(OpentronsContext)

    return (
        <div
            className='deck'
            style={{
                bottom: opentronsSetupList.length > 0 || chemicalSetupList.length > 0 ? 20 : 'inherit'
            }}
        >
            <img className='img-deck' src={img_deck} alt='OT-2 Deck' />
            {deckSlotPositions.map((slotPosition) => (
                <Slot key={slotPosition.slot} slot={slotPosition.slot} bottom={slotPosition.bottom} left={slotPosition.left} />
            ))}
        </div>
    )
}
