<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">

    <!-- Sticky Header with Category Tabs -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-30">
      <div class="max-w-[1200px] mx-auto px-4 pt-3 pb-0">
        <h1 class="text-lg font-black text-gray-900 dark:text-white mb-3 flex items-center gap-2">
          <span>📰</span> {{ locale === 'ko' ? '뉴스' : 'News' }}
        </h1>

        <!-- Main Category Tabs -->
        <div class="flex overflow-x-auto gap-0 scrollbar-hide -mx-4 px-4">
          <button v-for="main in mainCategories" :key="main.id"
            @click="selectMain(main)"
            class="flex-shrink-0 px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-all border-b-2"
            :class="activeMain?.id === main.id
              ? 'text-blue-600 dark:text-blue-400 border-blue-600 font-bold'
              : 'text-gray-500 dark:text-gray-400 border-transparent hover:text-gray-800 dark:hover:text-gray-200'">
            {{ main.name }}
          </button>
        </div>
      </div>

      <!-- Sub Category Tabs -->
      <div v-if="activeMain && activeSubs.length" class="bg-gray-50 dark:bg-gray-900 border-t border-gray-100 dark:border-gray-700">
        <div class="max-w-[1200px] mx-auto flex overflow-x-auto gap-1 px-4 py-2 scrollbar-hide">
          <button @click="selectSub(null)"
            class="flex-shrink-0 px-3 py-1 text-xs rounded-full transition whitespace-nowrap"
            :class="!activeSub ? 'bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-800 font-semibold' : 'text-gray-500 hover:text-gray-700'">
            {{ locale === 'ko' ? '전체' : 'All' }}
          </button>
          <button v-for="sub in activeSubs" :key="sub.id"
            @click="selectSub(sub)"
            class="flex-shrink-0 px-3 py-1 text-xs rounded-full transition whitespace-nowrap"
            :class="activeSub?.id === sub.id
              ? 'bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-800 font-semibold'
              : 'text-gray-500 hover:text-gray-700'">
            {{ sub.name }}
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-[1200px] mx-auto px-4">

      <!-- Sort Options -->
      <div class="flex items-center justify-between mt-4 mb-3">
        <span class="text-xs text-gray-400">{{ total.toLocaleString() }} {{ locale === 'ko' ? '건' : 'articles' }}</span>
        <div class="flex gap-1">
          <button @click="loadNews()" class="text-xs px-2.5 py-1.5 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium">
            {{ locale === 'ko' ? '최신' : 'Latest' }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-16 text-gray-400">
        <div class="animate-spin w-8 h-8 border-2 border-gray-300 border-t-blue-500 rounded-full mx-auto mb-3"></div>
        <p class="text-sm">{{ locale === 'ko' ? '불러오는 중...' : 'Loading...' }}</p>
      </div>

      <template v-else>
        <!-- News List -->
        <div class="space-y-3 mt-2">
          <!-- Headline (first article) -->
          <div v-if="news.length" @click="openNews(news[0])"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition flex border border-gray-100 dark:border-gray-700">
            <div class="flex-shrink-0 bg-gray-100 dark:bg-gray-700" style="width:160px; min-height:120px">
              <img v-if="news[0].image_url" :src="news[0].image_url"
                class="w-full h-full object-cover" style="min-height:120px" @error="e => e.target.src=''" />
              <div v-else class="w-full h-full flex items-center justify-center text-4xl bg-gradient-to-br from-blue-400 to-purple-500" style="min-height:120px">📰</div>
            </div>
            <div class="flex-1 min-w-0 px-4 py-3">
              <div class="flex items-center gap-2 mb-1.5">
                <span v-if="news[0].category" class="text-[10px] text-blue-600 dark:text-blue-400 font-bold bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded-full">
                  {{ news[0].category }}
                </span>
                <span class="text-xs text-gray-400">{{ news[0].source }}</span>
              </div>
              <h2 class="font-bold text-sm text-gray-900 dark:text-white leading-snug line-clamp-2 mb-2">{{ news[0].title }}</h2>
              <p class="text-gray-400 text-[11px]">{{ timeAgo(news[0].published_at) }}</p>
            </div>
          </div>

          <!-- Rest of articles -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="item in news.slice(1)" :key="item.id"
              @click="openNews(item)"
              class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-3 flex gap-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition border border-gray-100 dark:border-gray-700">
              <div class="flex-shrink-0 w-20 h-16 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700">
                <img v-if="item.image_url" :src="item.image_url" class="w-full h-full object-cover" @error="e => e.target.src=''" />
                <div v-else class="w-full h-full flex items-center justify-center text-2xl bg-gradient-to-br from-blue-400 to-purple-500">📰</div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1 mb-1">
                  <span v-if="item.category" class="text-[10px] text-blue-600 dark:text-blue-400 font-semibold">{{ item.category }}</span>
                  <span v-if="item.source" class="text-gray-300 dark:text-gray-600 text-[10px]">· {{ item.source }}</span>
                </div>
                <h3 class="font-semibold text-gray-800 dark:text-gray-200 text-sm leading-snug line-clamp-2">{{ item.title }}</h3>
                <p class="text-gray-400 text-[11px] mt-1">{{ timeAgo(item.published_at) }}</p>
              </div>
            </div>
          </div>

          <!-- Empty -->
          <div v-if="!news.length" class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
            <p class="text-4xl mb-3">📰</p>
            <p class="text-gray-400 text-sm">{{ locale === 'ko' ? '뉴스가 없습니다' : 'No news articles' }}</p>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="lastPage > 1" class="flex justify-center items-center gap-2 mt-6 pb-4">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1"
            class="px-3 py-1.5 rounded-lg text-sm border border-gray-200 dark:border-gray-600 disabled:opacity-40 hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-600 dark:text-gray-300">
            {{ locale === 'ko' ? '이전' : 'Prev' }}
          </button>
          <template v-for="p in visiblePages" :key="p">
            <button v-if="p !== '...'" @click="changePage(p)"
              class="w-8 h-8 rounded-lg text-sm font-medium transition"
              :class="p === currentPage ? 'bg-blue-600 text-white' : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'">
              {{ p }}
            </button>
            <span v-else class="px-1 text-gray-400">...</span>
          </template>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage === lastPage"
            class="px-3 py-1.5 rounded-lg text-sm border border-gray-200 dark:border-gray-600 disabled:opacity-40 hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-600 dark:text-gray-300">
            {{ locale === 'ko' ? '다음' : 'Next' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const router = useRouter()
const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const mainCategories = ref([])
const activeMain = ref(null)
const activeSub = ref(null)
const activeSubs = computed(() => activeMain.value?.children ?? [])

const news = ref([])
const loading = ref(false)
const currentPage = ref(1)
const lastPage = ref(1)
const total = ref(0)

const visiblePages = computed(() => {
  const pages = []
  const t = lastPage.value
  const c = currentPage.value
  if (t <= 7) { for (let i = 1; i <= t; i++) pages.push(i); return pages }
  pages.push(1)
  if (c > 3) pages.push('...')
  for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) pages.push(i)
  if (c < t - 2) pages.push('...')
  pages.push(t)
  return pages
})

function timeAgo(dt) {
  if (!dt) return ''
  const diff = Date.now() - new Date(dt).getTime()
  const hrs = Math.floor(diff / 3600000)
  if (hrs < 1) return locale.value === 'ko' ? '방금 전' : 'Just now'
  if (hrs < 24) return `${hrs}${locale.value === 'ko' ? '시간 전' : 'h ago'}`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `${days}${locale.value === 'ko' ? '일 전' : 'd ago'}`
  return new Date(dt).toLocaleDateString('ko-KR')
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/news/categories')
    mainCategories.value = data
  } catch { mainCategories.value = [] }
}

async function loadNews() {
  loading.value = true
  try {
    const params = { per_page: 20, page: currentPage.value }
    let url = '/api/news'
    if (activeSub.value) url = `/api/news/category/${activeSub.value.slug}`
    else if (activeMain.value) url = `/api/news/category/${activeMain.value.slug}`

    const { data } = await axios.get(url, { params })
    news.value = data.data || []
    lastPage.value = data.last_page || 1
    total.value = data.total || 0
  } catch { news.value = [] }
  finally { loading.value = false }
}

function selectMain(main) {
  activeMain.value = activeMain.value?.id === main.id ? null : main
  activeSub.value = null
  currentPage.value = 1
  loadNews()
}

function selectSub(sub) {
  activeSub.value = sub
  currentPage.value = 1
  loadNews()
}

function changePage(p) {
  if (p < 1 || p > lastPage.value) return
  currentPage.value = p
  loadNews()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function openNews(item) {
  router.push(`/news/${item.id}`)
}

onMounted(async () => {
  await loadCategories()
  await loadNews()
})
</script>

<style scoped>
.scrollbar-hide { scrollbar-width: none; -ms-overflow-style: none; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
