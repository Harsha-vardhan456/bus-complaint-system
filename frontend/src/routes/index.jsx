import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from '../pages/Home'
import AdminDashboard from '../pages/admin/AdminDashboard'
import ComplaintForm from '../pages/complaints/ComplaintForm'
import Login from '../pages/auth/Login'
import Register from '../pages/auth/Register'
import ProtectedAdminRoute from '../components/ProtectedAdminRoute'

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/submit-complaint" element={<ComplaintForm />} />
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedAdminRoute>
            <AdminDashboard />
          </ProtectedAdminRoute>
        }
      />
    </Routes>
  )
}

export default AppRoutes