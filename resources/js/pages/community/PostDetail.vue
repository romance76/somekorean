<template>
  <DetailTemplate
    :item="post"
    :loading="loading"
    :breadcrumb="breadcrumb"
    :images="postImages"
    :showAuthor="true"
    :showActions="true"
    :showComments="true"
    commentType="post"
    @like="toggleLike"
    @bookmark="toggleBookmark"
    @report="reportPost"
  >
    <template #body>
      <!-- Title -->
      <h1 class="text-lg font-bold text-gray-900 dark:text-white mb-4">{{ post?.title }}</h1>

      <!-- Category & Meta -->
      <div class="flex items-center gap-2 mb-4">
        <span v-if="post?.board?.name" class="text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 px-2 py-1 rounded-full font-medium">
          {{ post.board.name }}
        </span>
        <span v-if="post?.is_question" class="text-xs bg-violet-50 text-violet-600 px-2 py-1 rounded-full font-medium">Q&A</span>
      </div>

      <!-- Content -->
      <div class="prose prose-sm max-w-none text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed"
        v-html="post?.content_html || post?.content"></div>

      <!-- Map -->
      <div v-if="post?.latitude && post?.longitude" class="mt-6 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-600">
        <iframe
          :src="`https://maps.google.com/maps?q=${post.latitude},${post.longitude}&output=embed`"
          class="w-full h-[250px] border-0" allowfullscreen loading="lazy" />
        <div v-if="post.address" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700">
          {{ post.address }}
        </div>
      </div>

      <!-- Edit/Delete -->
      <div v-if="canEdit" class="mt-6 flex items-center gap-2 pt-4 border-t border-gray-100 dark:border-gray-700">
        <router-link :to="`/community/write?edit=${post?.id}`"
          class="text-xs text-gray-500 hover:text-blue-600 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-600 transition">
          {{ locale === 'ko' ? '수정' : 'Edit' }}
        </router-link>
        <button @click="deletePost"
          class="text-xs text-gray-500 hover:text-red-600 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-600 transition">
          {{ locale === 'ko' ? '삭제' : 'Delete' }}
        </button>
      </div>
    </template>

    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        <h3 class="font-bold text-gray-800 dark:text-white text-sm px-4 py-3 border-b border-gray-100 dark:border-gray-700">
          {{ post?.board?.name || '게시판' }} {{ locale === 'ko' ? '최신글' : 'Latest' }}
        </h3>
        <div v-if="relatedPosts.length">
          <div v-for="(r, idx) in relatedPosts" :key="r.id"
            @click="$router.push(`/community/${post?.board?.slug || 'free'}/${r.id}`)"
            class="flex gap-3 py-3 px-3 cursor-pointer hover:bg-blue-50/40 dark:hover:bg-gray-700/50 transition border-b border-gray-50 dark:border-gray-700 last:border-0"
            :class="r.id == $route.params.id ? 'bg-blue-50 dark:bg-gray-700' : ''">
            <span class="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-black mt-0.5"
              :class="String(r.id) === String($route.params.id) ? 'bg-blue-500 text-white' : 'bg-gray-100 dark:bg-gray-600 text-gray-500 dark:text-gray-300'">
              {{ idx + 1 }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-800 dark:text-gray-200 line-clamp-2 leading-snug">{{ r.title }}</p>
              <div class="flex items-center gap-1.5 mt-1 text-[11px] text-gray-400">
                <span>{{ r.user?.name || '익명' }}</span>
                <span>·</span>
                <span>{{ formatDate(r.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-10 text-gray-400 text-sm">
          {{ locale === 'ko' ? '관련 글이 없습니다' : 'No related posts' }}
        </div>
      </div>
    </template>
  </DetailTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import DetailTemplate from '../../components/templates/DetailTemplate.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const post = ref(null)
const loading = ref(true)
const relatedPosts = ref([])

const canEdit = computed(() => auth.user && (auth.user.id === post.value?.user_id || auth.user.is_admin))

const breadcrumb = computed(() => {
  if (!post.value) return []
  return [
    { label: locale.value === 'ko' ? '커뮤니티' : 'Community', to: '/community' },
    { label: post.value.board?.name || '게시판', to: `/community/${post.value.board?.slug || 'free'}` },
    { label: post.value.title }
  ]
})

const postImages = computed(() => {
  if (!post.value) return null
  const imgs = post.value.images || []
  return imgs.length ? imgs : null
})

function formatDate(d) {
  if (!d) return ''
  const diff = (Date.now() - new Date(d).getTime()) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  return new Date(d).toLocaleDateString('ko-KR')
}

async function loadPost() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/posts/${route.params.id}`)
    post.value = data
    loadRelatedPosts()
  } catch { post.value = null }
  loading.value = false
}

async function loadRelatedPosts() {
  if (!post.value?.board_id) return
  try {
    const { data } = await axios.get(`/api/posts?board_id=${post.value.board_id}&limit=5`)
    relatedPosts.value = (data.data || data || []).filter(p => p.id !== post.value.id).slice(0, 5)
  } catch { relatedPosts.value = [] }
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/posts/${post.value.id}/like`)
    post.value.is_liked = data.liked
    post.value.like_count = data.like_count
  } catch { /* empty */ }
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/posts/${post.value.id}/bookmark`)
    post.value.is_bookmarked = data.bookmarked
  } catch { /* empty */ }
}

function reportPost() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  if (confirm(locale.value === 'ko' ? '이 게시글을 신고하시겠습니까?' : 'Report this post?')) {
    axios.post(`/api/posts/${post.value.id}/report`).catch(() => {})
  }
}

async function deletePost() {
  if (!confirm(locale.value === 'ko' ? '게시글을 삭제하시겠습니까?' : 'Delete this post?')) return
  try {
    await axios.delete(`/api/posts/${post.value.id}`)
    router.push(`/community/${post.value.board?.slug || ''}`)
  } catch { /* empty */ }
}

watch(() => route.params.id, () => { if (route.params.id) loadPost() })
onMounted(loadPost)
</script>
