/// <reference types="react" />
interface NumberControlProps {
    value: number;
    label: string;
    onChange(value: number): void;
}
export declare function NumberControl({ value, label, onChange, ...others }: NumberControlProps): JSX.Element;
export declare namespace NumberControl {
    var initialValue: number;
}
export {};
//# sourceMappingURL=NumberControl.d.ts.map