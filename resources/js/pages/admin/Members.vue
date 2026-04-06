<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">👥 회원관리</h1>
  <div class="bg-white rounded-xl shadow-sm border p-3 mb-4">
    <form @submit.prevent="loadUsers()" class="flex gap-2">
      <input v-model="search" type="text" placeholder="이름 또는 이메일 검색..." class="flex-1 border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-amber-400" />
      <select v-model="roleFilter" @change="loadUsers()" class="border rounded-lg px-2 py-2 text-sm outline-none">
        <option value="">전체</option><option value="admin">관리자</option><option value="user">일반</option>
      </select>
      <button type="submit" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm">검색</button>
    </form>
  </div>
  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
  <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 border-b"><tr>
        <th class="px-3 py-2 text-left text-xs text-gray-500">이름</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">이메일</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">역할</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">포인트</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">상태</th>
        <th class="px-3 py-2 text-xs text-gray-500">관리</th>
      </tr></thead>
      <tbody>
        <tr v-for="u in users" :key="u.id" class="border-b last:border-0 hover:bg-amber-50/30">
          <td class="px-3 py-2.5 font-semibold text-gray-800">{{ u.name }}</td>
          <td class="px-3 py-2.5 text-gray-500">{{ u.email }}</td>
          <td class="px-3 py-2.5"><span class="text-[10px] px-2 py-0.5 rounded-full font-bold" :class="u.role==='admin'?'bg-purple-100 text-purple-700':'bg-gray-100 text-gray-600'">{{ u.role }}</span></td>
          <td class="px-3 py-2.5 text-amber-600 font-semibold">{{ u.points }}P</td>
          <td class="px-3 py-2.5"><span :class="u.is_banned?'text-red-500':'text-green-500'" class="text-xs font-bold">{{ u.is_banned ? '정지' : '활동' }}</span></td>
          <td class="px-3 py-2.5 text-center">
            <button v-if="!u.is_banned" @click="banUser(u)" class="text-red-400 text-xs hover:text-red-600">정지</button>
            <button v-else @click="unbanUser(u)" class="text-green-400 text-xs hover:text-green-600">해제</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
    <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="loadUsers(pg)"
      class="px-3 py-1 rounded text-sm" :class="pg===page?'bg-amber-400 text-amber-900 font-bold':'bg-white border text-gray-600'">{{ pg }}</button>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const users = ref([])
const loading = ref(true)
const search = ref('')
const roleFilter = ref('')
const page = ref(1)
const lastPage = ref(1)
async function loadUsers(p = 1) {
  loading.value = true; page.value = p
  const params = { page: p }
  if (search.value) params.search = search.value
  if (roleFilter.value) params.role = roleFilter.value
  try { const { data } = await axios.get('/api/admin/users', { params }); users.value = data.data?.data || []; lastPage.value = data.data?.last_page || 1 } catch {}
  loading.value = false
}
async function banUser(u) {
  if (!confirm(`${u.name}을(를) 정지하시겠습니까?`)) return
  try { await axios.post(`/api/admin/users/${u.id}/ban`, { reason: '관리자 정지' }); u.is_banned = true } catch {}
}
async function unbanUser(u) {
  try { await axios.post(`/api/admin/users/${u.id}/unban`); u.is_banned = false } catch {}
}
onMounted(() => loadUsers())
</script>
