<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">

    <!-- 검색 영역 -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-500 rounded-2xl px-6 py-6 mb-8 shadow-lg">
      <h1 class="text-white text-xl font-black mb-1">커뮤니티</h1>
      <p class="text-blue-100 text-sm mb-4">함께 나누는 한인 커뮤니티</p>
      <div class="flex gap-2">
        <div class="relative flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="궁금한 것을 검색해보세요"
            class="w-full pl-10 pr-4 py-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
            @keyup.enter="handleSearch"
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <button
          @click="handleSearch"
          class="bg-white text-blue-600 px-5 py-3 rounded-xl text-sm font-semibold hover:bg-blue-50 transition"
        >
          검색
        </button>
        <router-link
          to="/community/write"
          class="bg-yellow-400 text-gray-900 px-5 py-3 rounded-xl text-sm font-semibold hover:bg-yellow-300 transition flex items-center gap-1"
        >
          ✏ 질문하기
        </router-link>
      </div>
    </div>

    <!-- 많이 본 Q&A -->
    <section class="mb-8">
      <h2 class="text-lg font-bold text-gray-800 mb-4">🔥 많이 본 Q&A</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="(item, idx) in popularQuestions"
          :key="item.id"
          class="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md transition cursor-pointer flex gap-3"
          @click="goToPost(item.id)"
        >
          <span class="text-2xl font-extrabold text-blue-500 leading-none min-w-[28px]">{{ idx + 1 }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-gray-800 truncate">{{ item.title }}</p>
            <p class="text-xs text-gray-400 truncate mt-0.5">{{ item.preview }}</p>
            <div class="flex items-center gap-3 mt-1.5 text-xs text-gray-400">
              <span>👁 {{ item.views }}</span>
              <span>💬 {{ item.answers }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 3열 레이아웃 (데스크톱) -->
    <div class="flex gap-4 lg:gap-6">

      <!-- 왼쪽 사이드바: 카테고리 (데스크톱) -->
      <aside class="hidden lg:block w-48 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 overflow-hidden sticky top-20">
          <h3 class="text-sm font-bold text-gray-700 px-4 py-3 border-b border-gray-100">카테고리</h3>
          <ul>
            <li v-for="cat in categories" :key="cat.slug">
              <button
                @click="selectCategory(cat.slug)"
                class="w-full text-left px-4 py-2.5 text-sm transition"
                :class="selectedCategory === cat.slug
 ? 'bg-blue-50 text-blue-600 font-semibold border-l-2 border-blue-500'
                  : 'text-gray-600 hover:bg-gray-50'"
              >
                {{ cat.label }}
              </button>
            </li>
          </ul>
        </div>
      </aside>

      <!-- 모바일 카테고리 탭 -->
      <div class="lg:hidden w-full mb-4 overflow-hidden">
        <div class="flex overflow-x-auto gap-2 pb-2 scrollbar-hide">
          <button
            v-for="cat in categories"
            :key="cat.slug"
            @click="selectCategory(cat.slug)"
            class="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-medium transition"
            :class="selectedCategory === cat.slug
 ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          >
            {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- 중앙: 질문 리스트 -->
      <main class="flex-1 min-w-0">
        

        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm text-gray-500">
            전체 <span class="font-bold text-gray-800">{{ totalCount }}개</span>
          </h2>
          <select v-model="sortOrder" class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 text-gray-600 focus:outline-none">
            <option value="latest">최신순</option>
            <option value="views">조회순</option>
            <option value="answers">답변순</option>
          </select>
        </div>

        <!-- 로딩 -->
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 5" :key="i" class="bg-white rounded-xl border border-gray-100 p-4 animate-pulse">
            <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-100 rounded w-full mb-3"></div>
            <div class="h-3 bg-gray-100 rounded w-1/3"></div>
          </div>
        </div>

        <!-- 질문 카드 -->
        <div v-else class="space-y-3">
          <div
            v-for="post in posts"
            :key="post.id"
            class="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md transition cursor-pointer"
            @click="goToPost(post.id)"
          >
            <div class="flex items-center gap-2 mb-2 flex-wrap">
              <span class="bg-blue-100 text-blue-600 text-[11px] px-2 py-0.5 rounded-full font-medium">
                {{ post.board?.name || '전체' }}
              </span>
              <span v-if="post.points" class="bg-yellow-100 text-yellow-700 text-[11px] px-2 py-0.5 rounded-full font-bold">
                {{ post.points }}P
              </span>
              <span v-if="post.adopted" class="bg-green-100 text-green-600 text-[11px] px-2 py-0.5 rounded-full font-medium">
                ✓ 채택완료
              </span>
            </div>
            <h3 class="text-sm font-bold text-gray-800 mb-1 line-clamp-1">{{ post.title }}</h3>
            <p class="text-xs text-gray-400 line-clamp-1 mb-3">{{ stripHtml(post.content) }}</p>
            <div class="flex items-center justify-between text-xs text-gray-400">
              <div class="flex items-center gap-2">
                <div class="w-5 h-5 bg-gray-200 rounded-full flex items-center justify-center text-[10px] font-bold text-gray-500">
                  {{ post.user?.name?.charAt(0) || '?' }}
                </div>
                <span>{{ post.user?.name || '익명' }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span>💬 {{ post.comment_count || 0 }}</span>
                <span>👁 {{ post.view_count || 0 }}</span>
                <span>{{ formatDate(post.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 빈 상태 -->
          <div v-if="!loading && posts.length === 0" class="text-center py-16">
            <p class="text-gray-400 text-sm">아직 등록된 질문이 없습니다.</p>
            <router-link to="/community/write" class="text-blue-500 text-sm mt-2 inline-block hover:underline">
              첫 번째 질문을 작성해보세요 →
            </router-link>
          </div>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="lastPage > 1" class="flex justify-center gap-1 mt-6">
          <button
            v-for="p in lastPage"
            :key="p"
            @click="goPage(p)"
            class="w-8 h-8 rounded-lg text-xs font-medium transition"
            :class="currentPage === p
 ? 'bg-blue-500 text-white'
              : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'"
          >
            {{ p }}
          </button>
        </div>
      </main>

      <!-- 오른쪽 사이드바: 랭킹 (데스크톱) -->
      <aside class="hidden xl:block w-56 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 sticky top-20">
          <h3 class="text-sm font-bold text-gray-700 px-4 py-3 border-b border-gray-100">🏆 커뮤니티 랭킹</h3>
          <ul class="py-2">
            <li
              v-for="(user, idx) in topUsers"
              :key="user.name"
              class="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 transition"
            >
              <span class="text-sm font-bold w-5 text-center">
                <template v-if="idx === 0">🥇</template>
                <template v-else-if="idx === 1">🥈</template>
                <template v-else-if="idx === 2">🥉</template>
                <template v-else>{{ idx + 1 }}</template>
              </span>
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                :style="{ backgroundColor: user.color }"
              >
                {{ user.name.charAt(0) }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-semibold text-gray-800 truncate">{{ user.name }}</p>
                <div class="flex items-center gap-1.5">
                  <span class="text-[10px] bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded font-medium">{{ user.level }}</span>
                  <span class="text-[10px] text-gray-400">채택 {{ user.adopted }}회</span>
                </div>
              </div>
            </li>
          </ul>
          <div class="border-t border-gray-100 px-4 py-2.5">
            <button class="text-xs text-blue-500 hover:text-blue-600 font-medium">전체 →</button>
          </div>
        </div>
      </aside>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const searchQuery = ref('');
const selectedCategory = ref('all');
const sortOrder = ref('latest');
const loading = ref(false);
const posts = ref([]);
const currentPage = ref(1);
const lastPage = ref(1);
const totalCount = ref(0);

// 카테고리
const categories = [
  { slug: 'all', label: '전체' },
  { slug: 'education', label: '교육/학문' },
  { slug: 'it-tech', label: 'IT/테크' },
  { slug: 'game', label: '게임' },
  { slug: 'entertainment', label: '엔터테인먼트/예술' },
  { slug: 'life', label: '생활' },
  { slug: 'health', label: '건강' },
  { slug: 'society', label: '사회/정치' },
  { slug: 'economy', label: '경제' },
  { slug: 'travel', label: '여행' },
  { slug: 'sports', label: '스포츠/레저' },
  { slug: 'shopping', label: '쇼핑' },
];

// 많이 본 Q&A - 실제 API 데이터
const popularQuestions = ref([]);

// 랭킹
const topUsers = ref([]);

function handleSearch() {
  if (searchQuery.value.trim()) {
    fetchPosts(1);
  }
}

function selectCategory(slug) {
  selectedCategory.value = slug;
  currentPage.value = 1;
  fetchPosts(1);
}

function goToPost(id) {
  router.push(`/community/post/${id}`);
}

function goPage(page) {
  currentPage.value = page;
  fetchPosts(page);
}

function stripHtml(html) {
  if (!html) return '';
  return html.replace(/<[^>]*>/g, '').substring(0, 100);
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000);
  if (diff < 60) return '방금 전';
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}일 전`;
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

async function fetchPosts(page = 1) {
  loading.value = true;
  try {
    const params = { page };
    if (selectedCategory.value !== 'all') {
      params.board = selectedCategory.value;
    }
    if (searchQuery.value.trim()) {
      params.q = searchQuery.value.trim();
    }
    const { data } = await axios.get('/api/posts', { params });
    posts.value = (data.data || []).map(p => ({
      ...p,
      points: Math.random() > 0.6 ? [30, 50, 100][Math.floor(Math.random() * 3)] : null,
      adopted: Math.random() > 0.7,
      comment_count: p.comment_count || Math.floor(Math.random() * 20),
    }));
    totalCount.value = data.total || data.data?.length || 0;
    lastPage.value = data.last_page || 1;
    currentPage.value = data.current_page || page;
  } catch (e) {
    console.error('Failed to fetch posts:', e);
    posts.value = [];
  } finally {
    loading.value = false;
  }
}

async function fetchPopular() {
  try {
    const { data } = await axios.get('/api/posts', { params: { sort: 'views', per_page: 6 } });
    popularQuestions.value = (data.data || []).map(p => ({
      id: p.id,
      title: p.title,
      preview: p.content ? p.content.replace(/<[^>]*>/g, '').substring(0, 80) : '',
      views: p.view_count || 0,
      answers: p.comment_count || 0,
    }));
  } catch {}
}

onMounted(() => {
  fetchPosts(1);
  fetchPopular();
});

watch(sortOrder, () => {
  fetchPosts(1);
});
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>