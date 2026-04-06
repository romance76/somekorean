<template>
<div>
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-xl font-black text-gray-800">🖼️ 배너 관리</h1>
    <button @click="showCreate=true" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm">+ 배너 추가</button>
  </div>
  <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
    <div v-for="b in items" :key="b.id" class="px-4 py-3 border-b last:border-0 flex items-center justify-between">
      <div><span class="font-semibold text-gray-800">{{ b.title }}</span> <span class="text-xs px-2 py-0.5 rounded-full ml-2" :class="b.is_active?'bg-green-100 text-green-700':'bg-gray-100 text-gray-500'">{{ b.is_active ? '활성' : '비활성' }}</span></div>
      <button @click="deleteItem(b)" class="text-xs text-red-400 hover:text-red-600">삭제</button>
    </div>
    <div v-if="!items.length" class="px-4 py-6 text-sm text-gray-400 text-center">배너 없음</div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const items = ref([]); const showCreate = ref(false)
onMounted(async()=>{ try { const{data}=await axios.get('/api/admin/banners'); items.value=data.data||[] }catch{} })
async function deleteItem(b) { if(!confirm('삭제?'))return; try { await axios.delete('/api/admin/banners/'+b.id); items.value=items.value.filter(x=>x.id!==b.id) }catch{} }
</script>