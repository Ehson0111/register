import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authService from '../services/auth.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const userName = computed(() => {
    if (!user.value) return ''
    return `${user.value.first_name} ${user.value.last_name}`.trim() || user.value.email
  })

  async function login(credentials) {
    try {
      loading.value = true
      const response = await authService.login(credentials)

      if (response.data) {
        token.value = response.data.access
        refreshToken.value = response.data.refresh
        user.value = response.data.user

        localStorage.setItem('access_token', response.data.access)
        localStorage.setItem('refresh_token', response.data.refresh)

        return { success: true }
      }

      return { success: false, error: 'Invalid response from server' }
    } catch (error) {
      console.error('Login error:', error)
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed'
      }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function fetchProfile() {
    try {
      if (!token.value) return

      const response = await authService.getProfile()
      if (response.data) {
        user.value = response.data
      }
    } catch (error) {
      console.error('Fetch profile error:', error)
      if (error.response?.status === 401 || error.response?.status === 403) {
        await logout()
      }
    }
  }

  async function refreshAccessToken() {
    try {
      if (!refreshToken.value) return false

      const response = await authService.refreshToken(refreshToken.value)

      if (response.data?.access) {
        token.value = response.data.access
        localStorage.setItem('access_token', response.data.access)
        return true
      }

      return false
    } catch (error) {
      console.error('Token refresh error:', error)

      if (error.response?.status === 401) {
        await logout()
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }

      return false
    }
  }

  return {
    user,
    token,
    refreshToken,
    loading,
    isAuthenticated,
    userName,
    login,
    logout,
    fetchProfile,
    refreshAccessToken
  }
})
