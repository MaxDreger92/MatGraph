/// <reference types="react" />
interface StringControlProps {
    value: string;
    label: string;
    onChange(value: string): void;
}
export declare function StringControl({ value, label, onChange, ...others }: StringControlProps): JSX.Element;
export declare namespace StringControl {
    var initialValue: string;
}
export {};
//# sourceMappingURL=StringControl.d.ts.map