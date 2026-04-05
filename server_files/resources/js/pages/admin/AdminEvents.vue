<template>
  <div class="space-y-5">
    <!-- 헤더 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">이벤트 관리</h1>
        <p class="text-sm text-gray-500 mt-1">한인 커뮤니티 이벤트를 관리합니다</p>
      </div>
      <button @click="openCreateModal" class="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
        <span class="text-lg font-bold">+</span> 이벤트 등록
      </button>
    </div>

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">전체 이벤트</p>
        <p class="text-3xl font-bold text-gray-800 mt-1">{{ stats.total }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">진행중</p>
        <p class="text-3xl font-bold text-green-600 mt-1">{{ stats.ongoing }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">예정</p>
        <p class="text-3xl font-bold text-blue-600 mt-1">{{ stats.upcoming }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">종료</p>
        <p class="text-3xl font-bold text-gray-400 mt-1">{{ stats.ended }}</p>
      </div>
    </div>

    <!-- 이벤트 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100 flex items-center justify-between">
        <h2 class="font-semibold text-gray-800">이벤트 목록</h2>
        <div class="flex gap-2">
          <select v-model="filterStatus" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">전체 상태</option>
            <option value="진행중">진행중</option>
            <option value="예정">예정</option>
            <option value="종료">종료</option>
          </select>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-500 uppercase text-xs">
            <tr>
              <th class="px-4 py-3 text-left">이벤트명</th>
              <th class="px-4 py-3 text-left">날짜</th>
              <th class="px-4 py-3 text-left">장소</th>
              <th class="px-4 py-3 text-center">신청/최대</th>
              <th class="px-4 py-3 text-left">주최자</th>
              <th class="px-4 py-3 text-center">상태</th>
              <th class="px-4 py-3 text-center">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="event in filteredEvents" :key="event.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div class="font-medium text-gray-900">{{ event.name }}</div>
                <div class="text-xs text-gray-400">{{ event.category }}</div>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ event.date }}</td>
              <td class="px-4 py-3 text-gray-600">{{ event.location }}</td>
              <td class="px-4 py-3 text-center">
                <span class="font-medium">{{ event.registered }}</span>
                <span class="text-gray-400"> / {{ event.maxCapacity }}</span>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ event.organizer }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="statusBadge(event.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ event.status }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-center gap-2">
                  <button @click="openDetail(event)" class="text-blue-600 hover:text-blue-800 text-xs font-medium">상세</button>
                  <button @click="openEditModal(event)" class="text-yellow-600 hover:text-yellow-800 text-xs font-medium">수정</button>
                  <button @click="deleteEvent(event.id)" class="text-red-500 hover:text-red-700 text-xs font-medium">삭제</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 생성/수정 모달 -->
    <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-100 flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">{{ isEditing ? '이벤트 수정' : '이벤트 등록' }}</h2>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">이벤트명 *</label>
            <input v-model="form.name" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="이벤트명을 입력하세요" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">날짜 *</label>
              <input v-model="form.date" type="date" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">최대 인원</label>
              <input v-model.number="form.maxCapacity" type="number" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="0" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">장소 *</label>
            <input v-model="form.location" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="장소를 입력하세요" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">카테고리</label>
            <select v-model="form.category" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">카테고리 선택</option>
              <option>문화</option>
              <option>음악</option>
              <option>교육</option>
              <option>취업</option>
              <option>요리</option>
              <option>스포츠</option>
              <option>기타</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">이미지 URL</label>
            <input v-model="form.imageUrl" type="url" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="https://..." />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">설명</label>
            <textarea v-model="form.description" rows="3" class="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="이벤트 설명을 입력하세요"></textarea>
          </div>
        </div>
        <div class="p-6 border-t border-gray-100 flex gap-3">
          <button @click="closeModal" class="flex-1 border border-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-50 transition">취소</button>
          <button @click="saveEvent" class="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">{{ isEditing ? '수정 완료' : '등록하기' }}</button>
        </div>
      </div>
    </div>

    <!-- 상세/참가자 모달 -->
    <div v-if="showDetail" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        <div class="p-6 border-b border-gray-100 flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">이벤트 상세</h2>
          <button @click="showDetail = false" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div v-if="selectedEvent" class="p-6 space-y-4">
          <div class="bg-blue-50 rounded-xl p-4">
            <h3 class="font-bold text-blue-900 text-lg">{{ selectedEvent.name }}</h3>
            <p class="text-blue-700 text-sm mt-1">{{ selectedEvent.date }} · {{ selectedEvent.location }}</p>
            <p class="text-blue-600 text-sm mt-2">{{ selectedEvent.description }}</p>
          </div>
          <div class="grid grid-cols-3 gap-3 text-center">
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500">신청자</p>
              <p class="text-xl font-bold text-gray-800">{{ selectedEvent.registered }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500">최대 인원</p>
              <p class="text-xl font-bold text-gray-800">{{ selectedEvent.maxCapacity }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-500">주최자</p>
              <p class="text-sm font-bold text-gray-800">{{ selectedEvent.organizer }}</p>
            </div>
          </div>
          <div>
            <h4 class="font-semibold text-gray-800 mb-3">참가자 목록</h4>
            <div class="space-y-2">
              <div v-for="p in selectedEvent.participants" :key="p.id" class="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-2">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 font-bold text-xs">
                    {{ p.name[0] }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-800">{{ p.name }}</p>
                    <p class="text-xs text-gray-400">{{ p.email }}</p>
                  </div>
                </div>
                <span class="text-xs text-gray-400">{{ p.registeredAt }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import axios from 'axios'

const filterStatus = ref('')
const showModal = ref(false)
const showDetail = ref(false)
const isEditing = ref(false)
const selectedEvent = ref(null)

const form = reactive({
  id: null,
  name: '',
  date: '',
  location: '',
  description: '',
  maxCapacity: 0,
  imageUrl: '',
  category: ''
})

const events = ref([
  {
    id: 1,
    name: '한인 문화 축제',
    date: '2026-04-15',
    location: 'Koreatown Plaza, LA',
    description: '한인 전통 문화를 즐기는 봄 축제입니다. 전통 공연, 음식, 놀이 등 다양한 프로그램이 진행됩니다.',
    registered: 142,
    maxCapacity: 300,
    organizer: '김한국',
    category: '문화',
    status: '예정',
    participants: [
      { id: 1, name: '이지영', email: 'jiyoung@email.com', registeredAt: '2026-03-20' },
      { id: 2, name: '박민준', email: 'minjun@email.com', registeredAt: '2026-03-21' },
      { id: 3, name: '최수진', email: 'sujin@email.com', registeredAt: '2026-03-22' },
    ]
  },
  {
    id: 2,
    name: '한인 음악 콘서트',
    date: '2026-03-28',
    location: 'The Wiltern, LA',
    description: '한인 뮤지션들이 함께하는 K-Pop & 인디 음악 콘서트.',
    registered: 280,
    maxCapacity: 280,
    organizer: '박음악',
    category: '음악',
    status: '진행중',
    participants: [
      { id: 1, name: '홍길동', email: 'gildong@email.com', registeredAt: '2026-03-10' },
      { id: 2, name: '임채원', email: 'chaewon@email.com', registeredAt: '2026-03-11' },
    ]
  },
  {
    id: 3,
    name: '한영 언어 교환 모임',
    date: '2026-04-05',
    location: 'Cafe Bora, Koreatown',
    description: '한국어와 영어를 배우고 싶은 분들을 위한 언어 교환 모임입니다.',
    registered: 24,
    maxCapacity: 40,
    organizer: '정언어',
    category: '교육',
    status: '예정',
    participants: [
      { id: 1, name: '김어학', email: 'kim@email.com', registeredAt: '2026-03-25' },
    ]
  },
  {
    id: 4,
    name: '한인 취업 박람회',
    date: '2026-03-10',
    location: 'LA Convention Center',
    description: '한인 기업 및 미국 대기업들이 참가하는 취업 박람회.',
    registered: 520,
    maxCapacity: 500,
    organizer: '취업센터',
    category: '취업',
    status: '종료',
    participants: [
      { id: 1, name: '이취업', email: 'lee@email.com', registeredAt: '2026-03-01' },
      { id: 2, name: '박구직', email: 'park@email.com', registeredAt: '2026-03-02' },
    ]
  },
  {
    id: 5,
    name: '한식 요리 교실',
    date: '2026-04-20',
    location: 'Seoul Kitchen Studio, LA',
    description: '전통 한식 요리를 배우는 클래스. 김치, 된장찌개, 불고기 만들기.',
    registered: 12,
    maxCapacity: 20,
    organizer: '요리사 최',
    category: '요리',
    status: '예정',
    participants: [
      { id: 1, name: '요리초보', email: 'cook@email.com', registeredAt: '2026-03-26' },
    ]
  }
])

const stats = computed(() => ({
  total: events.value.length,
  ongoing: events.value.filter(e => e.status === '진행중').length,
  upcoming: events.value.filter(e => e.status === '예정').length,
  ended: events.value.filter(e => e.status === '종료').length
}))

const filteredEvents = computed(() => {
  if (!filterStatus.value) return events.value
  return events.value.filter(e => e.status === filterStatus.value)
})

function statusBadge(status) {
  const map = {
    '진행중': 'bg-green-100 text-green-700',
    '예정': 'bg-blue-100 text-blue-700',
    '종료': 'bg-gray-100 text-gray-500'
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

function openCreateModal() {
  isEditing.value = false
  Object.assign(form, { id: null, name: '', date: '', location: '', description: '', maxCapacity: 0, imageUrl: '', category: '' })
  showModal.value = true
}

function openEditModal(event) {
  isEditing.value = true
  Object.assign(form, { ...event })
  showModal.value = true
}

function closeModal() {
  showModal.value = false
}

function openDetail(event) {
  selectedEvent.value = event
  showDetail.value = true
}

async function saveEvent() {
  try {
    if (isEditing.value) {
      await axios.put(`/api/admin/events/${form.id}`, form)
      const idx = events.value.findIndex(e => e.id === form.id)
      if (idx !== -1) events.value[idx] = { ...events.value[idx], ...form }
    } else {
      const res = await axios.post('/api/admin/events', form)
      events.value.unshift({ ...form, id: res.data?.id || Date.now(), registered: 0, status: '예정', organizer: '관리자', participants: [] })
    }
    closeModal()
  } catch {
    // 데모 모드: API 없을 경우 로컬 상태만 업데이트
    if (isEditing.value) {
      const idx = events.value.findIndex(e => e.id === form.id)
      if (idx !== -1) events.value[idx] = { ...events.value[idx], ...form }
    } else {
      events.value.unshift({ ...form, id: Date.now(), registered: 0, status: '예정', organizer: '관리자', participants: [] })
    }
    closeModal()
  }
}

async function deleteEvent(id) {
  if (!confirm('이 이벤트를 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/admin/events/${id}`)
  } catch {}
  events.value = events.value.filter(e => e.id !== id)
}
</script>
