<template>
  <ListTemplate
    title="한인 업소록"
    emoji="📋"
    subtitle="한인 비즈니스 정보 디렉토리"
    :loading="loading"
    :items="businesses"
    :categories="categories"
    :activeCategory="category"
    :hasSearch="true"
    :searchQuery="search"
    searchPlaceholder="업소록 검색..."
    :sortOptions="sortOptions"
    :activeSort="sort"
    :hasViewToggle="true"
    :viewMode="viewMode"
    :hasWrite="true"
    writeTo="/directory/register"
    :pagination="pagination"
    :totalCount="pagination?.total || null"
    @category-change="onCategoryChange"
    @search="onSearch"
    @sort-change="onSortChange"
    @view-change="v => viewMode = v"
    @page-change="load"
  >
    <template #item-card="{ item }">
      <RouterLink :to="`/directory/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 hover:shadow-md transition">
        <div class="flex items-start gap-3">
          <!-- Logo/Image -->
          <div class="w-16 h-16 rounded-lg overflow-hidden flex-shrink-0 bg-gradient-to-br from-blue-400 to-blue-500">
            <img v-if="getFirstPhoto(item)" :src="getFirstPhoto(item)" :alt="item.name"
              class="w-full h-full object-cover"
              @error="e => { e.target.style.display='none' }" />
            <div v-if="!getFirstPhoto(item)" class="w-full h-full flex items-center justify-center text-white/60 text-xl">
              {{ item.category?.charAt(0) || '📋' }}
            </div>
          </div>
          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-0.5">
              <span v-if="item.is_sponsored" class="text-xs bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded font-medium">프리미엄</span>
              <h3 class="font-semibold text-gray-800 dark:text-white truncate">{{ item.name }}</h3>
            </div>
            <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mb-1">
              <span class="bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded">{{ item.category }}</span>
              <span v-if="item.region">📍 {{ item.region }}</span>
              <span v-if="item.distance" class="text-blue-500 font-medium">{{ Number(item.distance).toFixed(1) }}mi</span>
            </div>
            <p v-if="item.description" class="text-gray-500 dark:text-gray-400 text-xs truncate">{{ item.description }}</p>
          </div>
          <!-- Rating -->
          <div class="flex flex-col items-end ml-2 flex-shrink-0">
            <div class="flex items-center gap-1 text-sm">
              <span class="text-yellow-400">★</span>
              <span class="font-medium text-gray-700 dark:text-gray-300">{{ Number(item.rating_avg || 0).toFixed(1) }}</span>
              <span class="text-xs text-gray-400">({{ item.review_count || 0 }})</span>
            </div>
          </div>
        </div>
      </RouterLink>
    </template>

    <template #grid-card="{ item }">
      <RouterLink :to="`/directory/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition">
        <div class="h-36 bg-gradient-to-r from-blue-400 to-blue-500 relative">
          <img v-if="getFirstPhoto(item)" :src="getFirstPhoto(item)" :alt="item.name"
            class="w-full h-full object-cover" loading="lazy"
            @error="e => { e.target.style.display='none' }" />
          <div v-if="!getFirstPhoto(item)" class="w-full h-full flex items-center justify-center text-white/60 text-4xl">
            {{ item.category?.charAt(0) || '📋' }}
          </div>
          <span v-if="item.distance" class="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded-full">
            📍 {{ Number(item.distance).toFixed(1) }}mi
          </span>
        </div>
        <div class="p-4">
          <div class="flex items-center justify-between mb-1">
            <span v-if="item.is_sponsored" class="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full font-bold">프리미엄</span>
            <span v-else></span>
            <span class="text-yellow-500 text-sm font-bold">★ {{ Number(item.rating_avg || 0).toFixed(1) }}</span>
          </div>
          <h3 class="font-bold text-gray-800 dark:text-white truncate">{{ item.name }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ item.category }} · {{ item.region }}</p>
        </div>
      </RouterLink>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">📋</p>
        <p class="text-gray-400 text-sm">등록된 업소가 없습니다</p>
      </div>
    </template>
  </ListTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ListTemplate from '@/components/templates/ListTemplate.vue'
import axios from 'axios'

const auth = useAuthStore()
const businesses = ref([])
const loading = ref(true)
const category = ref('')
const search = ref('')
const sort = ref('rating')
const viewMode = ref('grid')
const pagination = ref(null)

const categories = [
  { value: '', label: '전체' },
  { value: '음식점', label: '🍽️ 음식점' },
  { value: '한국마트', label: '🛒 마트' },
  { value: '미용실', label: '💇 미용실' },
  { value: '의원/한의원', label: '🏥 병원' },
  { value: '변호사', label: '⚖️ 법률' },
  { value: '회계사', label: '📊 회계' },
  { value: '부동산', label: '🏠 부동산' },
  { value: '자동차', label: '🚗 자동차' },
  { value: '기타', label: '기타' },
]

const sortOptions = [
  { value: 'rating', label: '평점순' },
  { value: 'distance', label: '거리순' },
  { value: 'latest', label: '최신' },
]

function onCategoryChange(val) { category.value = val; load(1) }
function onSearch(val) { search.value = val; load(1) }
function onSortChange(val) { sort.value = val; load(1) }

function getFirstPhoto(biz) {
  if (biz.photos?.length) return typeof biz.photos[0] === 'string' ? biz.photos[0] : biz.photos[0]?.url
  if (biz.owner_photos?.length) return biz.owner_photos[0]
  return null
}

async function load(page = 1) {
  loading.value = true
  try {
    const params = { page, per_page: 24 }
    if (search.value) params.search = search.value
    if (category.value) params.category = category.value
    if (sort.value) params.sort = sort.value

    // Try to get user location
    const savedLoc = localStorage.getItem('sk_user_location')
    if (savedLoc) {
      const loc = JSON.parse(savedLoc)
      params.lat = loc.lat
      params.lng = loc.lng
    }

    const { data } = await axios.get('/api/businesses', { params })
    businesses.value = data.data || []
    pagination.value = {
      current_page: data.current_page || page,
      last_page: data.last_page || 1,
      total: data.total || businesses.value.length,
    }
  } catch {
    businesses.value = []
  }
  loading.value = false
}

onMounted(() => load())
</script>
