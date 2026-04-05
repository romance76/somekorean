import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('68.183.60.70', username='root', password='EhdRh0817wodl')
sftp = client.open_sftp()

base = '/var/www/somekorean/resources/js/pages/community'

# ======== CommunityHome.vue ========
sftp.open(f'{base}/CommunityHome.vue', 'w').write(r'''<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">

    <!-- 상단 배너 -->
    <div class="bg-gradient-to-r from-red-500 to-pink-500 rounded-2xl px-6 py-6 mb-8 shadow-lg">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-white text-2xl font-black mb-1">💬 커뮤니티</h1>
          <p class="text-red-100 text-sm">자유롭게 소통하는 한인 커뮤니티</p>
        </div>
        <router-link
          to="/community/write"
          class="bg-white text-red-600 px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-red-50 transition flex items-center gap-1.5 shadow"
        >
          ✏️ 새 글쓰기
        </router-link>
      </div>
    </div>

    <!-- 3컬럼 레이아웃 -->
    <div class="flex gap-5">

      <!-- 좌측: 카테고리 사이드바 -->
      <aside class="hidden lg:block w-52 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 overflow-hidden sticky top-20">
          <h3 class="text-sm font-bold text-gray-700 px-4 py-3 border-b border-gray-100">📂 카테고리</h3>
          <ul>
            <li>
              <router-link
                to="/community"
                class="block w-full text-left px-4 py-2.5 text-sm transition"
                :class="!currentSlug ? 'bg-red-50 text-red-600 font-semibold border-l-2 border-red-500' : 'text-gray-600 hover:bg-gray-50'"
              >
                전체
              </router-link>
            </li>
            <li v-for="cat in categories" :key="cat.slug">
              <router-link
                :to="'/community/' + cat.slug"
                class="block w-full text-left px-4 py-2.5 text-sm transition"
                :class="currentSlug === cat.slug ? 'bg-red-50 text-red-600 font-semibold border-l-2 border-red-500' : 'text-gray-600 hover:bg-gray-50'"
              >
                {{ cat.icon }} {{ cat.name }}
              </router-link>
            </li>
          </ul>
        </div>
      </aside>

      <!-- 중앙: 글 목록 -->
      <main class="flex-1 min-w-0">
        <!-- 모바일 카테고리 -->
        <div class="lg:hidden mb-4">
          <select v-model="mobileCategory" @change="onMobileCategory" class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm">
            <option value="">전체 카테고리</option>
            <option v-for="cat in categories" :key="cat.slug" :value="cat.slug">{{ cat.icon }} {{ cat.name }}</option>
          </select>
        </div>

        <div v-if="loading" class="space-y-3">
          <div v-for="i in 5" :key="i" class="bg-white rounded-xl border border-gray-100 p-4 animate-pulse">
            <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-100 rounded w-1/2"></div>
          </div>
        </div>

        <div v-else-if="posts.length === 0" class="bg-white rounded-xl border border-gray-100 p-12 text-center">
          <p class="text-gray-400 text-sm">아직 게시글이 없습니다.</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="post in posts"
            :key="post.id"
            @click="goToPost(post)"
            class="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md hover:border-red-100 transition cursor-pointer"
          >
            <div class="flex items-start gap-3">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1.5">
                  <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                    :style="{ background: getCategoryColor(post.category_slug) + '20', color: getCategoryColor(post.category_slug) }">
                    {{ post.category_name || '일반' }}
                  </span>
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
        </div>
      </main>

      <!-- 우측: 인기글 사이드바 -->
      <aside class="hidden xl:block w-64 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 overflow-hidden sticky top-20">
          <h3 class="text-sm font-bold text-gray-700 px-4 py-3 border-b border-gray-100">🔥 인기글 TOP 10</h3>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const posts = ref([])
const popularPosts = ref([])
const categories = ref([])
const currentSlug = ref('')
const mobileCategory = ref('')

const categoryColors = {
  free: '#3B82F6', anonymous: '#8B5CF6', life: '#10B981', food: '#F59E0B',
  parenting: '#EC4899', health: '#06B6D4', finance: '#6366F1', immigration: '#EF4444',
  travel: '#14B8A6', hobby: '#F97316', tech: '#2563EB', humor: '#A855F7',
  news: '#DC2626', seniors: '#78716C', faith: '#7C3AED'
}

function getCategoryColor(slug) {
  return categoryColors[slug] || '#6B7280'
}

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
  router.push(`/community/${post.category_slug || 'free'}/${post.id}`)
}

function onMobileCategory() {
  if (mobileCategory.value) {
    router.push(`/community/${mobileCategory.value}`)
  } else {
    router.push('/community')
  }
}

async function fetchCategories() {
  try {
    const { data } = await axios.get('/api/community-v2/categories', { headers: getAuthHeaders() })
    categories.value = data.data || data || []
  } catch (e) {
    console.error('카테고리 로딩 실패', e)
  }
}

async function fetchPosts() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/community-v2/free/posts', {
      params: { sort: 'latest', per_page: 20 },
      headers: getAuthHeaders()
    })
    posts.value = data.data || data || []
  } catch (e) {
    console.error('글 목록 로딩 실패', e)
  } finally {
    loading.value = false
  }
}

async function fetchPopular() {
  try {
    const { data } = await axios.get('/api/community-v2/free/posts', {
      params: { sort: 'popular', per_page: 10 },
      headers: getAuthHeaders()
    })
    popularPosts.value = data.data || data || []
  } catch (e) {
    console.error('인기글 로딩 실패', e)
  }
}

onMounted(() => {
  fetchCategories()
  fetchPosts()
  fetchPopular()
})
</script>
''')

