import { useContext, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSpring, animated } from 'react-spring'
import {
    createStyles,
    Container,
    UnstyledButton,
    Group,
    Text,
    Menu,
    Tabs,
    rem,
    useMantineColorScheme,
} from '@mantine/core'
import { IconLogout, IconSettings, IconChevronDown, IconUser } from '@tabler/icons-react'
import logo_sm from '../img/logo_nodes.png'
import logo_sm_light from '../img/logo_nodes_light.png'
import { UserContext } from '../context/UserContext'
import { useLocation } from 'react-router-dom'
import { MdOutlineLightMode, MdLightMode, MdOutlineDarkMode, MdDarkMode } from 'react-icons/md'
import client from '../client'
import toast from 'react-hot-toast'

const useStyles = createStyles((theme) => ({
    header: {
        paddingTop: theme.spacing.sm,
        paddingBottom: theme.spacing.sm,
        marginBottom: rem(0),
    },

    headerBackground: {
        position: 'absolute',
        width: '100%',
        height: 65,
        backgroundColor: theme.colorScheme === 'dark' ? '#25262b' : '#fff',
        borderBottom: `${rem(1)} solid ${
            theme.colorScheme === 'dark' ? '#333' : theme.colors.gray[4]
        }`,
    },

    mainSection: {},

    user: {
        color: theme.colorScheme === 'dark' ? theme.colors.dark[0] : theme.black,
        padding: `${theme.spacing.xs} ${theme.spacing.sm}`,
        borderRadius: theme.radius.sm,
        transition: 'background-color 100ms ease',

        '&:hover': {
            backgroundColor:
                theme.colorScheme === 'dark' ? theme.colors.dark[5] : theme.colors.gray[1],
        },

        [theme.fn.smallerThan('xs')]: {
            display: 'none',
        },
    },

    userActive: {
        backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.colors.gray[1],

        '&:hover': {
            backgroundColor:
                theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.colors.gray[1],
        },
    },

    tabs: {
        [theme.fn.smallerThan('sm')]: {
            display: 'none',
        },
    },

    tabsList: {
        borderBottom: '0 !important',
    },

    tab: {
        fontWeight: 500,
        height: rem(38),
        backgroundColor: 'transparent',

        '&:hover': {
            backgroundColor:
                theme.colorScheme === 'dark' ? theme.colors.dark[5] : theme.colors.gray[1],
        },

        '&[data-active]': {
            backgroundColor:
                theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.colors.gray[1],
            borderColor: theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.colors.gray[1],
        },
    },
}))

const tabs = ['Upload', 'Search']

interface HeaderProps {
    handleHeaderLinkClick: (key: string) => void
    handleLogout: () => void
}

