<template>
  <div class="p-6 space-y-6">
    <!-- Page Title -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">부동산 관리</h1>
        <p class="text-sm text-gray-500 mt-0.5">매물 등록 및 현황을 관리합니다</p>
      </div>
      <button @click="showCreateModal = true"
        class="flex items-center gap-2 bg-blue-600 text-white px-4 py-2.5 rounded-xl text-sm font-medium hover:bg-blue-700 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        매물 등록
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500 mb-1">전체 매물</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.total }}</p>
        <p class="text-xs text-gray-400 mt-1">등록된 매물 전체</p>
      </div>
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500 mb-1">판매/임대중</p>
        <p class="text-2xl font-bold text-green-600">{{ stats.active }}</p>
        <p class="text-xs text-gray-400 mt-1">현재 활성 매물</p>
      </div>
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500 mb-1">이번달 신규</p>
        <p class="text-2xl font-bold text-blue-600">{{ stats.newThisMonth }}</p>
        <p class="text-xs text-gray-400 mt-1">3월 신규 등록</p>
      </div>
      <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-500 mb-1">중개사 수</p>
        <p class="text-2xl font-bold text-purple-600">{{ stats.agents }}</p>
        <p class="text-xs text-gray-400 mt-1">등록 중개인</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
      <div class="flex flex-wrap gap-3 items-center">
        <!-- Category filter -->
        <select v-model="filter.type"
          class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50">
          <option value="">전체 카테고리</option>
          <option value="매매">매매</option>
          <option value="전세">전세</option>
          <option value="월세">월세</option>
          <option value="상가">상가</option>
          <option value="토지">토지</option>
        </select>

        <!-- Price range filter -->
        <select v-model="filter.priceRange"
          class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50">
          <option value="">전체 가격대</option>
          <option value="low">~$300K / ~$2,000/월</option>
          <option value="mid">$300K~$600K / $2,000~$3,000/월</option>
          <option value="high">$600K+ / $3,000+/월</option>
        </select>

        <!-- Region filter -->
        <select v-model="filter.region"
          class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50">
          <option value="">전체 지역</option>
          <option value="LA">Los Angeles</option>
          <option value="Gardena">Gardena</option>
          <option value="Irvine">Irvine</option>
          <option value="Torrance">Torrance</option>
        </select>

        <!-- Status filter -->
        <select v-model="filter.status"
          class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50">
          <option value="">전체 상태</option>
          <option value="active">활성</option>
          <option value="pending">검토중</option>
          <option value="closed">거래완료</option>
        </select>

        <!-- Search -->
        <div class="flex-1 min-w-[200px]">
          <input v-model="filter.search" type="text" placeholder="주소 또는 제목 검색..."
            class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50" />
        </div>

        <button @click="resetFilters"
          class="text-sm text-gray-500 hover:text-gray-700 px-3 py-2 rounded-xl hover:bg-gray-100 transition">
          초기화
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b border-gray-100">
              <th class="text-left px-5 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">매물 정보</th>
              <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">타입</th>
              <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">가격</th>
              <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">면적/방수</th>
              <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">중개인</th>
              <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">상태</th>
              <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">조회</th>
              <th class="text-left px-4 py-3.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="listing in filteredListings" :key="listing.id"
              class="hover:bg-gray-50 transition">
              <td class="px-5 py-4">
                <p class="font-medium text-gray-900 line-clamp-1">{{ listing.title }}</p>
                <p class="text-xs text-gray-400 mt-0.5">{{ listing.address }}</p>
                <p class="text-xs text-gray-300 mt-0.5">등록 {{ listing.created_at }}</p>
              </td>
              <td class="px-4 py-4">
                <span class="px-2.5 py-1 rounded-lg text-xs font-medium"
                  :class="typeColors[listing.type] || 'bg-gray-100 text-gray-600'">
                  {{ listing.type }}
                </span>
              </td>
              <td class="px-4 py-4 font-semibold text-gray-900 whitespace-nowrap">{{ listing.price }}</td>
              <td class="px-4 py-4 text-gray-600">
                <p>{{ listing.size }}</p>
                <p class="text-xs text-gray-400">{{ listing.rooms > 0 ? listing.rooms + '베드룸' : '상업용' }}</p>
              </td>
              <td class="px-4 py-4 text-gray-600">{{ listing.agent }}</td>
              <td class="px-4 py-4">
                <span class="px-2.5 py-1 rounded-full text-xs font-medium"
                  :class="statusColors[listing.status] || 'bg-gray-100 text-gray-500'">
                  {{ statusLabels[listing.status] || listing.status }}
                </span>
              </td>
              <td class="px-4 py-4 text-gray-500">{{ listing.views.toLocaleString() }}</td>
              <td class="px-4 py-4">
                <div class="flex items-center gap-1.5">
                  <button @click="openDetail(listing)"
                    class="px-3 py-1.5 text-xs bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition font-medium">
                    상세
                  </button>
                  <button @click="toggleStatus(listing)"
                    class="px-3 py-1.5 text-xs bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition font-medium">
                    {{ listing.status === 'active' ? '비활성' : '활성화' }}
                  </button>
                  <button @click="deleteListing(listing.id)"
                    class="px-3 py-1.5 text-xs bg-red-50 text-red-500 rounded-lg hover:bg-red-100 transition font-medium">
                    삭제
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredListings.length === 0">
              <td colspan="8" class="text-center py-12 text-gray-400">조건에 맞는 매물이 없습니다.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table footer -->
      <div class="px-5 py-3 border-t border-gray-100 flex items-center justify-between">
        <span class="text-xs text-gray-400">총 {{ filteredListings.length }}건</span>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedListing" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="selectedListing = null">
      <div class="bg-white rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 class="font-bold text-gray-900 text-lg">매물 상세 정보</h2>
          <button @click="selectedListing = null" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-5">
          <!-- Photo placeholder -->
          <div class="w-full h-48 bg-gradient-to-br from-blue-100 to-blue-50 rounded-xl flex items-center justify-center">
            <div class="text-center text-blue-400">
              <svg class="w-12 h-12 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
                <polyline stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" points="9,22 9,12 15,12 15,22" />
              </svg>
              <p class="text-sm">매물 사진</p>
            </div>
          </div>

          <!-- Info grid -->
          <div class="grid grid-cols-2 gap-4">
            <div class="col-span-2">
              <label class="text-xs text-gray-400 block mb-1">매물명</label>
              <p class="font-semibold text-gray-900">{{ selectedListing.title }}</p>
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">타입</label>
              <span class="px-2.5 py-1 rounded-lg text-xs font-medium"
                :class="typeColors[selectedListing.type] || 'bg-gray-100 text-gray-600'">
                {{ selectedListing.type }}
              </span>
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">상태</label>
              <span class="px-2.5 py-1 rounded-full text-xs font-medium"
                :class="statusColors[selectedListing.status] || 'bg-gray-100 text-gray-500'">
                {{ statusLabels[selectedListing.status] || selectedListing.status }}
              </span>
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">가격</label>
              <p class="font-bold text-gray-900">{{ selectedListing.price }}</p>
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">면적</label>
              <p class="text-gray-700">{{ selectedListing.size }}</p>
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">방수</label>
              <p class="text-gray-700">{{ selectedListing.rooms > 0 ? selectedListing.rooms + '베드룸' : '해당없음 (상업용)' }}</p>
            </div>
            <div>
              <label class="text-xs text-gray-400 block mb-1">조회수</label>
              <p class="text-gray-700">{{ selectedListing.views.toLocaleString() }}회</p>
            </div>
            <div class="col-span-2">
              <label class="text-xs text-gray-400 block mb-1">주소</label>
              <p class="text-gray-700">{{ selectedListing.address }}</p>
            </div>
          </div>

          <!-- Agent contact -->
          <div class="bg-blue-50 rounded-xl p-4">
            <p class="text-xs text-gray-500 mb-2 font-medium">중개인 연락처</p>
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-900">{{ selectedListing.agent }}</p>
                <p class="text-xs text-gray-500 mt-0.5">등록일: {{ selectedListing.created_at }}</p>
              </div>
              <div class="flex gap-2">
                <button class="px-3 py-1.5 bg-white text-blue-600 rounded-lg text-xs font-medium border border-blue-200 hover:bg-blue-100 transition">
                  전화
                </button>
                <button class="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-xs font-medium hover:bg-blue-700 transition">
                  메시지
                </button>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-2">
            <button @click="toggleStatus(selectedListing); selectedListing = null"
              class="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-50 transition">
              {{ selectedListing.status === 'active' ? '비활성 처리' : '활성화' }}
            </button>
            <button @click="deleteListing(selectedListing.id); selectedListing = null"
              class="flex-1 py-2.5 bg-red-50 text-red-500 rounded-xl text-sm font-medium hover:bg-red-100 transition">
              삭제
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showCreateModal = false">
      <div class="bg-white rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl">
        <div class="flex items-center justify-between p-6 border-b border-gray-100">
          <h2 class="font-bold text-gray-900 text-lg">매물 등록</h2>
          <button @click="showCreateModal = false" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitCreate" class="p-6 space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">매물명 *</label>
            <input v-model="createForm.title" type="text" required placeholder="예: 코리아타운 콘도 매매"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">타입 *</label>
              <select v-model="createForm.type" required
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-white">
                <option value="">선택</option>
                <option value="매매">매매</option>
                <option value="전세">전세</option>
                <option value="월세">월세</option>
                <option value="상가">상가</option>
                <option value="토지">토지</option>
              </select>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">가격 *</label>
              <input v-model="createForm.price" type="text" required placeholder="예: $450,000"
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">주소 *</label>
            <input v-model="createForm.address" type="text" required placeholder="예: 3200 Wilshire Blvd #505, LA"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">면적</label>
              <input v-model="createForm.size" type="text" placeholder="예: 850sqft"
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1.5">방수</label>
              <input v-model="createForm.rooms" type="number" min="0" placeholder="0"
                class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1.5">중개인/업체</label>
            <input v-model="createForm.agent" type="text" placeholder="예: 새롬 부동산"
              class="w-full border border-gray-200 rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>

          <div class="flex gap-3 pt-2">
            <button type="button" @click="showCreateModal = false"
              class="flex-1 py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm font-medium hover:bg-gray-50 transition">
              취소
            </button>
            <button type="submit"
              class="flex-1 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-medium hover:bg-blue-700 transition">
              등록하기
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import axios from 'axios'

