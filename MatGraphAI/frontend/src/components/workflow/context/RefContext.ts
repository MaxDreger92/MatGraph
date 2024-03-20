import { RefObject, createContext } from "react"

import { CustomRef } from "../../../types/canvas.types"

// Extending the context value to include functions for adding refs
interface RefContextType {
    refs: CustomRef[]; // This might need adjustment based on your actual useRefManager implementation
    getNewInputRef: () => RefObject<HTMLInputElement>;
    getNewSvgRef: () => RefObject<SVGSVGElement>;
    getNewDivRef: () => RefObject<HTMLDivElement>;
}

// Initialize with default values that mimic the original functionality
// The actual useRefManager hook will provide the real implementations
const defaultContextValue: RefContextType = {
    refs: [],
    getNewInputRef: () => ({ current: null }),
    getNewSvgRef: () => ({ current: null }),
    getNewDivRef: () => ({ current: null }),
};

const RefContext = createContext<RefContextType>(defaultContextValue);

export default RefContext;