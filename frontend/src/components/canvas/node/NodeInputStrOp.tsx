import { Select, useMantineColorScheme } from '@mantine/core'
import React, { useCallback, useContext, useEffect, useRef, useState } from 'react'
import CloseIcon from '@mui/icons-material/Close'
import PlusIcon from '@mui/icons-material/Add'
import MinusIcon from '@mui/icons-material/Remove'
import { WorkspaceTableContext } from '../../../context/WorkspaceContext'
import { splitStrBySemicolon } from '../../../common/helpers'

interface NodeInputStrOpProps {
    handleUpdate: (id: string, value?: string, operator?: string, index?: string) => void
    handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
    id: string
    defaultOp: string
    defaultVal: string
    showIndices: boolean
    index?: string
    showIndexChoice: string
    setShowIndexChoice: React.Dispatch<React.SetStateAction<string>>
    autoFocus: boolean
    zIndex: number
}

export default function NodeInputStrOp(props: NodeInputStrOpProps) {
    const {
        handleUpdate,
        handleKeyUp,
        id,
        defaultOp,
        defaultVal,
        showIndices,
        index,
        showIndexChoice,
        setShowIndexChoice,
        autoFocus,
        zIndex,
    } = props

    const [selectOpen, setSelectOpen] = useState(false)
    const [currentValue, setCurrentValue] = useState<string>('')
    const [valueButtonHovered, setValueButtonHovered] = useState(false)
    const [currentIndex, setCurrentIndex] = useState<string | number>('')
    const [indexButtonHovered, setIndexButtonHovered] = useState(false)
    const [indexChoiceHovered, setIndexChoiceHovered] = useState<number>(0)
    const [awaitingIndex, setAwaitingIndex] = useState(false)
    const { selectedColumnIndex, uploadMode } = useContext(WorkspaceTableContext)
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
        if (defaultVal) {
            setCurrentValue(defaultVal)
        }
    }, [defaultVal])

    // Set Value initial
    useEffect(() => {
        if (!index) return
        setCurrentIndex(index)
    }, [index])

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

    const stopPropagation = useCallback((e: MouseEvent) => {
        e.stopPropagation()
    }, [])

    const handleDropdownOpen = useCallback(() => {
        document.addEventListener('mouseup', stopPropagation, true)
        setSelectOpen(true)
    }, [stopPropagation])

    const handleDropdownClose = useCallback(() => {
        setTimeout(() => {
            document.removeEventListener('mouseup', stopPropagation, true)
            setSelectOpen(false)
        }, 100)
    }, [stopPropagation])

    const handleOpChangeLocal = (e: string | null) => {
        if (e === null) {
            handleUpdate(id, undefined, '')
        } else if (typeof e === 'string') {
            handleUpdate(id, undefined, e)
        }
    }

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
        e.preventDefault() // Necessary to allow the drop
    }

    // choiceHoverColor = '#373A40'

    return (
        <>
            <div
                style={{
                    position: 'relative',
                    display: 'flex',
                    flexDirection: 'row',
                    marginTop: 8,
                    alignItems: 'center',
                    justifyContent: 'center',
                }}
            >
                <Select
                    // className={`${inputClass}`}
                    onChange={handleOpChangeLocal}
                    onKeyUp={handleKeyUp}
                    placeholder="---"
                    defaultValue={defaultOp}
                    data={SELECT_DATA}
                    allowDeselect
                    onDropdownOpen={handleDropdownOpen}
                    onDropdownClose={handleDropdownClose}
                    maxDropdownHeight={Infinity}
                    styles={{
                        input: {
                            height: 40,
                            border: darkTheme ? '1px solid #333' : '1px solid #ced4da',
                            filter: darkTheme
                                ? 'drop-shadow(1px 1px 1px #111)'
                                : 'drop-shadow(1px 1px 1px #ddd)',
                        },
                    }}
                    style={{
                        width: 60,
                        borderRight: 'none',
                        zIndex: selectOpen ? zIndex + 10 : zIndex,
                        // filter: "drop-shadow(1px 1px 1px #111)",
                        // border: "1px solid #333",
                        borderRadius: 5,
                    }}
                />
                <div style={{ position: 'relative', display: 'flex' }}>
                    <input
                        // readOnly={uploadMode && index !== 'inferred'}
                        onDragOver={handleDragOver}
                        onDrop={handleColumnDrop}
                        ref={stringInputRef}
                        className={`${inputClass}`}
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
                            width: 157,
                            marginLeft: 8,
                            zIndex: zIndex,
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
                            onDragOver={handleDragOver}
                            onDrop={handleIndexDrop}
                            ref={indexInputRef}
                            className={`${inputClass}`}
                            type="text"
                            placeholder="Index"
                            value={currentIndex}
                            onChange={(e) => {
                                handleUpdate(id, undefined, undefined, e.target.value)
                                setCurrentIndex(e.target.value)
                            }}
                            onKeyUp={handleKeyUp}
                            style={{
                                marginLeft: 8,
                                zIndex: zIndex,
                                width: 100,
                                paddingRight: 25,
                            }}
                        />
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
                                    backgroundColor:
                                        indexChoiceHovered === 1 ? '#373A40' : 'inherit',
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
        </>
    )
}

const SELECT_DATA: { value: string; label: string }[] = [
    { value: '<', label: '<' },
    { value: '<=', label: '\u2264' },
    { value: '=', label: '=' },
    { value: '!=', label: '\u2260' },
    { value: '>=', label: '\u2265' },
    { value: '>', label: '>' },
]
