<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <button @click="$router.back()" class="text-sm text-gray-500 hover:text-amber-600 mb-3">← 안심서비스</button>
    <h1 class="text-xl font-black text-gray-800 mb-4">👨‍👩‍👧 보호자 대시보드</h1>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="!wards.length" class="text-center py-12">
      <div class="text-4xl mb-3">👨‍👩‍👧</div>
      <div class="text-gray-500 font-semibold">등록된 피보호자가 없습니다</div>
      <div class="text-xs text-gray-400 mt-1">피보호자가 보호자로 등록하면 여기에 표시됩니다</div>
    </div>
    <div v-else class="space-y-3">
      <div v-for="ward in wards" :key="ward.id" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-xl">👤</div>
          <div class="flex-1">
            <div class="text-sm font-bold text-gray-800">{{ ward.user?.name || '피보호자' }}</div>
            <div class="text-xs text-gray-400">체크인 간격: {{ ward.checkin_interval }}시간</div>
          </div>
          <div class="text-2xl">{{ ward.status === 'ok' ? '✅' : ward.status === 'sos' ? '🚨' : '⏰' }}</div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const wards = ref([])
const loading = ref(true)
onMounted(async () => {
  try { const { data } = await axios.get('/api/elder/guardian/wards'); wards.value = data.data || [] } catch {}
  loading.value = false
})
</script>
