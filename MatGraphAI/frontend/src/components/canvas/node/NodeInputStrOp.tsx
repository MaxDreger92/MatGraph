import { Select, useMantineColorScheme } from '@mantine/core'
import React, { useContext, useEffect, useState } from 'react'
import { AttributeIndex, Operator } from '../../../types/canvas.types'
import RefContext from '../../workflow/context/RefContext'
import CloseIcon from '@mui/icons-material/Close'
import PlusIcon from '@mui/icons-material/Add'
import MinusIcon from '@mui/icons-material/Remove'
import WorkflowContext from '../../workflow/context/WorkflowContext'

interface NodeInputStrOpProps {
    handleUpdate: (id: string, value?: string, operator?: string, index?: string) => void
    handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
    handleBlur: (e: React.FocusEvent<HTMLDivElement, Element>) => void
    id: string
    defaultOp: string
    defaultVal: string
    showIndices: boolean
    index?: AttributeIndex | AttributeIndex[]
    showIndexChoice: string
    setShowIndexChoice: React.Dispatch<React.SetStateAction<string>>
    autoFocus: boolean
    zIndex: number
}

export default function NodeInputStrOp(props: NodeInputStrOpProps) {
    const {
        handleUpdate,
        handleKeyUp,
        handleBlur,
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
    const [currentValue, setCurrentValue] = useState<string | undefined>(defaultVal)
    const [currentIndex, setCurrentIndex] = useState<string | number>('')
    const [indexButtonHovered, setIndexButtonHovered] = useState(false)
    const [indexChoiceHovered, setIndexChoiceHovered] = useState<number>(0)
    const [awaitingIndex, setAwaitingIndex] = useState(false)
    const { selectedColumnIndex, uploadMode } = useContext(WorkflowContext)

    const { getNewInputRef } = useContext(RefContext)
    const selectInputRef = getNewInputRef()
    const stringInputRef = getNewInputRef()
    const indexInputRef = getNewInputRef()

    const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'
    const inputClass = darkTheme ? 'input-dark-1' : 'input-light-1'

    useEffect(() => {
        if (defaultVal) {
            setCurrentValue(defaultVal)
        }
    }, [defaultVal])

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
        if (currentIndex !== '' && showIndexChoice === id) {
            setShowIndexChoice('')
        }
    }, [currentIndex, id, showIndexChoice, setShowIndexChoice])

    useEffect(() => {
        if (!(awaitingIndex && selectedColumnIndex !== null)) return

        handleUpdate(id, undefined, undefined, selectedColumnIndex.toString())
        setCurrentIndex(selectedColumnIndex)
        setAwaitingIndex(false)
    }, [awaitingIndex, selectedColumnIndex, handleUpdate, id])

    const toggleSelectOpen = () => {
        if (selectOpen) {
            setTimeout(() => {
                setSelectOpen(false)
            }, 100)
        } else {
            setSelectOpen(true)
        }
    }

    const handleOpChangeLocal = (e: string | null) => {
        if (e === null) {
            handleUpdate(id, undefined, '')
        } else if (typeof e === 'string') {
            handleUpdate(id, undefined, e)
        }
    }

    const deleteIndexLocal = () => {
        handleUpdate(id, '', undefined, '')
        setCurrentIndex('')
        setCurrentValue('')
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
        const dragDataString = e.dataTransfer.getData('text/plain');
        const dragData = JSON.parse(dragDataString)

        const {columnIndex} = dragData 
    
        setCurrentIndex(columnIndex);
        handleUpdate(id, undefined, undefined, columnIndex)

        if (indexInputRef.current) {
            indexInputRef.current.focus()
        }

        e.preventDefault();
    };

    const handleColumnDrop = (e: React.DragEvent<HTMLDivElement>) => {
        const dragDataString = e.dataTransfer.getData('text/plain');
        const dragData = JSON.parse(dragDataString);

        const { columnContent, columnIndex } = dragData;

        setCurrentValue(columnContent)
        setCurrentIndex(columnIndex)
        handleUpdate(id, columnContent, undefined, columnIndex)

        if (stringInputRef.current) {
            stringInputRef.current.focus()
        }

        e.preventDefault();
    }

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault(); // Necessary to allow the drop
    };

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
                    ref={selectInputRef}
                    onChange={handleOpChangeLocal}
                    onKeyUp={handleKeyUp}
                    onBlur={handleBlur}
                    placeholder="---"
                    defaultValue={defaultOp}
                    data={SELECT_DATA}
                    allowDeselect
                    onDropdownOpen={toggleSelectOpen}
                    onDropdownClose={toggleSelectOpen}
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
                <input
                    disabled={uploadMode && index !== 'inferred'}
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
                    onBlur={handleBlur}
                    autoFocus={autoFocus}
                    style={{
                        width: 157,
                        marginLeft: 8,
                        zIndex: zIndex,
                    }}
                />
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
                            onBlur={handleBlur}
                            style={{
                                marginLeft: 8,
                                zIndex: zIndex,
                                width: 100,
                            }}
                        />
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
                                    backgroundColor:
                                        awaitingIndex ? '#1864ab' : indexChoiceHovered === 2 ? '#373A40' : 'inherit',
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
