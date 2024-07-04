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

interface IWorkspaceWorkflowContext {
    setNodes: React.Dispatch<React.SetStateAction<TNode[]>>
    setRelationships: React.Dispatch<React.SetStateAction<TRelationship[]>>
    setNeedLayout: React.Dispatch<React.SetStateAction<boolean>>
}

const defaultWorkflowContextValue: IWorkspaceWorkflowContext = {
    setNodes: () => {},
    setRelationships: () => {},
    setNeedLayout: () => {},
}

export const WorkspaceTableContext = createContext<IWorkspaceTableContext>(defaultTableContextValue)
export const WorkspaceWorkflowContext = createContext<IWorkspaceWorkflowContext>(defaultWorkflowContextValue)