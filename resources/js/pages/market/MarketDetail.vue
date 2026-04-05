<template>
  <DetailTemplate
    :item="item"
    :loading="loading"
    :breadcrumb="breadcrumb"
    :images="itemImages"
    :showAuthor="false"
    :showActions="true"
    :showComments="true"
    commentType="market"
    @like="toggleLike"
    @bookmark="toggleBookmark"
  >
    <template #header>
      <div v-if="item" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <!-- Status badges -->
        <div class="flex items-center gap-2 mb-3">
          <span v-if="item.category" class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-1 rounded">{{ item.category }}</span>
          <span v-if="item.condition" class="text-xs bg-blue-50 dark:bg-blue-900/30 text-blue-600 px-2 py-1 rounded">{{ item.condition }}</span>
          <span v-if="item.status === 'sold'" class="text-xs bg-gray-600 text-white px-2 py-1 rounded font-medium">{{ locale === 'ko' ? '판매완료' : 'Sold' }}</span>
          <span v-else-if="item.status === 'reserved'" class="text-xs bg-yellow-500 text-white px-2 py-1 rounded font-medium">{{ locale === 'ko' ? '예약중' : 'Reserved' }}</span>
          <div v-if="canEdit" class="ml-auto flex gap-2">
            <router-link :to="`/market/write?edit=${item.id}`" class="text-xs text-gray-400 hover:text-gray-600">{{ locale === 'ko' ? '수정' : 'Edit' }}</router-link>
            <button @click="deleteItem" class="text-xs text-red-400 hover:text-red-600">{{ locale === 'ko' ? '삭제' : 'Delete' }}</button>
          </div>
        </div>

        <!-- Price -->
        <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mb-2">
          {{ Number(item.price) === 0 ? (locale === 'ko' ? '무료 나눔' : 'Free') : `$${Number(item.price).toLocaleString()}` }}
          <span v-if="item.price_negotiable" class="text-sm text-gray-400 font-normal ml-2">{{ locale === 'ko' ? '가격 협의 가능' : 'Negotiable' }}</span>
        </p>

        <h1 class="text-lg font-bold text-gray-900 dark:text-white mb-2">{{ item.title }}</h1>

        <div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
          <span>{{ locale === 'ko' ? '조회' : 'Views' }} {{ item.view_count || 0 }}</span>
          <span>{{ locale === 'ko' ? '관심' : 'Likes' }} {{ item.like_count || 0 }}</span>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
      </div>
    </template>

    <template #body>
      <!-- Description -->
      <div class="prose prose-sm max-w-none text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed mb-6">
        {{ item?.description || item?.content }}
      </div>

      <!-- Seller Info -->
      <div v-if="item?.user" class="border-t border-gray-100 dark:border-gray-700 pt-4 mb-4">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-3">{{ locale === 'ko' ? '판매자 정보' : 'Seller Info' }}</h3>
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-blue-100 dark:bg-blue-800 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-300 font-bold text-lg flex-shrink-0">
            {{ item.user.name?.[0] || '?' }}
          </div>
          <div>
            <p class="font-semibold text-gray-900 dark:text-white">{{ item.user.name }}</p>
            <div class="flex items-center gap-3 mt-0.5 text-xs text-gray-500">
              <span>📍 {{ item.region || (locale === 'ko' ? '지역 미상' : 'Unknown') }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Reserve Section -->
      <div v-if="item?.reservation_points > 0 && !canEdit && !item.reservation && item.status !== 'sold'" class="border-t border-gray-100 dark:border-gray-700 pt-4">
        <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700 rounded-xl p-4">
          <div class="flex items-center gap-3 mb-3">
            <span class="text-sm font-medium text-green-700 dark:text-green-300">{{ locale === 'ko' ? '찜 가능' : 'Available' }}</span>
            <span class="text-sm text-gray-600 dark:text-gray-400">{{ locale === 'ko' ? '보증금' : 'Deposit' }}: <strong class="text-orange-600">{{ item.reservation_points }}P</strong></span>
          </div>
          <button v-if="auth.isLoggedIn" @click="showReserveModal = true"
            class="w-full py-2.5 bg-green-600 text-white rounded-lg font-medium text-sm hover:bg-green-700 transition">
            {{ locale === 'ko' ? '찜하기' : 'Reserve' }}
          </button>
          <p v-else class="text-xs text-gray-400 text-center">
            <router-link to="/auth/login" class="text-blue-600 hover:underline">{{ locale === 'ko' ? '로그인' : 'Login' }}</router-link>
            {{ locale === 'ko' ? ' 후 찜할 수 있습니다' : ' to reserve' }}
          </p>
        </div>
      </div>

      <!-- Chat Button -->
      <div v-if="auth.isLoggedIn && !canEdit && item?.status !== 'sold'" class="mt-4">
        <button @click="sendMessage"
          class="w-full py-3 bg-blue-600 text-white rounded-xl font-medium text-sm hover:bg-blue-700 transition flex items-center justify-center gap-2">
          💬 {{ locale === 'ko' ? '연락하기' : 'Contact Seller' }}
        </button>
      </div>

      <!-- Map -->
      <div v-if="item?.latitude && item?.longitude" class="mt-6 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-600">
        <iframe :src="`https://maps.google.com/maps?q=${item.latitude},${item.longitude}&output=embed`"
          class="w-full h-[250px] border-0" allowfullscreen loading="lazy" />
        <div v-if="item.address" class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-700">{{ item.address }}</div>
      </div>
    </template>

    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 overflow-hidden">
        <h3 class="font-bold text-gray-800 dark:text-white text-sm px-4 py-3 border-b border-gray-100 dark:border-gray-700">
          {{ item?.category || '' }} {{ locale === 'ko' ? '관련 매물' : 'Related' }}
        </h3>
        <div v-if="sidebarItems.length">
          <router-link v-for="si in sidebarItems" :key="si.id" :to="`/market/${si.id}`"
            class="flex gap-3 py-3 px-3 hover:bg-blue-50/40 dark:hover:bg-gray-700/50 transition border-b border-gray-50 dark:border-gray-700 last:border-0">
            <div class="flex-shrink-0 w-14 h-14 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700">
              <img v-if="si.images?.[0]" :src="si.images[0]" class="w-full h-full object-cover" @error="e => e.target.src=''" />
              <div v-else class="w-full h-full flex items-center justify-center text-xl">📦</div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-800 dark:text-gray-200 line-clamp-2 leading-snug">{{ si.title }}</p>
              <p class="text-xs text-blue-600 font-bold mt-0.5">
                {{ Number(si.price) === 0 ? (locale === 'ko' ? '무료' : 'Free') : `$${Number(si.price).toLocaleString()}` }}
              </p>
            </div>
          </router-link>
        </div>
        <div v-else class="text-center py-10 text-gray-400 text-sm">{{ locale === 'ko' ? '관련 매물이 없습니다' : 'No related items' }}</div>
      </div>
    </template>
  </DetailTemplate>

  <!-- Reserve Modal -->
  <div v-if="showReserveModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showReserveModal = false">
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-sm w-full shadow-xl">
      <h3 class="text-lg font-bold text-gray-800 dark:text-white mb-4">{{ locale === 'ko' ? '찜하기' : 'Reserve Item' }}</h3>
      <div class="space-y-3 text-sm text-gray-700 dark:text-gray-300">
        <p><strong>{{ item?.title }}</strong></p>
        <div v-if="item?.reservation_points > 0" class="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700 rounded-lg p-3">
          <p class="font-medium text-orange-800 dark:text-orange-300">{{ locale === 'ko' ? '보증금' : 'Deposit' }}: {{ item.reservation_points }}P</p>
          <p class="text-xs text-orange-600 dark:text-orange-400 mt-1">{{ locale === 'ko' ? '찜 취소 시 보증금의 50%가 판매자에게 지급됩니다' : '50% deposit goes to seller on cancellation' }}</p>
        </div>
      </div>
      <div class="flex gap-2 mt-5">
        <button @click="showReserveModal = false" class="flex-1 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium text-sm hover:bg-gray-200 transition">
          {{ locale === 'ko' ? '취소' : 'Cancel' }}
        </button>
        <button @click="doReserve" :disabled="reserving" class="flex-1 py-2.5 bg-green-600 text-white rounded-lg font-medium text-sm hover:bg-green-700 disabled:opacity-50 transition">
          {{ reserving ? (locale === 'ko' ? '처리중...' : 'Processing...') : (locale === 'ko' ? '찜하기' : 'Reserve') }}
        </button>
      </div>
    </div>
  </div>
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

const item = ref(null)
const loading = ref(true)
const sidebarItems = ref([])
const showReserveModal = ref(false)
const reserving = ref(false)

const canEdit = computed(() => auth.user && (auth.user.id === item.value?.user_id || auth.user.is_admin))
const breadcrumb = computed(() => [
  { label: locale.value === 'ko' ? '중고장터' : 'Marketplace', to: '/market' },
  { label: item.value?.title || '' }
])
const itemImages = computed(() => item.value?.images?.length ? item.value.images : null)

function formatDate(d) {
  if (!d) return ''
  const diff = (Date.now() - new Date(d).getTime()) / 1000
  if (diff < 3600) return `${Math.floor(diff / 60)}${locale.value === 'ko' ? '분 전' : 'm ago'}`
  if (diff < 86400) return `${Math.floor(diff / 3600)}${locale.value === 'ko' ? '시간 전' : 'h ago'}`
  return new Date(d).toLocaleDateString('ko-KR')
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/like`)
    item.value.is_liked = data.liked
    item.value.like_count = data.like_count
  } catch { /* empty */ }
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/bookmark`)
    item.value.is_bookmarked = data.bookmarked
  } catch { /* empty */ }
}

