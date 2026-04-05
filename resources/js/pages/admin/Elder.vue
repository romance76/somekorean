<template>
  <div class="space-y-5">
    <h2 class="text-lg font-bold text-gray-800">안심서비스 관리</h2>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">등록 어르신</div>
        <div class="text-2xl font-black text-gray-800">{{ stats.total_elders || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">오늘 체크인</div>
        <div class="text-2xl font-black text-green-600">{{ stats.checked_in_today || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">미체크인</div>
        <div class="text-2xl font-black text-red-600">{{ stats.missed_today || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">SOS 알림</div>
        <div class="text-2xl font-black text-orange-600">{{ stats.active_sos || 0 }}</div>
      </div>
    </div>

    <!-- SOS Alerts -->
    <div v-if="sosAlerts.length" class="bg-red-50 border border-red-200 rounded-xl p-4">
      <h3 class="font-bold text-red-800 text-sm mb-3">활성 SOS 알림</h3>
      <div v-for="s in sosAlerts" :key="s.id" class="flex items-center gap-3 py-2 border-b border-red-100 last:border-0">
        <span class="text-lg">🚨</span>
        <div class="flex-1"><p class="text-sm font-bold text-red-800">{{ s.elder_name }}</p><p class="text-xs text-red-600">{{ formatDate(s.created_at) }}</p></div>
        <button @click="acknowledgeAlert(s.id)" class="text-xs bg-red-600 text-white px-3 py-1.5 rounded-lg font-bold hover:bg-red-700">확인</button>
      </div>
    </div>

    <!-- Elder List -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100"><h3 class="font-bold text-gray-800 text-sm">어르신 목록</h3></div>
      <div class="overflow-x-auto"><table class="w-full text-sm"><thead class="bg-gray-50 border-b border-gray-200"><tr>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">이름</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">체크인</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">마지막 체크인</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">보호자</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">연속일</th>
      </tr></thead><tbody class="divide-y divide-gray-50">
        <tr v-for="e in elders" :key="e.id" class="hover:bg-gray-50">
          <td class="px-4 py-3 font-medium text-gray-800">{{ e.name }}</td>
          <td class="px-4 py-3"><span class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="e.checked_in_today ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'">{{ e.checked_in_today ? '완료' : '미완료' }}</span></td>
          <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(e.last_checkin) }}</td>
          <td class="px-4 py-3 text-gray-600 text-xs">{{ e.guardian_name || '-' }}</td>
          <td class="px-4 py-3 text-right text-gray-700">{{ e.streak || 0 }}일</td>
        </tr>
      </tbody></table></div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const stats = ref({}), elders = ref([]), sosAlerts = ref([])
function formatDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '' }
async function loadData() { try { const { data } = await axios.get('/api/admin/elder'); stats.value = data.stats || {}; elders.value = data.elders || []; sosAlerts.value = data.sos_alerts || [] } catch {} }
async function acknowledgeAlert(id) { try { await axios.post(`/api/admin/elder/sos/${id}/acknowledge`); sosAlerts.value = sosAlerts.value.filter(s => s.id !== id) } catch {} }
onMounted(loadData)
</script>
