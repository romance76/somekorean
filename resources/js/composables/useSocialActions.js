import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useSiteStore } from '../stores/site'
import axios from 'axios'

/** Auth guard — returns false + toast if not logged in */
function requireAuth() {
  const auth = useAuthStore()
  if (!auth.isLoggedIn) {
    const site = useSiteStore()
    site.toast('로그인이 필요합니다', 'error')
    return false
  }
  return true
}

/**
 * 친구 요청 (간단 버전 — 상세 UI는 UserPopup.vue 사용)
 */
export function useFriendAction() {
  const loading = ref(false)
  const site = useSiteStore()

  async function sendRequest(targetUserId) {
    if (!requireAuth()) return false
    loading.value = true
    try {
      const { data } = await axios.post(`/api/friends/request/${targetUserId}`)
      if (data.auto_accepted) {
        site.toast('서로 친구가 되었습니다!', 'success')
      } else {
        site.toast('친구 요청을 보냈습니다', 'success')
      }
      return true
    } catch (e) {
      site.toast(e.response?.data?.message || '친구 요청 실패', 'error')
      return false
    } finally {
      loading.value = false
    }
  }

  return { sendRequest, loading }
}

/**
 * 쪽지 보내기
 */
export function useMessage() {
  const showModal = ref(false)
  const content = ref('')
  const sending = ref(false)
  const sent = ref(false)
  const sentContent = ref('')
  const site = useSiteStore()

  function open() {
    if (!requireAuth()) return
    content.value = ''
    sent.value = false
    sentContent.value = ''
    showModal.value = true
  }

  async function send(targetUserId) {
    if (!content.value.trim()) return false
    sending.value = true
    try {
      await axios.post('/api/messages', {
        receiver_id: targetUserId,
        content: content.value.trim(),
      })
      sentContent.value = content.value.trim()
      content.value = ''
      sent.value = true
      site.toast('쪽지를 보냈습니다', 'success')
      return true
    } catch (e) {
      site.toast(e.response?.data?.message || '쪽지 전송 실패', 'error')
      return false
    } finally {
      sending.value = false
    }
  }

  function reset() {
    content.value = ''
    sent.value = false
    sentContent.value = ''
    showModal.value = false
  }

  return { showModal, content, sending, sent, sentContent, open, send, reset }
}

/**
 * 좋아요 토글 (Bookmark API 기반 — market, realestate, job 등)
 */
export function useBookmarkLike(bookmarkableType) {
  const liked = ref(false)
  const loading = ref(false)
  const site = useSiteStore()

  async function check(itemId) {
    const auth = useAuthStore()
    if (!auth.isLoggedIn || !itemId) return
    try {
      const { data } = await axios.get('/api/bookmarks/check', {
        params: { type: bookmarkableType, ids: itemId },
      })
      liked.value = (data.data || []).includes(itemId)
    } catch {}
  }

  async function toggle(itemId) {
    if (!requireAuth()) return
    loading.value = true
    try {
      const { data } = await axios.post('/api/bookmarks', {
        bookmarkable_type: bookmarkableType,
        bookmarkable_id: itemId,
      })
      liked.value = data.bookmarked
      return data.bookmarked
    } catch (e) {
      site.toast('처리 실패', 'error')
    } finally {
      loading.value = false
    }
  }

  return { liked, loading, check, toggle }
}

/**
 * 신고하기
 */
export function useReport() {
  const showModal = ref(false)
  const loading = ref(false)
  const reported = ref(false)
  const site = useSiteStore()

  function open() {
    if (!requireAuth()) return
    showModal.value = true
  }

  async function submit(reportableType, reportableId, reason, customContent) {
    loading.value = true
    try {
      await axios.post('/api/reports', {
        reportable_type: reportableType,
        reportable_id: reportableId,
        reason,
        content: customContent || '',
      })
      reported.value = true
      showModal.value = false
      site.toast('신고가 접수되었습니다', 'success')
      return true
    } catch (e) {
      site.toast(e.response?.data?.message || '신고 접수 실패', 'error')
      return false
    } finally {
      loading.value = false
    }
  }

  return { showModal, loading, reported, open, submit }
}

/**
 * 게시글 좋아요 (PostLike API 기반)
 */
export function usePostLike() {
  const liked = ref(false)
  const loading = ref(false)

  async function toggle(postId) {
    if (!requireAuth()) return
    loading.value = true
    try {
      const { data } = await axios.post(`/api/posts/${postId}/like`)
      liked.value = data.liked
      return data.liked
    } catch {} finally {
      loading.value = false
    }
  }

  return { liked, loading, toggle }
}
