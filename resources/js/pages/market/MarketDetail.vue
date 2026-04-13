<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <button @click="$router.back()" class="text-sm text-gray-500 hover:text-amber-600 mb-3">← 장터 목록</button>
    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="item" class="grid grid-cols-12 gap-4">
    <div class="col-span-12 lg:col-span-9 bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <!-- 이미지 -->
      <div v-if="item.images?.length" class="flex overflow-x-auto gap-1 bg-gray-100">
        <img v-for="(img,i) in item.images" :key="i" :src="'/storage/'+img" class="h-64 object-cover" @error="e=>e.target.style.display='none'" />
      </div>
      <div v-else class="h-48 bg-gray-100 flex items-center justify-center text-5xl">📦</div>

      <div class="px-5 py-4">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs px-2 py-0.5 rounded-full font-bold"
            :class="{'bg-green-100 text-green-700':item.status==='active','bg-amber-100 text-amber-700':item.status==='reserved','bg-gray-200 text-gray-500':item.status==='sold'}">
            {{ {active:'판매중',reserved:'예약중',sold:'판매완료'}[item.status] }}
          </span>
          <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600">{{ item.condition }}</span>
          <span v-if="item.is_negotiable" class="text-xs text-amber-600">가격협의 가능</span>
        </div>
        <h1 class="text-lg font-bold text-gray-900">{{ item.title }}</h1>
        <div class="text-2xl font-black text-amber-600 mt-2">${{ Number(item.price).toLocaleString() }}</div>
        <div class="text-xs text-gray-400 mt-1">{{ item.city }}, {{ item.state }} · {{ item.view_count }}조회</div>
      </div>
      <div class="px-5 py-4 border-t text-sm text-gray-700 whitespace-pre-wrap">{{ item.content }}</div>
      <div class="px-5 py-3 border-t space-y-3">
        <!-- 홀드 상태 표시 -->
        <div v-if="item.active_hold" class="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
          <div class="flex items-center gap-2">
            <span class="text-amber-600 font-bold text-sm">🔒 홀드 중</span>
            <span class="text-xs text-gray-500">{{ item.active_hold.buyer?.nickname || item.active_hold.buyer?.name }}님이 예약</span>
          </div>
          <div class="text-xs text-amber-700 mt-1">만료: {{ formatHoldTime(item.active_hold.hold_until) }}</div>
        </div>

        <!-- 부스트 상태 표시 -->
        <div v-if="item.boosted_until && new Date(item.boosted_until) > new Date()" class="flex items-center gap-2">
          <span class="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-bold">🚀 상위노출 중</span>
          <span class="text-xs text-gray-400">{{ formatHoldTime(item.boosted_until) }}까지</span>
        </div>

        <div class="flex gap-2 flex-wrap">
          <!-- 홀드 버튼 (구매자용) -->
          <button v-if="item.hold_enabled && item.status==='active' && auth.isLoggedIn && item.user_id !== auth.user?.id && !item.active_hold"
            @click="showHoldModal = true"
            class="bg-blue-500 text-white font-bold px-5 py-2 rounded-lg text-sm hover:bg-blue-600">🔒 홀드 ({{ item.hold_price_per_6h }}P/6h)</button>

          <!-- 홀드 취소 (구매자/판매자) -->
          <button v-if="item.active_hold && (item.active_hold.buyer_id === auth.user?.id || item.user_id === auth.user?.id)"
            @click="cancelHold"
            class="bg-red-100 text-red-700 font-bold px-5 py-2 rounded-lg text-sm hover:bg-red-200">홀드 취소</button>

          <!-- 부스트 버튼 (판매자용) -->
          <button v-if="item.user_id === auth.user?.id && item.status === 'active'"
            @click="showBoostModal = true"
            class="bg-purple-500 text-white font-bold px-5 py-2 rounded-lg text-sm hover:bg-purple-600">🚀 상위노출</button>

          <RouterLink v-if="auth.isLoggedIn" to="/chat" class="bg-gray-100 text-gray-700 font-semibold px-5 py-2 rounded-lg text-sm hover:bg-gray-200">💬 채팅하기</RouterLink>
        </div>
      </div>

      <!-- 홀드 모달 -->
      <div v-if="showHoldModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showHoldModal=false">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm">
          <h3 class="font-bold text-lg mb-3">🔒 홀드 신청</h3>
          <p class="text-sm text-gray-600 mb-3">{{ item.title }}</p>
          <div class="text-xs text-gray-400 mb-3">6시간당 <b class="text-amber-600">{{ item.hold_price_per_6h }}P</b> · 최대 {{ item.hold_max_hours }}시간</div>

          <div class="grid grid-cols-3 gap-2 mb-3">
            <button v-for="h in holdOptions" :key="h" @click="holdHours = h"
              :class="holdHours === h ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'"
              class="py-2 rounded-lg text-sm font-bold">
              {{ h >= 24 ? (h/24) + '일' : h + '시간' }}
            </button>
          </div>

          <div class="bg-blue-50 rounded-lg p-3 mb-4 text-center">
            <div class="text-xs text-gray-500">차감 포인트</div>
            <div class="text-2xl font-black text-blue-600">{{ holdCost }}P</div>
            <div class="text-[10px] text-gray-400">판매자 {{ Math.floor(holdCost * 0.9) }}P · 수수료 {{ Math.ceil(holdCost * 0.1) }}P</div>
          </div>

          <div class="flex gap-2">
            <button @click="showHoldModal=false" class="flex-1 py-2 bg-gray-100 rounded-lg text-sm font-semibold">취소</button>
            <button @click="submitHold" :disabled="holdingInProgress" class="flex-1 py-2 bg-blue-500 text-white rounded-lg text-sm font-bold hover:bg-blue-600 disabled:opacity-50">홀드 신청</button>
          </div>
        </div>
      </div>

      <!-- 부스트 모달 -->
      <div v-if="showBoostModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showBoostModal=false">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm">
          <h3 class="font-bold text-lg mb-3">🚀 상위노출</h3>
          <p class="text-sm text-gray-600 mb-3">리스트 맨 위에 노출됩니다</p>

          <div class="grid grid-cols-3 gap-2 mb-3">
            <button @click="boostDays=1" :class="boostDays===1?'bg-purple-500 text-white':'bg-gray-100'" class="py-3 rounded-lg text-sm font-bold">1일<br><span class="text-xs">100P</span></button>
            <button @click="boostDays=3" :class="boostDays===3?'bg-purple-500 text-white':'bg-gray-100'" class="py-3 rounded-lg text-sm font-bold">3일<br><span class="text-xs">300P</span></button>
            <button @click="boostDays=7" :class="boostDays===7?'bg-purple-500 text-white':'bg-gray-100'" class="py-3 rounded-lg text-sm font-bold">7일<br><span class="text-xs">700P</span></button>
          </div>

          <div class="bg-purple-50 rounded-lg p-3 mb-4 text-center">
            <div class="text-2xl font-black text-purple-600">{{ boostDays * 100 }}P</div>
          </div>

          <div class="flex gap-2">
            <button @click="showBoostModal=false" class="flex-1 py-2 bg-gray-100 rounded-lg text-sm font-semibold">취소</button>
            <button @click="submitBoost" :disabled="boostingInProgress" class="flex-1 py-2 bg-purple-500 text-white rounded-lg text-sm font-bold hover:bg-purple-600 disabled:opacity-50">결제하기</button>
          </div>
        </div>
      </div>

      <!-- 댓글 -->
      <CommentSection v-if="item.id" :type="'market'" :typeId="item.id" class="mt-4" />
    </div>

    <!-- 사이드바 -->
    <div class="col-span-12 lg:col-span-3 hidden lg:block">
      <SidebarWidgets
        api-url="/api/market"
        detail-path="/market/"
        :current-id="item.id"
        label="물품"
        recommend-label="추천 물품"
        quick-label="방금 올라온"
        :links="[
          { to: '/market', icon: '📋', label: '전체 장터' },
          { to: '/market/write', icon: '✏️', label: '물품 등록' },
          { to: '/jobs', icon: '💼', label: '구인구직' },
        ]"
      />
    </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useSiteStore } from '../../stores/site'
