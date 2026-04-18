<template>
  <!-- /admin/v2/security/reports (Phase 2-C Post) -->
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold">🚨 신고 관리</h2>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-3 flex gap-2 flex-wrap">
      <select v-model="typeFilter" @change="load" class="px-3 py-1.5 border rounded text-sm">
        <option value="">모든 대상</option>
        <option value="post">게시글</option>
        <option value="comment">댓글</option>
        <option value="user">유저</option>
        <option value="market">장터</option>
      </select>
      <select v-model="statusFilter" @change="load" class="px-3 py-1.5 border rounded text-sm">
        <option value="">전체 상태</option>
        <option value="pending">대기중</option>
        <option value="resolved">처리됨</option>
        <option value="dismissed">기각</option>
      </select>
    </div>

    <DataTable
      :rows="reports"
      :columns="columns"
      :loading="loading"
      :page-size="40"
      exportable
      :search-keys="['reason', 'description']"
      empty-text="신고 없음"
      :bulk-actions="bulkActions"
      @bulk-action="handleBulk"
    >
      <template #cell-status="{ value }">
        <span :class="statusBadge(value)">{{ statusLabel(value) }}</span>
      </template>
      <template #cell-reportable_type="{ value }">
        <span class="px-2 py-0.5 bg-gray-100 rounded text-xs">{{ shortType(value) }}</span>
      </template>
      <template #cell-reporter="{ row }">
        <span class="text-xs">{{ row.reporter?.nickname || row.reporter?.name || '?' }}</span>
      </template>
      <template #cell-reason="{ value }">
        <span class="text-xs truncate block max-w-xs">{{ value }}</span>
      </template>
      <template #cell-created_at="{ value }">
        <span class="text-xs">{{ fmtDate(value) }}</span>
      </template>
      <template #actions="{ row }">
        <button v-if="row.status === 'pending'" @click="resolve(row, 'resolved')" class="text-xs px-2 py-1 bg-green-100 text-green-700 hover:bg-green-200 rounded mr-1">✓</button>
        <button v-if="row.status === 'pending'" @click="resolve(row, 'dismissed')" class="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded mr-1">기각</button>
        <button @click="viewTarget(row)" class="text-xs px-2 py-1 bg-blue-100 text-blue-700 hover:bg-blue-200 rounded">🔍</button>
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
const reports = ref([])
const loading = ref(true)
const typeFilter = ref('')
const statusFilter = ref('')
const fmtDate = (s) => s ? new Date(s).toLocaleString('ko-KR') : ''

const columns = [
  { key: 'id', label: 'ID', sortable: true, class: 'w-16 font-mono text-xs' },
  { key: 'reportable_type', label: '대상 유형', class: 'w-24' },
  { key: 'reportable_id', label: '대상 ID', class: 'font-mono text-xs w-20' },
  { key: 'reporter', label: '신고자', class: 'w-24' },
  { key: 'reason', label: '사유' },
  { key: 'status', label: '상태', sortable: true, class: 'text-center w-24' },
  { key: 'created_at', label: '신고일', sortable: true, class: 'w-32' },
]

const bulkActions = [
  { key: 'resolve_all',   label: '✓ 일괄 처리' },
  { key: 'dismiss_all',   label: '기각 일괄' },
]

const statusBadge = (s) => 'px-2 py-0.5 rounded text-xs font-semibold ' + ({
  pending: 'bg-yellow-100 text-yellow-700',
  resolved: 'bg-green-100 text-green-700',
  dismissed: 'bg-gray-100 text-gray-500',
}[s] || 'bg-gray-100')
const statusLabel = (s) => ({ pending: '대기', resolved: '처리됨', dismissed: '기각' }[s] || s)
const shortType = (t) => (t || '').split('\\').pop().toLowerCase()

async function load() {
  loading.value = true
  try {
    const params = { per_page: 200 }
    if (typeFilter.value) params.type = typeFilter.value
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await axios.get('/api/admin/reports', { params })
    reports.value = data?.data?.data || data?.data || []
  } finally { loading.value = false }
}

async function resolve(r, status) {
  try {
    await axios.put(`/api/admin/reports/${r.id}`, { status })
    r.status = status
    site.toast(status === 'resolved' ? '처리 완료' : '기각 처리', 'success')
  } catch { site.toast('실패', 'error') }
}

function viewTarget(r) {
  const t = shortType(r.reportable_type)
  const map = { post: `/community/${r.reportable_id}`, comment: `/community/${r.reportable_id}`, user: `/profile/${r.reportable_id}`, market: `/market/${r.reportable_id}` }
  const url = map[t]
  if (url) window.open(url, '_blank')
  else site.toast('대상 URL 미지원', 'info')
}

async function handleBulk({ key, rows }) {
  const status = key === 'resolve_all' ? 'resolved' : 'dismissed'
  const pending = rows.filter(r => r.status === 'pending')
  for (const r of pending) {
    try { await axios.put(`/api/admin/reports/${r.id}`, { status }) } catch {}
    r.status = status
  }
  site.toast(`${pending.length}건 ${status === 'resolved' ? '처리' : '기각'}`, 'success')
}

onMounted(load)
</script>
