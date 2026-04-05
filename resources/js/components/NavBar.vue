<template>
  <nav class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50">
    <!-- Row 1: Logo + Search + Actions -->
    <div class="max-w-[1200px] mx-auto px-4 flex items-center h-14 gap-3">
      <!-- Logo -->
      <RouterLink to="/" class="flex-shrink-0">
        <img :src="siteStore.logoUrl || '/images/logo_00.jpg'" alt="SomeKorean"
          class="h-8 rounded" @error="e => e.target.src = '/images/logo_00.jpg'" />
      </RouterLink>

      <!-- Search bar (desktop) -->
      <form @submit.prevent="goSearch" class="flex-1 max-w-xs hidden md:flex">
        <div class="relative w-full">
          <input v-model="searchQ" type="text" :placeholder="$t('common.search') + '...'"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-1.5 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 transition" />
          <button type="submit" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-500">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </button>
        </div>
      </form>

      <!-- Search icon (mobile) -->
      <button @click="mobileSearchOpen = !mobileSearchOpen" class="md:hidden p-1.5 text-gray-500 hover:text-blue-600">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </button>

      <!-- Right Side -->
      <div class="ml-auto flex items-center gap-2 flex-shrink-0">
        <!-- Logged In State -->
        <template v-if="auth.isLoggedIn">
          <!-- Notifications -->
          <RouterLink to="/notifications" class="relative p-1.5 text-gray-500 hover:text-blue-600">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
            <span v-if="unreadNotifs > 0"
              class="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white text-[10px] rounded-full flex items-center justify-center font-bold">
              {{ unreadNotifs > 9 ? '9+' : unreadNotifs }}
            </span>
          </RouterLink>

          <!-- Messages (desktop) -->
          <RouterLink to="/messages" class="p-1.5 text-gray-500 hover:text-blue-600 hidden sm:block">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </RouterLink>

          <!-- Points badge (desktop) -->
          <RouterLink to="/points" class="hidden md:flex items-center gap-1 text-xs text-yellow-600 font-bold bg-yellow-50 px-2.5 py-1 rounded-lg hover:bg-yellow-100 transition">
            {{ (auth.user?.points_total ?? 0).toLocaleString() }}P
          </RouterLink>

          <!-- Admin link -->
          <RouterLink v-if="auth.isAdmin" to="/admin"
            class="hidden lg:flex items-center text-xs text-purple-600 font-semibold bg-purple-50 px-2.5 py-1 rounded-lg hover:bg-purple-100 transition">
            {{ $t('nav.admin') }}
          </RouterLink>

          <!-- User avatar -->
          <RouterLink to="/dashboard"
            class="w-8 h-8 rounded-full overflow-hidden bg-blue-500 text-white flex items-center justify-center text-sm font-bold hover:ring-2 hover:ring-blue-300 flex-shrink-0 transition">
            <img v-if="auth.user?.avatar" :src="auth.user.avatar" class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
            <span v-if="!auth.user?.avatar">{{ (auth.user?.name || '?')[0] }}</span>
          </RouterLink>

          <!-- Logout (large screens) -->
          <button @click="handleLogout" class="text-xs text-gray-400 hover:text-red-400 hidden lg:block ml-1">
            {{ $t('auth.logout') }}
          </button>
        </template>

        <!-- Guest State -->
        <template v-else>
          <RouterLink to="/login" class="text-sm text-gray-600 hover:text-blue-600 px-3 py-1 hidden sm:block">
            {{ $t('auth.login') }}
          </RouterLink>
          <RouterLink to="/register" class="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 hidden sm:block">
            {{ $t('auth.register') }}
          </RouterLink>
        </template>

        <!-- Language toggle -->
        <button @click="langStore.toggle()"
          class="flex items-center text-xs font-bold px-2.5 py-1 rounded-lg border transition ml-1 flex-shrink-0"
          :class="langStore.locale === 'en' ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-blue-300'">
          {{ langStore.locale === 'ko' ? 'EN' : '\uD55C' }}
        </button>

        <!-- Mobile hamburger -->
        <button @click="drawerOpen = true" class="md:hidden p-1.5 text-gray-600 hover:text-blue-600 ml-0.5">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile Search (expandable) -->
    <div v-if="mobileSearchOpen" class="md:hidden px-4 pb-3 border-t border-gray-100">
      <form @submit.prevent="goSearch" class="mt-2">
        <div class="relative">
          <input v-model="searchQ" type="text" :placeholder="$t('common.search') + '...'" autofocus
            class="w-full border border-gray-200 rounded-lg px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          <button type="submit" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-blue-500">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </button>
        </div>
      </form>
    </div>

    <!-- Row 2: Desktop navigation links -->
    <div class="border-t border-gray-100 bg-gray-50/80 hidden md:block">
      <div class="max-w-[1200px] mx-auto px-4 flex items-center h-9 overflow-x-auto scrollbar-hide gap-0.5">
        <RouterLink v-for="item in visibleDesktopNav" :key="item.key"
          :to="item.to"
          class="text-xs text-gray-600 hover:text-blue-600 px-2.5 py-1.5 rounded-md hover:bg-blue-50 transition font-semibold whitespace-nowrap"
          :class="{ 'text-blue-600 bg-blue-50': isActive(item.to) }">
          {{ item.label }}
        </RouterLink>
      </div>
    </div>

    <!-- Mobile Drawer -->
    <Teleport to="body">
      <Transition name="drawer-fade">
        <div v-if="drawerOpen" class="fixed inset-0 z-[200] md:hidden" role="dialog">
          <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="drawerOpen = false"></div>

          <Transition name="drawer-slide" appear>
            <div v-if="drawerOpen" class="absolute right-0 top-0 h-full w-72 bg-white shadow-2xl flex flex-col">
              <!-- Drawer header -->
              <div class="flex items-center justify-between px-4 h-14 bg-blue-600 text-white flex-shrink-0">
                <span class="font-bold text-sm">SomeKorean</span>
                <button @click="drawerOpen = false" class="p-1 text-white/80 hover:text-white">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>

              <!-- User section -->
              <div v-if="auth.isLoggedIn" class="px-4 py-3 bg-blue-50 border-b flex items-center gap-3 flex-shrink-0">
                <RouterLink @click="drawerOpen = false" to="/dashboard"
                  class="w-10 h-10 rounded-full overflow-hidden bg-blue-500 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                  <img v-if="auth.user?.avatar" :src="auth.user.avatar" class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
                  <span v-if="!auth.user?.avatar">{{ (auth.user?.name || '?')[0] }}</span>
                </RouterLink>
                <div class="flex-1 min-w-0">
                  <div class="font-semibold text-gray-800 text-sm truncate">{{ auth.user?.name }}</div>
                  <div class="text-xs text-yellow-600">{{ (auth.user?.points_total ?? 0).toLocaleString() }}P</div>
                </div>
              </div>
              <div v-else class="px-4 py-3 bg-blue-50 border-b flex gap-2 flex-shrink-0">
                <RouterLink @click="drawerOpen = false" to="/login"
                  class="flex-1 text-center py-2 border border-blue-600 text-blue-600 rounded-lg text-sm font-semibold">
                  {{ $t('auth.login') }}
                </RouterLink>
                <RouterLink @click="drawerOpen = false" to="/register"
                  class="flex-1 text-center py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold">
                  {{ $t('auth.register') }}
                </RouterLink>
              </div>

              <!-- Drawer nav links -->
              <div class="flex-1 overflow-y-auto">
                <RouterLink v-for="item in visibleNavItems" :key="item.key"
                  :to="item.to" @click="drawerOpen = false"
                  class="flex items-center gap-3 px-4 py-3 hover:bg-blue-50 transition border-b border-gray-50 text-gray-700 hover:text-blue-600">
                  <span class="text-lg w-6 text-center flex-shrink-0">{{ item.icon }}</span>
                  <span class="text-sm font-medium">{{ item.label }}</span>
                </RouterLink>

                <!-- Admin link in drawer -->
                <RouterLink v-if="auth.isAdmin" to="/admin" @click="drawerOpen = false"
                  class="flex items-center gap-3 px-4 py-3 hover:bg-purple-50 transition border-b border-gray-50 text-purple-600">
                  <span class="text-lg w-6 text-center flex-shrink-0">&#x2699;&#xFE0F;</span>
                  <span class="text-sm font-medium">{{ $t('nav.admin') }}</span>
                </RouterLink>
              </div>

              <!-- Drawer bottom -->
              <div class="border-t px-4 py-3 flex items-center gap-2 flex-shrink-0 bg-gray-50">
                <button @click="langStore.toggle()"
                  class="flex-1 py-2 text-xs font-bold rounded-lg border text-center transition"
                  :class="langStore.locale === 'en' ? 'bg-blue-50 border-blue-300 text-blue-700' : 'bg-white border-gray-200 text-gray-600'">
                  {{ langStore.locale === 'ko' ? 'English' : '\uD55C\uAD6D\uC5B4' }}
                </button>
                <button v-if="auth.isLoggedIn" @click="logoutAndClose"
                  class="flex-1 py-2 text-xs font-bold rounded-lg border border-red-200 text-red-500 bg-red-50 hover:bg-red-100 transition">
                  {{ $t('auth.logout') }}
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useLangStore } from '../stores/lang'
import { useSiteStore } from '../stores/site'
import axios from 'axios'