print('CommunityHome.vue written')

# ======== CommunityCategory.vue ========
sftp.open(f'{base}/CommunityCategory.vue', 'w').write(r'''<template>
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
''')

print('CommunityCategory.vue written')

# ======== CommunityPost.vue ========
sftp.open(f'{base}/CommunityPost.vue', 'w').write(r'''<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">

    <!-- 뉴스 스타일 헤더 -->
    <div class="bg-gradient-to-r from-red-500 to-pink-500 rounded-2xl px-6 py-6 mb-6 shadow-lg" v-if="post">
      <div class="flex items-center justify-between mb-4">
        <router-link :to="'/community/' + slug" class="text-white/80 hover:text-white text-sm transition flex items-center gap-1">
          ← {{ categoryInfo.name || slug }} 돌아가기
        </router-link>
        <div class="flex items-center gap-2">
          <span class="text-xs px-2.5 py-1 rounded-full bg-white/20 text-white font-medium">{{ categoryInfo.icon }} {{ categoryInfo.name }}</span>
          <button @click="sharePost" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition" title="공유">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
          </button>
          <button @click="bookmarkPost" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition" title="북마크">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/></svg>
          </button>
          <!-- 본인 글이면 수정/삭제 -->
          <template v-if="isOwner">
            <router-link :to="`/community/${slug}/${postId}/edit`" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition" title="수정">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
            </router-link>
            <button @click="deletePost" class="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition" title="삭제">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </template>
        </div>
      </div>
      <h1 class="text-white text-xl md:text-2xl font-black mb-3">{{ post.title }}</h1>
      <div class="flex items-center gap-3 text-white/70 text-sm">
        <span>{{ post.is_anonymous ? '🎭 익명' : (post.author_name || '알수없음') }}</span>
        <span>·</span>
        <span>{{ timeAgo(post.created_at) }}</span>
        <span>·</span>
        <span>👁 {{ post.views || 0 }}</span>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="loading" class="bg-white rounded-xl border border-gray-100 p-8 animate-pulse">
      <div class="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div class="h-4 bg-gray-100 rounded w-full mb-2"></div>
      <div class="h-4 bg-gray-100 rounded w-2/3"></div>
    </div>

    <!-- 2컬럼 -->
    <div v-else-if="post" class="flex gap-6">

      <!-- 좌측: 본문 -->
      <main class="flex-1 min-w-0">
        <!-- 본문 -->
        <div class="bg-white rounded-xl border border-gray-100 p-6 mb-4">
          <div class="prose prose-sm max-w-none text-gray-700 leading-relaxed" v-html="post.content"></div>
        </div>

        <!-- 작성자 정보 -->
        <div v-if="!post.is_anonymous && post.author" class="bg-white rounded-xl border border-gray-100 p-4 mb-4 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center text-red-500 font-bold text-sm">
            {{ (post.author_name || '?')[0] }}
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">{{ post.author_name }}</p>
            <p class="text-xs text-gray-400">{{ post.author?.bio || '한인 커뮤니티 멤버' }}</p>
          </div>
        </div>

        <!-- 좋아요 -->
        <div class="bg-white rounded-xl border border-gray-100 p-4 mb-6 flex items-center justify-center gap-3">
          <button
            @click="toggleLike"
            class="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition"
            :class="post.is_liked ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-500'"
          >
            ❤️ {{ post.is_liked ? '좋아요 취소' : '좋아요' }}
            <span class="ml-1">{{ post.likes_count || 0 }}</span>
          </button>
        </div>

        <!-- 댓글 -->
        <div class="bg-white rounded-xl border border-gray-100 p-6">
          <h3 class="text-sm font-bold text-gray-700 mb-4">💬 댓글 {{ comments.length }}개</h3>

          <!-- 댓글 작성 -->
          <div class="mb-6">
            <textarea
              v-model="newComment"
              rows="3"
              placeholder="댓글을 입력하세요..."
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-300 resize-none"
            ></textarea>
            <div class="flex justify-end mt-2">
              <button
                @click="submitComment()"
                :disabled="!newComment.trim()"
                class="bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-600 transition disabled:opacity-50"
              >
                등록
              </button>
            </div>
          </div>

          <!-- 댓글 목록 -->
          <div class="space-y-4">
            <div v-for="comment in topLevelComments" :key="comment.id">
              <div class="flex gap-3">
                <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 text-xs font-bold flex-shrink-0">
                  {{ (comment.is_anonymous ? '?' : (comment.author_name || '?')[0]) }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm font-bold text-gray-700">{{ comment.is_anonymous ? '🎭 익명' : (comment.author_name || '알수없음') }}</span>
                    <span class="text-xs text-gray-400">{{ timeAgo(comment.created_at) }}</span>
                  </div>
                  <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ comment.content }}</p>
                  <button
                    @click="replyTo = replyTo === comment.id ? null : comment.id"
                    class="text-xs text-gray-400 hover:text-red-500 mt-1 transition"
                  >
                    답글
                  </button>

                  <!-- 답글 입력 -->
                  <div v-if="replyTo === comment.id" class="mt-2">
                    <textarea
                      v-model="replyContent"
                      rows="2"
                      placeholder="답글을 입력하세요..."
                      class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-300 resize-none"
                    ></textarea>
                    <div class="flex justify-end gap-2 mt-1">
                      <button @click="replyTo = null" class="text-xs text-gray-400 hover:text-gray-600">취소</button>
                      <button
                        @click="submitComment(comment.id)"
                        :disabled="!replyContent.trim()"
                        class="bg-red-500 text-white px-3 py-1 rounded-lg text-xs font-bold hover:bg-red-600 transition disabled:opacity-50"
                      >
                        등록
                      </button>
                    </div>
                  </div>

                  <!-- 대댓글 -->
                  <div v-if="getReplies(comment.id).length" class="mt-3 space-y-3 pl-4 border-l-2 border-gray-100">
                    <div v-for="reply in getReplies(comment.id)" :key="reply.id" class="flex gap-2">
                      <div class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 text-[10px] font-bold flex-shrink-0">
                        {{ (reply.is_anonymous ? '?' : (reply.author_name || '?')[0]) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-0.5">
                          <span class="text-xs font-bold text-gray-600">{{ reply.is_anonymous ? '🎭 익명' : (reply.author_name || '알수없음') }}</span>
                          <span class="text-[10px] text-gray-400">{{ timeAgo(reply.created_at) }}</span>
                        </div>
                        <p class="text-xs text-gray-500 whitespace-pre-wrap">{{ reply.content }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="comments.length === 0" class="text-center text-gray-400 text-sm py-6">
            아직 댓글이 없습니다. 첫 댓글을 남겨보세요!
          </div>
        </div>
      </main>

      <!-- 우측: 사이드바 -->
      <aside class="hidden xl:block w-72 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 overflow-hidden sticky top-20">
          <h3 class="text-sm font-bold text-gray-700 px-4 py-3 border-b border-gray-100">📰 같은 카테고리 최신글</h3>
          <ul>
            <li v-for="item in relatedPosts" :key="item.id">
              <router-link
                :to="`/community/${slug}/${item.id}`"
                class="block px-4 py-3 hover:bg-gray-50 transition border-b border-gray-50"
              >
                <p class="text-xs font-medium text-gray-700 truncate">{{ item.title }}</p>
                <div class="flex items-center gap-2 mt-1 text-[10px] text-gray-400">
                  <span>{{ item.is_anonymous ? '익명' : (item.author_name || '') }}</span>
                  <span>{{ timeAgo(item.created_at) }}</span>
                </div>
              </router-link>
            </li>
          </ul>
          <div v-if="relatedPosts.length === 0" class="px-4 py-6 text-center text-xs text-gray-400">
            관련 글이 없습니다.
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
const post = ref(null)
const comments = ref([])
const relatedPosts = ref([])
const categoryInfo = ref({ name: '', icon: '' })
const categories = ref([])
const newComment = ref('')
const replyContent = ref('')
const replyTo = ref(null)

const slug = computed(() => route.params.slug)
const postId = computed(() => route.params.id)

const isOwner = computed(() => {
  if (!post.value) return false
  try {
    const token = localStorage.getItem('sk_token')
    if (!token) return false
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub == post.value.user_id
  } catch { return false }
})

const topLevelComments = computed(() => comments.value.filter(c => !c.parent_id))

function getReplies(parentId) {
  return comments.value.filter(c => c.parent_id === parentId)
}

function getAuthHeaders() {
  const token = localStorage.getItem('sk_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
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

function sharePost() {
  if (navigator.share) {
    navigator.share({ title: post.value.title, url: window.location.href })
  } else {
    navigator.clipboard.writeText(window.location.href)
    alert('링크가 복사되었습니다!')
  }
}

function bookmarkPost() {
  alert('북마크 기능은 준비 중입니다.')
}

async function fetchPost() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/community-v2/${slug.value}/posts/${postId.value}`, { headers: getAuthHeaders() })
    post.value = data.data || data
  } catch (e) {
    console.error('글 로딩 실패', e)
  } finally {
    loading.value = false
  }
}

async function fetchComments() {
  try {
    const { data } = await axios.get(`/api/community-v2/${slug.value}/posts/${postId.value}/comments`, { headers: getAuthHeaders() })
    comments.value = data.data || data || []
  } catch (e) {
    console.error('댓글 로딩 실패', e)
  }
}

async function fetchRelated() {
  try {
    const { data } = await axios.get(`/api/community-v2/${slug.value}/posts`, {
      params: { sort: 'latest', per_page: 5 },
      headers: getAuthHeaders()
    })
    relatedPosts.value = (data.data || data || []).filter(p => p.id != postId.value).slice(0, 5)
  } catch (e) {
    console.error('관련글 로딩 실패', e)
  }
}

async function fetchCategories() {
  try {
    const { data } = await axios.get('/api/community-v2/categories', { headers: getAuthHeaders() })
    categories.value = data.data || data || []
    const found = categories.value.find(c => c.slug === slug.value)
    if (found) categoryInfo.value = found
    else categoryInfo.value = { name: slug.value, icon: '📁' }
  } catch (e) {
    console.error('카테고리 로딩 실패', e)
  }
}

async function toggleLike() {
  try {
    await axios.post(`/api/community-v2/${slug.value}/posts/${postId.value}/like`, {}, { headers: getAuthHeaders() })
    post.value.is_liked = !post.value.is_liked
    post.value.likes_count = post.value.is_liked
      ? (post.value.likes_count || 0) + 1
      : Math.max(0, (post.value.likes_count || 0) - 1)
  } catch (e) {
    alert('로그인이 필요합니다.')
  }
}

async function submitComment(parentId = null) {
  const content = parentId ? replyContent.value : newComment.value
  if (!content.trim()) return
  try {
    await axios.post(`/api/community-v2/${slug.value}/posts/${postId.value}/comments`, {
      content: content.trim(),
      parent_id: parentId || undefined
    }, { headers: getAuthHeaders() })
    if (parentId) {
      replyContent.value = ''
      replyTo.value = null
    } else {
      newComment.value = ''
    }
    fetchComments()
  } catch (e) {
    alert('댓글 등록에 실패했습니다. 로그인이 필요합니다.')
  }
}

async function deletePost() {
  if (!confirm('정말 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/community-v2/${slug.value}/posts/${postId.value}`, { headers: getAuthHeaders() })
    router.push(`/community/${slug.value}`)
  } catch (e) {
    alert('삭제에 실패했습니다.')
  }
}

watch(() => route.params.id, () => {
  fetchPost()
  fetchComments()
  fetchRelated()
})

onMounted(() => {
  fetchCategories()
  fetchPost()
  fetchComments()
  fetchRelated()
})
</script>
''')

