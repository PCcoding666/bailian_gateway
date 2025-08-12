// API utility functions
const API_BASE_URL = '/api'

// Get auth headers
export const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// Generic API call function
export const apiCall = async (endpoint, method = 'GET', data = null, useAuth = true) => {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = {
    'Content-Type': 'application/json',
    ...(useAuth ? getAuthHeaders() : {})
  }

  const config = {
    method,
    headers,
    ...(data ? { body: JSON.stringify(data) } : {})
  }

  try {
    const response = await fetch(url, config)
    const result = await response.json()
    
    if (!response.ok) {
      throw new Error(result.message || 'API call failed')
    }
    
    return result
  } catch (error) {
    console.error('API call error:', error)
    throw error
  }
}

// Auth API functions
export const authAPI = {
  login: (username, password) => 
    apiCall('/auth/login', 'POST', { username, password }, false),
  
  register: (userData) => 
    apiCall('/auth/register', 'POST', userData, false),
  
  refresh: (refreshToken) => 
    apiCall('/auth/refresh', 'POST', { refresh_token: refreshToken }, false),
  
  getCurrentUser: () => 
    apiCall('/auth/user', 'GET'),
  
  updateCurrentUser: (userData) => 
    apiCall('/auth/user', 'PUT', userData)
}

// Conversation API functions
export const conversationAPI = {
  create: (data) => 
    apiCall('/conversations', 'POST', data),
  
  list: (page = 1, limit = 10) => 
    apiCall(`/conversations?page=${page}&limit=${limit}`, 'GET'),
  
  get: (id) => 
    apiCall(`/conversations/${id}`, 'GET'),
  
  update: (id, data) => 
    apiCall(`/conversations/${id}`, 'PUT', data),
  
  delete: (id) => 
    apiCall(`/conversations/${id}`, 'DELETE'),
  
  sendMessage: (conversationId, content) => 
    apiCall(`/conversations/${conversationId}/messages`, 'POST', { content }),
  
  getMessages: (conversationId, page = 1, limit = 20) => 
    apiCall(`/conversations/${conversationId}/messages?page=${page}&limit=${limit}`, 'GET')
}

// Bailian API functions
export const bailianAPI = {
  chatCompletion: (data) => 
    apiCall('/bailian/chat/completions', 'POST', data),
  
  generation: (data) => 
    apiCall('/bailian/generation', 'POST', data)
}