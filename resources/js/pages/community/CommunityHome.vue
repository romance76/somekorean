<template>
  <ListTemplate
    :title="boardName"
    :emoji="boardIcon"
    :subtitle="boardDesc"
    :loading="loading"
    :items="posts"
    :categories="categoryTabs"
    :activeCategory="activeCategory"
    :hasSearch="true"
    :searchQuery="search"
    :searchPlaceholder="locale === 'ko' ? '게시글 검색...' : 'Search posts...'"
    :sortOptions="sortOptions"
    :activeSort="sort"
    :hasWrite="true"
    :writeTo="'/community/write?board=' + (currentSlug || '')"
    :pagination="pagination"
    @category-change="onCategoryChange"
    @search="onSearch"
    @sort-change="onSortChange"
    @page-change="onPageChange"
  >
    <template #item-card="{ item }">
      <router-link :to="`/community/${item.board_slug || currentSlug || 'free'}/${item.id}`"
        class="block bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 p-4 hover:shadow-md hover:border-blue-200 dark:hover:border-blue-700 transition">
        <div class="flex items-start gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span v-if="item.category_name" class="text-[11px] px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-medium">
                {{ item.category_name }}
              </span>
              <span v-if="item.is_pinned" class="text-[11px] text-orange-500 font-bold">📌</span>
            </div>
            <h3 class="text-sm font-semibold text-gray-800 dark:text-white truncate mb-1">{{ item.title }}</h3>
            <div class="flex items-center gap-3 text-xs text-gray-400">
              <span>{{ item.is_anonymous ? '🎭 익명' : (item.user?.name || item.author_name || '알수없음') }}</span>
              <span>❤️ {{ item.like_count || item.likes_count || 0 }}</span>
              <span>💬 {{ item.comment_count || item.comments_count || 0 }}</span>
              <span>👁 {{ item.view_count || item.views || 0 }}</span>
              <span>{{ formatTimeAgo(item.created_at) }}</span>
            </div>
          </div>
        </div>
      </router-link>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">📭</p>
        <p class="text-gray-400 text-sm">{{ locale === 'ko' ? '아직 게시글이 없습니다' : 'No posts yet' }}</p>
        <router-link :to="'/community/write?board=' + (currentSlug || '')"
          class="text-blue-500 text-sm mt-2 inline-block hover:underline">
          {{ locale === 'ko' ? '첫 글을 작성해보세요!' : 'Write the first post!' }}
        </router-link>
      </div>
    </template>

    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        <h3 class="text-sm font-bold text-gray-700 dark:text-gray-200 px-4 py-3 border-b border-gray-100 dark:border-gray-700">
          🔥 {{ locale === 'ko' ? '인기글' : 'Popular' }}
        </h3>
        <div v-if="popularPosts.length">
          <router-link v-for="(p, idx) in popularPosts" :key="p.id"
            :to="`/community/${p.board_slug || currentSlug || 'free'}/${p.id}`"
            class="flex gap-2.5 items-start px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition border-b border-gray-50 dark:border-gray-700 last:border-0">
            <span class="text-sm font-extrabold leading-none min-w-[20px]"
              :class="idx < 3 ? 'text-red-500' : 'text-gray-400'">{{ idx + 1 }}</span>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium text-gray-700 dark:text-gray-300 truncate">{{ p.title }}</p>
              <p class="text-[10px] text-gray-400 mt-0.5">👁 {{ p.view_count || p.views || 0 }} · 💬 {{ p.comment_count || p.comments_count || 0 }}</p>
            </div>
          </router-link>
        </div>
        <div v-else class="px-4 py-8 text-center text-xs text-gray-400">
          {{ locale === 'ko' ? '인기글이 없습니다' : 'No popular posts' }}
        </div>
      </div>
    </template>
  </ListTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLangStore } from '../../stores/lang'
import ListTemplate from '../../components/templates/ListTemplate.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const loading = ref(true)
const posts = ref([])
const popularPosts = ref([])
const categories = ref([])
const boardInfo = ref(null)
const search = ref('')
const sort = ref('latest')
const activeCategory = ref('')
const pagination = ref(null)

const currentSlug = computed(() => route.params.slug || '')
const boardName = computed(() => boardInfo.value?.name || (locale.value === 'ko' ? '커뮤니티' : 'Community'))
const boardIcon = computed(() => boardInfo.value?.icon || '💬')
const boardDesc = computed(() => boardInfo.value?.description || '')

const sortOptions = computed(() => [
  { value: 'latest', label: locale.value === 'ko' ? '최신순' : 'Latest' },
  { value: 'popular', label: locale.value === 'ko' ? '인기순' : 'Popular' },
])

const categoryTabs = computed(() => {
  const all = [{ value: '', label: locale.value === 'ko' ? '전체' : 'All' }]
  return all.concat(categories.value.map(c => ({ value: c.slug || c.key || c.id, label: c.name })))
})

function onCategoryChange(val) { activeCategory.value = val; loadPosts(1) }
function onSearch(val) { search.value = val; loadPosts(1) }
function onSortChange(val) { sort.value = val; loadPosts(1) }
function onPageChange(page) { loadPosts(page) }

function formatTimeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt).getTime()) / 1000
  if (diff < 60) return locale.value === 'ko' ? '방금 전' : 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}${locale.value === 'ko' ? '분 전' : 'm ago'}`
  if (diff < 86400) return `${Math.floor(diff / 3600)}${locale.value === 'ko' ? '시간 전' : 'h ago'}`
  if (diff < 604800) return `${Math.floor(diff / 86400)}${locale.value === 'ko' ? '일 전' : 'd ago'}`
  return new Date(dt).toLocaleDateString('ko-KR')
}

async function loadPosts(page = 1) {
  loading.value = true
  try {
    const params = { page, sort: sort.value, per_page: 20 }
    if (activeCategory.value) params.category = activeCategory.value
    if (search.value.trim()) params.search = search.value.trim()

    const slug = currentSlug.value
    const url = slug ? `/api/community-v2/${slug}/posts` : '/api/posts'
    const { data } = await axios.get(url, { params })

    posts.value = data.data || data || []
    pagination.value = data.last_page > 1 ? { current_page: data.current_page, last_page: data.last_page, total: data.total } : null
  } catch { posts.value = [] }
  finally { loading.value = false }
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/community-v2/categories')
    categories.value = data.data || data || []
  } catch { /* empty */ }
}

async function loadBoardInfo() {
  if (!currentSlug.value) return
  try {
    const { data } = await axios.get(`/api/boards/${currentSlug.value}`)
    boardInfo.value = data
  } catch { /* empty */ }
}

async function loadPopular() {
  try {
    const slug = currentSlug.value || 'free'
    const { data } = await axios.get(`/api/community-v2/${slug}/posts`, { params: { sort: 'popular', per_page: 10 } })
    popularPosts.value = (data.data || data || []).slice(0, 10)
  } catch { /* empty */ }
}

watch(() => route.params.slug, () => {
  activeCategory.value = ''
  search.value = ''
  loadBoardInfo()
  loadPosts(1)
  loadPopular()
})

onMounted(() => {
  loadCategories()
  loadBoardInfo()
  loadPosts(1)
  loadPopular()
})
</script>
