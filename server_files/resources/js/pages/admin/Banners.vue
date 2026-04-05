<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
        <p class="text-2xl font-bold text-gray-800">{{ banners.length }}</p>
        <p class="text-xs text-gray-500 mt-1">전체 배너</p>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
        <p class="text-2xl font-bold text-green-600">{{ activeBannerCount }}</p>
        <p class="text-xs text-gray-500 mt-1">활성 배너</p>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
        <p class="text-2xl font-bold text-blue-600">{{ totalClicks.toLocaleString() }}</p>
        <p class="text-xs text-gray-500 mt-1">총 클릭수</p>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center">
        <p class="text-2xl font-bold text-purple-600">${{ totalRevenue.toLocaleString() }}</p>
        <p class="text-xs text-gray-500 mt-1">총 광고 수익</p>
      </div>
    </div>

    <!-- 필터 + 추가 버튼 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div class="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        <div class="flex flex-wrap gap-2">
          <select v-model="filterPosition" @change="applyFilter"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 위치</option>
            <option value="메인상단">메인상단</option>
            <option value="메인중간">메인중간</option>
            <option value="사이드">사이드</option>
            <option value="게시판상단">게시판상단</option>
            <option value="팝업">팝업</option>
          </select>
          <select v-model="filterStatus" @change="applyFilter"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 상태</option>
            <option value="active">활성</option>
            <option value="inactive">비활성</option>
          </select>
        </div>
        <button @click="openModal(null)"
          class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center gap-1.5">
          <span class="text-base leading-none">+</span> 배너 추가
        </button>
      </div>
    </div>

    <!-- 배너 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
      <div v-else-if="filtered.length === 0" class="text-center py-10 text-gray-400 text-sm">배너가 없습니다.</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">ID</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">배너명</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">위치</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">이미지</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden xl:table-cell">링크</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">기간</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">클릭</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">노출</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">CTR</th>
              <th class="text-center px-4 py-3 text-xs font-semibold text-gray-500">상태</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="b in filtered" :key="b.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3 text-xs text-gray-400">#{{ b.id }}</td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-800 text-xs">{{ b.name }}</div>
                <div class="text-[10px] text-gray-400">{{ b.advertiser }}</div>
              </td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span class="text-[10px] px-2 py-0.5 rounded-full font-semibold"
                  :class="positionColor(b.position)">{{ b.position }}</span>
              </td>
              <td class="px-4 py-3 hidden lg:table-cell">
                <img v-if="b.image_url" :src="b.image_url" :alt="b.name"
                  class="h-8 w-16 object-cover rounded border border-gray-100" @error="e => e.target.style.display='none'" />
                <span v-else class="text-[10px] text-gray-300">없음</span>
              </td>
              <td class="px-4 py-3 hidden xl:table-cell">
                <a v-if="b.link_url" :href="b.link_url" target="_blank"
                  class="text-[10px] text-blue-500 hover:underline truncate block max-w-[120px]">{{ b.link_url }}</a>
                <span v-else class="text-[10px] text-gray-300">없음</span>
              </td>
              <td class="px-4 py-3 hidden lg:table-cell text-[10px] text-gray-500">
                <div>{{ b.start_date }}</div>
                <div>~ {{ b.end_date }}</div>
              </td>
              <td class="px-4 py-3 text-xs text-right text-gray-600 hidden sm:table-cell">{{ (b.clicks || 0).toLocaleString() }}</td>
              <td class="px-4 py-3 text-xs text-right text-gray-600 hidden sm:table-cell">{{ (b.impressions || 0).toLocaleString() }}</td>
              <td class="px-4 py-3 text-xs text-right hidden sm:table-cell">
                <span :class="ctrColor(calcCtr(b))">{{ calcCtr(b) }}%</span>
              </td>
              <td class="px-4 py-3 text-center">
                <button @click="toggleStatus(b)"
                  :class="['text-[10px] px-2.5 py-1 rounded-full font-semibold transition',
                    b.status === 'active'
                      ? 'bg-green-100 text-green-600 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-400 hover:bg-gray-200']">
                  {{ b.status === 'active' ? '활성' : '비활성' }}
                </button>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-1.5">
                  <button @click="openModal(b)"
                    class="text-[10px] bg-blue-50 hover:bg-blue-100 text-blue-600 px-2 py-1 rounded-lg transition">수정</button>
                  <button @click="deleteBanner(b)"
                    class="text-[10px] bg-red-50 hover:bg-red-100 text-red-500 px-2 py-1 rounded-lg transition">삭제</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 팝업 배너 섹션 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100">
        <h2 class="font-semibold text-gray-800">팝업 배너 관리</h2>
        <span class="text-xs bg-orange-100 text-orange-600 px-2 py-0.5 rounded font-medium">{{ popupBanners.length }}개</span>
      </div>
      <div v-if="popupBanners.length === 0" class="text-center py-8 text-gray-400 text-sm">팝업 배너가 없습니다.</div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="p in popupBanners" :key="p.id" class="px-5 py-4">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1.5">
                <span class="font-medium text-sm text-gray-800">{{ p.name }}</span>
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold',
                  p.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400']">
                  {{ p.status === 'active' ? '활성' : '비활성' }}
                </span>
                <span class="text-[10px] bg-blue-50 text-blue-500 px-2 py-0.5 rounded-full">{{ p.show_condition }}</span>
              </div>
              <textarea v-model="p.html_content" rows="3"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-xs font-mono focus:outline-none focus:border-blue-400 resize-none"
                placeholder="팝업 HTML 내용 입력..."></textarea>
              <div class="flex gap-2 mt-2">
                <select v-model="p.show_condition"
                  class="border border-gray-200 rounded-lg px-2 py-1 text-xs focus:outline-none focus:border-blue-400">
                  <option value="전체">전체</option>
                  <option value="로그인">로그인</option>
                  <option value="비로그인">비로그인</option>
                </select>
                <button @click="savePopupContent(p)"
                  class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded-lg text-xs font-semibold transition">저장</button>
                <button @click="toggleStatus(p)"
                  :class="['px-3 py-1 rounded-lg text-xs font-semibold transition',
                    p.status === 'active' ? 'bg-orange-100 text-orange-600 hover:bg-orange-200' : 'bg-green-100 text-green-600 hover:bg-green-200']">
                  {{ p.status === 'active' ? '비활성화' : '활성화' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 추가/수정 모달 -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="closeModal">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
          <h3 class="font-bold text-gray-800">{{ editingBanner ? '배너 수정' : '배너 추가' }}</h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
        </div>
        <div class="overflow-y-auto p-6 space-y-4">

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <!-- 배너명 -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-600 mb-1">배너명 *</label>
              <input v-model="form.name" type="text" placeholder="배너명 입력"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>

            <!-- 위치 -->
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">위치 *</label>
              <select v-model="form.position"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
                <option value="">선택</option>
                <option value="메인상단">메인상단</option>
                <option value="메인중간">메인중간</option>
                <option value="사이드">사이드바</option>
                <option value="게시판상단">게시판상단</option>
                <option value="팝업">팝업</option>
              </select>
            </div>

            <!-- 노출 순서 -->
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">노출 순서</label>
              <input v-model.number="form.sort_order" type="number" min="0" placeholder="0"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>

            <!-- 이미지 URL -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-600 mb-1">이미지 URL</label>
              <input v-model="form.image_url" type="text" placeholder="https://example.com/banner.jpg"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
              <div v-if="form.image_url" class="mt-2">
                <img :src="form.image_url" alt="미리보기"
                  class="h-16 rounded-lg border border-gray-100 object-cover" @error="e => e.target.style.display='none'" />
              </div>
            </div>

            <!-- 링크 URL -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-600 mb-1">링크 URL</label>
              <input v-model="form.link_url" type="text" placeholder="https://example.com"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>

            <!-- 새 탭 열기 -->
            <div class="sm:col-span-2 flex items-center gap-2">
              <input v-model="form.open_new_tab" id="openNewTab" type="checkbox"
                class="w-4 h-4 text-blue-500 rounded border-gray-300" />
              <label for="openNewTab" class="text-sm text-gray-600 cursor-pointer">새 탭에서 열기</label>
            </div>

            <!-- 기간 -->
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">노출 시작일</label>
              <input v-model="form.start_date" type="date"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">노출 종료일</label>
              <input v-model="form.end_date" type="date"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>

            <!-- 광고주명 -->
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">광고주명</label>
              <input v-model="form.advertiser" type="text" placeholder="광고주 이름"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>

            <!-- 광고 금액 -->
            <div>
              <label class="block text-xs font-semibold text-gray-600 mb-1">광고 금액 ($)</label>
              <input v-model.number="form.price" type="number" min="0" placeholder="0"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>

            <!-- 활성화 -->
            <div class="sm:col-span-2 flex items-center gap-2">
              <input v-model="form.active" id="bannerActive" type="checkbox"
                class="w-4 h-4 text-green-500 rounded border-gray-300" />
              <label for="bannerActive" class="text-sm text-gray-600 cursor-pointer">활성화</label>
            </div>

            <!-- 메모 -->
            <div class="sm:col-span-2">
              <label class="block text-xs font-semibold text-gray-600 mb-1">메모</label>
              <textarea v-model="form.memo" rows="2" placeholder="내부 메모..."
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 resize-none"></textarea>
            </div>
          </div>
        </div>

        <div class="flex gap-3 px-6 py-4 border-t border-gray-100 flex-shrink-0">
          <button @click="saveBanner" :disabled="saving"
            class="flex-1 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white py-2.5 rounded-xl text-sm font-bold transition">
            {{ saving ? '저장 중...' : (editingBanner ? '수정 저장' : '배너 추가') }}
          </button>
          <button @click="closeModal"
            class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 py-2.5 rounded-xl text-sm font-semibold transition">
            취소
          </button>
        </div>
      </div>
    </div>

    <!-- 토스트 -->
    <transition name="toast">
      <div v-if="toast.show"
        :class="['fixed bottom-6 right-6 z-[60] px-4 py-3 rounded-xl shadow-lg text-white text-sm font-medium',
          toast.type === 'error' ? 'bg-red-500' : 'bg-green-500']">
        {{ toast.message }}
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const banners   = ref([])
const loading   = ref(false)
const saving    = ref(false)
const showModal = ref(false)
const editingBanner = ref(null)

const filterPosition = ref('')
const filterStatus   = ref('')

const toast = ref({ show: false, message: '', type: 'success' })

const defaultForm = () => ({
  name: '', position: '', image_url: '', link_url: '',
  open_new_tab: false, start_date: '', end_date: '',
  sort_order: 0, active: true, advertiser: '',
  price: 0, memo: '', html_content: '', show_condition: '전체'
})
const form = ref(defaultForm())

// --- dummy data ---
const dummyBanners = [
  { id: 1, name: '한인마트 오픈 기념 배너', position: '메인상단', image_url: 'https://placehold.co/320x80/3b82f6/white?text=Banner1', link_url: 'https://example.com', open_new_tab: true, start_date: '2026-03-01', end_date: '2026-04-30', sort_order: 1, status: 'active', advertiser: '한인마트', price: 500, clicks: 1240, impressions: 32000, memo: '', html_content: '', show_condition: '전체' },
  { id: 2, name: '법률 상담 광고', position: '사이드', image_url: 'https://placehold.co/160x600/10b981/white?text=Law', link_url: 'https://example.com/law', open_new_tab: true, start_date: '2026-02-01', end_date: '2026-05-31', sort_order: 2, status: 'active', advertiser: '김변호사', price: 300, clicks: 830, impressions: 15000, memo: '월간 계약', html_content: '', show_condition: '전체' },
  { id: 3, name: '한국어 학원 홍보', position: '메인중간', image_url: 'https://placehold.co/728x90/f59e0b/white?text=School', link_url: 'https://example.com/school', open_new_tab: false, start_date: '2026-03-15', end_date: '2026-06-15', sort_order: 3, status: 'active', advertiser: '한글학원', price: 200, clicks: 412, impressions: 8900, memo: '', html_content: '', show_condition: '전체' },
  { id: 4, name: '세금보고 시즌 이벤트', position: '게시판상단', image_url: 'https://placehold.co/728x90/ef4444/white?text=Tax', link_url: 'https://example.com/tax', open_new_tab: true, start_date: '2026-01-01', end_date: '2026-04-15', sort_order: 1, status: 'active', advertiser: 'ABC 회계', price: 400, clicks: 2100, impressions: 41000, memo: '세금 시즌 특별 계약', html_content: '', show_condition: '전체' },
  { id: 5, name: '한인 부동산 광고', position: '사이드', image_url: 'https://placehold.co/160x600/8b5cf6/white?text=Real+Estate', link_url: 'https://example.com/realestate', open_new_tab: true, start_date: '2026-03-01', end_date: '2026-08-31', sort_order: 4, status: 'inactive', advertiser: '박부동산', price: 600, clicks: 55, impressions: 2200, memo: '', html_content: '', show_condition: '전체' },
  { id: 6, name: '한인 식당 신규 오픈 팝업', position: '팝업', image_url: '', link_url: 'https://example.com/restaurant', open_new_tab: false, start_date: '2026-03-20', end_date: '2026-04-20', sort_order: 1, status: 'active', advertiser: '맛있는 식당', price: 150, clicks: 380, impressions: 5400, memo: '오픈 기념 1개월', html_content: '<div style="text-align:center;padding:20px"><h2>한인 식당 신규 오픈!</h2><p>오픈 기념 10% 할인</p></div>', show_condition: '전체' },
  { id: 7, name: '커뮤니티 가입 유도 팝업', position: '팝업', image_url: '', link_url: '', open_new_tab: false, start_date: '2026-01-01', end_date: '2026-12-31', sort_order: 2, status: 'active', advertiser: 'SomeKorean', price: 0, clicks: 920, impressions: 18000, memo: '자체 운영', html_content: '<div style="text-align:center;padding:20px"><h2>함께해요!</h2><p>지금 가입하고 포인트 받으세요</p></div>', show_condition: '비로그인' },
]

// --- computed ---
const filtered = computed(() => {
  return banners.value.filter(b => {
    const posOk = !filterPosition.value || b.position === filterPosition.value
    const stOk  = !filterStatus.value   || b.status === filterStatus.value
    return posOk && stOk
  })
})

const popupBanners = computed(() => banners.value.filter(b => b.position === '팝업'))

const activeBannerCount = computed(() => banners.value.filter(b => b.status === 'active').length)

const totalClicks = computed(() => banners.value.reduce((s, b) => s + (b.clicks || 0), 0))

const totalRevenue = computed(() => banners.value.reduce((s, b) => s + (b.price || 0), 0))

// --- helpers ---
function calcCtr(b) {
  if (!b.impressions) return '0.00'
  return ((b.clicks / b.impressions) * 100).toFixed(2)
}

function ctrColor(ctr) {
  const v = parseFloat(ctr)
  if (v >= 3) return 'text-green-600 font-semibold'
  if (v >= 1) return 'text-yellow-600'
  return 'text-gray-400'
}

function positionColor(pos) {
  const map = {
    '메인상단': 'bg-blue-100 text-blue-600',
    '메인중간': 'bg-indigo-100 text-indigo-600',
    '사이드':   'bg-green-100 text-green-600',
    '게시판상단':'bg-orange-100 text-orange-600',
    '팝업':     'bg-purple-100 text-purple-600',
  }
  return map[pos] || 'bg-gray-100 text-gray-500'
}

function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}

