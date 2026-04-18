<template>
  <!-- /admin/v2/payments (Phase 2-C Post) -->
  <div class="space-y-4">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <h2 class="text-xl font-bold">💳 결제 관리</h2>
      <div class="flex gap-3 text-sm">
        <div class="bg-green-50 px-3 py-1.5 rounded">
          완료: <strong class="text-green-700">${{ totalCompleted.toFixed(2) }}</strong>
        </div>
        <div class="bg-red-50 px-3 py-1.5 rounded">
          환불: <strong class="text-red-700">${{ totalRefunded.toFixed(2) }}</strong>
        </div>
        <div class="bg-yellow-50 px-3 py-1.5 rounded">
          대기: <strong class="text-yellow-700">{{ pendingCount }}건</strong>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm p-3 flex gap-2 flex-wrap">
      <select v-model="statusFilter" @change="load" class="px-3 py-1.5 border rounded text-sm">
        <option value="">모든 상태</option>
        <option value="completed">완료</option>
        <option value="pending">대기</option>
        <option value="failed">실패</option>
        <option value="refunded">환불</option>
      </select>
      <select v-model="methodFilter" @change="load" class="px-3 py-1.5 border rounded text-sm">
        <option value="">모든 수단</option>
        <option value="stripe">Stripe</option>
        <option value="cardpointe">CardPointe</option>
      </select>
    </div>

    <DataTable
      :rows="payments"
      :columns="columns"
      :loading="loading"
      :page-size="40"
      exportable
      :search-keys="['stripe_payment_id', 'description']"
      search-placeholder="결제 ID·설명 검색"
      empty-text="결제 내역 없음"
    >
      <template #cell-amount="{ value }">
        <span class="font-bold">${{ Number(value).toFixed(2) }}</span>
      </template>
      <template #cell-status="{ value }">
        <span :class="statusBadge(value)">{{ statusLabel(value) }}</span>
      </template>
      <template #cell-user="{ row }">
        <span class="text-xs">{{ row.user?.nickname || row.user?.email || '?' }}</span>
      </template>
      <template #cell-created_at="{ value }">
        <span class="text-xs">{{ fmtDate(value) }}</span>
      </template>
      <template #actions="{ row }">
        <button v-if="row.status === 'completed'" @click="refund(row)" class="text-xs px-2 py-1 bg-red-100 text-red-700 hover:bg-red-200 rounded">환불</button>
        <span v-else class="text-xs text-gray-400">-</span>
      </template>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import DataTable from '../../../components/admin/DataTable.vue'
import { useSiteStore } from '../../../stores/site'

const site = useSiteStore()
const payments = ref([])
const loading = ref(true)
const statusFilter = ref('')
const methodFilter = ref('')
const fmtDate = (s) => s ? new Date(s).toLocaleString('ko-KR') : ''

const totalCompleted = computed(() => payments.value.filter(p => p.status === 'completed').reduce((s, p) => s + Number(p.amount || 0), 0))
const totalRefunded = computed(() => payments.value.filter(p => p.status === 'refunded').reduce((s, p) => s + Number(p.amount || 0), 0))
const pendingCount = computed(() => payments.value.filter(p => p.status === 'pending').length)

const columns = [
  { key: 'id', label: 'ID', sortable: true, class: 'w-16 font-mono text-xs' },
  { key: 'user', label: '유저' },
  { key: 'amount', label: '금액', sortable: true, class: 'text-right w-24' },
  { key: 'status', label: '상태', sortable: true, class: 'text-center w-24' },
  { key: 'description', label: '설명' },
  { key: 'stripe_payment_id', label: 'Provider ID', class: 'font-mono text-xs' },
  { key: 'created_at', label: '일시', sortable: true, class: 'w-32' },
]

const statusBadge = (s) => 'px-2 py-0.5 rounded text-xs font-semibold ' + ({
  completed: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  failed: 'bg-red-100 text-red-700',
  refunded: 'bg-gray-100 text-gray-500',
}[s] || 'bg-gray-100')
const statusLabel = (s) => ({ completed: '완료', pending: '대기', failed: '실패', refunded: '환불' }[s] || s)

async function load() {
  loading.value = true
  try {
    const params = { per_page: 200 }
    if (statusFilter.value) params.status = statusFilter.value
    if (methodFilter.value) params.method = methodFilter.value
    const { data } = await axios.get('/api/admin/payments', { params })
    payments.value = data?.data?.data || data?.data || []
  } finally { loading.value = false }
}

async function refund(row) {
  if (!confirm(`결제 #${row.id} ($${Number(row.amount).toFixed(2)}) 를 환불하시겠습니까?`)) return
  try {
    await axios.post(`/api/admin/payments/${row.id}/refund`)
    row.status = 'refunded'
    site.toast('환불 처리됨', 'success')
  } catch (e) { site.toast(e.response?.data?.message || '환불 실패', 'error') }
}

onMounted(load)
</script>