function sendMessage() {
  router.push(`/messages?to=${item.value.user_id}&item=${item.value.id}`)
}

async function deleteItem() {
  if (!confirm(locale.value === 'ko' ? '삭제하시겠습니까?' : 'Delete this item?')) return
  try {
    await axios.delete(`/api/market/${item.value.id}`)
    router.push('/market')
  } catch { /* empty */ }
}

async function doReserve() {
  reserving.value = true
  try {
    await axios.post(`/api/market/${item.value.id}/reserve`)
    showReserveModal.value = false
    const { data } = await axios.get(`/api/market/${route.params.id}`)
    item.value = data
    alert(locale.value === 'ko' ? '찜이 완료되었습니다!' : 'Reserved successfully!')
  } catch (e) {
    alert(e.response?.data?.message || (locale.value === 'ko' ? '찜하기 실패' : 'Reserve failed'))
  } finally { reserving.value = false }
}

async function loadSidebarItems() {
  try {
    const { data } = await axios.get('/api/market', { params: { category: item.value.category, per_page: 5 } })
    sidebarItems.value = (data.data || data || []).filter(i => i.id !== item.value.id).slice(0, 5)
  } catch { /* empty */ }
}

watch(() => route.params.id, () => { if (route.params.id) loadItem() })

async function loadItem() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/market/${route.params.id}`)
    item.value = data
    loadSidebarItems()
  } catch { item.value = null }
  loading.value = false
}

onMounted(loadItem)
</script>
