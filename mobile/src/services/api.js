import axios from 'axios'
import * as SecureStore from 'expo-secure-store'

export const BASE_URL = 'https://somekorean.com/api'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
})

// 요청 인터셉터: 토큰 자동 첨부
api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 응답 인터셉터: 401 처리
api.interceptors.response.use(
  res => res,
  async (err) => {
    if (err.response?.status === 401) {
      await SecureStore.deleteItemAsync('token')
    }
    return Promise.reject(err)
  }
)

export default api
