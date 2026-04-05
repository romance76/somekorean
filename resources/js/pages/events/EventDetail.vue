<template>
  <DetailTemplate
    :item="event"
    :loading="loading"
    :images="event?.image_url ? [event.image_url] : []"
    :showAuthor="true"
    :showActions="true"
    :showComments="true"
    commentType="event"
    :breadcrumb="[{ label: '이벤트', to: '/events' }, { label: event?.title || '' }]"
    @like="toggleLike"
    @bookmark="toggleBookmark"
  >
    <template #header>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <!-- Badges -->
        <div class="flex items-center gap-2 mb-3 flex-wrap">
          <span class="text-xs bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-400 px-2.5 py-1 rounded-full font-medium">
            {{ categoryLabel(event.category) }}
          </span>
          <span v-if="event.is_online" class="text-xs bg-green-100 text-green-600 px-2.5 py-1 rounded-full font-medium">온라인</span>
          <span v-if="isPastEvent" class="text-xs bg-red-100 text-red-600 px-2.5 py-1 rounded-full font-medium">종료됨</span>
          <div v-if="canEdit" class="ml-auto flex gap-2">
            <RouterLink :to="`/events/create?edit=${event.id}`" class="text-xs text-blue-500 bg-blue-50 px-3 py-1.5 rounded-lg hover:bg-blue-100">수정</RouterLink>
            <button @click="deleteEvent" class="text-xs text-red-500 bg-red-50 px-3 py-1.5 rounded-lg hover:bg-red-100">삭제</button>
          </div>
        </div>

        <h1 class="text-xl font-black text-gray-800 dark:text-white mb-2">{{ event.title }}</h1>

        <!-- Stats grid -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4">
          <div class="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-xl">
            <div class="text-2xl font-black text-purple-600 dark:text-purple-400">{{ event.attendee_count || 0 }}</div>
            <div class="text-xs text-gray-500">참가자</div>
          </div>
          <div class="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-xl">
            <div v-if="event.price" class="text-2xl font-black text-green-600 dark:text-green-400">${{ Number(event.price).toLocaleString() }}</div>
            <div v-else class="text-xl font-black text-green-600 dark:text-green-400">무료</div>
            <div class="text-xs text-gray-500">참가비</div>
          </div>
          <div class="text-center p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl">
            <div class="text-lg font-black text-indigo-600 dark:text-indigo-400">{{ daysUntilEvent }}</div>
            <div class="text-xs text-gray-500">{{ isPastEvent ? '종료됨' : '남은 일수' }}</div>
          </div>
          <div v-if="event.max_attendees" class="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-xl">
            <div class="text-2xl font-black text-gray-600 dark:text-gray-300">{{ event.max_attendees }}</div>
            <div class="text-xs text-gray-500">최대 정원</div>
          </div>
        </div>

        <!-- Attend button -->
        <div class="flex gap-3 mt-4">
          <button v-if="auth.isLoggedIn" @click="toggleAttend"
            :disabled="attendLoading"
            class="px-6 py-2.5 rounded-xl font-semibold text-sm transition disabled:opacity-50"
            :class="event.is_attending
              ? 'bg-red-50 text-red-500 border border-red-200 hover:bg-red-100'
              : 'bg-purple-600 text-white hover:bg-purple-700'">
            {{ attendLoading ? '...' : event.is_attending ? '참가 취소' : '참가 신청' }}
          </button>
          <RouterLink v-else to="/auth/login"
            class="px-6 py-2.5 rounded-xl font-semibold text-sm bg-purple-600 text-white hover:bg-purple-700">
            로그인 후 참가
          </RouterLink>
        </div>

        <!-- Event info -->
        <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 space-y-2 text-sm">
          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-300">
            <span>📅</span>
            <span>{{ formatDate(event.event_date) }}</span>
            <span v-if="event.end_date">~ {{ formatDate(event.end_date) }}</span>
          </div>
          <div v-if="event.location" class="flex items-center gap-2 text-gray-600 dark:text-gray-300">
            <span>📍</span>
            <span>{{ event.location }}<span v-if="event.region">, {{ event.region }}</span></span>
          </div>
          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-300">
            <span>👤</span>
            <span>주최: {{ event.user?.name || '커뮤니티' }}</span>
          </div>
        </div>
      </div>
    </template>

    <template #body>
      <h2 class="text-sm font-bold text-gray-700 dark:text-white mb-3">이벤트 소개</h2>
      <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed whitespace-pre-line">{{ event.description || '설명이 없습니다.' }}</p>
    </template>

    <template #after-body>
      <!-- Map -->
      <div v-if="event.latitude && event.longitude" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-100 dark:border-gray-700">
          <h2 class="text-sm font-bold text-gray-700 dark:text-white">📍 장소</h2>
        </div>
        <iframe
          :src="`https://maps.google.com/maps?q=${event.latitude},${event.longitude}&output=embed`"
          class="w-full h-[250px] border-0" allowfullscreen loading="lazy"></iframe>
        <div class="px-5 py-3 text-sm text-gray-600 dark:text-gray-400">
          {{ event.location }}<span v-if="event.region">, {{ event.region }}</span>
        </div>
      </div>

      <!-- Attendees -->
      <div v-if="event.attendees?.length" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <h2 class="text-sm font-bold text-gray-700 dark:text-white mb-3">참가자 {{ event.attendee_count }}명</h2>
        <div class="flex flex-wrap gap-2">
          <div v-for="att in event.attendees" :key="att.id"
            class="flex items-center gap-2 bg-gray-50 dark:bg-gray-700 rounded-full px-3 py-1.5">
            <div class="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center text-xs font-bold text-purple-600">
              {{ (att.name || '?')[0] }}
            </div>
            <span class="text-sm text-gray-700 dark:text-gray-300">{{ att.name }}</span>
          </div>
        </div>
      </div>
    </template>

    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4">
        <h3 class="font-bold text-gray-800 dark:text-white text-sm mb-3">관련 이벤트</h3>
        <div v-if="relatedEvents.length === 0" class="text-center py-4 text-gray-400 text-sm">관련 이벤트가 없습니다</div>
        <div v-else class="space-y-3">
          <RouterLink v-for="r in relatedEvents" :key="r.id" :to="`/events/${r.id}`"
            class="block p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition border border-gray-100 dark:border-gray-600">
            <p class="text-sm font-bold text-gray-800 dark:text-white line-clamp-2">{{ r.title }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ formatDate(r.event_date) }} · {{ r.attendee_count || 0 }}명</p>
          </RouterLink>
        </div>
      </div>
    </template>
  </DetailTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DetailTemplate from '@/components/templates/DetailTemplate.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const event = ref(null)
