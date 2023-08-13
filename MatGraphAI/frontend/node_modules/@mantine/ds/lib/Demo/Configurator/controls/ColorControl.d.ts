/// <reference types="react" />
interface ColorControlProps {
    value: string;
    label: string;
    onChange(value: string): void;
}
export declare function ColorControl({ value, label, onChange, ...others }: ColorControlProps): JSX.Element;
export declare namespace ColorControl {
    var initialValue: string;
}
export {};
//# sourceMappingURL=ColorControl.d.ts.map