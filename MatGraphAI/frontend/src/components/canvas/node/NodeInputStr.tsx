import React, { RefObject, useContext, useEffect, useState } from 'react'
import { AttributeIndex } from '../../../types/canvas.types'
import { useMantineColorScheme } from '@mantine/core'
import CloseIcon from '@mui/icons-material/Close'
import RefContext from '../../workflow/context/RefContext'

interface NodeInputStrProps {
    handleStrChange: (id: string, value: string) => void
    handleIndexChange: (id: string, value: string) => void
    handleKeyUp: (e: React.KeyboardEvent<HTMLInputElement>) => void
    handleBlur: () => void
    id: string
    defaultValue: string | undefined
    showIndices: boolean
    index?: AttributeIndex | AttributeIndex[]
    autoFocus: boolean
    add: boolean
    zIndex: number
}

export default function NodeInputStr(props: NodeInputStrProps) {
    const {
        handleStrChange,
        handleIndexChange,
        handleKeyUp,
        handleBlur,
        id,
        defaultValue,
        showIndices,
        index,
        autoFocus,
        add,
        zIndex,
    } = props

    const [indexDeleteHovered, setIndexDeleteHovered] = useState(false)

    const { getNewInputRef } = useContext(RefContext)

    const placeholder = id.charAt(0).toUpperCase() + id.slice(1)

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'
    const inputClass = darkTheme ? 'input-dark-1' : 'input-light-1'

    const deleteIndexLocal = () => {
        if (index === "") return
        if (index === "inferred") {
            handleIndexChange(id, "")
            return
        }
        handleIndexChange(id, "inferred")
        return
    }

    return (
        <div
            style={{
                display: 'flex',
                flexDirection: 'row',
            }}
        >
            <input
                className={`${inputClass}`}
                ref={getNewInputRef()}
                type="text"
                placeholder={placeholder}
                defaultValue={defaultValue}
                onChange={(e) => handleStrChange(id, e.target.value)} // write nodeName state
                onKeyUp={handleKeyUp} // confirm name with enter
                onBlur={handleBlur}
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
                        className={`${inputClass}`}
                        ref={getNewInputRef()}
                        type="text"
                        placeholder="Idx"
                        defaultValue={index !== undefined ? index.toString() : ''}
                        onChange={(e) => handleIndexChange(id, e.target.value)}
                        onKeyUp={handleKeyUp}
                        onBlur={handleBlur}
                        style={{
                            marginTop: add ? 8 : 0,
                            marginLeft: 8,
                            zIndex: zIndex,
                            width: 110,
                        }}
                    />
                    <div
                        onMouseEnter={() => setIndexDeleteHovered(true)}
                        onMouseLeave={() => setIndexDeleteHovered(false)}
                        onClick={deleteIndexLocal}
                        style={{
                            position: "relative",
                            display: "flex",
                            alignSelf: "center",
                            justifyContent: "center",
                            alignItems: "center",
                            transform: add ? 'translate(0, 4px)' : 'none',
                            width: 30,
                            height: 30,
                            zIndex: zIndex + 1,
                            left: -28,
                            cursor: 'pointer',
                            color: indexDeleteHovered ? "#ff0000" : darkTheme ? '#444' : '#ced4da',
                        }}
                    >
                        <CloseIcon
                            style={{

                                color: "inherit",
                            }}
                        />
                    </div>
                    
                </div>
            )}
        </div>
    )
}