const listings = ref([])
const loading = ref(false)
const filter = reactive({ type: '', status: '', search: '' })
const selectedListing = ref(null)

const typeColors = {
  '매매': 'bg-blue-100 text-blue-700',
  '전세': 'bg-purple-100 text-purple-700',
  '렌트': 'bg-green-100 text-green-700',
  '룸메이트': 'bg-teal-100 text-teal-700',
  '상가': 'bg-orange-100 text-orange-700',
}

const statusColors = {
  'active':  'bg-green-100 text-green-700',
  'closed':  'bg-gray-100 text-gray-500',
  'deleted': 'bg-red-100 text-red-500',
}

const statusLabels = {
  'active':  '활성',
  'closed':  '마감',
  'deleted': '삭제',
}

const stats = computed(() => ({
  total:       listings.value.length,
  active:      listings.value.filter(l => l.status === 'active').length,
  closed:      listings.value.filter(l => l.status === 'closed').length,
  newThisMonth: listings.value.filter(l => l.created_at?.startsWith('2026-03')).length,
}))

const filteredListings = computed(() => {
  return listings.value.filter(l => {
    if (filter.type   && l.type   !== filter.type)   return false
    if (filter.status && l.status !== filter.status) return false
    if (filter.search) {
      const q = filter.search.toLowerCase()
      if (!l.title?.toLowerCase().includes(q) && !l.address?.toLowerCase().includes(q)) return false
    }
    return true
  })
})

function resetFilters() {
  filter.type = ''
  filter.status = ''
  filter.search = ''
}

function openDetail(listing) {
  selectedListing.value = { ...listing }
}

async function toggleStatus(listing) {
  try {
    const { data } = await axios.patch(`/api/admin/realestate/${listing.id}/toggle`)
    const idx = listings.value.findIndex(l => l.id === listing.id)
    if (idx !== -1) listings.value[idx].status = data.status
    if (selectedListing.value?.id === listing.id) selectedListing.value.status = data.status
  } catch (e) {
    alert('상태 변경 실패')
  }
}

async function deleteListing(id) {
  if (!confirm('이 매물을 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/admin/realestate/${id}`)
    listings.value = listings.value.filter(l => l.id !== id)
    if (selectedListing.value?.id === id) selectedListing.value = null
  } catch (e) {
    alert('삭제 실패')
  }
}

async function loadListings() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/admin/realestate', {
      params: {
        search: filter.search || undefined,
        type:   filter.type || undefined,
        status: filter.status || undefined,
      }
    })
    listings.value = data.data || data
  } catch (e) {
    listings.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => loadListings())
</script>
