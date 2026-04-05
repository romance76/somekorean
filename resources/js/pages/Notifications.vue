<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="max-w-3xl mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-6 rounded-2xl">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-black">{{ $t('notifications.title') }}</h1>
            <p class="text-blue-200 text-sm mt-0.5">{{ $t('notifications.subtitle') }}</p>
          </div>
          <button v-if="unread > 0" @click="markAll"
            class="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-xl text-sm font-bold transition">
            {{ $t('notifications.mark_all_read') }}
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 py-4 space-y-2">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-16 text-gray-400">
        <svg class="w-8 h-8 animate-spin mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        {{ $t('common.loading') }}
      </div>

      <!-- Empty -->
      <div v-else-if="!notifications.length" class="text-center py-16">
        <svg class="w-16 h-16 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
        </svg>
        <p class="text-gray-400">{{ $t('notifications.empty') }}</p>
      </div>

      <!-- Notification List -->
      <div v-else>
        <div v-for="n in notifications" :key="n.id" @click="openNotification(n)"
          class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex gap-3 cursor-pointer hover:shadow-md transition mb-2"
          :class="!n.read_at ? 'border-l-4 border-l-blue-500' : ''">
          <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 text-lg"
            :class="iconBg(n.type)">
            {{ typeIcon(n.type) }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm" :class="!n.read_at ? 'font-bold text-gray-900' : 'font-medium text-gray-700'">{{ n.title }}</p>
            <p class="text-xs text-gray-500 mt-0.5 line-clamp-2">{{ n.body }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ timeAgo(n.created_at) }}</p>
          </div>
          <div v-if="!n.read_at" class="w-2.5 h-2.5 bg-blue-500 rounded-full mt-1 flex-shrink-0"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLangStore } from '../stores/lang'
import axios from 'axios'

const router = useRouter()
const { $t } = useLangStore()
const notifications = ref([])
const loading = ref(true)
const unread = computed(() => notifications.value.filter(n => !n.read_at).length)

const typeIconMap = {
  like: '👍', post_liked: '👍', comment: '💬', friend_request: '👋',
  friend_accepted: '🤝', qa_answer: '❓', message: '📩',
  reservation: '📦', point: '💰', system: '📢', checkin: '✅',
}

const iconBgMap = {
  like: 'bg-red-100', post_liked: 'bg-red-100', comment: 'bg-blue-100',
  friend_request: 'bg-yellow-100', friend_accepted: 'bg-green-100',
  qa_answer: 'bg-purple-100', message: 'bg-indigo-100',
  reservation: 'bg-orange-100', point: 'bg-yellow-100',
  system: 'bg-gray-100', checkin: 'bg-teal-100',
}

function typeIcon(type) { return typeIconMap[type] || '🔔' }
function iconBg(type) { return iconBgMap[type] || 'bg-gray-100' }

function timeAgo(d) {
  if (!d) return ''
  const diff = Date.now() - new Date(d).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return $t('time.just_now')
  if (m < 60) return `${m}분 전`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}시간 전`
  const days = Math.floor(h / 24)
  if (days < 7) return `${days}일 전`
  return new Date(d).toLocaleDateString('ko-KR')
}

async function loadNotifications() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/notifications')
    notifications.value = data.data || data || []
  } catch { /* ignore */ }
  loading.value = false
}

async function markAll() {
  try {
    await axios.post('/api/notifications/read-all')
    notifications.value.forEach(n => (n.read_at = new Date().toISOString()))
  } catch { /* ignore */ }
}

async function openNotification(n) {
  // Mark as read
  if (!n.read_at) {
    try {
      await axios.post(`/api/notifications/${n.id}/read`)
      n.read_at = new Date().toISOString()
    } catch { /* ignore */ }
  }
  // Navigate to relevant page
  if (n.url || n.link) {
    router.push(n.url || n.link)
  }
}

onMounted(loadNotifications)
</script>
