<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-black text-gray-800 mb-6">{{ title || '개인정보처리방침' }}</h1>
    <div v-if="loading" class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-400">로딩 중...</div>
    <div v-else-if="html" class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-700 leading-relaxed prose max-w-none" v-html="html" />
    <div v-else class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-700 leading-relaxed space-y-3">
      <h2 class="font-bold text-base">1. 수집하는 개인정보</h2>
      <p>회원가입 시 이메일, 비밀번호, 이름(선택)을 수집합니다.</p>
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
    const { data } = await axios.get('/api/site/static-pages/privacy')
    if (data?.data) {
      title.value = data.data.title
      html.value = data.data.content
    }
  } catch {} finally { loading.value = false }
})
</script>
