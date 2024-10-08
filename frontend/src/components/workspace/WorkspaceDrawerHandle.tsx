import React, { useCallback, useEffect, useRef, useState } from 'react'
import { setLocalStorageItem } from '../../common/localStorageHelpers'

interface WorkspaceDrawerHandleProps {
    handleActive: React.MutableRefObject<boolean>
    tableViewHeight: number
    setTableViewHeight: React.Dispatch<React.SetStateAction<number>>
    setTableView: React.Dispatch<React.SetStateAction<boolean>>
}

export default function WorkspaceDrawerHandle(props: WorkspaceDrawerHandleProps) {
    const { handleActive, tableViewHeight, setTableViewHeight, setTableView } = props

    const [screenSize, setScreenSize] = useState(window.innerHeight)

    const draggingRef = useRef(false)
    const startYRef = useRef(0)
    const initialHeightRef = useRef(0)
    const drawerClosedRef = useRef(false)
    const tableHeightMirror = useRef(0)

    const handleMouseDown = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
        draggingRef.current = true
        handleActive.current = true
        startYRef.current = e.clientY
        initialHeightRef.current = tableViewHeight

        document.addEventListener('mousemove', handleMouseMove)
        document.addEventListener('mouseup', handleMouseUp)
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [tableViewHeight])

    const handleMouseMove = useCallback(
        (e: MouseEvent) => {
            if (draggingRef.current) {
                const newY = e.clientY
                const diffY = startYRef.current - newY
                const newHeight = initialHeightRef.current + diffY
                if (newHeight < 25) {
                    tableHeightMirror.current = 0
                    setTableViewHeight(0)
                    drawerClosedRef.current = true
                } else if (newHeight > 180) {
                    const value =  Math.min(Math.max(250, newHeight), window.innerHeight - 160)
                    tableHeightMirror.current = value
                    setTableViewHeight(value)
                    drawerClosedRef.current = false
                } 

            }
        },
        [setTableViewHeight]
    )

    const handleMouseUp = useCallback(() => {
        draggingRef.current = false
        startYRef.current = 0
        initialHeightRef.current = 0

        if (drawerClosedRef.current === true) {
            setTableView(false)
        }

        console.log(tableHeightMirror.current)
        setLocalStorageItem('uploadTableViewHeight', tableHeightMirror.current)

        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)

        setTimeout(() => {
            handleActive.current = false   
        }, 250)
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [handleMouseMove])

    return (
        <div
            onMouseDown={handleMouseDown}
            style={{
                position: 'absolute',
                width: '100%',
                height: 8,
                top: -3,
                cursor: 'row-resize',
            }}
        />
    )
}
