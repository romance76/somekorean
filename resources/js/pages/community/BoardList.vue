<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-black text-gray-800">💬 커뮤니티</h1>
      <div class="flex items-center gap-2">
        <button @click="viewMode='list'" class="p-1.5 rounded" :class="viewMode==='list'?'bg-amber-100 text-amber-700':'text-gray-400'">☰</button>
        <button @click="viewMode='card'" class="p-1.5 rounded" :class="viewMode==='card'?'bg-amber-100 text-amber-700':'text-gray-400'">⊞</button>
        <RouterLink v-if="auth.isLoggedIn" to="/community/write" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm hover:bg-amber-500">✏️ 글쓰기</RouterLink>
      </div>
    </div>

    <div class="grid grid-cols-12 gap-4">
      <!-- 왼쪽: 게시판 카테고리 -->
      <div class="col-span-12 lg:col-span-2 hidden lg:block">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden sticky top-20">
          <div class="px-3 py-2.5 border-b font-bold text-xs text-amber-900">📋 게시판</div>
          <button @click="activeBoard=null; loadPosts()" class="w-full text-left px-3 py-2 text-xs transition"
            :class="!activeBoard ? 'bg-amber-50 text-amber-700 font-bold' : 'text-gray-600 hover:bg-amber-50/50'">전체</button>
          <button v-for="b in boards" :key="b.id" @click="activeBoard=b; loadPosts()"
            class="w-full text-left px-3 py-2 text-xs transition"
            :class="activeBoard?.id === b.id ? 'bg-amber-50 text-amber-700 font-bold' : 'text-gray-600 hover:bg-amber-50/50'">
            {{ b.name }}
          </button>
        </div>
      </div>

      <!-- 메인: 게시글 목록 -->
      <div class="col-span-12 lg:col-span-7">
        <!-- 모바일 게시판 선택 -->
        <div class="lg:hidden mb-3">
          <select v-model="mobileBoardId" @change="onMobileBoard" class="w-full border rounded-lg px-3 py-2 text-sm">
            <option :value="null">전체 게시판</option>
            <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.name }}</option>
          </select>
        </div>

        <div v-if="activeBoard" class="mb-3 text-sm text-gray-600">
          <span class="font-bold text-amber-700">{{ activeBoard.name }}</span>
          <span v-if="activeBoard.description" class="text-xs text-gray-400 ml-2">{{ activeBoard.description }}</span>
        </div>

        <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
        <div v-else-if="!items.length" class="text-center py-12 text-gray-400">게시글이 없습니다</div>

        <!-- 리스트 뷰 -->
        <div v-else-if="viewMode==='list'" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <RouterLink v-for="item in items" :key="item.id" :to="`/community/${item.board?.slug || 'free'}/${item.id}`"
            class="block px-4 py-3 border-b border-gray-50 hover:bg-amber-50/50 transition">
            <div class="flex items-center gap-2">
              <span class="text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-semibold flex-shrink-0">{{ item.board?.name || '자유' }}</span>
              <span class="text-sm font-medium text-gray-800 truncate flex-1">{{ item.title }}</span>
              <span v-if="item.comment_count" class="text-[10px] text-amber-500 font-bold flex-shrink-0">[{{ item.comment_count }}]</span>
            </div>
            <div class="flex items-center gap-2 mt-1 text-xs text-gray-400">
              <span>{{ item.user?.name }}</span>
              <span>{{ item.view_count }}조회</span>
              <span>❤️{{ item.like_count }}</span>
              <span>{{ formatDate(item.created_at) }}</span>
            </div>
          </RouterLink>
        </div>

        <!-- 카드 뷰 -->
        <div v-else class="grid grid-cols-2 gap-3">
          <RouterLink v-for="item in items" :key="item.id" :to="`/community/${item.board?.slug || 'free'}/${item.id}`"
            class="bg-white rounded-xl shadow-sm border border-gray-100 p-3 hover:shadow-md transition">
            <div v-if="item.images?.length" class="aspect-video bg-gray-100 rounded-lg mb-2 overflow-hidden">
              <img :src="'/storage/'+item.images[0]" class="w-full h-full object-cover" @error="e=>e.target.style.display='none'" />
            </div>
            <div v-else class="aspect-video bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg mb-2 flex items-center justify-center text-3xl">💬</div>
            <div class="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-semibold inline-block mb-1">{{ item.board?.name || '자유' }}</div>
            <div class="text-sm font-medium text-gray-800 line-clamp-2">{{ item.title }}</div>
            <div class="text-[10px] text-gray-400 mt-1">{{ item.user?.name }} · {{ item.view_count }}조회</div>
          </RouterLink>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
          <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="loadPosts(pg)"
            class="px-3 py-1 rounded text-sm" :class="pg===page?'bg-amber-400 text-amber-900 font-bold':'bg-white border text-gray-600 hover:bg-amber-50'">{{ pg }}</button>
        </div>
      </div>

      <!-- 오른쪽: 위젯 -->
      <div class="col-span-12 lg:col-span-3 hidden lg:block space-y-3">
        <!-- 인기글 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-3 py-2.5 border-b font-bold text-xs text-amber-900">🔥 인기 게시글</div>
          <div class="py-1">
            <RouterLink v-for="(p, i) in popularPosts" :key="p.id" :to="`/community/${p.board?.slug||'free'}/${p.id}`"
              class="flex items-start gap-2 px-3 py-1.5 hover:bg-amber-50/50 transition">
              <span class="text-[10px] font-bold w-4 text-center" :class="i<3?'text-amber-600':'text-gray-400'">{{ i+1 }}</span>
              <span class="text-xs text-gray-700 leading-snug line-clamp-2 flex-1">{{ p.title }}</span>
            </RouterLink>
          </div>
        </div>

        <!-- 최신 구인 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-3 py-2.5 border-b font-bold text-xs text-amber-900">💼 최신 구인</div>
          <RouterLink v-for="j in recentJobs" :key="j.id" :to="`/jobs/${j.id}`"
            class="block px-3 py-1.5 hover:bg-amber-50/50 transition">
            <div class="text-xs text-gray-700 truncate">{{ j.title }}</div>
            <div class="text-[10px] text-gray-400">{{ j.company }}</div>
          </RouterLink>
          <div v-if="!recentJobs.length" class="px-3 py-3 text-xs text-gray-400 text-center">구인 없음</div>
        </div>

        <!-- 바로가기 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-3">
          <div class="font-bold text-xs text-gray-800 mb-2">⚡ 바로가기</div>
          <RouterLink to="/qa" class="block text-xs text-gray-600 hover:text-amber-700 py-1">❓ Q&A</RouterLink>
          <RouterLink to="/clubs" class="block text-xs text-gray-600 hover:text-amber-700 py-1">👥 동호회</RouterLink>
          <RouterLink to="/news" class="block text-xs text-gray-600 hover:text-amber-700 py-1">📰 뉴스</RouterLink>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const auth = useAuthStore()
