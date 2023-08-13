/// <reference types="react" />
import { MantineColor } from '@mantine/core';
export type MantineLogoVariant = 'mantine.dev' | 'ui.mantine.dev';
export interface LogoProps extends React.ComponentPropsWithoutRef<'svg'> {
    color?: MantineColor;
    variant?: MantineLogoVariant;
    size?: number | string;
    inverted?: boolean;
}
export declare function useMantineLogoColors(color: MantineColor, variant?: MantineLogoVariant, inverted?: boolean): {
    background: string;
    color: string;
};
//# sourceMappingURL=use-mantine-logo-colors.d.ts.map