<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-blue-600">{{ stats.total }}</div>
        <div class="text-xs text-gray-500 mt-0.5">전체 매물</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-green-500">{{ stats.selling }}</div>
        <div class="text-xs text-gray-500 mt-0.5">판매중</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-gray-500">{{ stats.done }}</div>
        <div class="text-xs text-gray-500 mt-0.5">거래완료</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-orange-500">{{ stats.newThisWeek }}</div>
        <div class="text-xs text-gray-500 mt-0.5">이번주 신규</div>
      </div>
    </div>

    <!-- 필터 & 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <!-- 필터 -->
      <div class="p-4 border-b border-gray-100">
        <div class="flex flex-col sm:flex-row gap-3">
          <input v-model="search" placeholder="상품명 / 판매자 검색"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 flex-1" />
          <select v-model="filterCategory"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 카테고리</option>
            <option value="전자기기">전자기기</option>
            <option value="가구">가구</option>
            <option value="의류">의류</option>
            <option value="자동차">자동차</option>
            <option value="기타">기타</option>
          </select>
          <select v-model="filterStatus"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 상태</option>
            <option value="판매중">판매중</option>
            <option value="예약중">예약중</option>
            <option value="완료">완료</option>
            <option value="숨김">숨김</option>
          </select>
          <button @click="resetFilters"
            class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-semibold transition">
            초기화
          </button>
        </div>
      </div>

      <!-- 벌크 액션 -->
      <div v-if="selected.length > 0" class="px-4 py-2 bg-blue-50 border-b border-blue-100 flex items-center gap-3">
        <span class="text-xs font-semibold text-blue-700">{{ selected.length }}개 선택됨</span>
        <button @click="bulkHide"
          class="text-xs bg-yellow-100 hover:bg-yellow-200 text-yellow-700 px-3 py-1 rounded-lg font-semibold transition">
          숨기기
        </button>
        <button @click="bulkDelete"
          class="text-xs bg-red-100 hover:bg-red-200 text-red-600 px-3 py-1 rounded-lg font-semibold transition">
          삭제
        </button>
        <button @click="selected = []"
          class="text-xs text-gray-400 hover:text-gray-600 ml-auto transition">
          선택 해제
        </button>
      </div>

      <!-- 테이블 -->
      <div class="overflow-x-auto">
        <div v-if="filteredItems.length === 0" class="text-center py-12 text-gray-400 text-sm">
          검색 결과가 없습니다.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="px-4 py-3 w-8">
                <input type="checkbox" :checked="allSelected" @change="toggleAll"
                  class="rounded border-gray-300 text-blue-500" />
              </th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">상품</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">카테고리</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">가격</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">판매자</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">상태</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">조회수</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">등록일</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="item in filteredItems" :key="item.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <input type="checkbox" :value="item.id" v-model="selected"
                  class="rounded border-gray-300 text-blue-500" />
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <!-- 썸네일 placeholder -->
                  <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-gray-100 to-gray-200 flex-shrink-0 flex items-center justify-center text-gray-400 text-xs font-bold overflow-hidden">
                    {{ categoryIcon(item.category) }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-800 truncate max-w-[150px]">{{ item.title }}</div>
                    <div class="text-[10px] text-gray-400 truncate max-w-[150px]">{{ item.description }}</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', categoryClass(item.category)]">
                  {{ item.category }}
                </span>
              </td>
              <td class="px-4 py-3 text-sm font-bold text-gray-800">
                ${{ item.price.toLocaleString() }}
              </td>
              <td class="px-4 py-3 text-xs text-gray-600 hidden sm:table-cell">{{ item.seller }}</td>
              <td class="px-4 py-3">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', statusClass(item.status)]">
                  {{ item.status }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden lg:table-cell">{{ item.views }}</td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden lg:table-cell">{{ item.created_at }}</td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openDetail(item)"
                    class="text-[11px] bg-blue-50 hover:bg-blue-100 text-blue-600 px-2.5 py-1 rounded-lg transition font-medium">
                    상세
                  </button>
                  <button @click="confirmDelete(item)"
                    class="text-[11px] bg-red-50 hover:bg-red-100 text-red-500 px-2.5 py-1 rounded-lg transition font-medium">
                    삭제
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 상세 모달 -->
    <div v-if="selectedItem" class="fixed inset-0 z-50 flex items-center justify-center p-4"
      style="background:rgba(0,0,0,0.45)" @click.self="selectedItem = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <!-- 모달 헤더 -->
        <div class="flex items-start justify-between p-5 border-b border-gray-100">
          <div>
            <h2 class="text-lg font-bold text-gray-900">{{ selectedItem.title }}</h2>
            <div class="flex items-center gap-2 mt-1">
              <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', categoryClass(selectedItem.category)]">
                {{ selectedItem.category }}
              </span>
              <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', statusClass(selectedItem.status)]">
                {{ selectedItem.status }}
              </span>
            </div>
          </div>
          <button @click="selectedItem = null"
            class="text-gray-400 hover:text-gray-600 text-xl font-bold leading-none ml-4">×</button>
        </div>

        <!-- 모달 내용 -->
        <div class="p-5 space-y-5">
          <!-- 사진 갤러리 placeholder -->
          <div class="grid grid-cols-3 gap-2">
            <div v-for="n in 3" :key="n"
              class="aspect-square rounded-xl bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center text-3xl">
              {{ categoryIcon(selectedItem.category) }}
            </div>
          </div>

          <!-- 상품 정보 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-xl p-3">
              <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">가격</div>
              <div class="text-lg font-black text-blue-600">${{ selectedItem.price.toLocaleString() }}</div>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">조회수</div>
              <div class="text-lg font-black text-gray-700">{{ selectedItem.views }}</div>
            </div>
          </div>

          <!-- 상품 설명 -->
          <div>
            <div class="text-xs font-semibold text-gray-500 mb-2">상품 설명</div>
            <div class="bg-gray-50 rounded-xl p-3 text-sm text-gray-700 leading-relaxed">
              {{ selectedItem.description }}
            </div>
          </div>

          <!-- 채팅 문의 수 -->
          <div class="flex items-center gap-3 bg-blue-50 rounded-xl p-3">
            <div class="text-2xl">💬</div>
            <div>
              <div class="text-xs font-semibold text-blue-700">채팅 문의</div>
              <div class="text-sm text-blue-600">{{ Math.floor(selectedItem.views / 5) }}건의 채팅 문의</div>
            </div>
          </div>

          <!-- 판매자 정보 -->
          <div class="border-t border-gray-100 pt-4">
            <div class="text-xs font-semibold text-gray-500 mb-2">판매자 정보</div>
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center text-sm font-bold text-purple-600">
                {{ selectedItem.seller.charAt(0) }}
              </div>
              <div>
                <div class="text-sm font-semibold text-gray-800">{{ selectedItem.seller }}</div>
                <div class="text-[10px] text-gray-400">등록일: {{ selectedItem.created_at }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 모달 푸터 -->
        <div class="flex justify-end gap-2 px-5 pb-5">
          <button @click="hideItem(selectedItem); selectedItem = null"
            class="bg-yellow-50 hover:bg-yellow-100 text-yellow-700 px-4 py-2 rounded-lg text-sm font-semibold transition">
            숨기기
          </button>
          <button @click="confirmDelete(selectedItem); selectedItem = null"
            class="bg-red-50 hover:bg-red-100 text-red-500 px-4 py-2 rounded-lg text-sm font-semibold transition">
            삭제
          </button>
          <button @click="selectedItem = null"
            class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-semibold transition">
            닫기
          </button>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4"
      style="background:rgba(0,0,0,0.45)" @click.self="deleteTarget = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center">
        <div class="text-4xl mb-3">🗑️</div>
        <h3 class="text-base font-bold text-gray-900 mb-1">매물을 삭제하시겠습니까?</h3>
        <p class="text-sm text-gray-500 mb-5">
          <span class="font-semibold text-gray-700">{{ deleteTarget.title }}</span> 매물이 영구 삭제됩니다.
        </p>
        <div class="flex gap-2 justify-center">
          <button @click="deleteTarget = null"
            class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 py-2.5 rounded-xl text-sm font-semibold transition">
            취소
          </button>
          <button @click="doDelete"
            class="flex-1 bg-red-500 hover:bg-red-600 text-white py-2.5 rounded-xl text-sm font-semibold transition">
            삭제
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'


const items = ref([])
const search = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const selected = ref([])
const selectedItem = ref(null)
const deleteTarget = ref(null)

const stats = computed(() => ({
  total: items.value.length,
  selling: items.value.filter(i => i.status === '판매중').length,
  done: items.value.filter(i => i.status === '완료').length,
  newThisWeek: items.value.filter(i => i.created_at >= '2026-03-22').length,
}))

const filteredItems = computed(() => {
  return items.value.filter(i => {
    const matchSearch = !search.value ||
      i.title.toLowerCase().includes(search.value.toLowerCase()) ||
      i.seller.toLowerCase().includes(search.value.toLowerCase())
    const matchCat = !filterCategory.value || i.category === filterCategory.value
    const matchStatus = !filterStatus.value || i.status === filterStatus.value
    return matchSearch && matchCat && matchStatus
  })
})

const allSelected = computed(() =>
  filteredItems.value.length > 0 &&
  filteredItems.value.every(i => selected.value.includes(i.id))
)

function toggleAll(e) {
  if (e.target.checked) {
    selected.value = filteredItems.value.map(i => i.id)
  } else {
    selected.value = []
  }
}

function categoryClass(cat) {
  const map = {
    '전자기기': 'bg-blue-50 text-blue-600',
    '가구': 'bg-amber-50 text-amber-600',
    '의류': 'bg-pink-50 text-pink-600',
    '자동차': 'bg-indigo-50 text-indigo-600',
    '기타': 'bg-gray-100 text-gray-500',
  }
  return map[cat] || 'bg-gray-100 text-gray-500'
}

function statusClass(status) {
  const map = {
    '판매중': 'bg-green-50 text-green-600',
    '예약중': 'bg-yellow-50 text-yellow-600',
    '완료': 'bg-gray-100 text-gray-500',
    '숨김': 'bg-red-50 text-red-500',
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

function categoryIcon(cat) {
  const map = {
    '전자기기': '📱',
    '가구': '🛋️',
    '의류': '👗',
    '자동차': '🚗',
    '기타': '📦',
  }
  return map[cat] || '📦'
}

function openDetail(item) {
  selectedItem.value = item
}

function confirmDelete(item) {
  deleteTarget.value = item
}

function hideItem(item) {
  const idx = items.value.findIndex(i => i.id === item.id)
  if (idx !== -1) items.value[idx] = { ...items.value[idx], status: '숨김' }
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await axios.delete(`/api/admin/market/${deleteTarget.value.id}`)
  } catch (e) {
    // demo: proceed with local deletion
  }
  items.value = items.value.filter(i => i.id !== deleteTarget.value.id)
  selected.value = selected.value.filter(id => id !== deleteTarget.value.id)
  deleteTarget.value = null
}

function bulkHide() {
  selected.value.forEach(id => {
    const idx = items.value.findIndex(i => i.id === id)
    if (idx !== -1) items.value[idx] = { ...items.value[idx], status: '숨김' }
  })
  selected.value = []
}

function bulkDelete() {
  items.value = items.value.filter(i => !selected.value.includes(i.id))
  selected.value = []
}

function resetFilters() {
  search.value = ''
  filterCategory.value = ''
  filterStatus.value = ''
}

async function loadItems() {
  try {
    const res = await axios.get('/api/admin/market')
    items.value = res.data?.data || res.data || []
  } catch (e) {
    items.value = []
  }
}

onMounted(() => {
  loadItems()
})
</script>
