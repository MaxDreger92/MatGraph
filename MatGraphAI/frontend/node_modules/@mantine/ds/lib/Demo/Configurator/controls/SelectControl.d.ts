/// <reference types="react" />
interface SelectControlProps {
    value: string;
    label: string;
    capitalize: boolean;
    onChange(value: string): void;
    data: {
        label: string;
        value: string;
    }[];
}
export declare function SelectControl({ value, label, onChange, data, capitalize: capitalizeItems, ...others }: SelectControlProps): JSX.Element;
export declare namespace SelectControl {
    var initialValue: string;
}
export {};
//# sourceMappingURL=SelectControl.d.ts.map