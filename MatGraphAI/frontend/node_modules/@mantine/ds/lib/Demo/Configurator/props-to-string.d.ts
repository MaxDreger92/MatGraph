import { ControlType, ControlProps } from './controls';
interface PropToString {
    type: ControlType;
    name: string;
    value: any;
    defaultValue: any;
}
export declare function propToString({ type, name, value, defaultValue }: PropToString): string;
interface PropsToString {
    props: ControlProps[];
    values: Record<string, any>;
    multiline: boolean | number;
}
export declare function propsToString({ props, values, multiline }: PropsToString): string;
export {};
//# sourceMappingURL=props-to-string.d.ts.map