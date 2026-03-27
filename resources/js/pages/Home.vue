<template>
  <div>
    <!-- 히어로 배너 -->
    <section class="bg-gradient-to-r from-red-600 to-red-800 text-white py-12 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <h1 class="text-3xl md:text-4xl font-bold mb-3">미국 한인 커뮤니티</h1>
        <p class="text-red-100 text-lg mb-6">정보 공유, 구인구직, 중고장터, 한인 업소 — 한 곳에서</p>
        <div class="flex justify-center space-x-3">
          <router-link to="/community" class="bg-white text-red-600 px-6 py-2.5 rounded-full font-semibold hover:bg-red-50 transition">커뮤니티 보기</router-link>
          <router-link to="/auth/register" v-if="!authStore.isLoggedIn" class="border-2 border-white text-white px-6 py-2.5 rounded-full font-semibold hover:bg-white hover:text-red-600 transition">무료 가입</router-link>
        </div>
      </div>
    </section>

    <!-- 출석체크 배너 (로그인 시) -->
    <div v-if="authStore.isLoggedIn && !checkedIn" class="bg-yellow-50 border-b border-yellow-200 py-2 px-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <span class="text-yellow-800 text-sm">🌟 오늘 출석체크 하고 포인트 받으세요!</span>
        <button @click="doCheckin" :disabled="checkingIn" class="bg-yellow-500 text-white text-xs px-4 py-1.5 rounded-full hover:bg-yellow-600 disabled:opacity-50">
          {{ checkingIn ? '처리 중...' : '출석체크 (+10P)' }}
        </button>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <router-link v-for="card in serviceCards" :key="card.to" :to="card.to"
          class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition border border-gray-100 flex flex-col items-center text-center">
          <div class="text-3xl mb-2">{{ card.emoji }}</div>
          <h3 class="font-bold text-gray-800 mb-1">{{ card.title }}</h3>
          <p class="text-gray-500 text-xs">{{ card.desc }}</p>
        </router-link>
      </div>

      <!-- 최신 게시글 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 자유게시판 최신글 -->
        <div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100">
            <h2 class="font-bold text-gray-800">📋 최신 게시글</h2>
            <router-link to="/community" class="text-red-600 text-sm hover:underline">더보기</router-link>
          </div>
          <div v-if="loading" class="p-5 text-center text-gray-400 text-sm">불러오는 중...</div>
          <ul v-else>
            <li v-for="post in recentPosts" :key="post.id" class="px-5 py-3 border-b border-gray-50 hover:bg-gray-50 last:border-0">
              <router-link :to="`/community/post/${post.id}`" class="flex items-start justify-between">
                <div class="flex-1 min-w-0 mr-4">
                  <span class="text-xs text-red-500 font-medium mr-2">{{ post.board?.name }}</span>
                  <span class="text-gray-800 text-sm truncate">{{ post.title }}</span>
                </div>
                <div class="flex items-center space-x-2 text-xs text-gray-400 flex-shrink-0">
                  <span>👍 {{ post.like_count }}</span>
                  <span>💬 {{ post.comment_count }}</span>
                </div>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- 사이드바 -->
        <div class="space-y-4">
          <!-- 내 정보 (로그인 시) -->
          <div v-if="authStore.isLoggedIn" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <div class="flex items-center space-x-3 mb-3">
              <div class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <span class="text-red-600 font-bold">{{ authStore.user?.name?.[0] }}</span>
              </div>
              <div>
                <p class="font-semibold text-gray-800 text-sm">{{ authStore.user?.name }}</p>
                <p class="text-xs text-red-500">{{ authStore.user?.level }} · {{ authStore.user?.points?.toLocaleString() }}P</p>
              </div>
            </div>
            <router-link to="/points" class="block w-full text-center bg-red-50 text-red-600 text-sm py-2 rounded-lg hover:bg-red-100 font-medium">포인트 현황 보기</router-link>
          </div>

          <!-- 구인구직 최신 -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100">
              <h3 class="font-bold text-gray-800 text-sm">💼 최신 채용</h3>
              <router-link to="/jobs" class="text-red-600 text-xs hover:underline">더보기</router-link>
            </div>
            <ul>
              <li v-for="job in recentJobs" :key="job.id" class="px-4 py-2.5 border-b border-gray-50 last:border-0 hover:bg-gray-50">
                <router-link :to="`/jobs/${job.id}`">
                  <p class="text-gray-800 text-sm truncate">{{ job.title }}</p>
                  <p class="text-gray-400 text-xs">{{ job.company_name || '회사명 비공개' }} · {{ job.region }}</p>
                </router-link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import axios from 'axios';

const authStore = useAuthStore();
const recentPosts = ref([]);
const recentJobs = ref([]);
const loading = ref(true);
const checkedIn = ref(false);
const checkingIn = ref(false);

const serviceCards = [
    { to: '/community', emoji: '💬', title: '커뮤니티', desc: '한인들과 정보 교류' },
    { to: '/jobs',      emoji: '💼', title: '구인구직', desc: '일자리 찾기 & 채용' },
    { to: '/market',    emoji: '🛍️', title: '중고장터', desc: '물건 사고팔기' },
    { to: '/directory', emoji: '🏪', title: '한인 업소록', desc: '가까운 한인 업소 찾기' },
];

async function doCheckin() {
    checkingIn.value = true;
    try {
        const { data } = await axios.post('/api/points/checkin');
        checkedIn.value = true;
        await authStore.fetchMe();
        alert(data.message);
    } catch(e) {
        if (e.response?.data?.message) alert(e.response.data.message);
        checkedIn.value = true;
    } finally {
        checkingIn.value = false;
    }
}

onMounted(async () => {
    try {
        const [postsRes, jobsRes] = await Promise.all([
            axios.get('/api/posts?per_page=8'),
            axios.get('/api/jobs?per_page=5'),
        ]);
        recentPosts.value = postsRes.data.data || [];
        recentJobs.value = jobsRes.data.data || [];
    } catch {}
    loading.value = false;
});
</script>
