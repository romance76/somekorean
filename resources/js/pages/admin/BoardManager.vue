<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-bold text-gray-800">게시판 관리</h2>
        <p class="text-xs text-gray-400 mt-0.5">게시판 추가, 수정, 순서 변경</p>
      </div>
      <button @click="showModal = true; editBoard = null; form = { name: '', slug: '', description: '' }"
        class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-700 transition">
        + 게시판 추가
      </button>
    </div>

    <!-- Board List -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="!boards.length" class="text-center py-12 text-gray-400 text-sm">게시판이 없습니다</div>
      <div v-else>
        <div v-for="(board, idx) in boards" :key="board.id"
          class="px-5 py-4 border-b border-gray-50 last:border-0 flex items-center gap-4 hover:bg-gray-50 transition">
          <!-- Reorder -->
          <div class="flex flex-col gap-0.5 flex-shrink-0">
            <button @click="moveUp(idx)" :disabled="idx === 0" class="text-gray-400 hover:text-gray-600 disabled:opacity-30">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
            </button>
            <button @click="moveDown(idx)" :disabled="idx === boards.length - 1" class="text-gray-400 hover:text-gray-600 disabled:opacity-30">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-800 text-sm">{{ board.name }}</p>
            <p class="text-xs text-gray-400">slug: {{ board.slug }} · {{ board.description || '-' }}</p>
          </div>
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full"
            :class="board.is_active ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-500'">
            {{ board.is_active ? '활성' : '비활성' }}
          </span>
          <div class="flex gap-1 flex-shrink-0">
            <button @click="openEdit(board)" class="text-xs px-2 py-1 rounded bg-blue-50 text-blue-600 hover:bg-blue-100">수정</button>
            <button @click="toggleActive(board)" class="text-xs px-2 py-1 rounded bg-yellow-50 text-yellow-600 hover:bg-yellow-100">
              {{ board.is_active ? '비활성' : '활성' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showModal = false">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-gray-800 text-lg mb-4">{{ editBoard ? '게시판 수정' : '게시판 추가' }}</h3>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">이름</label>
            <input v-model="form.name" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Slug (URL)</label>
            <input v-model="form.slug" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">설명</label>
            <input v-model="form.description" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button @click="showModal = false" class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm hover:bg-gray-50">취소</button>
            <button @click="saveBoard" :disabled="!form.name" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold hover:bg-red-700 disabled:opacity-50">저장</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const boards = ref([])
const showModal = ref(false)
const editBoard = ref(null)
const form = ref({ name: '', slug: '', description: '' })

async function loadBoards() {
  try { const { data } = await axios.get('/api/admin/boards'); boards.value = data.data || data || [] } catch {}
}

function openEdit(board) {
  editBoard.value = board
  form.value = { name: board.name, slug: board.slug, description: board.description || '' }
  showModal.value = true
}

async function saveBoard() {
  try {
    if (editBoard.value) {
      await axios.put(`/api/admin/boards/${editBoard.value.id}`, form.value)
    } else {
      await axios.post('/api/admin/boards', form.value)
    }
    showModal.value = false
    await loadBoards()
  } catch (e) { alert(e.response?.data?.message || '저장 실패') }
}

async function toggleActive(board) {
  try { await axios.post(`/api/admin/boards/${board.id}/toggle`); board.is_active = !board.is_active } catch {}
}

async function moveUp(idx) {
  if (idx === 0) return
  const arr = [...boards.value]; [arr[idx - 1], arr[idx]] = [arr[idx], arr[idx - 1]]; boards.value = arr
  await saveOrder()
}

async function moveDown(idx) {
  if (idx >= boards.value.length - 1) return
  const arr = [...boards.value]; [arr[idx], arr[idx + 1]] = [arr[idx + 1], arr[idx]]; boards.value = arr
  await saveOrder()
}

async function saveOrder() {
  try { await axios.post('/api/admin/boards/reorder', { ids: boards.value.map(b => b.id) }) } catch {}
}

onMounted(loadBoards)
</script>
