<template>
<div>
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-xl font-black text-gray-800">📰 뉴스 관리</h1>
    <button @click="fetchNews" :disabled="fetching" class="bg-blue-500 text-white font-bold px-4 py-2 rounded-lg text-sm hover:bg-blue-600 disabled:opacity-50">
      {{ fetching ? '수집 중...' : '🔄 뉴스 수집' }}
    </button>
  </div>
  <AdminListView icon="📰" title="" api-url="/api/news"
    :extra-cols='[{"key":"source","label":"출처"},{"key":"category.name","label":"카테고리"}]'
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
async function fetchNews() {
  fetching.value = true
  try { await axios.post('/api/admin/fetch-news'); alert('뉴스 수집 완료!') } catch(e) { alert(e.response?.data?.message || '수집 실패') }
  fetching.value = false
}
</script>
