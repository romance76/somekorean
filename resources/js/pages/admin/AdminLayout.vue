<template>
  <div class="min-h-screen bg-gray-100 flex">
    <!-- Mobile overlay -->
    <div v-if="sidebarOpen" class="fixed inset-0 z-40 lg:hidden" @click="sidebarOpen = false">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
    </div>

    <!-- Sidebar -->
    <aside class="fixed top-0 left-0 h-full w-60 bg-slate-900 text-white z-50 flex flex-col transition-transform duration-300"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'">

      <!-- Logo -->
      <div class="flex items-center gap-2.5 px-4 py-3.5 border-b border-slate-700/80 flex-shrink-0">
        <div class="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center font-black text-sm">SK</div>
        <div class="flex-1 min-w-0">
          <div class="font-black text-sm text-white leading-tight">SomeKorean</div>
          <div class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">Admin Panel</div>
        </div>
        <button @click="sidebarOpen = false" class="lg:hidden text-slate-400 hover:text-white p-0.5">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <!-- Quick actions -->
      <div class="px-3 py-2 flex items-center gap-1 border-b border-slate-700/50 flex-shrink-0">
        <a href="/" target="_blank"
          class="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition flex-1 justify-center">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
          </svg>
          사이트 보기
        </a>
        <button @click="logout"
          class="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg text-red-400 hover:text-red-300 hover:bg-slate-800 transition flex-1 justify-center">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
          로그아웃
        </button>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto py-2 px-2 scrollbar-thin">
        <div v-for="group in navGroups" :key="group.label" class="mb-0.5">
          <button @click="toggleGroup(group.label)"
            class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left hover:bg-slate-800/60 transition-colors group">
            <span class="text-base leading-none">{{ group.icon }}</span>
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex-1 group-hover:text-slate-300">{{ group.label }}</span>
            <span class="text-[9px] text-slate-600 bg-slate-800 rounded px-1 py-0.5 font-mono">{{ group.items.length }}</span>
            <svg class="w-2.5 h-2.5 text-slate-600 flex-shrink-0 transition-transform duration-200"
              :class="openGroups[group.label] ? 'rotate-90' : ''"
              fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/>
            </svg>
          </button>

          <div class="overflow-hidden transition-all duration-200 ease-in-out"
            :style="openGroups[group.label]
              ? { maxHeight: group.items.length * 38 + 8 + 'px', opacity: '1' }
              : { maxHeight: '0px', opacity: '0' }">
            <div class="mt-0.5 ml-2 pl-2 border-l border-slate-700/50 space-y-0.5 pb-1">
              <router-link v-for="item in group.items" :key="item.to" :to="item.to"
                @click="sidebarOpen = false"
                class="flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px] font-medium transition-all"
                :class="isActive(item.to)
                  ? 'bg-red-600 text-white shadow-sm'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'">
                <span class="text-sm w-4 text-center flex-shrink-0 leading-none">{{ item.icon }}</span>
                <span class="flex-1 leading-tight">{{ item.label }}</span>
              </router-link>
            </div>
          </div>
        </div>
      </nav>

      <!-- Footer -->
      <div class="px-4 py-2 border-t border-slate-700/50 flex-shrink-0">
        <p class="text-[10px] text-slate-600 text-center">SomeKorean Admin v2.0</p>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col min-w-0 lg:ml-60">
      <!-- Top header -->
      <header class="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 sticky top-0 z-30 shadow-sm">
        <button @click="sidebarOpen = true" class="lg:hidden p-1.5 text-gray-500 hover:text-gray-800 hover:bg-gray-100 rounded-lg">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <div class="flex items-center gap-2">
          <span class="text-xs text-gray-400 hidden sm:block">관리자</span>
          <svg class="w-3 h-3 text-gray-300 hidden sm:block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
          <h1 class="font-bold text-gray-800 text-sm">{{ currentTitle }}</h1>
        </div>

        <div class="ml-auto flex items-center gap-3">
          <span class="text-xs text-gray-400 hidden md:block font-mono">{{ currentTime }}</span>
          <div class="flex items-center gap-2">
            <span class="text-xs text-gray-500 hidden sm:block">{{ auth.user?.nickname || auth.user?.name }}</span>
            <div class="w-8 h-8 rounded-full bg-red-600 text-white flex items-center justify-center text-sm font-bold shadow-sm">
              {{ (auth.user?.nickname || auth.user?.name || 'A')[0].toUpperCase() }}
            </div>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="flex-1 p-4 md:p-6 overflow-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const sidebarOpen = ref(false)
