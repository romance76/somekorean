<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <!-- 헤더 -->
      <div class="bg-gradient-to-r from-violet-600 to-violet-500 text-white px-6 py-6 rounded-2xl mb-4">
        <h1 class="text-xl font-black">❓ Q&A 게시판</h1>
        <p class="text-violet-100 text-sm mt-0.5">미국 한인 생활 질문과 답변</p>
      </div>

      <!-- 카테고리 탭 -->
      <div class="bg-white rounded-2xl shadow-sm overflow-hidden mb-4">
        <div class="flex overflow-x-auto border-b border-gray-100 px-2 py-2 gap-1">
          <button @click="activeCategory = ''" :class="tabClass('')" class="flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition">
            전체
          </button>
          <button v-for="cat in categories" :key="cat.id"
            @click="activeCategory = cat.key; loadPosts()"
            :class="tabClass(cat.key)" class="flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium transition">
            {{ cat.icon }} {{ cat.name }}
          </button>
        </div>

        <!-- 검색 + 글쓰기 -->
        <div class="flex gap-2 p-3">
          <input v-model="search" @keyup.enter="loadPosts" type="text" placeholder="질문 검색..."
            class="flex-1 border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-violet-400" />
          <button @click="loadPosts" class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-xl text-sm transition">검색</button>
          <button @click="$router.push('/qa/write')" class="bg-violet-500 hover:bg-violet-600 text-white px-4 py-2 rounded-xl text-sm font-semibold transition">
            + 질문하기
          </button>
        </div>
      </div>

      <!-- 글 목록 -->
      <div v-if="loading" class="text-center py-16 text-gray-400">불러오는 중...</div>
      <div v-else class="space-y-2">
        <div v-for="post in posts" :key="post.id"
          @click="$router.push('/qa/' + post.id)"
          class="bg-white rounded-2xl shadow-sm p-4 cursor-pointer hover:shadow-md transition flex gap-3">
          <!-- 상태 배지 -->
          <div class="flex-shrink-0 mt-0.5">
            <span :class="statusBadgeClass(post.status)" class="text-xs px-2 py-1 rounded-full font-medium">
              {{ statusLabel(post.status) }}
            </span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span v-if="post.category" class="text-xs px-2 py-0.5 rounded-full bg-violet-50 text-violet-700 font-medium">
                {{ post.category.icon }} {{ post.category.name }}
              </span>
              <span v-if="post.is_pinned" class="text-xs text-orange-500">📌</span>
            </div>
            <h3 class="font-semibold text-gray-800 text-sm leading-snug line-clamp-2 mb-1">{{ post.title }}</h3>
            <div class="flex items-center gap-3 text-xs text-gray-400">
              <span>{{ post.user?.name }}</span>
              <span>{{ timeAgo(post.created_at) }}</span>
              <span>조회 {{ post.view_count }}</span>
              <span class="text-blue-500 font-medium">답변 {{ post.answer_count }}</span>
            </div>
          </div>
        </div>
        <div v-if="posts.length === 0" class="text-center py-16 text-gray-400">
          <div class="text-4xl mb-3">❓</div>
          <div>게시글이 없습니다</div>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="totalPages > 1" class="flex justify-center gap-1 mt-6">
        <button v-for="p in totalPages" :key="p" @click="page = p; loadPosts()"
          :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition',
            page === p ? 'bg-violet-500 text-white' : 'bg-white text-gray-600 hover:bg-gray-50']">
          {{ p }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const categories = ref([])
const posts = ref([])
const loading = ref(false)
const activeCategory = ref('')
const search = ref('')
const page = ref(1)
const totalPages = ref(1)

function tabClass(key) {
  return activeCategory.value === key
    ? 'bg-violet-500 text-white'
    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
}

function statusLabel(s) {
  return { open: '미답변', solved: '해결', closed: '마감' }[s] || s
}

function statusBadgeClass(s) {
  if (s === 'solved') return 'bg-green-100 text-green-700'
  if (s === 'closed') return 'bg-gray-100 text-gray-500'
  return 'bg-blue-100 text-blue-700'
}

function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt)) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return Math.floor(diff/60) + '분 전'
  if (diff < 86400) return Math.floor(diff/3600) + '시간 전'
  return Math.floor(diff/86400) + '일 전'
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/qa/categories')
    categories.value = data
  } catch {}
}

async function loadPosts() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (activeCategory.value) params.category = activeCategory.value
    if (search.value) params.search = search.value
    const { data } = await axios.get('/api/qa', { params })
    posts.value = data.data || data
    totalPages.value = data.last_page || 1
  } catch { posts.value = [] }
  finally { loading.value = false }
}

onMounted(async () => {
  await loadCategories()
  await loadPosts()
})
</script>
