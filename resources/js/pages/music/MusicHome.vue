<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">🎵 음악듣기</h1>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else class="grid grid-cols-12 gap-4">
      <!-- 카테고리 -->
      <div class="col-span-12 lg:col-span-3">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-4 py-3 border-b font-bold text-sm text-amber-900">🎵 카테고리</div>
          <div class="py-1">
            <button v-for="cat in categories" :key="cat.id" @click="selectCategory(cat)"
              class="w-full text-left px-4 py-2.5 text-sm transition"
              :class="activeCat?.id === cat.id ? 'bg-amber-50 text-amber-700 font-bold' : 'text-gray-600 hover:bg-amber-50/50'">
              {{ cat.name }}
            </button>
          </div>
        </div>
      </div>

      <!-- 트랙 목록 -->
      <div class="col-span-12 lg:col-span-6">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div class="px-4 py-3 border-b font-bold text-sm text-amber-900">
            🎶 {{ activeCat?.name || '트랙 선택' }}
          </div>
          <div v-if="!tracks.length" class="py-8 text-center text-sm text-gray-400">카테고리를 선택해주세요</div>
          <div v-for="(track, i) in tracks" :key="track.id"
            class="flex items-center gap-3 px-4 py-3 border-b last:border-0 hover:bg-amber-50/50 transition cursor-pointer"
            :class="playing?.id === track.id ? 'bg-amber-50' : ''"
            @click="playTrack(track)">
            <span class="text-xs text-gray-400 w-5 text-center">{{ i + 1 }}</span>
            <div class="w-8 h-8 bg-amber-100 rounded flex items-center justify-center text-sm flex-shrink-0">
              {{ playing?.id === track.id ? '🔊' : '🎵' }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-800 truncate">{{ track.title }}</div>
              <div class="text-[10px] text-gray-400">{{ track.artist }}</div>
            </div>
            <span class="text-[10px] text-gray-400">{{ formatDuration(track.duration) }}</span>
          </div>
        </div>
      </div>

      <!-- 플레이어 -->
      <div class="col-span-12 lg:col-span-3">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden sticky top-20">
          <div class="px-4 py-3 border-b font-bold text-sm text-amber-900">🎧 Now Playing</div>
          <div v-if="playing" class="p-4">
            <div class="aspect-video bg-gray-900 rounded-lg overflow-hidden mb-3">
              <iframe :src="`https://www.youtube.com/embed/${playing.youtube_id}?autoplay=1`"
                class="w-full h-full" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
            </div>
            <div class="text-sm font-bold text-gray-800">{{ playing.title }}</div>
            <div class="text-xs text-gray-400 mt-0.5">{{ playing.artist }}</div>
          </div>
          <div v-else class="p-4 text-center text-sm text-gray-400">트랙을 선택해주세요</div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const categories = ref([])
const tracks = ref([])
const activeCat = ref(null)
const playing = ref(null)
const loading = ref(true)

function formatDuration(sec) {
  if (!sec) return '--:--'
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

async function selectCategory(cat) {
  activeCat.value = cat
  try {
    const { data } = await axios.get(`/api/music/tracks/${cat.id}`)
    tracks.value = data.data || []
  } catch {}
}

function playTrack(track) { playing.value = track }

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/music/categories')
    categories.value = data.data || []
    if (categories.value.length) selectCategory(categories.value[0])
  } catch {}
  loading.value = false
})
</script>
