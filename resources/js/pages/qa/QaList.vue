<template>
  <ListTemplate
    :title="locale === 'ko' ? '지식인 Q&A' : 'Q&A'"
    emoji="❓"
    :subtitle="locale === 'ko' ? '궁금한 건 뭐든 물어보세요! 미국 한인 생활 Q&A' : 'Ask anything about Korean-American life'"
    :totalCount="totalCount"
    :loading="loading"
    :items="posts"
    :categories="categoryTabs"
    :activeCategory="activeCategory"
    :hasSearch="true"
    :searchQuery="search"
    :searchPlaceholder="locale === 'ko' ? '질문을 검색해보세요' : 'Search questions...'"
    :sortOptions="sortOpts"
    :activeSort="sortOrder"
    :hasWrite="true"
    writeTo="/qa/write"
    :pagination="pagination"
    @category-change="onCatChange"
    @search="onSearch"
    @sort-change="onSortChange"
    @page-change="onPageChange"
  >
    <template #header-right>
      <div class="flex gap-1">
        <button v-for="f in statusFilters" :key="f.value"
          @click="statusFilter = f.value; loadPosts(1)"
          class="px-2.5 py-1.5 text-xs font-medium rounded-lg transition"
          :class="statusFilter === f.value ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300' : 'bg-white dark:bg-gray-700 text-gray-500 hover:bg-gray-100 border border-gray-200 dark:border-gray-600'">
          {{ f.label }}
        </button>
      </div>
    </template>

    <template #item-card="{ item }">
      <router-link :to="`/qa/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 hover:shadow-md transition">
        <div class="flex items-start gap-3">
          <!-- Answer Count Box -->
          <div class="flex-shrink-0 text-center min-w-[48px]">
            <div class="border rounded-lg px-2 py-1"
              :class="(item.answer_count || 0) > 0 ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-green-200 dark:border-green-700' : 'bg-gray-50 dark:bg-gray-700 text-gray-400 border-gray-200 dark:border-gray-600'">
              <div class="text-lg font-bold leading-none">{{ item.answer_count || 0 }}</div>
              <div class="text-[10px] mt-0.5">{{ locale === 'ko' ? '답변' : 'Answers' }}</div>
            </div>
          </div>
          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1 flex-wrap">
              <span v-if="item.category" class="text-[11px] px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-medium">
                {{ item.category.name || item.category }}
              </span>
              <span v-if="item.status === 'solved'" class="text-[11px] px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 font-medium">
                {{ locale === 'ko' ? '해결' : 'Solved' }}
              </span>
              <span v-if="item.point_reward > 0" class="text-[11px] px-2 py-0.5 rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 font-bold">
                {{ item.point_reward }}P
              </span>
            </div>
            <h3 class="text-sm font-semibold text-gray-800 dark:text-white line-clamp-1 mb-1">{{ item.title }}</h3>
            <div class="flex items-center gap-3 text-xs text-gray-400">
              <span>{{ item.user?.name || item.user?.nickname || (locale === 'ko' ? '익명' : 'Anonymous') }}</span>
              <span>{{ timeAgo(item.created_at) }}</span>
              <span>👁 {{ item.view_count || 0 }}</span>
            </div>
          </div>
        </div>
      </router-link>
    </template>

    <template #sidebar>
      <!-- Popular Q&A -->
      <div v-if="popularPosts.length" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden mb-4">
        <h3 class="text-xs font-bold text-gray-500 dark:text-gray-400 px-4 py-3 border-b border-gray-100 dark:border-gray-700">
          🔥 {{ locale === 'ko' ? '많이 본 Q&A' : 'Popular Q&A' }}
        </h3>
        <div>
          <router-link v-for="(p, idx) in popularPosts" :key="p.id" :to="`/qa/${p.id}`"
            class="flex gap-2.5 items-start px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition border-b border-gray-50 dark:border-gray-700 last:border-0">
            <span class="text-sm font-extrabold leading-none min-w-[20px]"
              :class="idx < 3 ? 'text-red-500' : 'text-gray-400'">{{ idx + 1 }}</span>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">{{ p.title }}</p>
              <p class="text-[10px] text-gray-400 mt-0.5">👁 {{ p.view_count || 0 }} · 💬 {{ p.answer_count || 0 }}</p>
            </div>
          </router-link>
        </div>
      </div>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">🤔</p>
        <p class="text-gray-400 text-sm">{{ locale === 'ko' ? '등록된 질문이 없습니다' : 'No questions yet' }}</p>
        <router-link to="/qa/write" class="text-blue-500 text-sm mt-2 inline-block hover:underline">
          {{ locale === 'ko' ? '첫 번째 질문 작성하기' : 'Ask the first question' }} →
        </router-link>
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

