import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import MainPage from './pages/MainPage'
import ConversationDetailPage from './pages/ConversationDetailPage'
import HistoryPage from './pages/HistoryPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)

  // Check if user is authenticated on app load
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      // In a real app, you would verify the token with the backend
      setIsAuthenticated(true)
      // Load user data from localStorage or fetch from backend
      const userData = JSON.parse(localStorage.getItem('user_data') || '{}')
      setUser(userData)
    }
  }, [])

  const handleLogin = (userData) => {
    setIsAuthenticated(true)
    setUser(userData)
    // Store user data in localStorage
    localStorage.setItem('user_data', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setUser(null)
    // Clear tokens and user data from localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/login" 
            element={isAuthenticated ? <Navigate to="/" /> : <LoginPage onLogin={handleLogin} />} 
          />
          <Route 
            path="/register" 
            element={isAuthenticated ? <Navigate to="/" /> : <RegisterPage onLogin={handleLogin} />} 
          />
          <Route 
            path="/" 
            element={isAuthenticated ? <MainPage user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/conversations/:id" 
            element={isAuthenticated ? <ConversationDetailPage user={user} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/history" 
            element={isAuthenticated ? <HistoryPage user={user} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/settings" 
            element={isAuthenticated ? <SettingsPage user={user} /> : <Navigate to="/login" />} 
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App