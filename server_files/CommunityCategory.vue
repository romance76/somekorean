<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">

    <!-- 상단 배너 -->
    <div class="rounded-2xl px-6 py-6 mb-8 shadow-lg"
      :style="{ background: `linear-gradient(135deg, ${bannerColor}, ${bannerColorEnd})` }">
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <router-link to="/community" class="text-white/80 hover:text-white text-sm transition">← 전체</router-link>
          </div>
          <h1 class="text-white text-2xl font-black mb-1">{{ categoryInfo.icon }} {{ categoryInfo.name }}</h1>
          <p class="text-white/80 text-sm">{{ categoryInfo.description || '' }}</p>
        </div>
        <router-link
          :to="'/community/write?category=' + slug"
          class="bg-white/20 backdrop-blur text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-white/30 transition flex items-center gap-1.5"
        >
          ✏️ 글쓰기
        </router-link>
      </div>
    </div>

    <!-- 정렬 탭 -->
    <div class="flex items-center gap-2 mb-4">
      <button
        v-for="s in sortOptions"
        :key="s.value"
        @click="currentSort = s.value; fetchPosts()"
        class="px-4 py-1.5 rounded-full text-sm font-medium transition"
        :class="currentSort === s.value
          ? 'bg-red-500 text-white'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
      >
        {{ s.label }}
      </button>
    </div>

    <!-- 3컬럼 -->
    <div class="flex gap-5">

      <!-- 좌측: 카테고리 사이드바 -->
      <aside class="hidden lg:block w-52 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 overflow-hidden sticky top-20">
          <h3 class="text-sm font-bold text-gray-700 px-4 py-3 border-b border-gray-100">📂 카테고리</h3>
          <ul>
            <li>
              <router-link
                to="/community"
                class="block w-full text-left px-4 py-2.5 text-sm text-gray-600 hover:bg-gray-50 transition"
              >
                전체
              </router-link>
            </li>
            <li v-for="cat in categories" :key="cat.slug">
              <router-link
                :to="'/community/' + cat.slug"
                class="block w-full text-left px-4 py-2.5 text-sm transition"
                :class="slug === cat.slug ? 'bg-red-50 text-red-600 font-semibold border-l-2 border-red-500' : 'text-gray-600 hover:bg-gray-50'"
              >
                {{ cat.icon }} {{ cat.name }}
              </router-link>
            </li>
          </ul>
        </div>
      </aside>

      <!-- 중앙: 글 목록 -->
      <main class="flex-1 min-w-0">
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 5" :key="i" class="bg-white rounded-xl border border-gray-100 p-4 animate-pulse">
            <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-100 rounded w-1/2"></div>
          </div>
        </div>

        <div v-else-if="posts.length === 0" class="bg-white rounded-xl border border-gray-100 p-12 text-center">
          <p class="text-gray-400 text-sm">이 카테고리에 게시글이 없습니다.</p>
          <router-link :to="'/community/write?category=' + slug" class="text-red-500 text-sm mt-2 inline-block hover:underline">첫 글을 작성해보세요!</router-link>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="post in posts"
            :key="post.id"
            @click="goToPost(post)"
            class="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md hover:border-red-100 transition cursor-pointer"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1.5">
                <span v-if="post.is_pinned" class="text-xs text-orange-500 font-bold">📌 고정</span>
              </div>
              <h3 class="text-sm font-bold text-gray-800 truncate mb-1">{{ post.title }}</h3>
              <p class="text-xs text-gray-400 line-clamp-1 mb-2">{{ stripHtml(post.content) }}</p>
              <div class="flex items-center gap-3 text-xs text-gray-400">
                <span>{{ post.is_anonymous ? '🎭 익명' : (post.author_name || '알수없음') }}</span>
                <span>❤️ {{ post.likes_count || 0 }}</span>
                <span>💬 {{ post.comments_count || 0 }}</span>
                <span>👁 {{ post.views || 0 }}</span>
                <span>{{ timeAgo(post.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="totalPages > 1" class="flex justify-center gap-1 mt-8">
          <button
            v-for="p in paginationRange"
            :key="p"
            @click="currentPage = p; fetchPosts()"
            class="w-9 h-9 rounded-lg text-sm font-medium transition"
            :class="currentPage === p ? 'bg-red-500 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'"
          >
            {{ p }}
          </button>
        </div>
      </main>

      <!-- 우측: 인기글 사이드바 -->
      <aside class="hidden xl:block w-64 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 overflow-hidden sticky top-20">
          <h3 class="text-sm font-bold text-gray-700 px-4 py-3 border-b border-gray-100">🔥 이 카테고리 인기글</h3>
          <ul>
            <li v-for="(item, idx) in popularPosts" :key="item.id">
              <div
                @click="goToPost(item)"
                class="px-4 py-2.5 hover:bg-gray-50 cursor-pointer transition flex gap-2.5 items-start"
              >
                <span class="text-sm font-extrabold leading-none min-w-[20px]"
                  :class="idx < 3 ? 'text-red-500' : 'text-gray-400'">{{ idx + 1 }}</span>
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium text-gray-700 truncate">{{ item.title }}</p>
                  <p class="text-[10px] text-gray-400 mt-0.5">👁 {{ item.views }} · 💬 {{ item.comments_count || 0 }}</p>
                </div>
              </div>
            </li>
          </ul>
          <div v-if="popularPosts.length === 0" class="px-4 py-6 text-center text-xs text-gray-400">
            인기글이 없습니다.
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const posts = ref([])
const popularPosts = ref([])
const categories = ref([])
const categoryInfo = ref({ name: '', icon: '', description: '' })
const currentSort = ref('latest')
const currentPage = ref(1)
const totalPages = ref(1)

const slug = computed(() => route.params.slug)

const sortOptions = [
  { label: '최신순', value: 'latest' },
  { label: '인기순', value: 'popular' },
]

const categoryColorMap = {
  free: ['#3B82F6','#60A5FA'], anonymous: ['#8B5CF6','#A78BFA'], life: ['#10B981','#34D399'],
  food: ['#F59E0B','#FBBF24'], parenting: ['#EC4899','#F472B6'], health: ['#06B6D4','#22D3EE'],
  finance: ['#6366F1','#818CF8'], immigration: ['#EF4444','#F87171'], travel: ['#14B8A6','#2DD4BF'],
  hobby: ['#F97316','#FB923C'], tech: ['#2563EB','#3B82F6'], humor: ['#A855F7','#C084FC'],
  news: ['#DC2626','#EF4444'], seniors: ['#78716C','#A8A29E'], faith: ['#7C3AED','#8B5CF6']
}

const bannerColor = computed(() => (categoryColorMap[slug.value] || ['#EF4444','#EC4899'])[0])
const bannerColorEnd = computed(() => (categoryColorMap[slug.value] || ['#EF4444','#EC4899'])[1])

const paginationRange = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, start + 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

function getAuthHeaders() {
  const token = localStorage.getItem('sk_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function stripHtml(html) {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '').substring(0, 100)
}

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now - date) / 1000)
  if (diff < 60) return '방금 전'
  if (diff < 3600) return Math.floor(diff / 60) + '분 전'
  if (diff < 86400) return Math.floor(diff / 3600) + '시간 전'
  if (diff < 172800) return '어제'
  if (diff < 604800) return Math.floor(diff / 86400) + '일 전'
  return date.toLocaleDateString('ko-KR')
}

function goToPost(post) {
  router.push(`/community/${slug.value}/${post.id}`)
}

async function fetchCategories() {
  try {
    const { data } = await axios.get('/api/community-v2/categories', { headers: getAuthHeaders() })
    categories.value = data.data || data || []
    const found = categories.value.find(c => c.slug === slug.value)
    if (found) categoryInfo.value = found
    else categoryInfo.value = { name: slug.value, icon: '📁', description: '' }
  } catch (e) {
    console.error('카테고리 로딩 실패', e)
  }
}

async function fetchPosts() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/community-v2/${slug.value}/posts`, {
      params: { sort: currentSort.value, page: currentPage.value, per_page: 20 },
      headers: getAuthHeaders()
    })
    posts.value = data.data || data || []
    if (data.meta) {
      totalPages.value = data.meta.last_page || 1
    } else if (data.last_page) {
      totalPages.value = data.last_page || 1
    }
  } catch (e) {
    console.error('글 목록 로딩 실패', e)
  } finally {
    loading.value = false
  }
}

async function fetchPopular() {
  try {
    const { data } = await axios.get(`/api/community-v2/${slug.value}/posts`, {
      params: { sort: 'popular', per_page: 5 },
      headers: getAuthHeaders()
    })
    popularPosts.value = data.data || data || []
  } catch (e) {
    console.error('인기글 로딩 실패', e)
  }
}

watch(() => route.params.slug, () => {
  currentPage.value = 1
  currentSort.value = 'latest'
  fetchCategories()
  fetchPosts()
  fetchPopular()
})

onMounted(() => {
  fetchCategories()
  fetchPosts()
  fetchPopular()
})
</script>
