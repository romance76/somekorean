import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)

  // Promise that resolves once initial auth check is complete
  let _resolveInit
  const initPromise = new Promise((resolve) => { _resolveInit = resolve })

  // ── Computed ──
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => !!user.value?.is_admin)

  // ── Initialize from localStorage ──
  function initialize() {
    const savedToken = localStorage.getItem('sk_token')
    const savedUser = localStorage.getItem('sk_user')
    if (savedToken) {
      token.value = savedToken
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
      if (savedUser) {
        try { user.value = JSON.parse(savedUser) } catch { /* ignore */ }
      }
    }
  }

  // ── Auth Actions ──
  async function login(email, password) {
    const { data } = await axios.post('/api/auth/login', { email, password })
    setAuth(data.token, data.user)
    return data
  }

  async function register(form) {
    const { data } = await axios.post('/api/auth/register', form)
    setAuth(data.token, data.user)
    return data
  }

  async function logout() {
    try { await axios.post('/api/auth/logout') } catch { /* ignore */ }
    clearAuth()
  }

  async function fetchUser() {
    try {
      const { data } = await axios.get('/api/auth/me')
      user.value = data.user || data
      localStorage.setItem('sk_user', JSON.stringify(user.value))
    } catch {
      clearAuth()
    } finally {
      _resolveInit()
    }
  }

  async function updateProfile(formData) {
    const { data } = await axios.post('/api/profile/update', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (data.user) {
      user.value = data.user
      localStorage.setItem('sk_user', JSON.stringify(data.user))
    }
    return data
  }

  // Refresh points/level after actions (posting, commenting, etc.)
  async function refreshPoints() {
    try {
      const { data } = await axios.get('/api/points/balance')
      if (user.value) {
        user.value = { ...user.value, points: data.points, cash: data.cash, level: data.level }
        localStorage.setItem('sk_user', JSON.stringify(user.value))
      }
    } catch { /* ignore */ }
  }

  // Resolve init immediately when no token exists
  function resolveInit() { _resolveInit() }

  // ── Internal helpers ──
  function setAuth(tok, usr) {
    token.value = tok
    user.value = usr
    localStorage.setItem('sk_token', tok)
    localStorage.setItem('sk_user', JSON.stringify(usr))
    axios.defaults.headers.common['Authorization'] = `Bearer ${tok}`
  }

  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('sk_token')
    localStorage.removeItem('sk_user')
    delete axios.defaults.headers.common['Authorization']
  }

  return {
    user, token, isLoggedIn, isAdmin, initPromise,
    initialize, login, register, logout,
    fetchUser, updateProfile, refreshPoints, resolveInit,
  }
})
