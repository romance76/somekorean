<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">💙 안심서비스 관리</h1>

  <!-- 탭 -->
  <div class="flex gap-0 border-b mb-4 overflow-x-auto">
    <button v-for="t in tabs" :key="t.key" @click="switchTab(t.key)"
      class="px-4 py-2 text-sm font-bold border-b-2 transition whitespace-nowrap"
      :class="tab === t.key ? 'border-amber-500 text-amber-700' : 'border-transparent text-gray-400 hover:text-gray-600'">
      {{ t.icon }} {{ t.label }}
    </button>
  </div>

  <!-- 📊 통계 -->
  <div v-if="tab === 'overview'">
    <div v-if="overviewLoading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else class="grid grid-cols-2 lg:grid-cols-3 gap-3">
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-xs text-gray-500">활성 매칭</div>
        <div class="text-2xl font-black text-amber-600 mt-1">{{ overview.active_guardians || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-xs text-gray-500">대기 중 매칭</div>
        <div class="text-2xl font-black text-gray-600 mt-1">{{ overview.pending_guardians || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-xs text-gray-500">활성 스케줄</div>
        <div class="text-2xl font-black text-blue-600 mt-1">{{ overview.total_schedules || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-xs text-gray-500">오늘 통화</div>
        <div class="text-2xl font-black text-green-600 mt-1">{{ overview.calls_today || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-xs text-gray-500">오늘 체크인</div>
        <div class="text-2xl font-black text-emerald-600 mt-1">{{ overview.checkins_today || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border p-4">
        <div class="text-xs text-gray-500">미해결 SOS</div>
        <div class="text-2xl font-black text-red-600 mt-1">{{ overview.sos_unresolved || 0 }}</div>
      </div>
    </div>
  </div>

  <!-- 👫 매칭 -->
  <div v-else-if="tab === 'guardians'">
    <div class="bg-white rounded-xl shadow-sm border p-3 mb-3 flex gap-2">
      <input v-model="search" @keyup.enter="loadGuardians(1)" placeholder="보호자/보호대상 이름·이메일 검색..."
        class="flex-1 border rounded px-3 py-1.5 text-sm" />
      <select v-model="statusFilter" @change="loadGuardians(1)" class="border rounded px-3 py-1.5 text-sm">
        <option value="">전체</option>
        <option value="active">활성</option>
        <option value="pending">대기</option>
        <option value="rejected">거절</option>
      </select>
      <button @click="loadGuardians(1)" class="bg-amber-400 text-amber-900 font-bold px-4 py-1.5 rounded text-sm">검색</button>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!guardians.length" class="text-center py-8 text-gray-400">데이터 없음</div>
    <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="px-3 py-2 text-left text-xs text-gray-500">보호자</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">보호대상</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">상태</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">스케줄</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">등록일</th>
            <th class="px-3 py-2 text-xs text-gray-500">관리</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in guardians" :key="g.id" class="border-b last:border-0 hover:bg-amber-50/30">
            <td class="px-3 py-2.5">
              <div class="font-semibold text-gray-800 text-xs">{{ g.guardian_name || '-' }}</div>
              <div class="text-[10px] text-gray-400">{{ g.guardian_email }}</div>
            </td>
            <td class="px-3 py-2.5">
              <div class="font-semibold text-gray-800 text-xs">{{ g.ward_name || '-' }}</div>
              <div class="text-[10px] text-gray-400">{{ g.ward_email }}</div>
              <div v-if="g.ward_phone" class="text-[10px] text-gray-400">📞 {{ g.ward_phone }}</div>
            </td>
            <td class="px-3 py-2.5">
              <span class="text-[10px] px-2 py-0.5 rounded-full font-bold"
                :class="g.status === 'active' ? 'bg-green-100 text-green-700' : g.status === 'pending' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'">
                {{ g.status }}
              </span>
            </td>
            <td class="px-3 py-2.5 text-xs text-gray-600">
              <template v-if="g.schedule_type">
                <div class="font-semibold">{{ g.schedule_type === 'random' ? '랜덤' : '예약' }}</div>
                <div class="text-[10px] text-gray-400">{{ g.time_start }} ~ {{ g.time_end }} · {{ g.calls_per_day }}회/일</div>
              </template>
              <span v-else class="text-gray-400 text-[10px]">미설정</span>
            </td>
            <td class="px-3 py-2.5 text-[10px] text-gray-500">{{ fmt(g.created_at) }}</td>
            <td class="px-3 py-2.5 text-center">
              <button @click="deleteGuardian(g)" class="text-xs text-red-400 hover:text-red-600">해제</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
      <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="loadGuardians(pg)"
        class="px-3 py-1 rounded text-sm"
        :class="pg === page ? 'bg-amber-400 text-amber-900 font-bold' : 'bg-white border text-gray-600'">{{ pg }}</button>
    </div>
  </div>

  <!-- 📞 통화 -->
  <div v-else-if="tab === 'calls'">
    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!calls.length" class="text-center py-8 text-gray-400">통화 기록 없음</div>
    <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="px-3 py-2 text-left text-xs text-gray-500">시각</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">보호자</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">보호대상</th>
            <th class="px-3 py-2 text-center text-xs text-gray-500">응답</th>
            <th class="px-3 py-2 text-center text-xs text-gray-500">시도</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">노트</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in calls" :key="c.id" class="border-b last:border-0 hover:bg-amber-50/30">
            <td class="px-3 py-2.5 text-[11px] text-gray-500">{{ fmt(c.called_at) }}</td>
            <td class="px-3 py-2.5 text-xs">{{ c.guardian_name || '-' }}</td>
            <td class="px-3 py-2.5 text-xs">{{ c.ward_name || '-' }}</td>
            <td class="px-3 py-2.5 text-center">
              <span class="text-[10px] px-2 py-0.5 rounded-full font-bold"
                :class="c.answered ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                {{ c.answered ? '응답' : '미응답' }}
              </span>
            </td>
            <td class="px-3 py-2.5 text-center text-xs">{{ c.attempts }}</td>
            <td class="px-3 py-2.5 text-xs text-gray-500">{{ c.notes || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
      <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="loadCalls(pg)"
        class="px-3 py-1 rounded text-sm"
        :class="pg === page ? 'bg-amber-400 text-amber-900 font-bold' : 'bg-white border text-gray-600'">{{ pg }}</button>
    </div>
  </div>

  <!-- ✅ 체크인 -->
  <div v-else-if="tab === 'checkins'">
    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!checkins.length" class="text-center py-8 text-gray-400">체크인 없음</div>
    <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b">
          <tr>
            <th class="px-3 py-2 text-left text-xs text-gray-500">유저</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">시각</th>
            <th class="px-3 py-2 text-center text-xs text-gray-500">상태</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">위치</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in checkins" :key="c.id" class="border-b last:border-0 hover:bg-amber-50/30">
            <td class="px-3 py-2.5 text-xs">
              <div class="font-semibold">{{ c.user?.name || '-' }}</div>
              <div class="text-[10px] text-gray-400">{{ c.user?.email }}</div>
            </td>
            <td class="px-3 py-2.5 text-[11px] text-gray-500">{{ fmt(c.checked_in_at) }}</td>
            <td class="px-3 py-2.5 text-center">
              <span class="text-[10px] px-2 py-0.5 rounded-full font-bold"
                :class="c.status === 'ok' ? 'bg-green-100 text-green-700' : c.status === 'sos' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'">
                {{ c.status }}
              </span>
            </td>
            <td class="px-3 py-2.5 text-[10px] text-gray-500">
              <template v-if="c.lat && c.lng">{{ Number(c.lat).toFixed(4) }}, {{ Number(c.lng).toFixed(4) }}</template>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
      <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="loadCheckins(pg)"
        class="px-3 py-1 rounded text-sm"
        :class="pg === page ? 'bg-amber-400 text-amber-900 font-bold' : 'bg-white border text-gray-600'">{{ pg }}</button>
    </div>
  </div>

  <!-- 🚨 SOS -->
  <div v-else-if="tab === 'sos'">
    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!sosLogs.length" class="text-center py-8 text-gray-400">SOS 없음</div>
    <div v-else class="space-y-2">
      <div v-for="s in sosLogs" :key="s.id" class="bg-white rounded-xl shadow-sm border p-4">
        <div class="flex items-start justify-between gap-3">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-lg">🚨</span>
              <span class="font-bold text-gray-800">{{ s.user?.name || '-' }}</span>
              <span class="text-[10px] text-gray-400">{{ s.user?.email }}</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full font-bold ml-auto"
                :class="s.resolved_at ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                {{ s.resolved_at ? '해결' : '미해결' }}
              </span>
            </div>
            <div class="text-xs text-gray-600 mb-1">{{ s.message || '(메시지 없음)' }}</div>
            <div class="text-[10px] text-gray-400">
              {{ fmt(s.created_at) }}
              <template v-if="s.lat && s.lng"> · {{ Number(s.lat).toFixed(4) }}, {{ Number(s.lng).toFixed(4) }}</template>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
      <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="loadSos(pg)"
        class="px-3 py-1 rounded text-sm"
        :class="pg === page ? 'bg-amber-400 text-amber-900 font-bold' : 'bg-white border text-gray-600'">{{ pg }}</button>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tabs = [
  { key: 'overview', icon: '📊', label: '통계' },
  { key: 'guardians', icon: '👫', label: '매칭' },
  { key: 'calls', icon: '📞', label: '통화' },
  { key: 'checkins', icon: '✅', label: '체크인' },
  { key: 'sos', icon: '🚨', label: 'SOS' },
]
const tab = ref('overview')
const loading = ref(false)
const overviewLoading = ref(true)
const overview = ref({})
const guardians = ref([])
const calls = ref([])
const checkins = ref([])
const sosLogs = ref([])
const search = ref('')
const statusFilter = ref('')
const page = ref(1)
const lastPage = ref(1)

function fmt(v) {
  if (!v) return '-'
  try { return new Date(v).toLocaleString('ko-KR', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }
  catch { return v }
}

async function loadOverview() {
  overviewLoading.value = true
  try {
    const { data } = await axios.get('/api/admin/elder/overview')
    overview.value = data.data || {}
  } catch (e) {}
  overviewLoading.value = false
}

async function loadGuardians(p = 1) {
  loading.value = true
  page.value = p
  try {
    const { data } = await axios.get('/api/admin/elder/guardians', {
      params: { page: p, search: search.value, status: statusFilter.value }
    })
    guardians.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
  } catch (e) {}
  loading.value = false
}

async function deleteGuardian(g) {
  if (!confirm(`${g.guardian_name} ↔ ${g.ward_name} 매칭을 해제할까요?`)) return
  try {
    await axios.delete(`/api/admin/elder/guardians/${g.id}`)
    guardians.value = guardians.value.filter(x => x.id !== g.id)
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function loadCalls(p = 1) {
  loading.value = true
  page.value = p
  try {
    const { data } = await axios.get('/api/admin/elder/calls', { params: { page: p } })
    calls.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
  } catch (e) {}
  loading.value = false
}

async function loadCheckins(p = 1) {
  loading.value = true
  page.value = p
  try {
    const { data } = await axios.get('/api/admin/elder/checkins', { params: { page: p } })
    checkins.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
  } catch (e) {}
  loading.value = false
}

async function loadSos(p = 1) {
  loading.value = true
  page.value = p
  try {
    const { data } = await axios.get('/api/admin/elder/sos', { params: { page: p } })
    sosLogs.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
  } catch (e) {}
  loading.value = false
}

function switchTab(k) {
  tab.value = k
  page.value = 1
  lastPage.value = 1
  if (k === 'overview') loadOverview()
  else if (k === 'guardians') loadGuardians(1)
  else if (k === 'calls') loadCalls(1)
  else if (k === 'checkins') loadCheckins(1)
  else if (k === 'sos') loadSos(1)
}

onMounted(() => loadOverview())
</script>
