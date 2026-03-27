<template>
  <div class="max-w-4xl mx-auto px-4 py-6">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h1 class="text-xl font-bold text-gray-800">{{ board?.name || '게시판' }}</h1>
        <p class="text-gray-500 text-sm">{{ board?.description }}</p>
      </div>
      <router-link to="/community/write" v-if="authStore.isLoggedIn"
        class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700">글쓰기</router-link>
    </div>

    <!-- 검색 -->
    <div class="flex space-x-2 mb-4">
      <input v-model="searchQ" @keyup.enter="searchPosts" type="text" placeholder="검색어 입력"
        class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
      <button @click="searchPosts" class="bg-gray-100 px-4 py-2 rounded-lg text-sm hover:bg-gray-200">검색</button>
    </div>

    <!-- 게시글 목록 -->
    <div v-if="loading" class="text-center py-10 text-gray-400">불러오는 중...</div>
    <div v-else-if="posts.length === 0" class="text-center py-10 text-gray-400">게시글이 없습니다.</div>
    <ul v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <li v-for="post in posts" :key="post.id"
        class="px-5 py-4 border-b border-gray-100 last:border-0 hover:bg-gray-50 transition">
        <router-link :to="`/community/post/${post.id}`" class="block">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2 mb-1">
                <span v-if="post.is_pinned" class="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-medium">공지</span>
                <span class="text-gray-800 text-sm font-medium truncate">{{ post.title }}</span>
                <span v-if="post.comment_count > 0" class="text-red-500 text-xs">[{{ post.comment_count }}]</span>
              </div>
              <div class="flex items-center space-x-2 text-xs text-gray-400">
                <span>{{ post.user?.is_anonymous ? '익명' : post.user?.name }}</span>
                <span>·</span>
                <span>{{ formatDate(post.created_at) }}</span>
              </div>
            </div>
            <div class="flex items-center space-x-3 text-xs text-gray-400 flex-shrink-0 ml-4">
              <span>👁 {{ post.view_count }}</span>
              <span>👍 {{ post.like_count }}</span>
            </div>
          </div>
        </router-link>
      </li>
    </ul>

    <!-- 페이지네이션 -->
    <div v-if="totalPages > 1" class="flex justify-center space-x-1 mt-4">
      <button v-for="p in totalPages" :key="p" @click="loadPosts(p)"
        :class="['px-3 py-1.5 rounded text-sm', p === currentPage ? 'bg-red-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300']">
        {{ p }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import axios from 'axios';

const route = useRoute();
const authStore = useAuthStore();
const posts = ref([]);
const board = ref(null);
const loading = ref(true);
const searchQ = ref('');
const currentPage = ref(1);
const totalPages = ref(1);

async function loadPosts(page = 1) {
    loading.value = true;
    try {
        const params = { board: route.params.slug, page, search: searchQ.value };
        const { data } = await axios.get('/api/posts', { params });
        posts.value = data.data;
        currentPage.value = data.current_page;
        totalPages.value = data.last_page;
        // 게시판 정보 로드
        if (!board.value) {
            const boardRes = await axios.get(`/api/boards`);
            board.value = boardRes.data.find(b => b.slug === route.params.slug);
        }
    } catch {}
    loading.value = false;
}

function searchPosts() { loadPosts(1); }

function formatDate(d) {
    const date = new Date(d);
    const now = new Date();
    const diff = (now - date) / 1000;
    if (diff < 60) return '방금 전';
    if (diff < 3600) return `${Math.floor(diff/60)}분 전`;
    if (diff < 86400) return `${Math.floor(diff/3600)}시간 전`;
    return date.toLocaleDateString('ko-KR');
}

onMounted(() => loadPosts());
watch(() => route.params.slug, () => { board.value = null; loadPosts(); });
</script>
