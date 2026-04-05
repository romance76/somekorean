<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">

      <!-- 인라인 그라디언트 헤더 -->
      <div class="bg-gradient-to-r from-red-700 to-orange-500 text-white px-6 py-4 rounded-2xl mb-4">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <router-link to="/directory" class="text-white/70 text-sm hover:text-white transition">← 업소록</router-link>
            <span v-if="biz?.category" class="bg-white/20 text-xs px-3 py-1 rounded-full">{{ biz.category }}</span>
            <span v-if="biz?.is_verified" class="bg-green-500/80 text-xs px-3 py-1 rounded-full">✓ 인증</span>
          </div>
          <div class="flex items-center gap-2">
            <button @click="shareBusiness"
              class="flex items-center gap-1 text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
              공유
            </button>
            <button @click="toggleBookmark"
              :class="['flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg transition',
                bookmarked ? 'bg-yellow-400/30 text-yellow-200' : 'text-white/80 hover:text-white bg-white/10 hover:bg-white/20']">
              <svg class="w-3.5 h-3.5" :fill="bookmarked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/></svg>
              북마크
            </button>
          </div>
        </div>
        <h1 class="text-xl font-black leading-tight mb-1">{{ biz?.name }}</h1>
        <div class="flex items-center gap-3 text-sm text-white/80">
          <span v-if="biz?.category">{{ biz.category }}</span>
          <span v-if="biz?.view_count != null">· 조회 {{ biz.view_count }}</span>
        </div>
      </div>

      <div v-if="loading" class="text-center py-20 text-gray-400">불러오는 중...</div>
      <template v-else-if="biz">

        <!-- 2컬럼 레이아웃 -->
        <div class="flex gap-5 items-start">

          <!-- 왼쪽 본문 -->
          <div class="flex-1 min-w-0">

            <!-- 인포 카드 (평점) -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-4">
              <div class="flex items-center gap-2 mb-3">
                <div class="flex text-yellow-400">
                  <span v-for="i in 5" :key="i" class="text-lg">{{ i <= Math.round(Number(biz.rating_avg)) ? '★' : '☆' }}</span>
                </div>
                <span class="font-bold text-gray-800">{{ Number(biz.rating_avg).toFixed(1) }}</span>
                <span class="text-sm text-gray-400">(리뷰 {{ biz.review_count }}개)</span>
              </div>
              <p v-if="biz.description" class="text-gray-600 text-sm leading-relaxed">{{ biz.description }}</p>
            </div>

            <!-- 사진 -->
            <div v-if="biz.photos && biz.photos.length" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-4">
              <h3 class="font-semibold text-gray-800 mb-3">📷 사진</h3>
              <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                <div v-for="(photo, idx) in biz.photos" :key="idx"
                  class="aspect-square rounded-lg overflow-hidden cursor-pointer hover:opacity-90 transition"
                  @click="openPhoto(idx)">
                  <img :src="photo.url || photo" :alt="`${biz.name} 사진`" class="w-full h-full object-cover" />
                </div>
              </div>
              <div v-if="photoModal !== null" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4" @click="photoModal = null">
                <button class="absolute top-4 right-4 text-white text-3xl" @click="photoModal = null">&times;</button>
                <button v-if="photoModal > 0" class="absolute left-4 text-white text-4xl" @click.stop="photoModal--">&lsaquo;</button>
                <button v-if="photoModal < biz.photos.length - 1" class="absolute right-4 text-white text-4xl" @click.stop="photoModal++">&rsaquo;</button>
                <img :src="biz.photos[photoModal]?.url || biz.photos[photoModal]" class="max-w-full max-h-[80vh] rounded-lg" @click.stop />
              </div>
            </div>

            <!-- 업소 정보 + 영업시간 그리드 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
              <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                <h3 class="font-semibold text-gray-800 mb-4">📋 업소 정보</h3>
                <div class="space-y-3 text-sm">
                  <div v-if="biz.address" class="flex items-start gap-2">
                    <span class="text-gray-400 mt-0.5">📍</span>
                    <span class="text-gray-700">{{ biz.address }}</span>
                  </div>
                  <div v-if="biz.phone" class="flex items-center gap-2">
                    <span class="text-gray-400">📞</span>
                    <a :href="`tel:${biz.phone}`" class="text-red-600 hover:underline font-medium">{{ biz.phone }}</a>
                  </div>
                  <div v-if="biz.website" class="flex items-center gap-2">
                    <span class="text-gray-400">🌐</span>
                    <a @click="trackClick('website')" :href="biz.website" target="_blank" rel="noopener" class="text-red-600 hover:underline truncate">{{ biz.website }}</a>
                  </div>
                  <div v-if="biz.email" class="flex items-center gap-2">
                    <span class="text-gray-400">✉️</span>
                    <a :href="`mailto:${biz.email}`" class="text-red-600 hover:underline">{{ biz.email }}</a>
                  </div>
                </div>
                <a v-if="biz.address"
                  :href="`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(biz.address)}`"
                  target="_blank" rel="noopener"
                  class="mt-4 inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-lg text-sm font-semibold hover:bg-blue-700 transition">
                  🧭 길찾기
                </a>
              </div>
              <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                <h3 class="font-semibold text-gray-800 mb-4">🕐 영업시간</h3>
                <table v-if="parsedHours" class="w-full text-sm">
                  <tbody>
                    <tr v-for="day in weekDays" :key="day.key"
                      class="border-b border-gray-50 last:border-0"
                      :class="{ 'bg-red-50/50': isToday(day.key) }">
                      <td class="py-2.5 pr-4 font-medium text-gray-700 whitespace-nowrap">
                        <span v-if="isToday(day.key)" class="inline-block w-1.5 h-1.5 bg-red-500 rounded-full mr-1.5"></span>
                        {{ day.label }}
                      </td>
                      <td class="py-2.5 text-gray-600">{{ parsedHours[day.key] || '휴무' }}</td>
                    </tr>
                  </tbody>
                </table>
                <p v-else class="text-sm text-gray-400">영업시간 정보가 없습니다.</p>
              </div>
            </div>

            <!-- 지도 -->
            <div v-if="biz.address || (biz.lat && biz.lng)" class="map-section">
              <LeafletMap :lat="biz.lat ? parseFloat(biz.lat) : null" :lng="biz.lng ? parseFloat(biz.lng) : null" :name="biz.name" :address="biz.address || ''" />
            </div>

            <!-- 소유권 신청 배너 -->
            <div v-if="!biz.is_claimed" class="claim-banner">
              <div>
                <p class="claim-title">🏪 이 업소의 사장님이신가요?</p>
                <p class="claim-sub">업소 정보를 직접 관리하고 고객과 소통하세요.</p>
              </div>
              <router-link :to="{ name: 'claim-business', params: { id: biz.id } }" class="claim-btn">내 업소 등록하기 →</router-link>
            </div>
            <div v-else-if="isOwner" class="owner-manage-banner">
              <router-link to="/dashboard" class="manage-btn">📊 내 업소 관리하기</router-link>
            </div>

            <!-- 리뷰 -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mb-4">
              <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
                <h3 class="font-semibold text-gray-800">💬 리뷰 {{ biz.reviews?.length || 0 }}개</h3>
                <div class="flex items-center gap-2">
                  <div class="flex text-yellow-400 text-lg">
                    <span v-for="i in 5" :key="i">{{ i <= Math.round(Number(biz.rating_avg)) ? '★' : '☆' }}</span>
                  </div>
                  <span class="font-bold text-gray-800">{{ Number(biz.rating_avg).toFixed(1) }}</span>
                </div>
              </div>
              <div v-if="biz.reviews?.length">
                <div v-for="review in biz.reviews" :key="review.id" class="px-5 py-4 border-b border-gray-50 last:border-0">
                  <div class="flex items-center justify-between mb-2">
                    <div class="flex items-center gap-2">
                      <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
                        {{ (review.user?.name || review.user_name || '익명')[0] }}
                      </div>
                      <div>
                        <span class="text-sm font-medium text-gray-700">{{ review.user?.name || review.user_name || '익명' }}</span>
                        <div class="flex text-yellow-400 text-xs">
                          <span v-for="i in 5" :key="i">{{ i <= review.rating ? '★' : '☆' }}</span>
                        </div>
                      </div>
                    </div>
                    <span v-if="review.created_at" class="text-xs text-gray-400">{{ formatDate(review.created_at) }}</span>
                  </div>
                  <p v-if="review.content" class="text-sm text-gray-600 leading-relaxed">{{ review.content }}</p>
                </div>
              </div>
              <div v-else class="px-5 py-10 text-center text-gray-400 text-sm">아직 리뷰가 없습니다.</div>
              <div v-if="authStore.isLoggedIn" class="px-5 py-4 bg-gray-50 border-t border-gray-100">
                <h4 class="text-sm font-semibold text-gray-700 mb-2">리뷰 작성</h4>
                <div class="flex items-center gap-1 mb-2">
                  <button v-for="i in 5" :key="i" @click="reviewForm.rating = i"
                    :class="['text-2xl transition-colors', i <= reviewForm.rating ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300']">★</button>
                  <span v-if="reviewForm.rating" class="ml-2 text-sm text-gray-500">{{ ratingLabels[reviewForm.rating - 1] }}</span>
                </div>
                <textarea v-model="reviewForm.content" rows="3" placeholder="이 업소에 대한 솔직한 리뷰를 남겨주세요..."
                  class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 resize-none mb-2"></textarea>
                <div class="flex justify-end">
                  <button @click="submitReview" :disabled="!reviewForm.rating || submitting"
                    class="bg-red-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-red-700 disabled:opacity-40 transition">
                    {{ submitting ? '등록 중...' : '리뷰 등록' }}
                  </button>
                </div>
              </div>
              <div v-else class="px-5 py-4 bg-gray-50 border-t border-gray-100 text-center">
                <p class="text-sm text-gray-500">리뷰를 작성하려면 <router-link to="/auth/login" class="text-red-600 hover:underline font-medium">로그인</router-link>이 필요합니다.</p>
              </div>
            </div>

            <router-link to="/directory" class="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-red-600 transition">← 업소 목록으로</router-link>
          </div>

          <!-- 오른쪽 사이드바 -->
          <aside class="hidden lg:block w-72 flex-shrink-0 sticky top-20">
            <div class="bg-white rounded-2xl shadow-sm overflow-hidden">
              <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <h3 class="text-sm font-bold text-gray-700">최신 업소</h3>
                <router-link to="/directory" class="text-xs text-red-500 hover:text-red-600">전체 →</router-link>
              </div>
              <ul v-if="latestBiz.length">
                <li v-for="b in latestBiz" :key="b.id" class="border-b border-gray-50 last:border-0">
                  <router-link :to="'/directory/' + b.id" class="block px-4 py-3.5 hover:bg-gray-50 transition">
                    <div class="flex items-center gap-3">
                      <div class="w-10 h-10 bg-red-100 rounded-lg overflow-hidden flex-shrink-0 flex items-center justify-center">
                        <img v-if="b.photos?.[0]" :src="b.photos[0]?.url || b.photos[0]" class="w-full h-full object-cover" />
                        <span v-else class="text-lg">🏪</span>
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-semibold text-gray-800 truncate">{{ b.name }}</p>
                        <div class="flex items-center gap-1 mt-0.5">
                          <span class="text-xs text-gray-400">{{ b.category }}</span>
                          <span v-if="b.rating_avg" class="text-xs text-yellow-500">· ★ {{ Number(b.rating_avg).toFixed(1) }}</span>
                        </div>
                      </div>
                    </div>
                  </router-link>
                </li>
              </ul>
              <div v-else class="px-4 py-8 text-center text-xs text-gray-400">목록이 없습니다.</div>
            </div>
          </aside>

        </div>
      </template>
      <div v-else class="text-center py-20">
        <p class="text-4xl mb-3">😢</p>
        <p class="text-gray-400">업소 정보를 찾을 수 없습니다.</p>
        <router-link to="/directory" class="mt-3 inline-block text-red-600 text-sm hover:underline">목록으로 돌아가기</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'