export default function Header(props: HeaderProps) {
    const { handleHeaderLinkClick, handleLogout } = props
    const { classes, cx } = useStyles()
    const [userMenuOpened, setUserMenuOpened] = useState(false)
    const user = useContext(UserContext)
    const [activeTab, setActiveTab] = useState<string | null>(null)
    const location = useLocation()

    useEffect(() => {
        // pathname = '/path'
        const slicedPath = location.pathname.slice(1)
        if (['upload', 'search'].includes(slicedPath)) {
            setActiveTab(slicedPath.charAt(0).toUpperCase() + slicedPath.slice(1))
        } else {
            setActiveTab('')
        }
    }, [location, setActiveTab])

    const handleLogoutLocal = () => {
        handleLogout()
    }

    async function getApiActiveStatus() {
        try {
            const response = await client.apiActiveStatus()

            if (response.data.message) {
                toast.success(response.data.message)
            } else {
                throw new Error('Unexpected server response while testing API active status!')
            }
        } catch (err: any) {
            toast.error(err.message)
        }
    }

    const items = tabs.map((tab, i) => (
        <Tabs.Tab
            value={tab}
            key={tab}
            onClick={() => handleHeaderLinkClick(tab.toLowerCase())}
            style={{
                height: 40,
                borderRadius: 3,
            }}
        >
            {tab}
        </Tabs.Tab>
    ))

    const { colorScheme, toggleColorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'

    const springProps = useSpring({
        top: activeTab ? 0 : -65,
        config: {
            tension: 500,
            friction: 40,
        },
    })

    return (
        <div className={classes.header}>
            <animated.div
                className={classes.headerBackground}
                style={{
                    top: springProps.top,
                    zIndex: -1,
                }}
            />
            <Container size="default" className={classes.mainSection}>
                <Group position="apart">
                    {/* Logo */}
                    <div
                        className="logo-sm-container"
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                        }}
                    >
                        <Link to="/" onClick={() => setActiveTab('')}>
                            <img
                                src={darkTheme ? logo_sm : logo_sm_light}
                                alt="mgai"
                                className="logo-sm"
                            />
                        </Link>
                        {/*activeTab && (
                            <div
                                style={{
                                    marginTop: 5,
                                    paddingLeft: 20,
                                    fontSize: 13,
                                    cursor: 'pointer',
                                }}
                                onClick={getApiActiveStatus}
                            >
                                <u>Is the API active?</u>
                            </div>
                        )*/}
                        {location.pathname !== '/legal-information' && (
                            <div
                                style={{
                                    marginTop: 5,
                                    paddingLeft: 20,
                                    fontSize: '0.875rem',
                                    fontWeight: 500,
                                }}
                            >
                                <Link to="/legal-information" className="custom-link">
                                    Legal Information
                                </Link>
                            </div>
                        )}
                    </div>

                    {!user && location.pathname !== '/login' && (
                        <Link
                            to="/login"
                            style={{
                                paddingTop: 4,
                                paddingRight: 30,
                                fontSize: '0.875rem',
                                fontWeight: 500,
                            }}
                            className="custom-link"
                        >
                            Login
                        </Link>
                    )}

                    {/* Tabs */}
                    {user && (
                        <Tabs
                            value={activeTab}
                            // onTabChange={setActiveTab}
                            variant="outline"
                            style={{
                                transform: 'translate(0px,0)',
                            }}
                            classNames={{
                                root: classes.tabs,
                                tabsList: classes.tabsList,
                                tab: classes.tab,
                            }}
                        >
                            <Tabs.List>{items}</Tabs.List>
                        </Tabs>
                    )}

                    {/* User (settings) Menu */}

                    {user && (
                        <div className="user-menu-container">
                            <Menu
                                width={200}
                                position="bottom-end"
                                transitionProps={{ transition: 'pop-top-right' }}
                                onClose={() => setUserMenuOpened(false)}
                                onOpen={() => setUserMenuOpened(true)}
                                withinPortal
                            >
                                <Menu.Target>
                                    <UnstyledButton
                                        className={cx(classes.user, {
                                            [classes.userActive]: userMenuOpened,
                                        })}
                                        style={{ height: 40 }}
                                    >
                                        <Group spacing={7}>
                                            {user && (user.imgurl ? <div></div> : <div></div>)}
                                            <Text
                                                weight={500}
                                                size="sm"
                                                sx={{ lineHeight: 1 }}
                                                mr={3}
                                            >
                                                {user.username ? user.username : 'User'}
                                            </Text>
                                            <IconChevronDown size={rem(12)} stroke={1.5} />
                                        </Group>
                                    </UnstyledButton>
                                </Menu.Target>
                                <Menu.Dropdown
                                    style={{
                                        border: darkTheme ? '1px solid #333' : '1px solid #ced4da',
                                    }}
                                >
                                    <Link to="/profile" onClick={() => setActiveTab('')}>
                                        <Menu.Item icon={<IconUser size="0.9rem" stroke={1.5} />}>
                                            User Profile
                                        </Menu.Item>
                                    </Link>
                                    <Menu.Divider />
                                    <Menu.Item
                                        icon={
                                            darkTheme ? (
                                                <MdOutlineLightMode />
                                            ) : (
                                                <MdOutlineDarkMode />
                                            )
                                        }
                                        onClick={() => toggleColorScheme()}
                                    >
                                        Color Theme
                                    </Menu.Item>
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
    )
}
