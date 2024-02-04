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
import { IconLogout, IconSettings, IconChevronDown, IconUser } from "@tabler/icons-react";
import logo_sm from "../img/logo_nodes.png";
import { userContext } from "../common/userContext";
import { useLocation } from "react-router-dom";

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
        theme.colorScheme === "dark" ? theme.colors.dark[5] : theme.white,
    },

    [theme.fn.smallerThan("xs")]: {
      display: "none",
    },
  },

  userActive: {
    backgroundColor:
      theme.colorScheme === "dark" ? theme.colors.dark[7] : theme.white,

    "&:hover": {
      backgroundColor:
        theme.colorScheme === "dark" ? theme.colors.dark[7] : theme.white
    }
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

const tabs = ["Workflow", "Database"];

interface HeaderProps {
  handleHeaderLinkClick: (key: string) => void
  handleLogout: () => void;
}

export default function Header(props: HeaderProps) {
  const { handleHeaderLinkClick, handleLogout } = props;
  const { classes, cx } = useStyles();
  const [userMenuOpened, setUserMenuOpened] = useState(false);
  const user = useContext(userContext);
  const [activeTab, setActiveTab] = useState<string | null>(null)
  const location = useLocation()

  useEffect(() => {
    const slicedPath = location.pathname.slice(1)
    setActiveTab(slicedPath.charAt(0).toUpperCase() + slicedPath.slice(1))
  }, [location, setActiveTab])

  const handleLogoutLocal = () => {
    handleLogout();
  };

  const items = tabs.map((tab) => (
    <Tabs.Tab
      value={tab}
      key={tab}
      onClick={() => handleHeaderLinkClick(tab.toLowerCase())}
      style={{height:40}}
    >
      {tab}
    </Tabs.Tab>
  ));

  return (
    <div className={classes.header}
      style={{
        backgroundColor: "#25262b",
      }}
    >
      <Container size="default" className={classes.mainSection}>
        <Group position="apart">
          {/* Logo */}
          <div className="logo-sm-container">
            <Link to="/" onClick={() => setActiveTab("")}>
              <img
                src={logo_sm}
                alt="mgai"
                className="logo-sm"
              />
            </Link>
          </div>

          {/* Tabs */}
          <Tabs
            value={activeTab}
            // onTabChange={setActiveTab}
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
                    style={{height:40}}
                  >
                    <Group spacing={7}>
                      {user && (user.imgurl ? <div></div> : <div></div>)}
                      <Text
                        weight={500}
                        size="sm"
                        sx={{ lineHeight: 1 }}
                        mr={3}
                      >
                        {user.username ? user.username : "User"}
                      </Text>
                      <IconChevronDown size={rem(12)} stroke={1.5} />
                    </Group>
                  </UnstyledButton>
                </Menu.Target>
                <Menu.Dropdown>
                  <Link to="/profile" onClick={() => setActiveTab("")}>
                    <Menu.Item
                      icon={<IconUser size="0.9rem" stroke={1.5} />}
                    >
                      User Profile
                    </Menu.Item>
                  </Link>
                  <Menu.Divider />
                  <Menu.Item
                    icon={<IconLogout size="0.9rem" stroke={1.5} />}
                    onClick={handleLogoutLocal}
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
