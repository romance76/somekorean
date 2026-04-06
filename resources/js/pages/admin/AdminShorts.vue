<template>
<div>
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-xl font-black text-gray-800">📱 숏츠 관리</h1>
    <button @click="fetchShorts" :disabled="fetching" class="bg-blue-500 text-white font-bold px-4 py-2 rounded-lg text-sm hover:bg-blue-600 disabled:opacity-50">
      {{ fetching ? '수집 중...' : '🔄 YouTube 숏츠 수집' }}
    </button>
  </div>
  <AdminListView icon="📱" title="" api-url="/api/shorts"
    :extra-cols='[{"key":"youtube_id","label":"YouTube ID"}]'
    @open-user="u => { selectedUserId = u?.id; showUser = true }" />
  <AdminUserModal :show="showUser" :user-id="selectedUserId" @close="showUser=false" />
</div>
</template>
<script setup>
import { ref } from 'vue'
import axios from 'axios'
import AdminListView from '../../components/AdminListView.vue'
import AdminUserModal from '../../components/AdminUserModal.vue'
const showUser = ref(false)
const selectedUserId = ref(null)
const fetching = ref(false)
async function fetchShorts() {
  fetching.value = true
  try { await axios.post('/api/admin/fetch-shorts'); alert('숏츠 수집 완료!') } catch(e) { alert(e.response?.data?.message || '수집 실패') }
  fetching.value = false
}
</script>
