<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <!-- Header -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 mb-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
              <span class="text-xl">🛒</span> 쇼핑 정보
            </h1>
            <p class="text-sm text-gray-500 mt-0.5">한인 / 미국 마트 주간 세일 & 특가 정보</p>
          </div>
          <button @click="detectLocation"
            class="flex items-center gap-1.5 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg px-3 py-2 text-sm text-gray-600 dark:text-gray-300 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
            {{ locationText }}
          </button>
        </div>

        <!-- Store category tabs -->
        <div class="flex gap-2 mt-3 overflow-x-auto scrollbar-hide">
          <button v-for="cat in storeCats" :key="cat.value" @click="selectedCat = cat.value; loadStores()"
            class="px-3 py-1.5 text-xs font-medium rounded-full whitespace-nowrap transition"
            :class="selectedCat === cat.value
              ? 'bg-orange-500 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200'">
            {{ cat.icon }} {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loadingStores && !stores.length" class="text-center py-16 text-gray-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mb-3"></div>
        <p class="text-sm">불러오는 중...</p>
      </div>

      <template v-else>
        <!-- Store horizontal scroll -->
        <div v-if="filteredStores.length" class="flex gap-3 overflow-x-auto pb-3 mb-5 scrollbar-hide">
          <button v-for="s in filteredStores" :key="s.id" @click="selectStore(s)"
            :class="[selectedStore?.id === s.id ? 'border-orange-500 bg-orange-50 dark:bg-orange-900/20' : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 hover:border-orange-300']"
            class="flex-shrink-0 w-28 border rounded-xl p-3 text-center transition">
            <div class="text-2xl mb-1">{{ storeEmoji(s.category) }}</div>
            <div class="text-xs font-bold text-gray-800 dark:text-white truncate">{{ s.name }}</div>
            <div v-if="s.active_deals_count" class="text-[10px] text-blue-500 mt-0.5">딜 {{ s.active_deals_count }}개</div>
            <div class="text-[10px] text-gray-400 mt-0.5">{{ s.locations_count || 0 }}지점</div>
          </button>
        </div>

        <!-- Selected store details -->
        <div v-if="selectedStore && storeDetail" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm mb-5 overflow-hidden">
          <div class="bg-gray-50 dark:bg-gray-700/50 p-4 border-b border-gray-100 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="font-bold text-lg text-gray-900 dark:text-white">{{ storeDetail.name }}</h2>
                <p v-if="storeDetail.name_en" class="text-xs text-gray-400">{{ storeDetail.name_en }}</p>
              </div>
              <button @click="selectedStore = null; storeDetail = null"
                class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-xl">&times;</button>
            </div>
          </div>

          <!-- Store tabs -->
          <div class="flex border-b border-gray-100 dark:border-gray-700">
            <button @click="storeTab = 'deals'"
              :class="storeTab === 'deals' ? 'border-orange-500 text-orange-600' : 'border-transparent text-gray-500'"
              class="flex-1 py-3 text-sm font-medium border-b-2 transition">이번주 세일</button>
            <button @click="storeTab = 'flyers'"
              :class="storeTab === 'flyers' ? 'border-orange-500 text-orange-600' : 'border-transparent text-gray-500'"
              class="flex-1 py-3 text-sm font-medium border-b-2 transition">전단지</button>
          </div>

          <!-- Deals grid -->
          <div v-if="storeTab === 'deals'" class="p-4">
            <div v-if="storeDetail.deals?.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
              <div v-for="d in storeDetail.deals" :key="d.id"
                class="border dark:border-gray-600 rounded-xl overflow-hidden hover:shadow-md transition group cursor-pointer"
                @click="selectedDeal = d">
                <div class="aspect-square bg-gray-100 dark:bg-gray-700 relative overflow-hidden">
                  <img v-if="d.image_url" :src="d.image_url" class="w-full h-full object-cover group-hover:scale-105 transition"
                    @error="e => { e.target.style.display='none' }" />
                  <div v-if="!d.image_url" class="w-full h-full flex items-center justify-center text-4xl text-gray-300">🛒</div>
                  <span v-if="discountRate(d)" class="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">-{{ discountRate(d) }}%</span>
                </div>
                <div class="p-2.5">
                  <div class="text-xs font-medium text-gray-800 dark:text-gray-200 line-clamp-2 leading-tight">{{ d.title }}</div>
                  <div class="flex items-baseline gap-1.5 mt-1.5">
                    <span v-if="d.sale_price" class="text-sm font-bold text-red-600">${{ Number(d.sale_price).toFixed(2) }}</span>
                    <span v-if="d.original_price && d.original_price != d.sale_price" class="text-xs text-gray-400 line-through">${{ Number(d.original_price).toFixed(2) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-400 text-sm">등록된 세일 정보가 없습니다</div>
          </div>

          <!-- Flyers -->
          <div v-if="storeTab === 'flyers'" class="p-4">
            <div v-if="storeDetail.flyers?.length" class="grid grid-cols-2 gap-3">
              <div v-for="f in storeDetail.flyers" :key="f.id" class="border dark:border-gray-600 rounded-xl overflow-hidden">
                <img v-if="f.image_url" :src="f.image_url" class="w-full" @error="e => { e.target.style.display='none' }" />
                <div class="p-2 text-xs text-gray-500">{{ f.title || '전단지' }}</div>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-400 text-sm">등록된 전단지가 없습니다</div>
          </div>
        </div>

        <!-- Special deals -->
        <div v-if="specialDeals.length" class="mb-5">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-3">🔥 이번 주 특가</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            <div v-for="d in specialDeals" :key="d.id"
              class="bg-white dark:bg-gray-800 border border-red-100 dark:border-red-800 rounded-xl overflow-hidden hover:shadow-md transition group cursor-pointer"
              @click="selectedDeal = d">
              <div class="aspect-square bg-gray-50 dark:bg-gray-700 relative overflow-hidden">
                <img v-if="d.image_url" :src="d.image_url" class="w-full h-full object-cover group-hover:scale-105 transition"
                  @error="e => { e.target.style.display='none' }" />
                <div v-if="!d.image_url" class="w-full h-full flex items-center justify-center text-4xl text-gray-300">🏷️</div>
                <span v-if="discountRate(d)" class="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">-{{ discountRate(d) }}%</span>
              </div>
              <div class="p-2.5">
                <div v-if="d.store_name" class="text-[10px] text-orange-500 font-medium">{{ d.store_name }}</div>
                <div class="text-xs font-medium text-gray-800 dark:text-gray-200 line-clamp-2 mt-0.5">{{ d.title }}</div>
                <div class="flex items-baseline gap-1.5 mt-1">
                  <span class="text-sm font-bold text-red-600">${{ Number(d.sale_price).toFixed(2) }}</span>
                  <span v-if="d.original_price" class="text-xs text-gray-400 line-through">${{ Number(d.original_price).toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- All deals -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-lg font-bold text-gray-900 dark:text-white">🛍️ 세일 정보</h2>
            <select v-model="dealSort" @change="loadDeals(true)"
              class="text-xs border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-2 py-1.5 focus:outline-none">
              <option value="">전체</option>
              <option value="discount">할인율순</option>
              <option value="latest">최신순</option>
            </select>
          </div>

          <!-- Deals grid -->
          <div v-if="deals.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            <div v-for="d in deals" :key="d.id"
              class="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-xl overflow-hidden hover:shadow-md transition group cursor-pointer"
              @click="selectedDeal = d">
              <div class="aspect-[4/3] bg-gray-100 dark:bg-gray-700 relative overflow-hidden">
                <img v-if="d.image_url" :src="d.image_url" class="w-full h-full object-cover group-hover:scale-105 transition" loading="lazy"
                  @error="e => { e.target.style.display='none' }" />
                <div v-if="!d.image_url" class="w-full h-full flex items-center justify-center text-4xl text-gray-300">🛒</div>
                <span v-if="discountRate(d)" class="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">-{{ discountRate(d) }}%</span>
              </div>
              <div class="p-2.5">
                <div v-if="d.store_name" class="text-[10px] text-orange-500 font-medium mb-0.5">{{ d.store_name }}</div>
                <div class="text-xs font-medium text-gray-800 dark:text-gray-200 line-clamp-2 leading-tight">{{ d.title }}</div>
                <div class="flex items-baseline gap-1.5 mt-1.5">
                  <span v-if="d.sale_price" class="text-sm font-bold text-red-600">${{ Number(d.sale_price).toFixed(2) }}</span>
                  <span v-if="d.original_price && d.original_price != d.sale_price" class="text-xs text-gray-400 line-through">${{ Number(d.original_price).toFixed(2) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Loading skeleton -->
          <div v-if="loadingDeals" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            <div v-for="i in 8" :key="i" class="border dark:border-gray-700 rounded-xl overflow-hidden animate-pulse">
              <div class="aspect-[4/3] bg-gray-200 dark:bg-gray-700"></div>
              <div class="p-3 space-y-2"><div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div><div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div></div>
            </div>
          </div>

          <div v-if="!deals.length && !loadingDeals" class="text-center py-12 text-gray-400">
            <div class="text-4xl mb-2">🛒</div>
            <p class="text-sm">등록된 세일 정보가 없습니다</p>
          </div>

          <!-- Load more -->
          <div v-if="hasMore" class="text-center mt-4">
            <button @click="loadDeals()" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 px-6 py-2.5 rounded-xl text-sm font-medium transition">더보기</button>
          </div>
        </div>
      </template>

      <!-- Deal detail modal -->
      <Teleport to="body">
        <div v-if="selectedDeal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="selectedDeal = null">
          <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto">
            <div class="relative">
              <img v-if="selectedDeal.image_url" :src="selectedDeal.image_url" class="w-full aspect-video object-cover rounded-t-2xl"
                @error="e => { e.target.style.display='none' }" />
              <button @click="selectedDeal = null" class="absolute top-3 right-3 bg-black/50 text-white w-8 h-8 rounded-full flex items-center justify-center">&times;</button>
            </div>
            <div class="p-5">
              <div v-if="selectedDeal.store_name" class="text-xs text-orange-500 font-medium mb-1">{{ selectedDeal.store_name }}</div>
              <h3 class="font-bold text-gray-900 dark:text-white">{{ selectedDeal.title }}</h3>
              <div class="flex items-baseline gap-2 mt-2">
                <span v-if="selectedDeal.sale_price" class="text-xl font-bold text-red-600">${{ Number(selectedDeal.sale_price).toFixed(2) }}</span>
                <span v-if="selectedDeal.original_price" class="text-sm text-gray-400 line-through">${{ Number(selectedDeal.original_price).toFixed(2) }}</span>
                <span v-if="discountRate(selectedDeal)" class="bg-red-100 text-red-600 text-xs font-bold px-2 py-0.5 rounded-full">-{{ discountRate(selectedDeal) }}%</span>
              </div>
              <p v-if="selectedDeal.description" class="text-sm text-gray-600 dark:text-gray-300 mt-3">{{ selectedDeal.description }}</p>
              <div v-if="selectedDeal.valid_until" class="text-xs text-gray-400 mt-2">세일기간: {{ formatDate(selectedDeal.valid_from) }} ~ {{ formatDate(selectedDeal.valid_until) }}</div>
              <a v-if="selectedDeal.url" :href="selectedDeal.url" target="_blank"
                class="block mt-4 bg-orange-500 hover:bg-orange-600 text-white text-center py-3 rounded-xl font-medium transition">
                구매 페이지 바로가기
              </a>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const auth = useAuthStore()

// Location
const userLat = ref(null)
const userLng = ref(null)
const radius = ref(30)
const locationText = ref('위치 설정')

// Data
const stores = ref([])
const deals = ref([])
const specialDeals = ref([])
const loadingStores = ref(false)
const loadingDeals = ref(false)
const selectedCat = ref('')
const selectedStore = ref(null)
const storeDetail = ref(null)
const storeTab = ref('deals')
const dealSort = ref('')
const selectedDeal = ref(null)
const page = ref(1)
const hasMore = ref(false)

const storeCats = [
  { value: '', icon: '🏪', label: '전체' },
  { value: 'korean_mart', icon: '🇰🇷', label: '한인마트' },
  { value: 'us_mart', icon: '🇺🇸', label: '미국마트' },
  { value: 'asian_mart', icon: '🌏', label: '아시안마트' },
  { value: 'online', icon: '💻', label: '온라인' },
]

const filteredStores = computed(() => {
  if (!selectedCat.value) return stores.value
  return stores.value.filter(s => s.category === selectedCat.value)
})

function storeEmoji(cat) {
  return { korean_mart: '🇰🇷', us_mart: '🇺🇸', asian_mart: '🌏', online: '💻' }[cat] || '🏪'
}

function discountRate(d) {
  if (d.discount_percent > 0) return d.discount_percent
  if (d.original_price && d.sale_price && d.original_price > 0) return Math.round((1 - d.sale_price / d.original_price) * 100)
  return null
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}

function detectLocation() {
  const saved = localStorage.getItem('sk_user_location')
  if (saved) {
    const loc = JSON.parse(saved)
    userLat.value = loc.lat; userLng.value = loc.lng
    locationText.value = '내 위치'
    refreshAll(); return
  }
  if (!navigator.geolocation) { locationText.value = '위치 미지원'; return }
  locationText.value = '감지 중...'
  navigator.geolocation.getCurrentPosition(
    pos => {
      userLat.value = pos.coords.latitude; userLng.value = pos.coords.longitude
      localStorage.setItem('sk_user_location', JSON.stringify({ lat: userLat.value, lng: userLng.value }))
      locationText.value = '현재 위치'
      refreshAll()
    },
    () => { locationText.value = '위치 거부됨' },
    { timeout: 10000 }
  )
}

function refreshAll() { loadStores(); loadDeals(true); loadSpecial() }

async function loadStores() {
  loadingStores.value = true
  try {
    const params = {}
    if (userLat.value) { params.lat = userLat.value; params.lng = userLng.value; params.radius_miles = radius.value }
    const { data } = await axios.get('/api/shopping/stores', { params })
    stores.value = Array.isArray(data) ? data : (data.data || [])
  } catch { stores.value = [] }
  loadingStores.value = false
}

async function selectStore(s) {
  if (selectedStore.value?.id === s.id) { selectedStore.value = null; storeDetail.value = null; return }
  selectedStore.value = s; storeTab.value = 'deals'
  try {
    const params = {}
    if (userLat.value) { params.lat = userLat.value; params.lng = userLng.value }
    const { data } = await axios.get(`/api/shopping/stores/${s.id}`, { params })
    storeDetail.value = data
  } catch { storeDetail.value = { ...s, deals: [], flyers: [] } }
}

async function loadDeals(reset = false) {
  if (reset) { page.value = 1; deals.value = [] }
  loadingDeals.value = true
  try {
    const params = { page: page.value, per_page: 20 }
    if (dealSort.value) params.sort = dealSort.value
    if (userLat.value) { params.lat = userLat.value; params.lng = userLng.value; params.radius_miles = radius.value }
    const { data } = await axios.get('/api/shopping/deals', { params })
    const items = data.data || data || []
    if (reset) deals.value = items; else deals.value.push(...items)
    hasMore.value = !!data.next_page_url
    page.value++
  } catch {}
  loadingDeals.value = false
}

async function loadSpecial() {
  try {
    const params = { is_special: 1, per_page: 8 }
    if (userLat.value) { params.lat = userLat.value; params.lng = userLng.value; params.radius_miles = radius.value }
    const { data } = await axios.get('/api/shopping/deals', { params })
    specialDeals.value = (data.data || data || []).filter(d => discountRate(d) >= 30)
  } catch { specialDeals.value = [] }
}

onMounted(async () => {
  detectLocation()
  await Promise.all([loadStores(), loadDeals(true)])
  loadSpecial()
})
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
