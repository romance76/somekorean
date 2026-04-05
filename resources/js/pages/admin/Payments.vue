<template>
  <div class="space-y-5">
    <h2 class="text-lg font-bold text-gray-800">결제/포인트 관리</h2>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-wrap gap-3">
      <select v-model="statusFilter" @change="loadPayments" class="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white">
        <option value="">전체 상태</option><option value="completed">완료</option><option value="pending">대기</option><option value="failed">실패</option>
      </select>
      <input v-model="dateFrom" type="date" @change="loadPayments" class="border border-gray-200 rounded-lg px-3 py-2 text-sm" />
      <span class="text-gray-400 self-center">~</span>
      <input v-model="dateTo" type="date" @change="loadPayments" class="border border-gray-200 rounded-lg px-3 py-2 text-sm" />
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto"><table class="w-full text-sm"><thead class="bg-gray-50 border-b border-gray-200"><tr>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">회원</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">금액</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">포인트</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">상태</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">유형</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">날짜</th>
      </tr></thead><tbody class="divide-y divide-gray-50">
        <tr v-for="p in payments" :key="p.id" class="hover:bg-gray-50">
          <td class="px-4 py-3 text-gray-800">{{ p.user?.name || '-' }}</td>
          <td class="px-4 py-3 text-right font-medium text-gray-700">${{ (p.amount || 0).toFixed(2) }}</td>
          <td class="px-4 py-3 text-right text-gray-700">{{ (p.points || 0).toLocaleString() }}P</td>
          <td class="px-4 py-3"><span class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="{'bg-green-50 text-green-600': p.status==='completed', 'bg-yellow-50 text-yellow-600': p.status==='pending', 'bg-red-50 text-red-600': p.status==='failed'}">{{ {completed:'완료',pending:'대기',failed:'실패'}[p.status] || p.status }}</span></td>
          <td class="px-4 py-3 text-gray-600 text-xs">{{ p.type || '-' }}</td>
          <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(p.created_at) }}</td>
        </tr>
      </tbody></table></div>
      <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-100 flex justify-center gap-1">
        <button v-for="p in Math.min(totalPages, 10)" :key="p" @click="page = p; loadPayments()" class="w-8 h-8 rounded text-xs font-medium" :class="p === page ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">{{ p }}</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
const payments = ref([]), statusFilter = ref(''), dateFrom = ref(''), dateTo = ref(''), page = ref(1), total = ref(0)
const totalPages = computed(() => Math.ceil(total.value / 20))
function formatDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '' }
async function loadPayments() { try { const { data } = await axios.get('/api/admin/payments', { params: { status: statusFilter.value, from: dateFrom.value, to: dateTo.value, page: page.value } }); payments.value = data.data || []; total.value = data.total || data.meta?.total || 0 } catch {} }
onMounted(loadPayments)
</script>
