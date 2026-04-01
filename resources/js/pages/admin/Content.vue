<template>
  <div class="space-y-5">

    <!-- 탭 -->
    <div class="flex gap-2 flex-wrap">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key; loadTab()"
        :class="['px-4 py-2 rounded-xl text-sm font-semibold transition',
          activeTab === tab.key ? 'bg-blue-500 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50']">
        {{ tab.icon }} {{ tab.label }}
        <span v-if="tab.badge" class="ml-1 text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded-full">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- 검색 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex gap-3">
      <input v-model="search" @keyup.enter="loadTab" type="text" placeholder="검색..."
        class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
      <select v-if="activeTab === 'reports'" v-model="reportStatus" @change="loadTab"
        class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
        <option value="pending">미처리</option>
        <option value="dismissed">처리됨</option>
      </select>
      <button @click="loadTab"
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition">
        검색
      </button>
    </div>

    <!-- 신고 목록 -->
    <div v-if="activeTab === 'reports'" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
      <div v-else-if="items.length === 0" class="text-center py-10 text-gray-400 text-sm">신고 없음 ✓</div>
      <div v-else class="divide-y divide-gray-50">
        <div v-for="r in items" :key="r.id" class="px-5 py-4 flex items-start gap-4">
          <div class="w-9 h-9 rounded-full bg-red-100 text-red-500 flex items-center justify-center text-sm flex-shrink-0">🚨</div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-800">{{ r.reason }}</div>
            <div class="text-xs text-gray-400 mt-0.5">
              신고자: {{ r.reporter?.name ?? '알수없음' }} · {{ formatDate(r.created_at) }}
            </div>
            <div v-if="r.reportable_type" class="text-[10px] text-gray-400 mt-0.5">
              대상: {{ r.reportable_type.split('\\').pop() }} #{{ r.reportable_id }}
            </div>
          </div>
          <div class="flex gap-2 flex-shrink-0">
            <button v-if="r.status === 'pending'" @click="dismissReport(r)"
              class="text-xs bg-green-50 hover:bg-green-100 text-green-600 px-3 py-1.5 rounded-lg transition font-semibold">
              처리
            </button>
            <span v-else class="text-xs text-gray-400 bg-gray-50 px-3 py-1.5 rounded-lg">처리됨</span>
          </div>
        </div>
      </div>
      <PaginationBar :page="page" :lastPage="lastPage" @change="changePage" />
    </div>

    <!-- 게시글 목록 -->
    <div v-if="activeTab === 'posts'" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
      <div v-else-if="items.length === 0" class="text-center py-10 text-gray-400 text-sm">게시글이 없습니다.</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">제목</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">작성자</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">날짜</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div class="text-xs font-medium text-gray-800 truncate max-w-[200px]">{{ item.title }}</div>
                <div class="text-[10px] text-gray-400">{{ item.category }}</div>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden sm:table-cell">{{ item.user?.name }}</td>
              <td class="px-4 py-3 text-xs text-gray-400 hidden md:table-cell">{{ formatDate(item.created_at) }}</td>
              <td class="px-4 py-3 text-right">
                <button @click="deleteItem(item)" class="text-xs bg-red-50 hover:bg-red-100 text-red-500 px-2.5 py-1 rounded-lg transition">삭제</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationBar :page="page" :lastPage="lastPage" @change="changePage" />
    </div>

    <!-- 구인구직 목록 -->
    <div v-if="activeTab === 'jobs'" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
      <div v-else-if="items.length === 0" class="text-center py-10 text-gray-400 text-sm">구인구직이 없습니다.</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">제목</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">작성자</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">상태</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3 text-xs font-medium text-gray-800 truncate max-w-[200px]">{{ item.title }}</td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden sm:table-cell">{{ item.user?.name }}</td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold',
                  item.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500']">
                  {{ item.status }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button @click="deleteItem(item)" class="text-xs bg-red-50 hover:bg-red-100 text-red-500 px-2.5 py-1 rounded-lg transition">삭제</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationBar :page="page" :lastPage="lastPage" @change="changePage" />
    </div>

    <!-- 중고장터 목록 -->
    <div v-if="activeTab === 'market'" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
      <div v-else-if="items.length === 0" class="text-center py-10 text-gray-400 text-sm">중고장터 글이 없습니다.</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">제목</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">작성자</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">가격</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3 text-xs font-medium text-gray-800 truncate max-w-[200px]">{{ item.title }}</td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden sm:table-cell">{{ item.user?.name }}</td>
              <td class="px-4 py-3 text-xs text-gray-600 hidden md:table-cell">${{ item.price?.toLocaleString() }}</td>
              <td class="px-4 py-3 text-right">
                <button @click="deleteItem(item)" class="text-xs bg-red-50 hover:bg-red-100 text-red-500 px-2.5 py-1 rounded-lg transition">삭제</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <PaginationBar :page="page" :lastPage="lastPage" @change="changePage" />
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, defineComponent, h } from 'vue'
import axios from 'axios'

