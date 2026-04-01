<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">

    <!-- 뉴스 스타일 헤더 -->
    <div class="bg-gradient-to-r from-red-500 to-pink-500 text-white px-6 py-4 rounded-2xl mb-4" v-if="post">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center gap-2">
          <router-link :to="'/community/' + slug" class="text-red-200 text-sm hover:text-white transition">&larr; {{ categoryInfo.name || slug }}</router-link>
          <span class="bg-white/20 text-xs px-3 py-1 rounded-full">{{ categoryInfo.icon }} {{ categoryInfo.name }}</span>
        </div>
        <div class="flex items-center gap-2">
          <button @click="sharePost" class="flex items-center gap-1 text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
            공유
          </button>
          <button @click="bookmarkPost" class="flex items-center gap-1 text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/></svg>
            북마크
          </button>
          <!-- 본인 글이면 수정/삭제 -->
          <template v-if="isOwner">
            <router-link :to="`/community/${slug}/${postId}/edit`" class="flex items-center gap-1 text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">수정</router-link>
            <button @click="deletePost" class="flex items-center gap-1 text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">삭제</button>
          </template>
        </div>
      </div>
      <h1 class="text-lg sm:text-xl font-black leading-tight">{{ post.title }}</h1>
      <div class="flex items-center gap-2 mt-2 text-sm text-red-100">
        <span class="font-medium">{{ post.is_anonymous ? '익명' : (post.author_name || '알수없음') }}</span>
        <span>·</span>
        <span>{{ timeAgo(post.created_at) }}</span>
        <span>·</span>
        <span>조회 {{ post.views || 0 }}</span>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="loading" class="bg-white rounded-xl border border-gray-100 p-8 animate-pulse">
      <div class="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div class="h-4 bg-gray-100 rounded w-full mb-2"></div>
      <div class="h-4 bg-gray-100 rounded w-2/3"></div>
    </div>

    <!-- 2컬럼 -->
    <div v-else-if="post" class="flex gap-5 items-start">

      <!-- 좌측: 본문 -->
      <main class="flex-1 min-w-0">
        <!-- 본문 -->
        <div class="bg-white rounded-xl border border-gray-100 p-6 mb-4">
          <div class="prose prose-sm max-w-none text-gray-700 leading-relaxed" v-html="post.content"></div>
        </div>

        <!-- 작성자 정보 -->
        <div v-if="!post.is_anonymous && post.author" class="bg-white rounded-xl border border-gray-100 p-4 mb-4 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center text-red-500 font-bold text-sm">
            {{ (post.author_name || '?')[0] }}
          </div>
          <div>
            <p class="text-sm font-bold text-gray-800">{{ post.author_name }}</p>
            <p class="text-xs text-gray-400">{{ post.author?.bio || '한인 커뮤니티 멤버' }}</p>
          </div>
        </div>

        <!-- 좋아요 -->
        <div class="bg-white rounded-xl border border-gray-100 p-4 mb-6 flex items-center justify-center gap-3">
          <button
            @click="toggleLike"
            class="flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-bold transition"
            :class="post.is_liked ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-500'"
          >
            ❤️ {{ post.is_liked ? '좋아요 취소' : '좋아요' }}
            <span class="ml-1">{{ post.likes_count || 0 }}</span>
          </button>
        </div>

        <!-- 댓글 -->
        <div class="bg-white rounded-xl border border-gray-100 p-6">
          <h3 class="text-sm font-bold text-gray-700 mb-4">💬 댓글 {{ comments.length }}개</h3>

          <!-- 댓글 작성 -->
          <div class="mb-6">
            <textarea
              v-model="newComment"
              rows="3"
              placeholder="댓글을 입력하세요..."
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-300 resize-none"
            ></textarea>
            <div class="flex justify-end mt-2">
              <button
                @click="submitComment()"
                :disabled="!newComment.trim()"
                class="bg-red-500 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-600 transition disabled:opacity-50"
              >
                등록
              </button>
            </div>
          </div>

          <!-- 댓글 목록 -->
          <div class="space-y-4">
            <div v-for="comment in topLevelComments" :key="comment.id">
              <div class="flex gap-3">
                <div class="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 text-xs font-bold flex-shrink-0">
                  {{ (comment.is_anonymous ? '?' : (comment.author_name || '?')[0]) }}
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm font-bold text-gray-700">{{ comment.is_anonymous ? '🎭 익명' : (comment.author_name || '알수없음') }}</span>
                    <span class="text-xs text-gray-400">{{ timeAgo(comment.created_at) }}</span>
                  </div>
                  <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ comment.content }}</p>
                  <button
                    @click="replyTo = replyTo === comment.id ? null : comment.id"
                    class="text-xs text-gray-400 hover:text-red-500 mt-1 transition"
                  >
                    답글
                  </button>

                  <!-- 답글 입력 -->
                  <div v-if="replyTo === comment.id" class="mt-2">
                    <textarea
                      v-model="replyContent"
                      rows="2"
                      placeholder="답글을 입력하세요..."
                      class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-300 resize-none"
                    ></textarea>
                    <div class="flex justify-end gap-2 mt-1">
                      <button @click="replyTo = null" class="text-xs text-gray-400 hover:text-gray-600">취소</button>
                      <button
                        @click="submitComment(comment.id)"
                        :disabled="!replyContent.trim()"
                        class="bg-red-500 text-white px-3 py-1 rounded-lg text-xs font-bold hover:bg-red-600 transition disabled:opacity-50"
                      >
                        등록
                      </button>
                    </div>
                  </div>

                  <!-- 대댓글 -->
                  <div v-if="getReplies(comment.id).length" class="mt-3 space-y-3 pl-4 border-l-2 border-gray-100">
                    <div v-for="reply in getReplies(comment.id)" :key="reply.id" class="flex gap-2">
                      <div class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center text-gray-400 text-[10px] font-bold flex-shrink-0">
                        {{ (reply.is_anonymous ? '?' : (reply.author_name || '?')[0]) }}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-0.5">
                          <span class="text-xs font-bold text-gray-600">{{ reply.is_anonymous ? '🎭 익명' : (reply.author_name || '알수없음') }}</span>
                          <span class="text-[10px] text-gray-400">{{ timeAgo(reply.created_at) }}</span>
                        </div>
                        <p class="text-xs text-gray-500 whitespace-pre-wrap">{{ reply.content }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="comments.length === 0" class="text-center text-gray-400 text-sm py-6">
            아직 댓글이 없습니다. 첫 댓글을 남겨보세요!
          </div>
        </div>
      </main>

      <!-- 우측: 사이드바 -->
      <div class="hidden lg:block flex-shrink-0 sticky top-4" style="width:320px">
        <div class="bg-white rounded-2xl shadow-sm flex flex-col overflow-hidden">
          <h3 class="flex-shrink-0 font-bold text-gray-800 text-sm px-4 py-3 border-b border-gray-100">같은 카테고리 최신글</h3>
          <div>
            <div v-if="relatedPosts.length">
              <router-link v-for="item in relatedPosts" :key="item.id"
                :to="`/community/${slug}/${item.id}`"
                class="flex gap-3 py-3 px-3 cursor-pointer hover:bg-blue-50/40 transition border-b border-gray-50 last:border-0">
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-800 line-clamp-2 leading-snug">{{ item.title }}</p>
                  <div class="flex items-center gap-1.5 mt-1">
                    <span class="text-[11px] text-gray-400">{{ item.is_anonymous ? '익명' : (item.author_name || '') }}</span>
                    <span class="text-gray-300 text-[10px]">&middot;</span>
                    <span class="text-[11px] text-gray-400">{{ timeAgo(item.created_at) }}</span>
                  </div>
                </div>
              </router-link>
            </div>
            <div v-else class="text-center py-10 text-gray-400 text-sm">관련 글이 없습니다.</div>
          </div>
        </div>
      </div><!-- /사이드바 -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const post = ref(null)
const comments = ref([])
const relatedPosts = ref([])
const categoryInfo = ref({ name: '', icon: '' })
const categories = ref([])
const newComment = ref('')
const replyContent = ref('')
const replyTo = ref(null)

const slug = computed(() => route.params.slug)
const postId = computed(() => route.params.id)

const isOwner = computed(() => {
  if (!post.value) return false
  try {
    const token = localStorage.getItem('sk_token')
    if (!token) return false
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub == post.value.user_id
  } catch { return false }
})

const topLevelComments = computed(() => comments.value.filter(c => !c.parent_id))

function getReplies(parentId) {
  return comments.value.filter(c => c.parent_id === parentId)
}

function getAuthHeaders() {
  const token = localStorage.getItem('sk_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now - date) / 1000)
  if (diff < 60) return '방금 전'
  if (diff < 3600) return Math.floor(diff / 60) + '분 전'
  if (diff < 86400) return Math.floor(diff / 3600) + '시간 전'
  if (diff < 172800) return '어제'
  if (diff < 604800) return Math.floor(diff / 86400) + '일 전'
  return date.toLocaleDateString('ko-KR')
}

function sharePost() {
  if (navigator.share) {
    navigator.share({ title: post.value.title, url: window.location.href })
  } else {
    navigator.clipboard.writeText(window.location.href)
    alert('링크가 복사되었습니다!')
  }
}

function bookmarkPost() {
  alert('북마크 기능은 준비 중입니다.')
}

async function fetchPost() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/community-v2/${slug.value}/posts/${postId.value}`, { headers: getAuthHeaders() })
    post.value = data.data || data
  } catch (e) {
    console.error('글 로딩 실패', e)
  } finally {
    loading.value = false
  }
}

async function fetchComments() {
  try {
    const { data } = await axios.get(`/api/community-v2/${slug.value}/posts/${postId.value}/comments`, { headers: getAuthHeaders() })
    comments.value = data.data || data || []
  } catch (e) {
    console.error('댓글 로딩 실패', e)
  }
}

async function fetchRelated() {
  try {
    const { data } = await axios.get(`/api/community-v2/${slug.value}/posts`, {
      params: { sort: 'latest', per_page: 5 },
      headers: getAuthHeaders()
    })
    relatedPosts.value = (data.data || data || []).filter(p => p.id != postId.value).slice(0, 5)
  } catch (e) {
    console.error('관련글 로딩 실패', e)
  }
}

async function fetchCategories() {
  try {
    const { data } = await axios.get('/api/community-v2/categories', { headers: getAuthHeaders() })
    categories.value = data.data || data || []
    const found = categories.value.find(c => c.slug === slug.value)
    if (found) categoryInfo.value = found
    else categoryInfo.value = { name: slug.value, icon: '📁' }
  } catch (e) {
    console.error('카테고리 로딩 실패', e)
  }
}

async function toggleLike() {
  try {
    await axios.post(`/api/community-v2/${slug.value}/posts/${postId.value}/like`, {}, { headers: getAuthHeaders() })
    post.value.is_liked = !post.value.is_liked
    post.value.likes_count = post.value.is_liked
      ? (post.value.likes_count || 0) + 1
      : Math.max(0, (post.value.likes_count || 0) - 1)
  } catch (e) {
    alert('로그인이 필요합니다.')
  }
}

async function submitComment(parentId = null) {
  const content = parentId ? replyContent.value : newComment.value
  if (!content.trim()) return
  try {
    await axios.post(`/api/community-v2/${slug.value}/posts/${postId.value}/comments`, {
      content: content.trim(),
      parent_id: parentId || undefined
    }, { headers: getAuthHeaders() })
    if (parentId) {
      replyContent.value = ''
      replyTo.value = null
    } else {
      newComment.value = ''
    }
    fetchComments()
  } catch (e) {
    alert('댓글 등록에 실패했습니다. 로그인이 필요합니다.')
  }
}

async function deletePost() {
  if (!confirm('정말 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/community-v2/${slug.value}/posts/${postId.value}`, { headers: getAuthHeaders() })
    router.push(`/community/${slug.value}`)
  } catch (e) {
    alert('삭제에 실패했습니다.')
  }
}

watch(() => route.params.id, () => {
  fetchPost()
  fetchComments()
  fetchRelated()
})

onMounted(() => {
  fetchCategories()
  fetchPost()
  fetchComments()
  fetchRelated()
})
</script>
