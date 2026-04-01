<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 배너 -->
    <div class="bg-gradient-to-r from-yellow-400 to-orange-500 text-white">
      <div class="max-w-4xl mx-auto px-4 py-8">
        <h1 class="text-2xl font-bold">&#127942; 해결왕 프로필</h1>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-4 py-6">
      <!-- 프로필 카드 -->
      <div class="bg-white rounded-2xl shadow-sm p-6 mb-6">
        <div class="flex items-center gap-4">
          <div class="w-16 h-16 rounded-full bg-gradient-to-br from-yellow-400 to-orange-400 flex items-center justify-center text-white text-2xl font-black">
            {{ (profile.name || '?').charAt(0) }}
          </div>
          <div class="flex-1">
            <h2 class="text-xl font-bold text-gray-800">{{ profile.name || '사용자' }}</h2>
            <p v-if="profile.title" class="text-sm text-purple-600">{{ profile.title }}</p>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4 mt-6">
          <div class="bg-green-50 rounded-xl p-4 text-center">
            <p class="text-2xl font-black text-green-600">{{ profile.total_accepted || 0 }}</p>
            <p class="text-xs text-gray-500 mt-1">총 채택 수</p>
          </div>
          <div class="bg-yellow-50 rounded-xl p-4 text-center">
            <p class="text-2xl font-black text-yellow-600">{{ (profile.total_points || 0).toLocaleString() }}</p>
            <p class="text-xs text-gray-500 mt-1">총 받은 포인트</p>
          </div>
        </div>
      </div>

      <!-- 채택된 답변 목록 -->
      <h3 class="font-bold text-gray-800 text-lg mb-4">&#9989; 채택된 답변 목록</h3>
      <div v-if="loading" class="text-center py-12 text-gray-400">로딩 중...</div>
      <div v-else-if="resolvedAnswers.length === 0" class="text-center py-12 text-gray-400">
        아직 채택된 답변이 없습니다.
      </div>
      <div v-else class="space-y-3">
        <div v-for="ans in resolvedAnswers" :key="ans.id"
          class="bg-white rounded-xl shadow-sm p-5 hover:shadow-md transition">
          <div class="flex items-center justify-between mb-2">
            <router-link :to="'/qa/' + (ans.question?.category?.slug || 'general') + '/' + ans.question_id"
              class="font-bold text-blue-600 hover:underline text-sm line-clamp-1">
              {{ ans.question?.title || '삭제된 질문' }}
            </router-link>
            <span v-if="ans.points_received > 0"
              class="text-xs font-bold text-yellow-600 bg-yellow-50 px-2 py-1 rounded-full">+{{ ans.points_received }}P</span>
          </div>
          <p class="text-sm text-gray-600 line-clamp-2 mb-2">{{ stripHtml(ans.content) }}</p>
          <div class="text-xs text-gray-400">
            채택일: {{ formatDate(ans.accepted_at || ans.updated_at) }}
          </div>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="pagination.last_page > 1" class="flex justify-center mt-6 gap-1">
        <button v-for="p in pagination.last_page" :key="p"
          @click="fetchResolved(p)"
          class="w-8 h-8 rounded-lg text-sm"
          :class="p === pagination.current_page ? 'bg-yellow-500 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'">
          {{ p }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const userId = ref(route.params.userId)

const profile = ref({})
const resolvedAnswers = ref([])
const loading = ref(true)
const pagination = ref({ current_page: 1, last_page: 1 })

const token = localStorage.getItem('sk_token')
const headers = token ? { Authorization: 'Bearer ' + token } : {}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
}

function stripHtml(html) {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '').substring(0, 200)
}

async function fetchResolved(page) {
  loading.value = true
  try {
    const resp = await axios.get('/api/user/' + userId.value + '/resolved-answers', {
      params: { page: page || 1 },
      headers: headers
    })
    const data = resp.data
    if (data.user) profile.value = data.user
    if (data.profile) profile.value = data.profile
    resolvedAnswers.value = data.data || data.answers || []
    if (data.meta) pagination.value = data.meta
    else if (data.current_page) pagination.value = data
  } catch (e) { console.error(e) }
  loading.value = false
}

onMounted(function() {
  fetchResolved(1)
})
</script>
