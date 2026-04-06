<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <button @click="$router.back()" class="text-sm text-gray-500 hover:text-amber-600 mb-3">← 뉴스 목록</button>
    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="news" class="grid grid-cols-12 gap-4">
      <div class="col-span-12 lg:col-span-9">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div v-if="news.image_url" class="h-56 bg-gray-200 overflow-hidden">
            <img :src="news.image_url" class="w-full h-full object-cover" @error="e=>e.target.style.display='none'" />
          </div>
          <div class="px-5 py-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-semibold">{{ news.category?.name }}</span>
              <span class="text-xs text-gray-400">{{ news.source }}</span>
              <span class="text-xs text-gray-400">{{ formatDate(news.published_at) }}</span>
            </div>
            <h1 class="text-lg font-bold text-gray-900 leading-snug">{{ news.title }}</h1>
            <div class="text-xs text-gray-400 mt-2">👁 {{ news.view_count }}조회</div>
          </div>
          <div class="px-5 py-5 border-t text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ news.content }}</div>
          <div v-if="news.source_url" class="px-5 py-3 border-t">
            <a :href="news.source_url" target="_blank" class="text-amber-600 text-sm hover:underline">📎 원문 보기 →</a>
          </div>
        </div>
      </div>
      <div class="col-span-12 lg:col-span-3 hidden lg:block space-y-3">
        <div v-if="relatedNews.length" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div class="font-bold text-sm text-amber-900 mb-3">📰 관련 뉴스</div>
          <RouterLink v-for="n in relatedNews" :key="n.id" :to="'/news/'+n.id"
            class="block text-xs text-gray-600 hover:text-amber-700 py-1.5 border-b border-gray-50 last:border-0 truncate transition">
            {{ n.title }}
          </RouterLink>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div class="font-bold text-sm text-amber-900 mb-3">📋 뉴스 카테고리</div>
          <div class="space-y-1">
            <RouterLink to="/news" class="block text-xs text-gray-600 hover:text-amber-700 py-1">📰 전체 뉴스</RouterLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
const route = useRoute()
const news = ref(null)
const relatedNews = ref([])
const loading = ref(true)
function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString('ko-KR') : '' }
onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/news/${route.params.id}`)
    news.value = data.data
    try {
      const { data: r } = await axios.get('/api/news?per_page=5')
      relatedNews.value = (r.data?.data || []).filter(n => n.id !== news.value.id).slice(0, 5)
    } catch {}
  } catch {}
  loading.value = false
})
</script>