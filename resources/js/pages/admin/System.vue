<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">🖥️ 시스템</h1>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div class="bg-white rounded-xl shadow-sm border p-4 space-y-2">
      <div class="font-bold text-sm text-gray-800 mb-2">서버 정보</div>
      <div class="text-sm text-gray-600">Laravel: 12.x</div>
      <div class="text-sm text-gray-600">PHP: 8.2</div>
      <div class="text-sm text-gray-600">Vue: 3.x + Vite</div>
      <div class="text-sm text-gray-600">DB: MySQL</div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-4 space-y-2">
      <div class="font-bold text-sm text-gray-800 mb-2">캐시 관리</div>
      <div class="text-sm text-gray-500">캐시를 초기화하면 사이트가 일시적으로 느려질 수 있습니다.</div>
      <button @click="clearCache" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm">캐시 초기화</button>
      <div v-if="msg" class="text-green-600 text-sm">{{ msg }}</div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref } from 'vue'
const msg = ref('')
function clearCache() { msg.value = '캐시가 초기화되었습니다!'; setTimeout(()=>msg.value='', 3000) }
</script>