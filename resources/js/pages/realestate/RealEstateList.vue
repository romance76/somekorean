<template>
  <ListTemplate
    title="부동산"
    emoji="🏠"
    subtitle="한인 부동산 매물 정보"
    :loading="loading"
    :items="items"
    :categories="typeTabs"
    :activeCategory="filters.type"
    :hasSearch="true"
    :searchQuery="filters.search"
    searchPlaceholder="매물 검색..."
    :sortOptions="sortOptions"
    :activeSort="filters.sort"
    :hasViewToggle="true"
    :viewMode="viewMode"
    :hasWrite="true"
    writeTo="/realestate/write"
    :pagination="pagination"
    :totalCount="pagination?.total || null"
    @category-change="onTypeChange"
    @search="onSearch"
    @sort-change="onSortChange"
    @view-change="v => viewMode = v"
    @page-change="load"
  >
    <!-- Extra filters -->
    <template #header-right>
      <div class="flex items-center gap-2">
        <!-- Property type filter -->
        <select v-model="filters.property_type" @change="load(1)"
          class="text-xs border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-400">
          <option value="">건물유형</option>
          <option v-for="pt in propertyTypes" :key="pt.value" :value="pt.value">{{ pt.label }}</option>
        </select>
        <!-- Bedrooms filter -->
        <select v-model="filters.bedrooms" @change="load(1)"
          class="text-xs border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-400">
          <option value="">방 수</option>
          <option value="0">스튜디오</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4+</option>
        </select>
      </div>
    </template>

    <!-- Card -->
    <template #item-card="{ item }">
      <RouterLink :to="`/realestate/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition group">
        <div class="flex" :class="viewMode === 'grid' ? 'flex-col' : 'flex-row'">
          <!-- Image -->
          <div :class="viewMode === 'grid' ? 'h-48 w-full' : 'w-32 sm:w-44 flex-shrink-0'"
            class="bg-gray-100 dark:bg-gray-700 relative overflow-hidden">
            <img v-if="getPhoto(item)" :src="getPhoto(item)"
              class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
              @error="onImgError($event, '🏠')" />
            <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-sky-50 dark:from-blue-900 dark:to-sky-900">
              <span class="text-4xl">🏠</span>
            </div>
            <!-- Type badge -->
            <span class="absolute top-2 left-2 text-xs font-bold px-2 py-1 rounded-full"
              :class="typeBadgeClass(item.type)">
              {{ item.type }}
            </span>
          </div>

          <!-- Info -->
          <div class="p-4 flex-1 min-w-0">
            <h3 class="font-bold text-gray-800 dark:text-white text-sm mb-1 truncate">{{ item.title }}</h3>
            <p class="text-blue-600 dark:text-blue-400 font-black text-lg">
              {{ formatPrice(item.price) }}
              <span v-if="(item.type === '렌트' || item.type === '룸메이트') && item.price" class="text-sm font-medium text-gray-400">/월</span>
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              {{ item.address || item.region || '주소 미입력' }}
            </p>
            <div class="flex items-center gap-3 mt-2 text-xs text-gray-400 dark:text-gray-500">
              <span v-if="item.bedrooms != null">🛏️ {{ item.bedrooms }}방</span>
              <span v-if="item.bathrooms != null">🚿 {{ item.bathrooms }}욕실</span>
              <span v-if="item.sqft">📐 {{ Number(item.sqft).toLocaleString() }}sqft</span>
            </div>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ formatDate(item.created_at) }}</p>
          </div>
        </div>
      </RouterLink>
    </template>

    <!-- Grid card override -->
    <template #grid-card="{ item }">
      <RouterLink :to="`/realestate/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition group">
        <div class="h-48 bg-gray-100 dark:bg-gray-700 relative overflow-hidden">
          <img v-if="getPhoto(item)" :src="getPhoto(item)"
            class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
            @error="onImgError($event, '🏠')" />
          <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-100 to-sky-50">
            <span class="text-5xl">🏠</span>
          </div>
          <span class="absolute top-2 left-2 text-xs font-bold px-2 py-1 rounded-full"
            :class="typeBadgeClass(item.type)">
            {{ item.type }}
          </span>
        </div>
        <div class="p-4">
          <h3 class="font-bold text-gray-800 dark:text-white text-sm mb-1 truncate">{{ item.title }}</h3>
          <p class="text-blue-600 font-black text-lg">
            {{ formatPrice(item.price) }}
            <span v-if="(item.type === '렌트' || item.type === '룸메이트') && item.price" class="text-sm font-medium text-gray-400">/월</span>
          </p>
          <p class="text-xs text-gray-500 mt-1 truncate">📍 {{ item.address || item.region }}</p>
          <div class="flex items-center gap-3 mt-2 text-xs text-gray-400">
            <span v-if="item.bedrooms != null">🛏️ {{ item.bedrooms }}방</span>
            <span v-if="item.bathrooms != null">🚿 {{ item.bathrooms }}욕실</span>
            <span v-if="item.sqft">📐 {{ Number(item.sqft).toLocaleString() }}sqft</span>
          </div>
        </div>
      </RouterLink>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">🏠</p>
        <p class="text-gray-400 text-sm">등록된 매물이 없습니다</p>
      </div>
    </template>
  </ListTemplate>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ListTemplate from '@/components/templates/ListTemplate.vue'
