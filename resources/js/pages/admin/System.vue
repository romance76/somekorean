<template>
  <div class="space-y-5">
    <h2 class="text-lg font-bold text-gray-800">시스템</h2>

    <!-- Server Info -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="text-xs text-gray-400 mb-2">PHP 버전</div>
        <div class="text-lg font-black text-gray-800">{{ info.php_version || '-' }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="text-xs text-gray-400 mb-2">Laravel 버전</div>
        <div class="text-lg font-black text-gray-800">{{ info.laravel_version || '-' }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="text-xs text-gray-400 mb-2">서버 시간</div>
        <div class="text-lg font-black text-gray-800">{{ info.server_time || '-' }}</div>
      </div>
    </div>

    <!-- Cache Actions -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">캐시 관리</h3>
      <div class="flex flex-wrap gap-3">
        <button @click="clearCache('config')" :disabled="clearing"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 disabled:opacity-50 transition">
          설정 캐시 초기화
        </button>
        <button @click="clearCache('route')" :disabled="clearing"
          class="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-green-700 disabled:opacity-50 transition">
          라우트 캐시 초기화
        </button>
        <button @click="clearCache('view')" :disabled="clearing"
          class="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-purple-700 disabled:opacity-50 transition">
          뷰 캐시 초기화
        </button>
        <button @click="clearCache('all')" :disabled="clearing"
          class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-700 disabled:opacity-50 transition">
          전체 캐시 초기화
        </button>
      </div>
      <div v-if="cacheResult" class="mt-3 text-sm text-green-600 bg-green-50 p-3 rounded-lg">{{ cacheResult }}</div>
    </div>

    <!-- Queue Status -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">큐 상태</h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="text-center p-3 bg-gray-50 rounded-xl">
          <div class="text-2xl font-black text-gray-800">{{ queue.pending || 0 }}</div>
          <div class="text-xs text-gray-500 mt-1">대기중</div>
        </div>
        <div class="text-center p-3 bg-gray-50 rounded-xl">
          <div class="text-2xl font-black text-green-600">{{ queue.completed || 0 }}</div>
          <div class="text-xs text-gray-500 mt-1">완료</div>
        </div>
        <div class="text-center p-3 bg-gray-50 rounded-xl">
          <div class="text-2xl font-black text-red-600">{{ queue.failed || 0 }}</div>
          <div class="text-xs text-gray-500 mt-1">실패</div>
        </div>
        <div class="text-center p-3 bg-gray-50 rounded-xl">
          <div class="text-2xl font-black text-blue-600">{{ queue.workers || 0 }}</div>
          <div class="text-xs text-gray-500 mt-1">워커</div>
        </div>
      </div>
    </div>

    <!-- Disk Usage -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">디스크 사용량</h3>
      <div class="space-y-2">
        <div v-for="disk in disks" :key="disk.name" class="flex items-center gap-3">
          <span class="text-sm text-gray-700 w-24 flex-shrink-0">{{ disk.name }}</span>
          <div class="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
            <div class="h-full rounded-full transition-all" :class="disk.percent > 80 ? 'bg-red-500' : 'bg-blue-500'" :style="{ width: disk.percent + '%' }"></div>
          </div>
          <span class="text-xs text-gray-500 w-20 text-right flex-shrink-0">{{ disk.used }} / {{ disk.total }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const info = ref({}), queue = ref({}), disks = ref([]), clearing = ref(false), cacheResult = ref('')
async function loadData() { try { const { data } = await axios.get('/api/admin/system'); info.value = data.info || {}; queue.value = data.queue || {}; disks.value = data.disks || [] } catch {} }
async function clearCache(type) {
  clearing.value = true; cacheResult.value = ''
  try { const { data } = await axios.post('/api/admin/system/clear-cache', { type }); cacheResult.value = data.message || '캐시가 초기화되었습니다' } catch (e) { cacheResult.value = e.response?.data?.message || '실패' }
  clearing.value = false
}
onMounted(loadData)
</script>
