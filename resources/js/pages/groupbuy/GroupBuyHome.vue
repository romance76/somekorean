<template>
  <ListTemplate
    title="공동구매"
    emoji="🛒"
    subtitle="함께 사면 더 저렴하게! 한인 그룹 바이"
    :loading="loading"
    :items="items"
    :categories="statusTabs"
    :activeCategory="activeStatus"
    :hasSearch="true"
    :searchQuery="search"
    searchPlaceholder="공동구매 검색..."
    :hasViewToggle="false"
    @category-change="onStatusChange"
    @search="onSearch"
  >
    <template #header-right>
      <button v-if="auth.isLoggedIn" @click="showWrite = true"
        class="bg-orange-500 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-orange-600 transition whitespace-nowrap">
        + 등록
      </button>
    </template>

    <template #item-card="{ item }">
      <div @click="openDetail(item)"
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-md transition cursor-pointer">
        <!-- Image -->
        <div v-if="item.images?.[0]" class="h-36 bg-gray-100 dark:bg-gray-700 overflow-hidden">
          <img :src="item.images[0]" class="w-full h-full object-cover"
            @error="e => { e.target.style.display='none' }" />
        </div>
        <div v-else class="h-28 bg-gradient-to-br from-orange-400 to-amber-400 flex items-center justify-center">
          <span class="text-4xl">🛒</span>
        </div>
        <div class="p-4">
          <!-- Status badge -->
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xs font-bold px-2 py-0.5 rounded-full"
              :class="statusClass(item.status)">
              {{ statusLabel(item.status) }}
            </span>
            <span v-if="item.category" class="text-xs text-gray-400">{{ item.category }}</span>
          </div>
          <h3 class="font-bold text-gray-800 dark:text-white text-sm mb-2 line-clamp-2">{{ item.title }}</h3>

          <!-- Progress bar -->
          <div class="mb-2">
            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
              <span>{{ item.participants_count || 0 }}명 참여</span>
              <span>최소 {{ item.min_participants }}명</span>
            </div>
            <div class="h-2 bg-gray-100 dark:bg-gray-700 rounded-full overflow-hidden">
              <div class="h-full bg-orange-400 rounded-full transition-all"
                :style="{ width: Math.min(100, ((item.participants_count || 0) / (item.min_participants || 1)) * 100) + '%' }"></div>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <span class="font-black text-orange-600 dark:text-orange-400 text-sm">${{ item.target_price }}</span>
            <span class="text-xs text-gray-400">{{ deadlineText(item.deadline) }}</span>
          </div>
        </div>
      </div>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-5xl mb-3">🛒</p>
        <p class="text-gray-400 font-semibold text-sm">등록된 공동구매가 없습니다</p>
        <button v-if="auth.isLoggedIn" @click="showWrite = true"
          class="mt-4 bg-orange-500 text-white px-6 py-2.5 rounded-xl font-bold text-sm">첫 공동구매 등록</button>
      </div>
    </template>
  </ListTemplate>

  <!-- Detail Modal -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="selected" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4" @click.self="selected = null">
        <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto shadow-2xl">
          <div v-if="selected.images?.[0]" class="h-48 overflow-hidden rounded-t-2xl">
            <img :src="selected.images[0]" class="w-full h-full object-cover" />
          </div>
          <div class="p-6">
            <div class="flex items-start justify-between mb-3">
              <h2 class="font-black text-gray-800 dark:text-white text-lg flex-1">{{ selected.title }}</h2>
              <button @click="selected = null" class="text-gray-400 ml-2 hover:text-gray-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
            <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed mb-4 whitespace-pre-wrap">{{ selected.description }}</p>

            <!-- Progress -->
            <div class="bg-orange-50 dark:bg-orange-900/20 rounded-xl p-4 mb-4">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm font-bold text-orange-700 dark:text-orange-400">참여 현황</span>
                <span class="text-sm font-black text-orange-600">{{ selected.participants_count }} / {{ selected.min_participants }}명</span>
              </div>
              <div class="h-3 bg-orange-100 dark:bg-orange-900/40 rounded-full overflow-hidden">
                <div class="h-full bg-orange-500 rounded-full"
                  :style="{ width: Math.min(100, ((selected.participants_count || 0) / (selected.min_participants || 1)) * 100) + '%' }"></div>
              </div>
            </div>

            <div class="flex items-center gap-2 mb-4">
              <span class="text-2xl font-black text-orange-600">${{ selected.target_price }}</span>
              <span class="text-sm text-gray-400">목표가</span>
            </div>

            <a v-if="selected.product_url" :href="selected.product_url" target="_blank"
              class="flex items-center gap-1 text-blue-600 text-sm hover:underline mb-4">🔗 상품 링크</a>

            <div class="flex gap-3">
              <button v-if="selected.status === 'open' && auth.isLoggedIn && !selected.is_joined"
                @click="join(selected.id)" :disabled="joining"
                class="flex-1 bg-orange-500 text-white py-3 rounded-xl font-black text-sm disabled:opacity-50">
                {{ joining ? '처리중...' : '참여하기' }}
              </button>
              <button v-else-if="selected.is_joined" @click="leave(selected.id)"
                class="flex-1 border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 py-3 rounded-xl font-semibold text-sm">
                참여 취소
              </button>
              <button v-else-if="!auth.isLoggedIn" @click="$router.push('/auth/login')"
                class="flex-1 bg-orange-500 text-white py-3 rounded-xl font-black text-sm">
                로그인 후 참여
              </button>
              <span v-else class="flex-1 text-center text-sm text-gray-400 py-3">
                {{ selected.status === 'completed' ? '달성 완료' : '취소됨' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Write Modal -->
    <Transition name="fade">
      <div v-if="showWrite" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4" @click.self="showWrite = false">
        <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto shadow-2xl">
          <div class="bg-gradient-to-r from-orange-500 to-amber-500 text-white px-6 py-4 rounded-t-2xl">
            <h2 class="font-black text-lg">🛒 공동구매 등록</h2>
          </div>
          <div class="p-5 space-y-4">
            <div>
              <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">제목 *</label>
              <input v-model="writeForm.title" type="text" placeholder="예: 삼양 불닭볶음면 공동구매"
                class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">설명 *</label>
              <textarea v-model="writeForm.description" rows="3" placeholder="상품 설명, 배송 방법 등..."
                class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-orange-400"></textarea>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">목표가 ($) *</label>
                <input v-model="writeForm.target_price" type="number" placeholder="0.00"
                  class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">최소 인원 *</label>
                <input v-model="writeForm.min_participants" type="number" min="2" placeholder="2"
                  class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">마감일 *</label>
              <input v-model="writeForm.deadline" type="datetime-local"
                class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 mb-1">상품 링크 (선택)</label>
              <input v-model="writeForm.product_url" type="url" placeholder="https://..."
                class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400" />
            </div>
            <div class="flex gap-3 pt-2">
              <button @click="showWrite = false"
                class="flex-1 border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 py-2.5 rounded-xl font-semibold text-sm">취소</button>
              <button @click="submitGroupBuy" :disabled="submitting || !writeForm.title || !writeForm.target_price"
                class="flex-1 bg-orange-500 text-white py-2.5 rounded-xl font-black text-sm disabled:opacity-50">
                {{ submitting ? '등록 중...' : '등록하기' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ListTemplate from '@/components/templates/ListTemplate.vue'
import axios from 'axios'

const auth = useAuthStore()
const items = ref([])
const loading = ref(true)
const selected = ref(null)
const showWrite = ref(false)
const joining = ref(false)
const submitting = ref(false)
const search = ref('')
const activeStatus = ref('')

const statusTabs = [
  { value: '', label: '전체' },
  { value: 'open', label: '모집중' },
  { value: 'completed', label: '확정' },
  { value: 'closed', label: '완료' },
]

const writeForm = ref({
  title: '', description: '', target_price: '', min_participants: 2,
  category: 'food', deadline: '', product_url: '',
})

function statusClass(s) {
  if (s === 'open') return 'bg-green-100 text-green-700'
  if (s === 'completed') return 'bg-blue-100 text-blue-700'
  return 'bg-gray-100 text-gray-500'
}

function statusLabel(s) {
  if (s === 'open') return '모집중'
  if (s === 'completed') return '달성완료'
  return '취소'
}

function deadlineText(dt) {
  if (!dt) return ''
  const diff = (new Date(dt) - Date.now()) / 1000
  if (diff < 0) return '마감'
  if (diff < 3600) return `${Math.floor(diff / 60)}분 남음`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 남음`
  return `${Math.floor(diff / 86400)}일 남음`
}

function onStatusChange(val) { activeStatus.value = val; fetchItems() }
function onSearch(val) { search.value = val; fetchItems() }
function openDetail(item) { selected.value = item }

async function fetchItems() {
  loading.value = true
  try {
    const params = {}
    if (activeStatus.value) params.status = activeStatus.value
    if (search.value) params.search = search.value
    const { data } = await axios.get('/api/groupbuy', { params })
    items.value = data.data ?? data ?? []
  } catch { items.value = [] }
  loading.value = false
}

async function join(id) {
  joining.value = true
  try {
    const { data } = await axios.post(`/api/groupbuy/${id}/join`)
    if (selected.value) { selected.value.participants_count = data.participants_count; selected.value.is_joined = true }
    const idx = items.value.findIndex(i => i.id === id)
    if (idx >= 0) items.value[idx].participants_count = data.participants_count
  } catch (e) { alert(e?.response?.data?.message || '참여 실패') }
  joining.value = false
}

async function leave(id) {
  try {
    await axios.post(`/api/groupbuy/${id}/leave`)
    if (selected.value) { selected.value.is_joined = false; selected.value.participants_count-- }
  } catch {}
}

async function submitGroupBuy() {
  if (!writeForm.value.title || !writeForm.value.target_price || !writeForm.value.deadline) return
  submitting.value = true
  try {
    const { data } = await axios.post('/api/groupbuy', writeForm.value)
    items.value.unshift(data)
    showWrite.value = false
    writeForm.value = { title: '', description: '', target_price: '', min_participants: 2, category: 'food', deadline: '', product_url: '' }
  } catch (e) { alert(e?.response?.data?.message || '등록 실패') }
  submitting.value = false
}

onMounted(fetchItems)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
