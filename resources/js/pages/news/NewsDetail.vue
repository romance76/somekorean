<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <button @click="$router.back()" class="text-sm text-gray-500 hover:text-amber-600 mb-3">← 뉴스 목록</button>
    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="news" class="grid grid-cols-12 gap-4">
      <!-- 메인 콘텐츠 -->
      <div class="col-span-12 lg:col-span-9">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-5 py-4">
            <h1 class="text-lg font-bold text-gray-900 leading-snug">{{ news.title }}</h1>
            <div class="flex items-center gap-3 mt-2 text-xs text-gray-400">
              <span>{{ news.source }}</span>
              <span>{{ formatDate(news.published_at) }}</span>
              <span>👁 {{ news.view_count }}조회</span>
            </div>
          </div>
          <div v-if="news.image_url" class="px-5 pb-3">
            <img :src="news.image_url" class="w-full max-h-96 object-cover rounded-lg" @error="e=>e.target.style.display='none'" />
          </div>
          <div class="px-5 py-5 border-t text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ news.content }}</div>
          <div v-if="news.source_url" class="px-5 py-3 border-t">
            <a :href="news.source_url" target="_blank" class="text-amber-600 text-sm hover:underline">📎 원문 보기 →</a>
          </div>
        </div>
      </div>

      <!-- 오른쪽 사이드바 -->
      <div class="col-span-12 lg:col-span-3 hidden lg:block">
        <SidebarWidgets
          api-url="/api/news"
          detail-path="/news/"
          :current-id="news.id"
          label="뉴스"
          recommend-label="좋아할 기사"
          quick-label="실시간 뉴스"
          :links="[
            { to: '/news', icon: '📰', label: '전체 뉴스' },
            { to: '/community', icon: '💬', label: '커뮤니티' },
          ]"
        />
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import SidebarWidgets from '../../components/SidebarWidgets.vue'
import axios from 'axios'

const route = useRoute()
const news = ref(null)
const loading = ref(true)

function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString('ko-KR') : '' }

onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/news/${route.params.id}`)
    news.value = data.data
  } catch {}
  loading.value = false
})
</script>