const currentTime = ref('')

let timer
onMounted(() => {
  const update = () => {
    currentTime.value = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }
  update()
  timer = setInterval(update, 1000)
})
onUnmounted(() => clearInterval(timer))

const navGroups = [
  {
    label: '대시보드', icon: '📊',
    items: [
      { to: '/admin/overview', icon: '📊', label: '전체 현황' },
      { to: '/admin/dashboard', icon: '📈', label: '커뮤니티 통계' },
    ]
  },
  {
    label: '회원 관리', icon: '👥',
    items: [
      { to: '/admin/members', icon: '👤', label: '회원 목록' },
      { to: '/admin/content', icon: '🚨', label: '콘텐츠 관리' },
      { to: '/admin/friends', icon: '👫', label: '친구 관리' },
    ]
  },
  {
    label: '게시판', icon: '📋',
    items: [
      { to: '/admin/boards', icon: '📋', label: '게시판 관리' },
    ]
  },
  {
    label: '커뮤니티', icon: '💬',
    items: [
      { to: '/admin/clubs', icon: '🤝', label: '동호회' },
      { to: '/admin/events-admin', icon: '🎉', label: '이벤트' },
      { to: '/admin/chats', icon: '💬', label: '채팅방' },
    ]
  },
  {
    label: '콘텐츠', icon: '📱',
    items: [
      { to: '/admin/news-admin', icon: '📰', label: '뉴스' },
      { to: '/admin/qa-admin', icon: '❓', label: 'Q&A' },
      { to: '/admin/recipes-admin', icon: '🍳', label: '레시피' },
      { to: '/admin/shorts-admin', icon: '📱', label: '숏츠' },
      { to: '/admin/music-admin', icon: '🎵', label: '음악' },
      { to: '/admin/shopping-admin', icon: '🛍️', label: '쇼핑' },
    ]
  },
  {
    label: '비즈니스', icon: '🏪',
    items: [
      { to: '/admin/jobs', icon: '💼', label: '구인구직' },
      { to: '/admin/market', icon: '🛒', label: '중고장터' },
      { to: '/admin/realestate-admin', icon: '🏠', label: '부동산' },
      { to: '/admin/business', icon: '🏪', label: '업소록' },
    ]
  },
  {
    label: '서비스', icon: '🛡️',
    items: [
      { to: '/admin/groupbuy', icon: '🤲', label: '공동구매' },
      { to: '/admin/elder', icon: '💙', label: '안심서비스' },
    ]
  },
  {
    label: '게임/포인트', icon: '🎮',
    items: [
      { to: '/admin/games-admin', icon: '🎮', label: '게임 관리' },
      { to: '/admin/payments', icon: '💰', label: '결제/포인트' },
    ]
  },
  {
    label: '운영', icon: '⚙️',
    items: [
      { to: '/admin/security', icon: '🛡️', label: '보안' },
      { to: '/admin/site', icon: '⚙️', label: '사이트 설정' },
      { to: '/admin/banners', icon: '📢', label: '배너/광고' },
      { to: '/admin/system', icon: '🖥️', label: '시스템' },
    ]
  },
]

function getInitialOpenGroups() {
  const result = {}
  navGroups.forEach(g => {
    result[g.label] = g.items.some(item => route.path === item.to || route.path.startsWith(item.to + '/'))
  })
  result['대시보드'] = true
  return result
}

const openGroups = ref(getInitialOpenGroups())

watch(() => route.path, (newPath) => {
  navGroups.forEach(g => {
    if (g.items.some(item => newPath === item.to || newPath.startsWith(item.to + '/'))) {
      openGroups.value[g.label] = true
    }
  })
})

function toggleGroup(label) { openGroups.value[label] = !openGroups.value[label] }

const titleMap = {}
navGroups.forEach(g => g.items.forEach(item => { titleMap[item.to] = `${item.icon} ${item.label}` }))

const currentTitle = computed(() => titleMap[route.path] || '관리자 패널')
function isActive(to) { return route.path === to || route.path.startsWith(to + '/') }

async function logout() {
  await auth.logout()
  router.push('/')
}
</script>
