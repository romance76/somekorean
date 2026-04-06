<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-4xl mx-auto px-4 py-5">
    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="user">
      <!-- 프로필 헤더 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-4">
        <div class="bg-gradient-to-r from-amber-400 to-orange-400 h-24"></div>
        <div class="px-5 pb-4 -mt-10">
          <div class="w-20 h-20 rounded-full bg-amber-500 text-white flex items-center justify-center text-3xl font-black border-4 border-white shadow">
            {{ (user.name || '?')[0] }}
          </div>
          <h1 class="text-lg font-bold text-gray-900 mt-2">{{ user.name }}</h1>
          <div v-if="user.nickname" class="text-sm text-gray-500">@{{ user.nickname }}</div>
          <div v-if="user.bio" class="text-sm text-gray-600 mt-1">{{ user.bio }}</div>
          <div class="flex items-center gap-4 mt-3 text-xs text-gray-400">
            <span v-if="user.city">📍 {{ user.city }}, {{ user.state }}</span>
            <span>⭐ {{ user.points || 0 }}P</span>
            <span>📅 {{ formatDate(user.created_at) }} 가입</span>
          </div>
        </div>
      </div>

      <!-- 게시글 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-3 border-b font-bold text-sm text-amber-900">📝 작성한 글</div>
        <div v-for="post in posts" :key="post.id">
          <RouterLink :to="`/community/free/${post.id}`" class="block px-5 py-3 border-b hover:bg-amber-50/50 transition">
            <div class="text-sm font-medium text-gray-800">{{ post.title }}</div>
            <div class="text-xs text-gray-400 mt-0.5">{{ post.view_count }}조회 · {{ post.like_count }}좋아요</div>
          </RouterLink>
        </div>
        <div v-if="!posts.length" class="px-5 py-6 text-center text-sm text-gray-400">작성한 글이 없습니다</div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
const route = useRoute()
const user = ref(null)
const posts = ref([])
const loading = ref(true)
function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString('ko-KR') : '' }
onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/users/${route.params.id}`)
    user.value = data.data
    const { data: pData } = await axios.get(`/api/users/${route.params.id}/posts`)
    posts.value = pData.data?.data || pData.data || []
  } catch {}
  loading.value = false
})
</script>
