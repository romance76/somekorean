<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-black text-gray-800 mb-6">{{ title || '이용약관' }}</h1>
    <div v-if="loading" class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-400">로딩 중...</div>
    <div v-else-if="html" class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-700 leading-relaxed prose max-w-none" v-html="html" />
    <div v-else class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-700 leading-relaxed space-y-3">
      <h2 class="font-bold text-base">제1조 (목적)</h2>
      <p>이 약관은 SomeKorean(이하 "서비스")이 제공하는 인터넷 관련 서비스의 이용조건 및 절차, 이용자와 서비스 간의 권리, 의무 등을 규정함을 목적으로 합니다.</p>
      <p class="text-gray-400 mt-4">최종 수정일: 2026-04-06</p>
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
    const { data } = await axios.get('/api/site/static-pages/terms')
    if (data?.data) {
      title.value = data.data.title
      html.value = data.data.content
    }
  } catch {} finally { loading.value = false }
})
</script>