const loading = ref(true)
const attendLoading = ref(false)
const relatedEvents = ref([])

const canEdit = computed(() => auth.user && event.value && (auth.user.id === event.value.user_id || auth.user.is_admin))
const isPastEvent = computed(() => event.value?.event_date ? new Date(event.value.event_date) < new Date() : false)
const daysUntilEvent = computed(() => {
  if (!event.value?.event_date) return '-'
  const diff = Math.ceil((new Date(event.value.event_date) - new Date()) / (1000 * 60 * 60 * 24))
  if (diff < 0) return `${Math.abs(diff)}일 전`
  if (diff === 0) return 'D-Day'
  return `D-${diff}`
})

const catLabels = { general: '일반', meetup: '모임', food: '음식', culture: '문화', sports: '스포츠', education: '교육', business: '비즈니스' }
function categoryLabel(c) { return catLabels[c] || c || '일반' }

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function toggleAttend() {
  if (!auth.isLoggedIn) return
  attendLoading.value = true
  try {
    const { data } = await axios.post(`/api/events/${event.value.id}/attend`)
    event.value.is_attending = data.attending
    event.value.attendee_count = data.attendee_count
    if (data.attendees) event.value.attendees = data.attendees
  } catch (e) {
    alert(e.response?.data?.message || '오류가 발생했습니다.')
  } finally {
    attendLoading.value = false
  }
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/events/${event.value.id}/like`)
    event.value.is_liked = data.liked
    event.value.like_count = data.like_count
  } catch {}
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/events/${event.value.id}/bookmark`)
    event.value.is_bookmarked = data.bookmarked
  } catch {}
}

async function deleteEvent() {
  if (!confirm('이벤트를 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/events/${event.value.id}`)
    router.push('/events')
  } catch {}
}

onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/events/${route.params.id}`)
    event.value = data
  } catch { event.value = null }

  if (event.value?.category) {
    try {
      const { data } = await axios.get(`/api/events?category=${event.value.category}&limit=5`)
      relatedEvents.value = (data.data || data || []).filter(e => e.id !== event.value.id).slice(0, 5)
    } catch {}
  }

  loading.value = false
})
</script>
