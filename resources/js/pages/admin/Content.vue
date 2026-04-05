<template>
  <div class="space-y-5">
    <!-- Tabs -->
    <div class="flex gap-2 flex-wrap">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key; loadTab()"
        class="px-4 py-2 rounded-xl text-sm font-semibold transition"
        :class="activeTab === tab.key ? 'bg-red-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'">
        {{ tab.label }}
        <span v-if="tab.count" class="ml-1 text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded-full">{{ tab.count }}</span>
      </button>
    </div>

    <!-- Search & Filter -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-wrap gap-3">
      <input v-model="search" type="text" placeholder="검색..." @input="debounceLoad"
        class="flex-1 min-w-[200px] border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
      <select v-model="boardFilter" @change="loadTab"
        class="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-red-500">
        <option value="">전체 게시판</option>
        <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">제목</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">게시판</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">작성자</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">상태</th>
              <th class="text-left px-4 py-3 font-semibold text-gray-600">작성일</th>
              <th class="text-right px-4 py-3 font-semibold text-gray-600">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3 font-medium text-gray-800 max-w-xs truncate">{{ item.title }}</td>
              <td class="px-4 py-3 text-gray-600 text-xs">{{ item.board?.name || '-' }}</td>
              <td class="px-4 py-3 text-gray-600">{{ item.user?.name }}</td>
              <td class="px-4 py-3">
                <span class="text-xs font-semibold px-2 py-0.5 rounded-full"
                  :class="item.is_hidden ? 'bg-red-50 text-red-600' : item.is_pinned ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600'">
                  {{ item.is_hidden ? '숨김' : item.is_pinned ? '고정' : '공개' }}
                </span>
              </td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(item.created_at) }}</td>
              <td class="px-4 py-3 text-right">
                <div class="flex justify-end gap-1">
                  <button @click="togglePin(item)" class="text-xs px-2 py-1 rounded bg-blue-50 text-blue-600 hover:bg-blue-100">
                    {{ item.is_pinned ? '고정해제' : '고정' }}
                  </button>
                  <button @click="toggleHide(item)" class="text-xs px-2 py-1 rounded bg-yellow-50 text-yellow-600 hover:bg-yellow-100">
                    {{ item.is_hidden ? '공개' : '숨김' }}
                  </button>
                  <button @click="deleteItem(item)" class="text-xs px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100">삭제</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-100 flex items-center justify-center gap-1">
        <button v-for="p in Math.min(totalPages, 10)" :key="p" @click="page = p; loadTab()"
          class="w-8 h-8 rounded text-xs font-medium transition"
          :class="p === page ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">{{ p }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const items = ref([])
const boards = ref([])
const search = ref('')
const boardFilter = ref('')
const activeTab = ref('all')
const page = ref(1)
const total = ref(0)
let debounceTimer = null

const tabs = [
  { key: 'all', label: '전체', count: 0 },
  { key: 'pinned', label: '고정', count: 0 },
  { key: 'hidden', label: '숨김', count: 0 },
  { key: 'reported', label: '신고', count: 0 },
]

const totalPages = computed(() => Math.ceil(total.value / 20))

function formatDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '' }
function debounceLoad() { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => { page.value = 1; loadTab() }, 400) }

async function loadTab() {
  try {
    const { data } = await axios.get('/api/admin/posts', {
      params: { search: search.value, board: boardFilter.value, status: activeTab.value, page: page.value }
    })
    items.value = data.data || []
    total.value = data.total || data.meta?.total || 0
  } catch { /* ignore */ }
}

async function loadBoards() {
  try { const { data } = await axios.get('/api/admin/boards'); boards.value = data.data || data || [] } catch {}
}

async function togglePin(item) {
  try { await axios.post(`/api/admin/posts/${item.id}/pin`); item.is_pinned = !item.is_pinned } catch {}
}
async function toggleHide(item) {
  try { await axios.post(`/api/admin/posts/${item.id}/hide`); item.is_hidden = !item.is_hidden } catch {}
}
async function deleteItem(item) {
  if (!confirm('삭제할까요?')) return
  try { await axios.delete(`/api/admin/posts/${item.id}`); items.value = items.value.filter(i => i.id !== item.id) } catch {}
}

onMounted(() => { loadTab(); loadBoards() })
</script>
