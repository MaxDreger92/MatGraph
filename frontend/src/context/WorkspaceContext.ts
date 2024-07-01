import React, { createContext } from "react";

interface IWorkspaceContext {
    setHighlightedColumnIndex: React.Dispatch<React.SetStateAction<number | null>>
    selectedColumnIndex: number | null
    setSelectedColumnIndex: React.Dispatch<React.SetStateAction<number | null>>
    forceEndEditing: () => void
    uploadMode: boolean
    tableViewHeight: number
}

const defaultContextValue: IWorkspaceContext = {
    setHighlightedColumnIndex: () => {},
    selectedColumnIndex: null,
    setSelectedColumnIndex: () => {},
    forceEndEditing: () => {},
    uploadMode: false,
    tableViewHeight: 0,
}

const WorkspaceContext = createContext<IWorkspaceContext>(defaultContextValue)

export default WorkspaceContext