<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-gray-900">회원 관리</h1>
        <p class="text-sm text-gray-500 mt-0.5">전체 회원 목록 및 관리</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div class="flex flex-wrap gap-3">
        <input v-model="search" type="text" placeholder="이름, 이메일 검색..."
          class="flex-1 min-w-[200px] border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
          @input="debounceLoad" />
        <select v-model="roleFilter" @change="loadUsers"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-red-500">
          <option value="">전체 역할</option>
          <option value="admin">관리자</option>
          <option value="user">일반회원</option>
        </select>
        <select v-model="statusFilter" @change="loadUsers"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-red-500">
          <option value="">전체 상태</option>
          <option value="active">활성</option>
          <option value="banned">차단</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">회원</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">이메일</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">역할</th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600">포인트</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">상태</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">가입일</th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-red-400 to-red-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0 overflow-hidden">
                    <img v-if="u.avatar" :src="u.avatar" class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
                    <span v-else>{{ (u.name || '?')[0] }}</span>
                  </div>
                  <div>
                    <p class="font-semibold text-gray-800">{{ u.name }}</p>
                    <p class="text-xs text-gray-400">@{{ u.username }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ u.email }}</td>
              <td class="px-4 py-3">
                <span class="text-xs font-semibold px-2 py-0.5 rounded-full"
                  :class="u.is_admin ? 'bg-red-50 text-red-600' : 'bg-gray-50 text-gray-600'">
                  {{ u.is_admin ? '관리자' : '회원' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right font-medium text-gray-700">{{ (u.points || 0).toLocaleString() }}P</td>
              <td class="px-4 py-3">
                <span class="text-xs font-semibold px-2 py-0.5 rounded-full"
                  :class="u.banned ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'">
                  {{ u.banned ? '차단' : '활성' }}
                </span>
              </td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(u.created_at) }}</td>
              <td class="px-4 py-3 text-right">
                <div class="flex justify-end gap-1">
                  <button @click="toggleAdmin(u)" class="text-xs px-2 py-1 rounded bg-blue-50 text-blue-600 hover:bg-blue-100 transition">
                    {{ u.is_admin ? '관리자해제' : '관리자지정' }}
                  </button>
                  <button @click="toggleBan(u)" class="text-xs px-2 py-1 rounded transition"
                    :class="u.banned ? 'bg-green-50 text-green-600 hover:bg-green-100' : 'bg-red-50 text-red-600 hover:bg-red-100'">
                    {{ u.banned ? '해제' : '차단' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-100 flex items-center justify-between">
        <span class="text-xs text-gray-500">총 {{ total }}명</span>
        <div class="flex gap-1">
          <button v-for="p in totalPages" :key="p" @click="page = p; loadUsers()"
            class="w-8 h-8 rounded text-xs font-medium transition"
            :class="p === page ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
            {{ p }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const users = ref([])
const search = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const page = ref(1)
const total = ref(0)
const perPage = ref(20)
let debounceTimer = null

const totalPages = computed(() => Math.ceil(total.value / perPage.value))

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR')
}

function debounceLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; loadUsers() }, 400)
}

async function loadUsers() {
  try {
    const { data } = await axios.get('/api/admin/users', {
      params: { search: search.value, role: roleFilter.value, status: statusFilter.value, page: page.value }
    })
    users.value = data.data || []
    total.value = data.total || data.meta?.total || 0
  } catch { /* ignore */ }
}

async function toggleAdmin(u) {
  try {
    await axios.post(`/api/admin/users/${u.id}/toggle-admin`)
    u.is_admin = !u.is_admin
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function toggleBan(u) {
  try {
    await axios.post(`/api/admin/users/${u.id}/toggle-ban`)
    u.banned = !u.banned
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

onMounted(loadUsers)
</script>
