import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useSiteStore = defineStore('site', () => {
  const menus    = ref([])
  const siteName = ref('SomeKorean')
  const logoUrl  = ref(null)
  const loaded   = ref(false)

  async function load() {
    if (loaded.value) return
    try {
      const { data } = await axios.get('/api/settings/public')
      menus.value    = Array.isArray(data.menus) ? data.menus : []
      siteName.value = data.site_name || 'SomeKorean'
      logoUrl.value  = data.logo_url  || null
    } catch { /* 실패해도 기본값 유지 */ }
    finally { loaded.value = true }
  }

  function isEnabled(key) {
    if (!menus.value.length) return true
    const m = menus.value.find(item => item.key === key)
    return m ? m.enabled !== false : true
  }

  /** 관리자가 설정한 순서대로 정렬 */
  function getOrder(key) {
    if (!menus.value.length) return 999
    const idx = menus.value.findIndex(item => item.key === key)
    return idx >= 0 ? idx : 999
  }

  return { menus, siteName, logoUrl, loaded, load, isEnabled, getOrder }
})