import LeafletMap from '../../components/LeafletMap.vue'

const route = useRoute()
const authStore = useAuthStore()
const biz = ref(null)
const loading = ref(true)
const bookmarked = ref(false)
const photoModal = ref(null)
const submitting = ref(false)
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
function openPhoto(idx) { photoModal.value = idx }
function formatDate(s) {
  if (!s) return ''
  const d = new Date(s)
  return d.getFullYear() + '.' + String(d.getMonth()+1).padStart(2,'0') + '.' + String(d.getDate()).padStart(2,'0')
}
async function trackClick(t) { try { await axios.post('/api/businesses/'+biz.value.id+'/stat/'+t) } catch {} }
async function toggleBookmark() {
  if (!authStore.isLoggedIn) { alert('로그인이 필요합니다.'); return }
  try { const { data } = await axios.post('/api/businesses/'+biz.value.id+'/bookmark'); bookmarked.value = data.bookmarked }
  catch { bookmarked.value = !bookmarked.value }
}
function shareBusiness() {
  const url = window.location.href
  if (navigator.share) navigator.share({ title: biz.value.name, url })
  else if (navigator.clipboard) { navigator.clipboard.writeText(url); alert('링크가 복사되었습니다.') }
}
async function submitReview() {
  if (submitting.value) return
  submitting.value = true
  try {
    await axios.post('/api/businesses/'+biz.value.id+'/review', reviewForm.value)
    const { data } = await axios.get('/api/businesses/'+biz.value.id)
    biz.value = data
    reviewForm.value = { rating: 0, content: '' }
  } catch(e) { alert(e.response?.data?.message || '오류가 발생했습니다.') }
  submitting.value = false
}
const isOwner = computed(() => authStore.user && biz.value && biz.value.owner_id === authStore.user.id)

