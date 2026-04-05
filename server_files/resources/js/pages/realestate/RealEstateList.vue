<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <!-- Header -->
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-5 rounded-2xl">
        <div class="flex items-center justify-between gap-2">
          <div>
            <h1 class="text-xl font-black">🏠 부동산</h1>
            <p class="text-blue-100 text-sm mt-0.5 opacity-80">한인 부동산 매물 정보</p>
          </div>
          <router-link v-if="authStore.isLoggedIn" to="/realestate/write"
            class="bg-white text-blue-600 px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-50">+ 매물 등록</router-link>
        </div>
      </div>
    </div>

    <!-- Category tabs -->
    <div class="max-w-[1200px] mx-auto px-4 mt-3">
      <div class="flex gap-2 overflow-x-auto pb-1" style="scrollbar-width:none">
        <button v-for="cat in categories" :key="cat.value"
          @click="category = cat.value; load(1)"
          class="flex-shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition"
          :class="category === cat.value ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:border-blue-300'">
          {{ cat.label }}
        </button>
      </div>
    </div>

    <!-- LocationBar -->
    <div class="max-w-[1200px] mx-auto px-4 mt-2">
      <LocationBar placeholder="부동산 검색..." @search="onLocationSearch" @location-change="onLocationChange" />
    </div>

    <!-- Content -->
    <div class="max-w-[1200px] mx-auto px-4 py-4">
      <div v-if="loading" class="text-center py-16 text-gray-400">불러오는 중...</div>
      <div v-else-if="items.length === 0" class="text-center py-16 text-gray-400">등록된 매물이 없습니다.</div>
      <template v-else>
        <!-- Grid View -->
        <div v-if="viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <router-link v-for="item in items" :key="item.id" :to="`/realestate/${item.id}`"
            class="bg-white rounded-2xl shadow-sm overflow-hidden hover:shadow-md transition group">
            <div class="h-48 bg-gray-100 flex items-center justify-center relative overflow-hidden">
              <img v-if="item.photos?.[0]" :src="item.photos[0]" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" />
              <span v-else class="text-5xl text-gray-300">🏠</span>
              <span class="absolute top-2 left-2 text-xs font-bold px-2 py-1 rounded-full"
                :class="item.type === '매매' ? 'bg-red-500 text-white' : item.type === '렌트' ? 'bg-blue-500 text-white' : item.type === '룸메이트' ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'">
                {{ item.type }}
              </span>
            </div>
            <div class="p-4">
              <h3 class="font-bold text-gray-800 mb-1 truncate">{{ item.title }}</h3>
              <p class="text-blue-600 font-black text-lg">{{ item.price ? '$' + Number(item.price).toLocaleString() : '가격문의' }}
                <span v-if="item.type === '렌트' && item.price" class="text-sm font-medium text-gray-400">/월</span>
              </p>
              <p class="text-xs text-gray-500 mt-1 truncate">📍 {{ item.address }}</p>
              <div class="flex items-center gap-3 mt-2 text-xs text-gray-400">
                <span v-if="item.bedrooms">🛏️ {{ item.bedrooms }}방</span>
                <span v-if="item.bathrooms">🚿 {{ item.bathrooms }}욕실</span>
                <span v-if="item.sqft">📐 {{ Number(item.sqft).toLocaleString() }}sqft</span>
              </div>
              <div class="flex items-center justify-between mt-2 text-xs text-gray-400">
                <span>{{ item.region }}</span>
                <span>{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </router-link>
        </div>

        <!-- List View -->
        <div v-else class="space-y-3">
          <router-link v-for="item in items" :key="item.id" :to="`/realestate/${item.id}`"
            class="bg-white rounded-2xl shadow-sm overflow-hidden hover:shadow-md transition flex group">
            <div class="w-28 sm:w-40 md:w-56 flex-shrink-0 bg-gray-100 flex items-center justify-center relative overflow-hidden">
              <img v-if="item.photos?.[0]" :src="item.photos[0]" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" />
              <span v-else class="text-4xl text-gray-300">🏠</span>
              <span class="absolute top-2 left-2 text-xs font-bold px-2 py-1 rounded-full"
                :class="item.type === '매매' ? 'bg-red-500 text-white' : item.type === '렌트' ? 'bg-blue-500 text-white' : item.type === '룸메이트' ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'">
                {{ item.type }}
              </span>
            </div>
            <div class="flex-1 p-4 min-w-0">
              <h3 class="font-bold text-gray-800 mb-1 truncate">{{ item.title }}</h3>
              <p class="text-blue-600 font-black text-lg">{{ item.price ? '$' + Number(item.price).toLocaleString() : '가격문의' }}
                <span v-if="item.type === '렌트' && item.price" class="text-sm font-medium text-gray-400">/월</span>
              </p>
              <p class="text-xs text-gray-500 mt-1 truncate">📍 {{ item.address }}</p>
              <div class="flex items-center gap-3 mt-2 text-xs text-gray-400">
                <span v-if="item.bedrooms">🛏️ {{ item.bedrooms }}방</span>
                <span v-if="item.bathrooms">🚿 {{ item.bathrooms }}욕실</span>
                <span v-if="item.sqft">📐 {{ Number(item.sqft).toLocaleString() }}sqft</span>
              </div>
              <div class="flex items-center gap-3 mt-2 text-xs text-gray-400">
                <span>{{ item.region }}</span>
                <span>{{ formatDate(item.created_at) }}</span>
              </div>
            </div>
          </router-link>
        </div>
      </template>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center space-x-1 mt-5">
        <button v-for="p in totalPages" :key="p" @click="load(p)"
          class="w-8 h-8 rounded-lg text-sm font-bold transition"
          :class="page === p ? 'bg-blue-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-100'">
          {{ p }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'
import LocationBar from '../../components/location/LocationBar.vue'

const authStore = useAuthStore()

const categories = [
  { value: '', label: '전체' },
  { value: '렌트', label: '렌트' },
  { value: '매매', label: '매매' },
  { value: '룸메이트', label: '룸메이트' },
  { value: '상가', label: '상가' },
]

const regions = [
  'Los Angeles', 'New York', 'Atlanta', 'Chicago', 'Seattle',
  'Dallas', 'Houston', 'San Francisco', 'Boston', 'Miami',
  'Washington DC', 'Las Vegas', 'Phoenix', 'San Diego', 'Denver',
  'Portland', 'Nashville', 'Austin', 'New Jersey', 'Virginia',
]

const category = ref('')
const search = ref('')
const region = ref('')
const radius = ref(30)
const viewMode = ref('grid')

const userLat = ref(null);
const userLng = ref(null);
const userRadius = ref(30);

function getUserLocation() {
  const saved = localStorage.getItem('sk_user_location');
  if (saved) {
    const loc = JSON.parse(saved);
    userLat.value = loc.lat;
    userLng.value = loc.lng;
    return;
  }
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLat.value = pos.coords.latitude;
        userLng.value = pos.coords.longitude;
        localStorage.setItem('sk_user_location', JSON.stringify({lat: pos.coords.latitude, lng: pos.coords.longitude}));
      },
      () => {},
      { timeout: 5000 }
    );
  }
}
const loading = ref(true)
const items = ref([])
const page = ref(1)
const totalPages = ref(1)

async function load(p = 1) {
  loading.value = true
  page.value = p
  try {
    const { data } = await axios.get('/api/realestate', {
      params: {
        page: p,
        search: search.value,
        type: category.value,
        region: region.value,
        lat: userLat.value,
        lng: userLng.value,
        radius: radius.value,
      }
    })
    items.value = data.data || data
    totalPages.value = data.last_page || 1
  } catch {}
  loading.value = false
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}


function onLocationSearch({ keyword, city, radius }) {
  search.value = keyword
  if (city?.lat) { userLat.value = city.lat; userLng.value = city.lng }
  if (radius !== '전국') userRadius.value = parseInt(radius)
  load()
}
function onLocationChange({ city, radius }) {
  if (city?.lat) { userLat.value = city.lat; userLng.value = city.lng }
  userRadius.value = radius === '전국' ? 0 : parseInt(radius)
  load()
}

onMounted(() => load())
</script>
