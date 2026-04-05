<template>
  <DetailTemplate
    :item="biz"
    :loading="loading"
    :images="biz?.photos?.map(p => p.url || p) || []"
    :showAuthor="false"
    :showActions="true"
    :showComments="false"
    commentType="business"
    :breadcrumb="[{ label: '업소록', to: '/directory' }, { label: biz?.name || '' }]"
    @like="() => {}"
    @bookmark="toggleBookmark"
  >
    <!-- Header: Business info -->
    <template #header>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <div class="flex items-center gap-2 mb-3">
          <span class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2.5 py-1 rounded-full">{{ biz.category }}</span>
          <span v-if="biz.is_verified" class="text-xs bg-green-100 text-green-600 px-2.5 py-1 rounded-full">✓ 인증</span>
        </div>
        <h1 class="text-xl font-black text-gray-800 dark:text-white mb-2">{{ biz.name }}</h1>

        <!-- Rating -->
        <div class="flex items-center gap-2 mb-3">
          <div class="flex text-yellow-400">
            <span v-for="i in 5" :key="i" class="text-lg">{{ i <= Math.round(Number(biz.rating_avg || 0)) ? '★' : '☆' }}</span>
          </div>
          <span class="font-bold text-gray-800 dark:text-white">{{ Number(biz.rating_avg || 0).toFixed(1) }}</span>
          <span class="text-sm text-gray-400">(리뷰 {{ biz.review_count || 0 }}개)</span>
        </div>

        <p v-if="biz.description" class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">{{ biz.description }}</p>
      </div>
    </template>

    <!-- Body: Contact info + Hours -->
    <template #body>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- Contact -->
        <div>
          <h3 class="font-semibold text-gray-800 dark:text-white mb-4">📋 업소 정보</h3>
          <div class="space-y-3 text-sm">
            <div v-if="biz.address" class="flex items-start gap-2">
              <span class="text-gray-400 mt-0.5">📍</span>
              <span class="text-gray-700 dark:text-gray-300">{{ biz.address }}</span>
            </div>
            <div v-if="biz.phone" class="flex items-center gap-2">
              <span class="text-gray-400">📞</span>
              <a :href="`tel:${biz.phone}`" class="text-blue-600 hover:underline font-medium">{{ biz.phone }}</a>
            </div>
            <div v-if="biz.email" class="flex items-center gap-2">
              <span class="text-gray-400">✉️</span>
              <a :href="`mailto:${biz.email}`" class="text-blue-600 hover:underline">{{ biz.email }}</a>
            </div>
            <div v-if="biz.website" class="flex items-center gap-2">
              <span class="text-gray-400">🌐</span>
              <a :href="biz.website" target="_blank" rel="noopener" class="text-blue-600 hover:underline truncate">{{ biz.website }}</a>
            </div>
          </div>
          <a v-if="biz.address"
            :href="`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(biz.address)}`"
            target="_blank" rel="noopener"
            class="mt-4 inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition">
            🧭 길찾기
          </a>
        </div>

        <!-- Hours -->
        <div>
          <h3 class="font-semibold text-gray-800 dark:text-white mb-4">🕐 영업시간</h3>
          <table v-if="parsedHours" class="w-full text-sm">
            <tbody>
              <tr v-for="day in weekDays" :key="day.key"
                class="border-b border-gray-50 dark:border-gray-700 last:border-0"
                :class="{ 'bg-blue-50/50 dark:bg-blue-900/20': isToday(day.key) }">
                <td class="py-2.5 pr-4 font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
                  <span v-if="isToday(day.key)" class="inline-block w-1.5 h-1.5 bg-blue-500 rounded-full mr-1.5"></span>
                  {{ day.label }}
                </td>
                <td class="py-2.5 text-gray-600 dark:text-gray-400">{{ parsedHours[day.key] || '휴무' }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-sm text-gray-400">영업시간 정보가 없습니다.</p>
        </div>
      </div>
    </template>

    <!-- After body: Map + Claim + Reviews -->
    <template #after-body>
      <!-- Map -->
      <div v-if="biz.address || (biz.lat && biz.lng)" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <LeafletMap :lat="biz.lat ? parseFloat(biz.lat) : null" :lng="biz.lng ? parseFloat(biz.lng) : null" :name="biz.name" :address="biz.address || ''" />
      </div>

      <!-- Claim banner -->
      <div v-if="!biz.is_claimed" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex items-center justify-between flex-wrap gap-3">
        <div>
          <p class="text-sm font-bold text-blue-800 dark:text-blue-300">🏪 이 업소의 사장님이신가요?</p>
          <p class="text-xs text-blue-600 dark:text-blue-400">업소 정보를 직접 관리하고 고객과 소통하세요.</p>
        </div>
        <RouterLink :to="`/directory/${biz.id}/claim`"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 transition whitespace-nowrap">
          내 업소 등록하기
        </RouterLink>
      </div>

      <!-- Reviews -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h3 class="font-semibold text-gray-800 dark:text-white">💬 리뷰 {{ biz.reviews?.length || 0 }}개</h3>
          <div class="flex items-center gap-2">
            <div class="flex text-yellow-400 text-lg">
              <span v-for="i in 5" :key="i">{{ i <= Math.round(Number(biz.rating_avg || 0)) ? '★' : '☆' }}</span>
            </div>
            <span class="font-bold text-gray-800 dark:text-white">{{ Number(biz.rating_avg || 0).toFixed(1) }}</span>
          </div>
        </div>

        <!-- Review list -->
        <div v-if="biz.reviews?.length">
          <div v-for="review in biz.reviews" :key="review.id" class="px-5 py-4 border-b border-gray-50 dark:border-gray-700 last:border-0">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white">
                  {{ (review.user?.name || '익명')[0] }}
                </div>
                <div>
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ review.user?.name || '익명' }}</span>
                  <div class="flex text-yellow-400 text-xs">
                    <span v-for="i in 5" :key="i">{{ i <= review.rating ? '★' : '☆' }}</span>
                  </div>
                </div>
              </div>
              <span class="text-xs text-gray-400">{{ formatDate(review.created_at) }}</span>
            </div>
            <p v-if="review.content" class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{{ review.content }}</p>
          </div>
        </div>
        <div v-else class="px-5 py-10 text-center text-gray-400 text-sm">아직 리뷰가 없습니다.</div>

        <!-- Write review form -->
        <div v-if="auth.isLoggedIn" class="px-5 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-100 dark:border-gray-700">
          <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">리뷰 작성</h4>
          <div class="flex items-center gap-1 mb-2">
            <button v-for="i in 5" :key="i" @click="reviewForm.rating = i"
              :class="['text-2xl transition-colors', i <= reviewForm.rating ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300']">★</button>
            <span v-if="reviewForm.rating" class="ml-2 text-sm text-gray-500">{{ ratingLabels[reviewForm.rating - 1] }}</span>
          </div>
          <textarea v-model="reviewForm.content" rows="3" placeholder="이 업소에 대한 솔직한 리뷰를 남겨주세요..."
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none mb-2"></textarea>
          <div class="flex justify-end">
            <button @click="submitReview" :disabled="!reviewForm.rating || submittingReview"
              class="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-40 transition">
              {{ submittingReview ? '등록 중...' : '리뷰 등록' }}
            </button>
          </div>
        </div>
        <div v-else class="px-5 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-100 dark:border-gray-700 text-center">
          <p class="text-sm text-gray-500">리뷰를 작성하려면 <RouterLink to="/auth/login" class="text-blue-600 hover:underline font-medium">로그인</RouterLink>이 필요합니다.</p>
        </div>
      </div>
    </template>

    <!-- Sidebar -->
    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-sm font-bold text-gray-700 dark:text-gray-300">최신 업소</h3>
          <RouterLink to="/directory" class="text-xs text-blue-500 hover:text-blue-600">전체</RouterLink>
        </div>
        <div v-if="latestBiz.length">
          <RouterLink v-for="b in latestBiz" :key="b.id" :to="`/directory/${b.id}`"
            class="block px-4 py-3 border-b border-gray-50 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700 transition">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-blue-100 rounded-lg overflow-hidden flex-shrink-0 flex items-center justify-center">
                <img v-if="b.photos?.[0]" :src="b.photos[0]?.url || b.photos[0]" class="w-full h-full object-cover"
                  @error="e => e.target.parentElement.innerHTML='<span class=\'text-lg\'>🏪</span>'" />
                <span v-else class="text-lg">🏪</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-gray-800 dark:text-white truncate">{{ b.name }}</p>
                <div class="flex items-center gap-1 mt-0.5">
                  <span class="text-xs text-gray-400">{{ b.category }}</span>
                  <span v-if="b.rating_avg" class="text-xs text-yellow-500">★ {{ Number(b.rating_avg).toFixed(1) }}</span>
                </div>
              </div>
            </div>
          </RouterLink>
        </div>
        <div v-else class="px-4 py-8 text-center text-xs text-gray-400">목록이 없습니다.</div>
      </div>
    </template>
  </DetailTemplate>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DetailTemplate from '@/components/templates/DetailTemplate.vue'
