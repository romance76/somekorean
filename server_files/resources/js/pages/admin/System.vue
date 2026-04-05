<template>
  <div class="space-y-5">

    <!-- 서버 정보 카드 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-gradient-to-br from-slate-700 to-slate-800 text-white rounded-xl p-5">
        <div class="text-slate-400 text-xs font-semibold mb-1">서버</div>
        <div class="font-bold text-sm">DigitalOcean</div>
        <div class="text-slate-300 text-xs mt-1">68.183.60.70</div>
      </div>
      <div class="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-5">
        <div class="text-blue-200 text-xs font-semibold mb-1">도메인</div>
        <div class="font-bold text-sm">somekorean.com</div>
        <div class="text-blue-200 text-xs mt-1">HTTPS 활성화</div>
      </div>
      <div class="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-5">
        <div class="text-green-200 text-xs font-semibold mb-1">스택</div>
        <div class="font-bold text-sm">Laravel 11 + Vue 3</div>
        <div class="text-green-200 text-xs mt-1">MySQL 8 + Reverb WS</div>
      </div>
    </div>

    <!-- DB 현황 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">🗄️ DB 현황</h3>
      <div v-if="loadingStats" class="text-center py-6 text-gray-400 text-sm">불러오는 중...</div>
      <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        <div v-for="s in dbStats" :key="s.label" class="bg-gray-50 rounded-xl p-3 text-center">
          <div class="text-xl font-black text-gray-800">{{ s.value.toLocaleString() }}</div>
          <div class="text-[10px] text-gray-400 mt-0.5">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- 공지 / 점검 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">📢 공지사항 관리</h3>
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">공지 제목</label>
          <input v-model="notice.title" type="text" placeholder="공지 제목 입력..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">내용</label>
          <textarea v-model="notice.content" rows="4" placeholder="공지 내용..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 resize-none"></textarea>
        </div>
        <div class="flex gap-3">
          <button @click="saveNotice"
            class="bg-blue-500 hover:bg-blue-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition">
            공지 저장
          </button>
          <span v-if="noticeSaved" class="text-green-600 text-sm flex items-center">✓ 저장됨</span>
        </div>
      </div>
    </div>

    <!-- 점검 모드 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">🔧 시스템 설정</h3>
      <div class="space-y-4">
        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
          <div>
            <div class="text-sm font-semibold text-gray-800">점검 모드</div>
            <div class="text-xs text-gray-400">활성화 시 일반 회원 접근 차단</div>
          </div>
          <button @click="toggleMaintenance"
            :class="['relative w-12 h-6 rounded-full transition-colors',
              maintenanceMode ? 'bg-red-500' : 'bg-gray-200']">
            <span :class="['absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
              maintenanceMode ? 'translate-x-6' : 'translate-x-0.5']"></span>
          </button>
        </div>

        <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
          <div>
            <div class="text-sm font-semibold text-gray-800">회원가입 허용</div>
            <div class="text-xs text-gray-400">비활성화 시 신규 가입 차단</div>
          </div>
          <button @click="registrationOpen = !registrationOpen"
            :class="['relative w-12 h-6 rounded-full transition-colors',
              registrationOpen ? 'bg-green-500' : 'bg-gray-200']">
            <span :class="['absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
              registrationOpen ? 'translate-x-6' : 'translate-x-0.5']"></span>
          </button>
        </div>
      </div>
    </div>

    <!-- 빠른 명령 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">⚡ 빠른 작업</h3>
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <button v-for="cmd in commands" :key="cmd.label" @click="runCommand(cmd)"
          :class="['p-3 rounded-xl border text-left transition', cmd.danger
            ? 'border-red-200 bg-red-50 hover:bg-red-100'
            : 'border-gray-200 bg-gray-50 hover:bg-gray-100']">
          <div class="text-lg mb-1">{{ cmd.icon }}</div>
          <div :class="['text-xs font-semibold', cmd.danger ? 'text-red-600' : 'text-gray-700']">{{ cmd.label }}</div>
          <div class="text-[10px] text-gray-400">{{ cmd.desc }}</div>
        </button>
      </div>
    </div>

    <!-- 토스트 -->
    <div v-if="toast" class="fixed bottom-6 right-6 bg-gray-800 text-white text-sm px-4 py-2.5 rounded-xl shadow-lg z-50 transition">
      {{ toast }}
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loadingStats    = ref(true)
const dbStats         = ref([])
const maintenanceMode = ref(false)
const registrationOpen = ref(true)
const notice          = ref({ title: '', content: '' })
const noticeSaved     = ref(false)
const toast           = ref('')

const commands = [
  { icon: '🗑️', label: '캐시 초기화', desc: 'Artisan cache:clear', key: 'cache' },
  { icon: '📦', label: '큐 재시작',   desc: 'Queue worker restart', key: 'queue' },
  { icon: '📊', label: '통계 새로고침', desc: 'Stats cache refresh', key: 'stats' },
  { icon: '🗃️', label: 'DB 백업',     desc: 'Database export', key: 'backup', danger: false },
]

async function loadStats() {
  try {
    const res = await axios.get('/api/admin/stats')
    const s = res.data
    dbStats.value = [
      { label: '전체 회원', value: s.users ?? 0 },
      { label: '게시글', value: s.posts ?? 0 },
      { label: '구인구직', value: s.jobs ?? 0 },
      { label: '중고장터', value: s.market ?? 0 },
      { label: '업소록', value: s.businesses ?? 0 },
      { label: '채팅방', value: s.chat_rooms ?? 0 },
      { label: '동호회', value: s.clubs ?? 0 },
      { label: '공동구매', value: s.group_buys ?? 0 },
      { label: '멘토', value: s.mentors ?? 0 },
      { label: '라이드', value: s.rides ?? 0 },
      { label: '정지회원', value: s.banned_users ?? 0 },
      { label: '미처리신고', value: s.reports ?? 0 },
    ]
  } finally {
    loadingStats.value = false
  }
}

function saveNotice() {
  // TODO: POST /api/admin/notice
  noticeSaved.value = true
  setTimeout(() => noticeSaved.value = false, 2000)
}

function toggleMaintenance() {
  maintenanceMode.value = !maintenanceMode.value
  showToast(maintenanceMode.value ? '점검 모드 활성화' : '점검 모드 해제')
}

function runCommand(cmd) {
  showToast(`${cmd.label} 실행 요청됨`)
  // TODO: POST /api/admin/system/command with cmd.key
}

function showToast(msg) {
  toast.value = msg
  setTimeout(() => toast.value = '', 2500)
}

onMounted(loadStats)
</script>