print('CommunityPost.vue written')

# ======== CommunityWrite.vue ========
sftp.open(f'{base}/CommunityWrite.vue', 'w').write(r'''<template>
  <div class="max-w-[800px] mx-auto px-4 py-6">

    <!-- 헤더 -->
    <div class="bg-gradient-to-r from-red-500 to-pink-500 rounded-2xl px-6 py-5 mb-6 shadow-lg">
      <h1 class="text-white text-xl font-black">{{ isEdit ? '✏️ 글 수정' : '✏️ 새 글쓰기' }}</h1>
      <p class="text-red-100 text-sm mt-1">커뮤니티에 글을 {{ isEdit ? '수정' : '작성' }}합니다</p>
    </div>

    <div class="bg-white rounded-xl border border-gray-100 p-6">
      <!-- 카테고리 선택 -->
      <div class="mb-4">
        <label class="block text-sm font-bold text-gray-700 mb-1.5">카테고리</label>
        <select
          v-model="form.category_slug"
          class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-300"
        >
          <option value="">카테고리를 선택하세요</option>
          <option v-for="cat in categories" :key="cat.slug" :value="cat.slug">
            {{ cat.icon }} {{ cat.name }}
          </option>
        </select>
      </div>

      <!-- 제목 -->
      <div class="mb-4">
        <label class="block text-sm font-bold text-gray-700 mb-1.5">제목</label>
        <input
          v-model="form.title"
          type="text"
          placeholder="제목을 입력하세요"
          class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-300"
          maxlength="200"
        />
      </div>

      <!-- 내용 -->
      <div class="mb-4">
        <label class="block text-sm font-bold text-gray-700 mb-1.5">내용</label>
        <textarea
          v-model="form.content"
          rows="12"
          placeholder="내용을 입력하세요..."
          class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-300 resize-none"
        ></textarea>
      </div>

      <!-- 익명 체크박스 -->
      <div class="mb-6">
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            v-model="form.is_anonymous"
            type="checkbox"
            class="w-4 h-4 rounded border-gray-300 text-red-500 focus:ring-red-300"
          />
          <span class="text-sm text-gray-600">🎭 익명으로 작성</span>
        </label>
        <p v-if="form.category_slug === 'anonymous'" class="text-xs text-gray-400 mt-1 ml-6">
          이 카테고리는 자동으로 익명 처리됩니다.
        </p>
      </div>

      <!-- 버튼 -->
      <div class="flex justify-end gap-3">
        <button
          @click="cancel"
          class="px-6 py-2.5 rounded-xl text-sm font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 transition"
        >
          취소
        </button>
        <button
          @click="submitPost"
          :disabled="submitting || !form.category_slug || !form.title.trim() || !form.content.trim()"
          class="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-red-500 hover:bg-red-600 transition disabled:opacity-50"
        >
          {{ submitting ? '처리 중...' : (isEdit ? '수정' : '등록') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const categories = ref([])
const submitting = ref(false)

const form = ref({
  category_slug: '',
  title: '',
  content: '',
  is_anonymous: false
})

const isEdit = computed(() => route.name === 'community-edit')
const editSlug = computed(() => route.params.slug)
const editId = computed(() => route.params.id)

function getAuthHeaders() {
  const token = localStorage.getItem('sk_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function fetchCategories() {
  try {
    const { data } = await axios.get('/api/community-v2/categories', { headers: getAuthHeaders() })
    categories.value = data.data || data || []
  } catch (e) {
    console.error('카테고리 로딩 실패', e)
  }
}

async function fetchPostForEdit() {
  if (!isEdit.value) return
  try {
    const { data } = await axios.get(`/api/community-v2/${editSlug.value}/posts/${editId.value}`, { headers: getAuthHeaders() })
    const p = data.data || data
    form.value.category_slug = p.category_slug || editSlug.value
    form.value.title = p.title
    form.value.content = p.content_raw || p.content || ''
    form.value.is_anonymous = !!p.is_anonymous
  } catch (e) {
    console.error('글 로딩 실패', e)
    alert('글을 불러올 수 없습니다.')
    router.push('/community')
  }
}

async function submitPost() {
  if (!form.value.category_slug || !form.value.title.trim() || !form.value.content.trim()) {
    alert('카테고리, 제목, 내용을 모두 입력해주세요.')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await axios.put(`/api/community-v2/${editSlug.value}/posts/${editId.value}`, {
        title: form.value.title,
        content: form.value.content,
        is_anonymous: form.value.is_anonymous
      }, { headers: getAuthHeaders() })
      router.push(`/community/${editSlug.value}/${editId.value}`)
    } else {
      const { data } = await axios.post(`/api/community-v2/${form.value.category_slug}/posts`, {
        title: form.value.title,
        content: form.value.content,
        is_anonymous: form.value.is_anonymous
      }, { headers: getAuthHeaders() })
      const newPost = data.data || data
      router.push(`/community/${form.value.category_slug}/${newPost.id}`)
    }
  } catch (e) {
    console.error('글 저장 실패', e)
    alert('저장에 실패했습니다. 로그인 상태를 확인해주세요.')
  } finally {
    submitting.value = false
  }
}

function cancel() {
  if (isEdit.value) {
    router.push(`/community/${editSlug.value}/${editId.value}`)
  } else {
    router.push('/community')
  }
}

// 익명 카테고리 자동 체크
watch(() => form.value.category_slug, (val) => {
  if (val === 'anonymous') {
    form.value.is_anonymous = true
  }
})

// URL 쿼리에서 카테고리 자동 선택
onMounted(() => {
  fetchCategories()
  if (route.query.category) {
    form.value.category_slug = route.query.category
  }
  if (isEdit.value) {
    fetchPostForEdit()
  }
})
</script>
''')

print('CommunityWrite.vue written')

sftp.close()
client.close()
print('All community Vue files deployed successfully!')
