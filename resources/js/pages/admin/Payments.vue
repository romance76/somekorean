<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">💳 결제 관리</h1>
  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
  <div v-else-if="!items.length" class="text-center py-8 text-gray-400">결제 내역 없음</div>
  <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 border-b"><tr>
        <th class="px-3 py-2 text-left text-xs text-gray-500">유저</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">금액</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">포인트</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">상태</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">날짜</th>
      </tr></thead>
      <tbody>
        <tr v-for="item in items" :key="item.id" class="border-b last:border-0">
          <td class="px-3 py-2.5 text-gray-800">{{ item.user?.name || '-' }}</td>
          <td class="px-3 py-2.5 text-amber-600 font-bold">${{ item.amount }}</td>
          <td class="px-3 py-2.5">{{ item.points_purchased }}P</td>
          <td class="px-3 py-2.5"><span class="text-xs px-2 py-0.5 rounded-full" :class="item.status==='completed'?'bg-green-100 text-green-700':'bg-gray-100 text-gray-500'">{{ item.status }}</span></td>
          <td class="px-3 py-2.5 text-xs text-gray-400">{{ item.created_at?.slice(0,10) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const items = ref([]); const loading = ref(true)
onMounted(async()=>{ try { const{data}=await axios.get('/api/admin/payments'); items.value=data.data?.data||data.data||[] }catch{}; loading.value=false })
</script>