<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">📐 페이지별 광고 슬롯 설정</h1>
  <p class="text-xs text-gray-500 mb-4">각 페이지의 왼쪽/오른쪽 사이드바에 표시할 광고 슬롯 수를 설정합니다.</p>

  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
  <div v-else class="space-y-2">
    <div v-for="(cfg, pageKey) in config" :key="pageKey"
      class="bg-white rounded-xl border p-4 flex items-center gap-4">
      <div class="w-28 flex-shrink-0">
        <div class="text-sm font-bold text-gray-800">{{ cfg.label || pageKey }}</div>
        <div class="text-[10px] text-gray-400">/{{ pageKey === 'home' ? '' : pageKey }}</div>
      </div>
      <div class="flex-1 grid grid-cols-2 gap-4">
        <div>
          <label class="text-[10px] font-bold text-blue-600 block mb-1">좌측 슬롯</label>
          <div class="flex items-center gap-2">
            <input type="range" v-model.number="cfg.left_slots" min="0" max="5" class="flex-1" />
            <span class="text-sm font-black text-blue-700 w-6 text-center">{{ cfg.left_slots }}</span>
          </div>
        </div>
        <div>
          <label class="text-[10px] font-bold text-orange-600 block mb-1">우측 슬롯</label>
          <div class="flex items-center gap-2">
            <input type="range" v-model.number="cfg.right_slots" min="0" max="5" class="flex-1" />
            <span class="text-sm font-black text-orange-700 w-6 text-center">{{ cfg.right_slots }}</span>
          </div>
        </div>
      </div>
    </div>

    <button @click="save" :disabled="saving"
      class="w-full bg-amber-400 text-amber-900 font-bold py-3 rounded-xl text-sm hover:bg-amber-500 disabled:opacity-50 mt-4">
      {{ saving ? '저장중...' : '설정 저장' }}
    </button>
    <div v-if="msg" class="text-center text-sm text-green-600 mt-2">{{ msg }}</div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const config = ref({})
const loading = ref(true)
const saving = ref(false)
const msg = ref('')

async function load() {
  try {
    const { data } = await axios.get('/api/admin/ad-settings')
    config.value = data.data || {}
  } catch {}
  loading.value = false
}

async function save() {
  saving.value = true; msg.value = ''
  try {
    const { data } = await axios.post('/api/admin/ad-settings', { config: config.value })
    msg.value = data.message || '저장됨'
  } catch { msg.value = '저장 실패' }
  saving.value = false
}

onMounted(load)
</script>
