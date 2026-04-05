<template>
  <div class="space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="stat in statCards" :key="stat.label"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 text-center">
        <p class="text-3xl font-black" :class="stat.color">{{ (stat.value ?? 0).toLocaleString() }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ stat.label }}</p>
      </div>
    </div>

    <!-- Board Stats -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 mb-4 text-sm">게시판별 통계</h3>
      <div v-if="!boardStats.length" class="text-center py-6 text-gray-400 text-sm">데이터 없음</div>
      <div v-else class="space-y-2">
        <div v-for="b in boardStats" :key="b.id" class="flex items-center gap-3">
          <span class="text-sm text-gray-700 w-24 flex-shrink-0 truncate">{{ b.name }}</span>
          <div class="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
            <div class="h-full bg-red-500 rounded-full transition-all"
              :style="{ width: Math.max(2, (b.count / maxCount) * 100) + '%' }"></div>
          </div>
          <span class="text-xs text-gray-500 w-12 text-right flex-shrink-0">{{ b.count }}건</span>
        </div>
      </div>
    </div>

    <!-- Recent Posts -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 mb-4 text-sm">최근 게시글</h3>
      <div v-if="!recentPosts.length" class="text-center py-6 text-gray-400 text-sm">게시글 없음</div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="p in recentPosts" :key="p.id" class="py-2.5 flex items-center gap-3">
          <span class="text-xs text-gray-400 w-16 flex-shrink-0">{{ p.board?.name || '일반' }}</span>
          <span class="text-sm text-gray-800 flex-1 truncate">{{ p.title }}</span>
          <span class="text-xs text-gray-400 flex-shrink-0">{{ p.user?.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({})
const boardStats = ref([])
const recentPosts = ref([])

const maxCount = computed(() => Math.max(1, ...boardStats.value.map(b => b.count || 0)))

const statCards = computed(() => [
  { label: '총 회원', value: stats.value.total_users, color: 'text-blue-600' },
  { label: '오늘 게시글', value: stats.value.posts_today, color: 'text-green-600' },
  { label: '오늘 가입', value: stats.value.signups_today, color: 'text-purple-600' },
  { label: '활성 유저 (7일)', value: stats.value.active_users, color: 'text-red-600' },
])

async function loadData() {
  try {
    const { data } = await axios.get('/api/admin/dashboard')
    stats.value = data.stats || data
    boardStats.value = data.board_stats || []
    recentPosts.value = (data.recent_posts || []).slice(0, 10)
  } catch { /* ignore */ }
}

onMounted(loadData)
</script>
