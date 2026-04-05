<template>
  <div class="min-h-screen bg-gray-50 pb-24">
    <!-- Header Banner -->
    <div class="max-w-4xl mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-red-600 to-red-500 text-white px-6 py-6 rounded-2xl relative overflow-hidden">
        <div class="flex items-center gap-4">
          <!-- Avatar -->
          <div class="relative flex-shrink-0">
            <div class="w-20 h-20 rounded-full bg-white/20 border-4 border-white/50 overflow-hidden flex items-center justify-center text-3xl font-black text-white shadow-lg">
              <img v-if="auth.user?.avatar" :src="auth.user.avatar" class="w-full h-full object-cover"
                @error="e => e.target.style.display='none'" />
              <span v-else>{{ (auth.user?.name || '?')[0]?.toUpperCase() }}</span>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <h1 class="text-white font-black text-xl truncate">{{ auth.user?.name }}</h1>
            <p class="text-red-200 text-sm">@{{ auth.user?.username }}</p>
            <div class="flex items-center gap-2 mt-1">
              <span class="bg-white/20 text-white text-xs px-2 py-0.5 rounded-full font-medium">{{ auth.user?.level || 'Lv.1' }}</span>
              <span class="text-yellow-300 text-xs font-bold">{{ (auth.user?.points ?? 0).toLocaleString() }}P</span>
            </div>
          </div>
          <router-link to="/profile/edit" class="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-xl text-sm font-bold transition flex-shrink-0">
            {{ $t('profile.edit') }}
          </router-link>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="max-w-4xl mx-auto px-4 mt-4">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-black text-red-600">{{ (auth.user?.points ?? 0).toLocaleString() }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ $t('points.points') }}</div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-black text-blue-600">{{ (auth.user?.cash ?? 0).toLocaleString() }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ $t('points.game_money') }}</div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-black text-green-600">{{ stats.posts || 0 }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ $t('profile.posts') }}</div>
        </div>
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 text-center">
          <div class="text-2xl font-black text-purple-600">{{ stats.comments || 0 }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ $t('profile.comments') }}</div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="max-w-4xl mx-auto px-4 mt-4">
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="font-bold text-gray-800 text-sm">{{ $t('dashboard.recent_activity') }}</h2>
        </div>
        <div v-if="!activities.length" class="text-center py-10 text-gray-400 text-sm">{{ $t('dashboard.no_activity') }}</div>
        <div v-else>
          <div v-for="a in activities" :key="a.id" class="px-5 py-3 border-b border-gray-50 last:border-0 flex items-center gap-3">
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-sm flex-shrink-0"
              :class="activityBg(a.type)">
              {{ activityIcon(a.type) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-800 line-clamp-1">{{ a.description }}</p>
              <p class="text-xs text-gray-400">{{ timeAgo(a.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Links -->
    <div class="max-w-4xl mx-auto px-4 mt-4">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <router-link v-for="link in quickLinks" :key="link.to" :to="link.to"
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 text-center hover:shadow-md transition group">
          <div class="text-2xl mb-2">{{ link.icon }}</div>
          <div class="text-sm font-semibold text-gray-700 group-hover:text-red-600 transition">{{ link.label }}</div>
          <div v-if="link.count !== undefined" class="text-xs text-gray-400 mt-0.5">{{ link.count }}{{ $t('common.count_suffix') }}</div>
        </router-link>
      </div>
    </div>

    <!-- My Posts -->
    <div class="max-w-4xl mx-auto px-4 mt-4">
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="font-bold text-gray-800 text-sm">{{ $t('dashboard.my_posts') }}</h2>
          <router-link :to="`/profile/${auth.user?.username}`" class="text-xs text-red-600 font-semibold hover:underline">
            {{ $t('common.view_all') }}
          </router-link>
        </div>
        <div v-if="!myPosts.length" class="text-center py-10 text-gray-400 text-sm">{{ $t('profile.no_posts') }}</div>
        <div v-else>
          <div v-for="post in myPosts" :key="post.id" class="px-5 py-3 border-b border-gray-50 last:border-0">
            <router-link :to="`/community/${post.board?.slug || 'general'}/${post.id}`"
              class="flex items-center justify-between hover:text-red-600 transition">
              <span class="text-sm text-gray-800 line-clamp-1 flex-1">{{ post.title }}</span>
              <span class="text-xs text-gray-400 ml-3 flex-shrink-0">{{ formatDate(post.created_at) }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const auth = useAuthStore()
const { $t } = useLangStore()

const stats = ref({ posts: 0, comments: 0, bookmarks: 0 })
const activities = ref([])
const myPosts = ref([])

const quickLinks = [
  { to: '/points', icon: '💰', label: $t('nav.points'), count: undefined },
  { to: '/friends', icon: '👫', label: $t('nav.friends'), count: undefined },
  { to: '/messages', icon: '💬', label: $t('nav.messages'), count: undefined },
  { to: '/notifications', icon: '🔔', label: $t('nav.notifications'), count: undefined },
]

function activityIcon(type) {
  const map = { post: '📝', comment: '💬', like: '❤️', point: '💰', friend: '👫', checkin: '✅' }
  return map[type] || '📋'
}

function activityBg(type) {
  const map = {
    post: 'bg-blue-100',
    comment: 'bg-green-100',
    like: 'bg-red-100',
    point: 'bg-yellow-100',
    friend: 'bg-purple-100',
    checkin: 'bg-teal-100',
  }
  return map[type] || 'bg-gray-100'
}

function timeAgo(d) {
  if (!d) return ''
  const diff = Date.now() - new Date(d).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return $t('time.just_now')
  if (m < 60) return `${m}${$t('time.minutes_ago')}`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}${$t('time.hours_ago')}`
  const days = Math.floor(h / 24)
  return `${days}${$t('time.days_ago')}`
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR')
}

async function loadDashboard() {
  try {
    const [statsRes, activityRes, postsRes] = await Promise.all([
      axios.get('/api/profile/me/stats').catch(() => ({ data: {} })),
      axios.get('/api/profile/me/activity').catch(() => ({ data: { data: [] } })),
      axios.get('/api/profile/me/posts').catch(() => ({ data: { data: [] } })),
    ])
    stats.value = statsRes.data || {}
    activities.value = (activityRes.data.data || activityRes.data || []).slice(0, 10)
    myPosts.value = (postsRes.data.data || []).slice(0, 5)
  } catch { /* ignore */ }
}

onMounted(loadDashboard)
</script>
