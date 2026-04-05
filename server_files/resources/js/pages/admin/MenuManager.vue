<template>
  <div class="space-y-5">

    <!-- 헤더 -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-bold text-gray-800">🗂️ 메뉴 ON/OFF 관리</h2>
        <p class="text-xs text-gray-400 mt-0.5">각 메뉴의 활성화 여부 및 접근 권한을 설정합니다</p>
      </div>
      <div class="flex items-center gap-3">
        <span v-if="toast.show" class="text-sm font-medium px-3 py-1.5 rounded-lg"
          :class="toast.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'">
          {{ toast.type === 'success' ? '✓' : '✗' }} {{ toast.message }}
        </span>
        <button @click="saveAll" :disabled="saving"
          class="bg-blue-500 hover:bg-blue-600 disabled:opacity-60 text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition flex items-center gap-2">
          <svg v-if="saving" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          {{ saving ? '저장 중...' : '전체 저장' }}
        </button>
      </div>
    </div>

    <!-- 통계 배지 -->
    <div class="grid grid-cols-3 gap-3">
      <div class="bg-green-50 border border-green-100 rounded-xl p-4 text-center">
        <div class="text-2xl font-black text-green-600">{{ enabledCount }}</div>
        <div class="text-xs text-green-500 mt-0.5">활성 메뉴</div>
      </div>
      <div class="bg-gray-50 border border-gray-100 rounded-xl p-4 text-center">
        <div class="text-2xl font-black text-gray-500">{{ menus.length - enabledCount }}</div>
        <div class="text-xs text-gray-400 mt-0.5">비활성 메뉴</div>
      </div>
      <div class="bg-blue-50 border border-blue-100 rounded-xl p-4 text-center">
        <div class="text-2xl font-black text-blue-600">{{ authRequiredCount }}</div>
        <div class="text-xs text-blue-500 mt-0.5">로그인 필요</div>
      </div>
    </div>

    <!-- 메뉴 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <!-- 테이블 헤더 -->
      <div class="grid grid-cols-12 gap-2 px-5 py-3 bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wide">
        <div class="col-span-5">메뉴</div>
        <div class="col-span-2 text-center">ON/OFF</div>
        <div class="col-span-2 text-center">로그인 필요</div>
        <div class="col-span-2 text-center">관리자만</div>
        <div class="col-span-1 text-center">저장</div>
      </div>

      <!-- 메뉴 행 목록 -->
      <div v-if="loading" class="py-12 text-center text-gray-400 text-sm">불러오는 중...</div>
      <div v-else>
        <div
          v-for="(menu, idx) in menus"
          :key="menu.key"
          class="grid grid-cols-12 gap-2 px-5 py-3.5 items-center border-b border-gray-50 last:border-0 hover:bg-gray-50/50 transition"
          :class="{ 'opacity-50': !menu.enabled }"
        >
          <!-- 메뉴 정보 -->
          <div class="col-span-5 flex items-center gap-3">
            <span class="text-xl w-7 text-center leading-none">{{ menu.icon }}</span>
            <div>
              <div class="font-semibold text-gray-800 text-sm">{{ menu.label_ko }}</div>
              <div class="text-xs text-gray-400">{{ menu.label_en }}</div>
            </div>
          </div>

          <!-- ON/OFF 토글 -->
          <div class="col-span-2 flex justify-center">
            <button
              @click="toggleEnabled(idx)"
              class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1"
              :class="menu.enabled ? 'bg-green-500 focus:ring-green-400' : 'bg-gray-300 focus:ring-gray-300'"
            >
              <span
                class="inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform"
                :class="menu.enabled ? 'translate-x-6' : 'translate-x-1'"
              />
            </button>
          </div>

          <!-- 로그인 필요 체크박스 -->
          <div class="col-span-2 flex justify-center">
            <input
              type="checkbox"
              v-model="menu.auth_required"
              :disabled="!menu.enabled"
              class="w-4 h-4 rounded border-gray-300 text-blue-500 focus:ring-blue-400 disabled:opacity-40 cursor-pointer"
            />
          </div>

          <!-- 관리자만 체크박스 -->
          <div class="col-span-2 flex justify-center">
            <input
              type="checkbox"
              v-model="menu.admin_only"
              :disabled="!menu.enabled"
              class="w-4 h-4 rounded border-gray-300 text-purple-500 focus:ring-purple-400 disabled:opacity-40 cursor-pointer"
            />
          </div>

          <!-- 개별 저장 버튼 -->
          <div class="col-span-1 flex justify-center">
            <button
              @click="saveOne(menu)"
              :disabled="savingKey === menu.key"
              class="text-xs text-blue-500 hover:text-blue-700 hover:bg-blue-50 px-2 py-1 rounded-lg transition disabled:opacity-50"
            >
              {{ savingKey === menu.key ? '...' : '저장' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 하단 전체 저장 -->
    <div class="flex justify-end">
      <button @click="saveAll" :disabled="saving"
        class="bg-blue-500 hover:bg-blue-600 disabled:opacity-60 text-white px-8 py-3 rounded-xl text-sm font-semibold transition">
        {{ saving ? '저장 중...' : '💾 전체 저장' }}
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// ─── 기본 메뉴 데이터 ───────────────────────────────────────────────────────
const defaultMenus = [
  { key: 'community',  icon: '📋', label_ko: '커뮤니티',  label_en: 'Community',   enabled: true,  auth_required: false, admin_only: false },
  { key: 'clubs',      icon: '👥', label_ko: '동호회',    label_en: 'Clubs',       enabled: true,  auth_required: false, admin_only: false },
  { key: 'jobs',       icon: '💼', label_ko: '구인구직',  label_en: 'Jobs',        enabled: true,  auth_required: false, admin_only: false },
  { key: 'market',     icon: '🛍️', label_ko: '중고장터',  label_en: 'Market',      enabled: true,  auth_required: false, admin_only: false },
  { key: 'realestate', icon: '🏠', label_ko: '부동산',    label_en: 'Real Estate', enabled: true,  auth_required: false, admin_only: false },
  { key: 'directory',  icon: '🏪', label_ko: '업소록',    label_en: 'Directory',   enabled: true,  auth_required: false, admin_only: false },
  { key: 'chat',       icon: '💬', label_ko: '채팅',      label_en: 'Chat',        enabled: true,  auth_required: true,  admin_only: false },
  { key: 'friends',    icon: '🤝', label_ko: '친구',      label_en: 'Friends',     enabled: true,  auth_required: true,  admin_only: false },
  { key: 'match',      icon: '💕', label_ko: '매칭',      label_en: 'Match',       enabled: true,  auth_required: true,  admin_only: false },
  { key: 'games',      icon: '🎮', label_ko: '게임',      label_en: 'Games',       enabled: true,  auth_required: false, admin_only: false },
  { key: 'events',     icon: '📅', label_ko: '이벤트',    label_en: 'Events',      enabled: true,  auth_required: false, admin_only: false },
  { key: 'ride',       icon: '🚗', label_ko: '라이드',    label_en: 'Ride',        enabled: true,  auth_required: false, admin_only: false },
  { key: 'elder',      icon: '💙', label_ko: '노인안심',  label_en: 'Elder Care',  enabled: true,  auth_required: true,  admin_only: false },
  { key: 'news',       icon: '📰', label_ko: '뉴스',      label_en: 'News',        enabled: true,  auth_required: false, admin_only: false },
  { key: 'shorts',     icon: '📱', label_ko: '숏츠',      label_en: 'Shorts',      enabled: true,  auth_required: false, admin_only: false },
  { key: 'shopping',   icon: '🛒', label_ko: '쇼핑정보',  label_en: 'Shopping',    enabled: true,  auth_required: false, admin_only: false },
  { key: 'groupbuy',   icon: '🤝', label_ko: '공동구매',  label_en: 'Group Buy',   enabled: true,  auth_required: false, admin_only: false },
  { key: 'mentor',     icon: '🎓', label_ko: '멘토링',    label_en: 'Mentoring',   enabled: true,  auth_required: false, admin_only: false },
  { key: 'ai',         icon: '🤖', label_ko: 'AI검색',    label_en: 'AI Search',   enabled: true,  auth_required: false, admin_only: false },
  { key: 'points',     icon: '⭐', label_ko: '포인트',    label_en: 'Points',      enabled: true,  auth_required: true,  admin_only: false },
  { key: 'music',      icon: '🎵', label_ko: '음악듣기',  label_en: 'Music',       enabled: true,  auth_required: false, admin_only: false },
]

// ─── 상태 ────────────────────────────────────────────────────────────────────
const menus   = ref([])
const loading = ref(false)
const saving  = ref(false)
const savingKey = ref(null)
const toast   = ref({ show: false, type: 'success', message: '' })

// ─── Computed ────────────────────────────────────────────────────────────────
const enabledCount      = computed(() => menus.value.filter(m => m.enabled).length)
const authRequiredCount = computed(() => menus.value.filter(m => m.auth_required).length)

// ─── 토스트 헬퍼 ──────────────────────────────────────────────────────────────
let toastTimer = null
function showToast(message, type = 'success') {
  clearTimeout(toastTimer)
  toast.value = { show: true, type, message }
  toastTimer = setTimeout(() => { toast.value.show = false }, 3000)
}

// ─── 토글 헬퍼 ────────────────────────────────────────────────────────────────
function toggleEnabled(idx) {
  menus.value[idx].enabled = !menus.value[idx].enabled
  if (!menus.value[idx].enabled) {
    menus.value[idx].auth_required = false
    menus.value[idx].admin_only    = false
  }
}

// ─── API: 개별 저장 ───────────────────────────────────────────────────────────
async function saveOne(menu) {
  savingKey.value = menu.key
  try {
    await axios.post(`/api/admin/settings/menus/${menu.key}`, {
      enabled:       menu.enabled,
      auth_required: menu.auth_required,
      admin_only:    menu.admin_only,
    })
    showToast(`${menu.label_ko} 저장 완료`)
  } catch {
    showToast(`${menu.label_ko} 저장 실패`, 'error')
  } finally {
    savingKey.value = null
  }
}

// ─── API: 전체 저장 ───────────────────────────────────────────────────────────
async function saveAll() {
  saving.value = true
  try {
    const payload = menus.value.map(m => ({
      key:           m.key,
      enabled:       m.enabled,
      auth_required: m.auth_required,
      admin_only:    m.admin_only,
    }))
    await axios.post('/api/admin/settings/menus/batch', { menus: payload })
    showToast('전체 메뉴 설정이 저장되었습니다')
  } catch {
    showToast('저장 중 오류가 발생했습니다', 'error')
  } finally {
    saving.value = false
  }
}

// ─── 마운트: 서버에서 메뉴 설정 로드 ─────────────────────────────────────────
onMounted(async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/api/admin/settings/menus')
    // 서버 응답을 기본값과 병합 (새 메뉴가 추가됐을 때 fallback)
    menus.value = defaultMenus.map(def => {
      const fromServer = data.find(s => s.key === def.key)
      return fromServer ? { ...def, ...fromServer } : { ...def }
    })
  } catch {
    menus.value = defaultMenus.map(m => ({ ...m }))
  } finally {
    loading.value = false
  }
})
</script>
