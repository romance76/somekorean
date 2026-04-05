<template>
  <ListTemplate
    title="이벤트 & 모임"
    emoji="🎉"
    subtitle="한인 커뮤니티 행사와 모임"
    :loading="loading"
    :items="events"
    :categories="categoryTabs"
    :activeCategory="selectedCat"
    :hasSearch="true"
    :searchQuery="search"
    searchPlaceholder="이벤트 검색..."
    :sortOptions="dateFilters"
    :activeSort="dateFilter"
    :hasWrite="true"
    writeTo="/events/create"
    :pagination="pagination"
    :totalCount="pagination?.total || null"
    @category-change="onCategoryChange"
    @search="onSearch"
    @sort-change="onDateFilterChange"
    @page-change="load"
  >
    <template #item-card="{ item }">
      <div @click="$router.push(`/events/${item.id}`)"
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 cursor-pointer hover:shadow-md transition">
        <div class="flex items-start gap-3">
          <!-- Date badge -->
          <div class="bg-blue-100 dark:bg-blue-900/40 rounded-xl p-3 text-center min-w-[3rem] flex-shrink-0">
            <p class="text-xs text-blue-600 dark:text-blue-400 font-bold">{{ formatMonth(item.event_date) }}</p>
            <p class="text-xl font-black text-blue-700 dark:text-blue-300">{{ formatDay(item.event_date) }}</p>
          </div>
          <!-- Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span class="text-xs bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400 px-2 py-0.5 rounded-full">
                {{ categoryLabel(item.category) }}
              </span>
              <span v-if="item.is_online" class="text-xs bg-green-100 dark:bg-green-900/40 text-green-600 dark:text-green-400 px-2 py-0.5 rounded-full">온라인</span>
              <span v-if="!item.price || item.price == 0" class="text-xs bg-yellow-100 dark:bg-yellow-900/40 text-yellow-600 dark:text-yellow-400 px-2 py-0.5 rounded-full">무료</span>
            </div>
            <h3 class="font-bold text-gray-800 dark:text-white truncate">{{ item.title }}</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm truncate mt-0.5">📍 {{ item.location || item.region || '온라인' }}</p>
            <p class="text-gray-400 text-xs mt-1">주최: {{ item.user?.name || item.organizer_name || '커뮤니티' }}</p>
          </div>
          <!-- Price + Attendees -->
          <div class="text-right flex-shrink-0">
            <p v-if="item.price > 0" class="font-bold text-blue-600 dark:text-blue-400 text-sm">${{ item.price }}</p>
            <p v-else class="font-bold text-green-500 text-sm">무료</p>
            <p class="text-xs text-gray-400 mt-1">{{ item.attendee_count || 0 }}명 참가</p>
          </div>
        </div>
      </div>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">📅</p>
        <p class="text-gray-400 text-sm">이벤트가 없습니다</p>
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
const events = ref([])
const loading = ref(true)
const selectedCat = ref('')
const search = ref('')
const dateFilter = ref('')
const pagination = ref(null)

const categoryTabs = [
  { value: '', label: '전체' },
  { value: 'culture', label: '문화' },
  { value: 'education', label: '교육' },
  { value: 'meetup', label: '네트워킹' },
  { value: 'religion', label: '종교' },
  { value: 'sports', label: '스포츠' },
  { value: 'food', label: '음식' },
  { value: 'business', label: '비즈니스' },
]

const dateFilters = [
  { value: '', label: '전체' },
  { value: 'upcoming', label: '다가오는' },
  { value: 'this_week', label: '이번주' },
  { value: 'this_month', label: '이번달' },
]

const catLabels = { general: '일반', meetup: '모임', food: '음식', culture: '문화', sports: '스포츠', education: '교육', business: '비즈니스', religion: '종교' }
function categoryLabel(c) { return catLabels[c] || c || '일반' }
function formatMonth(d) { return d ? new Date(d).toLocaleDateString('en-US', { month: 'short' }) : '' }
function formatDay(d) { return d ? new Date(d).getDate() : '' }

function onCategoryChange(val) { selectedCat.value = val; load(1) }
function onSearch(val) { search.value = val; load(1) }
function onDateFilterChange(val) { dateFilter.value = val; load(1) }

async function load(page = 1) {
  loading.value = true
  try {
    const params = { page }
    if (selectedCat.value) params.category = selectedCat.value
    if (search.value) params.search = search.value
    if (dateFilter.value) params.date_filter = dateFilter.value
    const { data } = await axios.get('/api/events', { params })
    events.value = data.data || data || []
    pagination.value = data.data ? {
      current_page: data.current_page,
      last_page: data.last_page,
      total: data.total,
    } : null
  } catch {
    events.value = []
  }
  loading.value = false
}

onMounted(() => load())
</script>
