<template>
<div>
  <h2 class="text-lg font-bold text-gray-800 mb-4">💙 안심서비스 관리</h2>

  <!-- 통계 카드 -->
  <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-4">
    <div class="bg-white rounded-lg border p-3">
      <div class="text-[10px] text-gray-500">활성 보호자</div>
      <div class="text-lg font-bold text-amber-600">{{ overview.active_guardians || 0 }}</div>
    </div>
    <div class="bg-white rounded-lg border p-3">
      <div class="text-[10px] text-gray-500">대기 중</div>
      <div class="text-lg font-bold text-amber-600">{{ overview.pending_guardians || 0 }}</div>
    </div>
    <div class="bg-white rounded-lg border p-3">
      <div class="text-[10px] text-gray-500">오늘 통화</div>
      <div class="text-lg font-bold text-green-600">{{ overview.calls_today || 0 }}</div>
    </div>
    <div class="bg-white rounded-lg border p-3">
      <div class="text-[10px] text-gray-500">오늘 체크인</div>
      <div class="text-lg font-bold text-blue-600">{{ overview.checkins_today || 0 }}</div>
    </div>
    <div class="bg-white rounded-lg border p-3">
      <div class="text-[10px] text-gray-500">미해결 SOS</div>
      <div class="text-lg font-bold text-red-600">{{ overview.sos_unresolved || 0 }}</div>
    </div>
    <div class="bg-white rounded-lg border p-3">
      <div class="text-[10px] text-gray-500">스케줄</div>
      <div class="text-lg font-bold text-gray-700">{{ overview.total_schedules || 0 }}</div>
    </div>
  </div>

  <!-- 탭 -->
  <div class="flex gap-1 mb-4 border-b">
    <button v-for="t in tabs" :key="t.key" @click="tab=t.key; loadData()"
      class="px-4 py-2 text-xs font-bold border-b-2 transition"
      :class="tab===t.key ? 'border-amber-500 text-amber-700' : 'border-transparent text-gray-400 hover:text-gray-600'">
      {{ t.label }}
    </button>
  </div>

  <!-- 매칭 관리 -->
  <div v-if="tab==='guardians'">
    <div class="flex gap-2 mb-3">
      <input v-model="search" @keyup.enter="loadGuardians()" placeholder="이름/이메일 검색..." class="flex-1 border rounded-lg px-3 py-1.5 text-sm" />
      <select v-model="statusFilter" @change="loadGuardians()" class="border rounded-lg px-3 py-1.5 text-xs">
        <option value="">전체</option>
        <option value="active">활성</option>
        <option value="pending">대기</option>
      </select>
    </div>
    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!guardians.length" class="text-center py-8 text-gray-400">매칭이 없습니다</div>
    <div v-else class="bg-white rounded-lg border overflow-x-auto">
      <table class="w-full text-xs">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="px-3 py-2 text-left">보호자</th>
            <th class="px-3 py-2 text-left">보호대상</th>
            <th class="px-3 py-2 text-left">스케줄</th>
            <th class="px-3 py-2 text-left">상태</th>
            <th class="px-3 py-2 text-left">등록일</th>
            <th class="px-3 py-2 text-right">작업</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in guardians" :key="g.id" class="border-b hover:bg-amber-50/30">
            <td class="px-3 py-2">
              <div class="font-semibold">{{ g.guardian_name || '-' }}</div>
              <div class="text-[10px] text-gray-400">{{ g.guardian_email }}</div>
            </td>
            <td class="px-3 py-2">
              <div class="font-semibold">{{ g.ward_name || '-' }}</div>
              <div class="text-[10px] text-gray-400">{{ g.ward_phone }} · {{ g.ward_city }}, {{ g.ward_state }}</div>
            </td>
            <td class="px-3 py-2">
              <div v-if="g.schedule_type">{{ {daily:'매일', weekly:'매주', scheduled:'지정시각'}[g.schedule_type] || g.schedule_type }}</div>
              <div v-if="g.time_start" class="text-[10px] text-gray-400">{{ g.time_start }}~{{ g.time_end }} ({{ g.calls_per_day }}회/일)</div>
            </td>
            <td class="px-3 py-2">
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold"
                :class="g.status==='active'?'bg-green-100 text-green-700':'bg-amber-100 text-amber-700'">{{ g.status }}</span>
            </td>
            <td class="px-3 py-2 text-gray-500">{{ formatDate(g.created_at) }}</td>
            <td class="px-3 py-2 text-right">
              <button @click="deleteGuardian(g)" class="text-red-500 hover:text-red-700 text-[10px]">해제</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- 통화 로그 -->
  <div v-else-if="tab==='calls'">
    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!callLogs.length" class="text-center py-8 text-gray-400">통화 기록이 없습니다</div>
    <div v-else class="bg-white rounded-lg border overflow-x-auto">
      <table class="w-full text-xs">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="px-3 py-2 text-left">시각</th>
            <th class="px-3 py-2 text-left">보호자</th>
            <th class="px-3 py-2 text-left">보호대상</th>
            <th class="px-3 py-2 text-center">응답</th>
            <th class="px-3 py-2 text-center">시도</th>
            <th class="px-3 py-2 text-center">알림</th>
            <th class="px-3 py-2 text-left">비고</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in callLogs" :key="c.id" class="border-b">
            <td class="px-3 py-2 text-gray-500">{{ formatDateTime(c.called_at) }}</td>
            <td class="px-3 py-2">{{ c.guardian_name }}</td>
            <td class="px-3 py-2">{{ c.ward_name }}</td>
            <td class="px-3 py-2 text-center">
              <span v-if="c.answered" class="text-green-600">✅</span>
              <span v-else class="text-red-500">❌</span>
            </td>
            <td class="px-3 py-2 text-center">{{ c.attempts }}</td>
            <td class="px-3 py-2 text-center">
              <span v-if="c.guardian_notified" class="text-amber-600">알림</span>
            </td>
            <td class="px-3 py-2 text-gray-500 text-[10px]">{{ c.notes }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- SOS 로그 -->
  <div v-else-if="tab==='sos'">
    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!sosLogs.length" class="text-center py-8 text-gray-400">SOS 기록이 없습니다</div>
    <div v-else class="space-y-2">
      <div v-for="s in sosLogs" :key="s.id" class="bg-white rounded-lg border p-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span v-if="!s.resolved_at" class="bg-red-100 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded-full">🚨 미해결</span>
            <span v-else class="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5 rounded-full">✅ 해결</span>
            <span class="text-sm font-bold">{{ s.user?.name }}</span>
          </div>
          <span class="text-[10px] text-gray-400">{{ formatDateTime(s.created_at) }}</span>
        </div>
        <div class="text-xs text-gray-600 mt-1">{{ s.message }}</div>
      </div>
    </div>
  </div>

  <!-- 체크인 로그 -->
  <div v-else-if="tab==='checkins'">
    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!checkins.length" class="text-center py-8 text-gray-400">체크인 기록이 없습니다</div>
    <div v-else class="bg-white rounded-lg border">
      <table class="w-full text-xs">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="px-3 py-2 text-left">사용자</th>
            <th class="px-3 py-2 text-left">체크인 시각</th>
            <th class="px-3 py-2 text-left">상태</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in checkins" :key="c.id" class="border-b">
            <td class="px-3 py-2">{{ c.user?.name }}</td>
            <td class="px-3 py-2 text-gray-500">{{ formatDateTime(c.checked_in_at) }}</td>
            <td class="px-3 py-2">{{ c.status || '정상' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const overview = ref({})
const tab = ref('guardians')
const loading = ref(false)
const search = ref('')
const statusFilter = ref('')
const guardians = ref([])
const callLogs = ref([])
const sosLogs = ref([])
const checkins = ref([])

const tabs = [
  { key: 'guardians', label: '매칭 관리' },
  { key: 'calls', label: '통화 로그' },
  { key: 'sos', label: 'SOS 로그' },
  { key: 'checkins', label: '체크인' },
]

function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString('ko-KR') : '' }
function formatDateTime(dt) { return dt ? new Date(dt).toLocaleString('ko-KR') : '' }

async function loadOverview() {
  try { const { data } = await axios.get('/api/admin/elder/overview'); overview.value = data.data || {} } catch {}
}

async function loadGuardians() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/admin/elder/guardians', { params: { search: search.value, status: statusFilter.value } })
    guardians.value = data.data?.data || []
  } catch {}
  loading.value = false
}

async function loadCalls() {
  loading.value = true
  try { const { data } = await axios.get('/api/admin/elder/call-logs'); callLogs.value = data.data?.data || [] } catch {}
  loading.value = false
}

async function loadSos() {
  loading.value = true
  try { const { data } = await axios.get('/api/admin/elder/sos'); sosLogs.value = data.data?.data || [] } catch {}
  loading.value = false
}

async function loadCheckins() {
  loading.value = true
  try { const { data } = await axios.get('/api/admin/elder/checkins'); checkins.value = data.data?.data || [] } catch {}
  loading.value = false
}

function loadData() {
  if (tab.value === 'guardians') loadGuardians()
  else if (tab.value === 'calls') loadCalls()
  else if (tab.value === 'sos') loadSos()
  else if (tab.value === 'checkins') loadCheckins()
}

async function deleteGuardian(g) {
  if (!confirm('이 매칭을 해제하시겠습니까? 관련 스케줄과 통화 기록이 모두 삭제됩니다.')) return
  try {
    await axios.delete(`/api/admin/elder/guardians/${g.id}`)
    loadGuardians()
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

onMounted(() => {
  loadOverview()
  loadGuardians()
})
</script>
