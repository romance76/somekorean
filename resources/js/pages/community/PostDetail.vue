<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <div v-if="loading" class="text-center py-20 text-gray-400">불러오는 중...</div>
      <div v-else-if="!post" class="text-center py-20 text-gray-400">게시글을 찾을 수 없습니다.</div>
      <template v-else>
        <!-- 상단 컬러 헤더 -->
        <div class="bg-gradient-to-r from-red-500 to-pink-500 text-white px-6 py-4 rounded-2xl mb-4">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <router-link :to="`/community/${post.board?.slug}`" class="text-red-200 text-sm hover:text-white transition">&larr; {{ post.board?.name || '게시판' }}</router-link>
              <span class="bg-white/20 text-xs px-3 py-1 rounded-full">{{ post.board?.name }}</span>
            </div>
            <div class="flex items-center gap-2">
              <button @click="sharePost" class="flex items-center gap-1 text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
                공유
              </button>
              <button @click="toggleBookmark" :class="post.is_bookmarked ? 'bg-yellow-400/30' : 'bg-white/10 hover:bg-white/20'" class="flex items-center gap-1 text-xs text-white/80 hover:text-white px-3 py-1.5 rounded-lg transition">
                <svg class="w-3.5 h-3.5" :fill="post.is_bookmarked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/></svg>
                북마크
              </button>
              <!-- 수정/삭제 (작성자 본인) -->
              <template v-if="canEdit">
                <router-link :to="`/community/write?edit=${post.id}`" class="text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">수정</router-link>
                <button @click="deletePost" class="text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">삭제</button>
              </template>
            </div>
          </div>
          <h1 class="text-lg sm:text-xl font-black leading-tight">{{ post.title }}</h1>
          <div class="flex items-center gap-2 mt-2 text-sm text-red-100">
            <span class="font-medium">{{ post.is_anonymous ? '익명' : post.user?.name }}</span>
            <span>·</span>
            <span>{{ formatDate(post.created_at) }}</span>
            <span>·</span>
            <span>조회 {{ post.view_count }}</span>
          </div>
        </div>

        <!-- 2컬럼 레이아웃 -->
        <div class="flex gap-5 items-start">

          <!-- 좌: 본문 컬럼 -->
          <div class="flex-1 min-w-0">

            <!-- 본문 -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-4">
              <div class="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap leading-relaxed" v-html="post.content_html || post.content"></div>
            </div>

            <!-- 지도 (주소가 있는 경우) -->
            <div v-if="post.latitude && post.longitude" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-4">
              <div class="px-5 py-3 border-b border-gray-100">
                <h3 class="font-semibold text-gray-800 text-sm">위치</h3>
              </div>
              <iframe
                :src="`https://maps.google.com/maps?q=${post.latitude},${post.longitude}&output=embed`"
                class="w-full h-[300px] border-0"
                allowfullscreen
                loading="lazy"
              ></iframe>
              <div v-if="post.address" class="px-5 py-3 text-sm text-gray-600">{{ post.address }}</div>
            </div>

            <!-- 작성자 정보 카드 -->
            <div v-if="!post.is_anonymous && post.user" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">작성자 정보</h3>
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center text-red-600 font-bold text-xl flex-shrink-0">
                  {{ post.user.name?.[0] || '?' }}
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900">{{ post.user.name }}</p>
                  <div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
                    <span v-if="post.user.level" class="bg-blue-50 text-blue-600 px-2 py-0.5 rounded">Lv.{{ post.user.level }}</span>
                    <span v-if="post.user.post_count != null">게시글 {{ post.user.post_count }}개</span>
                    <span v-if="post.user.comment_count != null">댓글 {{ post.user.comment_count }}개</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 좋아요 / 액션 버튼 -->
            <div class="flex justify-center gap-3 mb-6">
              <button @click="toggleLike"
                :class="['flex items-center space-x-2 px-6 py-2.5 rounded-full border-2 transition font-medium text-sm',
   post.is_liked ? 'border-red-500 bg-red-50 text-red-600' : 'border-gray-200 text-gray-500 hover:border-red-300']">
                <span>{{ post.is_liked ? '&#10084;&#65039;' : '&#9825;' }}</span>
                <span>추천 {{ post.like_count || 0 }}</span>
              </button>
            </div>

            <!-- 댓글 섹션 -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-4">
              <div class="px-5 py-3 border-b border-gray-100">
                <h3 class="font-semibold text-gray-800 text-sm">댓글 {{ post.comments?.length || 0 }}개</h3>
              </div>
              <ul v-if="post.comments?.length">
                <li v-for="comment in post.comments" :key="comment.id" class="px-5 py-3.5 border-b border-gray-50 last:border-0">
                  <div class="flex items-start justify-between">
                    <div class="flex items-start space-x-2 flex-1">
                      <div class="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center text-gray-500 text-xs font-bold flex-shrink-0 mt-0.5">
                        {{ (comment.user?.name || comment.user_name || '익명')[0] }}
                      </div>
                      <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-1">
                          <span class="text-sm font-medium text-gray-800">{{ comment.user?.name || comment.user_name || '익명' }}</span>
                          <span class="text-xs text-gray-400">{{ formatDate(comment.created_at) }}</span>
                          <span v-if="comment.is_accepted" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">채택됨</span>
                        </div>
                        <p class="text-sm text-gray-700">{{ comment.content }}</p>
                      </div>
                    </div>
                    <div class="flex items-center gap-2 ml-2">
                      <!-- 채택 버튼 (Q&A 게시글이고, 작성자 본인이 볼 때, 아직 채택 안 된 댓글) -->
                      <button
                        v-if="isQuestionPost && canEdit && !comment.is_accepted && comment.user_id !== authStore.user?.id"
                        @click="acceptComment(comment.id)"
                        class="text-xs text-green-600 hover:text-green-800 border border-green-200 px-2 py-0.5 rounded hover:bg-green-50 transition">
                        채택
                      </button>
                      <button v-if="authStore.user?.id === comment.user?.id || authStore.user?.is_admin"
                        @click="deleteComment(comment.id)" class="text-xs text-gray-300 hover:text-red-400">삭제</button>
                    </div>
                  </div>
                </li>
              </ul>
              <div v-else class="px-5 py-8 text-center text-sm text-gray-400">아직 댓글이 없습니다. 첫 댓글을 남겨보세요!</div>

              <!-- 댓글 입력 -->
              <div v-if="authStore.isLoggedIn" class="px-5 py-3 bg-gray-50 border-t border-gray-100">
                <div class="flex gap-2">
                  <input v-model="commentText" @keyup.enter.ctrl="submitComment" type="text" placeholder="댓글을 입력하세요 (Ctrl+Enter)"
                    class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
                  <button @click="submitComment" :disabled="!commentText.trim()"
                    class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-40">등록</button>
                </div>
              </div>
              <div v-else class="px-5 py-3 bg-gray-50 border-t border-gray-100 text-center">
                <router-link to="/auth/login" class="text-red-600 text-sm hover:underline">로그인 후 댓글을 작성할 수 있습니다</router-link>
              </div>
            </div>

            <router-link :to="`/community/${post.board?.slug}`" class="text-sm text-gray-500 hover:text-red-600">&larr; 목록으로</router-link>
          </div><!-- /본문 컬럼 -->

          <!-- 우: 사이드바 - 같은 게시판 최신글 -->
          <div class="hidden lg:block flex-shrink-0 sticky top-4" style="width:320px">
            <div class="bg-white rounded-2xl shadow-sm flex flex-col overflow-hidden">
              <h3 class="flex-shrink-0 font-bold text-gray-800 text-sm px-4 py-3 border-b border-gray-100">
                {{ post.board?.name || '게시판' }} 최신글
              </h3>
              <div>
                <div v-if="relatedPosts.length">
                  <div v-for="(r, idx) in relatedPosts" :key="r.id"
                    @click="$router.push(`/community/${post.board?.slug}/${r.id}`)"
                    class="flex gap-3 py-3 px-3 cursor-pointer hover:bg-red-50/40 transition border-b border-gray-50 last:border-0"
                    :class="r.id == $route.params.id ? 'bg-red-50' : ''">
                    <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-black mt-0.5"
                      :class="String(r.id) === String($route.params.id) ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-500'">
                      {{ idx + 1 }}
                    </span>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-800 line-clamp-2 leading-snug">{{ r.title }}</p>
                      <div class="flex items-center gap-1.5 mt-1">
                        <span class="text-[11px] text-gray-400">{{ r.user?.name || '익명' }}</span>
                        <span class="text-gray-300 text-[10px]">&middot;</span>
                        <span class="text-[11px] text-gray-400">{{ formatDate(r.created_at) }}</span>
                        <span class="text-gray-300 text-[10px]">&middot;</span>
                        <span class="text-[11px] text-gray-400">조회 {{ r.view_count || 0 }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-10 text-gray-400 text-sm">관련 글이 없습니다.</div>
              </div>
            </div>
          </div><!-- /사이드바 -->

        </div><!-- /2컬럼 -->
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const post = ref(null);
const loading = ref(true);
const commentText = ref('');
const relatedPosts = ref([]);

const canEdit = computed(() =>
  authStore.user && (authStore.user.id === post.value?.user_id || authStore.user.is_admin)
);

const isQuestionPost = computed(() =>
  post.value?.is_question || post.value?.board?.slug === 'qna' || post.value?.board?.type === 'qna'
);

async function loadPost() {
  loading.value = true;
  try {
    const { data } = await axios.get(`/api/posts/${route.params.id}`);
    post.value = data;
    // 사이드바: 같은 게시판 최신글 5개
    loadRelatedPosts();
  } catch { post.value = null; }
  loading.value = false;
}

async function loadRelatedPosts() {
  if (!post.value?.board_id) return;
  try {
    const { data } = await axios.get(`/api/posts?board_id=${post.value.board_id}&limit=5`);
    relatedPosts.value = (data.data || data || []).filter(p => p.id !== post.value.id).slice(0, 5);
  } catch {
    relatedPosts.value = [];
  }
}

async function toggleLike() {
  if (!authStore.isLoggedIn) { router.push('/auth/login'); return; }
  try {
    const { data } = await axios.post(`/api/posts/${post.value.id}/like`);
    post.value.is_liked = data.liked;
    post.value.like_count = data.like_count;
  } catch {}
}

async function toggleBookmark() {
  if (!authStore.isLoggedIn) { router.push('/auth/login'); return; }
  try {
    const { data } = await axios.post(`/api/posts/${post.value.id}/bookmark`);
    post.value.is_bookmarked = data.bookmarked;
  } catch {}
}

function sharePost() {
  const url = window.location.href;
  if (navigator.share) {
    navigator.share({ title: post.value.title, url });
  } else if (navigator.clipboard) {
    navigator.clipboard.writeText(url);
    alert('링크가 복사되었습니다.');
  }
}

async function acceptComment(commentId) {
  if (!confirm('이 댓글을 채택하시겠습니까?')) return;
  try {
    const { data } = await axios.post(`/api/comments/${commentId}/accept`);
    const comment = post.value.comments.find(c => c.id === commentId);
    if (comment) comment.is_accepted = true;
  } catch (e) {
    alert(e.response?.data?.message || '채택 실패');
  }
}

async function submitComment() {
  if (!commentText.value.trim()) return;
  try {
    const { data } = await axios.post(`/api/posts/${post.value.id}/comments`, { content: commentText.value });
    post.value.comments.push(data.comment);
    commentText.value = '';
    post.value.comment_count++;
  } catch(e) {
    alert(e.response?.data?.message || '댓글 등록 실패');
  }
}

async function deleteComment(id) {
  if (!confirm('댓글을 삭제하시겠습니까?')) return;
  try {
    await axios.delete(`/api/comments/${id}`);
    post.value.comments = post.value.comments.filter(c => c.id !== id);
    post.value.comment_count--;
  } catch {}
}

async function deletePost() {
  if (!confirm('게시글을 삭제하시겠습니까?')) return;
  try {
    await axios.delete(`/api/posts/${post.value.id}`);
    router.push(`/community/${post.value.board?.slug}`);
  } catch {}
}

function formatDate(d) {
  const date = new Date(d);
  const now = new Date();
  const diff = (now - date) / 1000;
  if (diff < 60) return '방금 전';
  if (diff < 3600) return `${Math.floor(diff/60)}분 전`;
  if (diff < 86400) return `${Math.floor(diff/3600)}시간 전`;
  return date.toLocaleDateString('ko-KR');
}

onMounted(loadPost);
</script>
