<template>
  <!-- /admin/v2/content (Phase 2-C Post: DataTable + 대량 삭제 Kay #6) -->
  <div class="space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <h2 class="text-xl font-bold">📝 게시글 관리</h2>
      <router-link to="/community" target="_blank" class="text-xs text-amber-600 hover:text-amber-800">↗️ 커뮤니티 보기</router-link>
    </div>

    <!-- 필터 -->
    <div class="bg-white rounded-xl shadow-sm p-3 flex gap-2 flex-wrap">
      <select v-model="boardFilter" @change="load" class="px-3 py-1.5 border rounded text-sm">
        <option value="">모든 게시판</option>
        <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <label class="flex items-center gap-1 text-xs px-3 py-1.5 border rounded cursor-pointer">
        <input type="checkbox" v-model="hiddenOnly" @change="load" /> 숨김만
      </label>
      <label class="flex items-center gap-1 text-xs px-3 py-1.5 border rounded cursor-pointer">
        <input type="checkbox" v-model="reportedOnly" @change="load" /> 신고된만
      </label>
    </div>

    <DataTable
      :rows="posts"
      :columns="columns"
      :loading="loading"
      :page-size="40"
      exportable
      :search-keys="['title', 'content']"
      search-placeholder="제목·본문 검색"
      empty-text="게시글 없음"
      :bulk-actions="bulkActions"
      @bulk-action="handleBulk"
    >
      <template #cell-is_pinned="{ value }">
        <span v-if="value" class="text-amber-500">📌</span>
      </template>
      <template #cell-is_hidden="{ value }">
        <span v-if="value" class="text-red-500">🙈</span>
      </template>
      <template #cell-title="{ row }">
        <router-link :to="`/community/${row.id}`" target="_blank" class="hover:text-amber-600 truncate block max-w-md">
          {{ row.title || row.content?.substring(0, 50) || '(제목 없음)' }}
        </router-link>
      </template>
      <template #cell-author="{ row }">
        <span class="text-xs">{{ row.user?.nickname || row.user?.name || '?' }}</span>
      </template>
      <template #cell-reports_count="{ value }">
        <span v-if="value > 0" class="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-bold">{{ value }}</span>
      </template>
      <template #cell-created_at="{ value }">
        <span class="text-xs">{{ fmtDate(value) }}</span>
      </template>
      <template #actions="{ row }">
        <button @click="togglePin(row)" class="text-xs px-2 py-1 rounded mr-1" :class="row.is_pinned ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 hover:bg-gray-200'">📌</button>
        <button @click="toggleHide(row)" class="text-xs px-2 py-1 rounded mr-1" :class="row.is_hidden ? 'bg-red-100 text-red-700' : 'bg-gray-100 hover:bg-gray-200'">🙈</button>
        <button @click="del(row)" class="text-xs px-2 py-1 bg-red-100 text-red-700 hover:bg-red-200 rounded">🗑️</button>
      </template>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import DataTable from '../../../components/admin/DataTable.vue'
import { useSiteStore } from '../../../stores/site'

const site = useSiteStore()
const posts = ref([])
const boards = ref([])
const loading = ref(true)
const boardFilter = ref('')
const hiddenOnly = ref(false)
const reportedOnly = ref(false)

const fmtDate = (s) => s ? new Date(s).toLocaleDateString('ko-KR') : ''

const columns = [
  { key: 'id', label: 'ID', sortable: true, class: 'font-mono text-xs w-16' },
  { key: 'is_pinned', label: '', class: 'w-8' },
  { key: 'is_hidden', label: '', class: 'w-8' },
  { key: 'title', label: '제목', sortable: true },
  { key: 'author', label: '작성자', class: 'w-24' },
  { key: 'comments_count', label: '💬', sortable: true, class: 'text-center w-12' },
  { key: 'likes_count', label: '❤️', sortable: true, class: 'text-center w-12' },
  { key: 'view_count', label: '👁', sortable: true, class: 'text-center w-12' },
  { key: 'reports_count', label: '🚨', sortable: true, class: 'text-center w-12' },
  { key: 'created_at', label: '작성일', sortable: true, class: 'w-24' },
]

const bulkActions = [
  { key: 'delete',  label: '🗑️ 대량 삭제',  danger: true, confirm: '선택한 게시글을 삭제하시겠습니까?' },
  { key: 'hide',    label: '🙈 대량 숨김' },
  { key: 'show',    label: '👁 대량 노출' },
]

async function load() {
  loading.value = true
  try {
    const params = { per_page: 200 }
    if (boardFilter.value) params.board_id = boardFilter.value
    if (hiddenOnly.value) params.hidden = 1
    if (reportedOnly.value) params.reported = 1
    const { data } = await axios.get('/api/admin/posts', { params })
    posts.value = data?.data?.data || data?.data || []
  } finally { loading.value = false }
}

async function loadBoards() {
  try {
    const { data } = await axios.get('/api/admin/boards')
    boards.value = data?.data || []
  } catch {}
}

async function togglePin(row) {
  try { await axios.post(`/api/admin/posts/${row.id}/pin`); row.is_pinned = !row.is_pinned } catch {}
}
async function toggleHide(row) {
  try { await axios.post(`/api/admin/posts/${row.id}/hide`); row.is_hidden = !row.is_hidden } catch {}
}
async function del(row) {
  if (!confirm(`"${row.title || row.id}" 를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/posts/${row.id}`)
    posts.value = posts.value.filter(p => p.id !== row.id)
    site.toast('삭제되었습니다', 'success')
  } catch { site.toast('실패', 'error') }
}

async function handleBulk({ key, rows }) {
  const ids = rows.map(r => r.id)
  try {
    if (key === 'delete') {
      const { data } = await axios.post('/api/admin/posts/bulk-delete', { ids })
      posts.value = posts.value.filter(p => !ids.includes(p.id))
      site.toast(`${data.deleted}건 삭제 완료`, 'success')
    } else if (key === 'hide' || key === 'show') {
      await axios.post('/api/admin/posts/bulk-hide', { ids, hidden: key === 'hide' })
      ids.forEach(id => { const p = posts.value.find(x => x.id === id); if (p) p.is_hidden = key === 'hide' })
      site.toast(`${ids.length}건 ${key === 'hide' ? '숨김' : '노출'}`, 'success')
    }
  } catch (e) {
    site.toast(e.response?.data?.message || '실패 (권한 확인)', 'error')
  }
}

onMounted(async () => {
  await Promise.all([load(), loadBoards()])
})
</script>
