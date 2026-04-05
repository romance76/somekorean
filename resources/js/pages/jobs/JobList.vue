<template>
  <ListTemplate
    :title="locale === 'ko' ? '구인구직' : 'Jobs'"
    emoji="💼"
    :subtitle="locale === 'ko' ? '한인 채용 정보와 구직 공고' : 'Korean job listings'"
    :loading="loading"
    :items="jobs"
    :categories="categoryTabs"
    :activeCategory="activeCategory"
    :hasSearch="true"
    :searchQuery="search"
    :searchPlaceholder="locale === 'ko' ? '구인구직 검색...' : 'Search jobs...'"
    :sortOptions="sortOpts"
    :activeSort="sort"
    :hasViewToggle="true"
    :viewMode="viewMode"
    :hasWrite="true"
    writeTo="/jobs/write"
    :pagination="pagination"
    @category-change="onCatChange"
    @search="onSearch"
    @sort-change="onSortChange"
    @view-change="onViewChange"
    @page-change="onPageChange"
  >
    <template #header-right>
      <div class="flex items-center gap-2">
        <select v-model="typeFilter" @change="load(1)"
          class="text-xs border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-2 py-1.5 focus:outline-none">
          <option value="">{{ locale === 'ko' ? '전체 유형' : 'All Types' }}</option>
          <option value="full_time">{{ locale === 'ko' ? '풀타임' : 'Full-time' }}</option>
          <option value="part_time">{{ locale === 'ko' ? '파트타임' : 'Part-time' }}</option>
          <option value="contract">{{ locale === 'ko' ? '계약직' : 'Contract' }}</option>
        </select>
      </div>
    </template>

    <template #item-card="{ item }">
      <router-link :to="`/jobs/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 hover:shadow-md transition">
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span v-if="item.is_pinned" class="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-medium">
                {{ locale === 'ko' ? '상단' : 'Pinned' }}
              </span>
              <span v-if="item.job_type" class="text-[11px] px-2 py-0.5 rounded-full font-semibold" :class="jobTypeColor(item.job_type)">
                {{ jobTypeLabel(item.job_type) }}
              </span>
              <span v-if="item.is_urgent" class="text-xs bg-red-500 text-white px-1.5 py-0.5 rounded-full font-medium">
                {{ locale === 'ko' ? '급구' : 'Urgent' }}
              </span>
            </div>
            <h3 class="font-semibold text-gray-800 dark:text-white truncate text-sm">{{ item.title }}</h3>
            <div class="flex items-center flex-wrap gap-x-2 gap-y-1 text-xs text-gray-500 dark:text-gray-400 mt-1">
              <span>🏢 {{ item.company_name || (locale === 'ko' ? '비공개' : 'Private') }}</span>
              <span v-if="item.region">📍 {{ item.region }}</span>
            </div>
            <p v-if="item.salary_range" class="text-sm text-green-600 dark:text-green-400 font-medium mt-1">
              💰 {{ item.salary_range }}
            </p>
          </div>
          <div class="text-xs text-gray-400 flex-shrink-0 ml-3">{{ formatDate(item.created_at) }}</div>
        </div>
      </router-link>
    </template>

    <template #grid-card="{ item }">
      <router-link :to="`/jobs/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition p-4">
        <div class="flex items-center gap-2 mb-2">
          <span v-if="item.job_type" class="text-[11px] px-2 py-0.5 rounded-full font-semibold" :class="jobTypeColor(item.job_type)">
            {{ jobTypeLabel(item.job_type) }}
          </span>
          <span class="text-xs text-gray-400">{{ item.region }}</span>
        </div>
        <h3 class="font-bold text-gray-800 dark:text-white mb-1 line-clamp-2 text-sm">{{ item.title }}</h3>
        <p class="text-xs text-gray-500 dark:text-gray-400">{{ item.company_name }}</p>
        <p v-if="item.salary_range" class="text-sm text-green-600 dark:text-green-400 font-bold mt-2">{{ item.salary_range }}</p>
        <div class="flex items-center justify-between mt-2 text-xs text-gray-400">
          <span>{{ item.user?.name }}</span>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
      </router-link>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">💼</p>
        <p class="text-gray-400 text-sm">{{ locale === 'ko' ? '등록된 공고가 없습니다' : 'No job posts yet' }}</p>
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

const jobs = ref([])
const loading = ref(true)
const search = ref('')
const sort = ref('latest')
const activeCategory = ref('')
const typeFilter = ref('')
const viewMode = ref('list')
const pagination = ref(null)

const categoryTabs = computed(() => [
  { value: '', label: locale.value === 'ko' ? '전체' : 'All' },
  { value: 'IT', label: 'IT' },
  { value: '요식업', label: locale.value === 'ko' ? '요식업' : 'Restaurant' },
  { value: '건설', label: locale.value === 'ko' ? '건설' : 'Construction' },
  { value: '사무직', label: locale.value === 'ko' ? '사무직' : 'Office' },
  { value: '교육', label: locale.value === 'ko' ? '교육' : 'Education' },
  { value: '의료', label: locale.value === 'ko' ? '의료' : 'Medical' },
  { value: '기타', label: locale.value === 'ko' ? '기타' : 'Other' },
])

const sortOpts = computed(() => [
  { value: 'latest', label: locale.value === 'ko' ? '최신순' : 'Latest' },
  { value: 'popular', label: locale.value === 'ko' ? '인기순' : 'Popular' },
])

function jobTypeLabel(type) {
  const ko = locale.value === 'ko'
  return { full_time: ko ? '풀타임' : 'Full-time', part_time: ko ? '파트타임' : 'Part-time', contract: ko ? '계약직' : 'Contract', freelance: ko ? '프리랜서' : 'Freelance' }[type] ?? type
}

function jobTypeColor(type) {
  return { full_time: 'bg-blue-100 text-blue-700', part_time: 'bg-green-100 text-green-700', contract: 'bg-orange-100 text-orange-700', freelance: 'bg-purple-100 text-purple-700' }[type] ?? 'bg-gray-100 text-gray-600'
}

function formatDate(d) {
  if (!d) return ''
  const diff = (Date.now() - new Date(d).getTime()) / 1000
  if (diff < 86400) return locale.value === 'ko' ? '오늘' : 'Today'
  if (diff < 172800) return locale.value === 'ko' ? '어제' : 'Yesterday'
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
    if (typeFilter.value) params.type = typeFilter.value
    if (sort.value) params.sort = sort.value

    const { data } = await axios.get('/api/jobs', { params })
    jobs.value = data.data || []
    pagination.value = data.last_page > 1 ? { current_page: data.current_page, last_page: data.last_page } : null
  } catch { jobs.value = [] }
  loading.value = false
}

onMounted(() => load())
</script>
