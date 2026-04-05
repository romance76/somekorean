import { create } from 'zustand'
import * as SecureStore from 'expo-secure-store'
import api from '../services/api'

export const useAuthStore = create((set, get) => ({
  user: null,
  token: null,
  isLoggedIn: false,
  loading: true,

  init: async () => {
    try {
      const token = await SecureStore.getItemAsync('token')
      if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        const { data } = await api.get('/auth/me')
        set({ user: data, token, isLoggedIn: true, loading: false })
      } else {
        set({ loading: false })
      }
    } catch {
      await SecureStore.deleteItemAsync('token')
      set({ loading: false })
    }
  },

  login: async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    await SecureStore.setItemAsync('token', data.access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    set({ user: data.user, token: data.access_token, isLoggedIn: true })
    return data
  },

  register: async (payload) => {
    const { data } = await api.post('/auth/register', payload)
    await SecureStore.setItemAsync('token', data.access_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    set({ user: data.user, token: data.access_token, isLoggedIn: true })
    return data
  },

  logout: async () => {
    try { await api.post('/auth/logout') } catch {}
    await SecureStore.deleteItemAsync('token')
    delete api.defaults.headers.common['Authorization']
    set({ user: null, token: null, isLoggedIn: false })
  },

  updateUser: (user) => set({ user }),
}))
