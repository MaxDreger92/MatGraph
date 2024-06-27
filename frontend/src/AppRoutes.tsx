import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './components/home/Home'
import Users from './components/admin/Users'
import Workflow from './components/workflow/Workflow'
import Database from './components/Database'
import Profile from './components/Profile'
import Authentication from './components/Authentication'
import Legal from './components/legal/Legal'

export default function AppRoutes() {
    return (
        <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/users" element={<Users />} />
        <Route path="/upload" element={<Workflow uploadMode={true} />} />
        <Route path="/search" element={<Workflow uploadMode={false} />} />
        <Route path="/database" element={<Database />} />
        <Route path="/login" element={<Authentication />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/legal-information" element={<Legal />} />
    </Routes>
    )
}