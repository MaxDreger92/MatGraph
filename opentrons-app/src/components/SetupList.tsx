import { useEffect, useRef, useState } from 'react'
import { Configuration } from '../types/configuration.types'
import { HiPlusSm } from 'react-icons/hi'
import isEqual from 'lodash/isEqual'
import { RiSaveFill } from 'react-icons/ri'
import { MdRestore } from 'react-icons/md'
import { RiFolderAddFill } from 'react-icons/ri'
import { IoCreateOutline } from "react-icons/io5";
import { VscFolderOpened } from "react-icons/vsc";

interface SetupListProps {
    currentConfig: Configuration
    numSetups: number
    header: string
    type: string
    setupList: any[]
    setActiveSetup: (type: string, index: number) => void
    createSetup: (type: string, name: string) => void
    saveSetup: (type: string, index: number) => void
}

export default function SetupList(props: SetupListProps) {
    const { currentConfig, numSetups, header, type, setupList, setActiveSetup, createSetup, saveSetup } = props

    const [isConfigUnchanged, setIsConfigUnchanged] = useState(1)
    const [isSaveHovered, setIsSaveHovered] = useState(false)
    const [isRestoreHovered, setIsRestoreHovered] = useState(false)
    const [isPlusHovered, setIsPlusHovered] = useState(false)
    const [activeIndex, setActiveIndex] = useState<number | null>()
    const [showInputField, setShowInputField] = useState(false)
    const [newSetupName, setNewSetupName] = useState('')

    const prevConfigRef = useRef(currentConfig)

    const handleSetActiveSetup = (index: number) => {
        if (activeIndex === index) return
        setActiveSetup(type, index)
        setActiveIndex(index)
        setIsConfigUnchanged(2)
    }

    const handleCreateSetup = () => {
        setShowInputField(true)
        setIsPlusHovered(false)
        handleSetActiveSetup(-1)
    }

    const handleSubmit = () => {
        if (newSetupName.trim() !== '') {
            createSetup(type, newSetupName.trim())
            setShowInputField(false)
            setNewSetupName('')
        }
    }

    const handleRestoreSetup = (index: number) => {
        setActiveSetup(type, index)
        setActiveIndex(index)
        setIsConfigUnchanged(2)
        setIsRestoreHovered(false)
    }

    const handleSaveSetup = (index: number) => {
        saveSetup(type, index)
        setIsConfigUnchanged(2)
        setIsSaveHovered(false)
    }

    useEffect(() => {
        const prevConfig = prevConfigRef.current

        switch (type) {
            case 'opentrons':
                if (!currentConfig.opentronsSetup.name) {
                    setActiveIndex(null)
                }
                if (isConfigUnchanged) {
                    if (!isEqual(prevConfig.opentronsSetup, currentConfig.opentronsSetup)) {
                        setIsConfigUnchanged((prev) => prev - 1)
                    }
                }
                break
            case 'chemicals':
                if (!currentConfig.chemicalSetup.name) {
                    setActiveIndex(null)
                }
                if (isConfigUnchanged) {
                    if (!isEqual(prevConfig.chemicalSetup, currentConfig.chemicalSetup)) {
                        setIsConfigUnchanged((prev) => prev - 1)
                    }
                }
                break
            default:
                return
        }

        prevConfigRef.current = currentConfig
    }, [currentConfig, type, isConfigUnchanged])

    const getListItemColor = (index: number): string => {
        if (activeIndex === index) {
            if (isConfigUnchanged) {
                return '#ff9519'
            }
            return '#DDD'
        }
        return 'transparent'
    }

    return (
        <div
            className='noselect'
            style={{
                display: 'flex',
                flexFlow: 'column',
                position: 'relative',
                width: `calc(100%/${numSetups})`,
                height: `calc(100%)`,
                overflow: 'hidden',
            }}
        >
            {/* Header */}
            <span
                style={{
                    display: 'block',
                    fontSize: '120%',
                    marginLeft: 5,
                    paddingBottom: 6,
                    pointerEvents: 'none',
                }}
            >
                {header}
            </span>

            <div
                style={{
                    position: 'absolute',
                    display: 'flex',
                    flexDirection: 'row-reverse',
                    justifyContent: 'center',
                    alignItems: 'center',
                    right: 4,
                }}
            >
                {!showInputField && (
                    <>
                        <HiPlusSm
                            onClick={handleCreateSetup}
                            onMouseEnter={() => setIsPlusHovered(true)}
                            onMouseLeave={() => setIsPlusHovered(false)}
                            style={{ fontSize: 25, color: isPlusHovered ? '#ff9519' : '#DDD', cursor: 'pointer' }}
                        />
                        {/* <VscFolderOpened
                            onClick={handleCreateSetup}
                            onMouseEnter={() => setIsPlusHovered(true)}
                            onMouseLeave={() => setIsPlusHovered(false)}
                            style={{ fontSize: 22, color: isPlusHovered ? '#ff9519' : '#DDD', cursor: 'pointer', position: 'relative', paddingRight: 5 }}
                        /> */}
                    </>
                )}
            </div>

            {/* Setup List */}
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifySelf: 'flex-start',
                    backgroundColor: '#EEE',
                    borderRadius: 5,
                    overflow: 'auto',
                    height: '100%',
                }}
            >
                {showInputField && (
                    <>
                        <input
                            type='text'
                            value={newSetupName}
                            onChange={(e) => setNewSetupName(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                    handleSubmit()
                                } else if (e.key === 'Escape') {
                                    setShowInputField(false)
                                    setNewSetupName('')
                                }
                            }}
                            onBlur={() => {
                                setShowInputField(false)
                                setNewSetupName('')
                            }}
                            style={{
                                position: 'relative',
                                border: 'none',
                                outline: 'none',
                                backgroundColor: 'transparent',
                                top: 5,
                                left: 4,
                                height: 16,
                                width: '50%',
                                paddingBottom: 5,
                                marginBottom: 5,
                                fontSize: '100%',
                                color: '#333',
                            }}
                            autoFocus
                        />
                        <div
                            style={{
                                width: '100%',
                                borderBottom: '1px solid #DDD',
                            }}
                        ></div>
                    </>
                )}
                {setupList.map((setup, index) => {
                    return (
                        <div
                            onClick={() => handleSetActiveSetup(index)}
                            style={{
                                position: 'relative',
                                width: '100%',
                                backgroundColor: getListItemColor(index),
                                paddingBottom: 8,
                                borderBottom: '1px solid #DDD',
                                cursor: 'pointer',
                            }}
                        >
                            <span
                                style={{
                                    position: 'relative',
                                    top: 3,
                                    marginLeft: 5,
                                }}
                            >
                                {setup.name}
                            </span>
                            {activeIndex === index && !isConfigUnchanged && (
                                <div
                                    style={{
                                        position: 'absolute',
                                        display: 'flex',
                                        flexDirection: 'row-reverse',
                                        justifyContent: 'center',
                                        alignItems: 'center',
                                        right: 4,
                                        top: 2,
                                    }}
                                >
                                    <RiSaveFill
                                        onClick={() => handleSaveSetup(index)}
                                        onMouseEnter={() => setIsSaveHovered(true)}
                                        onMouseLeave={() => setIsSaveHovered(false)}
                                        style={{
                                            fontSize: 24,
                                            color: isSaveHovered ? '#ff9519' : '#BBB',
                                            cursor: 'pointer',
                                        }}
                                    />
                                    <MdRestore
                                        onClick={() => handleRestoreSetup(index)}
                                        onMouseEnter={() => setIsRestoreHovered(true)}
                                        onMouseLeave={() => setIsRestoreHovered(false)}
                                        style={{
                                            fontSize: 24,
                                            color: isRestoreHovered ? '#ff9519' : '#BBB',
                                            cursor: 'pointer',
                                            marginRight: 2,
                                        }}
                                    />
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>
        </div>
    )
}
