import { createContext } from "react";

interface IWorkflowContext {
    setHighlightedColumnIndex: React.Dispatch<React.SetStateAction<number | null>>
    selectedColumnIndex: number | null
    setSelectedColumnIndex: React.Dispatch<React.SetStateAction<number | null>>
    forceEndEditing: () => void
}

const defaultContextValue: IWorkflowContext = {
    setHighlightedColumnIndex: () => {},
    selectedColumnIndex: null,
    setSelectedColumnIndex: () => {},
    forceEndEditing: () => {}
}

const WorkflowContext = createContext<IWorkflowContext>(defaultContextValue)

export default WorkflowContext