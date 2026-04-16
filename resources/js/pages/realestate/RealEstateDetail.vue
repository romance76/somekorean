<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <!-- 헤더 -->
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-black text-gray-800">🏠 부동산</h1>
      <div class="flex items-center gap-2">
        <RouterLink to="/realestate" class="text-xs text-gray-500 hover:text-amber-600">← 목록</RouterLink>
        <RouterLink v-if="auth.isLoggedIn" to="/realestate/write" class="bg-amber-400 text-amber-900 font-bold px-3 py-1.5 rounded-lg text-xs">✏️ 등록</RouterLink>
      </div>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="listing" class="grid grid-cols-12 gap-4">

      <!-- 왼쪽: 카테고리 사이드바 -->
      <div class="col-span-12 lg:col-span-2 hidden lg:block">
        <div class="sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto space-y-3 pr-0.5">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div class="px-3 py-2.5 border-b font-bold text-xs text-amber-900">📋 부동산</div>
            <RouterLink to="/realestate" class="block w-full text-left px-3 py-2 text-xs text-gray-600 hover:bg-amber-50/50">← 전체 목록</RouterLink>
          </div>
          <AdSlot page="realestate" position="left" :maxSlots="2" />
        </div>
      </div>

      <!-- 중앙: 상세 내용 -->
      <div class="col-span-12 lg:col-span-7 space-y-4">
        <!-- 사진 갤러리 -->
        <div v-if="listing.images && listing.images.length" class="bg-white rounded-xl shadow-sm border overflow-hidden">
          <div class="flex gap-1 overflow-x-auto p-2" style="-webkit-overflow-scrolling: touch;">
            <div v-for="(p, idx) in listing.images" :key="idx"
              class="flex-shrink-0 rounded-lg overflow-hidden cursor-pointer hover:opacity-90 transition relative bg-gray-100"
              style="min-width: 150px; height: 200px;"
              @click="openLightbox(idx)">
              <img :src="photoUrl(p)" style="height: 200px; width: auto; object-fit: cover;" />
            </div>
          </div>
          <div class="px-3 pb-2 text-[10px] text-gray-400">📷 {{ listing.images.length }}장 · 클릭하면 크게 보기</div>
        </div>

        <!-- 가격 + 기본정보 -->
        <div class="bg-white rounded-xl shadow-sm border p-4">
          <div class="flex items-center gap-2 mb-1 flex-wrap">
            <span class="text-[10px] px-1.5 py-0.5 rounded-full font-bold" :class="listing.type==='sale'?'bg-red-100 text-red-700':'bg-blue-100 text-blue-700'">
              {{ listing.type==='sale' ? '매매' : '렌트' }}
            </span>
            <span class="text-[10px] bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded-full font-bold">{{ listing.property_type }}</span>
          </div>
          <div class="text-2xl font-black text-gray-900">${{ Number(listing.price).toLocaleString() }}<span v-if="listing.type==='rent'" class="text-sm font-bold text-gray-500">/월</span></div>
          <h1 class="text-base font-bold text-gray-800 mt-1">{{ listing.title }}</h1>
          <div class="text-xs text-gray-500 mt-1">📍 {{ listing.address ? listing.address + ', ' : '' }}{{ listing.city }}, {{ listing.state }} {{ listing.zipcode }}</div>

          <div class="flex items-center gap-4 mt-3 pt-3 border-t text-center">
            <div v-if="listing.bedrooms"><div class="text-lg font-black text-gray-800">{{ listing.bedrooms }}</div><div class="text-[10px] text-gray-500">beds</div></div>
            <div v-if="listing.bathrooms"><div class="text-lg font-black text-gray-800">{{ listing.bathrooms }}</div><div class="text-[10px] text-gray-500">baths</div></div>
            <div v-if="listing.sqft"><div class="text-lg font-black text-gray-800">{{ Number(listing.sqft).toLocaleString() }}</div><div class="text-[10px] text-gray-500">sqft</div></div>
            <div><div class="text-lg font-black text-gray-800">{{ listing.view_count || 0 }}</div><div class="text-[10px] text-gray-500">조회</div></div>
          </div>
        </div>

        <!-- 설명 -->
        <div class="bg-white rounded-xl shadow-sm border p-4">
          <h2 class="font-bold text-sm text-gray-800 mb-2">📝 상세 설명</h2>
          <div class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">{{ listing.content }}</div>
        </div>

        <!-- 연락처 -->
        <div class="bg-white rounded-xl shadow-sm border p-4 bg-amber-50">
          <h2 class="font-bold text-sm text-amber-900 mb-2">📞 연락처</h2>
          <div class="flex items-center gap-4 flex-wrap text-sm">
            <a v-if="listing.contact_phone" :href="'tel:'+listing.contact_phone" class="text-blue-600 hover:underline font-bold">📱 {{ listing.contact_phone }}</a>
            <a v-if="listing.contact_email" :href="'mailto:'+listing.contact_email" class="text-blue-600 hover:underline">📧 {{ listing.contact_email }}</a>
          </div>
          <div v-if="listing.user" class="mt-2 pt-2 border-t border-amber-200 flex items-center gap-2 text-xs text-gray-600">
            <UserName :userId="listing.user.id" :name="listing.user.name || listing.user.nickname" />
            <span>· {{ fmtDate(listing.created_at) }}</span>
          </div>
        </div>

        <!-- 지도 -->
        <div v-if="listing.lat && listing.lng" class="bg-white rounded-xl shadow-sm border overflow-hidden">
          <h2 class="font-bold text-sm text-gray-800 px-4 pt-3 mb-1">📍 위치</h2>
          <iframe :src="`https://www.google.com/maps?q=${listing.lat},${listing.lng}&z=15&output=embed`"
            class="w-full h-[250px] border-0" loading="lazy"></iframe>
        </div>

        <!-- 주변 학교 -->
        <div v-if="listing.zipcode" class="bg-white rounded-xl shadow-sm border p-4">
          <h2 class="font-bold text-sm text-gray-800 mb-2">🏫 주변 학교</h2>
          <a :href="`https://www.greatschools.org/search/search.page?q=${listing.zipcode}&distance=5`"
            target="_blank" rel="noopener"
            class="inline-flex items-center gap-1 bg-green-500 text-white font-bold px-3 py-1.5 rounded-lg hover:bg-green-600 text-xs">
            🏫 주변 학교 보기 ({{ listing.zipcode }})
          </a>
        </div>

        <!-- 수정/삭제 -->
        <div v-if="isOwner" class="flex items-center gap-3 justify-end">
          <RouterLink :to="`/realestate/write?edit=${listing.id}`" class="text-sm text-amber-600 hover:text-amber-800">✏️ 수정</RouterLink>
          <button @click="deleteListing" class="text-sm text-red-400 hover:text-red-600">🗑 삭제</button>
        </div>

        <!-- 댓글 -->
        <CommentSection v-if="listing.id" type="realestate" :typeId="listing.id" />
      </div>

      <!-- 오른쪽: 위젯 -->
      <div class="col-span-12 lg:col-span-3 hidden lg:block">
        <SidebarWidgets api-url="/api/realestate" detail-path="/realestate/" :current-id="listing.id"
          label="매물"
          :filter-params="listing.lat && listing.lng ? { lat: listing.lat, lng: listing.lng, radius: 50 } : {}" />
        <AdSlot page="realestate" position="right" :maxSlots="2" class="mt-3" />
      </div>
    </div>
  </div>

  <!-- 라이트박스 -->
  <div v-if="lightboxIdx !== null" class="fixed inset-0 bg-black/90 z-50 flex items-center justify-center" @click.self="lightboxIdx=null">
    <button class="absolute top-4 right-4 text-white text-3xl hover:text-gray-300" @click="lightboxIdx=null">✕</button>
    <button class="absolute left-4 top-1/2 -translate-y-1/2 text-white text-3xl hover:text-gray-300" @click="prevPhoto">‹</button>
    <button class="absolute right-4 top-1/2 -translate-y-1/2 text-white text-3xl hover:text-gray-300" @click="nextPhoto">›</button>
    <img v-if="listing?.images?.[lightboxIdx]" :src="photoUrl(listing.images[lightboxIdx])" style="max-width:90vw;max-height:85vh;object-fit:contain;border-radius:8px;" />
    <div class="absolute bottom-4 text-white text-sm">{{ lightboxIdx + 1 }} / {{ listing?.images?.length || 0 }}</div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import SidebarWidgets from '../../components/SidebarWidgets.vue'
import CommentSection from '../../components/CommentSection.vue'
import AdSlot from '../../components/AdSlot.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const listing = ref(null)
const loading = ref(true)
const lightboxIdx = ref(null)

const isOwner = computed(() => auth.user?.id === listing.value?.user_id || auth.user?.is_admin)

function photoUrl(path) {
  if (!path) return ''
  return String(path).startsWith('http') || String(path).startsWith('/storage/') ? path : '/storage/' + path
}

function openLightbox(idx) { lightboxIdx.value = idx }
function prevPhoto() { if (lightboxIdx.value > 0) lightboxIdx.value-- }
function nextPhoto() { if (lightboxIdx.value < (listing.value?.images?.length || 1) - 1) lightboxIdx.value++ }

function fmtDate(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()}`
}

async function deleteListing() {
  if (!confirm('정말 삭제하시겠습니까?')) return
  try { await axios.delete(`/api/realestate/${listing.value.id}`); router.push('/realestate') } catch {}
}

onMounted(async () => {
  try { const { data } = await axios.get(`/api/realestate/${route.params.id}`); listing.value = data.data } catch {}
  loading.value = false
})
</script>
