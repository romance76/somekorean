<template>
  <div class="space-y-6">

    <!-- 탭 네비게이션 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-1 flex gap-1">
      <button v-for="tab in tabs" :key="tab.key"
        @click="activeTab = tab.key"
        class="flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold transition-all"
        :class="activeTab === tab.key
          ? 'bg-blue-600 text-white shadow-sm'
          : 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'">
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <!-- ====================== IP 차단 탭 ====================== -->
    <div v-if="activeTab === 'ip'" class="space-y-4">

      <!-- 통계 카드 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">전체 차단</p>
          <p class="text-2xl font-black text-gray-800 mt-1">{{ ipStats.total }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">활성 차단</p>
          <p class="text-2xl font-black text-red-600 mt-1">{{ ipStats.active }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">자동 차단</p>
          <p class="text-2xl font-black text-orange-600 mt-1">{{ ipStats.auto_blocked }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">영구 차단</p>
          <p class="text-2xl font-black text-purple-600 mt-1">{{ ipStats.permanent }}</p>
        </div>
      </div>

      <!-- IP 추가 폼 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 class="text-sm font-bold text-gray-700 mb-3">IP 차단 추가</h3>
        <div class="flex flex-wrap gap-3">
          <input v-model="newBan.ip_address" placeholder="IP 주소 (예: 192.168.1.1)"
            class="flex-1 min-w-[180px] px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
          <input v-model="newBan.reason" placeholder="차단 사유"
            class="flex-1 min-w-[200px] px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
          <select v-model="newBan.duration"
            class="px-3 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none">
            <option value="1h">1시간</option>
            <option value="1d">1일</option>
            <option value="7d">7일</option>
            <option value="30d">30일</option>
            <option value="permanent">영구</option>
          </select>
          <button @click="addIpBan" :disabled="!newBan.ip_address || !newBan.reason"
            class="px-5 py-2 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed">
            차단 추가
          </button>
        </div>
      </div>

      <!-- 차단 목록 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
          <h3 class="text-sm font-bold text-gray-700">차단 목록</h3>
          <div class="flex gap-2">
            <select v-model="ipFilter" @change="loadIpBans"
              class="text-xs px-2 py-1 border border-gray-200 rounded-lg">
              <option value="">전체</option>
              <option value="active">활성</option>
              <option value="expired">만료</option>
            </select>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th class="px-4 py-2.5 text-left">IP 주소</th>
                <th class="px-4 py-2.5 text-left">사유</th>
                <th class="px-4 py-2.5 text-left">만료일</th>
                <th class="px-4 py-2.5 text-left">차단일</th>
                <th class="px-4 py-2.5 text-center">상태</th>
                <th class="px-4 py-2.5 text-center">작업</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="ban in ipBans" :key="ban.id" class="hover:bg-gray-50/50">
                <td class="px-4 py-2.5 font-mono font-semibold text-gray-800">{{ ban.ip_address }}</td>
                <td class="px-4 py-2.5 text-gray-600 max-w-[250px] truncate">{{ ban.reason }}</td>
                <td class="px-4 py-2.5 text-gray-500">{{ ban.expires_at ? formatDate(ban.expires_at) : '영구' }}</td>
                <td class="px-4 py-2.5 text-gray-400">{{ formatDate(ban.created_at) }}</td>
                <td class="px-4 py-2.5 text-center">
                  <span v-if="!ban.expires_at || new Date(ban.expires_at) > new Date()"
                    class="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-red-100 text-red-700">활성</span>
                  <span v-else
                    class="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-500">만료</span>
                </td>
                <td class="px-4 py-2.5 text-center">
                  <button @click="removeIpBan(ban.id)"
                    class="text-xs text-blue-600 hover:text-blue-800 font-semibold">해제</button>
                </td>
              </tr>
              <tr v-if="!ipBans.length">
                <td colspan="6" class="px-4 py-8 text-center text-gray-400">차단된 IP가 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 페이지네이션 -->
        <div v-if="ipPagination.last_page > 1" class="px-5 py-3 border-t border-gray-100 flex justify-center gap-1">
          <button v-for="page in ipPagination.last_page" :key="page"
            @click="loadIpBans(page)"
            class="px-3 py-1 text-xs rounded-lg"
            :class="page === ipPagination.current_page ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100'">
            {{ page }}
          </button>
        </div>
      </div>
    </div>

    <!-- ====================== 신고 관리 탭 ====================== -->
    <div v-if="activeTab === 'reports'" class="space-y-4">

      <!-- 통계 카드 -->
      <div class="grid grid-cols-3 gap-3">
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">전체 신고</p>
          <p class="text-2xl font-black text-gray-800 mt-1">{{ reportStats.total }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">대기 중</p>
          <p class="text-2xl font-black text-yellow-600 mt-1">{{ reportStats.pending }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">오늘 접수</p>
          <p class="text-2xl font-black text-blue-600 mt-1">{{ reportStats.today }}</p>
        </div>
      </div>

      <!-- 필터 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex gap-3 flex-wrap">
        <select v-model="reportFilter.status" @change="loadReports"
          class="text-sm px-3 py-2 border border-gray-200 rounded-lg">
          <option value="">전체 상태</option>
          <option value="pending">대기 중</option>
          <option value="resolved">처리 완료</option>
          <option value="dismissed">무시</option>
        </select>
        <select v-model="reportFilter.type" @change="loadReports"
          class="text-sm px-3 py-2 border border-gray-200 rounded-lg">
          <option value="">전체 유형</option>
          <option value="Post">게시글</option>
          <option value="Comment">댓글</option>
          <option value="MarketItem">중고장터</option>
          <option value="JobPost">구인구직</option>
          <option value="User">회원</option>
        </select>
      </div>

      <!-- 신고 목록 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th class="px-4 py-2.5 text-left">ID</th>
                <th class="px-4 py-2.5 text-left">유형</th>
                <th class="px-4 py-2.5 text-left">대상 ID</th>
                <th class="px-4 py-2.5 text-left">사유</th>
                <th class="px-4 py-2.5 text-left">신고자</th>
                <th class="px-4 py-2.5 text-left">일시</th>
                <th class="px-4 py-2.5 text-center">상태</th>
                <th class="px-4 py-2.5 text-center">작업</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="report in reportList" :key="report.id" class="hover:bg-gray-50/50">
                <td class="px-4 py-2.5 text-gray-400 font-mono">#{{ report.id }}</td>
                <td class="px-4 py-2.5">
                  <span class="inline-block px-2 py-0.5 text-xs font-semibold rounded-full"
                    :class="typeColor(report.reportable_type)">
                    {{ shortType(report.reportable_type) }}
                  </span>
                </td>
                <td class="px-4 py-2.5 font-mono text-gray-600">#{{ report.reportable_id }}</td>
                <td class="px-4 py-2.5 text-gray-600">{{ reasonLabel(report.reason) }}</td>
                <td class="px-4 py-2.5 text-gray-600">{{ report.reporter_name || report.reporter_username || '-' }}</td>
                <td class="px-4 py-2.5 text-gray-400">{{ formatDate(report.created_at) }}</td>
                <td class="px-4 py-2.5 text-center">
                  <span class="inline-block px-2 py-0.5 text-xs font-semibold rounded-full"
                    :class="statusColor(report.status)">
                    {{ statusLabel(report.status) }}
                  </span>
                </td>
                <td class="px-4 py-2.5 text-center">
                  <div v-if="report.status === 'pending'" class="flex gap-1 justify-center">
                    <button @click="processReport(report.id, 'dismiss')"
                      class="px-2 py-1 text-xs text-gray-500 hover:bg-gray-100 rounded font-medium">무시</button>
                    <button @click="processReport(report.id, 'hide')"
                      class="px-2 py-1 text-xs text-yellow-600 hover:bg-yellow-50 rounded font-medium">숨김</button>
                    <button @click="processReport(report.id, 'delete')"
                      class="px-2 py-1 text-xs text-red-600 hover:bg-red-50 rounded font-medium">삭제</button>
                    <button @click="processReport(report.id, 'ban_user')"
                      class="px-2 py-1 text-xs text-purple-600 hover:bg-purple-50 rounded font-medium">차단</button>
                  </div>
                  <span v-else class="text-xs text-gray-400">{{ report.resolved_action || '완료' }}</span>
                </td>
              </tr>
              <tr v-if="!reportList.length">
                <td colspan="8" class="px-4 py-8 text-center text-gray-400">신고 내역이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="reportPagination.last_page > 1" class="px-5 py-3 border-t border-gray-100 flex justify-center gap-1">
          <button v-for="page in reportPagination.last_page" :key="page"
            @click="loadReports(page)"
            class="px-3 py-1 text-xs rounded-lg"
            :class="page === reportPagination.current_page ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100'">
            {{ page }}
          </button>
        </div>
      </div>
    </div>

    <!-- ====================== 봇 활동 탭 ====================== -->
    <div v-if="activeTab === 'bot'" class="space-y-4">

      <!-- 통계 카드 -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">자동 차단 전체</p>
          <p class="text-2xl font-black text-gray-800 mt-1">{{ botStats.total_auto }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">1시간 내</p>
          <p class="text-2xl font-black text-red-600 mt-1">{{ botStats.last_hour }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">24시간 내</p>
          <p class="text-2xl font-black text-orange-600 mt-1">{{ botStats.last_24h }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">Honeypot 감지</p>
          <p class="text-2xl font-black text-purple-600 mt-1">{{ botStats.honeypot_count }}</p>
        </div>
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
          <p class="text-xs text-gray-400 font-medium">속도 제한</p>
          <p class="text-2xl font-black text-blue-600 mt-1">{{ botStats.rate_limit_count }}</p>
        </div>
      </div>

      <!-- 봇 활동 로그 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-100">
          <h3 class="text-sm font-bold text-gray-700">자동 차단 로그</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                <th class="px-4 py-2.5 text-left">IP 주소</th>
                <th class="px-4 py-2.5 text-left">차단 사유</th>
                <th class="px-4 py-2.5 text-left">만료일</th>
                <th class="px-4 py-2.5 text-left">감지 시각</th>
                <th class="px-4 py-2.5 text-center">상태</th>
                <th class="px-4 py-2.5 text-center">작업</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="log in botLogs" :key="log.id" class="hover:bg-gray-50/50">
                <td class="px-4 py-2.5 font-mono font-semibold text-gray-800">{{ log.ip_address }}</td>
                <td class="px-4 py-2.5 text-gray-600">
                  <span class="inline-block px-2 py-0.5 text-xs font-semibold rounded-full"
                    :class="log.reason?.includes('Honeypot') ? 'bg-purple-100 text-purple-700' : 'bg-orange-100 text-orange-700'">
                    {{ log.reason?.includes('Honeypot') ? 'Honeypot' : '속도 제한' }}
                  </span>
                  <span class="text-xs text-gray-400 ml-1">{{ log.reason }}</span>
                </td>
                <td class="px-4 py-2.5 text-gray-500">{{ log.expires_at ? formatDate(log.expires_at) : '영구' }}</td>
                <td class="px-4 py-2.5 text-gray-400">{{ formatDate(log.created_at) }}</td>
                <td class="px-4 py-2.5 text-center">
                  <span v-if="!log.expires_at || new Date(log.expires_at) > new Date()"
                    class="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-red-100 text-red-700">활성</span>
                  <span v-else
                    class="inline-block px-2 py-0.5 text-xs font-semibold rounded-full bg-gray-100 text-gray-500">만료</span>
                </td>
                <td class="px-4 py-2.5 text-center">
                  <button @click="removeIpBan(log.id)"
                    class="text-xs text-blue-600 hover:text-blue-800 font-semibold">해제</button>
                </td>
              </tr>
              <tr v-if="!botLogs.length">
                <td colspan="6" class="px-4 py-8 text-center text-gray-400">자동 차단 기록이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="botPagination.last_page > 1" class="px-5 py-3 border-t border-gray-100 flex justify-center gap-1">
          <button v-for="page in botPagination.last_page" :key="page"
            @click="loadBotActivity(page)"
            class="px-3 py-1 text-xs rounded-lg"
            :class="page === botPagination.current_page ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100'">
            {{ page }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

const activeTab = ref('ip')

const tabs = [
  { key: 'ip',      icon: '', label: 'IP 차단' },
  { key: 'reports', icon: '', label: '신고 관리' },
  { key: 'bot',     icon: '', label: '봇 활동' },
]

// ── IP 차단 ────────────────────────────────────────────
const ipBans = ref([])
const ipStats = ref({ total: 0, active: 0, auto_blocked: 0, permanent: 0 })
const ipPagination = ref({ current_page: 1, last_page: 1 })
const ipFilter = ref('')
const newBan = reactive({ ip_address: '', reason: '', duration: '1d' })

async function loadIpBans(page = 1) {
  try {
    const { data } = await axios.get('/api/admin/security/ip-bans', {
      params: { page, status: ipFilter.value }
    })
    ipBans.value = data.bans?.data || []
    ipStats.value = data.stats || ipStats.value
    ipPagination.value = {
      current_page: data.bans?.current_page || 1,
      last_page: data.bans?.last_page || 1,
    }
  } catch (e) {
    console.error('IP bans load error:', e)
  }
}

async function addIpBan() {
  try {
    await axios.post('/api/admin/security/ip-bans', newBan)
    newBan.ip_address = ''
    newBan.reason = ''
    newBan.duration = '1d'
    loadIpBans()
  } catch (e) {
    alert(e.response?.data?.error || 'IP 차단 추가 실패')
  }
}

async function removeIpBan(id) {
  if (!confirm('IP 차단을 해제하시겠습니까?')) return
  try {
    await axios.delete(`/api/admin/security/ip-bans/${id}`)
    loadIpBans(ipPagination.value.current_page)
    loadBotActivity(botPagination.value.current_page)
  } catch (e) {
    alert('해제 실패')
  }
}

// ── 신고 관리 ──────────────────────────────────────────
const reportList = ref([])
const reportStats = ref({ total: 0, pending: 0, today: 0 })
const reportPagination = ref({ current_page: 1, last_page: 1 })
const reportFilter = reactive({ status: '', type: '' })

async function loadReports(page = 1) {
  try {
    const { data } = await axios.get('/api/admin/security/reports', {
      params: { page, status: reportFilter.status, type: reportFilter.type }
    })
    reportList.value = data.reports?.data || []
    reportStats.value = data.stats || reportStats.value
    reportPagination.value = {
      current_page: data.reports?.current_page || 1,
      last_page: data.reports?.last_page || 1,
    }
  } catch (e) {
    console.error('Reports load error:', e)
  }
}

async function processReport(id, action) {
  const labels = { dismiss: '무시', hide: '숨김', delete: '삭제', ban_user: '작성자 차단' }
  if (!confirm(`이 신고를 "${labels[action]}" 처리하시겠습니까?`)) return
  try {
    await axios.post(`/api/admin/security/reports/${id}/process`, { action })
    loadReports(reportPagination.value.current_page)
  } catch (e) {
    alert(e.response?.data?.error || '처리 실패')
  }
}

// ── 봇 활동 ────────────────────────────────────────────
const botLogs = ref([])
const botStats = ref({ total_auto: 0, last_hour: 0, last_24h: 0, honeypot_count: 0, rate_limit_count: 0 })
const botPagination = ref({ current_page: 1, last_page: 1 })

async function loadBotActivity(page = 1) {
  try {
    const { data } = await axios.get('/api/admin/security/bot-activity', { params: { page } })
    botLogs.value = data.logs?.data || []
    botStats.value = data.stats || botStats.value
    botPagination.value = {
      current_page: data.logs?.current_page || 1,
      last_page: data.logs?.last_page || 1,
    }
  } catch (e) {
    console.error('Bot activity load error:', e)
  }
}

// ── 유틸 ───────────────────────────────────────────────
function formatDate(d) {
  if (!d) return '-'
  const date = new Date(d)
  return `${date.getMonth()+1}/${date.getDate()} ${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`
}

function shortType(t) {
  if (!t) return '-'
  const map = { Post: '게시글', Comment: '댓글', MarketItem: '장터', JobPost: '구인', Business: '업소', User: '회원' }
  const name = t.split('\\').pop()
  return map[name] || name
}

function typeColor(t) {
  if (!t) return 'bg-gray-100 text-gray-600'
  const name = t.split('\\').pop()
  const map = {
    Post: 'bg-blue-100 text-blue-700',
    Comment: 'bg-green-100 text-green-700',
    MarketItem: 'bg-yellow-100 text-yellow-700',
    JobPost: 'bg-purple-100 text-purple-700',
    Business: 'bg-orange-100 text-orange-700',
    User: 'bg-red-100 text-red-700',
  }
  return map[name] || 'bg-gray-100 text-gray-600'
}

function reasonLabel(r) {
  const map = {
    spam: '스팸', illegal: '불법', obscene: '음란', advertisement: '광고',
    scam: '사기', inappropriate: '부적절', hate: '혐오', false_info: '허위정보', other: '기타'
  }
  return map[r] || r || '-'
}

function statusLabel(s) {
  const map = { pending: '대기', resolved: '처리완료', dismissed: '무시' }
  return map[s] || s || '-'
}

function statusColor(s) {
  const map = {
    pending: 'bg-yellow-100 text-yellow-700',
    resolved: 'bg-green-100 text-green-700',
    dismissed: 'bg-gray-100 text-gray-500',
  }
  return map[s] || 'bg-gray-100 text-gray-500'
}

// ── 초기 로드 ──────────────────────────────────────────
onMounted(() => {
  loadIpBans()
  loadReports()
  loadBotActivity()
})
</script>
