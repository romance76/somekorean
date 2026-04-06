<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <button @click="$router.back()" class="text-sm text-gray-500 hover:text-amber-600 mb-3">← 안심서비스</button>
    <h1 class="text-xl font-black text-gray-800 mb-4">📋 체크인 기록</h1>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="!logs.length" class="text-center py-12 text-gray-400">체크인 기록이 없습니다</div>
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-for="log in logs" :key="log.id" class="px-4 py-3 border-b last:border-0 flex items-center gap-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0"
          :class="log.status === 'ok' ? 'bg-green-100' : log.status === 'sos' ? 'bg-red-100' : 'bg-gray-100'">
          {{ log.status === 'ok' ? '✅' : log.status === 'sos' ? '🚨' : '⏰' }}
        </div>
        <div class="flex-1">
          <div class="text-sm font-semibold" :class="log.status === 'ok' ? 'text-green-700' : log.status === 'sos' ? 'text-red-600' : 'text-gray-500'">
            {{ { ok: '정상 체크인', sos: 'SOS 긴급', missed: '미체크인' }[log.status] }}
          </div>
          <div class="text-xs text-gray-400">{{ formatDate(log.checked_in_at) }}</div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const logs = ref([])
const loading = ref(true)
function formatDate(dt) { return dt ? new Date(dt).toLocaleString('ko-KR') : '' }
onMounted(async () => {
  try { const { data } = await axios.get('/api/elder/checkin-history'); logs.value = data.data?.data || data.data || [] } catch {}
  loading.value = false
})
</script>
