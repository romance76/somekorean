<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">📐 광고 슬롯 설정</h1>

  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
  <div v-else class="space-y-6">

    <!-- 등급별 최소 입찰가 설정 -->
    <div class="bg-amber-50 rounded-2xl border border-amber-200 p-5">
      <h2 class="font-bold text-amber-800 text-sm mb-3">💰 등급별 최소 월 입찰가 (P)</h2>
      <p class="text-xs text-amber-600 mb-4">광고 신청 페이지에서 각 슬롯 옆에 표시됩니다</p>

      <div class="mb-4">
        <h3 class="text-xs font-bold text-gray-700 mb-2">📌 좌측 사이드바</h3>
        <div class="grid grid-cols-3 gap-3">
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <label class="text-[10px] font-bold text-yellow-700 block mb-1">🥇 프리미엄 (고정)</label>
            <div class="flex items-center gap-1">
              <input type="number" v-model.number="minPrices.left_premium" min="100" step="100" class="flex-1 border rounded px-2 py-1.5 text-sm font-bold text-center" />
              <span class="text-[10px] font-bold">P</span>
            </div>
          </div>
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <label class="text-[10px] font-bold text-blue-700 block mb-1">🥈 스탠다드 (2개)</label>
            <div class="flex items-center gap-1">
              <input type="number" v-model.number="minPrices.left_standard" min="100" step="100" class="flex-1 border rounded px-2 py-1.5 text-sm font-bold text-center" />
              <span class="text-[10px] font-bold">P</span>
            </div>
          </div>
          <div class="bg-green-50 border border-green-200 rounded-lg p-3">
            <label class="text-[10px] font-bold text-green-700 block mb-1">🥉 이코노미 (5개)</label>
            <div class="flex items-center gap-1">
              <input type="number" v-model.number="minPrices.left_economy" min="100" step="100" class="flex-1 border rounded px-2 py-1.5 text-sm font-bold text-center" />
              <span class="text-[10px] font-bold">P</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <h3 class="text-xs font-bold text-gray-700 mb-2">📌 우측 사이드바</h3>
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
            <label class="text-[10px] font-bold text-yellow-700 block mb-1">🥇 프리미엄 (고정)</label>
            <div class="flex items-center gap-1">
              <input type="number" v-model.number="minPrices.right_premium" min="100" step="100" class="flex-1 border rounded px-2 py-1.5 text-sm font-bold text-center" />
              <span class="text-[10px] font-bold">P</span>
            </div>
          </div>
          <div class="bg-green-50 border border-green-200 rounded-lg p-3">
            <label class="text-[10px] font-bold text-green-700 block mb-1">🥉 이코노미 (3개)</label>
            <div class="flex items-center gap-1">
              <input type="number" v-model.number="minPrices.right_economy" min="100" step="100" class="flex-1 border rounded px-2 py-1.5 text-sm font-bold text-center" />
              <span class="text-[10px] font-bold">P</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4">
        <h3 class="text-xs font-bold text-gray-700 mb-2">🌍 지역별 추가금</h3>
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <label class="text-[10px] font-bold text-blue-700 block mb-1">주 (카운티 대비 추가)</label>
            <div class="flex items-center gap-1">
              <input type="number" v-model.number="geoMarkup.state" min="0" step="500" class="flex-1 border rounded px-2 py-1.5 text-sm font-bold text-center" />
              <span class="text-[10px] font-bold">P</span>
            </div>
          </div>
          <div class="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <label class="text-[10px] font-bold text-amber-700 block mb-1">전국 (주 대비 추가)</label>
            <div class="flex items-center gap-1">
              <input type="number" v-model.number="geoMarkup.national" min="0" step="500" class="flex-1 border rounded px-2 py-1.5 text-sm font-bold text-center" />
              <span class="text-[10px] font-bold">P</span>
            </div>
          </div>
        </div>
      </div>

      <button @click="savePrices" :disabled="savingPrices" class="mt-4 bg-amber-400 text-amber-900 font-bold px-6 py-2 rounded-lg text-xs hover:bg-amber-500 disabled:opacity-50">
        {{ savingPrices ? '저장중...' : '가격 설정 저장' }}
      </button>
      <span v-if="priceMsg" class="ml-3 text-xs text-green-600">{{ priceMsg }}</span>
    </div>

    <!-- 페이지별 슬롯 수 -->
    <div>
      <h2 class="font-bold text-gray-800 text-sm mb-3">📄 페이지별 광고 슬롯 수</h2>
      <p class="text-xs text-gray-500 mb-3">각 페이지의 왼쪽/오른쪽 사이드바에 표시할 광고 슬롯 수</p>
      <div class="space-y-2">
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
      </div>

      <button @click="save" :disabled="saving"
        class="w-full bg-amber-400 text-amber-900 font-bold py-3 rounded-xl text-sm hover:bg-amber-500 disabled:opacity-50 mt-4">
        {{ saving ? '저장중...' : '슬롯 설정 저장' }}
      </button>
      <div v-if="msg" class="text-center text-sm text-green-600 mt-2">{{ msg }}</div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const config = ref({})
const minPrices = ref({
  left_premium: 8000, left_standard: 7000, left_economy: 4000,
  right_premium: 10000, right_economy: 6000
})
const geoMarkup = ref({ state: 2000, national: 3000 })
const loading = ref(true)
const saving = ref(false)
const savingPrices = ref(false)
const msg = ref('')
const priceMsg = ref('')

async function load() {
  try {
    const { data } = await axios.get('/api/admin/ad-settings')
    config.value = data.data || {}
  } catch {}
  try {
    const { data } = await axios.get('/api/ad-settings/public')
    if (data.data?.slot_min_prices) minPrices.value = { ...minPrices.value, ...data.data.slot_min_prices }
    if (data.data?.geo_markup) geoMarkup.value = { ...geoMarkup.value, ...data.data.geo_markup }
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

async function savePrices() {
  savingPrices.value = true; priceMsg.value = ''
  try {
    await axios.post('/api/admin/ad-slot-prices', { prices: minPrices.value, geo_markup: geoMarkup.value })
    priceMsg.value = '저장됨!'
  } catch { priceMsg.value = '저장 실패' }
  savingPrices.value = false
}

onMounted(load)
</script>
