<template>
<div class="space-y-3">
  <!-- 많이 본 글 / 최신 글 (탭 + 페이지네이션) -->
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="flex border-b">
      <button @click="popTab='views'; loadTab('views')" class="flex-1 py-2.5 text-xs font-bold transition"
        :class="popTab==='views' ? 'text-amber-700 border-b-2 border-amber-500 bg-amber-50' : 'text-gray-400'">많이 본 {{ label }}</button>
      <button @click="popTab='latest'; loadTab('latest')" class="flex-1 py-2.5 text-xs font-bold transition"
        :class="popTab==='latest' ? 'text-amber-700 border-b-2 border-amber-500 bg-amber-50' : 'text-gray-400'">최신 {{ label }}</button>
    </div>
    <div class="py-1">
      <component v-for="(item, i) in currentItems" :key="item.id"
        :is="inline ? 'button' : 'RouterLink'" :to="inline ? undefined : detailPath + item.id"
        @click="inline && emit('select', item)"
        class="flex items-start gap-2 px-3 py-2 hover:bg-amber-50/50 transition w-full text-left">
        <span class="text-xs font-bold flex-shrink-0 w-5 text-center" :class="(currentPage - 1) * 10 + i < 3 ? 'text-amber-600' : 'text-gray-400'">{{ (currentPage - 1) * 10 + i + 1 }}</span>
        <span class="text-xs text-gray-700 leading-snug line-clamp-2">{{ item.title || item.name }}</span>
      </component>
      <div v-if="tabLoading" class="py-4 text-center text-xs text-gray-400">로딩중...</div>
      <div v-else-if="!currentItems.length" class="py-4 text-center text-xs text-gray-400">데이터가 없습니다</div>
    </div>
    <!-- 페이지네이션 -->
    <div v-if="currentLastPage > 1" class="px-3 py-2 border-t flex justify-center items-center gap-1">
      <button @click="goPage(1)" :disabled="currentPage<=1" class="text-[10px] text-gray-400 hover:text-amber-700 disabled:opacity-30 px-1">«</button>
      <button @click="goPage(currentPage-1)" :disabled="currentPage<=1" class="text-[10px] text-gray-400 hover:text-amber-700 disabled:opacity-30 px-1">‹</button>
      <button v-for="pg in visiblePages" :key="pg" @click="goPage(pg)"
        class="w-6 h-6 rounded text-[10px] font-bold" :class="pg===currentPage?'bg-amber-400 text-amber-900':'text-gray-400 hover:bg-amber-50'">{{ pg }}</button>
      <button @click="goPage(currentPage+1)" :disabled="currentPage>=currentLastPage" class="text-[10px] text-gray-400 hover:text-amber-700 disabled:opacity-30 px-1">›</button>
      <button @click="goPage(currentLastPage)" :disabled="currentPage>=currentLastPage" class="text-[10px] text-gray-400 hover:text-amber-700 disabled:opacity-30 px-1">»</button>
    </div>
  </div>

  <!-- 추천 글 -->
  <div v-if="recommendLabel && recommendItems.length" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="px-3 py-2.5 border-b font-bold text-xs text-gray-800">👍 {{ recommendLabel }}</div>
    <div class="py-1">
      <component v-for="item in recommendItems" :key="item.id"
        :is="inline ? 'button' : 'RouterLink'" :to="inline ? undefined : detailPath + item.id"
        @click="inline && emit('select', item)"
        class="block px-3 py-2 hover:bg-amber-50/50 transition w-full text-left">
        <div class="text-xs text-gray-700 line-clamp-2 leading-snug">{{ item.title || item.name }}</div>
        <div class="text-[10px] text-gray-400 mt-0.5">{{ item.user?.name || item.company || item.source || '' }}</div>
      </component>
    </div>
  </div>

  <!-- 실시간/바로가기 -->
  <div v-if="quickLabel && quickItems.length" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="px-3 py-2.5 border-b font-bold text-xs text-gray-800">⚡ {{ quickLabel }}</div>
    <div class="py-1">
      <component v-for="item in quickItems" :key="item.id"
        :is="inline ? 'button' : 'RouterLink'" :to="inline ? undefined : detailPath + item.id"
        @click="inline && emit('select', item)"
        class="flex items-center gap-2 px-3 py-1.5 hover:bg-amber-50/50 transition w-full text-left">
        <span class="text-[10px] text-amber-500">●</span>
        <span class="text-xs text-gray-600 truncate">{{ item.title || item.name }}</span>
      </component>
    </div>
  </div>

  <!-- 빠른 링크 -->
  <div v-if="links.length" class="bg-white rounded-xl shadow-sm border border-gray-100 p-3">
    <div class="font-bold text-xs text-gray-800 mb-2">📋 바로가기</div>
    <RouterLink v-for="link in links" :key="link.to" :to="link.to"
      class="block text-xs text-gray-600 hover:text-amber-700 py-1 transition">
      {{ link.icon }} {{ link.label }}
    </RouterLink>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  apiUrl: { type: String, required: true },
  detailPath: { type: String, required: true },
  currentId: { type: [Number, String], default: 0 },
  label: { type: String, default: '글' },
  recommendLabel: { type: String, default: '' },
  quickLabel: { type: String, default: '' },
  links: { type: Array, default: () => [] },
  filterParams: { type: Object, default: () => ({}) },
  inline: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])

