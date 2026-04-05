<template>
  <div class="space-y-5">
    <h2 class="text-lg font-bold text-gray-800">친구 관리</h2>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">총 친구 연결</div>
        <div class="text-2xl font-black text-gray-800">{{ stats.total_friendships || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">대기중 요청</div>
        <div class="text-2xl font-black text-yellow-600">{{ stats.pending_requests || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">오늘 새 친구</div>
        <div class="text-2xl font-black text-green-600">{{ stats.new_today || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">차단 관계</div>
        <div class="text-2xl font-black text-red-600">{{ stats.blocked || 0 }}</div>
      </div>
    </div>

    <!-- Recent friendships -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100"><h3 class="font-bold text-gray-800 text-sm">최근 친구 관계</h3></div>
      <div v-if="!friendships.length" class="text-center py-8 text-gray-400 text-sm">데이터 없음</div>
      <div class="overflow-x-auto"><table class="w-full text-sm"><thead class="bg-gray-50 border-b border-gray-200"><tr>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">사용자 1</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">사용자 2</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">상태</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">날짜</th>
      </tr></thead><tbody class="divide-y divide-gray-50">
        <tr v-for="f in friendships" :key="f.id" class="hover:bg-gray-50">
          <td class="px-4 py-3 text-gray-800">{{ f.user?.name || '-' }}</td>
          <td class="px-4 py-3 text-gray-800">{{ f.friend?.name || '-' }}</td>
          <td class="px-4 py-3"><span class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="f.status === 'accepted' ? 'bg-green-50 text-green-600' : f.status === 'blocked' ? 'bg-red-50 text-red-600' : 'bg-yellow-50 text-yellow-600'">{{ {accepted:'친구',blocked:'차단',pending:'대기'}[f.status] || f.status }}</span></td>
          <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(f.created_at) }}</td>
        </tr>
      </tbody></table></div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const stats = ref({}), friendships = ref([])
function formatDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '' }
async function loadData() { try { const { data } = await axios.get('/api/admin/friends'); stats.value = data.stats || {}; friendships.value = data.friendships || data.data || [] } catch {} }
onMounted(loadData)
</script>