// --- API ---
async function load() {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/banners')
    banners.value = res.data.data ?? res.data
  } catch {
    banners.value = dummyBanners
  } finally {
    loading.value = false
  }
}

function applyFilter() { /* reactive computed handles it */ }

function openModal(banner) {
  if (banner) {
    editingBanner.value = banner
    form.value = { ...defaultForm(), ...banner }
  } else {
    editingBanner.value = null
    form.value = defaultForm()
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingBanner.value = null
  form.value = defaultForm()
}

async function saveBanner() {
  if (!form.value.name || !form.value.position) {
    showToast('배너명과 위치는 필수입니다.', 'error')
    return
  }
  saving.value = true
  const payload = { ...form.value, status: form.value.active ? 'active' : 'inactive' }
  try {
    if (editingBanner.value) {
      await axios.put(`/api/admin/banners/${editingBanner.value.id}`, payload)
      const idx = banners.value.findIndex(b => b.id === editingBanner.value.id)
      if (idx !== -1) banners.value[idx] = { ...banners.value[idx], ...payload }
      showToast('배너가 수정되었습니다.')
    } else {
      const res = await axios.post('/api/admin/banners', payload)
      const newBanner = res.data.banner ?? res.data
      banners.value.unshift({ clicks: 0, impressions: 0, ...payload, id: newBanner.id ?? Date.now() })
      showToast('배너가 추가되었습니다.')
    }
    closeModal()
  } catch {
    showToast('저장 중 오류가 발생했습니다.', 'error')
  } finally {
    saving.value = false
  }
}

async function toggleStatus(banner) {
  const newStatus = banner.status === 'active' ? 'inactive' : 'active'
  try {
    await axios.put(`/api/admin/banners/${banner.id}`, { ...banner, status: newStatus })
  } catch { /* optimistic */ }
  banner.status = newStatus
  showToast(newStatus === 'active' ? '배너가 활성화되었습니다.' : '배너가 비활성화되었습니다.')
}

async function deleteBanner(banner) {
  if (!confirm(`"${banner.name}" 배너를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/banners/${banner.id}`)
  } catch { /* allow local delete */ }
  banners.value = banners.value.filter(b => b.id !== banner.id)
  showToast('배너가 삭제되었습니다.')
}

async function savePopupContent(popup) {
  try {
    await axios.put(`/api/admin/banners/${popup.id}`, popup)
    showToast('팝업 내용이 저장되었습니다.')
  } catch {
    showToast('저장 중 오류가 발생했습니다.', 'error')
  }
}

onMounted(load)
</script>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(10px); }
</style>