const items = ref([])
const boards = ref([])
const popularPosts = ref([])
const recentJobs = ref([])
const activeBoard = ref(null)
const mobileBoardId = ref(null)
const viewMode = ref('list')
const loading = ref(true)
const page = ref(1)
const lastPage = ref(1)

function formatDate(dt) {
  if (!dt) return ''
  const h = Math.floor((Date.now() - new Date(dt).getTime()) / 3600000)
  if (h < 1) return '방금'
  if (h < 24) return h + '시간 전'
  return Math.floor(h / 24) + '일 전'
}

function onMobileBoard() {
  activeBoard.value = boards.value.find(b => b.id === mobileBoardId.value) || null
  loadPosts()
}

async function loadPosts(p = 1) {
  loading.value = true
  page.value = p
  const params = { page: p, per_page: 20 }
  if (activeBoard.value) params.board_id = activeBoard.value.id
  try {
    const { data } = await axios.get('/api/posts', { params })
    items.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
  } catch {}
  loading.value = false
}

onMounted(async () => {
  // 게시판 목록 + 게시글 + 인기글 + 구인 동시 로딩
  const [bRes, pRes, popRes, jRes] = await Promise.allSettled([
    axios.get('/api/boards'),
    axios.get('/api/posts?per_page=20'),
    axios.get('/api/posts?sort=popular&per_page=10'),
    axios.get('/api/jobs?per_page=5'),
  ])
  if (bRes.status === 'fulfilled') boards.value = bRes.value.data?.data || []
  if (pRes.status === 'fulfilled') { items.value = pRes.value.data?.data?.data || []; lastPage.value = pRes.value.data?.data?.last_page || 1 }
  if (popRes.status === 'fulfilled') popularPosts.value = (popRes.value.data?.data?.data || []).slice(0, 10)
  if (jRes.status === 'fulfilled') recentJobs.value = (jRes.value.data?.data?.data || []).slice(0, 5)
  loading.value = false
})
</script>
