import './bootstrap'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { useSiteStore } from './stores/site'

// ── Pinia + App ──
const pinia = createPinia()
const app = createApp(App)
app.use(pinia)
app.use(router)

// ── Auth initialization ──
const authStore = useAuthStore()
authStore.initialize()
if (authStore.isLoggedIn) {
  authStore.fetchUser()
} else {
  authStore.resolveInit()
}

// ── Load site settings (menus, site name, logo) ──
const siteStore = useSiteStore()
siteStore.load()

// ── WebSocket (Laravel Echo + Reverb) ──
try {
  const Echo = (await import('laravel-echo')).default
  const Pusher = (await import('pusher-js')).default
  window.Pusher = Pusher
  window.Echo = new Echo({
    broadcaster: 'reverb',
    key: import.meta.env.VITE_REVERB_APP_KEY,
    wsHost: import.meta.env.VITE_REVERB_HOST,
    wsPort: import.meta.env.VITE_REVERB_PORT ?? 80,
    wssPort: import.meta.env.VITE_REVERB_PORT ?? 443,
    forceTLS: (import.meta.env.VITE_REVERB_SCHEME ?? 'https') === 'https',
    enabledTransports: ['ws', 'wss'],
    authEndpoint: '/broadcasting/auth',
    auth: {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('sk_token') ?? ''}`,
      },
    },
  })
} catch {
  // Echo/Pusher not available - continue without websockets
}

// ── Refresh Echo auth header after navigation ──
router.afterEach(() => {
  const token = localStorage.getItem('sk_token')
  if (window.Echo && token) {
    window.Echo.options.auth.headers.Authorization = `Bearer ${token}`
  }
})

// ── Mount ──
app.mount('#app')

// ── Chunk load error handler (auto-refresh on stale builds) ──
router.onError((err) => {
  const isChunkError =
    err?.message?.includes('Failed to fetch dynamically imported module') ||
    err?.message?.includes('Loading chunk') ||
    err?.name === 'ChunkLoadError'
  if (isChunkError) {
    const lastReload = sessionStorage.getItem('_chunk_reload')
    const now = Date.now()
    if (!lastReload || now - Number(lastReload) > 10000) {
      sessionStorage.setItem('_chunk_reload', String(now))
      window.location.reload()
    }
  }
})

// ── Service Worker (PWA) ──
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(() => {})
}
