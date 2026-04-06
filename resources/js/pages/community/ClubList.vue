<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-black text-gray-800">👥 동호회</h1>
      <RouterLink v-if="auth.isLoggedIn" to="/clubs" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm hover:bg-amber-500">+ 동호회 만들기</RouterLink>
    </div>

    <!-- 위치 필터 바 (이벤트와 동일) -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-3 mb-4">
      <div class="flex flex-wrap items-center gap-2">
        <!-- 타입 필터 -->
        <div class="flex gap-1">
          <button v-for="t in types" :key="t.value" @click="type=t.value; loadClubs()"
            class="px-3 py-1.5 rounded-full text-xs font-bold transition"
            :class="type===t.value ? 'bg-amber-400 text-amber-900' : 'bg-white border text-gray-500 hover:bg-amber-50'">{{ t.label }}</button>
        </div>

        <!-- 도시 선택 (지역 동호회일 때) -->
        <div v-if="type !== 'online'" class="flex items-center gap-1">
          <span class="text-amber-600 text-sm">📍</span>
          <select v-model="selectedCityIdx" @change="onCityChange" class="border border-gray-200 rounded-lg px-2 py-1.5 text-xs font-semibold text-gray-700 outline-none focus:ring-2 focus:ring-amber-400 bg-amber-50">
            <option value="-2" v-if="myCity">📌 내 위치 ({{ myCity.label || myCity.name }})</option>
            <option value="-1">🇺🇸 전국</option>
            <optgroup label="한인 밀집 도시">
              <option v-for="(c, i) in koreanCities" :key="i" :value="i">{{ c.label }}</option>
            </optgroup>
          </select>
          <select v-if="selectedCityIdx !== '-1' && selectedCityIdx !== -1" v-model="radius" @change="loadClubs()" class="border border-gray-200 rounded-lg px-2 py-1.5 text-xs text-gray-600 outline-none">
            <option value="10">10mi</option><option value="30">30mi</option><option value="50">50mi</option><option value="100">100mi</option>
          </select>
        </div>

        <!-- 검색 -->
        <form @submit.prevent="loadClubs()" class="flex-1 flex gap-2 min-w-[150px]">
          <input v-model="search" type="text" placeholder="동호회 검색..." class="flex-1 border rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
          <button type="submit" class="bg-amber-400 text-amber-900 font-bold px-3 py-1.5 rounded-lg text-xs">검색</button>
        </form>
      </div>
      <div v-if="type !== 'online'" class="text-[10px] text-gray-400 mt-1.5">{{ locationInfo }}</div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="!clubs.length" class="text-center py-12">
      <div class="text-4xl mb-3">👥</div>
      <div class="text-gray-500 font-semibold">검색 결과가 없습니다</div>
      <div v-if="type==='local'" class="text-xs text-gray-400 mt-1">다른 도시를 선택하거나 '전국'으로 검색해보세요</div>
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <RouterLink v-for="club in clubs" :key="club.id" :to="`/clubs/${club.id}`"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md hover:-translate-y-0.5 transition-all">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center text-2xl">👥</div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-bold text-gray-800 truncate">{{ club.name }}</div>
            <div class="text-[10px] text-gray-400">{{ club.category }} · {{ club.type === 'online' ? '온라인' : '지역' }}</div>
          </div>
        </div>
        <div class="text-xs text-gray-500 line-clamp-2 mb-2">{{ club.description }}</div>
        <div class="flex items-center justify-between text-[10px] text-gray-400">
          <span>👥 {{ club.member_count }}명</span>
          <div class="flex items-center gap-2">
            <span v-if="club.distance !== undefined && club.distance !== null" class="text-amber-600 font-semibold">{{ Number(club.distance).toFixed(1) }}mi</span>
            <span class="px-2 py-0.5 rounded-full" :class="club.type==='online' ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600'">
              {{ club.type === 'online' ? '🌐 온라인' : '📍 지역' }}
            </span>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLocation } from '../../composables/useLocation'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const auth = useAuthStore()
const { city, locationQuery, koreanCities, init: initLocation, selectKoreanCity } = useLocation()

const clubs = ref([])
const loading = ref(true)
const type = ref('')
const search = ref('')
const radius = ref('30')
const selectedCityIdx = ref('-2')
const myCity = ref(null)

const types = [
  { value: '', label: '전체' },
  { value: 'online', label: '🌐 온라인' },
  { value: 'local', label: '📍 지역' },
]

const locationInfo = computed(() => {
  if (selectedCityIdx.value === -1 || selectedCityIdx.value === '-1') return '전국 검색 중'
  const c = selectedCityIdx.value === '-2' || selectedCityIdx.value === -2
    ? myCity.value
    : koreanCities[selectedCityIdx.value]
  if (!c) return '위치를 선택해주세요'
  return (c.label || c.name) + ' 기준 ' + radius.value + 'mi 반경'
})

function onCityChange() {
  const idx = parseInt(selectedCityIdx.value)
  if (idx === -1) radius.value = '0'
  else if (idx >= 0) { selectKoreanCity(idx); radius.value = '30' }
  loadClubs()
}

async function loadClubs() {
  loading.value = true
  const params = {}
  if (type.value) params.type = type.value
  if (search.value) params.search = search.value

  // 지역 동호회일 때 위치 필터
  if (type.value !== 'online' && radius.value !== '0') {
    const idx = parseInt(selectedCityIdx.value)
    let lat, lng
    if (idx >= 0) { lat = koreanCities[idx].lat; lng = koreanCities[idx].lng }
    else if (myCity.value?.lat) { lat = myCity.value.lat; lng = myCity.value.lng }
    if (lat && lng) { params.lat = lat; params.lng = lng; params.radius = parseInt(radius.value) }
  }

  try {
    const { data } = await axios.get('/api/clubs', { params })
    clubs.value = data.data?.data || data.data || []
  } catch {}
  loading.value = false
}

onMounted(async () => {
  await initLocation()
  if (city.value) { myCity.value = { ...city.value }; selectedCityIdx.value = '-2' }
  else { selectedCityIdx.value = '-1'; radius.value = '0' }
  loadClubs()
})
</script>
