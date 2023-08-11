import { useContext, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  createStyles,
  Container,
  UnstyledButton,
  Group,
  Text,
  Menu,
  Tabs,
  rem,
} from "@mantine/core";
import { IconLogout, IconSettings, IconChevronDown } from "@tabler/icons-react";
import logo_sm from "../img/logo_nodes.png";
import { userContext } from "../common/userContext";

const useStyles = createStyles((theme) => ({
  header: {
    paddingTop: theme.spacing.sm,
    paddingBottom: theme.spacing.sm,
    backgroundColor:
      theme.colorScheme === "dark"
        ? theme.colors.dark[6]
        : theme.colors.gray[0],
    borderBottom: `${rem(1)} solid ${
      theme.colorScheme === "dark" ? "#333" : theme.colors.gray[2]
    }`,
    marginBottom: rem(0),
  },

  mainSection: {
  },

  user: {
    color: theme.colorScheme === "dark" ? theme.colors.dark[0] : theme.black,
    padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
    borderRadius: theme.radius.sm,
    transition: "background-color 100ms ease",

    "&:hover": {
      backgroundColor:
        theme.colorScheme === "dark" ? theme.colors.dark[8] : theme.white,
    },

    [theme.fn.smallerThan("xs")]: {
      display: "none",
    },
  },

  userActive: {
    backgroundColor:
      theme.colorScheme === "dark" ? theme.colors.dark[8] : theme.white,
  },

  tabs: {
    [theme.fn.smallerThan("sm")]: {
      display: "none",
    },
  },

  tabsList: {
    borderBottom: "0 !important",
  },

  tab: {
    fontWeight: 500,
    height: rem(38),
    backgroundColor: "transparent",

    "&:hover": {
      backgroundColor:
        theme.colorScheme === "dark"
          ? theme.colors.dark[5]
          : theme.colors.gray[1],
    },

    "&[data-active]": {
      backgroundColor:
        theme.colorScheme === "dark" ? theme.colors.dark[7] : theme.white,
      borderColor:
        theme.colorScheme === "dark"
          ? theme.colors.dark[7]
          : theme.colors.gray[2],
    },
  },
}));

const tabs = ["Search", "History"];

interface HeaderTabsProps {
  onHeaderLinkClick: (key: string) => void
  onLogout: () => void;
  tab: string | null
  setTab: (tab: string) => void
}

export function HeaderTabs(props: HeaderTabsProps) {
  const { onHeaderLinkClick, onLogout, tab, setTab } = props;
  const { classes, cx } = useStyles();
  const [userMenuOpened, setUserMenuOpened] = useState(false);
  const user = useContext(userContext);

  const onLogoutLocal = () => {
    onLogout();
  };

  const items = tabs.map((tab) => (
    <Tabs.Tab
      value={tab}
      key={tab}
      onClick={() => onHeaderLinkClick(tab.toLowerCase())}
    >
      {tab}
    </Tabs.Tab>
  ));

  return (
    <div className={classes.header}>
      <Container size="default" className={classes.mainSection}>
        <Group position="apart">
          {/* Logo */}
          <div className="logo-sm-container">
            <Link to="/" onClick={() => setTab("")}>
              <img
                src={logo_sm}
                alt="mgai"
                className="logo-sm"
              />
            </Link>
          </div>

          {/* Tabs */}
          <Tabs
            value={tab}
            onTabChange={setTab}
            variant="outline"
            style={{
              transform: "translate(0px,0)",
            }}
            classNames={{
              root: classes.tabs,
              tabsList: classes.tabsList,
              tab: classes.tab,
            }}
          >
            <Tabs.List>{items}</Tabs.List>
          </Tabs>

          {/* User (settings) Menu */}
          {user && (
            <div className="user-menu-container">
              <Menu
                width={200}
                position="bottom-end"
                transitionProps={{ transition: "pop-top-right" }}
                onClose={() => setUserMenuOpened(false)}
                onOpen={() => setUserMenuOpened(true)}
                withinPortal
              >
                <Menu.Target>
                  <UnstyledButton
                    className={cx(classes.user, {
                      [classes.userActive]: userMenuOpened,
                    })}
                  >
                    <Group spacing={7}>
                      {user && (user.image ? <div></div> : <div></div>)}
                      <Text
                        weight={500}
                        size="sm"
                        sx={{ lineHeight: 1 }}
                        mr={3}
                      >
                        {user.name ? user.name : "User"}
                      </Text>
                      <IconChevronDown size={rem(12)} stroke={1.5} />
                    </Group>
                  </UnstyledButton>
                </Menu.Target>
                <Menu.Dropdown>
                  <Link to="/account" onClick={() => setTab("")}>
                    <Menu.Item
                      icon={<IconSettings size="0.9rem" stroke={1.5} />}
                    >
                      Account settings
                    </Menu.Item>
                  </Link>
                  <Menu.Divider />
                  <Menu.Item
                    icon={<IconLogout size="0.9rem" stroke={1.5} />}
                    onClick={onLogoutLocal}
                  >
                    Logout
                  </Menu.Item>
                </Menu.Dropdown>
              </Menu>
            </div>
          )}
        </Group>
      </Container>
    </div>
  );
}