async function loadLatestBiz() {
  try {
    const { data } = await axios.get('/api/businesses', { params: { per_page: 8 } })
    const list = data.data || data
    const currentId = Number(route.params.id)
    latestBiz.value = list.filter(b => b.id !== currentId).slice(0, 8)
  } catch {}
}

async function loadAll() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/businesses/'+route.params.id)
    biz.value = data
    bookmarked.value = data.is_bookmarked || false
  } catch {}
  loading.value = false
  loadLatestBiz()
}
onMounted(loadAll)
watch(() => route.params.id, loadAll)
</script>

<style scoped>
.claim-banner{display:flex;justify-content:space-between;align-items:center;background:#eff6ff;border:1px solid #bfdbfe;border-radius:14px;padding:16px 20px;margin:16px 0;gap:12px;flex-wrap:wrap}
.claim-title{font-size:15px;font-weight:700;color:#1e40af;margin:0 0 4px}
.claim-sub{font-size:13px;color:#3b82f6;margin:0}
.claim-btn{background:#2563eb;color:#fff;padding:10px 20px;border-radius:10px;font-size:14px;font-weight:700;text-decoration:none;white-space:nowrap}
.owner-manage-banner{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:14px;padding:14px 20px;margin:16px 0}
.manage-btn{color:#16a34a;font-weight:700;text-decoration:none}
.map-section{margin:16px 0}
</style>
