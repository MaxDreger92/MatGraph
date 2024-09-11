import Deck from './Deck'
import { OpentronsContextProvider } from '../context/OpentronsContext'
import Menu from './Menu'

interface WorkspaceProps {}

export default function Workspace(props: WorkspaceProps) {
    return (
        <div className='workspace'>
            <OpentronsContextProvider>
                <Menu />
                <Deck />
            </OpentronsContextProvider>
        </div>
    )
}
