<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">💙 안심서비스 관리</h1>
  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
  <div v-else-if="!items.length" class="text-center py-8 text-gray-400">데이터 없음</div>
  <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 border-b"><tr>
        <th class="px-3 py-2 text-left text-xs text-gray-500">유저ID</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">간격(h)</th>
        <th class="px-3 py-2 text-xs text-gray-500">관리</th>
      </tr></thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="border-b last:border-0 hover:bg-amber-50/30">
          <td class="px-3 py-2.5 text-xs text-gray-500">{{ item.user_id }}</td>
          <td class="px-3 py-2.5 text-xs text-gray-500">{{ item.checkin_interval }}</td>
          <td class="px-3 py-2.5 text-center">
            <button @click="deleteItem(item)" class="text-xs text-red-400 hover:text-red-600">삭제</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
    <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="load(pg)"
      class="px-3 py-1 rounded text-sm" :class="pg===page?'bg-amber-400 text-amber-900 font-bold':'bg-white border text-gray-600'">{{ pg }}</button>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const items = ref([]); const loading = ref(true); const page = ref(1); const lastPage = ref(1)
async function load(p=1) { loading.value=true; page.value=p; try { const{data}=await axios.get('/api/elder/guardian/wards',{params:{page:p}}); items.value=data.data?.data||data.data||[]; lastPage.value=data.data?.last_page||1 }catch{}; loading.value=false }
async function deleteItem(item) { if(!confirm('삭제?'))return; try { await axios.delete('/api/elder/guardian/wards/'+item.id); items.value=items.value.filter(x=>x.id!==item.id) }catch{} }
onMounted(()=>load())
</script>