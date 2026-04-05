<template>
  <DetailTemplate
    :item="listing"
    :loading="loading"
    :images="listing?.photos || []"
    :showAuthor="true"
    :showActions="true"
    :showComments="true"
    commentType="realestate"
    :breadcrumb="[{ label: '부동산', to: '/realestate' }, { label: listing?.title || '' }]"
    @like="toggleLike"
    @bookmark="toggleBookmark"
  >
    <!-- Header slot -->
    <template #header>
      <!-- Price & Type header -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <div class="flex items-start justify-between mb-3">
          <div>
            <span class="text-xs font-bold px-2.5 py-1 rounded-full mr-2"
              :class="typeBadgeClass">{{ listing.type }}</span>
            <span v-if="listing.property_type" class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2.5 py-1 rounded-full">
              {{ listing.property_type }}
            </span>
          </div>
          <div v-if="canEdit" class="flex gap-2">
            <RouterLink :to="`/realestate/write?edit=${listing.id}`"
              class="text-xs text-blue-500 bg-blue-50 px-3 py-1.5 rounded-lg hover:bg-blue-100">수정</RouterLink>
            <button @click="deleteListing"
              class="text-xs text-red-500 bg-red-50 px-3 py-1.5 rounded-lg hover:bg-red-100">삭제</button>
          </div>
        </div>

        <h1 class="text-xl font-black text-gray-800 dark:text-white mb-2">{{ listing.title }}</h1>

        <p class="text-3xl font-black text-blue-600 dark:text-blue-400">
          {{ formatPrice(listing.price) }}
          <span v-if="isRent && listing.price" class="text-base font-medium text-gray-400">/월</span>
        </p>

        <p class="text-sm text-gray-500 dark:text-gray-400 mt-2 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          {{ listing.address }}
        </p>

        <!-- Property specs -->
        <div class="grid grid-cols-4 gap-3 bg-gray-50 dark:bg-gray-700 rounded-xl p-4 mt-4">
          <div v-if="listing.bedrooms != null" class="text-center">
            <p class="text-lg font-black text-gray-800 dark:text-white">{{ listing.bedrooms }}</p>
            <p class="text-xs text-gray-500">방</p>
          </div>
          <div v-if="listing.bathrooms != null" class="text-center">
            <p class="text-lg font-black text-gray-800 dark:text-white">{{ listing.bathrooms }}</p>
            <p class="text-xs text-gray-500">욕실</p>
          </div>
          <div v-if="listing.sqft" class="text-center">
            <p class="text-lg font-black text-gray-800 dark:text-white">{{ Number(listing.sqft).toLocaleString() }}</p>
            <p class="text-xs text-gray-500">sqft</p>
          </div>
          <div class="text-center">
            <p class="text-lg font-black text-gray-800 dark:text-white">{{ listing.type }}</p>
            <p class="text-xs text-gray-500">유형</p>
          </div>
        </div>

        <!-- Additional info -->
        <div v-if="listing.deposit || listing.move_in_date || listing.pet_policy"
          class="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4">
          <div v-if="listing.deposit" class="bg-blue-50 dark:bg-blue-900/30 rounded-xl p-3">
            <p class="text-xs text-gray-500">디파짓</p>
            <p class="font-bold text-gray-800 dark:text-white">${{ Number(listing.deposit).toLocaleString() }}</p>
          </div>
          <div v-if="listing.move_in_date" class="bg-green-50 dark:bg-green-900/30 rounded-xl p-3">
            <p class="text-xs text-gray-500">입주 가능일</p>
            <p class="font-bold text-gray-800 dark:text-white">{{ listing.move_in_date }}</p>
          </div>
          <div v-if="listing.pet_policy" class="bg-purple-50 dark:bg-purple-900/30 rounded-xl p-3">
            <p class="text-xs text-gray-500">반려동물</p>
            <p class="font-bold text-gray-800 dark:text-white">{{ listing.pet_policy }}</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Body: Description -->
    <template #body>
      <h2 class="font-bold text-gray-800 dark:text-white text-sm mb-2">상세 설명</h2>
      <p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">{{ listing.description || '설명이 없습니다.' }}</p>
    </template>

    <!-- After body: Contact + Map -->
    <template #after-body>
      <!-- Contact -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <h2 class="font-bold text-gray-800 dark:text-white text-sm mb-3">연락처</h2>
        <div class="flex flex-wrap gap-3">
          <a v-if="listing.phone" :href="`tel:${listing.phone}`"
            class="flex-1 min-w-[140px] bg-green-500 text-white text-center py-3 rounded-xl font-bold text-sm hover:bg-green-600 transition">
            📞 {{ listing.phone }}
          </a>
          <a v-if="listing.email" :href="`mailto:${listing.email}`"
            class="flex-1 min-w-[140px] bg-blue-500 text-white text-center py-3 rounded-xl font-bold text-sm hover:bg-blue-600 transition">
            ✉️ 이메일 보내기
          </a>
          <button v-if="auth.isLoggedIn && !canEdit" @click="sendMessage"
            class="flex-1 min-w-[140px] bg-indigo-500 text-white text-center py-3 rounded-xl font-bold text-sm hover:bg-indigo-600 transition">
            💬 쪽지 보내기
          </button>
        </div>
      </div>

      <!-- Map -->
      <div v-if="listing.address" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
        <div class="p-4 border-b border-gray-100 dark:border-gray-700 flex items-center justify-between">
          <h2 class="font-bold text-gray-800 dark:text-white text-sm">📍 위치</h2>
          <a :href="`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(listing.address)}`"
            target="_blank" rel="noopener"
            class="text-blue-600 text-xs font-bold hover:underline flex items-center gap-1">
            🚗 길찾기
          </a>
        </div>
        <div class="aspect-[16/7]">
          <iframe
            :src="`https://www.google.com/maps?q=${encodeURIComponent(listing.address)}&output=embed`"
            class="w-full h-full border-0"
            allowfullscreen loading="lazy"
            referrerpolicy="no-referrer-when-downgrade" />
        </div>
      </div>
    </template>

    <!-- Sidebar: Similar listings -->
    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4">
        <h3 class="font-bold text-gray-800 dark:text-white text-sm mb-3">같은 유형 매물</h3>
        <div v-if="similarListings.length === 0" class="text-center py-4 text-gray-400 text-sm">매물이 없습니다</div>
        <div v-else class="space-y-3">
          <RouterLink v-for="item in similarListings" :key="item.id" :to="`/realestate/${item.id}`"
            class="block p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition border border-gray-100 dark:border-gray-600">
            <div class="flex items-start gap-3">
              <div class="w-16 h-16 rounded-lg bg-gray-100 dark:bg-gray-700 flex-shrink-0 overflow-hidden flex items-center justify-center">
                <img v-if="item.photos?.length" :src="item.photos[0]" class="w-full h-full object-cover"
                  @error="e => e.target.parentElement.innerHTML = '<span class=\'text-2xl\'>🏠</span>'" />
                <span v-else class="text-2xl">🏠</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-bold text-gray-800 dark:text-white truncate">{{ item.title }}</p>
                <p class="text-xs text-blue-600 dark:text-blue-400 font-bold">{{ formatPrice(item.price) }}</p>
                <p class="text-xs text-gray-400 truncate">{{ item.address }}</p>
              </div>
            </div>
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

