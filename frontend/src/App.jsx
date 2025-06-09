import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box, Container } from '@mui/material'
import { AuthProvider } from './context/AuthContext'

// Layout components
import Navbar from './components/layout/Navbar'
import Footer from './components/layout/Footer'

// Page components
import Home from './pages/Home'
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Dashboard from './pages/dashboard/Dashboard'
import ComplaintForm from './pages/complaints/ComplaintForm'
import ComplaintTracker from './pages/complaints/ComplaintTracker'
import AdminRoute from './routes/AdminRoute'
import AdminDashboard from './pages/admin/AdminDashboard'

const App = () => {
  return (
    <AuthProvider>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Container component="main" sx={{ flex: 1, py: 4 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/submit-complaint" element={<ComplaintForm />} />
          <Route path="/track-complaint" element={<ComplaintTracker />} />
          <Route
            path="/admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
      <Footer />
    </Box>
    </AuthProvider>
  )
}

export default App