<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-black text-gray-800 mb-6">{{ title || 'SomeKorean 소개' }}</h1>
    <div v-if="loading" class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-400">로딩 중...</div>
    <div v-else-if="html" class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-700 leading-relaxed prose max-w-none" v-html="html" />
    <div v-else class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-700 leading-relaxed space-y-4">
      <p>SomeKorean은 미국에 거주하는 한인들을 위한 올인원 커뮤니티 플랫폼입니다.</p>
      <p>구인구직, 중고장터, 업소록, 부동산, 뉴스, 이벤트, Q&amp;A 등 한인 생활에 필요한 모든 서비스를 한 곳에서 제공합니다.</p>
      <p>문의: admin@somekorean.com</p>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const title = ref('')
const html = ref('')
const loading = ref(true)
onMounted(async () => {
  try {
    const { data } = await axios.get('/api/site/static-pages/about')
    if (data?.data) {
      title.value = data.data.title
      html.value = data.data.content
    }
  } catch {} finally { loading.value = false }
})
</script>
