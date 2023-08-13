import React from 'react';
import { DefaultProps } from '@mantine/core';
export interface SocialButtonProps extends DefaultProps, Omit<React.ComponentPropsWithoutRef<'a'>, 'type'> {
    icon?: React.ReactNode;
}
export declare function SocialButton({ icon, ...others }: SocialButtonProps): JSX.Element;
export declare function DiscordButton({ sx, ...others }: SocialButtonProps): JSX.Element;
export declare function TwitterButton({ sx, ...others }: SocialButtonProps): JSX.Element;
//# sourceMappingURL=SocialButton.d.ts.map