<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
    <!-- Header -->
    <div class="px-5 py-3 border-b border-gray-100 dark:border-gray-700">
      <h3 class="font-semibold text-gray-800 dark:text-white text-sm">
        {{ $t('common.comment') }} {{ comments.length }}\uAC1C
      </h3>
    </div>

    <!-- Comment list -->
    <ul v-if="comments.length">
      <li v-for="comment in topLevelComments" :key="comment.id" class="border-b border-gray-50 dark:border-gray-700 last:border-0">
        <!-- Comment body -->
        <div class="px-5 py-3.5">
          <div class="flex items-start justify-between">
            <div class="flex items-start gap-2 flex-1">
              <!-- Avatar -->
              <div class="w-7 h-7 bg-gray-100 dark:bg-gray-600 rounded-full flex items-center justify-center text-gray-500 dark:text-gray-300 text-xs font-bold flex-shrink-0 mt-0.5 overflow-hidden">
                <img v-if="comment.user?.avatar" :src="comment.user.avatar" class="w-full h-full object-cover"
                  @error="e => e.target.style.display='none'" />
                <span v-if="!comment.user?.avatar">{{ (comment.user?.name || comment.user_name || '\uC775\uBA85')[0] }}</span>
              </div>
              <div class="flex-1">
                <!-- Meta -->
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-sm font-medium text-gray-800 dark:text-white">{{ comment.user?.name || comment.user_name || '\uC775\uBA85' }}</span>
                  <span class="text-xs text-gray-400">{{ formatRelative(comment.created_at) }}</span>
                  <span v-if="comment.is_accepted" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">\uCC44\uD0DD\uB428</span>
                </div>

                <!-- Content -->
                <p v-if="editingId !== comment.id" class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">{{ comment.content }}</p>

                <!-- Edit mode -->
                <div v-else class="flex gap-2">
                  <input v-model="editText" @keyup.enter="saveEdit(comment.id)" type="text"
                    class="flex-1 border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                  <button @click="saveEdit(comment.id)" class="text-xs text-blue-600 font-medium">\uC800\uC7A5</button>
                  <button @click="editingId = null" class="text-xs text-gray-400">\uCDE8\uC18C</button>
                </div>

                <!-- Action buttons -->
                <div class="flex items-center gap-3 mt-2">
                  <!-- Like -->
                  <button @click="likeComment(comment)" class="flex items-center gap-1 text-xs transition"
                    :class="comment.is_liked ? 'text-red-500' : 'text-gray-400 hover:text-red-500'">
                    <svg class="w-3.5 h-3.5" :fill="comment.is_liked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                    </svg>
                    <span>{{ comment.like_count || 0 }}</span>
                  </button>

                  <!-- Reply -->
                  <button v-if="auth.isLoggedIn" @click="replyTo = replyTo === comment.id ? null : comment.id"
                    class="text-xs text-gray-400 hover:text-blue-500 transition">
                    {{ $t('common.reply') }}
                  </button>

                  <!-- Report -->
                  <button @click="reportComment(comment.id)"
                    class="text-xs text-gray-300 hover:text-red-400 transition">
                    {{ $t('common.report') }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Edit / Delete for own comments -->
            <div v-if="canModify(comment)" class="flex items-center gap-2 ml-2">
              <button @click="startEdit(comment)" class="text-xs text-gray-300 hover:text-blue-400">\uC218\uC815</button>
              <button @click="deleteComment(comment.id)" class="text-xs text-gray-300 hover:text-red-400">\uC0AD\uC81C</button>
            </div>
          </div>

          <!-- Reply input -->
          <div v-if="replyTo === comment.id" class="ml-9 mt-3">
            <div class="flex gap-2">
              <input v-model="replyText" @keyup.enter="submitReply(comment.id)" type="text"
                :placeholder="`${comment.user?.name || ''}\uB2D8\uC5D0\uAC8C \uB2F5\uAE00...`"
                class="flex-1 border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              <button @click="submitReply(comment.id)" :disabled="!replyText.trim()"
                class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-blue-700 disabled:opacity-40 whitespace-nowrap">
                \uB4F1\uB85D
              </button>
            </div>
          </div>
        </div>

        <!-- Replies (1 level deep) -->
        <div v-if="getReplies(comment.id).length" class="bg-gray-50/50 dark:bg-gray-700/30">
          <div v-for="reply in getReplies(comment.id)" :key="reply.id" class="px-5 py-3 ml-9 border-t border-gray-100 dark:border-gray-600">
            <div class="flex items-start justify-between">
              <div class="flex items-start gap-2 flex-1">
                <div class="w-6 h-6 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center text-gray-500 dark:text-gray-300 text-[10px] font-bold flex-shrink-0 mt-0.5">
                  {{ (reply.user?.name || reply.user_name || '\uC775\uBA85')[0] }}
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-0.5">
                    <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ reply.user?.name || reply.user_name || '\uC775\uBA85' }}</span>
                    <span class="text-xs text-gray-400">{{ formatRelative(reply.created_at) }}</span>
                  </div>
                  <p class="text-sm text-gray-600 dark:text-gray-400">{{ reply.content }}</p>
                </div>
              </div>
              <button v-if="canModify(reply)"
                @click="deleteComment(reply.id)" class="text-xs text-gray-300 hover:text-red-400 ml-2">\uC0AD\uC81C</button>
            </div>
          </div>
        </div>
      </li>
    </ul>

    <!-- Empty state -->
    <div v-else class="px-5 py-8 text-center text-sm text-gray-400">
      \uC544\uC9C1 \uB313\uAE00\uC774 \uC5C6\uC2B5\uB2C8\uB2E4. \uCCAB \uB313\uAE00\uC744 \uB0A8\uACA8\uBCF4\uC138\uC694!
    </div>

    <!-- Comment input -->
    <div v-if="auth.isLoggedIn" class="px-5 py-3 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-100 dark:border-gray-600">
      <div class="flex gap-2">
        <input v-model="commentText" @keyup.enter.ctrl="submitComment" type="text"
          :placeholder="'\uB313\uAE00\uC744 \uC785\uB825\uD558\uC138\uC694 (Ctrl+Enter)'"
          class="flex-1 border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <button @click="submitComment" :disabled="!commentText.trim() || submitting"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-40 whitespace-nowrap">
          {{ submitting ? '...' : '\uB4F1\uB85D' }}
        </button>
      </div>
    </div>
    <div v-else class="px-5 py-3 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-100 dark:border-gray-600 text-center">
      <RouterLink to="/login" class="text-blue-600 text-sm hover:underline">
        \uB85C\uADF8\uC778 \uD6C4 \uB313\uAE00\uC744 \uC791\uC131\uD560 \uC218 \uC788\uC2B5\uB2C8\uB2E4
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLangStore } from '../stores/lang'
import axios from 'axios'

