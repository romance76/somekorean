<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- 헤더 -->
    <div class="px-5 py-3 border-b border-gray-100">
      <h3 class="font-semibold text-gray-800 text-sm">댓글 {{ comments.length }}개</h3>
    </div>

    <!-- 댓글 목록 -->
    <ul v-if="comments.length">
      <li v-for="comment in topLevelComments" :key="comment.id" class="border-b border-gray-50 last:border-0">
        <!-- 댓글 본체 -->
        <div class="px-5 py-3.5">
          <div class="flex items-start justify-between">
            <div class="flex items-start gap-2 flex-1">
              <div class="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center text-gray-500 text-xs font-bold flex-shrink-0 mt-0.5">
                {{ (comment.user?.name || comment.user_name || '익명')[0] }}
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-sm font-medium text-gray-800">{{ comment.user?.name || comment.user_name || '익명' }}</span>
                  <span class="text-xs text-gray-400">{{ formatRelative(comment.created_at) }}</span>
                  <span v-if="comment.is_accepted" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">채택됨</span>
                </div>
                <p class="text-sm text-gray-700 whitespace-pre-line">{{ comment.content }}</p>
                <!-- 좋아요 / 답글 버튼 -->
                <div class="flex items-center gap-3 mt-2">
                  <button @click="likeComment(comment)" class="flex items-center gap-1 text-xs text-gray-400 hover:text-red-500 transition">
                    <svg class="w-3.5 h-3.5" :fill="comment.is_liked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                    </svg>
                    <span :class="comment.is_liked ? 'text-red-500' : ''">{{ comment.like_count || 0 }}</span>
                  </button>
                  <button v-if="auth.isLoggedIn" @click="replyTo = replyTo === comment.id ? null : comment.id"
                    class="text-xs text-gray-400 hover:text-blue-500 transition">
                    답글
                  </button>
                </div>
              </div>
            </div>
            <button v-if="auth.user?.id === comment.user_id || auth.user?.id === comment.user?.id || auth.user?.is_admin"
              @click="deleteComment(comment.id)" class="text-xs text-gray-300 hover:text-red-400 ml-2">삭제</button>
          </div>

          <!-- 답글 입력 -->
          <div v-if="replyTo === comment.id" class="ml-9 mt-3">
            <div class="flex gap-2">
              <input v-model="replyText" @keyup.enter.ctrl="submitReply(comment.id)" type="text"
                :placeholder="`${comment.user?.name || ''}님에게 답글...`"
                class="w-full border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <button @click="submitReply(comment.id)" :disabled="!replyText.trim()"
                class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-blue-700 disabled:opacity-40 whitespace-nowrap">등록</button>
            </div>
          </div>
        </div>

        <!-- 대댓글 -->
        <div v-if="getReplies(comment.id).length" class="bg-gray-50/50">
          <div v-for="reply in getReplies(comment.id)" :key="reply.id" class="px-5 py-3 ml-9 border-t border-gray-100">
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-2 flex-1">
                <div class="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-gray-500 text-[10px] font-bold flex-shrink-0 mt-0.5">
                  {{ (reply.user?.name || reply.user_name || '익명')[0] }}
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-0.5">
                    <span class="text-sm font-medium text-gray-700">{{ reply.user?.name || reply.user_name || '익명' }}</span>
                    <span class="text-xs text-gray-400">{{ formatRelative(reply.created_at) }}</span>
                  </div>
                  <p class="text-sm text-gray-600">{{ reply.content }}</p>
                </div>
              </div>
              <button v-if="auth.user?.id === reply.user_id || auth.user?.id === reply.user?.id || auth.user?.is_admin"
                @click="deleteComment(reply.id)" class="text-xs text-gray-300 hover:text-red-400 ml-2">삭제</button>
            </div>
          </div>
        </div>
      </li>
    </ul>
    <div v-else class="px-5 py-8 text-center text-sm text-gray-400">아직 댓글이 없습니다. 첫 댓글을 남겨보세요!</div>

    <!-- 댓글 입력 -->
    <div v-if="auth.isLoggedIn" class="px-5 py-3 bg-gray-50 border-t border-gray-100">
      <div class="flex gap-2">
        <input v-model="commentText" @keyup.enter.ctrl="submitComment" type="text" placeholder="댓글을 입력하세요 (Ctrl+Enter)"
          class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <button @click="submitComment" :disabled="!commentText.trim() || submitting"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-40 whitespace-nowrap">
          {{ submitting ? '...' : '등록' }}
        </button>
      </div>
    </div>
    <div v-else class="px-5 py-3 bg-gray-50 border-t border-gray-100 text-center">
      <router-link to="/auth/login" class="text-blue-600 text-sm hover:underline">로그인 후 댓글을 작성할 수 있습니다</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const props = defineProps({
  commentableType: { type: String, required: true },   // 'post', 'qa_question', 'event', 'market', 'job', 'news', 'recipe', 'realestate'
  commentableId: { type: Number, required: true }
})

