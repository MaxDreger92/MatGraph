/// <reference types="react" />
interface SizeControlProps {
    value: string;
    label: string;
    step?: number;
    onChange(value: string): void;
}
export declare function SizeControl({ label, value, onChange, step, ...others }: SizeControlProps): JSX.Element;
export declare namespace SizeControl {
    var initialValue: string;
}
export {};
//# sourceMappingURL=SizeControl.d.ts.map