const props = defineProps({
  commentableType: { type: String, required: true },
  commentableId: { type: [Number, String], required: true },
})

const auth = useAuthStore()
const langStore = useLangStore()

const comments = ref([])
const commentText = ref('')
const replyTo = ref(null)
const replyText = ref('')
const editingId = ref(null)
const editText = ref('')
const submitting = ref(false)

function $t(key) { return langStore.$t(key) }

// Top-level comments only
const topLevelComments = computed(() =>
  comments.value.filter(c => !c.parent_id)
)

// Get replies for a parent comment
function getReplies(parentId) {
  return comments.value.filter(c => c.parent_id === parentId)
}

// Check if current user can modify a comment
function canModify(comment) {
  if (!auth.user) return false
  return auth.user.id === comment.user_id || auth.user.id === comment.user?.id || auth.user.is_admin
}

// API endpoint based on commentable type
function getApiBase() {
  const type = props.commentableType
  const id = props.commentableId
  const typeMap = {
    post: `/api/posts/${id}/comments`,
    event: `/api/events/${id}/comments`,
    market: `/api/market/${id}/comments`,
    job: `/api/jobs/${id}/comments`,
    news: `/api/news/${id}/comments`,
    recipe: `/api/recipes/${id}/comments`,
    realestate: `/api/realestate/${id}/comments`,
    qa_question: `/api/posts/${id}/comments`,
  }
  return typeMap[type] || `/api/posts/${id}/comments`
}

