<template>
  <ListTemplate
    :title="locale === 'ko' ? '중고장터' : 'Marketplace'"
    emoji="🛍️"
    :subtitle="locale === 'ko' ? '한인 중고 거래 · 물물 교환' : 'Buy & Sell Used Items'"
    :loading="loading"
    :items="items"
    :categories="categoryTabs"
    :activeCategory="activeCategory"
    :hasSearch="true"
    :searchQuery="search"
    :searchPlaceholder="locale === 'ko' ? '중고장터 검색...' : 'Search marketplace...'"
    :sortOptions="sortOpts"
    :activeSort="sort"
    :hasViewToggle="true"
    :viewMode="viewMode"
    :hasWrite="true"
    writeTo="/market/write"
    :pagination="pagination"
    @category-change="onCatChange"
    @search="onSearch"
    @sort-change="onSortChange"
    @view-change="onViewChange"
    @page-change="onPageChange"
  >
    <template #header-right>
      <select v-model="conditionFilter" @change="load(1)"
        class="text-xs border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-2 py-1.5 focus:outline-none">
        <option value="">{{ locale === 'ko' ? '전체 상태' : 'All Conditions' }}</option>
        <option value="새것">{{ locale === 'ko' ? '새상품' : 'New' }}</option>
        <option value="거의 새것">{{ locale === 'ko' ? '거의 새것' : 'Like New' }}</option>
        <option value="사용감 있음">{{ locale === 'ko' ? '좋음' : 'Good' }}</option>
        <option value="많이 사용">{{ locale === 'ko' ? '보통' : 'Fair' }}</option>
      </select>
    </template>

    <template #item-card="{ item }">
      <router-link :to="`/market/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition">
        <div class="flex gap-3 p-3">
          <div class="w-24 h-24 flex-shrink-0 rounded-lg bg-gray-100 dark:bg-gray-700 overflow-hidden flex items-center justify-center">
            <img v-if="item.images?.[0]" :src="item.images[0]" class="w-full h-full object-cover" @error="e => e.target.src=''" />
            <span v-else class="text-3xl">📦</span>
          </div>
          <div class="flex-1 min-w-0 py-1">
            <div class="flex items-center gap-2 mb-1">
              <span v-if="item.status === 'reserved'" class="text-[10px] bg-yellow-500 text-white px-1.5 py-0.5 rounded-full font-bold">
                {{ locale === 'ko' ? '예약중' : 'Reserved' }}
              </span>
              <span v-if="item.status === 'sold'" class="text-[10px] bg-gray-500 text-white px-1.5 py-0.5 rounded-full font-bold">
                {{ locale === 'ko' ? '판매완료' : 'Sold' }}
              </span>
            </div>
            <h3 class="font-semibold text-gray-800 dark:text-white text-sm truncate">{{ item.title }}</h3>
            <p class="text-blue-600 dark:text-blue-400 font-bold text-sm mt-1">
              {{ Number(item.price) === 0 ? (locale === 'ko' ? '무료 나눔' : 'Free') : `$${Number(item.price).toLocaleString()}` }}
              <span v-if="item.price_negotiable" class="text-xs text-gray-400 font-normal">({{ locale === 'ko' ? '협의' : 'Negotiable' }})</span>
            </p>
            <div class="flex items-center gap-2 mt-1 text-xs text-gray-400">
              <span>📍 {{ item.region }}</span>
              <span v-if="item.condition">· {{ item.condition }}</span>
              <span>· {{ formatDate(item.created_at) }}</span>
            </div>
          </div>
        </div>
      </router-link>
    </template>

    <template #grid-card="{ item }">
      <router-link :to="`/market/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition relative">
        <div class="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center relative">
          <img v-if="item.images?.[0]" :src="item.images[0]" class="w-full h-full object-cover" @error="e => e.target.src=''" />
          <span v-else class="text-4xl">📦</span>
          <span v-if="item.status === 'reserved'" class="absolute top-2 left-2 bg-yellow-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
            {{ locale === 'ko' ? '예약중' : 'Reserved' }}
          </span>
        </div>
        <div class="p-3">
          <h3 class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{{ item.title }}</h3>
          <p class="text-blue-600 dark:text-blue-400 font-bold text-sm mt-0.5">
            {{ Number(item.price) === 0 ? (locale === 'ko' ? '무료' : 'Free') : `$${Number(item.price).toLocaleString()}` }}
          </p>
          <div class="flex items-center justify-between mt-1 text-xs text-gray-400">
            <span>{{ item.region }}</span>
            <span>{{ item.condition }}</span>
          </div>
        </div>
      </router-link>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">📦</p>
        <p class="text-gray-400 text-sm">{{ locale === 'ko' ? '등록된 물품이 없습니다' : 'No items yet' }}</p>
      </div>
    </template>
  </ListTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLangStore } from '../../stores/lang'
import ListTemplate from '../../components/templates/ListTemplate.vue'
import axios from 'axios'

const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const items = ref([])
const loading = ref(true)
const search = ref('')
const sort = ref('latest')
const activeCategory = ref('')
const conditionFilter = ref('')
const viewMode = ref('grid')
const pagination = ref(null)

const categoryTabs = computed(() => [
  { value: '', label: locale.value === 'ko' ? '전체' : 'All' },
  { value: '전자제품', label: locale.value === 'ko' ? '전자기기' : 'Electronics' },
  { value: '가구/인테리어', label: locale.value === 'ko' ? '가구' : 'Furniture' },
  { value: '의류/잡화', label: locale.value === 'ko' ? '의류' : 'Clothing' },
  { value: '자동차', label: locale.value === 'ko' ? '자동차' : 'Vehicles' },
  { value: '기타', label: locale.value === 'ko' ? '기타' : 'Other' },
])

const sortOpts = computed(() => [
  { value: 'latest', label: locale.value === 'ko' ? '최신순' : 'Latest' },
  { value: 'price_low', label: locale.value === 'ko' ? '가격낮은순' : 'Price Low' },
  { value: 'price_high', label: locale.value === 'ko' ? '가격높은순' : 'Price High' },
])

function formatDate(d) {
  if (!d) return ''
  const diff = (Date.now() - new Date(d).getTime()) / 1000
  if (diff < 3600) return `${Math.floor(diff / 60)}${locale.value === 'ko' ? '분 전' : 'm ago'}`
  if (diff < 86400) return `${Math.floor(diff / 3600)}${locale.value === 'ko' ? '시간 전' : 'h ago'}`
  return new Date(d).toLocaleDateString('ko-KR')
}

function onCatChange(val) { activeCategory.value = val; load(1) }
function onSearch(val) { search.value = val; load(1) }
function onSortChange(val) { sort.value = val; load(1) }
function onViewChange(val) { viewMode.value = val }
function onPageChange(page) { load(page) }

async function load(page = 1) {
  loading.value = true
  try {
    const params = { page, per_page: 20 }
    if (search.value.trim()) params.search = search.value.trim()
    if (activeCategory.value) params.category = activeCategory.value
    if (conditionFilter.value) params.condition = conditionFilter.value
    if (sort.value) params.sort = sort.value

    const { data } = await axios.get('/api/market', { params })
    items.value = data.data || []
    pagination.value = data.last_page > 1 ? { current_page: data.current_page, last_page: data.last_page } : null
  } catch { items.value = [] }
  loading.value = false
}

onMounted(() => load())
</script>
