<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-5">📊 관리자 대시보드</h1>

  <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
  <div v-else>
    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-2xl font-black text-amber-600">{{ stats.total_users?.toLocaleString() || 0 }}</div>
        <div class="text-xs text-gray-500 mt-1">전체 회원</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-2xl font-black text-blue-600">{{ stats.total_posts?.toLocaleString() || 0 }}</div>
        <div class="text-xs text-gray-500 mt-1">전체 게시글</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-2xl font-black text-green-600">{{ stats.posts_today || 0 }}</div>
        <div class="text-xs text-gray-500 mt-1">오늘 게시글</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-2xl font-black text-purple-600">{{ stats.new_users_week || 0 }}</div>
        <div class="text-xs text-gray-500 mt-1">이번 주 신규 가입</div>
      </div>
    </div>

    <!-- 신고 -->
    <div class="bg-white rounded-xl shadow-sm border p-4">
      <div class="font-bold text-sm text-gray-800 mb-2">⚠️ 대기 중인 신고: {{ stats.pending_reports || 0 }}건</div>
      <RouterLink to="/admin/security" class="text-amber-600 text-xs font-semibold hover:underline">신고 관리 →</RouterLink>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const stats = ref({})
const loading = ref(true)
onMounted(async () => {
  try { const { data } = await axios.get('/api/admin/overview'); stats.value = data.data || {} } catch {}
  loading.value = false
})
</script>
