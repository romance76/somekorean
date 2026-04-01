<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">🎵 음악 관리</h1>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Categories -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">카테고리 관리</h2>
          <button @click="showCatForm = !showCatForm" class="px-3 py-1.5 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700">+ 추가</button>
        </div>
        <div v-if="showCatForm" class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 mb-4">
          <div class="grid grid-cols-2 gap-2 mb-2">
            <input v-model="catForm.name" type="text" placeholder="카테고리명 (예: 트로트)" class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500">
            <input v-model="catForm.icon" type="text" placeholder="이모지 (예: 🎶)" maxlength="5" class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500">
          </div>
          <input v-model="catForm.description" type="text" placeholder="설명 (선택)" class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-purple-500">
          <div class="flex gap-2">
            <button @click="showCatForm = false" class="flex-1 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 text-sm">취소</button>
            <button @click="createCategory" class="flex-1 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700">저장</button>
          </div>
        </div>
        <div class="space-y-2">
          <div v-for="cat in categories" :key="cat.id"
            :class="['flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors', selectedCat && selectedCat.id === cat.id ? 'bg-purple-100 dark:bg-purple-900/30' : 'hover:bg-gray-50 dark:hover:bg-gray-700']"
            @click="selectCategory(cat)">
            <span class="text-xl">{{ cat.icon || '🎵' }}</span>
            <div class="flex-1">
              <div class="font-medium text-gray-900 dark:text-white">{{ cat.name }}</div>
              <div class="text-xs text-gray-500">{{ cat.tracks_count }}곡 · {{ cat.is_active ? '활성' : '비활성' }}</div>
            </div>
            <div class="flex gap-1">
              <button @click.stop="toggleCatActive(cat)" :class="['px-2 py-1 rounded text-xs', cat.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">{{ cat.is_active ? '활성' : '비활성' }}</button>
              <button @click.stop="deleteCategory(cat.id)" class="px-2 py-1 rounded text-xs bg-red-100 text-red-600 hover:bg-red-200">삭제</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tracks -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white">
            {{ selectedCat ? selectedCat.name + ' 곡 목록' : '카테고리를 선택하세요' }}
          </h2>
          <button v-if="selectedCat" @click="showTrackForm = !showTrackForm" class="px-3 py-1.5 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700">+ 추가</button>
        </div>
        <div v-if="showTrackForm && selectedCat" class="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 mb-4">
          <input v-model="trackForm.youtube_url" type="text" placeholder="YouTube URL" class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-purple-500">
          <div v-if="previewYoutubeId" class="mb-2">
            <img :src="'https://img.youtube.com/vi/' + previewYoutubeId + '/mqdefault.jpg'" class="h-16 rounded-lg object-cover">
          </div>
          <div class="flex gap-2">
            <button @click="showTrackForm = false" class="flex-1 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 text-sm">취소</button>
            <button @click="createTrack" class="flex-1 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700">저장</button>
          </div>
        </div>
        <div v-if="!selectedCat" class="text-center py-8 text-gray-400">← 카테고리를 선택해주세요</div>
        <div v-else-if="tracksLoading" class="text-center py-8"><div class="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600 mx-auto"></div></div>
        <div v-else-if="catTracks.length === 0" class="text-center py-8 text-gray-400">아직 곡이 없습니다</div>
        <div v-else class="space-y-2 max-h-96 overflow-y-auto">
          <div v-for="track in catTracks" :key="track.id" class="flex items-center gap-3 p-2.5 border border-gray-100 dark:border-gray-700 rounded-xl">
            <img v-if="track.thumbnail" :src="track.thumbnail" class="w-14 h-10 rounded-lg object-cover flex-shrink-0">
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ track.title }}</div>
              <div class="text-xs text-gray-500">{{ track.artist || '-' }} · {{ track.play_count }}회 재생</div>
            </div>
            <div class="flex gap-1 flex-shrink-0">
              <button @click="toggleTrackActive(track)" :class="['px-2 py-1 rounded text-xs', track.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500']">{{ track.is_active ? '활성' : '숨김' }}</button>
              <button @click="deleteTrack(track.id)" class="px-2 py-1 rounded text-xs bg-red-100 text-red-600 hover:bg-red-200">삭제</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const categories = ref([])
const selectedCat = ref(null)
const catTracks = ref([])
const tracksLoading = ref(false)

const showCatForm = ref(false)
const catForm = ref({ name: '', icon: '🎵', description: '' })
const showTrackForm = ref(false)
const trackForm = ref({ youtube_url: '' })

const previewYoutubeId = computed(() => {
  const url = trackForm.value.youtube_url
  const m = url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/)
  return m ? m[1] : null
})

async function loadCategories() {
  const { data } = await axios.get('/api/admin/music/categories')
  categories.value = data
}

async function selectCategory(cat) {
  selectedCat.value = cat
  tracksLoading.value = true
  try {
    const { data } = await axios.get('/api/music/categories/' + cat.id + '/tracks')
    catTracks.value = data.tracks
  } catch (e) { catTracks.value = [] }
  tracksLoading.value = false
}

async function createCategory() {
  if (!catForm.value.name.trim()) return
  try {
    await axios.post('/api/admin/music/categories', catForm.value)
    catForm.value = { name: '', icon: '🎵', description: '' }
    showCatForm.value = false
    await loadCategories()
  } catch (e) { alert('생성 실패') }
}

async function toggleCatActive(cat) {
  await axios.put('/api/admin/music/categories/' + cat.id, { is_active: !cat.is_active })
  await loadCategories()
}

async function deleteCategory(id) {
  if (!confirm('카테고리와 모든 곡이 삭제됩니다. 계속하시겠습니까?')) return
  await axios.delete('/api/admin/music/categories/' + id)
  selectedCat.value = null
  catTracks.value = []
  await loadCategories()
}

async function createTrack() {
  if (!trackForm.value.youtube_url.trim()) return
  try {
    await axios.post('/api/admin/music/tracks', { youtube_url: trackForm.value.youtube_url, category_id: selectedCat.value.id })
    trackForm.value = { youtube_url: '' }
    showTrackForm.value = false
    await selectCategory(selectedCat.value)
    await loadCategories()
  } catch (e) { alert(e.response?.data?.message || '추가 실패') }
}

async function toggleTrackActive(track) {
  await axios.put('/api/admin/music/tracks/' + track.id, { is_active: !track.is_active })
  await selectCategory(selectedCat.value)
}

async function deleteTrack(id) {
  if (!confirm('삭제하시겠습니까?')) return
  await axios.delete('/api/admin/music/tracks/' + id)
  await selectCategory(selectedCat.value)
  await loadCategories()
}

loadCategories()
</script>
