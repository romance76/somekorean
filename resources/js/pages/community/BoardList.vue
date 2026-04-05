<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">

      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-5 rounded-xl mb-5">
        <h1 class="text-xl font-black flex items-center gap-2">
          <span>💬</span> {{ locale === 'ko' ? '커뮤니티' : 'Community' }}
        </h1>
        <p class="text-blue-100 text-sm mt-0.5">{{ locale === 'ko' ? '한인들과 정보를 나누고 소통해요' : 'Share and connect with Koreans' }}</p>
      </div>

      <!-- Q&A Banner -->
      <router-link to="/qa"
        class="flex items-center gap-4 bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-700 rounded-xl px-5 py-4 mb-5 hover:shadow-md transition group">
        <div class="w-12 h-12 bg-amber-100 dark:bg-amber-800 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">🧠</div>
        <div class="flex-1 min-w-0">
          <div class="font-bold text-amber-800 dark:text-amber-200 text-sm">{{ locale === 'ko' ? '지식인 Q&A' : 'Q&A' }}</div>
          <div class="text-xs text-amber-600 dark:text-amber-400 mt-0.5">
            {{ locale === 'ko' ? '궁금한 것을 물어보고 포인트로 답변 받아보세요' : 'Ask questions and earn points for answers' }}
          </div>
        </div>
        <svg class="w-5 h-5 text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
        </svg>
      </router-link>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-16">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
        <p class="text-sm text-gray-400">{{ locale === 'ko' ? '불러오는 중...' : 'Loading...' }}</p>
      </div>

      <!-- Board Groups -->
      <div v-else>
        <div v-for="(group, category) in grouped" :key="category" class="mb-5">
          <h2 class="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 px-1">
            {{ categoryLabel(category) }}
          </h2>
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
            <router-link v-for="board in group" :key="board.id"
              :to="`/community/${board.slug}`"
              class="flex items-center justify-between px-5 py-4 border-b border-gray-50 dark:border-gray-700 last:border-0 hover:bg-blue-50/50 dark:hover:bg-gray-700/50 transition">
              <div class="flex items-center gap-3">
                <span class="text-xl w-8 text-center">{{ board.icon || '📋' }}</span>
                <div>
                  <p class="text-gray-800 dark:text-white font-semibold text-sm">{{ board.name }}</p>
                  <p class="text-gray-400 dark:text-gray-500 text-xs mt-0.5">{{ board.description }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <span v-if="board.post_count" class="text-xs text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                  {{ board.post_count }}
                </span>
                <svg class="w-4 h-4 text-gray-300 dark:text-gray-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </div>
            </router-link>
          </div>
        </div>

        <!-- Empty -->
        <div v-if="!boards.length" class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
          <p class="text-4xl mb-3">📭</p>
          <p class="text-gray-400 text-sm">{{ locale === 'ko' ? '게시판이 없습니다' : 'No boards available' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const boards = ref([])
const loading = ref(true)

const grouped = computed(() => {
  const g = {}
  boards.value.forEach(b => {
    const cat = b.category || 'community'
    if (!g[cat]) g[cat] = []
    g[cat].push(b)
  })
  return g
})

function categoryLabel(cat) {
  if (locale.value === 'ko') {
    return { community: '커뮤니티 게시판', local: '지역별 게시판', expert: '전문가 칼럼' }[cat] || cat
  }
  return { community: 'Community Boards', local: 'Regional Boards', expert: 'Expert Columns' }[cat] || cat
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/boards')
    boards.value = Array.isArray(data) ? data : data.data || []
  } catch { /* empty */ }
  loading.value = false
})
</script>
