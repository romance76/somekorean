<template>
  <div class="min-h-screen bg-gray-100 flex">

    <!-- ── 사이드바 오버레이 (모바일) ── -->
    <div v-if="sidebarOpen" class="fixed inset-0 z-40 lg:hidden">
      <div class="absolute inset-0 bg-black/50" @click="sidebarOpen = false"></div>
    </div>

    <!-- ── 사이드바 ── -->
    <aside
      class="fixed top-0 left-0 h-full w-60 bg-slate-900 text-white z-50 flex flex-col transition-transform duration-300"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'">

      <!-- 로고 -->
      <div class="flex items-center gap-2 px-5 py-4 border-b border-slate-700 flex-shrink-0">
        <span class="text-xl">🇰🇷</span>
        <div>
          <div class="font-black text-sm text-white leading-tight">SomeKorean</div>
          <div class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Admin Panel</div>
        </div>
        <button @click="sidebarOpen = false" class="ml-auto lg:hidden text-slate-400 hover:text-white">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- 퀵 액션 (사이트 보기 / 로그아웃) -->
      <div class="border-b border-slate-700 px-3 py-2 flex items-center gap-2 flex-shrink-0">
        <a href="/" target="_blank"
          class="flex items-center gap-1.5 text-xs px-2 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition">
          <span>🌐</span> 사이트 보기
        </a>
        <button @click="logout"
          class="flex items-center gap-1.5 text-xs px-2 py-1.5 rounded-lg text-red-400 hover:text-red-300 hover:bg-slate-800 transition">
          <span>🚪</span> 로그아웃
        </button>
      </div>

      <!-- 네비게이션 (스크롤 가능) -->
      <nav class="flex-1 overflow-y-auto py-3 px-2 space-y-1">
        <div v-for="group in navGroups" :key="group.label" class="mb-1">

          <!-- 그룹 헤더 (클릭 시 토글) -->
          <button
            @click="toggleGroup(group.label)"
            class="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-left transition-colors hover:bg-slate-800">
            <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider flex-1">
              {{ group.label }}
            </span>
            <span class="text-[10px] text-slate-600 font-semibold">
              {{ group.items.length }}
            </span>
            <!-- 화살표: 열리면 아래(▼), 닫히면 오른쪽(▶) -->
            <svg
              class="w-3 h-3 text-slate-500 flex-shrink-0 transition-transform duration-200"
              :class="openGroups[group.label] ? 'rotate-90' : 'rotate-0'"
              fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>
            </svg>
          </button>

          <!-- 그룹 아이템 (아코디언, max-height 트랜지션) -->
          <div
            class="overflow-hidden transition-all duration-200 ease-in-out"
            :style="openGroups[group.label]
              ? { maxHeight: group.items.length * 44 + 'px', opacity: '1' }
              : { maxHeight: '0px', opacity: '0' }">
            <div class="mt-0.5 space-y-0.5">
              <RouterLink
                v-for="item in group.items"
                :key="item.to"
                :to="item.to"
                @click="sidebarOpen = false"
                class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all"
                :class="isActive(item.to)
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'">
                <span class="text-base w-5 text-center flex-shrink-0">{{ item.icon }}</span>
                <span class="flex-1">{{ item.label }}</span>
                <span v-if="item.badge" class="text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded-full font-bold">
                  {{ item.badge }}
                </span>
              </RouterLink>
            </div>
          </div>

        </div>
      </nav>

    </aside>

    <!-- ── 메인 영역 ── -->
    <div class="flex-1 flex flex-col min-w-0 lg:ml-60">

      <!-- 상단 헤더 -->
      <header class="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 sticky top-0 z-30">
        <!-- 햄버거 (모바일) -->
        <button @click="sidebarOpen = true" class="lg:hidden p-1 text-gray-500 hover:text-gray-800">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <!-- 페이지 타이틀 -->
        <h1 class="font-bold text-gray-800 text-sm">{{ currentTitle }}</h1>

        <!-- 오른쪽 -->
        <div class="ml-auto flex items-center gap-3">
          <span class="text-xs text-gray-400 hidden sm:block">{{ auth.user?.name }}</span>
          <div class="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-bold">
            {{ (auth.user?.name || 'A')[0] }}
          </div>
        </div>
      </header>

      <!-- 페이지 컨텐츠 -->
      <main class="flex-1 p-4 md:p-6 overflow-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth        = useAuthStore()
const route       = useRoute()
const router      = useRouter()
const sidebarOpen = ref(false)

