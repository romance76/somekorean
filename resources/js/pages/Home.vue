<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Hero Section -->
    <div class="bg-gradient-to-br from-blue-700 via-blue-600 to-indigo-700 text-white relative overflow-hidden">
      <div class="absolute inset-0 opacity-10"
        style="background-image:url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2260%22 height=%2260%22><g fill=%22%23fff%22 fill-opacity=%220.5%22><rect x=%2226%22 y=%220%22 width=%222%22 height=%2260%22/><rect x=%220%22 y=%2226%22 width=%2260%22 height=%222%22/></g></svg>')">
      </div>
      <div class="max-w-[1200px] mx-auto px-4 py-12 relative">
        <div class="text-center">
          <div class="inline-flex items-center gap-2 bg-white/20 rounded-full px-4 py-1.5 text-sm mb-5 backdrop-blur-sm">
            <span>🇰🇷</span>
            <span class="font-semibold">{{ locale === 'ko' ? '미국 한인 No.1 커뮤니티' : 'Korean American #1 Community' }}</span>
          </div>
          <h1 class="text-4xl md:text-5xl font-black tracking-tight">SomeKorean</h1>
          <p class="mt-3 text-blue-100 text-lg max-w-md mx-auto">
            {{ locale === 'ko'
              ? '미국 한인의 일상을 함께하는 올인원 플랫폼'
              : 'The all-in-one platform for Korean Americans' }}
          </p>
          <!-- CTA Buttons -->
          <div v-if="!auth.isLoggedIn" class="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
            <router-link to="/auth/register"
              class="bg-white text-blue-700 font-bold px-8 py-3 rounded-xl hover:bg-blue-50 transition shadow-lg">
              {{ locale === 'ko' ? '🚀 무료로 시작하기' : '🚀 Get Started Free' }}
            </router-link>
            <router-link to="/auth/login"
              class="border-2 border-white/50 text-white font-semibold px-8 py-3 rounded-xl hover:bg-white/10 transition">
              {{ t('auth.login') }}
            </router-link>
          </div>
          <div v-else class="mt-6 inline-flex items-center gap-3 bg-white/15 backdrop-blur-sm rounded-2xl px-5 py-3">
            <div class="w-10 h-10 rounded-full overflow-hidden bg-white/30 flex items-center justify-center text-base font-bold flex-shrink-0">
              <img v-if="auth.user?.avatar" :src="auth.user.avatar" class="w-full h-full object-cover" />
              <span v-else>{{ (auth.user?.name || '?')[0] }}</span>
            </div>
            <div class="text-left">
              <div class="font-bold text-sm">{{ locale === 'ko' ? '안녕하세요, ' : 'Welcome, ' }}{{ auth.user?.name }}님! 👋</div>
              <div class="text-blue-200 text-xs mt-0.5">⭐ {{ (auth.user?.points ?? 0).toLocaleString() }}P · {{ auth.user?.level }}</div>
            </div>
          </div>
        </div>

        <!-- Stats Bar -->
        <div class="mt-10 grid grid-cols-4 gap-3 max-w-2xl mx-auto">
          <div class="text-center bg-white/10 backdrop-blur-sm rounded-xl py-3 px-2">
            <div class="text-2xl font-black">{{ stats.users }}</div>
            <div class="text-blue-200 text-xs mt-0.5">{{ locale === 'ko' ? '회원' : 'Members' }}</div>
          </div>
          <div class="text-center bg-white/10 backdrop-blur-sm rounded-xl py-3 px-2">
            <div class="text-2xl font-black">{{ stats.posts }}</div>
            <div class="text-blue-200 text-xs mt-0.5">{{ locale === 'ko' ? '게시글' : 'Posts' }}</div>
          </div>
          <div class="text-center bg-white/10 backdrop-blur-sm rounded-xl py-3 px-2">
            <div class="text-2xl font-black">{{ stats.businesses }}</div>
            <div class="text-blue-200 text-xs mt-0.5">{{ locale === 'ko' ? '업소' : 'Businesses' }}</div>
          </div>
          <div class="text-center bg-white/10 backdrop-blur-sm rounded-xl py-3 px-2">
            <div class="text-2xl font-black">{{ stats.jobs }}</div>
            <div class="text-blue-200 text-xs mt-0.5">{{ locale === 'ko' ? '채용공고' : 'Job Posts' }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-[1200px] mx-auto px-4 py-8 space-y-8">

      <!-- Service Grid -->
      <div>
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-black text-gray-800">{{ locale === 'ko' ? '주요 서비스' : 'Our Services' }}</h2>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <router-link v-for="feat in features" :key="feat.path" :to="feat.path"
            class="bg-white rounded-2xl p-4 flex items-center gap-3 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all group border border-gray-100">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center text-xl flex-shrink-0"
              :style="{ backgroundColor: feat.bg }">{{ feat.icon }}</div>
            <div class="min-w-0">
              <div class="font-semibold text-gray-800 group-hover:text-blue-600 transition text-sm leading-tight">{{ feat.name }}</div>
              <div class="text-[11px] text-gray-400 mt-0.5 line-clamp-1">{{ feat.desc }}</div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Posts + Jobs side by side -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- 최신 게시글 -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
            <h3 class="font-bold text-gray-800 flex items-center gap-2 text-sm">
              <span>💬</span>
              {{ locale === 'ko' ? '최신 게시글' : 'Latest Posts' }}
            </h3>
            <router-link to="/community" class="text-blue-600 text-xs font-semibold hover:text-blue-700">
              {{ locale === 'ko' ? '더보기 →' : 'More →' }}
            </router-link>
          </div>
          <div v-if="loadingPosts" class="text-center py-8 text-gray-400 text-sm">{{ t('common.loading') }}</div>
          <div v-else class="divide-y divide-gray-50">
            <router-link v-for="post in posts" :key="post.id" :to="`/community/post/${post.id}`"
              class="px-4 py-3 flex items-start gap-3 hover:bg-blue-50/50 transition block">
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-800 truncate">{{ post.title }}</div>
                <div class="flex items-center gap-2 mt-0.5">
                  <span class="text-xs text-gray-400">{{ post.user?.name }}</span>
                  <span class="text-gray-200 text-xs">·</span>
                  <span class="text-xs text-gray-400">👁 {{ post.view_count }}</span>
                  <span class="text-gray-200 text-xs">·</span>
                  <span class="text-xs text-gray-400">💬 {{ post.comment_count }}</span>
                </div>
              </div>
              <span v-if="post.like_count > 5" class="text-[11px] bg-red-50 text-red-500 px-1.5 py-0.5 rounded-full flex-shrink-0 font-semibold">🔥</span>
            </router-link>
            <div v-if="!posts.length" class="px-4 py-6 text-center text-sm text-gray-400">{{ t('common.noData') }}</div>
          </div>
        </div>

        <!-- 최신 구인구직 -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
            <h3 class="font-bold text-gray-800 flex items-center gap-2 text-sm">
              <span>💼</span>
              {{ locale === 'ko' ? '최신 구인구직' : 'Latest Jobs' }}
            </h3>
            <router-link to="/jobs" class="text-blue-600 text-xs font-semibold hover:text-blue-700">
              {{ locale === 'ko' ? '더보기 →' : 'More →' }}
            </router-link>
          </div>
          <div v-if="loadingJobs" class="text-center py-8 text-gray-400 text-sm">{{ t('common.loading') }}</div>
          <div v-else class="divide-y divide-gray-50">
            <router-link v-for="job in jobs" :key="job.id" :to="`/jobs/${job.id}`"
              class="px-4 py-3 hover:bg-blue-50/50 transition block">
              <div class="flex items-center gap-2 mb-0.5">
                <span class="text-[11px] px-1.5 py-0.5 rounded-full font-semibold"
                  :class="jobTypeColor(job.job_type)">{{ jobTypeLabel(job.job_type) }}</span>
                <span class="text-xs text-gray-400">{{ job.region }}</span>
              </div>
              <div class="text-sm font-medium text-gray-800 truncate">{{ job.title }}</div>
              <div class="text-xs text-gray-500 mt-0.5">{{ job.company_name }} · {{ job.salary_range }}</div>
            </router-link>
            <div v-if="!jobs.length" class="px-4 py-6 text-center text-sm text-gray-400">{{ t('common.noData') }}</div>
          </div>
        </div>
      </div>

      <!-- 중고장터 -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
          <h3 class="font-bold text-gray-800 flex items-center gap-2 text-sm">
            <span>🛍️</span>
            {{ locale === 'ko' ? '중고장터' : 'Marketplace' }}
          </h3>
          <router-link to="/market" class="text-blue-600 text-xs font-semibold hover:text-blue-700">
            {{ locale === 'ko' ? '더보기 →' : 'More →' }}
          </router-link>
        </div>
        <div v-if="loadingMarket" class="text-center py-6 text-gray-400 text-sm">{{ t('common.loading') }}</div>
        <div v-else-if="!market.length" class="px-4 py-6 text-center text-sm text-gray-400">{{ t('common.noData') }}</div>
        <div v-else class="grid grid-cols-3 sm:grid-cols-6">
          <router-link v-for="item in market" :key="item.id" :to="`/market/${item.id}`"
            class="p-3 hover:bg-blue-50/50 transition block border-r border-b border-gray-50 last:border-r-0">
            <div class="text-2xl mb-1">{{ categoryEmoji(item.category) }}</div>
            <div class="text-xs font-medium text-gray-800 truncate">{{ item.title }}</div>
            <div class="text-blue-600 font-bold text-xs mt-0.5">${{ Number(item.price).toLocaleString() }}</div>
            <div class="text-[10px] text-gray-400">{{ item.region }}</div>
          </router-link>
        </div>
      </div>

      <!-- 이벤트 -->
      <div v-if="events.length" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
          <h3 class="font-bold text-gray-800 flex items-center gap-2 text-sm">
            <span>🎉</span>
            {{ locale === 'ko' ? '다가오는 이벤트' : 'Upcoming Events' }}
          </h3>
          <router-link to="/events" class="text-blue-600 text-xs font-semibold hover:text-blue-700">
            {{ locale === 'ko' ? '더보기 →' : 'More →' }}
          </router-link>
        </div>
        <div class="divide-y divide-gray-50">
          <router-link v-for="ev in events" :key="ev.id" :to="`/events/${ev.id}`"
            class="px-4 py-3 flex gap-3 hover:bg-blue-50/50 transition block">
            <div class="w-12 h-12 bg-blue-100 rounded-xl flex flex-col items-center justify-center flex-shrink-0">
              <div class="text-[10px] text-blue-600 font-bold uppercase leading-none">{{ formatEventDate(ev.event_date).month }}</div>
              <div class="text-xl font-black text-blue-700 leading-tight">{{ formatEventDate(ev.event_date).day }}</div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-800 truncate">{{ ev.title }}</div>
              <div class="text-xs text-gray-500 mt-0.5">📍 {{ ev.location }} · {{ ev.region }}</div>
              <div class="text-xs text-gray-400">👥 {{ ev.attendee_count || 0 }}/{{ ev.max_attendees }}{{ locale === 'ko' ? '명' : ' ppl' }}</div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- 📰 어제의 뉴스 요약 -->
      <div v-if="yesterdayNews.items?.length" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="flex items-center justify-between px-4 py-3 border-b border-gray-100 bg-gray-50/50">
          <h3 class="font-bold text-gray-800 flex items-center gap-2 text-sm">
            <span>📰</span>
            {{ locale === 'ko' ? '어제의 뉴스 요약' : "Yesterday's News" }}
            <span class="text-[10px] text-gray-400 font-normal">{{ formatNewsDate(yesterdayNews.date) }}</span>
          </h3>
          <router-link to="/news" class="text-blue-600 text-xs font-semibold hover:text-blue-700">
            {{ locale === 'ko' ? '뉴스 전체 →' : 'All News →' }}
          </router-link>
        </div>
        <div class="divide-y divide-gray-50">
          <router-link
            v-for="item in yesterdayNews.items"
            :key="item.id"
            :to="`/news/${item.id}`"
            class="flex items-start gap-3 px-4 py-2.5 hover:bg-blue-50/40 transition group">
            <!-- 카테고리 뱃지 -->
            <span class="flex-shrink-0 mt-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded-full whitespace-nowrap"
              :class="newsCatColor(item.category)">
              {{ item.category }}
            </span>
            <!-- 제목 -->
            <div class="flex-1 min-w-0">
              <div class="text-xs font-medium text-gray-800 line-clamp-1 group-hover:text-blue-600 transition leading-snug">
                {{ item.title }}
              </div>
              <div class="text-[10px] text-gray-400 mt-0.5">{{ item.source }} · {{ formatTimeAgo(item.published_at) }}</div>
            </div>
            <!-- 썸네일 -->
            <img v-if="item.image_url" :src="item.image_url"
              class="flex-shrink-0 w-12 h-10 rounded-lg object-cover bg-gray-100"
              @error="item.image_url = null" />
          </router-link>
        </div>
        <div class="px-4 py-2 text-center border-t border-gray-50">
          <router-link to="/news" class="text-xs text-blue-500 hover:text-blue-700 font-medium">
            {{ locale === 'ko' ? `어제 뉴스 ${yesterdayNews.total}건 전체 보기` : `View all ${yesterdayNews.total} news` }} →
          </router-link>
        </div>
      </div>

      <!-- 앱 설치 CTA -->
      <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-6 text-white text-center shadow-lg">
        <div class="text-4xl mb-2">📱</div>
        <h3 class="font-black text-xl">{{ locale === 'ko' ? '앱으로 더 편리하게!' : 'Use as an App!' }}</h3>
        <p class="text-blue-100 text-sm mt-2">
          {{ locale === 'ko' ? '홈화면에 추가하면 앱처럼 사용할 수 있어요' : 'Add to home screen for an app-like experience' }}
        </p>
        <div class="mt-3 text-xs text-blue-200 space-y-0.5">
          <div>{{ locale === 'ko' ? '📱 iOS: Safari → 공유 → 홈 화면에 추가' : '📱 iOS: Safari → Share → Add to Home Screen' }}</div>
          <div>{{ locale === 'ko' ? '🤖 Android: Chrome → 메뉴 → 앱 설치' : '🤖 Android: Chrome → Menu → Install App' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLangStore } from '../stores/lang'
import axios from 'axios'

const auth      = useAuthStore()
const langStore = useLangStore()
const locale    = computed(() => langStore.locale)
function t(key) { return langStore.$t(key) }

const posts         = ref([])
const jobs          = ref([])
const market        = ref([])
const events        = ref([])
const yesterdayNews = ref({ date: '', total: 0, items: [] })

const loadingPosts  = ref(false)
const loadingJobs   = ref(false)
const loadingMarket = ref(false)
const loadingEvents = ref(false)

const stats = ref({ users: '52+', posts: '50+', businesses: '50+', jobs: '51+' })

const features = computed(() => {
  const ko = locale.value === 'ko'
  return [
    { path:'/community',   icon:'💬', name: ko?'커뮤니티':'Community',     desc: ko?'한인 게시판 & 정보공유':'Boards & Info Sharing',   bg:'#dbeafe' },
    { path:'/jobs',        icon:'💼', name: ko?'구인구직':'Jobs',           desc: ko?'한인 채용공고 & 이력서':'Korean Job Listings',      bg:'#dcfce7' },
    { path:'/market',      icon:'🛍️', name: ko?'중고장터':'Marketplace',   desc: ko?'한인 중고거래 마켓':'Buy & Sell Used Items',         bg:'#fef9c3' },
    { path:'/directory',   icon:'🏪', name: ko?'업소록':'Directory',        desc: ko?'한인 업체 검색 & 리뷰':'Find Korean Businesses',    bg:'#f3e8ff' },
    { path:'/realestate',  icon:'🏠', name: ko?'부동산':'Real Estate',      desc: ko?'렌트 & 매매 정보':'Rent & Buy Properties',          bg:'#e0f2fe' },
    { path:'/ride',        icon:'🚗', name: ko?'알바 라이드':'Ride',        desc: ko?'한인 카풀 & 라이드셰어':'Korean Ride Sharing',       bg:'#fee2e2' },
    { path:'/chat',        icon:'💬', name: ko?'실시간 채팅':'Live Chat',   desc: ko?'지역별 · 테마별 단톡방':'Group Chat Rooms',          bg:'#e0f2fe' },
    { path:'/match',       icon:'💝', name: ko?'매칭':'Matching',           desc: ko?'나이별 한인 매칭 서비스':'Meet Korean Americans',    bg:'#fce7f3' },
    { path:'/clubs',       icon:'👥', name: ko?'동호회':'Clubs',            desc: ko?'관심사별 모임 & 동호회':'Interest-Based Groups',     bg:'#f0fdf4' },
    { path:'/games',       icon:'🀄', name: ko?'게임 & 포인트':'Games',     desc: ko?'고스톱 · 포커 · 퀴즈':'Go-Stop · Poker · Quiz',    bg:'#fef3c7' },
    { path:'/events',      icon:'🎉', name: ko?'이벤트':'Events',           desc: ko?'한인 모임 & 행사':'Korean Community Events',         bg:'#d1fae5' },
    { path:'/elder',       icon:'💙', name: ko?'노인 안심':'Elder Care',    desc: ko?'체크인 & 보호자 알림':'Check-in & Guardian Alert',  bg:'#e0e7ff' },
    { path:'/mentor',      icon:'🎓', name: ko?'멘토링':'Mentoring',        desc: ko?'한인 선배 멘토 매칭':'Korean Mentor Matching',       bg:'#ccfbf1' },
    { path:'/groupbuy',    icon:'🤝', name: ko?'공동구매':'Group Buy',       desc: ko?'함께 사면 더 저렴하게':'Save More Together',         bg:'#fff7ed' },
    { path:'/news',        icon:'📰', name: ko?'한인 뉴스':'Korean News',   desc: ko?'이민 · 경제 · 생활 뉴스':'Immigration & Local News', bg:'#f0fdf4' },
    { path:'/ai',          icon:'🤖', name: ko?'AI 검색':'AI Search',       desc: ko?'AI 기반 스마트 검색':'Smart AI-Powered Search',      bg:'#f5f3ff' },
  ]
})

function jobTypeLabel(type) {
  const ko = locale.value === 'ko'
  const labels = {
    full_time:  ko?'풀타임':'Full-time',
    part_time:  ko?'파트타임':'Part-time',
    contract:   ko?'계약직':'Contract',
    freelance:  ko?'프리랜서':'Freelance',
  }
  return labels[type] ?? type
}
function jobTypeColor(type) {
  return {
    full_time: 'bg-blue-100 text-blue-700',
    part_time: 'bg-green-100 text-green-700',
    contract:  'bg-orange-100 text-orange-700',
    freelance: 'bg-purple-100 text-purple-700',
  }[type] ?? 'bg-gray-100 text-gray-600'
}
function categoryEmoji(cat) {
  return {
    Electronics:'📱', Furniture:'🛋️', Vehicles:'🚗', Appliances:'🏠',
    Clothing:'👕', Sports:'⚽', Baby:'👶', Books:'📚', Food:'🍱', Retail:'🛒'
  }[cat] ?? '📦'
}
function newsCatColor(cat) {
  const map = {
    '이민/비자': 'bg-purple-100 text-purple-700',
    '미국생활':  'bg-blue-100 text-blue-700',
    '정치/사회': 'bg-red-100 text-red-700',
    '경제':      'bg-green-100 text-green-700',
    '생활':      'bg-orange-100 text-orange-700',
    '문화':      'bg-pink-100 text-pink-700',
    '스포츠':    'bg-yellow-100 text-yellow-700',
  }
  return map[cat] ?? 'bg-gray-100 text-gray-600'
}

function formatNewsDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const lang = locale.value === 'ko' ? 'ko-KR' : 'en-US'
  return d.toLocaleDateString(lang, { month: 'long', day: 'numeric' })
}

function formatTimeAgo(dt) {
  if (!dt) return ''
  const diff = Date.now() - new Date(dt).getTime()
  const h = Math.floor(diff / 3600000)
  if (h < 1) return locale.value === 'ko' ? '방금' : 'just now'
  if (h < 24) return locale.value === 'ko' ? `${h}시간 전` : `${h}h ago`
  const d = Math.floor(h / 24)
  return locale.value === 'ko' ? `${d}일 전` : `${d}d ago`
}

function formatEventDate(dt) {
  if (!dt) return { month: '?', day: '?' }
  const d = new Date(dt)
  const lang = locale.value === 'ko' ? 'ko-KR' : 'en-US'
  return { month: d.toLocaleDateString(lang, { month: 'short' }), day: d.getDate() }
}

async function loadAll() {
  loadingPosts.value  = true
  loadingJobs.value   = true
  loadingMarket.value = true
  loadingEvents.value = true

  const [postsRes, jobsRes, marketRes, eventsRes, newsRes] = await Promise.allSettled([
    axios.get('/api/posts?per_page=6'),
    axios.get('/api/jobs?per_page=6'),
    axios.get('/api/market?per_page=6'),
    axios.get('/api/events?per_page=3'),
    axios.get('/api/news/yesterday-summary'),
  ])

  if (postsRes.status === 'fulfilled')  posts.value  = postsRes.value.data?.data?.slice(0, 6)  ?? []
  if (jobsRes.status === 'fulfilled')   jobs.value   = jobsRes.value.data?.data?.slice(0, 6)   ?? []
  if (marketRes.status === 'fulfilled') market.value = marketRes.value.data?.data?.slice(0, 6) ?? []
  if (eventsRes.status === 'fulfilled') events.value = eventsRes.value.data?.data?.slice(0, 3) ?? []
  if (newsRes.status === 'fulfilled')   yesterdayNews.value = newsRes.value.data ?? { date: '', total: 0, items: [] }

  loadingPosts.value  = false
  loadingJobs.value   = false
  loadingMarket.value = false
  loadingEvents.value = false
}

onMounted(loadAll)
</script>
