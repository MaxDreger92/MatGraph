import React, { createContext } from "react";
import { TNode, TRelationship } from "../types/canvas.types";

interface IWorkspaceTableContext {
    setHighlightedColumnIndex: React.Dispatch<React.SetStateAction<number | null>>
    selectedColumnIndex: number | null
    setSelectedColumnIndex: React.Dispatch<React.SetStateAction<number | null>>
    forceEndEditing: () => void
    uploadMode: boolean
    tableViewHeight: number
}

const defaultTableContextValue: IWorkspaceTableContext = {
    setHighlightedColumnIndex: () => {},
    selectedColumnIndex: null,
    setSelectedColumnIndex: () => {},
    forceEndEditing: () => {},
    uploadMode: false,
    tableViewHeight: 0,
}

export const WorkspaceTableContext = createContext<IWorkspaceTableContext>(defaultTableContextValue)