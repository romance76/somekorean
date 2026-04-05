<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-800">음악 관리</h2>
      <button @click="showAddCat = true" class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-700 transition">+ 카테고리 추가</button>
    </div>

    <!-- Categories -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="cat in categories" :key="cat.id" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-4 py-3 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span>{{ cat.emoji || '🎵' }}</span>
            <span class="font-bold text-gray-800 text-sm">{{ cat.name }}</span>
            <span class="text-xs text-gray-400">({{ cat.tracks?.length || cat.tracks_count || 0 }}곡)</span>
          </div>
          <div class="flex gap-1">
            <button @click="editCat(cat)" class="text-xs px-2 py-1 rounded bg-blue-50 text-blue-600 hover:bg-blue-100">수정</button>
            <button @click="deleteCat(cat)" class="text-xs px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100">삭제</button>
          </div>
        </div>
        <!-- Tracks -->
        <div class="divide-y divide-gray-50 max-h-60 overflow-y-auto">
          <div v-for="track in (cat.tracks || [])" :key="track.id" class="px-4 py-2 flex items-center gap-2">
            <span class="text-sm text-gray-800 flex-1 truncate">{{ track.title }}</span>
            <span class="text-xs text-gray-400 flex-shrink-0">{{ track.artist }}</span>
            <button @click="deleteTrack(cat.id, track.id)" class="text-xs text-red-400 hover:text-red-600 flex-shrink-0">x</button>
          </div>
        </div>
        <!-- Add track -->
        <div class="px-4 py-2 border-t border-gray-100">
          <div class="flex gap-2">
            <input v-model="newTrackUrl[cat.id]" type="text" placeholder="YouTube URL 입력"
              class="flex-1 border border-gray-200 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-red-500" />
            <button @click="addTrack(cat.id)" :disabled="!newTrackUrl[cat.id]" class="bg-red-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-red-700 disabled:opacity-50 transition">추가</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showAddCat" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showAddCat = false">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-gray-800 text-lg mb-4">{{ editingCat ? '카테고리 수정' : '카테고리 추가' }}</h3>
        <div class="space-y-3">
          <input v-model="catForm.name" type="text" placeholder="카테고리명" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
          <input v-model="catForm.emoji" type="text" placeholder="이모지 (예: 🎵)" maxlength="4" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
          <div class="flex justify-end gap-2">
            <button @click="showAddCat = false; editingCat = null" class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm hover:bg-gray-50">취소</button>
            <button @click="saveCat" :disabled="!catForm.name" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold hover:bg-red-700 disabled:opacity-50">저장</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
const categories = ref([]), showAddCat = ref(false), editingCat = ref(null)
const catForm = ref({ name: '', emoji: '🎵' })
const newTrackUrl = reactive({})
async function loadCategories() { try { const { data } = await axios.get('/api/admin/music/categories'); categories.value = data.data || data || [] } catch {} }
function editCat(cat) { editingCat.value = cat; catForm.value = { name: cat.name, emoji: cat.emoji || '🎵' }; showAddCat.value = true }
async function saveCat() {
  try {
    if (editingCat.value) { await axios.put(`/api/admin/music/categories/${editingCat.value.id}`, catForm.value) }
    else { await axios.post('/api/admin/music/categories', catForm.value) }
    showAddCat.value = false; editingCat.value = null; catForm.value = { name: '', emoji: '🎵' }; await loadCategories()
  } catch (e) { alert(e.response?.data?.message || '저장 실패') }
}
async function deleteCat(cat) { if (!confirm(`"${cat.name}" 카테고리를 삭제할까요?`)) return; try { await axios.delete(`/api/admin/music/categories/${cat.id}`); await loadCategories() } catch {} }
async function addTrack(catId) { if (!newTrackUrl[catId]) return; try { await axios.post(`/api/admin/music/categories/${catId}/tracks`, { url: newTrackUrl[catId] }); newTrackUrl[catId] = ''; await loadCategories() } catch (e) { alert(e.response?.data?.message || '추가 실패') } }
async function deleteTrack(catId, trackId) { try { await axios.delete(`/api/admin/music/categories/${catId}/tracks/${trackId}`); await loadCategories() } catch {} }
onMounted(loadCategories)
</script>