import axios from 'axios'

const auth = useAuthStore()

const loading = ref(true)
const items = ref([])
const viewMode = ref('grid')
const pagination = ref(null)

const filters = reactive({
  type: '',
  search: '',
  sort: 'latest',
  property_type: '',
  bedrooms: '',
})

const typeTabs = [
  { value: '', label: '전체' },
  { value: '렌트', label: '렌트' },
  { value: '매매', label: '매매' },
  { value: '룸메이트', label: '룸메이트' },
]

const propertyTypes = [
  { value: '아파트', label: '아파트' },
  { value: '하우스', label: '하우스' },
  { value: '콘도', label: '콘도' },
  { value: '스튜디오', label: '스튜디오' },
  { value: '오피스', label: '오피스' },
]

const sortOptions = [
  { value: 'latest', label: '최신순' },
  { value: 'price_asc', label: '가격낮은순' },
  { value: 'price_desc', label: '가격높은순' },
]

function onTypeChange(val) { filters.type = val; load(1) }
function onSearch(val) { filters.search = val; load(1) }
function onSortChange(val) { filters.sort = val; load(1) }

async function load(page = 1) {
  loading.value = true
  try {
    const params = { page }
    if (filters.search) params.search = filters.search
    if (filters.type) params.type = filters.type
    if (filters.sort) params.sort = filters.sort
    if (filters.property_type) params.property_type = filters.property_type
    if (filters.bedrooms) params.bedrooms = filters.bedrooms

    const { data } = await axios.get('/api/realestate', { params })
    items.value = data.data || data || []
    pagination.value = data.data ? {
      current_page: data.current_page,
      last_page: data.last_page,
      total: data.total,
    } : null
  } catch {
    items.value = []
  }
  loading.value = false
}

function getPhoto(item) {
  return item.photos?.[0] || null
}

function typeBadgeClass(type) {
  if (type === '매매') return 'bg-red-500 text-white'
  if (type === '렌트') return 'bg-blue-500 text-white'
  if (type === '룸메이트') return 'bg-green-500 text-white'
  return 'bg-orange-500 text-white'
}

function formatPrice(price) {
  if (!price) return '가격문의'
  return '$' + Number(price).toLocaleString()
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}

function onImgError(e, emoji) {
  e.target.style.display = 'none'
  const parent = e.target.parentElement
  if (parent) {
    parent.classList.add('bg-gradient-to-br', 'from-blue-100', 'to-sky-50')
    parent.innerHTML = `<div class="flex items-center justify-center h-full text-5xl">${emoji}</div>`
  }
}

onMounted(() => load())
</script>
