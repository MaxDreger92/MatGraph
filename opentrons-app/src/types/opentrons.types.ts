import { ILabware } from "./labware.types";

type GenEquip = {
    type: string
}

export interface Equipment {
    type: string
    data: ILabware | GenEquip
}