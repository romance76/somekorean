<template>
  <div class="space-y-5">
    <!-- 헤더 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">숏츠 관리</h1>
        <p class="text-sm text-gray-500 mt-1">업로드된 숏츠 영상을 관리합니다</p>
      </div>
    </div>

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">전체 숏츠</p>
        <p class="text-3xl font-bold text-gray-800 mt-1">{{ stats.total }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">오늘 업로드</p>
        <p class="text-3xl font-bold text-blue-600 mt-1">{{ stats.todayUploads }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">총 조회수</p>
        <p class="text-3xl font-bold text-purple-600 mt-1">{{ formatNum(stats.totalViews) }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">신고된 영상</p>
        <p class="text-3xl font-bold text-red-500 mt-1">{{ stats.reported }}</p>
      </div>
    </div>

    <!-- 신고된 영상 섹션 -->
    <div v-if="reportedShorts.length > 0" class="bg-red-50 border border-red-200 rounded-xl overflow-hidden">
      <div class="p-4 border-b border-red-200 flex items-center gap-2">
        <span class="text-red-500 font-bold text-lg">⚠</span>
        <h2 class="font-semibold text-red-700">신고된 영상 ({{ reportedShorts.length }}건) — 즉시 검토 필요</h2>
      </div>
      <div class="divide-y divide-red-100">
        <div v-for="short in reportedShorts" :key="short.id" class="p-4 flex items-center gap-4">
          <div class="w-16 h-10 rounded-lg bg-red-200 flex items-center justify-center text-red-500 font-bold text-xs flex-shrink-0">
            영상
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-red-900 truncate">{{ short.title }}</p>
            <p class="text-xs text-red-500">업로더: {{ short.uploader }} · 신고 {{ short.reports }}건</p>
          </div>
          <div class="flex gap-2">
            <button @click="blindShort(short.id)" class="text-xs bg-yellow-500 text-white px-3 py-1 rounded-lg hover:bg-yellow-600 transition">블라인드</button>
            <button @click="deleteShort(short.id)" class="text-xs bg-red-500 text-white px-3 py-1 rounded-lg hover:bg-red-600 transition">삭제</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 필터 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div class="flex flex-wrap gap-3">
        <select v-model="filterCategory" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">전체 카테고리</option>
          <option>일상</option>
          <option>음식</option>
          <option>문화</option>
          <option>뷰티</option>
          <option>여행</option>
          <option>유머</option>
        </select>
        <select v-model="filterStatus" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">전체 상태</option>
          <option value="활성">활성</option>
          <option value="신고됨">신고됨</option>
          <option value="블라인드">블라인드</option>
          <option value="삭제됨">삭제됨</option>
        </select>
        <input v-model="searchQuery" type="text" placeholder="제목 또는 업로더 검색..." class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 w-52" />
      </div>
    </div>

    <!-- 숏츠 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-800">숏츠 목록 ({{ filteredShorts.length }}개)</h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-500 uppercase text-xs">
            <tr>
              <th class="px-4 py-3 text-left">제목 / 썸네일</th>
              <th class="px-4 py-3 text-left">업로더</th>
              <th class="px-4 py-3 text-center">조회수</th>
              <th class="px-4 py-3 text-center">좋아요</th>
              <th class="px-4 py-3 text-center">댓글</th>
              <th class="px-4 py-3 text-center">신고</th>
              <th class="px-4 py-3 text-left">업로드일</th>
              <th class="px-4 py-3 text-center">상태</th>
              <th class="px-4 py-3 text-center">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="short in filteredShorts" :key="short.id"
              :class="short.reports > 0 ? 'bg-red-50 hover:bg-red-100' : 'hover:bg-gray-50'"
              class="transition">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-14 h-9 rounded-lg flex-shrink-0 overflow-hidden"
                    :class="short.status === '블라인드' ? 'bg-gray-300' : 'bg-gradient-to-br from-purple-400 to-pink-400'">
                    <div class="w-full h-full flex items-center justify-center text-white text-xs font-bold">
                      {{ short.status === '블라인드' ? '🚫' : '▶' }}
                    </div>
                  </div>
                  <div>
                    <p class="font-medium text-gray-900 max-w-[150px] truncate">{{ short.title }}</p>
                    <p class="text-xs text-gray-400">{{ short.category }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ short.uploader }}</td>
              <td class="px-4 py-3 text-center text-gray-700 font-medium">{{ formatNum(short.views) }}</td>
              <td class="px-4 py-3 text-center text-pink-600 font-medium">{{ formatNum(short.likes) }}</td>
              <td class="px-4 py-3 text-center text-gray-600">{{ short.comments }}</td>
              <td class="px-4 py-3 text-center">
                <span v-if="short.reports > 0" class="text-red-600 font-bold">{{ short.reports }}</span>
                <span v-else class="text-gray-300">—</span>
              </td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ short.uploadedAt }}</td>
              <td class="px-4 py-3 text-center">
                <span :class="statusBadge(short.status)" class="px-2 py-1 rounded-full text-xs font-medium">
                  {{ short.status }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-center gap-1">
                  <button class="text-blue-600 hover:text-blue-800 text-xs font-medium px-1">보기</button>
                  <button @click="blindShort(short.id)" class="text-yellow-600 hover:text-yellow-800 text-xs font-medium px-1">블라인드</button>
                  <button @click="deleteShort(short.id)" class="text-red-500 hover:text-red-700 text-xs font-medium px-1">삭제</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="p-4 border-t border-gray-100 text-center">
        <button class="text-sm text-blue-600 hover:text-blue-800 font-medium">더 보기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const filterCategory = ref('')
const filterStatus = ref('')
const searchQuery = ref('')

const shorts = ref([
  {
    id: 1,
    title: '코리아타운 최고 맛집 TOP 5',
    uploader: '먹방킹',
    category: '음식',
    views: 45200,
    likes: 3100,
    comments: 214,
    reports: 0,
    uploadedAt: '2026-03-28',
    status: '활성'
  },
  {
    id: 2,
    title: '한복 입고 LA 돌아다니기',
    uploader: '한복미녀',
    category: '문화',
    views: 128000,
    likes: 9800,
    comments: 512,
    reports: 0,
    uploadedAt: '2026-03-27',
    status: '활성'
  },
  {
    id: 3,
    title: '한인타운 야경 드라이브',
    uploader: '나이트드라이버',
    category: '일상',
    views: 22000,
    likes: 1500,
    comments: 98,
    reports: 3,
    uploadedAt: '2026-03-26',
    status: '신고됨'
  },
  {
    id: 4,
    title: '5분 만에 배우는 김치찌개',
    uploader: '요리마스터',
    category: '음식',
    views: 87000,
    likes: 6200,
    comments: 330,
    reports: 0,
    uploadedAt: '2026-03-25',
    status: '활성'
  },
  {
    id: 5,
    title: '불법 도박 방법 공유',
    uploader: '유저123',
    category: '기타',
    views: 5400,
    likes: 120,
    comments: 45,
    reports: 12,
    uploadedAt: '2026-03-24',
    status: '신고됨'
  },
  {
    id: 6,
    title: 'K-뷰티 메이크업 튜토리얼',
    uploader: '뷰티크리에이터',
    category: '뷰티',
    views: 63000,
    likes: 4500,
    comments: 280,
    reports: 0,
    uploadedAt: '2026-03-23',
    status: '활성'
  }
])

const stats = computed(() => ({
  total: shorts.value.length,
  todayUploads: shorts.value.filter(s => s.uploadedAt === '2026-03-28').length,
  totalViews: shorts.value.reduce((sum, s) => sum + s.views, 0),
  reported: shorts.value.filter(s => s.reports > 0).length
}))

const reportedShorts = computed(() => shorts.value.filter(s => s.reports > 0))

const filteredShorts = computed(() => {
  let list = shorts.value
  if (filterCategory.value) list = list.filter(s => s.category === filterCategory.value)
  if (filterStatus.value) list = list.filter(s => s.status === filterStatus.value)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(s => s.title.toLowerCase().includes(q) || s.uploader.toLowerCase().includes(q))
  }
  return list
})

function statusBadge(status) {
  const map = {
    '활성': 'bg-green-100 text-green-700',
    '신고됨': 'bg-red-100 text-red-700',
    '블라인드': 'bg-yellow-100 text-yellow-700',
    '삭제됨': 'bg-gray-100 text-gray-500'
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

function formatNum(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n
}

async function blindShort(id) {
  try {
    await axios.patch(`/api/admin/shorts/${id}/blind`)
  } catch {}
  const s = shorts.value.find(s => s.id === id)
  if (s) s.status = '블라인드'
}

async function deleteShort(id) {
  if (!confirm('이 숏츠를 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/admin/shorts/${id}`)
  } catch {}
  shorts.value = shorts.value.filter(s => s.id !== id)
}
</script>
