<template>
  <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex items-center justify-between h-14">
        <!-- 로고 -->
        <router-link to="/" class="flex items-center space-x-2">
          <span class="text-2xl font-bold text-red-600">SomeKorean</span>
        </router-link>

        <!-- 메뉴 (데스크탑) -->
        <div class="hidden md:flex items-center space-x-6">
          <router-link to="/community" class="text-gray-700 hover:text-red-600 font-medium text-sm">커뮤니티</router-link>
          <router-link to="/jobs"      class="text-gray-700 hover:text-red-600 font-medium text-sm">구인구직</router-link>
          <router-link to="/market"    class="text-gray-700 hover:text-red-600 font-medium text-sm">중고장터</router-link>
          <router-link to="/directory" class="text-gray-700 hover:text-red-600 font-medium text-sm">업소록</router-link>
        </div>

        <!-- 우측 버튼 -->
        <div class="flex items-center space-x-3">
          <template v-if="authStore.isLoggedIn">
            <router-link to="/messages" class="relative p-1.5 text-gray-500 hover:text-red-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
              </svg>
              <span v-if="unreadCount > 0" class="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">{{ unreadCount }}</span>
            </router-link>
            <router-link :to="`/profile/${authStore.user?.username}`" class="flex items-center space-x-1.5">
              <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center overflow-hidden">
                <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" class="w-full h-full object-cover" />
                <span v-else class="text-red-600 font-bold text-sm">{{ authStore.user?.name?.[0] }}</span>
              </div>
            </router-link>
            <button @click="handleLogout" class="text-sm text-gray-500 hover:text-red-600">로그아웃</button>
          </template>
          <template v-else>
            <router-link to="/auth/login"    class="text-sm text-gray-700 hover:text-red-600 font-medium">로그인</router-link>
            <router-link to="/auth/register" class="bg-red-600 text-white text-sm px-4 py-1.5 rounded-lg hover:bg-red-700 font-medium">회원가입</router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import axios from 'axios';

const authStore = useAuthStore();
const router = useRouter();
const unreadCount = ref(0);

async function handleLogout() {
    await authStore.logout();
    router.push('/');
}

onMounted(async () => {
    if (authStore.isLoggedIn) {
        try {
            const { data } = await axios.get('/api/messages/unread');
            unreadCount.value = data.unread_count;
        } catch {}
    }
});
</script>
