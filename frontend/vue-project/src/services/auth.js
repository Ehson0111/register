import api from './api'
import axios from 'axios'

const authService = {
  async login(credentials) {
    return await api.post('/auth/login/', credentials)
  },

  async register(userData) {
    return await api.post('/users/register/', userData)
  },

  async registerVerify(payload) {
    return await api.post('/users/register/verify/', payload)
  },

  async refreshToken(refresh) {
    // Важно: refresh делаем через отдельный axios, чтобы не попасть в interceptor recursion.
    const plain = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' }
    })
    return await plain.post('/auth/refresh/', { refresh })
  },

  async passwordResetRequest(email) {
    return await api.post('/auth/password-reset/request/', { email })
  },

  async passwordResetConfirm(payload) {
    return await api.post('/auth/password-reset/confirm/', payload)
  },

  async getProfile() {
    return await api.get('/users/profile/')
  },

  async updateProfile(userData) {
    return await api.put('/users/profile/update/', userData)
  },

  async logout() {
    // In a real app, you might want to call a logout endpoint
    // to invalidate the token on the server
    return Promise.resolve()
  }
}

export default authService
