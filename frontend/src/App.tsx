import { useState, useEffect } from "react"
import { useQuery, useQueryClient } from "react-query"
import { useNavigate, useLocation } from "react-router-dom"
import { Routes, Route} from "react-router-dom"
import { UserContext } from "./common/UserContext"
import { Toaster, toast } from "react-hot-toast"
import Header from "./components/Header"
import {MDB_IUser as IUser} from "./types/user.type"

import client from "./client"
import { getCookie } from "./client"

import Home from "./components/home/Home"
import Workflow from "./components/workflow/Workflow"
import Database from "./components/Database"
import Profile from "./components/Profile"
import Authentication from "./components/Authentication"

import "bootstrap/dist/css/bootstrap.min.css"
import "./App.css"
import { useMantineColorScheme } from "@mantine/core"

export default function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()
  const version = process.env.REACT_APP_VERSION?.slice(1,-1) ?? "???"

  const {
    data: currentUser,
    isLoading,
    isError,
    error
  } = useQuery<IUser | null | undefined>(
    "getCurrentUser",
    client.getCurrentUser
  )

  useEffect(() => {
    if (isError) {
      const err = error as Error
      console.log(err.message)
    }
  }, [isError, error])

  useEffect(() => {
    if (!currentUser && !isLoading && !['/', '/login'].includes(location.pathname)) {
        navigate('/')
    }
  }, [location, navigate, currentUser, isLoading])
  
  const handleHeaderLinkClick = (key: string) => {
    navigate(key)
  }

  const handleLogout = () => {
    queryClient.setQueryData<IUser | null | undefined>("getCurrentUser", undefined)
    document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=None; Secure";
    navigate("/")
  }

  const { colorScheme } = useMantineColorScheme()
  const darkTheme = colorScheme === 'dark'

  return (
    <div className="app" style={{backgroundColor: darkTheme ? '#1a1b1e' : '#f8f9fa'}}>
      <UserContext.Provider value={currentUser}>
        <div className="header" style={{zIndex:20}}>
            <Header handleHeaderLinkClick={handleHeaderLinkClick} handleLogout={handleLogout}/>
        </div>

        <div className="main" style={{zIndex:10}}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/upload" element={<Workflow uploadMode={true} />} />
            <Route path="/search" element={<Workflow uploadMode={false} />} />
            <Route path="/database" element={<Database />} />
            <Route path="/login" element={<Authentication />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </div>
      </UserContext.Provider>

      <Toaster
        position="top-center"
        containerStyle={{
          top: "75px" // Toast position
        }}
        toastOptions={{
          style: {
            borderRadius: "5px",
            background: "#25262b",
            color: "#C1C2C5"
          }
        }}
      />

      <div
        className="app-version"
        children={`v${version}`}
      />
    </div>
  )
}
