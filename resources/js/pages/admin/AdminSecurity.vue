<template>
  <div class="space-y-5">
    <h2 class="text-lg font-bold text-gray-800">보안 관리</h2>

    <!-- Tabs -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-1 flex gap-1">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        class="flex-1 py-2 text-sm font-bold rounded-lg transition"
        :class="activeTab === tab.key ? 'bg-red-600 text-white' : 'text-gray-500 hover:bg-gray-50'">
        {{ tab.label }}
      </button>
    </div>

    <!-- IP Bans -->
    <div v-if="activeTab === 'ip'" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold text-gray-800 text-sm">IP 차단 목록</h3>
        <div class="flex gap-2">
          <input v-model="newIp" type="text" placeholder="IP 주소" class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm w-40 focus:outline-none focus:ring-2 focus:ring-red-500" />
          <button @click="addIpBan" :disabled="!newIp" class="bg-red-600 text-white px-3 py-1.5 rounded-lg text-sm font-bold hover:bg-red-700 disabled:opacity-50">차단 추가</button>
        </div>
      </div>
      <div v-if="!ipBans.length" class="text-center py-6 text-gray-400 text-sm">차단된 IP 없음</div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="ip in ipBans" :key="ip.id" class="py-2.5 flex items-center justify-between">
          <div>
            <span class="font-mono text-sm text-gray-800">{{ ip.ip_address }}</span>
            <span class="text-xs text-gray-400 ml-2">{{ ip.reason }}</span>
          </div>
          <button @click="removeIpBan(ip.id)" class="text-xs text-red-500 hover:text-red-700">해제</button>
        </div>
      </div>
    </div>

    <!-- Reports -->
    <div v-if="activeTab === 'reports'" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100"><h3 class="font-bold text-gray-800 text-sm">신고 목록</h3></div>
      <div v-if="!reports.length" class="text-center py-8 text-gray-400 text-sm">신고 없음</div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="r in reports" :key="r.id" class="px-5 py-3 flex items-center gap-3">
          <div class="flex-1 min-w-0">
            <p class="text-sm text-gray-800">{{ r.reason }}</p>
            <p class="text-xs text-gray-400">{{ r.reporter?.name }} > {{ r.reported?.name || r.target_type }} · {{ formatDate(r.created_at) }}</p>
          </div>
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="r.status === 'pending' ? 'bg-yellow-50 text-yellow-600' : 'bg-green-50 text-green-600'">{{ r.status === 'pending' ? '대기' : '처리됨' }}</span>
          <button v-if="r.status === 'pending'" @click="resolveReport(r)" class="text-xs px-2 py-1 rounded bg-green-50 text-green-600 hover:bg-green-100">처리</button>
        </div>
      </div>
    </div>

    <!-- Bot Stats -->
    <div v-if="activeTab === 'bots'" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">봇 감지 통계</h3>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div v-for="stat in botStats" :key="stat.label" class="text-center p-4 bg-gray-50 rounded-xl">
          <div class="text-2xl font-black text-gray-800">{{ stat.value }}</div>
          <div class="text-xs text-gray-500 mt-1">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const activeTab = ref('ip'), ipBans = ref([]), reports = ref([]), botStats = ref([]), newIp = ref('')
const tabs = [{ key: 'ip', label: 'IP 차단' }, { key: 'reports', label: '신고 관리' }, { key: 'bots', label: '봇 감지' }]
function formatDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '' }
async function loadData() {
  try { const { data } = await axios.get('/api/admin/security'); ipBans.value = data.ip_bans || []; reports.value = data.reports || []; botStats.value = data.bot_stats || [] } catch {}
}
async function addIpBan() { if (!newIp.value) return; try { await axios.post('/api/admin/security/ip-bans', { ip_address: newIp.value }); newIp.value = ''; await loadData() } catch (e) { alert(e.response?.data?.message || '실패') } }
async function removeIpBan(id) { try { await axios.delete(`/api/admin/security/ip-bans/${id}`); await loadData() } catch {} }
async function resolveReport(r) { try { await axios.post(`/api/admin/reports/${r.id}/resolve`); r.status = 'resolved' } catch {} }
onMounted(loadData)
</script>