import LeafletMap from '@/components/LeafletMap.vue'
import axios from 'axios'

const route = useRoute()
const auth = useAuthStore()

const biz = ref(null)
const loading = ref(true)
const bookmarked = ref(false)
const submittingReview = ref(false)
const reviewForm = ref({ rating: 0, content: '' })
const latestBiz = ref([])
const ratingLabels = ['별로예요', '그저 그래요', '보통이에요', '좋아요', '최고예요']

const weekDays = [
  { key: 'mon', label: '월요일' }, { key: 'tue', label: '화요일' },
  { key: 'wed', label: '수요일' }, { key: 'thu', label: '목요일' },
  { key: 'fri', label: '금요일' }, { key: 'sat', label: '토요일' },
  { key: 'sun', label: '일요일' },
]

const dayIndexMap = { sun: 0, mon: 1, tue: 2, wed: 3, thu: 4, fri: 5, sat: 6 }
function isToday(k) { return new Date().getDay() === dayIndexMap[k] }

const parsedHours = computed(() => {
  if (!biz.value?.hours) return null
  try { return typeof biz.value.hours === 'string' ? JSON.parse(biz.value.hours) : biz.value.hours } catch { return null }
})

function formatDate(s) {
  if (!s) return ''
  const d = new Date(s)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { alert('로그인이 필요합니다.'); return }
  try {
    const { data } = await axios.post(`/api/businesses/${biz.value.id}/bookmark`)
    biz.value.is_bookmarked = data.bookmarked
  } catch {}
}

async function submitReview() {
  if (submittingReview.value) return
  submittingReview.value = true
  try {
    await axios.post(`/api/businesses/${biz.value.id}/review`, reviewForm.value)
    const { data } = await axios.get(`/api/businesses/${biz.value.id}`)
    biz.value = data
    reviewForm.value = { rating: 0, content: '' }
  } catch (e) {
    alert(e.response?.data?.message || '오류가 발생했습니다.')
  }
  submittingReview.value = false
}

async function loadAll() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/businesses/${route.params.id}`)
    biz.value = data
    bookmarked.value = data.is_bookmarked || false
  } catch {}
  loading.value = false

  try {
    const { data } = await axios.get('/api/businesses', { params: { per_page: 8 } })
    const list = data.data || data
    latestBiz.value = list.filter(b => b.id !== Number(route.params.id)).slice(0, 8)
  } catch {}
}

onMounted(loadAll)
watch(() => route.params.id, loadAll)
</script>
