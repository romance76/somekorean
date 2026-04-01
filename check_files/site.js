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
    } catch { /* 실패해도 기본값 유지 (모두 표시) */ }
    finally { loaded.value = true }
  }

  /** key에 해당 메뉴가 enabled인지. 설정이 없으면 true(기본 표시) */
  function isEnabled(key) {
    if (!menus.value.length) return true
    const m = menus.value.find(item => item.key === key)
    return m ? m.enabled !== false : true
  }

  return { menus, siteName, logoUrl, loaded, load, isEnabled }
})
