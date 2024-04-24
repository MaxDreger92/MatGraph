import React, { useCallback, useContext, useEffect, useRef, useState } from 'react'
import { useMantineColorScheme } from '@mantine/core'
import CloseIcon from '@mui/icons-material/Close'
import PlusIcon from '@mui/icons-material/Add'
import MinusIcon from '@mui/icons-material/Remove'
import WorkflowContext from '../../workflow/context/WorkflowContext'
import { splitStrBySemicolon } from '../../../common/helpers'

interface NodeInputStrProps {
    handleUpdate: (id: string, value?: string, operator?: string, index?: string) => void
    handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
    id: string
    defaultValue: string | undefined
    showIndices: boolean
    index?: string
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
    const [valueButtonHovered, setValueButtonHovered] = useState(false)
    const [currentIndex, setCurrentIndex] = useState<string | number>('')
    const [indexButtonHovered, setIndexButtonHovered] = useState(false)
    const [indexChoiceHovered, setIndexChoiceHovered] = useState<number>(0)
    const [awaitingIndex, setAwaitingIndex] = useState(false)
    const { selectedColumnIndex, uploadMode } = useContext(WorkflowContext)
    const [indexMissing, setIndexMissing] = useState(false)
    const [numValues, setNumValues] = useState(0)
    const [numIndices, setNumIndices] = useState(0)

    const stringInputRef = useRef<HTMLInputElement>(null)
    const indexInputRef = useRef<HTMLInputElement>(null)

    const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'
    const inputClass = darkTheme ? 'input-dark-1' : 'input-light-1'

    // Set Index initial
    useEffect(() => {
        if (!index) return
        setCurrentIndex(index)
    }, [index])

    // Set Value initial
    useEffect(() => {
        if (defaultValue) {
            setCurrentValue(defaultValue)
        }
    }, [defaultValue])

    // Close IndexChoiceModal when Index changes
    useEffect(() => {
        setShowIndexChoice('')
    }, [currentIndex, setShowIndexChoice])

    // Check if there are more values in an attribute than indices
    useEffect(() => {
        setIndexMissing(numIndices === 0 || numValues > numIndices)
    }, [numValues, numIndices])

    useEffect(() => {
        const splitValue = splitStrBySemicolon(currentValue)

        if (!splitValue) {
            setNumValues(0)
            return
        }
        if (!Array.isArray(splitValue)) {
            setNumValues(1)
            return
        }
        setNumValues(splitValue.length)
    }, [currentValue])

    useEffect(() => {
        const splitIndex = splitStrBySemicolon(currentIndex.toString())

        if (!splitIndex) {
            setNumIndices(0)
            return
        }
        if (!Array.isArray(splitIndex)) {
            setNumIndices(1)
            return
        }
        setNumIndices(splitIndex.length)
    }, [currentIndex])

    const deleteIndexLocal = () => {
        handleUpdate(id, undefined, undefined, '')
        setCurrentIndex('')
        return
    }

    const constructNextIndex = useCallback((newIndex: string | number) => {
        let nextIndex: number | string = ''
        if (currentIndex === '') {
            nextIndex = newIndex
        } else {
            nextIndex = currentIndex + ';' + newIndex
        }
        return nextIndex.toString()
    }, [currentIndex])

    const toggleIndexChoiceModal = () => {
        if (showIndexChoice === id) {
            setAwaitingIndex(false)
            setShowIndexChoice('')
        } else {
            setShowIndexChoice(id)
        }
    }

    const handleIndexChoice = useCallback(
        (choice: string | number) => {
            const nextIndex = constructNextIndex(choice)

            handleUpdate(id, undefined, undefined, nextIndex)
            setCurrentIndex(nextIndex)
            setAwaitingIndex(false)
        },
        [handleUpdate, id, constructNextIndex]
    )

    // Listen to selectedColumnIndex and set Index when awaitingIndex is true
    useEffect(() => {
        if (!awaitingIndex || selectedColumnIndex === null) return

        handleIndexChoice(selectedColumnIndex)
        setAwaitingIndex(false)
    }, [awaitingIndex, selectedColumnIndex, handleIndexChoice])

    const handleIndexDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()

        const dragDataString = e.dataTransfer.getData('text/plain')
        const dragData = JSON.parse(dragDataString)

        const { columnIndex } = dragData

        if (!['string', 'number'].includes(typeof columnIndex)) {
            return
        }

        const nextIndex = constructNextIndex(columnIndex)

        handleUpdate(id, undefined, undefined, nextIndex)
        setCurrentIndex(nextIndex)

        if (indexInputRef.current) {
            indexInputRef.current.focus()
        }
    }

    const deleteValueLocal = () => {
        handleUpdate(id, '', undefined, undefined)
        setCurrentValue('')
        return
    }

    const constructNextValue = useCallback((newValue: string) => {
        let nextValue: string = ''
        if (currentValue === '') {
            nextValue = newValue
        } else {
            nextValue = currentValue + ';' + newValue
        }
        return nextValue
    }, [currentValue])

    const handleColumnDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()

        const dragDataString = e.dataTransfer.getData('text/plain')
        const dragData = JSON.parse(dragDataString)

        const { columnContent, columnIndex } = dragData

        if (
            !(typeof columnContent === 'string') ||
            !['string', 'number'].includes(typeof columnIndex)
        ) {
            return
        }

        const nextIndex = constructNextIndex(columnIndex)
        const nextValue = constructNextValue(columnContent)

        setCurrentValue(nextValue)
        setCurrentIndex(nextIndex)
        handleUpdate(id, nextValue, undefined, nextIndex)

        if (stringInputRef.current) {
            stringInputRef.current.focus()
        }
    }

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault()
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
            <div style={{ position: 'relative', display: 'flex' }}>
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
                        paddingRight: currentValue ? 25 : 0,
                    }}
                />
                {currentValue && <div
                    onMouseEnter={() => setValueButtonHovered(true)}
                    onMouseLeave={() => setValueButtonHovered(false)}
                    onClick={deleteValueLocal}
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
                        color: valueButtonHovered
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
                </div>}
            </div>
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
                    {!indexMissing ? (
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
                            onClick={toggleIndexChoiceModal}
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
                            onClick={toggleIndexChoiceModal}
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
