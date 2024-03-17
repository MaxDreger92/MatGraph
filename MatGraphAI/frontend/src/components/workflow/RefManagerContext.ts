import { createContext } from "react"
import { useRefManager } from "../../common/helpers"
import { CustomRef } from "../../types/canvas.types"

const RefContext = createContext<CustomRef[]>([])

export default RefContext