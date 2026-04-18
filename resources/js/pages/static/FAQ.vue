<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-black text-gray-800 mb-6">❓ 자주 묻는 질문</h1>

    <!-- 카테고리 필터 -->
    <div class="flex gap-2 mb-4 overflow-x-auto scrollbar-hide">
      <button
        @click="selectedCategory = null"
        :class="['px-3 py-1.5 rounded-full text-xs whitespace-nowrap', selectedCategory === null ? 'bg-amber-400 text-white font-semibold' : 'bg-gray-100 hover:bg-gray-200']"
      >전체</button>
      <button
        v-for="cat in categories"
        :key="cat"
        @click="selectedCategory = cat"
        :class="['px-3 py-1.5 rounded-full text-xs whitespace-nowrap', selectedCategory === cat ? 'bg-amber-400 text-white font-semibold' : 'bg-gray-100 hover:bg-gray-200']"
      >{{ categoryLabel(cat) }}</button>
    </div>

    <div v-if="loading" class="bg-white rounded-xl shadow-sm border p-6 text-sm text-gray-400">로딩 중...</div>
    <div v-else-if="!filtered.length" class="bg-white rounded-xl shadow-sm border p-8 text-center text-sm text-gray-500">
      해당 카테고리에 등록된 FAQ 가 없습니다.
    </div>
    <div v-else class="space-y-2">
      <details
        v-for="faq in filtered"
        :key="faq.id"
        class="bg-white rounded-xl shadow-sm border group"
      >
        <summary class="flex items-center gap-3 p-4 cursor-pointer hover:bg-gray-50 list-none">
          <span class="text-amber-500 font-bold">Q.</span>
          <span class="flex-1 font-semibold text-sm">{{ faq.question }}</span>
          <span class="text-gray-400 group-open:rotate-180 transition">▼</span>
        </summary>
        <div class="px-4 pb-4 pt-1 border-t text-sm text-gray-700 whitespace-pre-wrap">
          <span class="text-amber-500 font-bold mr-1">A.</span>{{ faq.answer }}
          <div class="mt-3 flex items-center gap-3">
            <button @click="helpful(faq)" class="text-xs text-gray-500 hover:text-amber-600">
              👍 도움됨 ({{ faq.helpful_count || 0 }})
            </button>
          </div>
        </div>
      </details>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const items = ref([])
const loading = ref(true)
const selectedCategory = ref(null)

const categories = computed(() => [...new Set(items.value.map(f => f.category))])
const filtered = computed(() => selectedCategory.value
  ? items.value.filter(f => f.category === selectedCategory.value)
  : items.value
)

const categoryLabel = (c) => ({
  account: '계정',
  payment: '결제',
  usage: '이용방법',
  safety: '안전·보안',
}[c] || c)

async function load() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/site/faqs')
    items.value = data?.data ?? []
  } finally {
    loading.value = false
  }
}

async function helpful(faq) {
  try {
    await axios.post(`/api/site/faqs/${faq.id}/helpful`)
    faq.helpful_count = (faq.helpful_count || 0) + 1
  } catch {}
}

onMounted(load)
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
