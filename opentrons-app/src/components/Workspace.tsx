import { useState, useRef, useEffect } from 'react'
import Deck from './Deck'
import { OpentronsContextProvider } from '../context/OpentronsContext'
import Menu from './Menu'

interface WorkspaceProps {}

export default function Workspace(props: WorkspaceProps) {
    const [focusMode, setFocusMode] = useState(false)
    const [split, setSplit] = useState(25)
    const isDraggingLeft = useRef(false)
    const isDraggingRight = useRef(false)
    const workspaceRef = useRef<HTMLDivElement>(null)

    const handleSetFocusMode = () => {
        setFocusMode((prevMode) => !prevMode)
    }

    useEffect(() => {
        const handleMouseMove = (event: MouseEvent) => {
            if ((isDraggingLeft.current || isDraggingRight.current) && workspaceRef.current) {
                const rect = workspaceRef.current.getBoundingClientRect()
                let newSplit = ((event.clientX - rect.left) / rect.width) * 100
                if (isDraggingRight.current) {
                    newSplit -= 50
                }
                const clampedSplit = Math.max(10, Math.min(newSplit, 40))
                setSplit(clampedSplit)
            }
        }

        const handleMouseUp = () => {
            isDraggingLeft.current = false
            isDraggingRight.current = false
        }

        document.addEventListener('mousemove', handleMouseMove)
        document.addEventListener('mouseup', handleMouseUp)

        return () => {
            document.removeEventListener('mousemove', handleMouseMove)
            document.removeEventListener('mouseup', handleMouseUp)
        }
    }, [])

    const handleMouseDown = (leftHandle: boolean) => {
        if (leftHandle) {
            isDraggingLeft.current = true
            return
        }
        if (!leftHandle) {
            isDraggingRight.current = true
            return
        }

    }

    const handleRightClick = (event: React.MouseEvent) => {
        event.preventDefault()
        setSplit(25)
    }

    return (
        <div className='workspace' ref={workspaceRef}>
            <OpentronsContextProvider>
                <Menu focusMode={focusMode} split={split} />
                <Deck focusMode={focusMode} setFocusMode={handleSetFocusMode} split={split} />
                {!focusMode && (
                    <>
                        <div
                            onMouseDown={() => handleMouseDown(true)}
                            onContextMenu={handleRightClick}
                            style={{
                                position: 'absolute',
                                left: `${split - 0.5}%`,
                                height: '100%',
                                width: 10,
                                cursor: 'col-resize',
                                zIndex: 1000,
                            }}
                        ></div>
                        <div
                            onMouseDown={() => handleMouseDown(false)}
                            onContextMenu={handleRightClick}
                            style={{
                                position: 'absolute',
                                left: `${split + 50}%`,
                                height: '100%',
                                width: 10,
                                cursor: 'col-resize',
                                zIndex: 1000,
                            }}
                        ></div>
                    </>
                )}
            </OpentronsContextProvider>
        </div>
    )
}
