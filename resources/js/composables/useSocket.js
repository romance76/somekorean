import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'

let socket = null
const isConnected = ref(false)
const connectionError = ref(null)

export function useSocket() {
  function connect() {
    if (socket?.connected) return
    const token = localStorage.getItem('sk_token')
    if (!token) return

    socket = io(window.location.origin, {
      path: '/socket.io/',
      auth: { token },
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
    })

    socket.on('connect', () => {
      isConnected.value = true
      connectionError.value = null
      console.log('[Socket] Connected')
    })

    socket.on('disconnect', (reason) => {
      isConnected.value = false
      console.log('[Socket] Disconnected:', reason)
    })

    socket.on('connect_error', (err) => {
      connectionError.value = err.message
      console.error('[Socket] Connection error:', err.message)
    })
  }

  function disconnect() {
    if (socket) {
      socket.disconnect()
      socket = null
      isConnected.value = false
    }
  }

  function emit(event, data) {
    if (socket?.connected) socket.emit(event, data)
  }

  function on(event, callback) {
    if (socket) socket.on(event, callback)
  }

  function off(event, callback) {
    if (socket) socket.off(event, callback)
  }

  return { socket: () => socket, isConnected, connectionError, connect, disconnect, emit, on, off }
}