async function loadComments() {
  try {
    const { data } = await axios.get(getApiBase())
    comments.value = data.comments || data.data || data || []
  } catch {
    comments.value = []
  }
}

async function submitComment() {
  if (!commentText.value.trim() || submitting.value) return
  submitting.value = true
  try {
    const { data } = await axios.post(getApiBase(), { content: commentText.value })
    comments.value.push(data.comment || data)
    commentText.value = ''
  } catch (e) {
    alert(e.response?.data?.message || '\uB313\uAE00 \uB4F1\uB85D \uC2E4\uD328')
  } finally {
    submitting.value = false
  }
}

async function submitReply(parentId) {
  if (!replyText.value.trim()) return
  try {
    const { data } = await axios.post(getApiBase(), {
      content: replyText.value,
      parent_id: parentId,
    })
    comments.value.push(data.comment || data)
    replyText.value = ''
    replyTo.value = null
  } catch (e) {
    alert(e.response?.data?.message || '\uB2F5\uAE00 \uB4F1\uB85D \uC2E4\uD328')
  }
}

function startEdit(comment) {
  editingId.value = comment.id
  editText.value = comment.content
}

async function saveEdit(commentId) {
  if (!editText.value.trim()) return
  try {
    await axios.put(`/api/comments/${commentId}`, { content: editText.value })
    const c = comments.value.find(c => c.id === commentId)
    if (c) c.content = editText.value
    editingId.value = null
  } catch {
    alert('\uC218\uC815 \uC2E4\uD328')
  }
}

async function deleteComment(id) {
  if (!confirm('\uB313\uAE00\uC744 \uC0AD\uC81C\uD558\uC2DC\uACA0\uC2B5\uB2C8\uAE4C?')) return
  try {
    await axios.delete(`/api/comments/${id}`)
    comments.value = comments.value.filter(c => c.id !== id)
  } catch { /* ignore */ }
}

async function likeComment(comment) {
  if (!auth.isLoggedIn) return
  try {
    const { data } = await axios.post(`/api/comments/${comment.id}/like`)
    comment.is_liked = data.liked
    comment.like_count = data.like_count ?? (comment.is_liked ? (comment.like_count || 0) + 1 : Math.max(0, (comment.like_count || 1) - 1))
  } catch { /* ignore */ }
}

async function reportComment(commentId) {
  if (!auth.isLoggedIn) return
  if (!confirm('\uC774 \uB313\uAE00\uC744 \uC2E0\uACE0\uD558\uC2DC\uACA0\uC2B5\uB2C8\uAE4C?')) return
  try {
    await axios.post(`/api/comments/${commentId}/report`)
    alert('\uC2E0\uACE0\uAC00 \uC811\uC218\uB418\uC5C8\uC2B5\uB2C8\uB2E4')
  } catch { /* ignore */ }
}

function formatRelative(d) {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const diff = (now - date) / 1000
  if (diff < 60) return '\uBC29\uAE08 \uC804'
  if (diff < 3600) return `${Math.floor(diff / 60)}\uBD84 \uC804`
  if (diff < 86400) return `${Math.floor(diff / 3600)}\uC2DC\uAC04 \uC804`
  if (diff < 604800) return `${Math.floor(diff / 86400)}\uC77C \uC804`
  return date.toLocaleDateString('ko-KR')
}

onMounted(loadComments)
</script>
