<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">

    <!-- 헤더: 지식인 스타일 -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-500 rounded-2xl px-6 py-6 mb-6 shadow-lg">
      <h1 class="text-white text-xl font-black mb-1">❓ 지식인</h1>
      <p class="text-blue-100 text-sm mb-4">궁금한 건 뭐든 물어보세요! 미국 한인 생활 Q&A</p>
      <div class="flex gap-2">
        <div class="relative flex-1">
          <input v-model="search" type="text" placeholder="질문을 검색해보세요"
            class="w-full pl-10 pr-4 py-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
            @keyup.enter="doSearch" />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <button @click="doSearch" class="bg-white text-blue-600 px-5 py-3 rounded-xl text-sm font-semibold hover:bg-blue-50 transition">검색</button>
        <button @click="$router.push('/qa/write')" class="bg-yellow-400 text-gray-900 px-5 py-3 rounded-xl text-sm font-semibold hover:bg-yellow-300 transition flex items-center gap-1">
          ✏ 질문하기
        </button>
      </div>
    </div>

    <!-- 많이 본 Q&A (인기글) -->
    <section v-if="popularPosts.length" class="mb-6">
      <h2 class="text-base font-bold text-gray-800 mb-3">🔥 많이 본 Q&A</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <div v-for="(item, idx) in popularPosts.slice(0,6)" :key="item.id"
          class="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md transition cursor-pointer flex gap-3"
          @click="$router.push('/qa/' + item.id)">
          <span class="text-2xl font-extrabold text-blue-500 leading-none min-w-[28px]">{{ idx + 1 }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-gray-800 truncate">{{ item.title }}</p>
            <div class="flex items-center gap-3 mt-1 text-xs text-gray-400">
              <span>👁 {{ item.view_count || 0 }}</span>
              <span>💬 {{ item.answer_count || 0 }}</span>
              <span v-if="item.category" class="text-blue-500">{{ item.category.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 3단 레이아웃 -->
    <div class="flex gap-5">

      <!-- 왼쪽: 카테고리 사이드바 (데스크톱) -->
      <aside class="hidden lg:block w-44 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 overflow-hidden sticky top-20">
          <h3 class="text-xs font-bold text-gray-500 px-4 py-3 border-b border-gray-100 uppercase tracking-wide">카테고리</h3>
          <ul>
            <li>
              <button @click="selectCat(''); page=1; loadPosts()"
                class="w-full text-left px-4 py-2.5 text-sm transition"
                :class="activeCategory==='' ? 'bg-blue-50 text-blue-600 font-bold border-l-2 border-blue-500' : 'text-gray-600 hover:bg-gray-50'">
                📋 전체
              </button>
            </li>
            <li v-for="cat in categories" :key="cat.id">
              <button @click="selectCat(cat.key)"
                class="w-full text-left px-4 py-2.5 text-sm transition"
                :class="activeCategory===cat.key ? 'bg-blue-50 text-blue-600 font-bold border-l-2 border-blue-500' : 'text-gray-600 hover:bg-gray-50'">
                {{ cat.icon || '•' }} {{ cat.name }}
              </button>
            </li>
          </ul>
        </div>
      </aside>

      <!-- 모바일 카테고리 탭 -->
      <div class="lg:hidden w-full">
        <div class="flex overflow-x-auto gap-2 pb-2 mb-3" style="scrollbar-width:none">
          <button @click="selectCat(''); page=1; loadPosts()"
            class="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-medium transition flex-shrink-0"
            :class="activeCategory==='' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
            전체
          </button>
          <button v-for="cat in categories" :key="'m'+cat.id" @click="selectCat(cat.key)"
            class="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-medium transition flex-shrink-0"
            :class="activeCategory===cat.key ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
            {{ cat.icon || '' }} {{ cat.name }}
          </button>
        </div>
      </div>

      <!-- 중앙: 질문 목록 -->
      <main class="flex-1 min-w-0">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-gray-500">총 <strong class="text-gray-800">{{ totalCount.toLocaleString() }}</strong>개</span>
          <div class="flex items-center gap-2">
            <select v-model="sortOrder" @change="loadPosts()" class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 text-gray-600 focus:outline-none">
              <option value="latest">최신순</option>
              <option value="views">조회순</option>
              <option value="answers">답변순</option>
            </select>
          </div>
        </div>

        <!-- 로딩 -->
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 5" :key="i" class="bg-white rounded-xl border border-gray-100 p-4 animate-pulse">
            <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-100 rounded w-full mb-3"></div>
            <div class="h-3 bg-gray-100 rounded w-1/3"></div>
          </div>
        </div>

        <!-- 질문 카드 -->
        <div v-else class="space-y-2">
          <div v-for="post in posts" :key="post.id"
            class="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md transition cursor-pointer"
            @click="$router.push('/qa/' + post.id)">
            <div class="flex items-start gap-3">
              <!-- 답변 카운트 박스 -->
              <div class="flex-shrink-0 text-center min-w-[48px]">
                <div :class="post.answer_count > 0 ? 'bg-green-50 text-green-700 border-green-200' : 'bg-gray-50 text-gray-400 border-gray-200'"
                  class="border rounded-lg px-2 py-1">
                  <div class="text-lg font-bold leading-none">{{ post.answer_count || 0 }}</div>
                  <div class="text-[10px] mt-0.5">답변</div>
                </div>
              </div>
              <!-- 내용 -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1 flex-wrap">
                  <span v-if="post.category" class="text-[11px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 font-medium">
                    {{ post.category.icon || '' }} {{ post.category.name }}
                  </span>
                  <span v-if="post.status==='solved'" class="text-[11px] px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">✓ 해결</span>
                  <span v-if="post.is_pinned" class="text-[11px] text-orange-500">📌</span>
                </div>
                <h3 class="text-sm font-semibold text-gray-800 line-clamp-1 mb-1">{{ post.title }}</h3>
                <div class="flex items-center gap-3 text-xs text-gray-400">
                  <div class="flex items-center gap-1">
                    <div class="w-4 h-4 rounded-full bg-blue-100 flex items-center justify-center text-[9px] font-bold text-blue-600">
                      {{ (displayName(post.user)).charAt(0) }}
                    </div>
                    <span>{{ displayName(post.user) }}</span>
                  </div>
                  <span>{{ timeAgo(post.created_at) }}</span>
                  <span>👁 {{ post.view_count || 0 }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="!loading && posts.length===0" class="text-center py-16">
            <div class="text-5xl mb-3">🤔</div>
            <p class="text-gray-400 text-sm">등록된 질문이 없습니다.</p>
            <button @click="$router.push('/qa/write')" class="text-blue-500 text-sm mt-2 hover:underline">첫 번째 질문 작성하기 →</button>
          </div>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="totalPages > 1" class="flex justify-center gap-1 mt-5 flex-wrap">
          <button @click="goPage(page-1)" :disabled="page<=1" class="w-8 h-8 rounded-lg text-xs font-medium bg-white text-gray-500 border border-gray-200 hover:bg-gray-50 disabled:opacity-30">‹</button>
          <button v-for="p in pageRange" :key="p" @click="goPage(p)"
            class="w-8 h-8 rounded-lg text-xs font-medium transition"
            :class="page===p ? 'bg-blue-500 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'">
            {{ p }}
          </button>
          <button @click="goPage(page+1)" :disabled="page>=totalPages" class="w-8 h-8 rounded-lg text-xs font-medium bg-white text-gray-500 border border-gray-200 hover:bg-gray-50 disabled:opacity-30">›</button>
        </div>
      </main>

      <!-- 오른쪽: 랭킹 사이드바 (데스크톱) -->
      <aside class="hidden xl:block w-52 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 sticky top-20 mb-4">
          <h3 class="text-xs font-bold text-gray-500 px-4 py-3 border-b border-gray-100 uppercase tracking-wide">🏆 지식인 랭킹</h3>
          <ul class="py-1">
            <li v-for="(u, idx) in topUsers" :key="u.name"
              class="flex items-center gap-2.5 px-4 py-2.5 hover:bg-gray-50 transition">
              <span class="text-sm font-bold w-5 text-center leading-none">
                <template v-if="idx===0">🥇</template>
                <template v-else-if="idx===1">🥈</template>
                <template v-else-if="idx===2">🥉</template>
                <template v-else>{{ idx+1 }}</template>
              </span>
              <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                :style="{background: u.color}">{{ u.name.charAt(0) }}</div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-semibold text-gray-800 truncate">{{ u.name }}</p>
                <p class="text-[10px] text-gray-400">채택 {{ u.adopted }}회</p>
              </div>
            </li>
          </ul>
        </div>

        <!-- 빠른 카테고리 링크 -->
        <div class="bg-white rounded-xl border border-gray-100">
          <h3 class="text-xs font-bold text-gray-500 px-4 py-3 border-b border-gray-100">📂 인기 카테고리</h3>
          <div class="p-3 flex flex-wrap gap-1.5">
            <button v-for="cat in categories.slice(0,8)" :key="'s'+cat.id"
              @click="selectCat(cat.key)"
              class="text-[11px] px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-blue-50 hover:text-blue-600 transition font-medium">
              {{ cat.name }}
            </button>
          </div>
        </div>
      </aside>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const categories = ref([])
const posts = ref([])
const popularPosts = ref([])
const loading = ref(false)
const activeCategory = ref('')
const search = ref('')
const sortOrder = ref('latest')
const page = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

const topUsers = ref([
  { name: '미국한인생활', color: '#3B82F6', adopted: 142 },
  { name: '비빔밥마스터', color: '#8B5CF6', adopted: 98 },
  { name: '핫도그킹', color: '#EC4899', adopted: 76 },
  { name: '조지아주한인', color: '#F59E0B', adopted: 51 },
  { name: '텍사스한국인', color: '#10B981', adopted: 43 },
  { name: '뉴욕한인', color: '#EF4444', adopted: 38 },
  { name: '캘리포니아꿈', color: '#6366F1', adopted: 31 },
])

function displayName(user) {
  if (!user) return '익명'
  return user.nickname || user.username || '익명'
}

function selectCat(key) {
  activeCategory.value = key
  page.value = 1
  loadPosts()
}

function doSearch() {
  page.value = 1
  loadPosts()
}

function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt)) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return Math.floor(diff/60) + '분 전'
  if (diff < 86400) return Math.floor(diff/3600) + '시간 전'
  if (diff < 604800) return Math.floor(diff/86400) + '일 전'
  const d = new Date(dt)
  return `${d.getMonth()+1}/${d.getDate()}`
}

const pageRange = computed(() => {
  const start = Math.max(1, page.value - 4)
  const end = Math.min(totalPages.value, page.value + 4)
  return Array.from({length: end-start+1}, (_,i) => start+i)
})

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  loadPosts()
  window.scrollTo({top: 0, behavior: 'smooth'})
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/qa/categories')
    categories.value = data
  } catch {}
}

async function loadPopular() {
  try {
    const { data } = await axios.get('/api/qa', { params: { sort: 'views', per_page: 6 } })
    popularPosts.value = (data.data || data).slice(0, 6)
  } catch {}
}

async function loadPosts() {
  loading.value = true
  try {
    const params = { page: page.value, sort: sortOrder.value }
    if (activeCategory.value) params.category = activeCategory.value
    if (search.value.trim()) params.search = search.value.trim()
    const { data } = await axios.get('/api/qa', { params })
    posts.value = data.data || data
    totalPages.value = data.last_page || 1
    totalCount.value = data.total || posts.value.length
    page.value = data.current_page || page.value
  } catch { posts.value = [] }
  finally { loading.value = false }
}

onMounted(async () => {
  await loadCategories()
  await Promise.all([loadPopular(), loadPosts()])
})
</script>

<style scoped>
.line-clamp-1 { display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden; }
</style>
