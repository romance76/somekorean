<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">🛍️ 쇼핑 / 핫딜</h1>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="!deals.length" class="text-center py-12 text-gray-400">등록된 딜이 없습니다</div>
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      <a v-for="deal in deals" :key="deal.id" :href="deal.url || '#'" target="_blank"
        class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition group">
        <div class="aspect-square bg-gray-100 flex items-center justify-center">
          <img v-if="deal.image_url" :src="deal.image_url" class="w-full h-full object-cover" @error="e=>e.target.style.display='none'" />
          <span v-else class="text-4xl">🛍️</span>
        </div>
        <div class="p-3">
          <div class="text-xs text-gray-500 mb-1">{{ deal.store?.name || '매장' }}</div>
          <div class="text-sm font-medium text-gray-800 line-clamp-2 group-hover:text-amber-700">{{ deal.title }}</div>
          <div class="flex items-center gap-2 mt-2">
            <span v-if="deal.original_price" class="text-xs text-gray-400 line-through">${{ Number(deal.original_price).toLocaleString() }}</span>
            <span v-if="deal.sale_price" class="text-sm font-bold text-red-500">${{ Number(deal.sale_price).toLocaleString() }}</span>
            <span v-if="deal.discount_percent" class="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded-full font-bold">-{{ deal.discount_percent }}%</span>
          </div>
        </div>
      </a>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const deals = ref([])
const loading = ref(true)
onMounted(async () => {
  try { const { data } = await axios.get('/api/shopping'); deals.value = data.data?.data || data.data || [] } catch {}
  loading.value = false
})
</script>