const navGroups = [
  {
    label: '현황',
    items: [
      { to: '/admin/overview',         icon: '📊', label: '대시보드' },
    ]
  },
  {
    label: '회원 관리',
    items: [
      { to: '/admin/members',          icon: '👤', label: '회원 목록' },
      { to: '/admin/content',          icon: '🚨', label: '신고/콘텐츠' },
      { to: '/admin/friends',          icon: '👫', label: '친구 관리' },
      { to: '/admin/matching',         icon: '💕', label: '매칭 관리' },
    ]
  },
  {
    label: '커뮤니티',
    items: [
      { to: '/admin/boards',           icon: '💬', label: '게시판 관리' },
      { to: '/admin/clubs',            icon: '🤝', label: '동호회 관리' },
      { to: '/admin/events-admin',     icon: '🎉', label: '이벤트 관리' },
    ]
  },
  {
    label: '거래/서비스',
    items: [
      { to: '/admin/jobs',             icon: '💼', label: '구인구직' },
      { to: '/admin/market',           icon: '🛒', label: '중고장터' },
      { to: '/admin/realestate-admin', icon: '🏠', label: '부동산' },
      { to: '/admin/business',         icon: '🏪', label: '업소록' },
    ]
  },
  {
    label: '생활/특별',
    items: [
      { to: '/admin/rides',            icon: '🚗', label: '알바라이드' },
      { to: '/admin/groupbuy',         icon: '🤲', label: '공동구매' },
      { to: '/admin/elder',            icon: '💙', label: '노인안심' },
      { to: '/admin/mentor-admin',     icon: '🎓', label: '멘토링' },
    ]
  },
  {
    label: '미디어',
    items: [
      { to: '/admin/news-admin',       icon: '📰', label: '뉴스 관리' },
      { to: '/admin/qa-admin',         icon: '❓', label: 'Q&A 관리' },
      { to: '/admin/recipes-admin',    icon: '🍳', label: '레시피 관리' },
      { to: '/admin/shorts-admin',     icon: '📱', label: '숏츠 관리' },
      { to: '/admin/shopping-admin',   icon: '🛍️', label: '쇼핑정보' },
      { to: '/admin/ai-admin',         icon: '🤖', label: 'AI검색' },
    ]
  },
  {
    label: '게임',
    items: [
      { to: '/admin/games-admin',      icon: '🎮', label: '게임 관리' },
    ]
  },
  {
    label: '운영 관리',
    items: [
      { to: '/admin/chats',            icon: '💬', label: '채팅방 관리' },
      { to: '/admin/payments',         icon: '💳', label: '결제 관리' },
      { to: '/admin/banners',          icon: '📢', label: '배너/광고' },
    ]
  },
  {
    label: '설정',
    items: [
      { to: '/admin/menus',            icon: '🔧', label: '메뉴 설정' },
      { to: '/admin/boards',           icon: '📋', label: '게시판 설정' },
      { to: '/admin/site',             icon: '⚙️', label: '사이트 설정' },
    ]
  },
]

// 모든 그룹 기본 열림 상태로 초기화
const openGroups = ref(
  Object.fromEntries(navGroups.map(g => [g.label, true]))
)

// 현재 활성 라우트가 포함된 그룹을 자동으로 열기
function autoOpenActiveGroup(path) {
  for (const group of navGroups) {
    const hasActive = group.items.some(
      item => path === item.to || path.startsWith(item.to + '/')
    )
    if (hasActive) {
      openGroups.value[group.label] = true
    }
  }
}

// 라우트 변경 시 해당 그룹 자동 열기
watch(() => route.path, (newPath) => {
  autoOpenActiveGroup(newPath)
}, { immediate: true })

function toggleGroup(label) {
  openGroups.value[label] = !openGroups.value[label]
}

const titleMap = {
  '/admin/overview':         '대시보드',
  '/admin/members':          '회원 목록',
  '/admin/users':            '회원 관리',
  '/admin/content':          '신고/콘텐츠 관리',
  '/admin/friends':          '친구 관리',
  '/admin/matching':         '매칭 관리',
  '/admin/boards':           '게시판 관리',
  '/admin/clubs':            '동호회 관리',
  '/admin/events-admin':     '이벤트 관리',
  '/admin/jobs':             '구인구직 관리',
  '/admin/market':           '중고장터 관리',
  '/admin/realestate-admin': '부동산 관리',
  '/admin/business':         '업소록 관리',
  '/admin/rides':            '알바라이드 관리',
  '/admin/groupbuy':         '공동구매 관리',
  '/admin/elder':            '노인 안심 모니터링',
  '/admin/mentor-admin':     '멘토링 관리',
  '/admin/news-admin':       '뉴스 관리',
  '/admin/shorts-admin':     '숏츠 관리',
  '/admin/shopping-admin':   '쇼핑정보 관리',
  '/admin/ai-admin':         'AI검색 관리',
  '/admin/games-admin':      '게임 관리',
  '/admin/chats':            '채팅방 관리',
  '/admin/payments':         '결제 관리',
  '/admin/banners':          '배너/광고 관리',
  '/admin/menus':            '메뉴 설정',
  '/admin/site':             '사이트 설정',
  '/admin/system':           '시스템 설정',
}

const currentTitle = computed(() => titleMap[route.path] || '관리자 패널')

function isActive(to) {
  return route.path === to || route.path.startsWith(to + '/')
}

async function logout() {
  await auth.logout()
  router.push('/')
}
</script>
