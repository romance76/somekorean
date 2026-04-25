<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-black text-gray-800">🔔 알림</h1>
      <button @click="markAllRead" class="text-xs text-amber-600 font-semibold hover:text-amber-800">전체 읽음</button>
    </div>
    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="!notifs.length" class="text-center py-12 text-gray-400">알림이 없습니다</div>
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div v-for="n in notifs" :key="n.id"
        class="px-4 py-3 border-b last:border-0 transition"
        :class="n.read_at ? 'bg-white' : 'bg-amber-50'">
        <div class="flex items-start gap-3">
          <span class="text-lg flex-shrink-0">{{ typeIcons[n.type] || '📢' }}</span>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-800">{{ n.title }}</div>
            <div v-if="n.content" class="text-xs text-gray-500 mt-0.5">{{ n.content }}</div>
            <div class="text-[10px] text-gray-400 mt-1">{{ formatDate(n.created_at) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const notifs = ref([])
const loading = ref(true)
const typeIcons = { like:'❤️', comment:'💬', friend:'👋', answer:'💡', reservation:'🛒', checkin:'✅', sos:'🚨' }
function formatDate(dt) {
  if (!dt) return ''
  const h = Math.floor((Date.now() - new Date(dt).getTime()) / 3600000)
  if (h < 1) return '방금'
  if (h < 24) return h + '시간 전'
  return Math.floor(h/24) + '일 전'
}
async function markAllRead() {
  try { await axios.post('/api/notifications/read'); notifs.value.forEach(n => n.read_at = new Date()) } catch {}
}
onMounted(async () => {
  try { const { data } = await axios.get('/api/notifications'); notifs.value = data.data?.data || data.data || [] } catch {}
  loading.value = false
})
</script>
