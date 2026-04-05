import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useSiteStore = defineStore('site', () => {
  // ── Site settings ──
  const siteName = ref('SomeKorean')
  const logoUrl = ref(null)
  const menus = ref([])
  const loaded = ref(false)

  // ── Global loading state ──
  const globalLoading = ref(false)

  // ── Dark mode ──
  const darkMode = ref(localStorage.getItem('sk_dark') === 'true')

  // ── Toast notifications ──
  const toasts = ref([])
  let toastId = 0

  function toast(message, type = 'info', duration = 3000) {
    const id = ++toastId
    toasts.value.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => removeToast(id), duration)
    }
  }

  function removeToast(id) {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  function toggleDark() {
    darkMode.value = !darkMode.value
    localStorage.setItem('sk_dark', darkMode.value)
  }

  // ── Load site settings from API ──
  async function load() {
    if (loaded.value) return
    try {
      const { data } = await axios.get('/api/settings/public')
      menus.value = Array.isArray(data.menus) ? data.menus : []
      siteName.value = data.site_name || 'SomeKorean'
      logoUrl.value = data.logo_url || null
    } catch { /* use defaults */ }
    finally { loaded.value = true }
  }

  // Check if a menu key is enabled by admin settings
  function isEnabled(key) {
    if (!menus.value.length) return true
    const m = menus.value.find(item => item.key === key)
    return m ? m.enabled !== false : true
  }

  // Get admin-configured sort order for a menu key
  function getOrder(key) {
    if (!menus.value.length) return 999
    const idx = menus.value.findIndex(item => item.key === key)
    return idx >= 0 ? idx : 999
  }

  return {
    siteName, logoUrl, menus, loaded, globalLoading,
    darkMode, toasts,
    load, isEnabled, getOrder,
    toast, removeToast, toggleDark,
  }
})