const popTab = ref('views')
const tabLoading = ref(false)

// 각 탭별 데이터 + 페이지
const viewsItems = ref([])
const viewsPage = ref(1)
const viewsLastPage = ref(1)
const latestItemsData = ref([])
const latestPage = ref(1)
const latestLastPage = ref(1)

const recommendItems = ref([])
const quickItems = ref([])

const currentItems = computed(() => popTab.value === 'views' ? viewsItems.value : latestItemsData.value)
const currentPage = computed(() => popTab.value === 'views' ? viewsPage.value : latestPage.value)
const currentLastPage = computed(() => popTab.value === 'views' ? viewsLastPage.value : latestLastPage.value)

const visiblePages = computed(() => {
  const p = currentPage.value
  const last = currentLastPage.value
  const start = Math.max(1, p - 2)
  const end = Math.min(last, start + 4)
  const pages = []
  for (let i = Math.max(1, end - 4); i <= end; i++) pages.push(i)
  return pages
})

async function loadTab(tab, page = 1) {
  tabLoading.value = true
  const sort = tab === 'views' ? 'popular' : 'latest'
  try {
    const { data } = await axios.get(props.apiUrl, { params: { sort, per_page: 10, page, ...props.filterParams } })
    const items = (data.data?.data || []).filter(i => i.id !== Number(props.currentId)).slice(0, 10)
    const totalItems = data.data?.total || items.length
    const lastPg = Math.ceil(totalItems / 10) || 1
    if (tab === 'views') { viewsItems.value = items; viewsPage.value = page; viewsLastPage.value = lastPg }
    else { latestItemsData.value = items; latestPage.value = page; latestLastPage.value = lastPg }
  } catch {}
  tabLoading.value = false
}

function goPage(pg) {
  if (pg < 1 || pg > currentLastPage.value) return
  loadTab(popTab.value, pg)
}

onMounted(async () => {
  // 인기 + 최신 동시 로드
  await Promise.allSettled([loadTab('views', 1), loadTab('latest', 1)])

  // 추천 (recommendLabel 있을 때만)
  if (props.recommendLabel) {
    try {
      const { data } = await axios.get(props.apiUrl, { params: { per_page: 5 } })
      recommendItems.value = (data.data?.data || []).filter(i => i.id !== Number(props.currentId)).slice(0, 5)
    } catch {}
  }

  // 실시간 = 최신 상위 6개
  quickItems.value = latestItemsData.value.slice(0, 6)
})
</script>
