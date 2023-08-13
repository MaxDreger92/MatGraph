import { useMantineTheme } from '@mantine/core';

function useMantineLogoColors(color, variant = "mantine.dev", inverted = false) {
  const theme = useMantineTheme();
  if (variant === "mantine.dev") {
    return {
      background: inverted ? theme.white : theme.fn.themeColor(color || theme.primaryColor, 5),
      color: inverted ? theme.fn.themeColor(color || theme.primaryColor, 5) : theme.white
    };
  }
  return {
    background: theme.colorScheme === "dark" ? theme.colors.yellow[4] : theme.colors.cyan[6],
    color: theme.colorScheme === "dark" ? theme.colors.dark[9] : theme.white
  };
}

export { useMantineLogoColors };
//# sourceMappingURL=use-mantine-logo-colors.js.map