const auth = useAuthStore()
const langStore = useLangStore()
const siteStore = useSiteStore()
const router = useRouter()
const route = useRoute()

const searchQ = ref('')
const mobileSearchOpen = ref(false)
const drawerOpen = ref(false)
const unreadNotifs = ref(0)

function $t(key) { return langStore.$t(key) }

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path === path || route.path.startsWith(path + '/')
}

function goSearch() {
  if (!searchQ.value.trim()) return
  router.push({ name: 'search', query: { q: searchQ.value } })
  searchQ.value = ''
  mobileSearchOpen.value = false
}

async function handleLogout() {
  await auth.logout()
  router.push('/')
}

async function logoutAndClose() {
  drawerOpen.value = false
  await auth.logout()
  router.push('/')
}

// All nav items with menu key for admin filtering
const allNavItems = computed(() => [
  { key: 'community',  to: '/community',  icon: '\uD83D\uDCAC', label: $t('nav.community') },
  { key: 'clubs',      to: '/clubs',      icon: '\uD83D\uDC65', label: $t('nav.clubs') },
  { key: 'qa',         to: '/qa',         icon: '\u2753',       label: $t('nav.qa') },
  { key: 'jobs',       to: '/jobs',       icon: '\uD83D\uDCBC', label: $t('nav.jobs') },
  { key: 'market',     to: '/market',     icon: '\uD83D\uDED2', label: $t('nav.market') },
  { key: 'realestate', to: '/realestate', icon: '\uD83C\uDFE0', label: $t('nav.realestate') },
  { key: 'directory',  to: '/directory',  icon: '\uD83C\uDFEA', label: $t('nav.directory') },
  { key: 'events',     to: '/events',     icon: '\uD83C\uDF89', label: $t('nav.events') },
  { key: 'news',       to: '/news',       icon: '\uD83D\uDCF0', label: $t('nav.news') },
  { key: 'recipes',    to: '/recipes',    icon: '\uD83C\uDF73', label: $t('nav.recipes') },
  { key: 'games',      to: '/games',      icon: '\uD83C\uDFAE', label: $t('nav.games') },
  { key: 'shorts',     to: '/shorts',     icon: '\uD83D\uDCF1', label: $t('nav.shorts') },
  { key: 'music',      to: '/music',      icon: '\uD83C\uDFB5', label: $t('nav.music') },
  { key: 'groupbuy',   to: '/groupbuy',   icon: '\uD83E\uDD1D', label: $t('nav.groupbuy') },
  { key: 'elder',      to: '/elder',      icon: '\uD83D\uDC99', label: $t('nav.elder') },
  { key: 'chat',       to: '/chat',       icon: '\uD83D\uDCAC', label: $t('nav.chat') },
  { key: 'friends',    to: '/friends',    icon: '\uD83D\uDC6B', label: $t('nav.friends') },
  { key: 'points',     to: '/points',     icon: '\u2B50',       label: $t('nav.points') },
  { key: 'messages',   to: '/messages',   icon: '\u2709\uFE0F', label: $t('nav.messages') },
])

// Filtered by admin settings
const visibleNavItems = computed(() =>
  allNavItems.value
    .filter(item => siteStore.isEnabled(item.key))
    .sort((a, b) => siteStore.getOrder(a.key) - siteStore.getOrder(b.key))
)

// Desktop nav excludes items that have dedicated icons (points, messages)
const visibleDesktopNav = computed(() =>
  visibleNavItems.value.filter(item => !['points', 'messages'].includes(item.key))
)

// Fetch unread notifications on mount
onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      const { data } = await axios.get('/api/notifications/unread')
      unreadNotifs.value = data.count || 0
    } catch { /* ignore */ }
  }
})
</script>

<style scoped>
.drawer-fade-enter-active, .drawer-fade-leave-active { transition: opacity 0.25s; }
.drawer-fade-enter-from, .drawer-fade-leave-to { opacity: 0; }
.drawer-slide-enter-active, .drawer-slide-leave-active { transition: transform 0.25s ease; }
.drawer-slide-enter-from, .drawer-slide-leave-to { transform: translateX(100%); }
</style>
