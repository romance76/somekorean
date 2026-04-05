<template>
  <div class="space-y-6">

    <!-- 핵심 통계 카드 -->
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

    <!-- 오늘 & 알림 요약 -->
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
          <RouterLink to="/admin/content" class="ml-auto text-red-200 hover:text-white text-xs underline">처리하기 →</RouterLink>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">

      <!-- 7일 활동 차트 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 class="font-bold text-gray-800 mb-4 text-sm">📈 최근 7일 활동</h3>
        <div v-if="loadingActivity" class="text-center py-6 text-gray-400 text-sm">불러오는 중...</div>
        <div v-else class="space-y-2">
          <div v-for="day in activity" :key="day.date" class="flex items-center gap-3">
            <span class="text-xs text-gray-500 w-10 flex-shrink-0">{{ day.date }}</span>
            <div class="flex-1 flex items-center gap-2">
              <div class="h-4 bg-blue-400 rounded-sm flex-shrink-0 min-w-[4px] transition-all"
                :style="{ width: Math.max(4, (day.users / maxUsers) * 120) + 'px' }"></div>
              <span class="text-xs text-gray-500">가입 {{ day.users }}</span>
            </div>
            <div class="flex-1 flex items-center gap-2">
              <div class="h-4 bg-green-400 rounded-sm flex-shrink-0 min-w-[4px] transition-all"
                :style="{ width: Math.max(4, (day.posts / maxPosts) * 120) + 'px' }"></div>
              <span class="text-xs text-gray-500">게시 {{ day.posts }}</span>
            </div>
          </div>
        </div>
        <div class="flex gap-4 mt-4 text-xs text-gray-400">
          <span class="flex items-center gap-1"><span class="w-3 h-3 bg-blue-400 rounded-sm inline-block"></span>신규 가입</span>
          <span class="flex items-center gap-1"><span class="w-3 h-3 bg-green-400 rounded-sm inline-block"></span>새 게시글</span>
        </div>
      </div>

      <!-- 빠른 링크 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 class="font-bold text-gray-800 mb-4 text-sm">⚡ 빠른 관리</h3>
        <div class="grid grid-cols-2 gap-3">
          <RouterLink v-for="link in quickLinks" :key="link.to" :to="link.to"
            class="flex items-center gap-3 p-3 rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50 transition group">
            <span class="text-xl">{{ link.icon }}</span>
            <div>
              <div class="text-xs font-semibold text-gray-700 group-hover:text-blue-600">{{ link.label }}</div>
              <div class="text-[10px] text-gray-400">{{ link.count }}</div>
            </div>
          </RouterLink>
        </div>
      </div>

      <!-- 최근 신고 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100">
          <h3 class="font-bold text-gray-800 text-sm">🚨 최근 미처리 신고</h3>
          <RouterLink to="/admin/content" class="text-xs text-blue-600 hover:text-blue-700">전체 보기 →</RouterLink>
        </div>
        <div v-if="reports.length === 0" class="text-center py-8 text-gray-400 text-sm">미처리 신고 없음 ✓</div>
        <div v-else class="divide-y divide-gray-50">
          <div v-for="r in reports.slice(0, 5)" :key="r.id" class="px-5 py-3 flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-red-100 text-red-500 flex items-center justify-center text-sm flex-shrink-0">🚨</div>
            <div class="flex-1 min-w-0">
              <div class="text-xs font-medium text-gray-700 truncate">{{ r.reporter?.name }} → {{ r.reason }}</div>
              <div class="text-[10px] text-gray-400">{{ formatDate(r.created_at) }}</div>
            </div>
            <button @click="dismiss(r)"
              class="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-2.5 py-1 rounded-lg transition flex-shrink-0">
              처리
            </button>
          </div>
        </div>
      </div>

      <!-- 최근 가입 회원 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100">
          <h3 class="font-bold text-gray-800 text-sm">👥 최근 가입 회원</h3>
          <RouterLink to="/admin/members" class="text-xs text-blue-600 hover:text-blue-700">전체 보기 →</RouterLink>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="user in recentUsers" :key="user.id" class="px-5 py-3 flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold flex-shrink-0">
              {{ (user.name || '?')[0] }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs font-medium text-gray-700">{{ user.name }}
                <span class="text-gray-400">@{{ user.username }}</span>
              </div>
              <div class="text-[10px] text-gray-400">{{ user.email }}</div>
            </div>
            <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold flex-shrink-0',
              user.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600']">
              {{ user.status === 'active' ? '활성' : '정지' }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const stats       = ref({})
const activity    = ref([])
const reports     = ref([])
const recentUsers = ref([])
const loadingActivity = ref(true)

const maxUsers = computed(() => Math.max(1, ...activity.value.map(d => d.users)))
const maxPosts = computed(() => Math.max(1, ...activity.value.map(d => d.posts)))

const mainCards = computed(() => [
  { icon: '👥', label: '전체 회원',   value: stats.value.users,      tag: '누적',  tagClass: 'bg-blue-100 text-blue-600' },
  { icon: '📝', label: '게시글',      value: stats.value.posts,      tag: '활성',  tagClass: 'bg-green-100 text-green-600' },
  { icon: '💼', label: '구인구직',    value: stats.value.jobs,       tag: '활성',  tagClass: 'bg-purple-100 text-purple-600' },
  { icon: '🛍️', label: '중고장터',    value: stats.value.market,     tag: '활성',  tagClass: 'bg-yellow-100 text-yellow-700' },
  { icon: '🏪', label: '업소록',      value: stats.value.businesses, tag: '활성',  tagClass: 'bg-pink-100 text-pink-600' },
  { icon: '🚗', label: '라이드',      value: stats.value.rides,      tag: '전체',  tagClass: 'bg-orange-100 text-orange-600' },
  { icon: '👥', label: '동호회',      value: stats.value.clubs,      tag: '전체',  tagClass: 'bg-teal-100 text-teal-600' },
  { icon: '🤝', label: '공동구매',    value: stats.value.group_buys, tag: '진행중', tagClass: 'bg-indigo-100 text-indigo-600' },
  { icon: '💙', label: '노인안심',    value: stats.value.elder_users,tag: '등록',  tagClass: 'bg-cyan-100 text-cyan-600' },
  { icon: '🚫', label: '정지 회원',   value: stats.value.banned_users,tag: '누적', tagClass: 'bg-red-100 text-red-600' },
  { icon: '💬', label: '채팅방',      value: stats.value.chat_rooms, tag: '전체',  tagClass: 'bg-slate-100 text-slate-600' },
  { icon: '🎓', label: '멘토',        value: stats.value.mentors,    tag: '활성',  tagClass: 'bg-lime-100 text-lime-600' },
])

const quickLinks = computed(() => [
  { to: '/admin/members',  icon: '👥', label: '회원 관리',    count: (stats.value.users ?? 0) + '명' },
  { to: '/admin/content',  icon: '🚨', label: '신고 처리',    count: (stats.value.reports ?? 0) + '건 대기' },
  { to: '/admin/elder',    icon: '💙', label: '노인 모니터링', count: (stats.value.elder_users ?? 0) + '명 등록' },
  { to: '/admin/business', icon: '🏪', label: '업소록',       count: (stats.value.businesses ?? 0) + '개' },
  { to: '/admin/rides',    icon: '🚗', label: '라이드',       count: (stats.value.rides ?? 0) + '건' },
  { to: '/admin/chats',    icon: '💬', label: '채팅방',       count: (stats.value.chat_rooms ?? 0) + '개' },
])

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function dismiss(r) {
  await axios.post(`/api/admin/reports/${r.id}/dismiss`)
  reports.value = reports.value.filter(x => x.id !== r.id)
  if (stats.value.reports > 0) stats.value.reports--
}

onMounted(async () => {
  const [statsRes, actRes, repsRes, usersRes] = await Promise.allSettled([
    axios.get('/api/admin/stats'),
    axios.get('/api/admin/activity'),
    axios.get('/api/admin/reports'),
    axios.get('/api/admin/users'),
  ])
  if (statsRes.status === 'fulfilled') stats.value = statsRes.value.data
  if (actRes.status === 'fulfilled')   { activity.value = actRes.value.data; loadingActivity.value = false }
  if (repsRes.status === 'fulfilled')  reports.value = repsRes.value.data?.data ?? []
  if (usersRes.status === 'fulfilled') recentUsers.value = usersRes.value.data?.data?.slice(0, 5) ?? []
})
</script>