const listing = ref(null)
const loading = ref(true)
const similarListings = ref([])

const canEdit = computed(() =>
  auth.user && listing.value && (auth.user.id === listing.value.user_id || auth.user.is_admin)
)

const isRent = computed(() => {
  const t = listing.value?.type
  return t === '렌트' || t === '룸메이트'
})

const typeBadgeClass = computed(() => {
  const t = listing.value?.type
  if (t === '매매') return 'bg-red-500 text-white'
  if (t === '렌트') return 'bg-blue-500 text-white'
  if (t === '룸메이트') return 'bg-green-500 text-white'
  return 'bg-orange-500 text-white'
})

function formatPrice(price) {
  if (!price) return '가격문의'
  return '$' + Number(price).toLocaleString()
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/realestate/${listing.value.id}/like`)
    listing.value.is_liked = data.liked
    listing.value.like_count = data.like_count
  } catch {}
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/realestate/${listing.value.id}/bookmark`)
    listing.value.is_bookmarked = data.bookmarked
  } catch {}
}

function sendMessage() {
  router.push(`/messages?to=${listing.value.user_id || listing.value.user?.id}&listing=${listing.value.id}`)
}

async function deleteListing() {
  if (!confirm('이 매물을 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/realestate/${listing.value.id}`)
    router.push('/realestate')
  } catch {
    alert('삭제 실패')
  }
}

onMounted(async () => {
  const id = route.params.id
  try {
    const { data } = await axios.get(`/api/realestate/${id}`)
    listing.value = data
  } catch {
    listing.value = null
  }

  // Similar listings
  if (listing.value?.type) {
    try {
      const { data } = await axios.get('/api/realestate', { params: { type: listing.value.type, limit: 5 } })
      const list = data.data || data || []
      similarListings.value = list.filter(i => i.id !== listing.value.id).slice(0, 5)
    } catch {}
  }

  loading.value = false
})
</script>
