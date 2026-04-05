<template>
  <ListTemplate
    title="커뮤니티 동호회"
    emoji="👥"
    subtitle="관심사가 같은 한인들과 함께하세요"
    :loading="loading"
    :items="filteredClubs"
    :categories="typeTabs"
    :activeCategory="selectedFilter"
    :hasSearch="true"
    :searchQuery="search"
    searchPlaceholder="동호회 검색..."
    :hasViewToggle="false"
    :totalCount="filteredClubs.length"
    @category-change="onFilterChange"
    @search="onSearch"
  >
    <template #header-right>
      <button @click="showCreateModal = true"
        class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-blue-700 transition whitespace-nowrap">
        + 동호회 만들기
      </button>
    </template>

    <!-- Category sub-tabs -->
    <template #empty>
      <!-- Category filter row -->
      <div class="flex gap-2 overflow-x-auto mb-4 scrollbar-hide">
        <button v-for="cat in clubCategories" :key="cat.value"
          @click="selectedCategory = cat.value"
          class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition"
          :class="selectedCategory === cat.value ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200'">
          {{ cat.label }}
        </button>
      </div>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">🔍</p>
        <p class="text-gray-400 text-sm">해당 카테고리의 동호회가 없습니다</p>
        <button @click="showCreateModal = true" class="mt-3 text-blue-500 text-sm hover:underline">새로운 동호회 만들기</button>
      </div>
    </template>

    <template #item-card="{ item }">
      <div @click="$router.push('/clubs/' + item.id)"
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition cursor-pointer group">
        <!-- Gradient banner -->
        <div class="h-24 relative"
          :style="{ background: `linear-gradient(135deg, ${item.gradientFrom}, ${item.gradientTo})` }">
          <div class="absolute top-2 left-2 flex gap-1.5">
            <span v-if="item.isOnline"
              class="bg-blue-500/90 backdrop-blur-sm text-white text-[10px] px-2 py-0.5 rounded-full font-medium">
              🌐 온라인
            </span>
            <span v-else-if="item.regionLabel"
              class="bg-green-500/90 backdrop-blur-sm text-white text-[10px] px-2 py-0.5 rounded-full font-medium">
              📍 {{ item.regionLabel }}
            </span>
          </div>
          <span v-if="item.isApproval"
            class="absolute top-2 right-2 bg-white/90 backdrop-blur-sm text-[10px] px-2 py-0.5 rounded-full font-medium text-gray-600">
            🔒 승인제
          </span>
        </div>

        <!-- Content -->
        <div class="px-4 pb-4 -mt-6 relative">
          <div class="w-12 h-12 rounded-full border-3 border-white flex items-center justify-center text-lg font-bold text-white shadow-md mb-2"
            :style="{ background: `linear-gradient(135deg, ${item.gradientFrom}, ${item.gradientTo})` }">
            {{ item.emoji }}
          </div>
          <h3 class="text-sm font-bold text-gray-800 dark:text-white mb-0.5 group-hover:text-blue-600 transition truncate">
            {{ item.name }}
          </h3>
          <span class="inline-block bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-[10px] px-2 py-0.5 rounded-full mb-1.5">
            {{ item.category }}
          </span>
          <p class="text-xs text-gray-400 line-clamp-1 mb-3">{{ item.description }}</p>
          <div class="flex items-center justify-between">
            <span class="text-[11px] text-gray-400">👤 {{ item.memberCount }}명</span>
            <span class="bg-gradient-to-r from-pink-500 to-red-500 text-white text-[10px] font-semibold px-3 py-1 rounded-full">
              가입하기
            </span>
          </div>
        </div>
      </div>
    </template>
  </ListTemplate>

  <!-- Create Club Modal -->
  <Teleport to="body">
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="showCreateModal = false">
      <div class="fixed inset-0 bg-black/50" @click="showCreateModal = false"></div>
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md relative z-10 max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-5">
            <h2 class="text-lg font-black text-gray-800 dark:text-white">👥 동호회 만들기</h2>
            <button @click="showCreateModal = false" class="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-400 hover:bg-gray-200">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>

          <div class="space-y-4">
            <!-- Photo -->
            <div>
              <label class="block text-xs text-gray-500 mb-1 font-semibold">동호회 사진/로고</label>
              <div class="flex items-center gap-3">
                <div class="w-16 h-16 rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-700 flex items-center justify-center border-2 border-dashed border-gray-300">
                  <img v-if="newClubPhotoPreview" :src="newClubPhotoPreview" class="w-full h-full object-cover" />
                  <span v-else class="text-xl text-gray-400">📷</span>
                </div>
                <label class="bg-blue-50 text-blue-600 px-3 py-1.5 rounded-lg text-sm font-semibold cursor-pointer hover:bg-blue-100">
                  사진 선택
                  <input type="file" accept="image/*" class="hidden" @change="onClubPhotoSelect" />
                </label>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">동호회 이름 <span class="text-red-400">*</span></label>
              <input v-model="createForm.name" type="text" placeholder="예: 애틀랜타 한인 축구회" maxlength="50"
                class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">카테고리 <span class="text-red-400">*</span></label>
              <select v-model="createForm.category"
                class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
                <option value="">선택하세요</option>
                <option v-for="cat in clubCategories.filter(c => c.value !== 'all')" :key="cat.value" :value="cat.value">
                  {{ cat.label }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">소개 <span class="text-red-400">*</span></label>
              <textarea v-model="createForm.description" rows="3" placeholder="동호회에 대해 소개해 주세요"
                class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none" />
            </div>

            <!-- Club type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">동호회 유형</label>
              <div class="flex gap-4">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" :value="true" v-model="createForm.is_online" class="w-4 h-4 text-blue-600" />
                  <span class="text-sm text-gray-700 dark:text-gray-300">🌐 온라인</span>
                </label>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input type="radio" :value="false" v-model="createForm.is_online" class="w-4 h-4 text-blue-600" />
                  <span class="text-sm text-gray-700 dark:text-gray-300">📍 지역</span>
                </label>
              </div>
            </div>

            <!-- Location for local club -->
            <div v-if="!createForm.is_online">
              <label class="block text-xs text-gray-500 mb-1 font-semibold">집코드 (Zip Code)</label>
              <input v-model="createForm.zip_code" type="text" placeholder="예: 90001" maxlength="10"
                class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
            </div>

            <label class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-xl cursor-pointer">
              <input v-model="createForm.is_approval" type="checkbox" class="w-5 h-5 rounded border-gray-300 text-blue-600" />
              <div>
                <p class="text-sm font-medium text-gray-700 dark:text-gray-300">승인제로 운영</p>
                <p class="text-xs text-gray-400">가입 신청을 관리자가 승인해야 가입됩니다</p>
              </div>
            </label>

            <div v-if="createError" class="text-red-600 text-sm bg-red-50 p-3 rounded-xl">{{ createError }}</div>

            <div class="flex gap-3 pt-2">
              <button @click="showCreateModal = false"
                class="flex-1 px-4 py-2.5 border border-gray-300 text-gray-600 rounded-xl text-sm hover:bg-gray-50 transition">취소</button>
              <button @click="submitCreateClub" :disabled="creating"
                class="flex-1 px-4 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 disabled:opacity-50 transition">
                {{ creating ? '만드는 중...' : '동호회 만들기' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ListTemplate from '@/components/templates/ListTemplate.vue'
import axios from 'axios'

const router = useRouter()
const loading = ref(true)
const clubs = ref([])
const search = ref('')
const selectedFilter = ref('all')
const selectedCategory = ref('all')
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const newClubPhoto = ref(null)
const newClubPhotoPreview = ref('')

const typeTabs = [
  { value: 'all', label: '전체' },
  { value: 'online', label: '🌐 온라인' },
  { value: 'local', label: '📍 지역' },
]

const clubCategories = [
  { value: 'all', label: '전체' },
  { value: '스포츠', label: '스포츠' },
  { value: '음식/요리', label: '음식/요리' },
  { value: '육아/교육', label: '육아/교육' },
  { value: '취미/여가', label: '취미/여가' },
  { value: '종교', label: '종교' },
  { value: '비즈니스', label: '비즈니스' },
  { value: '기타', label: '기타' },
]

const createForm = ref({
  name: '', category: '', description: '',
  is_approval: false, is_online: false, zip_code: '',
})

const gradientColors = [
  { from: '#F472B6', to: '#A78BFA' },
  { from: '#34D399', to: '#3B82F6' },
  { from: '#6366F1', to: '#8B5CF6' },
  { from: '#F59E0B', to: '#EF4444' },
  { from: '#059669', to: '#0D9488' },
  { from: '#3B82F6', to: '#1D4ED8' },
  { from: '#EC4899', to: '#BE185D' },
]

const filteredClubs = computed(() => {
  let result = clubs.value
  if (selectedFilter.value === 'online') result = result.filter(c => c.isOnline)
  else if (selectedFilter.value === 'local') result = result.filter(c => !c.isOnline)
  if (selectedCategory.value !== 'all') result = result.filter(c => c.category === selectedCategory.value)
  if (search.value.trim()) {
    const q = search.value.trim().toLowerCase()
    result = result.filter(c => c.name.toLowerCase().includes(q) || c.description.toLowerCase().includes(q))
  }
  return result
})

function onFilterChange(val) { selectedFilter.value = val }
function onSearch(val) { search.value = val }

function onClubPhotoSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  newClubPhoto.value = file
  const reader = new FileReader()
  reader.onload = ev => { newClubPhotoPreview.value = ev.target.result }
  reader.readAsDataURL(file)
}

async function fetchClubs() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/clubs')
    const list = data.data || data || []
    clubs.value = list.map((c, i) => {
      const g = gradientColors[i % gradientColors.length]
      let regionLabel = ''
      if (!c.is_online) regionLabel = c.region || c.zip_code || ''
      return {
        id: c.id, name: c.name,
        category: c.category || '기타',
        emoji: c.name?.charAt(0) || '👥',
        description: c.description || '',
        memberCount: c.member_count || 0,
        isApproval: c.is_approval || false,
        isOnline: c.is_online || false,
        regionLabel,
        gradientFrom: g.from, gradientTo: g.to,
      }
    })
  } catch {}
  loading.value = false
}

