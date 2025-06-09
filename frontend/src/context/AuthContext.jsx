import React, { createContext, useState, useContext, useEffect } from 'react'
import authService from '../services/authService'
import jwt_decode from 'jwt-decode'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const token = localStorage.getItem('userToken')
    if (token) {
      try {
        const decoded = jwt_decode(token)
        setIsAuthenticated(true)
        setUser({
          email: decoded.email,
          role: decoded.role
        })
        setIsAdmin(decoded.role === 'admin')
      } catch (error) {
        console.error('Invalid token:', error)
        logout()
      }
    }
  }, [])

  const login = async (credentials) => {
    try {
      const response = await authService.login(credentials)
      const decoded = jwt_decode(response.token)
      setIsAuthenticated(true)
      setUser({
        ...response.user,
        role: decoded.role
      })
      setIsAdmin(decoded.role === 'admin')
      return response
    } catch (error) {
      const errorMessage = error.details || error.message || 'Login failed. Please check your credentials.'
      throw { message: errorMessage }
    }
  }

  const logout = () => {
    authService.logout()
    setIsAuthenticated(false)
    setUser(null)
    setIsAdmin(false)
  }

  const value = {
    isAuthenticated,
    isAdmin,
    user,
    login,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
