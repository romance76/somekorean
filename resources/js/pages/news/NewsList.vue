<template>
  <div class="min-h-screen bg-gray-50 pb-20">

    <!-- 헤더 -->
    <div class="bg-white border-b sticky top-0 z-30">
      <div class="max-w-[1200px] mx-auto px-4 pt-3 pb-0">
        <h1 class="text-lg font-black text-gray-900 mb-3">뉴스</h1>

        <!-- 메인 카테고리 탭 (가로 스크롤) -->
        <div class="flex overflow-x-auto gap-0 hide-scrollbar -mx-4 px-4">
          <button
            v-for="main in mainCategories"
            :key="main.id"
            @click="selectMain(main)"
            class="flex-shrink-0 px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-all border-b-2"
            :class="activeMain?.id === main.id
              ? 'text-[#D00000] border-[#D00000] font-bold'
              : 'text-gray-500 border-transparent hover:text-gray-800'"
          >
            {{ main.name }}
          </button>
        </div>
      </div>

      <!-- 서브 카테고리 (선택된 메인 카테고리의 하위) -->
      <div v-if="activeMain && activeSubs.length" class="bg-gray-50 border-t">
        <div class="max-w-[1200px] mx-auto flex overflow-x-auto gap-1 px-4 py-2 hide-scrollbar">
          <button
            @click="selectSub(null)"
            class="flex-shrink-0 px-3 py-1 text-xs rounded-full transition whitespace-nowrap"
            :class="!activeSub ? 'bg-gray-800 text-white font-semibold' : 'text-gray-500 hover:text-gray-700'"
          >
            전체
          </button>
          <button
            v-for="sub in activeSubs"
            :key="sub.id"
            @click="selectSub(sub)"
            class="flex-shrink-0 px-3 py-1 text-xs rounded-full transition whitespace-nowrap"
            :class="activeSub?.id === sub.id
              ? 'bg-gray-800 text-white font-semibold'
              : 'text-gray-500 hover:text-gray-700'"
          >
            {{ sub.name }}
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-[1200px] mx-auto px-4">

      <!-- 일일 다이제스트 섹션 (메인 카테고리 선택 전 / 전체일 때) -->
      <div v-if="!activeMain && digestNews.length" class="mt-4">
        <div class="bg-gray-100 rounded-2xl p-4">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-red-600 font-black text-sm">오늘의 주요 뉴스</span>
            <span class="text-gray-400 text-xs">{{ todayDateStr }}</span>
          </div>

          <!-- 주요 뉴스 카드 3개 -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div
              v-for="item in digestNews.slice(0, 3)"
              :key="item.id"
              @click="openNews(item)"
              class="bg-white rounded-xl overflow-hidden cursor-pointer hover:shadow-md transition"
            >
              <div class="aspect-[16/9] bg-gray-200 overflow-hidden">
                <img
                  v-if="item.image_url"
                  :src="item.image_url"
                  class="w-full h-full object-cover"
                  @error="item.image_url = null"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-3xl bg-gray-100">
                  📰
                </div>
              </div>
              <div class="p-3">
                <span v-if="item.category" class="text-[10px] text-[#D00000] font-semibold">{{ item.category }}</span>
                <h3 class="text-sm font-bold text-gray-900 leading-snug line-clamp-2 mt-0.5">{{ item.title }}</h3>
                <p class="text-xs text-gray-400 mt-1">{{ timeAgo(item.published_at) }}</p>
              </div>
            </div>
          </div>

          <!-- 어제 뉴스 요약 텍스트 -->
          <div v-if="yesterdayNews.length" class="mt-3 pt-3 border-t border-gray-200">
            <p class="text-xs text-gray-500 font-semibold mb-2">어제 주요 뉴스</p>
            <div class="space-y-1.5">
              <div
                v-for="item in yesterdayNews.slice(0, 4)"
                :key="'y-' + item.id"
                @click="openNews(item)"
                class="flex items-start gap-2 cursor-pointer group"
              >
                <span class="text-[#D00000] text-xs mt-0.5 flex-shrink-0">▸</span>
                <p class="text-xs text-gray-600 group-hover:text-gray-900 line-clamp-1">{{ item.title }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="text-center py-16 text-gray-400">
        <div class="animate-spin w-8 h-8 border-2 border-gray-300 border-t-[#D00000] rounded-full mx-auto mb-3"></div>
        불러오는 중...
      </div>

      <template v-else>
        <!-- 뉴스 목록 -->
        <div class="mt-4">
          <!-- 상단 첫 번째 뉴스 (헤드라인) -->
          <div
            v-if="news.length"
            @click="openNews(news[0])"
            class="bg-white rounded-xl shadow-sm overflow-hidden mb-3 cursor-pointer hover:shadow-md transition flex"
          >
            <div class="flex-shrink-0 bg-gray-100" style="width:160px; min-height:120px">
              <img
                v-if="news[0].image_url"
                :src="news[0].image_url"
                class="w-full h-full object-cover"
                style="min-height:120px"
                @error="news[0].image_url = null"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-4xl" style="min-height:120px">📰</div>
            </div>
            <div class="flex-1 min-w-0 px-4 py-3">
              <div class="flex items-center gap-2 mb-1.5">
                <span v-if="news[0].category" class="text-[10px] text-[#D00000] font-bold bg-red-50 px-2 py-0.5 rounded-full">
                  {{ news[0].category }}
                </span>
                <span class="text-xs text-gray-400">{{ news[0].source }}</span>
              </div>
              <h2 class="font-bold text-[15px] text-gray-900 leading-snug line-clamp-3 mb-2">{{ news[0].title }}</h2>
              <p v-if="cleanSummary(news[0].summary)" class="text-gray-500 text-xs line-clamp-2">
                {{ cleanSummary(news[0].summary) }}
              </p>
              <p class="text-gray-400 text-[11px] mt-1.5">{{ timeAgo(news[0].published_at) }}</p>
            </div>
          </div>

          <!-- 나머지 뉴스 2컬럼 그리드 -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div
              v-for="item in news.slice(1)"
              :key="item.id"
              @click="openNews(item)"
              class="bg-white rounded-xl shadow-sm p-3 flex gap-3 cursor-pointer hover:bg-gray-50 transition"
            >
              <div class="flex-shrink-0 w-20 h-16 rounded-lg overflow-hidden bg-gray-100">
                <img
                  v-if="item.image_url"
                  :src="item.image_url"
                  class="w-full h-full object-cover"
                  @error="item.image_url = null"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-2xl">📰</div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1 mb-1">
                  <span v-if="item.category" class="text-[10px] text-[#D00000] font-semibold">{{ item.category }}</span>
                  <span v-if="item.source" class="text-gray-300 text-[10px]">· {{ item.source }}</span>
                </div>
                <h3 class="font-semibold text-gray-800 text-sm leading-snug line-clamp-2">{{ item.title }}</h3>
                <p class="text-gray-400 text-[11px] mt-1">{{ timeAgo(item.published_at) }}</p>
              </div>
            </div>
          </div>

          <div v-if="!news.length" class="text-center py-16 text-gray-400">
            뉴스가 없습니다.
          </div>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="lastPage > 1" class="flex justify-center items-center gap-2 mt-6 pb-4">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-1.5 rounded-lg text-sm border disabled:opacity-40 hover:bg-gray-100 transition"
          >
            이전
          </button>
          <template v-for="p in visiblePages" :key="p">
            <button
              v-if="p !== '...'"
              @click="changePage(p)"
              class="w-8 h-8 rounded-lg text-sm font-medium transition"
              :class="p === currentPage ? 'bg-[#D00000] text-white' : 'hover:bg-gray-100 text-gray-600'"
            >
              {{ p }}
            </button>
            <span v-else class="px-1 text-gray-400">...</span>
          </template>
          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === lastPage"
            class="px-3 py-1.5 rounded-lg text-sm border disabled:opacity-40 hover:bg-gray-100 transition"
          >
            다음
          </button>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route  = useRoute()

// ── 카테고리 상태 ──────────────────────────────────────────────
const mainCategories = ref([])
const activeMain     = ref(null)
const activeSub      = ref(null)

const activeSubs = computed(() => activeMain.value?.children ?? [])

// ── 뉴스 상태 ──────────────────────────────────────────────────
const news        = ref([])
const loading     = ref(false)
const currentPage = ref(1)
const lastPage    = ref(1)
const total       = ref(0)

// ── 다이제스트 ────────────────────────────────────────────────
const digestNews   = ref([])
const yesterdayNews = ref([])
const todayDateStr  = ref('')

// ── 페이지네이션 (최대 7개 버튼) ─────────────────────────────
const visiblePages = computed(() => {
  const pages = []
  const total = lastPage.value
  const cur   = currentPage.value
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cur > 3) pages.push('...')
    const start = Math.max(2, cur - 1)
    const end   = Math.min(total - 1, cur + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (cur < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

// ── 카테고리 로드 ─────────────────────────────────────────────
async function loadCategories() {
  try {
    const { data } = await axios.get('/api/news/categories')
    mainCategories.value = data
  } catch {
    mainCategories.value = []
  }
}

// ── 다이제스트 로드 ───────────────────────────────────────────
async function loadDigest() {
  try {
    const { data } = await axios.get('/api/news/digest')
    digestNews.value   = data.today    ?? []
    yesterdayNews.value = data.yesterday ?? []
    todayDateStr.value  = formatDate(data.date)
  } catch {
    digestNews.value = []
  }
}

// ── 뉴스 로드 ────────────────────────────────────────────────
async function loadNews() {
  loading.value = true
  try {
    const params = { per_page: 20, page: currentPage.value }

    if (activeSub.value) {
      // 서브카테고리 선택 시
      const { data } = await axios.get(`/api/news/category/${activeSub.value.slug}`, { params })
      news.value  = data.data
      lastPage.value = data.last_page
      total.value    = data.total
    } else if (activeMain.value) {
      // 메인카테고리 선택 시
      const { data } = await axios.get(`/api/news/category/${activeMain.value.slug}`, { params })
      news.value  = data.data
      lastPage.value = data.last_page
      total.value    = data.total
    } else {
      // 전체
      const { data } = await axios.get('/api/news', { params })
      news.value  = data.data
      lastPage.value = data.last_page
      total.value    = data.total
    }
  } catch {
    news.value = []
  } finally {
    loading.value = false
  }
}

// ── 카테고리 선택 ─────────────────────────────────────────────
function selectMain(main) {
  if (activeMain.value?.id === main.id) {
    // 같은 탭 클릭 시 해제
    activeMain.value = null
    activeSub.value  = null
  } else {
    activeMain.value = main
    activeSub.value  = null
  }
  currentPage.value = 1
  loadNews()
}

function selectSub(sub) {
  activeSub.value   = sub
  currentPage.value = 1
  loadNews()
}

function changePage(p) {
  if (p < 1 || p > lastPage.value) return
  currentPage.value = p
  loadNews()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ── 뉴스 열기 ────────────────────────────────────────────────
function openNews(item) {
  router.push('/news/' + item.id)
}

// ── 유틸 ─────────────────────────────────────────────────────
function timeAgo(dt) {
  if (!dt) return ''
  const diff = Date.now() - new Date(dt).getTime()
  const hrs  = Math.floor(diff / 3600000)
  if (hrs < 1) return '방금 전'
  if (hrs < 24) return `${hrs}시간 전`
  const days = Math.floor(hrs / 24)
  if (days < 30) return `${days}일 전`
  return `${Math.floor(days / 30)}개월 전`
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}월 ${d.getDate()}일`
}

function cleanSummary(text) {
  if (!text) return ''
  let t = text
  t = t.replace(/^[\s\S]*?기사를\s*읽어드립니다[\s\S]*?\d+:\d+\s*/m, '')
  t = t.replace(/기사를\s*읽어드립니다/g, '')
  t = t.replace(/Your browser does not support\s*the?\s*audio element\.?/gi, '')
  t = t.replace(/[가-힣]{1,10}기자\s*수정\s*\d{4}[-./]\d{2}[-./]\d{2}[\s\S]*?등록\s*\d{4}[-./]\d{2}[-./]\d{2}\s*\d{2}:\d{2}\s*/g, '')
  t = t.replace(/수정\s*\d{4}[-./]\d{2}[-./]\d{2}[\s\S]*?등록\s*\d{4}[-./]\d{2}[-./]\d{2}\s*\d{2}:\d{2}\s*/g, '')
  t = t.replace(/^본문[가-힣\s]{2,40}/g, '')
  t = t.replace(/(?<![가-힣])광고(?![가-힣])/g, '')
  t = t.replace(/^\s*\d+:\d{2}\s*/g, '')
  t = t.trim()
  if (t.length > 100) t = t.slice(0, 100) + '...'
  return t
}

// ── 초기화 ───────────────────────────────────────────────────
onMounted(async () => {
  await loadCategories()
  await Promise.all([loadNews(), loadDigest()])
})
</script>

<style scoped>
.hide-scrollbar {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