const auth = useAuthStore()
const comments = ref([])
const commentText = ref('')
const replyTo = ref(null)
const replyText = ref('')
const submitting = ref(false)
const loading = ref(false)

// 최상위 댓글만
const topLevelComments = computed(() =>
  comments.value.filter(c => !c.parent_id)
)

// 특정 댓글의 대댓글
function getReplies(parentId) {
  return comments.value.filter(c => c.parent_id === parentId)
}

// type별 API 엔드포인트 매핑
function getApiBase() {
  const type = props.commentableType
  const id = props.commentableId
  // 커뮤니티 게시글은 /api/posts/{id}/comments
  if (type === 'post') return `/api/posts/${id}/comments`
  if (type === 'event') return `/api/events/${id}/comments`
  if (type === 'market') return `/api/market/${id}/comments`
  if (type === 'job') return `/api/jobs/${id}/comments`
  if (type === 'news') return `/api/news/${id}/comments`
  if (type === 'recipe') return `/api/recipes/${id}/comments`
  if (type === 'realestate') return `/api/realestate/${id}/comments`
  if (type === 'qa_question') return `/api/posts/${id}/comments`
  return `/api/posts/${id}/comments`
}

async function loadComments() {
  loading.value = true
  try {
    const { data } = await axios.get(getApiBase())
    comments.value = data.comments || data.data || data || []
  } catch {
    comments.value = []
  } finally {
    loading.value = false
  }
}

async function submitComment() {
  if (!commentText.value.trim() || submitting.value) return
  submitting.value = true
  try {
    const { data } = await axios.post(getApiBase(), { content: commentText.value })
    const newComment = data.comment || data
    comments.value.push(newComment)
    commentText.value = ''
  } catch (e) {
    alert(e.response?.data?.message || '댓글 등록 실패')
  } finally {
    submitting.value = false
  }
}

async function submitReply(parentId) {
  if (!replyText.value.trim()) return
  try {
    const { data } = await axios.post(getApiBase(), {
      content: replyText.value,
      parent_id: parentId
    })
    const newReply = data.comment || data
    comments.value.push(newReply)
    replyText.value = ''
    replyTo.value = null
  } catch (e) {
    alert(e.response?.data?.message || '답글 등록 실패')
  }
}

async function likeComment(comment) {
  if (!auth.isLoggedIn) return
  try {
    const { data } = await axios.post(`/api/comments/${comment.id}/like`)
    comment.is_liked = data.liked
    comment.like_count = data.like_count ?? (comment.is_liked ? (comment.like_count || 0) + 1 : (comment.like_count || 1) - 1)
  } catch {}
}

async function deleteComment(id) {
  if (!confirm('댓글을 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/comments/${id}`)
    comments.value = comments.value.filter(c => c.id !== id)
  } catch {}
}

function formatRelative(d) {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const diff = (now - date) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  return date.toLocaleDateString('ko-KR')
}

onMounted(loadComments)
</script>
