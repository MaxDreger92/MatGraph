import React, { useRef } from "react"
import { CustomRef } from "../../../types/canvas.types"

export function useRefManager() {
    const refs = useRef<CustomRef[]>([])

    const getNewInputRef = () => {
        const newRef = React.createRef<HTMLInputElement>()
        refs.current.push(newRef)
        return newRef
    }

    const getNewSvgRef = (): React.RefObject<SVGSVGElement> => {
        const newRef = React.createRef<SVGSVGElement>()
        refs.current.push(newRef)
        return newRef
    }

    const getNewDivRef = (): React.RefObject<HTMLDivElement> => {
        const newRef = React.createRef<HTMLDivElement>()
        // console.log(refs.current.length)
        refs.current.push(newRef)
        // console.log(refs.current.length)
        return newRef
    }

    const removeRef = (refToRemove: CustomRef) => {
        refs.current = refs.current.filter((ref) => ref !== refToRemove)
    }

    const removeRefs = (refsToRemove: CustomRef[]) => {
        refsToRemove.forEach((ref) => removeRef(ref))
    }

    const resetRefs = () => {
        refs.current = []
    }

    return {
        getNewDivRef,
        getNewInputRef,
        getNewSvgRef,
        removeRef,
        removeRefs,
        resetRefs,
        refs: refs.current,
    }
}