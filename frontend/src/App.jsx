import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import AdminLoginPage from './pages/AdminLoginPage'
import UserLoginPage from './pages/UserLoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ProjectPage from './pages/ProjectPage'
import ChatPage from './pages/ChatPage'
import LoadingSpinner from './components/LoadingSpinner'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingSpinner fullScreen />
  return user ? children : <Navigate to="/user/login" replace />
}
//done
function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingSpinner fullScreen />
  return user ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/user/login" replace />} />
      <Route path="/admin/login" element={<PublicRoute><AdminLoginPage /></PublicRoute>} />
      <Route path="/user/login" element={<PublicRoute><UserLoginPage /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
       <Route path="/dashboard" element={<PrivateRoute><DashboardPage /></PrivateRoute>} /> 
      <Route path="/projects/:id" element={<PrivateRoute><ProjectPage /></PrivateRoute>} />
      <Route path="/projects/:id/chat" element={<PrivateRoute><ChatPage /></PrivateRoute>} />
      <Route path="*" element={<Navigate to="/user/login" replace />} />
    </Routes>
  )
}