const posts = ref([])
const popularPosts = ref([])
const categories = ref([])
const loading = ref(false)
const search = ref('')
const sortOrder = ref('latest')
const activeCategory = ref('')
const statusFilter = ref('')
const totalCount = ref(0)
const pagination = ref(null)

const categoryTabs = computed(() => {
  const all = [{ value: '', label: locale.value === 'ko' ? '전체' : 'All' }]
  return all.concat(categories.value.map(c => ({ value: c.key || c.slug || c.id, label: c.name })))
})

const sortOpts = computed(() => [
  { value: 'latest', label: locale.value === 'ko' ? '최신순' : 'Latest' },
  { value: 'bounty', label: locale.value === 'ko' ? '현상금순' : 'Bounty' },
  { value: 'views', label: locale.value === 'ko' ? '인기순' : 'Popular' },
])

const statusFilters = computed(() => [
  { value: '', label: locale.value === 'ko' ? '전체' : 'All' },
  { value: 'unsolved', label: locale.value === 'ko' ? '미해결' : 'Unsolved' },
  { value: 'solved', label: locale.value === 'ko' ? '해결됨' : 'Solved' },
  { value: 'bounty', label: locale.value === 'ko' ? '현상금' : 'Bounty' },
])

function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt).getTime()) / 1000
  if (diff < 60) return locale.value === 'ko' ? '방금 전' : 'Just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}${locale.value === 'ko' ? '분 전' : 'm ago'}`
  if (diff < 86400) return `${Math.floor(diff / 3600)}${locale.value === 'ko' ? '시간 전' : 'h ago'}`
  if (diff < 604800) return `${Math.floor(diff / 86400)}${locale.value === 'ko' ? '일 전' : 'd ago'}`
  return new Date(dt).toLocaleDateString('ko-KR')
}

function onCatChange(val) { activeCategory.value = val; loadPosts(1) }
function onSearch(val) { search.value = val; loadPosts(1) }
function onSortChange(val) { sortOrder.value = val; loadPosts(1) }
function onPageChange(page) { loadPosts(page) }

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/qa/categories')
    categories.value = Array.isArray(data) ? data : data.data || []
  } catch { /* empty */ }
}

async function loadPopular() {
  try {
    const { data } = await axios.get('/api/qa', { params: { sort: 'views', per_page: 6 } })
    popularPosts.value = (data.data || data || []).slice(0, 6)
  } catch { /* empty */ }
}

async function loadPosts(page = 1) {
  loading.value = true
  try {
    const params = { page, sort: sortOrder.value, per_page: 20 }
    if (activeCategory.value) params.category = activeCategory.value
    if (search.value.trim()) params.search = search.value.trim()
    if (statusFilter.value) params.status = statusFilter.value

    const { data } = await axios.get('/api/qa', { params })
    posts.value = data.data || data || []
    totalCount.value = data.total || posts.value.length
    pagination.value = (data.last_page || 1) > 1 ? { current_page: data.current_page || page, last_page: data.last_page || 1 } : null
  } catch { posts.value = [] }
  finally { loading.value = false }
}

onMounted(async () => {
  await loadCategories()
  await Promise.all([loadPopular(), loadPosts()])
})
</script>
