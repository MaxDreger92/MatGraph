import img_deck from '../img/deck-outline-new.png'
import { deckSlotPositions } from '../data/opentrons.data'
import Slot from './Slot'

interface DeckProps {}

export default function Deck(props: DeckProps) {

    return (
        <div className='deck'>
            <img className='img-deck' src={img_deck} alt='OT-2 Deck' />
            {deckSlotPositions.map((slotPosition) => (
                <Slot key={slotPosition.slot} slot={slotPosition.slot} bottom={slotPosition.bottom} left={slotPosition.left} />
            ))}
            {/* <div
                style={{
                    position: 'absolute',
                    bottom: '3.5%',
                    width: '21.3%',
                    height: '6.5%',
                    backgroundColor: 'rgba(0.5,0.5,0.5,0.5)',
                    borderRadius: 30,
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center'
                }}
            >
                Load Configuration
            </div> */}
        </div>
    )
}
