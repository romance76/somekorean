<template>
<div>
  <div class="flex items-center justify-between mb-4">
    <h2 class="text-lg font-bold">🤝 공동구매 관리</h2>
    <div class="flex gap-2">
      <select v-model="filter" @change="load()" class="border rounded px-2 py-1 text-sm">
        <option value="">전체</option>
        <option value="pending">승인 대기</option>
        <option value="recruiting">모집중</option>
        <option value="confirmed">확정</option>
        <option value="completed">완료</option>
        <option value="cancelled">취소</option>
      </select>
    </div>
  </div>

  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>

  <div v-else class="bg-white rounded-xl border overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 text-xs text-gray-500">
        <tr>
          <th class="px-3 py-2 text-left">ID</th>
          <th class="px-3 py-2 text-left">제목</th>
          <th class="px-3 py-2">카테고리</th>
          <th class="px-3 py-2">상태</th>
          <th class="px-3 py-2">승인</th>
          <th class="px-3 py-2">참여</th>
          <th class="px-3 py-2">가격</th>
          <th class="px-3 py-2">작성자</th>
          <th class="px-3 py-2">관리</th>
        </tr>
      </thead>
      <tbody class="divide-y">
        <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50">
          <td class="px-3 py-2 text-gray-400">{{ item.id }}</td>
          <td class="px-3 py-2 font-medium truncate max-w-[200px]">{{ item.title }}</td>
          <td class="px-3 py-2 text-center text-xs">{{ item.category || '-' }}</td>
          <td class="px-3 py-2 text-center">
            <span class="text-xs px-1.5 py-0.5 rounded font-bold"
              :class="{'bg-green-100 text-green-700':item.status==='recruiting','bg-blue-100 text-blue-700':item.status==='confirmed','bg-gray-100 text-gray-500':item.status==='completed','bg-red-100 text-red-600':item.status==='cancelled'}">
              {{ {recruiting:'모집중',confirmed:'확정',completed:'완료',cancelled:'취소'}[item.status] || item.status }}
            </span>
          </td>
          <td class="px-3 py-2 text-center">
            <span v-if="item.is_approved" class="text-green-600 text-xs font-bold">승인됨</span>
            <span v-else class="text-orange-500 text-xs font-bold">대기중</span>
          </td>
          <td class="px-3 py-2 text-center text-xs">{{ item.current_participants }}/{{ item.max_participants || item.min_participants }}</td>
          <td class="px-3 py-2 text-center text-xs">${{ item.original_price }} → ${{ item.group_price }}</td>
          <td class="px-3 py-2 text-center text-xs text-gray-500">{{ item.user?.name || '-' }}</td>
          <td class="px-3 py-2">
            <div class="flex items-center gap-1 justify-center">
              <button @click="openDetail(item)" class="text-blue-600 hover:underline text-xs">상세</button>
              <button v-if="!item.is_approved" @click="approve(item.id)" class="text-green-600 hover:underline text-xs">승인</button>
              <button v-if="!item.is_approved" @click="reject(item.id)" class="text-red-500 hover:underline text-xs">거절</button>
              <button v-if="item.status==='recruiting'" @click="complete(item.id)" class="text-purple-600 hover:underline text-xs">완료</button>
              <button @click="del(item.id)" class="text-red-400 hover:underline text-xs">삭제</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <Pagination :page="page" :lastPage="lastPage" @page="load" />

  <!-- 상세 모달 -->
  <div v-if="detail" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4" @click.self="detail=null">
    <div class="bg-white rounded-xl max-w-lg w-full max-h-[80vh] overflow-y-auto p-5">
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-bold">{{ detail.title }}</h3>
        <button @click="detail=null" class="text-gray-400 text-lg">&times;</button>
      </div>
      <div class="text-sm space-y-2 text-gray-600">
        <div><b>카테고리:</b> {{ detail.category }}</div>
        <div><b>상태:</b> {{ detail.status }} | <b>승인:</b> {{ detail.is_approved ? '승인됨' : '대기중' }}</div>
        <div><b>가격:</b> ${{ detail.original_price }} → ${{ detail.group_price }}</div>
        <div><b>참여:</b> {{ detail.current_participants }}/{{ detail.max_participants || detail.min_participants }}명</div>
        <div><b>종료 유형:</b> {{ {target_met:'목표달성시',time_limit:'시간제한',flexible:'유동적'}[detail.end_type] }}</div>
        <div><b>결제 방식:</b> {{ {point:'포인트',stripe:'Stripe',both:'둘다',none:'없음'}[detail.payment_method] }}</div>
        <div><b>마감:</b> {{ detail.deadline }}</div>
        <div v-if="detail.discount_tiers"><b>할인 티어:</b>
          <div v-for="t in detail.discount_tiers" :key="t.min_people" class="ml-3 text-xs">{{ t.min_people }}명 이상 → {{ t.discount_pct }}% 할인</div>
        </div>
        <div v-if="detail.business_doc"><b>사업자 등록증:</b> <a :href="detail.business_doc" target="_blank" class="text-blue-600 underline">보기</a></div>
        <div v-if="detail.rejection_reason"><b>거절 사유:</b> <span class="text-red-500">{{ detail.rejection_reason }}</span></div>
        <div class="border-t pt-2 mt-2 whitespace-pre-wrap text-xs">{{ detail.content }}</div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const items = ref([])
const loading = ref(true)
const filter = ref('')
const page = ref(1)
const lastPage = ref(1)
const detail = ref(null)

async function load(p = 1) {
  loading.value = true; page.value = p
  const params = { page: p, per_page: 20, admin: 1 }
  if (filter.value === 'pending') { params.is_approved = 0 }
  else if (filter.value) params.status = filter.value
  try {
    const { data } = await axios.get('/api/groupbuys', { params })
    items.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
  } catch {}
  loading.value = false
}

async function openDetail(item) {
  try { const { data } = await axios.get(`/api/groupbuys/${item.id}`); detail.value = data.data } catch { detail.value = item }
}

async function approve(id) {
  if (!confirm('승인하시겠습니까?')) return
  try { await axios.post(`/api/admin/groupbuys/${id}/approve`); load(page.value) } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function reject(id) {
  const reason = prompt('거절 사유를 입력하세요:')
  if (!reason) return
  try { await axios.post(`/api/admin/groupbuys/${id}/reject`, { reason }); load(page.value) } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function complete(id) {
  if (!confirm('완료 처리하시겠습니까?')) return
  try { await axios.post(`/api/admin/groupbuys/${id}/complete`); load(page.value) } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function del(id) {
  if (!confirm('삭제하시겠습니까?')) return
  try { await axios.delete(`/api/admin/groupbuys/${id}`); items.value = items.value.filter(x => x.id !== id) } catch (e) { alert(e.response?.data?.message || '삭제 실패') }
}

onMounted(() => load())
</script>
