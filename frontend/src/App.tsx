import { useState, useEffect, useCallback } from 'react'
import { useQuery, useQueryClient } from 'react-query'
import { useNavigate, useLocation } from 'react-router-dom'
import { Routes, Route } from 'react-router-dom'
import { UserContext } from './context/UserContext'
import { Toaster } from 'react-hot-toast'
import Header from './components/Header'
import { MDB_IUser as IUser } from './types/user.type'

import client from './client'
import { getCookie } from './client'

import Home from './components/home/Home'
import Workspace from './components/workspace/Workspace'
import Database from './components/Database'
import Profile from './components/Profile'
import Authentication from './components/Authentication'
import Legal from './components/legal/Legal'

import 'bootstrap/dist/css/bootstrap.min.css'
import './App.css'
import { useMantineColorScheme } from '@mantine/core'
import CookieInfo from './components/CookieInfo'

export default function App() {
    const navigate = useNavigate()
    const location = useLocation()
    const queryClient = useQueryClient()
    const version = process.env.REACT_APP_VERSION?.slice(1, -1) ?? '???'

    const [showCookieInfo, setShowCookieInfo] = useState(false)

    const {
        data: currentUser,
        isLoading: userIsLoading,
        isError: userIsError,
        error: userError,
    } = useQuery<IUser | null | undefined>('getCurrentUser', client.getCurrentUser)

    useEffect(() => {
        if (userIsError) {
            const err = userError as Error
            console.log(err.message)
        }
    }, [userIsError, userError])

    useEffect(() => {
        if (
            !currentUser &&
            !userIsLoading &&
            !['/', '/login', '/legal-information'].includes(location.pathname)
        ) {
            navigate('/')
        }
    }, [location, navigate, currentUser, userIsLoading])

    const handleLogout = () => {
        queryClient.setQueryData<IUser | null | undefined>('getCurrentUser', undefined)
        document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=None; Secure'
        navigate('/')
    }

    const handleHeaderLinkClick = (key: string) => {
        navigate(key)
    }

    const getCookieConsent = useCallback(() => {
        if (getCookie('cookieConsent') !== 'true') {
            setShowCookieInfo(true)
        }
    }, [])

    useEffect(() => {
        getCookieConsent()
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [location])

    const setCookieConsent = () => {
        const d = new Date()
        d.setTime(d.getTime() + 365 * 24 * 60 * 60 * 1000)
        const expires = 'expires=' + d.toUTCString()
        document.cookie = `cookieConsent=true; ${expires}; SameSite=None; Secure`
        setTimeout(() => {
            setShowCookieInfo(false)
        }, 100)
    }

    const { colorScheme } = useMantineColorScheme()
    const darkTheme = colorScheme === 'dark'

    return (
        <div className="app" style={{ backgroundColor: darkTheme ? '#1a1b1e' : '#f8f9fa' }}>
            <UserContext.Provider value={currentUser}>
                <div className="header" style={{ zIndex: 20 }}>
                    <Header
                        handleHeaderLinkClick={handleHeaderLinkClick}
                        handleLogout={handleLogout}
                    />
                </div>

                <div className="main" style={{ zIndex: 10 }}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/upload" element={<Workspace uploadMode={true} />} />
                        <Route path="/search" element={<Workspace uploadMode={false} />} />
                        <Route path="/database" element={<Database />} />
                        <Route path="/login" element={<Authentication />} />
                        <Route path="/profile" element={<Profile />} />
                        <Route path="/legal-information" element={<Legal />} />
                    </Routes>
                </div>
            </UserContext.Provider>

            <Toaster
                position="top-center"
                containerStyle={{
                    top: '75px', // Toast position
                }}
                toastOptions={{
                    style: {
                        borderRadius: '5px',
                        background: '#25262b',
                        color: '#C1C2C5',
                    },
                }}
            />

            <div className="app-version" children={`v${version}`} />
            {showCookieInfo && (
                <CookieInfo setCookieConsent={setCookieConsent} darkTheme={darkTheme} />
            )}
        </div>
    )
}
