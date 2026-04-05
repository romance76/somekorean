<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="max-w-[800px] mx-auto px-4 pt-4">

      <!-- Loading -->
      <div v-if="loading" class="text-center py-16 text-gray-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
        <p class="text-sm">{{ locale === 'ko' ? '불러오는 중...' : 'Loading...' }}</p>
      </div>

      <template v-else-if="post">
        <!-- Back -->
        <button @click="$router.back()" class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 mb-4 transition">
          ← {{ locale === 'ko' ? '목록으로' : 'Back' }}
        </button>

        <!-- Question Card -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5 mb-4">
          <div class="flex items-center gap-2 mb-3">
            <span v-if="post.category" class="text-xs px-2.5 py-1 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-semibold">
              {{ post.category.name || post.category }}
            </span>
            <span :class="statusBadge" class="text-xs px-2.5 py-1 rounded-full font-semibold">
              {{ statusLabel }}
            </span>
            <span v-if="post.point_reward > 0" class="text-xs px-2.5 py-1 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 font-bold">
              🏆 {{ post.point_reward }}P
            </span>
          </div>

          <h1 class="text-lg font-bold text-gray-900 dark:text-white mb-3 leading-snug">{{ post.title }}</h1>
          <p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap mb-4">{{ post.content }}</p>

          <div class="flex items-center gap-3 text-xs text-gray-400 pt-3 border-t border-gray-100 dark:border-gray-700">
            <div class="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold text-sm">
              {{ (post.user?.name || post.user?.nickname || '?')[0] }}
            </div>
            <span class="font-medium text-gray-600 dark:text-gray-300">{{ post.user?.name || post.user?.nickname || (locale === 'ko' ? '익명' : 'Anonymous') }}</span>
            <span>{{ timeAgo(post.created_at) }}</span>
            <span>{{ locale === 'ko' ? '조회' : 'Views' }} {{ post.view_count }}</span>
          </div>
        </div>

        <!-- Best Answer -->
        <div v-if="post.best_answer" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-xl p-5 mb-4">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-yellow-500 text-lg">👑</span>
            <span class="text-sm font-bold text-yellow-700 dark:text-yellow-300">{{ locale === 'ko' ? '베스트 답변' : 'Best Answer' }}</span>
          </div>
          <p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap mb-3">{{ post.best_answer.content }}</p>
          <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <div class="w-6 h-6 rounded-full bg-yellow-200 dark:bg-yellow-700 flex items-center justify-center text-yellow-700 dark:text-yellow-200 font-bold text-xs">
              {{ (post.best_answer.user?.name || '?')[0] }}
            </div>
            <span>{{ post.best_answer.user?.name || (locale === 'ko' ? '익명' : 'Anonymous') }}</span>
            <span>{{ timeAgo(post.best_answer.created_at) }}</span>
            <span>👍 {{ post.best_answer.like_count || 0 }}</span>
          </div>
        </div>

        <!-- All Answers -->
        <div class="mb-4">
          <h2 class="text-sm font-bold text-gray-600 dark:text-gray-300 mb-3">
            {{ locale === 'ko' ? '답변' : 'Answers' }} {{ post.answers?.length || 0 }}{{ locale === 'ko' ? '개' : '' }}
          </h2>
          <div v-for="ans in nonBestAnswers" :key="ans.id"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 mb-3">
            <p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap mb-3">{{ ans.content }}</p>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-xs text-gray-400">
                <div class="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-800 flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold text-xs">
                  {{ (ans.user?.name || '?')[0] }}
                </div>
                <span>{{ ans.user?.name || (locale === 'ko' ? '익명' : 'Anonymous') }}</span>
                <span>{{ timeAgo(ans.created_at) }}</span>
              </div>
              <div class="flex items-center gap-2">
                <button @click="likeAnswer(ans)" class="flex items-center gap-1 text-xs text-gray-400 hover:text-blue-500 transition">
                  👍 {{ ans.like_count || 0 }}
                </button>
                <button v-if="isPostOwner && !post.best_answer_id" @click="setBest(ans.id)"
                  class="text-xs px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-lg hover:bg-yellow-200 dark:hover:bg-yellow-900/50 transition">
                  {{ locale === 'ko' ? '베스트 선택' : 'Accept' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="!post.answers?.length" class="text-center py-10 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700">
            <p class="text-4xl mb-2">💬</p>
            <p class="text-gray-400 text-sm">{{ locale === 'ko' ? '아직 답변이 없습니다. 첫 답변을 남겨보세요!' : 'No answers yet. Be the first!' }}</p>
          </div>
        </div>

        <!-- Write Answer -->
        <div v-if="auth.isLoggedIn" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
          <h3 class="text-sm font-bold text-gray-700 dark:text-gray-200 mb-3">{{ locale === 'ko' ? '답변 작성' : 'Write Answer' }}</h3>
          <textarea v-model="newAnswer" rows="4" :placeholder="locale === 'ko' ? '실용적인 답변을 작성해주세요...' : 'Write a helpful answer...'"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none mb-3" />
          <div class="flex justify-end">
            <button @click="submitAnswer" :disabled="!newAnswer.trim() || submitting"
              class="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2 rounded-xl text-sm font-semibold transition">
              {{ submitting ? (locale === 'ko' ? '등록 중...' : 'Submitting...') : (locale === 'ko' ? '답변 등록' : 'Submit Answer') }}
            </button>
          </div>
        </div>
        <div v-else class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5 text-center">
          <router-link to="/auth/login" class="text-blue-600 text-sm hover:underline">
            {{ locale === 'ko' ? '로그인 후 답변을 작성할 수 있습니다' : 'Login to write an answer' }}
          </router-link>
        </div>
      </template>

      <!-- Not Found -->
      <div v-else-if="!loading" class="text-center py-20">
        <p class="text-4xl mb-3">😞</p>
        <p class="text-gray-400">{{ locale === 'ko' ? '질문을 찾을 수 없습니다' : 'Question not found' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const post = ref(null)
const loading = ref(true)
const newAnswer = ref('')
const submitting = ref(false)

const isPostOwner = computed(() => auth.user?.id === post.value?.user_id)

const nonBestAnswers = computed(() => {
  if (!post.value?.answers) return []
  return post.value.answers.filter(a => a.id !== post.value.best_answer_id)
})

const statusLabel = computed(() => {
  if (!post.value) return ''
  if (post.value.status === 'solved') return locale.value === 'ko' ? '해결됨' : 'Solved'
  return locale.value === 'ko' ? '미해결' : 'Unsolved'
})

const statusBadge = computed(() => {
  if (post.value?.status === 'solved') return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
  return 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
})

function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt).getTime()) / 1000
  if (diff < 60) return locale.value === 'ko' ? '방금 전' : 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}${locale.value === 'ko' ? '분 전' : 'm ago'}`
  if (diff < 86400) return `${Math.floor(diff / 3600)}${locale.value === 'ko' ? '시간 전' : 'h ago'}`
  return new Date(dt).toLocaleDateString('ko-KR')
}

async function likeAnswer(ans) {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/qa/answers/${ans.id}/like`)
    ans.like_count = data.like_count
  } catch { /* empty */ }
}

async function setBest(answerId) {
  if (!confirm(locale.value === 'ko' ? '이 답변을 베스트로 선택하시겠습니까?' : 'Accept this answer as best?')) return
  try {
    await axios.post(`/api/qa/${post.value.id}/accept`, { answer_id: answerId })
    await loadPost()
  } catch (e) {
    alert(e.response?.data?.message || (locale.value === 'ko' ? '베스트 선택 실패' : 'Failed'))
  }
}

async function submitAnswer() {
  if (!newAnswer.value.trim()) return
  submitting.value = true
  try {
    await axios.post(`/api/qa/${post.value.id}/answers`, { content: newAnswer.value })
    newAnswer.value = ''
    await loadPost()
  } catch (e) {
    alert(e.response?.data?.message || (locale.value === 'ko' ? '답변 등록 실패' : 'Failed to submit'))
  }
  submitting.value = false
}

watch(() => route.params.id, () => { if (route.params.id) loadPost() })

async function loadPost() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/qa/${route.params.id}`)
    post.value = data.data || data
  } catch { post.value = null }
  loading.value = false
}

onMounted(loadPost)
</script>
