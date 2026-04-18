<template>
<div>
  <!-- 승인 대기 공구 -->
  <div v-if="pending.length" class="bg-orange-50 border border-orange-200 rounded-lg p-3 mb-3">
    <div class="flex justify-between items-center mb-2">
      <div class="font-bold text-sm text-orange-800">⏳ 승인 대기 공동구매 {{ pending.length }}건</div>
      <button @click="loadPending" class="text-xs text-orange-700 hover:underline">새로고침</button>
    </div>
    <div class="space-y-1">
      <div v-for="item in pending" :key="item.id" class="flex items-center gap-2 text-xs bg-white rounded p-2">
        <span class="flex-1 font-medium truncate">{{ item.title }}</span>
        <span class="text-gray-500">{{ item.category }}</span>
        <span class="text-gray-500">${{ item.original_price }} → ${{ item.group_price }}</span>
        <span class="text-gray-500">{{ item.user?.name }}</span>
        <a v-if="item.business_doc" :href="item.business_doc" target="_blank" class="text-blue-600">사업자증</a>
        <button @click="approve(item.id)" class="bg-green-500 text-white px-2 py-0.5 rounded text-[10px]">승인</button>
        <button @click="reject(item.id)" class="bg-red-500 text-white px-2 py-0.5 rounded text-[10px]">거절</button>
      </div>
    </div>
  </div>

  <AdminBoardManager
    slug="groupbuy"
    label="공동구매"
    icon="🛍"
    api-url="/api/groupbuys"
    delete-url="/api/admin/groupbuys"
    :extra-cols='[{"key":"category","label":"카테고리"},{"key":"status","label":"상태"},{"key":"current_participants","label":"참여"},{"key":"group_price","label":"공동가"},{"key":"is_approved","label":"승인"}]'
    :setting-schema="settingSchema"
    :point-schema="pointSchema"
    @open-user="u => { selectedUserId = u?.id; showUser = true }"
  />
  <AdminUserModal :show="showUser" :user-id="selectedUserId" @close="showUser=false" />
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AdminBoardManager from '../../components/AdminBoardManager.vue'
import AdminUserModal from '../../components/AdminUserModal.vue'

const showUser = ref(false)
const selectedUserId = ref(null)
const pending = ref([])

async function loadPending() {
  try {
    const { data } = await axios.get('/api/groupbuys', { params: { is_approved: 0, admin: 1, per_page: 20 } })
    pending.value = data.data?.data || []
  } catch {}
}

async function approve(id) {
  if (!confirm('승인하시겠습니까?')) return
  try { await axios.post(`/api/admin/groupbuys/${id}/approve`); loadPending() }
  catch (e) { alert(e.response?.data?.message || '실패') }
}

async function reject(id) {
  const reason = prompt('거절 사유를 입력하세요:')
  if (!reason) return
  try { await axios.post(`/api/admin/groupbuys/${id}/reject`, { reason }); loadPending() }
  catch (e) { alert(e.response?.data?.message || '실패') }
}

const settingSchema = {
  enabled:            { label: '게시판 활성화',             type: 'bool',   default: true },
  require_approval:   { label: '공구 등록 승인제',          type: 'bool',   default: true },
  require_business_doc:{label: '사업자등록증 필수',        type: 'bool',   default: true },
  allow_stripe:       { label: 'Stripe 결제 허용',          type: 'bool',   default: true },
  allow_point:        { label: '포인트 결제 허용',          type: 'bool',   default: true },
  min_participants:   { label: '최소 참여 인원',            type: 'number', default: 3 },
  max_discount_pct:   { label: '최대 할인율 (%)',           type: 'number', default: 70 },
  auto_close_days:    { label: '자동 마감 (일)',            type: 'number', default: 14 },
}

const pointSchema = {
  groupbuy_create:  { label: '공구 등록 (승인 후)',    default: 50, daily_max: 1 },
  groupbuy_join:    { label: '공구 참여',             default: 10, daily_max: 5 },
  groupbuy_complete:{ label: '공구 완료 (주최자)',    default: 100, daily_max: 0 },
  rejected:         { label: '거절된 공구 (-차감)',    is_deduction: true, default: -0, daily_max: 0 },
  reported:         { label: '신고 당함 (-차감)',      is_deduction: true, default: -20, daily_max: 0 },
}

onMounted(() => loadPending())
</script>
