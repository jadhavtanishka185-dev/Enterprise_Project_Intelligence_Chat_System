import api from './api'

export const authService = {
  // User registration endpoint
  userRegister: async (name, email, password) => {
    const { data } = await api.post('/auth/user/register', { name, email, password })
    return data
  },

  // Admin login endpoint
  adminLogin: async (email, password) => {
    const { data } = await api.post('/auth/admin/login', { email, password })
    return data
  },

  // User login endpoint
  userLogin: async (email, password) => {
    const { data } = await api.post('/auth/user/login', { email, password })
    return data
  },

  // Legacy login (kept for backward compatibility)
  login: async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    return data
  },

  getMe: async () => {
    const { data } = await api.get('/auth/me')
    return data
  },
}
