import { useState, useEffect } from "react"
import { useQuery, useQueryClient } from "react-query"
import { useNavigate, useLocation } from "react-router-dom"
import { Routes, Route} from "react-router-dom"
import { UserContext } from "./common/UserContext"
import { Toaster, toast } from "react-hot-toast"
import Header from "./components/Header"
import {MDB_IUser as IUser} from "./types/user.type"

import client from "./client"

import Home from "./components/Home"
import Workflow from "./components/workflow/Workflow"
import Database from "./components/Database"
import Profile from "./components/Profile"
import Authentication from "./components/Authentication"

import "bootstrap/dist/css/bootstrap.min.css"
import "./App.css"

export default function App() {
  const navigate = useNavigate()
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
    // navigate to login after getCurrentUser is 
    // resolved and currentUser is undefined
    // errors are caught separately
    if (!isLoading && !currentUser) {
      navigate("/login")
    }
  }, [isLoading, currentUser, navigate])

  useEffect(() => {
    if (isError) {
      const err = error as Error
      console.log(err.message)
    }
  }, [isError, error])

  // useEffect(() => {
  //   if (isLoading) {
  //     //something
  //   }
  // }, [isLoading])
  
  const handleHeaderLinkClick = (key: string) => {
    navigate(key)
  }

  const handleLogout = () => {
    queryClient.setQueryData<IUser | null | undefined>("getCurrentUser", undefined)
    document.cookie = "token="
    navigate("/login")
  }

  return (
    <div className="app">
      <UserContext.Provider value={currentUser}>
        {currentUser && (
          <div className="header">
            <Header handleHeaderLinkClick={handleHeaderLinkClick} handleLogout={handleLogout}/>
          </div>
        )}
        {/* <div className="header">
          <HeaderTabs onHeaderLinkClick={handleHeaderLinkClick} onLogout={handleLogout} tab={activeTab} setTab={setTab}/>
        </div> */}
        <div className="main">
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
