<template>
  <DetailTemplate
    :item="news"
    :loading="loading"
    :breadcrumb="breadcrumb"
    :images="null"
    :showAuthor="false"
    :showActions="true"
    :showComments="false"
    commentType="news"
    @like="toggleLike"
    @bookmark="toggleBookmark"
  >
    <template #header>
      <div v-if="news" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <!-- Category Breadcrumb -->
        <div class="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 mb-3">
          <router-link to="/news" class="hover:text-blue-600 transition">{{ locale === 'ko' ? '뉴스' : 'News' }}</router-link>
          <span class="text-gray-300">/</span>
          <span v-if="news.category" class="text-gray-700 dark:text-gray-300 font-medium">{{ news.sub_category?.name || news.category }}</span>
        </div>

        <h1 class="text-lg font-bold text-gray-900 dark:text-white leading-snug mb-3">{{ news.title }}</h1>

        <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span v-if="news.source" class="font-medium text-gray-700 dark:text-gray-300">{{ news.source }}</span>
          <span>{{ formatDate(news.published_at || news.created_at) }}</span>
          <span>{{ locale === 'ko' ? '조회' : 'Views' }} {{ news.view_count || 0 }}</span>
        </div>
      </div>
    </template>

    <template #body>
      <!-- Hero Image -->
      <div v-if="heroImage" class="mb-4 -mx-5 -mt-5">
        <div class="bg-gray-50 dark:bg-gray-900 flex justify-center">
          <img :src="heroImage" :alt="news?.title"
            class="max-w-full max-h-[70vh] object-contain" @error="heroImage = null" />
        </div>
      </div>

      <!-- Article Content -->
      <div class="article-content prose prose-sm max-w-none text-gray-800 dark:text-gray-200 leading-relaxed" v-html="formattedContent"></div>

      <p v-if="!formattedContent" class="text-gray-400 text-sm">{{ locale === 'ko' ? '내용을 불러올 수 없습니다' : 'Content not available' }}</p>

      <!-- Source Link -->
      <div v-if="news?.url" class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-700">
        <a :href="news.url" target="_blank" rel="noopener noreferrer"
          class="inline-flex items-center gap-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-medium px-4 py-2 rounded-xl hover:bg-blue-100 dark:hover:bg-blue-900/50 transition text-sm">
          {{ locale === 'ko' ? '원본 기사 보기' : 'View Original' }} →
        </a>
      </div>
    </template>

    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        <h3 class="font-bold text-gray-800 dark:text-white text-sm px-4 py-3 border-b border-gray-100 dark:border-gray-700">
          {{ locale === 'ko' ? '관련 뉴스' : 'Related News' }}
        </h3>
        <div v-if="relatedNews.length">
          <router-link v-for="rn in relatedNews" :key="rn.id" :to="`/news/${rn.id}`"
            class="flex gap-3 py-3 px-3 hover:bg-blue-50/40 dark:hover:bg-gray-700/50 transition border-b border-gray-50 dark:border-gray-700 last:border-0">
            <div v-if="rn.image_url" class="flex-shrink-0 w-14 h-12 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700">
              <img :src="rn.image_url" class="w-full h-full object-cover" @error="e => e.target.src=''" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium text-gray-800 dark:text-gray-200 line-clamp-2 leading-snug">{{ rn.title }}</p>
              <p class="text-[10px] text-gray-400 mt-0.5">{{ rn.source }} · {{ timeAgo(rn.published_at) }}</p>
            </div>
          </router-link>
        </div>
        <div v-else class="text-center py-10 text-gray-400 text-sm">{{ locale === 'ko' ? '관련 뉴스가 없습니다' : 'No related news' }}</div>
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

const news = ref(null)
const loading = ref(true)
const relatedNews = ref([])
const heroImage = ref(null)

const breadcrumb = computed(() => [
  { label: locale.value === 'ko' ? '뉴스' : 'News', to: '/news' },
  { label: news.value?.sub_category?.name || news.value?.category || '' }
])

const formattedContent = computed(() => {
  if (!news.value) return ''
  let content = news.value.content_html || news.value.content || ''
  // Clean bylines
  content = content.replace(/기사를\s*읽어드립니다/g, '')
  content = content.replace(/Your browser does not support\s*the?\s*audio element\.?/gi, '')
  return content
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString(locale.value === 'ko' ? 'ko-KR' : 'en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

function timeAgo(dt) {
  if (!dt) return ''
  const diff = Date.now() - new Date(dt).getTime()
  const hrs = Math.floor(diff / 3600000)
  if (hrs < 1) return locale.value === 'ko' ? '방금' : 'Just now'
  if (hrs < 24) return `${hrs}${locale.value === 'ko' ? '시간 전' : 'h ago'}`
  const days = Math.floor(hrs / 24)
  return `${days}${locale.value === 'ko' ? '일 전' : 'd ago'}`
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/news/${news.value.id}/like`)
    news.value.is_liked = data.liked
    news.value.like_count = data.like_count
  } catch { /* empty */ }
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/news/${news.value.id}/bookmark`)
    news.value.is_bookmarked = data.bookmarked
  } catch { /* empty */ }
}

async function loadRelatedNews() {
  try {
    const params = { per_page: 5 }
    if (news.value.category) params.category = news.value.category
    const { data } = await axios.get('/api/news', { params })
    relatedNews.value = (data.data || []).filter(n => n.id !== news.value.id).slice(0, 5)
  } catch { /* empty */ }
}

watch(() => route.params.id, () => { if (route.params.id) loadNews() })

async function loadNews() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/news/${route.params.id}`)
    news.value = data
    heroImage.value = data.image_url || null
    loadRelatedNews()
  } catch { news.value = null }
  loading.value = false
}

onMounted(loadNews)
</script>

<style scoped>
.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1rem 0;
}
.article-content :deep(p) {
  margin-bottom: 0.75rem;
}
</style>