// 인라인 페이지네이션 컴포넌트
const PaginationBar = defineComponent({
  props: ['page', 'lastPage'],
  emits: ['change'],
  setup(props, { emit }) {
    return () => props.lastPage > 1 ? h('div', {
      class: 'flex items-center justify-center gap-2 px-4 py-3 border-t border-gray-100'
    }, [
      h('button', { onClick: () => emit('change', props.page - 1), disabled: props.page <= 1,
        class: 'px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition' }, '‹ 이전'),
      h('span', { class: 'text-xs text-gray-500' }, `${props.page} / ${props.lastPage}`),
      h('button', { onClick: () => emit('change', props.page + 1), disabled: props.page >= props.lastPage,
        class: 'px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition' }, '다음 ›'),
    ]) : null
  }
})

const tabs = [
  { key: 'reports', icon: '🚨', label: '신고 처리' },
  { key: 'posts',   icon: '📝', label: '게시글' },
  { key: 'jobs',    icon: '💼', label: '구인구직' },
  { key: 'market',  icon: '🛍️', label: '중고장터' },
]

const activeTab    = ref('reports')
const items        = ref([])
const page         = ref(1)
const lastPage     = ref(1)
const loading      = ref(false)
const search       = ref('')
const reportStatus = ref('pending')

const endpointMap = { reports: '/api/admin/reports', posts: '/api/admin/posts', jobs: '/api/admin/jobs', market: '/api/admin/market' }

async function loadTab() {
  loading.value = true
  page.value = 1
  try {
    const params = { page: 1, search: search.value }
    if (activeTab.value === 'reports') params.status = reportStatus.value
    const res = await axios.get(endpointMap[activeTab.value], { params })
    items.value    = res.data.data ?? []
    lastPage.value = res.data.last_page ?? 1
  } finally {
    loading.value = false
  }
}

async function changePage(p) {
  if (p < 1 || p > lastPage.value) return
  page.value = p
  loading.value = true
  try {
    const params = { page: p, search: search.value }
    if (activeTab.value === 'reports') params.status = reportStatus.value
    const res = await axios.get(endpointMap[activeTab.value], { params })
    items.value = res.data.data ?? []
  } finally {
    loading.value = false
  }
}

async function dismissReport(r) {
  await axios.post(`/api/admin/reports/${r.id}/dismiss`)
  r.status = 'dismissed'
}

async function deleteItem(item) {
  const urlMap = { posts: `/api/admin/posts/${item.id}`, jobs: `/api/admin/jobs/${item.id}`, market: `/api/admin/market/${item.id}` }
  if (!confirm(`삭제하시겠습니까?`)) return
  await axios.delete(urlMap[activeTab.value])
  items.value = items.value.filter(i => i.id !== item.id)
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(loadTab)
</script>
