<template>
  <div class="space-y-6">
    <!-- Stats Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
      <div v-for="card in mainCards" :key="card.label"
        class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div class="flex items-center justify-between mb-2">
          <span class="text-lg">{{ card.icon }}</span>
          <span class="text-[10px] font-bold px-1.5 py-0.5 rounded-full" :class="card.tagClass">{{ card.tag }}</span>
        </div>
        <div class="text-2xl font-black text-gray-800">{{ (card.value ?? 0).toLocaleString() }}</div>
        <div class="text-xs text-gray-500 mt-0.5">{{ card.label }}</div>
      </div>
    </div>

    <!-- Today Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-5">
        <div class="text-blue-200 text-xs font-semibold mb-1">오늘 신규 가입</div>
        <div class="text-4xl font-black">{{ stats.new_users_today ?? 0 }}</div>
        <div class="text-blue-200 text-sm mt-1">명</div>
      </div>
      <div class="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-5">
        <div class="text-green-200 text-xs font-semibold mb-1">오늘 새 게시글</div>
        <div class="text-4xl font-black">{{ stats.new_posts_today ?? 0 }}</div>
        <div class="text-green-200 text-sm mt-1">건</div>
      </div>
      <div class="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-xl p-5">
        <div class="text-red-200 text-xs font-semibold mb-1">미처리 신고</div>
        <div class="text-4xl font-black">{{ stats.reports ?? 0 }}</div>
        <div class="text-red-200 text-sm mt-1 flex items-center gap-1">
          건
          <router-link to="/admin/content" class="ml-auto text-red-200 hover:text-white text-xs underline">처리하기</router-link>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <!-- 7-day Activity Chart -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 class="font-bold text-gray-800 mb-4 text-sm">최근 7일 활동</h3>
        <div v-if="!activity.length" class="text-center py-6 text-gray-400 text-sm">데이터 없음</div>
        <div v-else class="space-y-2">
          <div v-for="day in activity" :key="day.date" class="flex items-center gap-3">
            <span class="text-xs text-gray-500 w-12 flex-shrink-0">{{ day.date }}</span>
            <div class="flex-1 flex items-center gap-2">
              <div class="h-5 bg-blue-400 rounded-sm min-w-[4px] transition-all"
                :style="{ width: Math.max(4, (day.users / maxUsers) * 100) + 'px' }"></div>
              <span class="text-xs text-gray-500">{{ day.users }}명 / {{ day.posts }}글</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Reports -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 class="font-bold text-gray-800 mb-4 text-sm">최근 신고</h3>
        <div v-if="!recentReports.length" class="text-center py-6 text-gray-400 text-sm">신고 없음</div>
        <div v-else class="space-y-2">
          <div v-for="r in recentReports" :key="r.id" class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50">
            <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-sm flex-shrink-0">🚨</div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-800 truncate">{{ r.reason || r.type }}</p>
              <p class="text-xs text-gray-400">{{ r.reporter?.name }} · {{ formatDate(r.created_at) }}</p>
            </div>
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full"
              :class="r.status === 'pending' ? 'bg-yellow-50 text-yellow-600' : 'bg-green-50 text-green-600'">
              {{ r.status === 'pending' ? '대기' : '처리됨' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity Log -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 mb-4 text-sm">최근 활동 로그</h3>
      <div v-if="!recentActivity.length" class="text-center py-6 text-gray-400 text-sm">활동 없음</div>
      <div v-else class="space-y-2">
        <div v-for="a in recentActivity" :key="a.id" class="flex items-center gap-3 py-2 border-b border-gray-50 last:border-0">
          <span class="text-lg">{{ activityIcon(a.type) }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-gray-800">{{ a.description }}</p>
            <p class="text-xs text-gray-400">{{ a.user?.name }} · {{ formatDate(a.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({})
const activity = ref([])
const recentReports = ref([])
const recentActivity = ref([])

const maxUsers = computed(() => Math.max(1, ...activity.value.map(d => d.users || 0)))

const mainCards = computed(() => [
  { icon: '👤', label: '총 회원', value: stats.value.total_users, tag: '전체', tagClass: 'bg-blue-50 text-blue-600' },
  { icon: '📝', label: '총 게시글', value: stats.value.total_posts, tag: '누적', tagClass: 'bg-green-50 text-green-600' },
  { icon: '🏪', label: '업소록', value: stats.value.businesses, tag: '등록', tagClass: 'bg-purple-50 text-purple-600' },
  { icon: '🎉', label: '이벤트', value: stats.value.events, tag: '진행중', tagClass: 'bg-pink-50 text-pink-600' },
  { icon: '📱', label: '숏츠', value: stats.value.shorts, tag: '전체', tagClass: 'bg-orange-50 text-orange-600' },
  { icon: '💬', label: '댓글', value: stats.value.total_comments, tag: '누적', tagClass: 'bg-cyan-50 text-cyan-600' },
])

function activityIcon(type) {
  const map = { user: '👤', post: '📝', comment: '💬', report: '🚨', login: '🔑' }
  return map[type] || '📋'
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function loadData() {
  try {
    const { data } = await axios.get('/api/admin/overview')
    stats.value = data.stats || data
    activity.value = data.activity || []
    recentReports.value = (data.reports || []).slice(0, 5)
    recentActivity.value = (data.recent_activity || []).slice(0, 10)
  } catch { /* ignore */ }
}

onMounted(loadData)
</script>
