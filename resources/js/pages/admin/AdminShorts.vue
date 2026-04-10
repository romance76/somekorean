<template>
<div>
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-xl font-black text-gray-800">📱 숏츠 관리</h1>
    <button @click="fetchShorts" :disabled="fetching" class="bg-blue-500 text-white font-bold px-4 py-2 rounded-lg text-sm hover:bg-blue-600 disabled:opacity-50">
      {{ fetching ? '수집 중...' : '🔄 YouTube 숏츠 수집 (100개, 한국 75%)' }}
    </button>
  </div>

  <!-- 통계 카드 -->
  <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
    <div class="bg-white rounded-xl shadow-sm border p-3">
      <div class="text-[10px] text-gray-500">전체</div>
      <div class="text-xl font-black text-gray-800">{{ stats.total || 0 }}</div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-3">
      <div class="text-[10px] text-gray-500">활성</div>
      <div class="text-xl font-black text-green-600">{{ stats.active || 0 }}</div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-3">
      <div class="text-[10px] text-gray-500">시스템 수집</div>
      <div class="text-xl font-black text-blue-600">{{ stats.system || 0 }}</div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-3">
      <div class="text-[10px] text-gray-500">유저 업로드</div>
      <div class="text-xl font-black text-purple-600">{{ stats.user_uploaded || 0 }}</div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border p-3">
      <div class="text-[10px] text-gray-500">오늘 추가</div>
      <div class="text-xl font-black text-amber-600">{{ stats.today || 0 }}</div>
    </div>
  </div>

  <AdminListView icon="📱" title="" api-url="/api/admin/shorts"
    :extra-cols='[{"key":"youtube_id","label":"YouTube ID"},{"key":"duration","label":"초"}]'
    @open-user="u => { selectedUserId = u?.id; showUser = true }" />
  <AdminUserModal :show="showUser" :user-id="selectedUserId" @close="showUser=false" />
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import AdminListView from '../../components/AdminListView.vue'
import AdminUserModal from '../../components/AdminUserModal.vue'
const showUser = ref(false)
const selectedUserId = ref(null)
const fetching = ref(false)
const stats = ref({})

async function loadStats() {
  try { const { data } = await axios.get('/api/admin/shorts/stats'); stats.value = data.data || {} } catch {}
}

async function fetchShorts() {
  fetching.value = true
  try {
    const { data } = await axios.post('/api/admin/fetch-shorts')
    alert(data.message || '숏츠 수집 완료!')
    await loadStats()
    location.reload()
  } catch(e) { alert(e.response?.data?.message || '수집 실패') }
  fetching.value = false
}

onMounted(loadStats)
</script>
