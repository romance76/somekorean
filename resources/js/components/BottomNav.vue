<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 z-50 md:hidden safe-bottom">
    <div class="grid grid-cols-5 h-16">
      <!-- Home -->
      <RouterLink to="/" class="bottom-nav-item" :class="{ active: $route.path === '/' }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
        <span>{{ $t('nav.home') }}</span>
      </RouterLink>

      <!-- Community -->
      <RouterLink to="/community" class="bottom-nav-item" :class="{ active: $route.path.startsWith('/community') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
        </svg>
        <span>{{ $t('nav.community') }}</span>
      </RouterLink>

      <!-- Games -->
      <RouterLink to="/games" class="bottom-nav-item" :class="{ active: $route.path.startsWith('/games') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <span>{{ $t('nav.games') }}</span>
      </RouterLink>

      <!-- Chat -->
      <RouterLink to="/chat" class="bottom-nav-item" :class="{ active: $route.path.startsWith('/chat') }">
        <div class="relative">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
          </svg>
          <span v-if="unreadChat > 0"
            class="absolute -top-1 -right-1 w-3.5 h-3.5 bg-red-500 text-white rounded-full flex items-center justify-center font-bold" style="font-size:9px">
            {{ unreadChat > 9 ? '9+' : unreadChat }}
          </span>
        </div>
        <span>{{ $t('nav.chat') }}</span>
      </RouterLink>

      <!-- My (Profile / Login) -->
      <RouterLink v-if="auth.isLoggedIn" to="/dashboard" class="bottom-nav-item"
        :class="{ active: $route.path === '/dashboard' || $route.path.startsWith('/profile') }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
        <span>MY</span>
      </RouterLink>
      <RouterLink v-else to="/login" class="bottom-nav-item">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
        <span>{{ $t('auth.login') }}</span>
      </RouterLink>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLangStore } from '../stores/lang'
import axios from 'axios'

const auth = useAuthStore()
const langStore = useLangStore()
const unreadChat = ref(0)

function $t(key) { return langStore.$t(key) }

onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      const { data } = await axios.get('/api/chat/unread-count')
      unreadChat.value = data.count || 0
    } catch { /* ignore */ }
  }
})
</script>

<style scoped>
.bottom-nav-item {
  @apply flex flex-col items-center justify-center gap-0.5 text-gray-400 text-[10px] py-2 transition;
}
.bottom-nav-item.active,
.bottom-nav-item.router-link-active {
  @apply text-blue-600 font-semibold;
}
.safe-bottom {
  padding-bottom: env(safe-area-inset-bottom, 0);
}
</style>