import SidebarWidgets from '../../components/SidebarWidgets.vue'
import CommentSection from '../../components/CommentSection.vue'
import axios from 'axios'
const route = useRoute()
const auth = useAuthStore()
const siteStore = useSiteStore()
const item = ref(null)
const relatedItems = ref([])
const loading = ref(true)

// 홀드
const showHoldModal = ref(false)
const holdHours = ref(6)
const holdingInProgress = ref(false)
const holdOptions = computed(() => {
  if (!item.value) return [6]
  const max = item.value.hold_max_hours || 24
  return [6, 12, 24, 48, 72, 168].filter(h => h <= max)
})
const holdCost = computed(() => {
  if (!item.value) return 0
  return Math.ceil(holdHours.value / 6) * (item.value.hold_price_per_6h || 0)
})

async function submitHold() {
  if (!confirm(`${holdHours.value}시간 홀드에 ${holdCost.value}P가 차감됩니다. 계속하시겠습니까?`)) return
  holdingInProgress.value = true
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/hold`, { hours: holdHours.value })
    siteStore.toast(data.message, 'success')
    showHoldModal.value = false
    loadItem()
  } catch (e) { siteStore.toast(e.response?.data?.message || '홀드 실패', 'error') }
  holdingInProgress.value = false
}

async function cancelHold() {
  if (!confirm('홀드를 취소하시겠습니까? 포인트는 환불되지 않습니다.')) return
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/hold/cancel`)
    siteStore.toast(data.message, 'success')
    loadItem()
  } catch (e) { siteStore.toast(e.response?.data?.message || '취소 실패', 'error') }
}

// 부스트
const showBoostModal = ref(false)
const boostDays = ref(1)
const boostingInProgress = ref(false)

async function submitBoost() {
  const cost = boostDays.value * 100
  if (!confirm(`${boostDays.value}일 상위노출에 ${cost}P가 차감됩니다.`)) return
  boostingInProgress.value = true
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/boost`, { days: boostDays.value })
    siteStore.toast(data.message, 'success')
    showBoostModal.value = false
    loadItem()
  } catch (e) { siteStore.toast(e.response?.data?.message || '부스트 실패', 'error') }
  boostingInProgress.value = false
}

function formatHoldTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleDateString('ko-KR') + ' ' + d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

async function reserve() {
  if (!confirm('100 포인트를 에스크로하여 찜하시겠습니까?')) return
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/reserve`, { points: 100 })
    siteStore.toast(data.message, 'success')
    item.value.status = 'reserved'
  } catch (e) { siteStore.toast(e.response?.data?.message || '예약 실패', 'error') }
}
async function loadItem() {
  try {
    const { data } = await axios.get(`/api/market/${route.params.id}`)
    item.value = data.data
  } catch {}
}

onMounted(async () => {
  await loadItem()
  // 관련 물품
  if (item.value) {
    try {
      const { data: rData } = await axios.get(`/api/market?category=${item.value.category}&per_page=5`)
      relatedItems.value = (rData.data?.data || []).filter(r => r.id !== item.value.id).slice(0, 5)
    } catch {}
  }
  loading.value = false
})
</script>