async function submitCreateClub() {
  createError.value = ''
  if (!createForm.value.name.trim()) { createError.value = '동호회 이름을 입력하세요.'; return }
  if (!createForm.value.category) { createError.value = '카테고리를 선택하세요.'; return }
  if (!createForm.value.description.trim()) { createError.value = '소개를 입력하세요.'; return }

  creating.value = true
  try {
    const fd = new FormData()
    fd.append('name', createForm.value.name)
    fd.append('category', createForm.value.category)
    fd.append('description', createForm.value.description)
    fd.append('is_approval', createForm.value.is_approval ? '1' : '0')
    fd.append('is_online', createForm.value.is_online ? '1' : '0')
    if (!createForm.value.is_online && createForm.value.zip_code) {
      fd.append('zip_code', createForm.value.zip_code)
    }
    if (newClubPhoto.value) fd.append('cover_image', newClubPhoto.value)
    await axios.post('/api/clubs', fd, { headers: { 'Content-Type': 'multipart/form-data' } })

    createForm.value = { name: '', category: '', description: '', is_approval: false, is_online: false, zip_code: '' }
    newClubPhoto.value = null
    newClubPhotoPreview.value = ''
    showCreateModal.value = false
    await fetchClubs()
  } catch (e) {
    createError.value = e.response?.data?.message || '동호회 생성에 실패했습니다.'
  } finally {
    creating.value = false
  }
}

onMounted(fetchClubs)
</script>
