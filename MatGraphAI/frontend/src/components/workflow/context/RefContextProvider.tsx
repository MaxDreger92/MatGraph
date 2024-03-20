// src/context/RefContextProvider.tsx
import React, { useContext, useEffect, useState } from 'react'
import RefContext from './RefContext'
import { useRefManager } from '../../../common/helpers'

interface RefContextProviderProps {
    children: React.ReactNode
}

export default function RefContextProvider(props: RefContextProviderProps) {
    const { children } = props

    const manager = useRefManager()

    return <RefContext.Provider value={manager}>{children}</RefContext.Provider>
}
