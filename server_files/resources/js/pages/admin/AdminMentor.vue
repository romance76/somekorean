<template>
  <div class="space-y-5">
    <!-- 헤더 -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">멘토링 관리</h1>
      <p class="text-sm text-gray-500 mt-1">멘토 심사, 멘토링 요청, 세션 현황을 관리합니다</p>
    </div>

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">전체 멘토</p>
        <p class="text-3xl font-bold text-gray-800 mt-1">{{ stats.totalMentors }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">활성 멘토</p>
        <p class="text-3xl font-bold text-green-600 mt-1">{{ stats.activeMentors }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">멘토링 요청</p>
        <p class="text-3xl font-bold text-blue-600 mt-1">{{ stats.pendingRequests }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">완료된 세션</p>
        <p class="text-3xl font-bold text-purple-600 mt-1">{{ stats.completedSessions }}</p>
      </div>
    </div>

    <!-- 멘토링 설정 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h2 class="font-semibold text-gray-800 mb-4">멘토링 서비스 설정</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <p class="font-medium text-gray-800 text-sm">멘토 승인제</p>
            <p class="text-xs text-gray-400 mt-0.5">신규 멘토 등록 시 관리자 승인 필요</p>
          </div>
          <button @click="settings.requireApproval = !settings.requireApproval"
            :class="settings.requireApproval ? 'bg-green-500' : 'bg-gray-300'"
            class="relative inline-flex w-10 h-6 rounded-full transition-colors duration-200 flex-shrink-0">
            <span :class="settings.requireApproval ? 'translate-x-4' : 'translate-x-0'" class="inline-block w-5 h-5 mt-0.5 ml-0.5 bg-white rounded-full shadow transform transition-transform duration-200"></span>
          </button>
        </div>
        <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div>
            <p class="font-medium text-gray-800 text-sm">멘토당 최대 멘티수</p>
            <p class="text-xs text-gray-400 mt-0.5">현재: {{ settings.maxMenteesPerMentor }}명</p>
          </div>
          <input v-model.number="settings.maxMenteesPerMentor" type="number" min="1" max="20"
            class="w-16 text-center border border-gray-200 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
      </div>
      <div class="mt-4 flex justify-end">
        <button @click="saveSettings" class="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">설정 저장</button>
      </div>
    </div>

    <!-- 멘토 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100 flex items-center justify-between">
        <h2 class="font-semibold text-gray-800">멘토 목록</h2>
        <div class="flex gap-2">
          <select v-model="filterField" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">전체 분야</option>
            <option>IT/개발</option>
            <option>비즈니스</option>
            <option>의료/헬스케어</option>
            <option>법률</option>
            <option>교육</option>
          </select>
          <select v-model="filterActive" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">전체</option>
            <option value="true">활성</option>
            <option value="false">정지</option>
          </select>
        </div>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-500 uppercase text-xs">
            <tr>
              <th class="px-4 py-3 text-left">이름</th>
              <th class="px-4 py-3 text-left">전문분야</th>
              <th class="px-4 py-3 text-left">언어</th>
              <th class="px-4 py-3 text-center">상태</th>
              <th class="px-4 py-3 text-center">평점</th>
              <th class="px-4 py-3 text-center">완료 세션</th>
              <th class="px-4 py-3 text-center">현재 멘티</th>
              <th class="px-4 py-3 text-center">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="mentor in filteredMentors" :key="mentor.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-indigo-200 flex items-center justify-center text-indigo-700 font-bold text-xs">
                    {{ mentor.name[0] }}
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ mentor.name }}</p>
                    <p class="text-xs text-gray-400">{{ mentor.location }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3">
                <span class="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded text-xs font-medium">{{ mentor.field }}</span>
              </td>
              <td class="px-4 py-3 text-gray-600 text-xs">{{ mentor.languages.join(', ') }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="mentor.active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'" class="px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ mentor.active ? '활성' : '정지' }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="text-yellow-500">★</span>
                <span class="font-medium text-gray-800 ml-1">{{ mentor.rating }}</span>
              </td>
              <td class="px-4 py-3 text-center font-medium text-gray-700">{{ mentor.completedSessions }}</td>
              <td class="px-4 py-3 text-center">
                <span class="text-gray-700">{{ mentor.currentMentees }}</span>
                <span class="text-gray-400"> / {{ settings.maxMenteesPerMentor }}</span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-center gap-1">
                  <button @click="openMentorDetail(mentor)" class="text-blue-600 hover:text-blue-800 text-xs font-medium px-1">상세</button>
                  <button @click="toggleMentorActive(mentor)" class="text-xs font-medium px-1"
                    :class="mentor.active ? 'text-yellow-600 hover:text-yellow-800' : 'text-green-600 hover:text-green-800'">
                    {{ mentor.active ? '정지' : '활성화' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 멘토링 요청 목록 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-800">멘토링 요청 ({{ pendingRequests.length }}건 대기중)</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-500 uppercase text-xs">
            <tr>
              <th class="px-4 py-3 text-left">요청자 (멘티)</th>
              <th class="px-4 py-3 text-left">멘토</th>
              <th class="px-4 py-3 text-left">주제</th>
              <th class="px-4 py-3 text-center">상태</th>
              <th class="px-4 py-3 text-left">요청일</th>
              <th class="px-4 py-3 text-center">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="req in mentorRequests" :key="req.id"
              :class="req.status === '대기중' ? 'bg-yellow-50' : 'hover:bg-gray-50'"
              class="transition">
              <td class="px-4 py-3 font-medium text-gray-900">{{ req.mentee }}</td>
              <td class="px-4 py-3 text-gray-700">{{ req.mentor }}</td>
              <td class="px-4 py-3 text-gray-600">{{ req.topic }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="reqStatusBadge(req.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">{{ req.status }}</span>
              </td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ req.date }}</td>
              <td class="px-4 py-3">
                <div v-if="req.status === '대기중'" class="flex items-center justify-center gap-2">
                  <button @click="approveRequest(req.id)" class="text-xs bg-green-500 text-white px-3 py-1 rounded-lg hover:bg-green-600 transition">승인</button>
                  <button @click="rejectRequest(req.id)" class="text-xs bg-red-400 text-white px-3 py-1 rounded-lg hover:bg-red-500 transition">거절</button>
                </div>
                <span v-else class="block text-center text-gray-300 text-xs">—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 멘토 상세 모달 -->
    <div v-if="showDetail" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4">
        <div class="p-6 border-b border-gray-100 flex items-center justify-between">
          <h2 class="text-lg font-bold text-gray-900">멘토 상세 정보</h2>
          <button @click="showDetail = false" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div v-if="selectedMentor" class="p-6 space-y-4">
          <div class="flex items-center gap-4">
            <div class="w-14 h-14 rounded-full bg-indigo-200 flex items-center justify-center text-indigo-700 font-bold text-xl">
              {{ selectedMentor.name[0] }}
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">{{ selectedMentor.name }}</h3>
              <p class="text-sm text-gray-500">{{ selectedMentor.location }} · {{ selectedMentor.field }}</p>
              <div class="flex items-center gap-1 mt-0.5">
                <span class="text-yellow-400 text-sm">★</span>
                <span class="text-sm font-medium text-gray-700">{{ selectedMentor.rating }}</span>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-3 gap-3 text-center">
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-400">완료 세션</p>
              <p class="text-xl font-bold text-gray-800">{{ selectedMentor.completedSessions }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-400">현재 멘티</p>
              <p class="text-xl font-bold text-gray-800">{{ selectedMentor.currentMentees }}</p>
            </div>
            <div class="bg-gray-50 rounded-lg p-3">
              <p class="text-xs text-gray-400">상태</p>
              <p class="text-sm font-bold" :class="selectedMentor.active ? 'text-green-600' : 'text-red-500'">{{ selectedMentor.active ? '활성' : '정지' }}</p>
            </div>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-700 mb-1">언어</p>
            <div class="flex gap-2 flex-wrap">
              <span v-for="lang in selectedMentor.languages" :key="lang" class="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs">{{ lang }}</span>
            </div>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-700 mb-1">소개</p>
            <p class="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">{{ selectedMentor.bio }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import axios from 'axios'

const filterField = ref('')
const filterActive = ref('')
const showDetail = ref(false)
const selectedMentor = ref(null)

const settings = reactive({
  requireApproval: true,
  maxMenteesPerMentor: 5
})

const stats = ref({
  totalMentors: 5,
  activeMentors: 4,
  pendingRequests: 2,
  completedSessions: 148
})

const mentors = ref([
  {
    id: 1,
    name: '김개발',
    field: 'IT/개발',
    location: 'LA, CA',
    languages: ['한국어', 'English'],
    active: true,
    rating: 4.9,
    completedSessions: 52,
    currentMentees: 3,
    bio: '10년 경력의 풀스택 개발자로 스타트업 창업 경험 보유. JavaScript, Python, AWS 전문. 미국 IT 취업 준비생을 돕고 있습니다.'
  },
  {
    id: 2,
    name: '이변호사',
    field: '법률',
    location: 'NY, NY',
    languages: ['한국어', 'English'],
    active: true,
    rating: 4.7,
    completedSessions: 38,
    currentMentees: 2,
    bio: '미국 변호사 (NY/CA Bar). 이민법, 비즈니스법 전문. 한인 이민자들의 법적 문제 해결을 위한 멘토링을 제공합니다.'
  },
  {
    id: 3,
    name: '박교수',
    field: '교육',
    location: 'Boston, MA',
    languages: ['한국어', 'English', '日本語'],
    active: true,
    rating: 4.8,
    completedSessions: 29,
    currentMentees: 4,
    bio: '미국 명문대 교수. 대학원 입시, 연구 경력 개발, 장학금 신청 등을 코칭합니다.'
  },
  {
    id: 4,
    name: '최의사',
    field: '의료/헬스케어',
    location: 'LA, CA',
    languages: ['한국어', 'English'],
    active: false,
    rating: 4.6,
    completedSessions: 18,
    currentMentees: 0,
    bio: '미국 공립병원 내과 전문의. 의대 입시, USMLE, 레지던시 매칭 등 의료 커리어 멘토링 전문.'
  },
  {
    id: 5,
    name: '정사업가',
    field: '비즈니스',
    location: 'SF, CA',
    languages: ['한국어', 'English', '中文'],
    active: true,
    rating: 4.5,
    completedSessions: 11,
    currentMentees: 2,
    bio: '실리콘밸리 스타트업 창업자 (Series A). 사업 계획, 투자 유치, 미국 시장 진출 전략 멘토링.'
  }
])

const mentorRequests = ref([
  { id: 1, mentee: '홍길동', mentor: '김개발', topic: '미국 IT 취업 준비 및 이력서 작성', status: '대기중', date: '2026-03-28' },
  { id: 2, mentee: '이민자', mentor: '이변호사', topic: 'H1B 비자 신청 절차 문의', status: '승인됨', date: '2026-03-26' },
  { id: 3, mentee: '김유학생', mentor: '박교수', topic: '박사과정 지원 및 연구 계획서', status: '대기중', date: '2026-03-25' },
  { id: 4, mentee: '박창업', mentor: '정사업가', topic: '스타트업 사업계획서 피드백', status: '완료', date: '2026-03-20' }
])

const filteredMentors = computed(() => {
  let list = mentors.value
  if (filterField.value) list = list.filter(m => m.field === filterField.value)
  if (filterActive.value !== '') list = list.filter(m => String(m.active) === filterActive.value)
  return list
})

const pendingRequests = computed(() => mentorRequests.value.filter(r => r.status === '대기중'))

function reqStatusBadge(status) {
  const map = {
    '대기중': 'bg-yellow-100 text-yellow-700',
    '승인됨': 'bg-green-100 text-green-700',
    '거절됨': 'bg-red-100 text-red-700',
    '완료': 'bg-blue-100 text-blue-700'
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

function openMentorDetail(mentor) {
  selectedMentor.value = mentor
  showDetail.value = true
}

function toggleMentorActive(mentor) {
  mentor.active = !mentor.active
}

async function approveRequest(id) {
  try { await axios.patch(`/api/admin/mentor/requests/${id}/approve`) } catch {}
  const req = mentorRequests.value.find(r => r.id === id)
  if (req) req.status = '승인됨'
}

async function rejectRequest(id) {
  try { await axios.patch(`/api/admin/mentor/requests/${id}/reject`) } catch {}
  const req = mentorRequests.value.find(r => r.id === id)
  if (req) req.status = '거절됨'
}

async function saveSettings() {
  try {
    await axios.post('/api/admin/mentor/settings', settings)
  } catch {}
  alert('설정이 저장되었습니다.')
}
</script>
