import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import { useSiteStore } from './site'
import axios from 'axios'

export const useBookmarkStore = defineStore('bookmarks', () => {
  // type별 북마크된 ID Set — { 'post': Set([1,2,3]), 'App\\Models\\JobPost': Set([5,8]) }
  const bookmarkedIds = ref({})
  let loaded = false
  let loadPromise = null

  /** 로그인 시 한 번만 전체 북마크 로드 */
  async function loadAll() {
    const auth = useAuthStore()
    if (!auth.isLoggedIn) return
    if (loaded) return
    if (loadPromise) return loadPromise
    loadPromise = _doLoad()
    return loadPromise
  }

  async function _doLoad() {
    try {
      const { data } = await axios.get('/api/bookmarks', { params: { per_page: 500 } })
      const items = data.data?.data || data.data || []
      const map = {}
      items.forEach(b => {
        const type = b.bookmarkable_type || ''
        if (!map[type]) map[type] = new Set()
        map[type].add(b.bookmarkable_id)
      })
      bookmarkedIds.value = map
    } catch {}
    loaded = true
    loadPromise = null
  }

  /** 특정 아이템이 북마크되었는지 체크 (로컬, API 호출 없음) */
  function isBookmarked(type, id) {
    return bookmarkedIds.value[type]?.has(id) || false
  }

  /** 특정 타입의 북마크된 ID 배열 반환 */
  function getBookmarkedIds(type) {
    return bookmarkedIds.value[type] ? [...bookmarkedIds.value[type]] : []
  }

  /** 북마크 토글 (API 호출 + 로컬 상태 업데이트) */
  async function toggle(type, id) {
    const auth = useAuthStore()
    if (!auth.isLoggedIn) {
      useSiteStore().toast('로그인이 필요합니다', 'error')
      return null
    }
    try {
      const { data } = await axios.post('/api/bookmarks', {
        bookmarkable_type: type,
        bookmarkable_id: id,
      })
      // 로컬 상태 즉시 업데이트
      if (!bookmarkedIds.value[type]) bookmarkedIds.value[type] = new Set()
      if (data.bookmarked) {
        bookmarkedIds.value[type].add(id)
      } else {
        bookmarkedIds.value[type].delete(id)
      }
      return data.bookmarked
    } catch {
      useSiteStore().toast('처리 실패', 'error')
      return null
    }
  }

  /** 로그아웃 시 초기화 */
  function clear() {
    bookmarkedIds.value = {}
    loaded = false
    loadPromise = null
  }

  return { bookmarkedIds, loadAll, isBookmarked, getBookmarkedIds, toggle, clear }
})
