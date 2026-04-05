<template>
  <div id="app" :class="{ 'dark': isDark }">
    <!-- Toast Notifications -->
    <Teleport to="body">
      <div class="fixed top-4 right-4 z-[9999] space-y-2">
        <TransitionGroup name="toast">
          <div v-for="toast in siteStore.toasts" :key="toast.id"
            class="flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium max-w-sm"
            :class="{
              'bg-green-500 text-white': toast.type === 'success',
              'bg-red-500 text-white': toast.type === 'error',
              'bg-yellow-500 text-white': toast.type === 'warning',
              'bg-blue-500 text-white': toast.type === 'info',
            }">
            <span>{{ toast.message }}</span>
            <button @click="siteStore.removeToast(toast.id)" class="ml-auto opacity-70 hover:opacity-100">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </TransitionGroup>
      </div>
    </Teleport>

    <!-- NavBar (hidden on auth pages, admin pages, fullscreen games) -->
    <NavBar v-if="showNav" />

    <!-- Main Content -->
    <main :class="mainClass">
      <router-view v-slot="{ Component }">
        <keep-alive :include="cachedViews">
          <component :is="Component" />
        </keep-alive>
      </router-view>
    </main>

    <!-- BottomNav (mobile only, hidden on auth/admin/fullscreen) -->
    <BottomNav v-if="showBottomNav" />

    <!-- Music MiniPlayer (global) -->
    <MiniPlayer v-if="musicStore.hasTrack" />

    <!-- Bottom padding for mobile nav -->
    <div v-if="showBottomNav" class="h-16 md:hidden"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useSiteStore } from './stores/site'
import { useMusicStore } from './stores/music'
import NavBar from './components/NavBar.vue'
import BottomNav from './components/BottomNav.vue'
import MiniPlayer from './components/MiniPlayer.vue'

const route = useRoute()
const siteStore = useSiteStore()
const musicStore = useMusicStore()

const isDark = computed(() => siteStore.darkMode)

const isAuthPage = computed(() =>
  route.path === '/login' || route.path === '/register'
)
const isAdminPage = computed(() => route.path.startsWith('/admin'))
const isFullscreen = computed(() => {
  const fullscreenPaths = [
    '/games/gostop', '/games/blackjack', '/games/poker',
    '/games/holdem', '/games/omok', '/games/2048'
  ]
  return fullscreenPaths.includes(route.path)
})

const showNav = computed(() => !isAuthPage.value && !isAdminPage.value && !isFullscreen.value)
const showBottomNav = computed(() => !isAuthPage.value && !isAdminPage.value && !isFullscreen.value)

const cachedViews = ['Home', 'BoardList', 'NewsList']

const mainClass = computed(() => {
  if (isFullscreen.value) return ''
  if (isAdminPage.value) return ''
  return 'min-h-screen bg-gray-50 dark:bg-gray-900'
})
</script>

<style>
/* CSS Variables for theming */
:root {
  --color-primary: #3B82F6;
  --color-primary-dark: #2563EB;
  --color-primary-light: #93C5FD;
  --color-accent: #F59E0B;
  --color-bg: #F9FAFB;
  --color-surface: #FFFFFF;
  --color-text: #111827;
  --color-text-secondary: #6B7280;
  --color-border: #E5E7EB;
}

.dark {
  --color-bg: #111827;
  --color-surface: #1F2937;
  --color-text: #F9FAFB;
  --color-text-secondary: #9CA3AF;
  --color-border: #374151;
}

/* Toast transitions */
.toast-enter-active { transition: all 0.3s ease; }
.toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from { transform: translateX(100%); opacity: 0; }
.toast-leave-to { transform: translateX(100%); opacity: 0; }
.toast-move { transition: transform 0.3s ease; }

/* Scrollbar hide utility */
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
