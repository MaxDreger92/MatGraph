import React, { useContext, useEffect, useRef, useState } from 'react'
import { useMantineColorScheme } from '@mantine/core'
import CloseIcon from '@mui/icons-material/Close'
import PlusIcon from '@mui/icons-material/Add'
import MinusIcon from '@mui/icons-material/Remove'
import WorkflowContext from '../../workflow/context/WorkflowContext'

interface NodeInputStrProps {
    handleUpdate: (id: string, value?: string, operator?: string, index?: string) => void
    handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
    id: string
    defaultValue: string | undefined
    showIndices: boolean
    index?: string | string[]
    showIndexChoice: string
    setShowIndexChoice: React.Dispatch<React.SetStateAction<string>>
    autoFocus: boolean
    add: boolean
    zIndex: number
}

export default function NodeInputStr(props: NodeInputStrProps) {
    const {
        handleUpdate,
        handleKeyUp,
        id,
        defaultValue,
        showIndices,
        index,
        showIndexChoice,
        setShowIndexChoice,
        autoFocus,
        add,
        zIndex,
    } = props

    const [currentValue, setCurrentValue] = useState<string>('')
    const [currentIndex, setCurrentIndex] = useState<string | number>('')
    const [indexButtonHovered, setIndexButtonHovered] = useState(false)
    const [indexChoiceHovered, setIndexChoiceHovered] = useState<number>(0)
    const [awaitingIndex, setAwaitingIndex] = useState(false)
    const { selectedColumnIndex, uploadMode } = useContext(WorkflowContext)

    const stringInputRef = useRef<HTMLInputElement>(null)
    const indexInputRef = useRef<HTMLInputElement>(null)

    const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'
    const inputClass = darkTheme ? 'input-dark-1' : 'input-light-1'

    useEffect(() => {
        if (!index) return
        if (Array.isArray(index)) {
            let indexString = ''
            index.map((index) => indexString.concat(index.toString()))
            setCurrentIndex(indexString)
            return
        }
        setCurrentIndex(index)
    }, [index])

    useEffect(() => {
        if (defaultValue) {
            setCurrentValue(defaultValue)
        }
    }, [defaultValue])

    useEffect(() => {
        if (currentIndex !== '' && showIndexChoice === id) {
            setShowIndexChoice('')
        }
    }, [currentIndex, id, showIndexChoice, setShowIndexChoice])

    useEffect(() => {
        if (!(awaitingIndex && selectedColumnIndex !== null)) return

        handleUpdate(id, undefined, undefined, selectedColumnIndex.toString())
        setCurrentIndex(selectedColumnIndex)
        setAwaitingIndex(false)
    }, [awaitingIndex, selectedColumnIndex, id, handleUpdate])

    const deleteIndexLocal = () => {
        handleUpdate(id, undefined, undefined, '')
        setCurrentIndex('')
        return
    }

    const handleIndexChoiceModal = () => {
        if (showIndexChoice === id) {
            setAwaitingIndex(false)
            setShowIndexChoice('')
        } else {
            setShowIndexChoice(id)
        }
    }

    const handleIndexChoice = (choice: string) => {
        if (choice === 'inferred') {
            handleUpdate(id, undefined, undefined, choice)
            setCurrentIndex(choice)
        }
    }

    const handleIndexDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()

        const dragDataString = e.dataTransfer.getData('text/plain')
        const dragData = JSON.parse(dragDataString)

        const { columnIndex } = dragData

        setCurrentIndex(columnIndex)
        handleUpdate(id, undefined, undefined, columnIndex)

        if (indexInputRef.current) {
            indexInputRef.current.focus()
        }
    }

    const handleColumnDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
        e.stopPropagation()
        const dragDataString = e.dataTransfer.getData('text/plain')
        const dragData = JSON.parse(dragDataString)

        const { columnContent, columnIndex } = dragData

        setCurrentValue(columnContent)
        setCurrentIndex(columnIndex)
        handleUpdate(id, columnContent, undefined, columnIndex)

        if (stringInputRef.current) {
            stringInputRef.current.focus()
        }
    }

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
    }

    return (
        <div

            style={{
                position: 'relative',
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                justifyContent: 'center',
            }}
        >
            <input
                // readOnly={uploadMode && index !== 'inferred'}
                onDragOver={handleDragOver}
                onDrop={handleColumnDrop}
                className={`${inputClass}`}
                ref={stringInputRef}
                type="text"
                placeholder={placeholder}
                value={currentValue}
                onChange={(e) => {
                    setCurrentValue(e.target.value)
                    handleUpdate(id, e.target.value)
                }}
                onKeyUp={handleKeyUp}
                autoFocus={autoFocus}
                style={{
                    marginTop: add ? 8 : 0,
                    zIndex: zIndex,
                    width: 225,
                }}
            />
            {showIndices && (
                <div style={{ position: 'relative', display: 'flex' }}>
                    <input
                        autoFocus={autoFocus && index !== 'inferred'}
                        onDragOver={handleDragOver}
                        onDrop={handleIndexDrop}
                        className={`${inputClass}`}
                        ref={indexInputRef}
                        type="text"
                        placeholder="Index"
                        value={currentIndex}
                        onChange={(e) => {
                            setCurrentIndex(e.target.value)
                            handleUpdate(id, undefined, undefined, e.target.value)
                        }}
                        onKeyUp={handleKeyUp}
                        style={{
                            marginTop: add ? 8 : 0,
                            marginLeft: 8,
                            zIndex: zIndex,
                            width: 100,
                            paddingRight: 25,
                        }}
                    />
                    {/* Index delete, open/close choice modal */}
                    {currentIndex !== '' ? (
                        <div
                            onMouseEnter={() => setIndexButtonHovered(true)}
                            onMouseLeave={() => setIndexButtonHovered(false)}
                            onClick={deleteIndexLocal}
                            style={{
                                position: 'absolute',
                                display: 'flex',
                                alignSelf: 'center',
                                justifyContent: 'center',
                                alignItems: 'center',
                                transform: add ? 'translate(0, 4px)' : 'none',
                                width: 30,
                                height: 30,
                                zIndex: zIndex + 1,
                                right: 0,
                                cursor: 'pointer',
                                color: indexButtonHovered
                                    ? '#ff0000'
                                    : darkTheme
                                    ? '#444'
                                    : '#ced4da',
                            }}
                        >
                            <CloseIcon
                                style={{
                                    color: 'inherit',
                                }}
                            />
                        </div>
                    ) : showIndexChoice !== id ? (
                        <div
                            onMouseEnter={() => setIndexButtonHovered(true)}
                            onMouseLeave={() => setIndexButtonHovered(false)}
                            onClick={handleIndexChoiceModal}
                            style={{
                                position: 'absolute',
                                display: 'flex',
                                alignSelf: 'center',
                                justifyContent: 'center',
                                alignItems: 'center',
                                width: 30,
                                height: 30,
                                transform: add ? 'translate(0, 4px)' : 'none',
                                zIndex: zIndex + 1,
                                right: 0,
                                cursor: 'pointer',
                                color: indexButtonHovered
                                    ? darkTheme
                                        ? '#0ff48b'
                                        : '#97e800'
                                    : darkTheme
                                    ? '#444'
                                    : '#ced4da',
                            }}
                        >
                            <PlusIcon
                                style={{
                                    color: 'inherit',
                                }}
                            />
                        </div>
                    ) : (
                        <div
                            onMouseEnter={() => setIndexButtonHovered(true)}
                            onMouseLeave={() => setIndexButtonHovered(false)}
                            onClick={handleIndexChoiceModal}
                            style={{
                                position: 'absolute',
                                display: 'flex',
                                alignSelf: 'center',
                                justifyContent: 'center',
                                alignItems: 'center',
                                width: 30,
                                height: 30,
                                transform: add ? 'translate(0, 4px)' : 'none',
                                zIndex: zIndex + 1,
                                right: 0,
                                cursor: 'pointer',
                                color: indexButtonHovered
                                    ? darkTheme
                                        ? '#fff07c'
                                        : '#ffb400'
                                    : darkTheme
                                    ? '#444'
                                    : '#ced4da',
                            }}
                        >
                            <MinusIcon
                                style={{
                                    color: 'inherit',
                                }}
                            />
                        </div>
                    )}
                </div>
            )}
            {/* Choose new index 'inferred' or from table */}
            {showIndexChoice === id && (
                <div style={{ position: 'relative' }}>
                    <div
                        className={`${inputClass}`}
                        style={{
                            position: 'absolute',
                            display: 'flex',
                            flexDirection: 'column',
                            width: 100,
                            marginLeft: 8,
                            transform: 'translate(0, -50%)',
                        }}
                    >
                        <div
                            onMouseEnter={() => setIndexChoiceHovered(1)}
                            onMouseLeave={() => setIndexChoiceHovered(0)}
                            onClick={() => handleIndexChoice('inferred')}
                            style={{
                                width: 'calc(100% - 8px)',
                                height: 30,
                                margin: '4px 4px 0 4px',
                                borderRadius: 3,
                                backgroundColor: indexChoiceHovered === 1 ? '#373A40' : 'inherit',
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                            }}
                        >
                            <div style={{ position: 'relative', top: 2 }}>"inferred"</div>
                        </div>
                        <div
                            onMouseEnter={() => setIndexChoiceHovered(2)}
                            onMouseLeave={() => setIndexChoiceHovered(0)}
                            onClick={() => setAwaitingIndex(!awaitingIndex)}
                            style={{
                                width: 'calc(100% - 8px)',
                                height: 30,
                                margin: '0 4px 4px 4px',
                                borderRadius: 3,
                                backgroundColor: awaitingIndex
                                    ? '#1864ab'
                                    : indexChoiceHovered === 2
                                    ? '#373A40'
                                    : 'inherit',
                                display: 'flex',
                                justifyContent: 'center',
                                alignItems: 'center',
                            }}
                        >
                            <div style={{ position: 'relative', top: 2 }}>select</div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
