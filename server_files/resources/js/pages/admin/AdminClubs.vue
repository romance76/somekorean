<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-blue-600">{{ stats.total }}</div>
        <div class="text-xs text-gray-500 mt-0.5">전체 동호회</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-green-500">{{ stats.active }}</div>
        <div class="text-xs text-gray-500 mt-0.5">활성</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-orange-500">{{ stats.newThisMonth }}</div>
        <div class="text-xs text-gray-500 mt-0.5">이번달 신규</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-purple-500">{{ stats.totalMembers }}</div>
        <div class="text-xs text-gray-500 mt-0.5">총 회원수</div>
      </div>
    </div>

    <!-- 필터 & 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <!-- 필터 -->
      <div class="p-4 border-b border-gray-100">
        <div class="flex flex-col sm:flex-row gap-3">
          <input v-model="search" placeholder="동호회명 / 관리자 검색"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 flex-1" />
          <select v-model="filterCategory"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 카테고리</option>
            <option value="운동">운동</option>
            <option value="음악">음악</option>
            <option value="요리">요리</option>
            <option value="독서">독서</option>
            <option value="여행">여행</option>
            <option value="사진">사진</option>
            <option value="기타">기타</option>
          </select>
          <button @click="resetFilters"
            class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-semibold transition">
            초기화
          </button>
        </div>
      </div>

      <!-- 테이블 -->
      <div class="overflow-x-auto">
        <div v-if="filteredClubs.length === 0" class="text-center py-12 text-gray-400 text-sm">
          검색 결과가 없습니다.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">동호회명</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">카테고리</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">회원수</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">최근 활동</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">관리자</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">생성일</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="club in filteredClubs" :key="club.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div :class="['w-9 h-9 rounded-xl flex items-center justify-center text-lg flex-shrink-0', categoryBg(club.category)]">
                    {{ categoryIcon(club.category) }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-800">{{ club.name }}</div>
                    <div class="text-[10px] text-gray-400 truncate max-w-[160px]">{{ club.description }}</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', categoryClass(club.category)]">
                  {{ club.category }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span class="font-bold text-blue-600">{{ club.members }}</span>
                <span class="text-xs text-gray-400">명</span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden lg:table-cell">{{ club.last_activity }}</td>
              <td class="px-4 py-3 text-xs text-gray-600 hidden sm:table-cell">{{ club.manager }}</td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden lg:table-cell">{{ club.created_at }}</td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openDetail(club)"
                    class="text-[11px] bg-blue-50 hover:bg-blue-100 text-blue-600 px-2.5 py-1 rounded-lg transition font-medium">
                    상세
                  </button>
                  <button @click="openNotice(club)"
                    class="text-[11px] bg-green-50 hover:bg-green-100 text-green-600 px-2.5 py-1 rounded-lg transition font-medium hidden sm:block">
                    공지
                  </button>
                  <button @click="confirmDelete(club)"
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
    <div v-if="selectedClub" class="fixed inset-0 z-50 flex items-center justify-center p-4"
      style="background:rgba(0,0,0,0.45)" @click.self="selectedClub = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <!-- 모달 헤더 -->
        <div class="flex items-start justify-between p-5 border-b border-gray-100">
          <div class="flex items-center gap-3">
            <div :class="['w-12 h-12 rounded-2xl flex items-center justify-center text-2xl', categoryBg(selectedClub.category)]">
              {{ categoryIcon(selectedClub.category) }}
            </div>
            <div>
              <h2 class="text-lg font-bold text-gray-900">{{ selectedClub.name }}</h2>
              <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', categoryClass(selectedClub.category)]">
                {{ selectedClub.category }}
              </span>
            </div>
          </div>
          <button @click="selectedClub = null"
            class="text-gray-400 hover:text-gray-600 text-xl font-bold leading-none ml-4">×</button>
        </div>

        <!-- 모달 내용 -->
        <div class="p-5 space-y-5">
          <!-- 기본 정보 -->
          <div class="grid grid-cols-3 gap-3">
            <div class="bg-gray-50 rounded-xl p-3 text-center">
              <div class="text-2xl font-black text-blue-600">{{ selectedClub.members }}</div>
              <div class="text-[10px] text-gray-500 mt-0.5">회원수</div>
            </div>
            <div class="bg-gray-50 rounded-xl p-3 text-center">
              <div class="text-sm font-bold text-gray-700">{{ selectedClub.last_activity }}</div>
              <div class="text-[10px] text-gray-500 mt-0.5">최근 활동</div>
            </div>
            <div class="bg-gray-50 rounded-xl p-3 text-center">
              <div class="text-sm font-bold text-gray-700">{{ selectedClub.created_at }}</div>
              <div class="text-[10px] text-gray-500 mt-0.5">생성일</div>
            </div>
          </div>

          <!-- 동호회 설명 -->
          <div>
            <div class="text-xs font-semibold text-gray-500 mb-2">동호회 소개</div>
            <div class="bg-gray-50 rounded-xl p-3 text-sm text-gray-700 leading-relaxed">
              {{ selectedClub.description }}
            </div>
          </div>

          <!-- 회원 목록 -->
          <div>
            <div class="text-xs font-semibold text-gray-500 mb-2">회원 목록 (최근 가입순)</div>
            <div class="space-y-2">
              <div v-for="i in Math.min(4, selectedClub.members)" :key="i"
                class="flex items-center gap-3 bg-gray-50 rounded-xl p-2.5">
                <div :class="['w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold', memberColor(i)]">
                  {{ memberNames[i - 1]?.charAt(0) || '회' }}
                </div>
                <div class="flex-1">
                  <div class="text-xs font-medium text-gray-700">{{ memberNames[i - 1] || `회원 ${i}` }}</div>
                  <div class="text-[10px] text-gray-400">가입일: 2026-03-{{ String(i + 10).padStart(2,'0') }}</div>
                </div>
                <span v-if="i === 1" class="text-[10px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-semibold">관리자</span>
                <span v-else class="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">일반</span>
              </div>
              <div v-if="selectedClub.members > 4"
                class="text-center text-xs text-gray-400 py-1">
                + {{ selectedClub.members - 4 }}명 더 있음
              </div>
            </div>
          </div>

          <!-- 활동 내역 -->
          <div>
            <div class="text-xs font-semibold text-gray-500 mb-2">최근 활동 내역</div>
            <div class="space-y-2">
              <div v-for="(activity, idx) in clubActivities" :key="idx"
                class="flex items-start gap-3">
                <div class="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 flex-shrink-0"></div>
                <div>
                  <div class="text-xs text-gray-700">{{ activity.text }}</div>
                  <div class="text-[10px] text-gray-400">{{ activity.date }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 관리자 변경 -->
          <div class="border-t border-gray-100 pt-4">
            <div class="text-xs font-semibold text-gray-500 mb-2">관리자 정보 및 변경</div>
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-blue-100 flex items-center justify-center text-sm font-bold text-blue-600">
                {{ selectedClub.manager.charAt(0) }}
              </div>
              <div class="flex-1">
                <div class="text-sm font-semibold text-gray-800">{{ selectedClub.manager }}</div>
                <div class="text-[10px] text-gray-400">현재 관리자</div>
              </div>
              <button class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1.5 rounded-lg font-semibold transition">
                관리자 변경
              </button>
            </div>
          </div>
        </div>

        <!-- 모달 푸터 -->
        <div class="flex justify-end gap-2 px-5 pb-5">
          <button @click="deactivateClub(selectedClub); selectedClub = null"
            class="bg-yellow-50 hover:bg-yellow-100 text-yellow-700 px-4 py-2 rounded-lg text-sm font-semibold transition">
            비활성화
          </button>
          <button @click="openNotice(selectedClub); selectedClub = null"
            class="bg-green-50 hover:bg-green-100 text-green-600 px-4 py-2 rounded-lg text-sm font-semibold transition">
            공지 발송
          </button>
          <button @click="confirmDelete(selectedClub); selectedClub = null"
            class="bg-red-50 hover:bg-red-100 text-red-500 px-4 py-2 rounded-lg text-sm font-semibold transition">
            삭제
          </button>
          <button @click="selectedClub = null"
            class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-semibold transition">
            닫기
          </button>
        </div>
      </div>
    </div>

    <!-- 공지 발송 모달 -->
    <div v-if="noticeClub" class="fixed inset-0 z-50 flex items-center justify-center p-4"
      style="background:rgba(0,0,0,0.45)" @click.self="noticeClub = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">
        <h3 class="text-base font-bold text-gray-900 mb-1">공지 발송</h3>
        <p class="text-sm text-gray-500 mb-4">
          <span class="font-semibold text-gray-700">{{ noticeClub.name }}</span> 회원 {{ noticeClub.members }}명에게 공지를 발송합니다.
        </p>
        <textarea v-model="noticeText" rows="4" placeholder="공지 내용을 입력하세요..."
          class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 resize-none mb-4">
        </textarea>
        <div class="flex gap-2">
          <button @click="noticeClub = null; noticeText = ''"
            class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 py-2.5 rounded-xl text-sm font-semibold transition">
            취소
          </button>
          <button @click="sendNotice"
            class="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-2.5 rounded-xl text-sm font-semibold transition">
            발송
          </button>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4"
      style="background:rgba(0,0,0,0.45)" @click.self="deleteTarget = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6 text-center">
        <div class="text-4xl mb-3">🗑️</div>
        <h3 class="text-base font-bold text-gray-900 mb-1">동호회를 삭제하시겠습니까?</h3>
        <p class="text-sm text-gray-500 mb-5">
          <span class="font-semibold text-gray-700">{{ deleteTarget.name }}</span> 동호회가 영구 삭제됩니다.
          소속 회원 {{ deleteTarget.members }}명의 데이터도 함께 삭제됩니다.
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

const dummyClubs = [
  { id:1, name:'LA 한인 풋살팀', category:'운동', members:24, manager:'김민준', last_activity:'2026-03-28', description:'매주 토요일 풋살 모임', created_at:'2025-08-01' },
  { id:2, name:'K-요리 동호회', category:'요리', members:18, manager:'박서연', last_activity:'2026-03-25', description:'한국 요리 함께 배우기', created_at:'2025-09-15' },
  { id:3, name:'한인 독서 모임', category:'독서', members:12, manager:'이하은', last_activity:'2026-03-20', description:'월 2회 독서 토론', created_at:'2025-10-01' },
  { id:4, name:'LA 사진 클럽', category:'사진', members:35, manager:'정우진', last_activity:'2026-03-27', description:'주말 사진 출사 및 품평', created_at:'2025-07-10' },
  { id:5, name:'한인 기타 앙상블', category:'음악', members:8, manager:'강이서', last_activity:'2026-03-22', description:'클래식 기타 함께 연주', created_at:'2025-11-01' },
  { id:6, name:'캘리포니아 여행 클럽', category:'여행', members:42, manager:'한준우', last_activity:'2026-03-26', description:'CA 명소 함께 탐방', created_at:'2025-06-01' },
]

const clubs = ref([...dummyClubs])
const search = ref('')
const filterCategory = ref('')
const selectedClub = ref(null)
const deleteTarget = ref(null)
const noticeClub = ref(null)
const noticeText = ref('')

const memberNames = ['김민준', '박서연', '이하은', '정우진']

const clubActivities = computed(() => [
  { text: '정기 모임 개최', date: selectedClub.value?.last_activity || '' },
  { text: '새 회원 2명 가입', date: '2026-03-25' },
  { text: '사진 공모전 결과 공지', date: '2026-03-20' },
  { text: '3월 일정 안내 공지 발송', date: '2026-03-01' },
])

const stats = computed(() => ({
  total: clubs.value.length,
  active: clubs.value.length,
  newThisMonth: clubs.value.filter(c => c.created_at >= '2026-03-01').length,
  totalMembers: clubs.value.reduce((sum, c) => sum + c.members, 0),
}))

const filteredClubs = computed(() => {
  return clubs.value.filter(c => {
    const matchSearch = !search.value ||
      c.name.toLowerCase().includes(search.value.toLowerCase()) ||
      c.manager.toLowerCase().includes(search.value.toLowerCase())
    const matchCat = !filterCategory.value || c.category === filterCategory.value
    return matchSearch && matchCat
  })
})

function categoryClass(cat) {
  const map = {
    '운동': 'bg-green-50 text-green-600',
    '음악': 'bg-purple-50 text-purple-600',
    '요리': 'bg-orange-50 text-orange-600',
    '독서': 'bg-blue-50 text-blue-600',
    '여행': 'bg-teal-50 text-teal-600',
    '사진': 'bg-pink-50 text-pink-600',
    '기타': 'bg-gray-100 text-gray-500',
  }
  return map[cat] || 'bg-gray-100 text-gray-500'
}

function categoryBg(cat) {
  const map = {
    '운동': 'bg-green-50',
    '음악': 'bg-purple-50',
    '요리': 'bg-orange-50',
    '독서': 'bg-blue-50',
    '여행': 'bg-teal-50',
    '사진': 'bg-pink-50',
    '기타': 'bg-gray-100',
  }
  return map[cat] || 'bg-gray-100'
}

function categoryIcon(cat) {
  const map = {
    '운동': '⚽',
    '음악': '🎸',
    '요리': '🍳',
    '독서': '📚',
    '여행': '✈️',
    '사진': '📷',
    '기타': '🌟',
  }
  return map[cat] || '🌟'
}

function memberColor(i) {
  const colors = ['bg-blue-100 text-blue-600', 'bg-green-100 text-green-600', 'bg-purple-100 text-purple-600', 'bg-orange-100 text-orange-600']
  return colors[(i - 1) % colors.length]
}

function openDetail(club) {
  selectedClub.value = club
}

function openNotice(club) {
  noticeClub.value = club
  noticeText.value = ''
}

function sendNotice() {
  if (!noticeText.value.trim()) return
  alert(`"${noticeClub.value.name}" 회원 ${noticeClub.value.members}명에게 공지가 발송되었습니다.`)
  noticeClub.value = null
  noticeText.value = ''
}

function deactivateClub(club) {
  alert(`"${club.name}" 동호회가 비활성화되었습니다.`)
}

function confirmDelete(club) {
  deleteTarget.value = club
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await axios.delete(`/api/admin/clubs/${deleteTarget.value.id}`)
  } catch (e) {
    // demo: proceed with local deletion
  }
  clubs.value = clubs.value.filter(c => c.id !== deleteTarget.value.id)
  deleteTarget.value = null
}

function resetFilters() {
  search.value = ''
  filterCategory.value = ''
}

async function loadClubs() {
  try {
    const res = await axios.get('/api/admin/clubs')
    if (res.data && res.data.length) clubs.value = res.data
  } catch (e) {
    // use dummy data
  }
}

onMounted(() => {
  loadClubs()
})
</script>
