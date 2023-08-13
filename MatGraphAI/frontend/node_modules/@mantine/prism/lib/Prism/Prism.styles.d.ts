import { MantineNumberSize } from '@mantine/core';
export interface PrismStylesParams {
    colorScheme: 'light' | 'dark';
    native: boolean;
    maxLineSize: number | string;
    radius: MantineNumberSize;
}
declare const _default: (params: PrismStylesParams, options?: import("@mantine/core").UseStylesOptions<string>) => {
    classes: {
        scrollArea: string;
        root: string;
        code: string;
        copy: string;
        line: string;
        lineNumber: string;
        lineContent: string;
    };
    cx: (...args: any) => string;
    theme: import("@mantine/core").MantineTheme;
};
export default _default;
//# sourceMappingURL=Prism.styles.d.ts.map