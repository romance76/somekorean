<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[800px] mx-auto px-4 pt-4">

      <!-- 로딩 -->
      <div v-if="loading" class="text-center py-16 text-gray-400">불러오는 중...</div>

      <template v-else-if="post">
        <!-- 뒤로가기 -->
        <button @click="$router.back()" class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition">
          ← 목록으로
        </button>

        <!-- 질문 카드 -->
        <div class="bg-white rounded-2xl shadow-sm p-5 mb-4">
          <div class="flex items-center gap-2 mb-3">
            <span v-if="post.category" class="text-xs px-2.5 py-1 rounded-full bg-violet-50 text-violet-700 font-semibold">
              {{ post.category.icon }} {{ post.category.name }}
            </span>
            <span :class="statusBadgeClass(post.status)" class="text-xs px-2.5 py-1 rounded-full font-semibold">
              {{ statusLabel(post.status) }}
            </span>
          </div>
          <h1 class="text-lg font-bold text-gray-900 mb-3 leading-snug">{{ post.title }}</h1>
          <p class="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap mb-4">{{ post.content }}</p>
          <div class="flex items-center gap-3 text-xs text-gray-400 pt-3 border-t border-gray-100">
            <div class="w-7 h-7 rounded-full bg-violet-100 flex items-center justify-center text-violet-600 font-bold text-sm">
              {{ (post.user?.name || '?').charAt(0) }}
            </div>
            <span class="font-medium text-gray-600">{{ post.user?.name }}</span>
            <span v-if="post.region" class="text-blue-500">📍 {{ post.region }}</span>
            <span>{{ timeAgo(post.created_at) }}</span>
            <span>조회 {{ post.view_count }}</span>
          </div>
        </div>

        <!-- 베스트 답변 -->
        <div v-if="post.best_answer" class="bg-yellow-50 border border-yellow-200 rounded-2xl p-5 mb-4">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-yellow-500 text-lg">⭐</span>
            <span class="text-sm font-bold text-yellow-700">베스트 답변</span>
          </div>
          <p class="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap mb-3">{{ post.best_answer.content }}</p>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <div class="w-6 h-6 rounded-full bg-yellow-200 flex items-center justify-center text-yellow-700 font-bold text-xs">
              {{ (post.best_answer.user?.name || '?').charAt(0) }}
            </div>
            <span>{{ post.best_answer.user?.name }}</span>
            <span>{{ timeAgo(post.best_answer.created_at) }}</span>
          </div>
        </div>

        <!-- 답변 목록 -->
        <div class="mb-4">
          <h2 class="text-sm font-bold text-gray-600 mb-3">답변 {{ post.answers?.length || 0 }}개</h2>
          <div v-for="ans in nonBestAnswers" :key="ans.id"
            class="bg-white rounded-2xl shadow-sm p-4 mb-3">
            <p class="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap mb-3">{{ ans.content }}</p>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-xs text-gray-400">
                <div class="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">
                  {{ (ans.user?.name || '?').charAt(0) }}
                </div>
                <span>{{ ans.user?.name }}</span>
                <span>{{ timeAgo(ans.created_at) }}</span>
              </div>
              <div class="flex items-center gap-2">
                <button @click="likeAnswer(ans)" class="flex items-center gap-1 text-xs text-gray-400 hover:text-blue-500 transition">
                  👍 {{ ans.like_count || 0 }}
                </button>
                <button v-if="isPostOwner && !post.best_answer_id" @click="setBest(ans.id)"
                  class="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition">
                  베스트 선택
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 답변 작성 -->
        <div class="bg-white rounded-2xl shadow-sm p-5">
          <h3 class="text-sm font-bold text-gray-700 mb-3">답변 작성</h3>
          <textarea v-model="newAnswer" rows="4" placeholder="실용적인 답변을 작성해주세요..."
            class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-violet-400 resize-none mb-3" />
          <div class="flex justify-end">
            <button @click="submitAnswer" :disabled="!newAnswer.trim() || submitting"
              class="bg-violet-500 hover:bg-violet-600 disabled:opacity-50 text-white px-5 py-2 rounded-xl text-sm font-semibold transition">
              {{ submitting ? '등록 중...' : '답변 등록' }}
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const post = ref(null)
const loading = ref(true)
const newAnswer = ref('')
const submitting = ref(false)

const isPostOwner = computed(() => auth.user && post.value && auth.user.id === post.value.user_id)
const nonBestAnswers = computed(() => (post.value?.answers || []).filter(a => !a.is_best))

function statusLabel(s) { return { open: '미답변', solved: '해결됨', closed: '마감' }[s] || s }
function statusBadgeClass(s) {
  if (s === 'solved') return 'bg-green-100 text-green-700'
  return 'bg-blue-100 text-blue-700'
}
function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt)) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return Math.floor(diff/60) + '분 전'
  if (diff < 86400) return Math.floor(diff/3600) + '시간 전'
  return Math.floor(diff/86400) + '일 전'
}

async function load() {
  try {
    const { data } = await axios.get('/api/qa/' + route.params.id)
    post.value = data
  } catch { post.value = null }
  finally { loading.value = false }
}

async function submitAnswer() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  if (!newAnswer.value.trim()) return
  submitting.value = true
  try {
    const { data } = await axios.post('/api/qa/' + post.value.id + '/answers', { content: newAnswer.value })
    if (!post.value.answers) post.value.answers = []
    post.value.answers.push(data.answer)
    post.value.answer_count++
    newAnswer.value = ''
  } catch (e) {
    alert(e.response?.data?.message || '등록 실패')
  } finally { submitting.value = false }
}

async function likeAnswer(ans) {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post('/api/qa/answers/' + ans.id + '/like')
    ans.like_count = data.like_count
  } catch {}
}

async function setBest(answerId) {
  try {
    await axios.post('/api/qa/' + post.value.id + '/best-answer', { answer_id: answerId })
    await load()
  } catch {}
}

onMounted(load)
</script>
