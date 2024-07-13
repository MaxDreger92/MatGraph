import { Button, createStyles, rem } from '@mantine/core'
import WorkspacePipelineArrow from './WorkspacePipelineArrow'
import { useEffect, useRef, useState } from 'react'
import { RxCross2 } from 'react-icons/rx'
import { Upload } from '../../types/workspace.types'
import { cancelTask } from '../../common/clientHelpers'

interface WorkspacePipelineProps {
    handlePipelineReset: () => void
    handleRevertProgress: (newProgress: number) => Promise<void>
    handleContextChange: (e: React.ChangeEvent<HTMLInputElement>) => void
    extractLabels: () => Promise<void>
    extractAttributes: () => Promise<void>
    extractNodes: () => Promise<void>
    extractGraph: () => Promise<void>
    importGraph: () => Promise<void>
    progress: number
    upload: Upload | undefined
    uploadProcessing: Set<string>
    darkTheme: boolean
}

export default function WorkspacePipeline(props: WorkspacePipelineProps) {
    const {
        handlePipelineReset,
        handleRevertProgress,
        handleContextChange,
        extractLabels,
        extractAttributes,
        extractNodes,
        extractGraph,
        importGraph,
        progress,
        upload,
        uploadProcessing,
        darkTheme,
    } = props
    const workspacePipelineRef = useRef<HTMLDivElement>(null)
    const [pipelineRect, setPipelineRect] = useState<DOMRect | null>(null)
    const [spaceBetween, setSpaceBetween] = useState(0)
    const [buttonWidth, setButtonWidth] = useState(155)
    const [buttonHovered, setButtonHovered] = useState<number | null>(null)

    useEffect(() => {
        const resizeObserver = new ResizeObserver(() => {
            if (workspacePipelineRef.current) {
                setPipelineRect(workspacePipelineRef.current.getBoundingClientRect())
            }
        })

        const currentCanvas = workspacePipelineRef.current
        if (currentCanvas) {
            resizeObserver.observe(currentCanvas)
        }

        return () => {
            if (currentCanvas) {
                resizeObserver.unobserve(currentCanvas)
            }
        }
    }, [workspacePipelineRef])

    // calculate space between
    useEffect(() => {
        if (!pipelineRect) {
            setSpaceBetween(200)
            setButtonWidth(155)
        } else {
            const availableWidth = pipelineRect.width - 250 - 90 - 40
            if (availableWidth > 935) {
                setButtonWidth(155)
                setSpaceBetween((availableWidth - 775) / 4)
            } else {
                setButtonWidth((availableWidth - 200) / 5)
                setSpaceBetween(50)
            }
        }
    }, [pipelineRect])

    const handleButtonLocal = (step: number, fn: () => any) => {
        const uploadId = upload?._id
        if (uploadId && uploadProcessing.has(uploadId)) {
            cancelTask(uploadId)
            return
        }
        if (step < progress) {
            handleRevertProgress(step)
            return
        }
        fn()
    }

    const getButtonDisabled = (step: number) => {
            return (step !== progress && uploadProcessing.has(upload?._id ?? '')) || step > progress
    }

    const getButtonText = (step: number) => {
        if (buttonWidth < 120) return step.toString()

        if (step === progress && uploadProcessing.has(upload?._id ?? '')) {
            return 'Cancel'
        }
        if (step < progress && step !== buttonHovered) {
            return 'Undo'
        }

        switch (step) {
            case 1:
                return 'Extract Labels'
            case 2:
                return 'Extract Attributes'
            case 3:
                return 'Extract Nodes'
            case 4:
                return 'Extract Graph'
            case 5:
                return 'Save to Database'
            default:
                return
        }
    }

    const getButtonColor = (step: number) => {


        if (step > progress) {
            return ''
        }

        if (uploadProcessing.has(upload?._id ?? '')) {
            if (step === progress) {
                if (buttonHovered === step) {
                    return darkTheme ? '#c94b4b' : '#e64b1c'
                } else {
                    return darkTheme ? '#e15554' : '#f6511d'
                }
            } else {
                return ''
            }
        }

        if (step < progress) {
            if (buttonHovered === step) {
                return darkTheme ? '#f0d971' : '#eba400'
            } else {
                return darkTheme ? '#fff07c' : '#ffb400'
            }
        }
    }

    const hasBlackFont = (step: number) => {
        if (step >= progress) return ''
        if (upload && uploadProcessing.has(upload._id)) return ''
        return '#1a1b1e'
    }

    // const hasBorder = (step: number) => {
    //     if (step >= progress) return false
    //     if (upload && uploadProcessing.has(upload._id)) return false
    //     if (step === buttonHovered) return false
    //     return true
    // }

    const inputClass = darkTheme ? 'input-dark-2' : 'input-light-2'

    return (
        <div
            ref={workspacePipelineRef}
            style={{
                width: '100%',
                height: 80,
                display: 'flex',
                flexDirection: 'row',
            }}
        >
            {/* Cancel */}
            <RxCross2
                onClick={() => handlePipelineReset()}
                onMouseEnter={() => setButtonHovered(0)}
                onMouseLeave={() => setButtonHovered(null)}
                style={{
                    alignSelf: 'center',
                    justifySelf: 'center',
                    width: 30,
                    height: 30,
                    marginLeft: 10,
                    color: buttonHovered === 0 ? 'red' : 'inherit',
                    cursor: 'pointer',
                }}
            />

            {/* Step 1 - Upload CSV -> Request label extraction */}
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'row',
                }}
            >
                {/* Context input field */}
                <div
                    style={{
                        display: 'flex',
                        flexDirection: 'column',
                        width: 250,
                        paddingLeft: 25,
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <input
                        className={`${inputClass}`}
                        type="text"
                        id="contextInput"
                        placeholder={'Enter table context...'}
                        defaultValue={upload?.context ?? ''}
                        onChange={handleContextChange} // write nodeName state
                        autoFocus={true}
                        style={{
                            alignSelf: 'center',
                            justifySelf: 'center',
                        }}
                    />
                </div>
                <Button
                    type="submit"
                    radius="xl"
                    style={{
                        alignSelf: 'center',
                        marginLeft: 15,
                        marginBottom: 1,
                        width: buttonWidth,
                        height: 40,
                        padding: 0,
                        backgroundColor: getButtonColor(1),
                        color: hasBlackFont(1)
                        // border: hasBorder(1) ? '1px dashed #1971c2' : 'none',
                    }}
                    onClick={() => handleButtonLocal(1, extractLabels)}
                    onMouseEnter={() => setButtonHovered(1)}
                    onMouseLeave={() => setButtonHovered(null)}
                    disabled={getButtonDisabled(1)}
                >
                    {getButtonText(1)}
                </Button>
            </div>

            {/* Arrow */}
            <WorkspacePipelineArrow length={spaceBetween} />

            {/* Step 2 - View extracted labels -> Request attribute extraction  */}
            <div
                style={{
                    display: 'flex',
                }}
            >
                <Button
                    type="submit"
                    radius="xl"
                    style={{
                        alignSelf: 'center',
                        marginLeft: 15,
                        marginBottom: 1,
                        width: buttonWidth,
                        height: 40,
                        padding: 0,
                        backgroundColor: getButtonColor(2),
                        color: hasBlackFont(2),
                    }}
                    onClick={() => handleButtonLocal(2, extractAttributes)}
                    onMouseEnter={() => setButtonHovered(2)}
                    onMouseLeave={() => setButtonHovered(null)}
                    disabled={getButtonDisabled(2)}
                >
                    {getButtonText(2)}
                </Button>
            </div>

            {/* Arrow */}
            <WorkspacePipelineArrow length={spaceBetween} />

            {/* Step 3 - View extracted attributes -> Request node extraction */}
            <div
                style={{
                    display: 'flex',
                }}
            >
                <Button
                    type="submit"
                    radius="xl"
                    style={{
                        alignSelf: 'center',
                        marginLeft: 15,
                        marginBottom: 1,
                        width: buttonWidth,
                        height: 40,
                        padding: 0,
                        backgroundColor: getButtonColor(3),
                        color: hasBlackFont(3),
                    }}
                    onClick={() => handleButtonLocal(3, extractNodes)}
                    onMouseEnter={() => setButtonHovered(3)}
                    onMouseLeave={() => setButtonHovered(null)}
                    disabled={getButtonDisabled(3)}
                >
                    {getButtonText(3)}
                </Button>
            </div>

            {/* Arrow */}
            <WorkspacePipelineArrow length={spaceBetween} />

            {/* Step 4 - View extracted nodes (in canvas) -> Request graph extraction */}
            <div
                style={{
                    display: 'flex',
                }}
            >
                <Button
                    type="submit"
                    radius="xl"
                    style={{
                        alignSelf: 'center',
                        marginLeft: 15,
                        marginBottom: 1,
                        width: buttonWidth,
                        height: 40,
                        padding: 0,
                        backgroundColor: getButtonColor(4),
                        color: hasBlackFont(4),
                    }}
                    onClick={() => handleButtonLocal(4, extractGraph)}
                    onMouseEnter={() => setButtonHovered(4)}
                    onMouseLeave={() => setButtonHovered(null)}
                    disabled={getButtonDisabled(4)}
                >
                    {getButtonText(4)}
                </Button>
            </div>

            {/* Arrow */}
            <WorkspacePipelineArrow length={spaceBetween} />

            {/* Step 5 - View extracted graph (in canvas) -> Request import of graph to database */}
            <div
                style={{
                    display: 'flex',
                }}
            >
                <Button
                    type="submit"
                    radius="xl"
                    style={{
                        alignSelf: 'center',
                        marginLeft: 15,
                        marginBottom: 1,
                        width: buttonWidth,
                        height: 40,
                        padding: 0,
                    }}
                    onClick={() => handleButtonLocal(5, importGraph)}
                    onMouseEnter={() => setButtonHovered(5)}
                    onMouseLeave={() => setButtonHovered(null)}
                    disabled={progress < 5}
                >
                    {getButtonText(5)}
                </Button>
            </div>
        </div>
    )
}
