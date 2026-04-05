<template>
  <div class="space-y-5">
    <!-- 헤더 -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">숏츠 관리</h1>
        <p class="text-sm text-gray-500 mt-1">업로드된 숏츠 영상을 관리합니다</p>
      </div>
      <button @click="loadShorts" class="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition">
        새로고침
      </button>
    </div>

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">전체 숏츠</p>
        <p class="text-3xl font-bold text-gray-800 mt-1">{{ stats.total }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">유튜브</p>
        <p class="text-3xl font-bold text-red-500 mt-1">{{ stats.youtube }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">회원업로드</p>
        <p class="text-3xl font-bold text-blue-600 mt-1">{{ stats.member }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">신고됨</p>
        <p class="text-3xl font-bold text-red-500 mt-1">{{ stats.reported }}</p>
      </div>
    </div>

    <!-- 필터 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div class="flex flex-wrap gap-3 items-center">
        <input
          v-model="searchText"
          @input="onSearch"
          placeholder="제목 검색..."
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 flex-1 min-w-[160px]"
        />
        <select v-model="filterPlatform" @change="onFilterChange" class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 플랫폼</option>
          <option value="youtube">YouTube</option>
          <option value="tiktok">TikTok</option>
          <option value="instagram">Instagram</option>
          <option value="member">회원업로드</option>
        </select>
        <select v-model="filterStatus" @change="onFilterChange" class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 상태</option>
          <option value="active">활성</option>
          <option value="hidden">숨김</option>
        </select>
        <button @click="resetFilters" class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-semibold transition">
          초기화
        </button>
      </div>
    </div>

    <!-- 로딩 -->
    <div v-if="loading" class="flex justify-center py-16">
      <div class="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <!-- 테이블 -->
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <div v-if="shorts.length === 0" class="text-center py-12 text-gray-400 text-sm">
          숏츠가 없습니다.
        </div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 w-20">썸네일</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">제목</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">플랫폼</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">업로더</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden lg:table-cell">조회/좋아요</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">상태</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden xl:table-cell">등록일</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="short in shorts" :key="short.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div
                  class="w-16 h-10 rounded-lg overflow-hidden bg-gray-100 cursor-pointer flex-shrink-0 relative group"
                  @click="openPreview(short)"
                >
                  <img
                    v-if="short.thumbnail"
                    :src="short.thumbnail"
                    :alt="short.title"
                    class="w-full h-full object-cover"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-gray-400 text-xs">No img</div>
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                    <span class="text-white text-lg">&#9654;</span>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 max-w-[180px]">
                <p class="font-medium text-gray-800 truncate">{{ short.title || '(제목 없음)' }}</p>
              </td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', platformClass(short.platform)]">
                  {{ platformLabel(short.platform) }}
                </span>
              </td>
              <td class="px-4 py-3 hidden lg:table-cell">
                <span class="text-gray-600 text-xs">{{ short.user_name || '-' }}</span>
              </td>
              <td class="px-4 py-3 hidden lg:table-cell">
                <div class="text-xs text-gray-500 flex flex-col gap-0.5">
                  <span>&#128065; {{ formatNum(short.view_count) }}</span>
                  <span>&#10084; {{ formatNum(short.like_count) }}</span>
                </div>
              </td>
              <td class="px-4 py-3 hidden sm:table-cell">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', short.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">
                  {{ short.is_active ? '활성' : '숨김' }}
                </span>
              </td>
              <td class="px-4 py-3 hidden xl:table-cell">
                <span class="text-xs text-gray-400">{{ formatDate(short.created_at) }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <div class="flex items-center justify-end gap-1.5">
                  <button @click="openPreview(short)" class="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-2 py-1 rounded-lg transition">미리보기</button>
                  <button
                    @click="toggleBlind(short)"
                    :class="['text-xs px-2 py-1 rounded-lg transition', short.is_active ? 'bg-yellow-50 text-yellow-600 hover:bg-yellow-100' : 'bg-green-50 text-green-600 hover:bg-green-100']"
                  >{{ short.is_active ? '숨김' : '활성화' }}</button>
                  <button @click="confirmDelete(short)" class="text-xs bg-red-50 text-red-500 hover:bg-red-100 px-2 py-1 rounded-lg transition">삭제</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="pagination.last_page > 1" class="flex justify-center items-center gap-2 p-4 border-t border-gray-100 flex-wrap">
        <button
          @click="goPage(pagination.current_page - 1)"
          :disabled="pagination.current_page <= 1"
          class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >&#8249; 이전</button>
        <template v-for="p in pageList" :key="p">
          <span v-if="p === '...'" class="px-2 text-gray-400">&#8230;</span>
          <button
            v-else
            @click="goPage(p)"
            :class="['px-3 py-1.5 text-sm rounded-lg transition', p === pagination.current_page ? 'bg-blue-500 text-white font-bold' : 'border border-gray-200 hover:bg-gray-50']"
          >{{ p }}</button>
        </template>
        <button
          @click="goPage(pagination.current_page + 1)"
          :disabled="pagination.current_page >= pagination.last_page"
          class="px-3 py-1.5 text-sm rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
        >다음 &#8250;</button>
        <span class="text-xs text-gray-400 ml-2">{{ pagination.total }}개 중 {{ shorts.length }}개</span>
      </div>
    </div>

    <!-- 비디오 미리보기 모달 -->
    <div
      v-if="previewShort"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70"
      @click.self="closePreview"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div class="flex items-center gap-3">
            <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold', platformClass(previewShort.platform)]">
              {{ platformLabel(previewShort.platform) }}
            </span>
            <h3 class="font-semibold text-gray-800 truncate max-w-[300px]">{{ previewShort.title || '(제목 없음)' }}</h3>
          </div>
          <button @click="closePreview" class="text-gray-400 hover:text-gray-700 text-2xl font-bold leading-none">&times;</button>
        </div>
        <div class="relative w-full" style="padding-top: 56.25%;">
          <iframe
            v-if="previewShort.embed_url"
            :src="previewShort.embed_url"
            class="absolute inset-0 w-full h-full"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
          ></iframe>
          <div v-else class="absolute inset-0 flex flex-col items-center justify-center bg-gray-900 text-white gap-3">
            <span class="text-4xl">&#128249;</span>
            <p class="text-sm text-gray-400">미리보기를 사용할 수 없습니다</p>
            <a :href="previewShort.url" target="_blank" class="text-blue-400 underline text-sm">원본 링크 열기</a>
          </div>
        </div>
        <div class="px-5 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-between text-sm text-gray-500">
          <div class="flex gap-4">
            <span>&#128065; {{ formatNum(previewShort.view_count) }}</span>
            <span>&#10084; {{ formatNum(previewShort.like_count) }}</span>
            <span>{{ previewShort.is_active ? '활성' : '숨김' }}</span>
          </div>
          <div class="flex gap-2">
            <button
              @click="toggleBlind(previewShort); closePreview()"
              :class="['px-3 py-1.5 rounded-lg text-sm font-medium transition', previewShort.is_active ? 'bg-yellow-500 text-white hover:bg-yellow-600' : 'bg-green-500 text-white hover:bg-green-600']"
            >{{ previewShort.is_active ? '숨김 처리' : '활성화' }}</button>
            <button
              @click="confirmDelete(previewShort); closePreview()"
              class="px-3 py-1.5 rounded-lg text-sm font-medium bg-red-500 text-white hover:bg-red-600 transition"
            >삭제</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div
      v-if="deleteTarget"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60"
      @click.self="deleteTarget = null"
    >
      <div class="bg-white rounded-2xl shadow-2xl p-6 w-full max-w-sm">
        <h3 class="text-lg font-bold text-gray-800 mb-2">숏츠 삭제</h3>
        <p class="text-sm text-gray-500 mb-5">
          "<span class="font-semibold text-gray-700">{{ deleteTarget.title || '(제목 없음)' }}</span>"을 삭제하시겠습니까?<br />
          <span class="text-red-500">이 작업은 되돌릴 수 없습니다.</span>
        </p>
        <div class="flex justify-end gap-3">
          <button @click="deleteTarget = null" class="px-4 py-2 rounded-lg border border-gray-200 text-sm hover:bg-gray-50 transition">취소</button>
          <button @click="doDelete" class="px-4 py-2 rounded-lg bg-red-500 text-white text-sm font-semibold hover:bg-red-600 transition">삭제</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(false)
const shorts = ref([])
const pagination = ref({ current_page: 1, last_page: 1, total: 0 })
const searchText = ref('')
const filterPlatform = ref('')
const filterStatus = ref('')
const previewShort = ref(null)
const deleteTarget = ref(null)
let searchTimer = null

const stats = computed(() => {
  const all = shorts.value
  return {
    total: pagination.value.total || 0,
    youtube: all.filter(s => s.platform === 'youtube').length,
    member: all.filter(s => !s.platform || s.platform === 'member').length,
    reported: 0
  }
})

const pageList = computed(() => {
  const cur = pagination.value.current_page
  const last = pagination.value.last_page
  if (last <= 7) return Array.from({ length: last }, (_, i) => i + 1)
  const pages = []
  if (cur > 3) pages.push(1, '...')
  for (let i = Math.max(1, cur - 2); i <= Math.min(last, cur + 2); i++) pages.push(i)
  if (cur < last - 2) pages.push('...', last)
  return pages
})

async function loadShorts(page = 1) {
  loading.value = true
  try {
    const params = { page }
    if (searchText.value) params.search = searchText.value
    if (filterPlatform.value) params.platform = filterPlatform.value
    if (filterStatus.value) params.status = filterStatus.value
    const res = await axios.get('/api/admin/shorts', { params })
    const data = res.data
    shorts.value = data.data || []
    pagination.value = {
      current_page: data.current_page || 1,
      last_page: data.last_page || 1,
      total: data.total || 0
    }
  } catch (e) {
    console.error('숏츠 로드 실패', e)
    shorts.value = []
  } finally {
    loading.value = false
  }
}

function goPage(p) {
  if (p < 1 || p > pagination.value.last_page) return
  loadShorts(p)
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => loadShorts(1), 400)
}

function onFilterChange() {
  loadShorts(1)
}

function resetFilters() {
  searchText.value = ''
  filterPlatform.value = ''
  filterStatus.value = ''
  loadShorts(1)
}

function openPreview(short) {
  previewShort.value = short
}

function closePreview() {
  previewShort.value = null
}

function confirmDelete(short) {
  deleteTarget.value = short
}

async function doDelete() {
  if (!deleteTarget.value) return
  try {
    await axios.delete(`/api/admin/shorts/${deleteTarget.value.id}`)
    shorts.value = shorts.value.filter(s => s.id !== deleteTarget.value.id)
    deleteTarget.value = null
  } catch (e) {
    alert('삭제 실패: ' + (e?.response?.data?.message || e.message))
  }
}

async function toggleBlind(short) {
  try {
    const res = await axios.patch(`/api/admin/shorts/${short.id}/blind`)
    const updated = res.data
    const idx = shorts.value.findIndex(s => s.id === short.id)
    if (idx !== -1) {
      shorts.value[idx] = { ...shorts.value[idx], is_active: updated.is_active }
    }
  } catch (e) {
    alert('상태 변경 실패: ' + (e?.response?.data?.message || e.message))
  }
}

function platformLabel(platform) {
  const map = { youtube: 'YouTube', tiktok: 'TikTok', instagram: 'Instagram', member: '회원' }
  return map[platform] || platform || '기타'
}

function platformClass(platform) {
  const map = {
    youtube: 'bg-red-100 text-red-600',
    tiktok: 'bg-black/10 text-gray-700',
    instagram: 'bg-pink-100 text-pink-600',
    member: 'bg-blue-100 text-blue-600'
  }
  return map[platform] || 'bg-gray-100 text-gray-600'
}

function formatNum(n) {
  if (!n) return '0'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

onMounted(() => loadShorts(1))
</script>
