import { createStyles, rem } from '@mantine/core';

const BREAKPOINT = rem(885);
var useStyles = createStyles((theme, { radius, background }) => ({
  configurator: {
    display: "flex",
    maxWidth: "100%",
    border: `${rem(1)} solid ${theme.colorScheme === "dark" ? theme.colors.dark[5] : theme.colors.gray[2]}`,
    overflow: "hidden",
    borderTopLeftRadius: theme.fn.radius(radius),
    borderTopRightRadius: theme.fn.radius(radius),
    borderBottom: 0,
    [`@media (max-width: ${BREAKPOINT})`]: {
      flexDirection: "column"
    }
  },
  noCode: {
    borderRadius: theme.fn.radius(radius),
    borderBottom: `${rem(1)} solid ${theme.colorScheme === "dark" ? theme.colors.dark[5] : theme.colors.gray[2]}`
  },
  preview: {
    flex: 1,
    padding: theme.spacing.md,
    display: "flex",
    flexDirection: "column"
  },
  controls: {
    boxSizing: "border-box",
    width: rem(250),
    padding: theme.spacing.md,
    backgroundColor: background || (theme.colorScheme === "dark" ? theme.colors.dark[7] : theme.white),
    borderLeft: `${rem(1)} solid ${theme.colorScheme === "dark" ? theme.colors.dark[5] : theme.colors.gray[2]}`,
    [`@media (max-width: ${BREAKPOINT})`]: {
      width: "100%",
      borderLeft: 0,
      borderTop: `${rem(1)} solid ${theme.colorScheme === "dark" ? theme.colors.dark[5] : theme.colors.gray[2]}`
    }
  },
  prism: {
    marginTop: 0,
    borderBottomRightRadius: theme.fn.radius(radius),
    borderBottomLeftRadius: theme.fn.radius(radius),
    border: `${rem(1)} solid ${theme.colorScheme === "dark" ? theme.colors.dark[5] : theme.colors.gray[2]}`
  },
  code: {
    borderTopRightRadius: 0,
    borderTopLeftRadius: 0,
    borderBottomRightRadius: theme.fn.radius(radius),
    borderBottomLeftRadius: theme.fn.radius(radius)
  }
}));

export default useStyles;
//# sourceMappingURL=Configurator.styles.js.map
