<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-blue-600">{{ stats.total }}</div>
        <div class="text-xs text-gray-500 mt-0.5">전체 공고</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-green-500">{{ stats.active }}</div>
        <div class="text-xs text-gray-500 mt-0.5">활성 공고</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-orange-500">{{ stats.newThisWeek }}</div>
        <div class="text-xs text-gray-500 mt-0.5">이번주 신규</div>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100 text-center">
        <div class="text-2xl font-black text-purple-500">{{ stats.totalApplicants }}</div>
        <div class="text-xs text-gray-500 mt-0.5">지원자 총수</div>
      </div>
    </div>

    <!-- 필터 & 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <!-- 필터 -->
      <div class="p-4 border-b border-gray-100">
        <div class="flex flex-col sm:flex-row gap-3">
          <input v-model="search" placeholder="공고명 / 회사명 검색"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 flex-1" />
          <select v-model="filterCategory"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 카테고리</option>
            <option value="정규직">정규직</option>
            <option value="파트타임">파트타임</option>
            <option value="프리랜서">프리랜서</option>
            <option value="인턴">인턴</option>
          </select>
          <select v-model="filterStatus"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 상태</option>
            <option value="active">활성</option>
            <option value="expired">만료</option>
            <option value="deleted">삭제</option>
          </select>
          <button @click="resetFilters"
            class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-semibold transition">
            초기화
          </button>
        </div>
      </div>

      <!-- 테이블 -->
      <div class="overflow-x-auto">
        <div v-if="filteredJobs.length === 0" class="text-center py-12 text-gray-400 text-sm">
          검색 결과가 없습니다.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">공고 제목</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">회사명</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">카테고리</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">급여</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">지원자</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">마감일</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">상태</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="job in filteredJobs" :key="job.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div class="font-medium text-gray-800 truncate max-w-[180px]">{{ job.title }}</div>
                <div class="text-[10px] text-gray-400 mt-0.5">{{ job.location }}</div>
              </td>
              <td class="px-4 py-3 text-xs text-gray-600 hidden sm:table-cell">{{ job.company }}</td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', categoryClass(job.category)]">
                  {{ job.category }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-700 font-medium hidden md:table-cell">{{ job.salary }}</td>
              <td class="px-4 py-3 text-xs text-gray-600 hidden lg:table-cell">
                <span class="font-semibold text-blue-600">{{ job.applicants }}</span>명
              </td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden lg:table-cell">{{ job.deadline }}</td>
              <td class="px-4 py-3">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', statusClass(job.status)]">
                  {{ statusLabel(job.status) }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openDetail(job)"
                    class="text-[11px] bg-blue-50 hover:bg-blue-100 text-blue-600 px-2.5 py-1 rounded-lg transition font-medium">
                    상세
                  </button>
                  <button @click="confirmDelete(job)"
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
    <div v-if="selectedJob" class="fixed inset-0 z-50 flex items-center justify-center p-4"
      style="background:rgba(0,0,0,0.45)" @click.self="selectedJob = null">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <!-- 모달 헤더 -->
        <div class="flex items-start justify-between p-5 border-b border-gray-100">
          <div>
            <h2 class="text-lg font-bold text-gray-900">{{ selectedJob.title }}</h2>
            <p class="text-sm text-gray-500 mt-0.5">{{ selectedJob.company }}</p>
          </div>
          <button @click="selectedJob = null"
            class="text-gray-400 hover:text-gray-600 text-xl font-bold leading-none ml-4">×</button>
        </div>

        <!-- 모달 내용 -->
        <div class="p-5 space-y-5">
          <!-- 기본 정보 -->
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-gray-50 rounded-xl p-3">
              <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">카테고리</div>
              <span :class="['text-xs px-2 py-0.5 rounded-full font-semibold', categoryClass(selectedJob.category)]">
                {{ selectedJob.category }}
              </span>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">급여</div>
              <div class="text-sm font-bold text-gray-800">{{ selectedJob.salary }}</div>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">근무 위치</div>
              <div class="text-sm text-gray-700">{{ selectedJob.location }}</div>
            </div>
            <div class="bg-gray-50 rounded-xl p-3">
              <div class="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1">마감일</div>
              <div class="text-sm text-gray-700">{{ selectedJob.deadline }}</div>
            </div>
          </div>

          <!-- 업무 내용 -->
          <div>
            <div class="text-xs font-semibold text-gray-500 mb-2">업무 내용</div>
            <div class="bg-gray-50 rounded-xl p-3 text-sm text-gray-700 leading-relaxed">
              {{ selectedJob.title }}에 관한 구인 공고입니다. {{ selectedJob.company }}에서 함께 일할 분을 모집하고 있습니다.
              근무지는 {{ selectedJob.location }}이며, 급여는 {{ selectedJob.salary }}입니다.
              관심 있으신 분은 마감일 {{ selectedJob.deadline }} 이전에 지원해 주세요.
            </div>
          </div>

          <!-- 지원자 목록 -->
          <div>
            <div class="text-xs font-semibold text-gray-500 mb-2">
              지원자 목록 <span class="text-blue-600 font-bold">{{ selectedJob.applicants }}명</span>
            </div>
            <div class="space-y-2">
              <div v-for="i in Math.min(selectedJob.applicants, 4)" :key="i"
                class="flex items-center gap-3 bg-gray-50 rounded-xl p-3">
                <div class="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-600">
                  {{ i }}
                </div>
                <div class="flex-1">
                  <div class="text-xs font-medium text-gray-700">지원자 {{ i }}</div>
                  <div class="text-[10px] text-gray-400">지원일: 2026-03-{{ String(i + 20).padStart(2,'0') }}</div>
                </div>
                <span class="text-[10px] bg-yellow-50 text-yellow-600 px-2 py-0.5 rounded-full font-semibold">검토중</span>
              </div>
              <div v-if="selectedJob.applicants > 4"
                class="text-center text-xs text-gray-400 py-1">
                + {{ selectedJob.applicants - 4 }}명 더 있음
              </div>
            </div>
          </div>

          <!-- 등록자 정보 -->
          <div class="border-t border-gray-100 pt-4">
            <div class="text-xs font-semibold text-gray-500 mb-2">등록자 정보</div>
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-green-100 flex items-center justify-center text-sm font-bold text-green-600">
                {{ selectedJob.user_name.charAt(0) }}
              </div>
              <div>
                <div class="text-sm font-semibold text-gray-800">{{ selectedJob.user_name }}</div>
                <div class="text-[10px] text-gray-400">등록일: {{ selectedJob.created_at }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 모달 푸터 -->
        <div class="flex justify-end gap-2 px-5 pb-5">
          <button @click="confirmDelete(selectedJob); selectedJob = null"
            class="bg-red-50 hover:bg-red-100 text-red-500 px-4 py-2 rounded-lg text-sm font-semibold transition">
            삭제
          </button>
          <button @click="selectedJob = null"
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
        <h3 class="text-base font-bold text-gray-900 mb-1">공고를 삭제하시겠습니까?</h3>
        <p class="text-sm text-gray-500 mb-5">
          <span class="font-semibold text-gray-700">{{ deleteTarget.title }}</span> 공고가 영구 삭제됩니다.
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


const jobs = ref([])
const search = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const selectedJob = ref(null)
const deleteTarget = ref(null)

const stats = computed(() => ({
  total: jobs.value.length,
  active: jobs.value.filter(j => j.status === 'active').length,
  newThisWeek: jobs.value.filter(j => j.created_at >= '2026-03-22').length,
  totalApplicants: jobs.value.reduce((sum, j) => sum + j.applicants, 0),
}))

const filteredJobs = computed(() => {
  return jobs.value.filter(j => {
    const matchSearch = !search.value ||
      j.title.toLowerCase().includes(search.value.toLowerCase()) ||
      j.company.toLowerCase().includes(search.value.toLowerCase())
    const matchCat = !filterCategory.value || j.category === filterCategory.value
    const matchStatus = !filterStatus.value || j.status === filterStatus.value
    return matchSearch && matchCat && matchStatus
  })
})

function categoryClass(cat) {
  const map = {
    '정규직': 'bg-blue-50 text-blue-600',
    '파트타임': 'bg-green-50 text-green-600',
    '프리랜서': 'bg-purple-50 text-purple-600',
    '인턴': 'bg-orange-50 text-orange-600',
  }
  return map[cat] || 'bg-gray-50 text-gray-500'
}

function statusClass(status) {
  const map = {
    active: 'bg-green-50 text-green-600',
    expired: 'bg-gray-100 text-gray-500',
    deleted: 'bg-red-50 text-red-500',
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

function statusLabel(status) {
  const map = { active: '활성', expired: '만료', deleted: '삭제' }
  return map[status] || status
}

function openDetail(job) {
  selectedJob.value = job
}

function confirmDelete(job) {
  deleteTarget.value = job
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await axios.delete(`/api/admin/jobs/${deleteTarget.value.id}`)
  } catch (e) {
    // demo: proceed with local deletion regardless
  }
  jobs.value = jobs.value.filter(j => j.id !== deleteTarget.value.id)
  deleteTarget.value = null
}

function resetFilters() {
  search.value = ''
  filterCategory.value = ''
  filterStatus.value = ''
}

async function loadJobs() {
  try {
    const res = await axios.get('/api/admin/jobs')
    jobs.value = res.data?.data || res.data || []
  } catch (e) {
    jobs.value = []
  }
}

onMounted(() => {
  loadJobs()
})
</script>
