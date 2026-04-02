<template>
  <div class="min-h-screen bg-gray-900 pb-16">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">

      <!-- Banner -->
      <div class="bg-gradient-to-r from-purple-700 to-indigo-600 text-white px-6 py-5 rounded-2xl mb-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-black">🎵 음악듣기</h1>
            <p class="text-sm opacity-80 mt-0.5">한인 커뮤니티 뮤직 스트리밍</p>
          </div>
          <div class="flex gap-2">
            <button @click="playAll" class="bg-white/20 backdrop-blur text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-white/30">▶ 전체재생</button>
            <button @click="playShuffleAll" class="bg-white/20 backdrop-blur text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-white/30">🔀 셔플</button>
          </div>
        </div>
      </div>

      <!-- Category tabs -->
      <div class="flex gap-2 overflow-x-auto pb-3 mb-4" style="scrollbar-width:none">
        <button v-for="cat in categories" :key="cat.id"
          @click="selectCategory(cat)"
          class="flex-shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition"
          :class="selectedCat?.id === cat.id ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'">
          {{ cat.emoji || '🎵' }} {{ cat.name }}
        </button>
        <button v-if="authStore.isLoggedIn" @click="showMyPlaylists = !showMyPlaylists"
          class="flex-shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition"
          :class="showMyPlaylists ? 'bg-yellow-500 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'">
          ⭐ 내 뮤직함
        </button>
      </div>

      <!-- Track count + sort -->
      <div class="flex items-center justify-between mb-3">
        <p class="text-gray-400 text-sm">{{ currentPlaylist.length }}곡</p>
      </div>

      <!-- 3-column grid -->
      <div v-if="tracksLoading" class="text-center py-16 text-gray-500">불러오는 중...</div>
      <div v-else-if="currentPlaylist.length === 0" class="text-center py-16 text-gray-500">곡이 없습니다</div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        <div v-for="(track, idx) in currentPlaylist" :key="track.id || idx"
          @click="playTrack(track, idx)"
          class="flex items-center gap-3 bg-gray-800 hover:bg-gray-750 rounded-xl p-3 cursor-pointer transition group"
          :class="{ 'ring-2 ring-purple-500 bg-purple-900/30': musicStore.currentTrack?.youtubeId === extractId(track) }">
          <!-- Thumbnail -->
          <div class="relative w-14 h-14 rounded-lg overflow-hidden bg-gray-700 flex-shrink-0">
            <img v-if="track.youtube_id || track.url"
              :src="'https://img.youtube.com/vi/' + extractId(track) + '/mqdefault.jpg'"
              class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
              <span class="text-white text-lg">▶</span>
            </div>
            <!-- Playing indicator -->
            <div v-if="musicStore.currentTrack?.youtubeId === extractId(track) && musicStore.isPlaying"
              class="absolute inset-0 bg-black/40 flex items-center justify-center">
              <span class="text-purple-400 text-sm animate-pulse">♫</span>
            </div>
          </div>
          <!-- Info -->
          <div class="flex-1 min-w-0">
            <p class="text-sm text-white font-medium truncate">{{ track.title }}</p>
            <p class="text-xs text-gray-400 truncate">{{ track.artist || track.channel || '' }}</p>
          </div>
          <!-- Number -->
          <span class="text-gray-600 text-xs flex-shrink-0">{{ idx + 1 }}</span>
        </div>
      </div>

      <!-- My Playlists section (shown when ⭐ clicked) -->
      <div v-if="showMyPlaylists && playlists.length" class="mt-6">
        <h3 class="text-white font-bold mb-3">⭐ 내 뮤직함</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div v-for="pl in playlists" :key="pl.id"
            @click="loadPlaylist(pl)"
            class="bg-gray-800 hover:bg-gray-750 rounded-xl p-4 cursor-pointer transition"
            :class="{ 'ring-2 ring-yellow-500': activePlaylist?.id === pl.id }">
            <p class="text-white font-semibold text-sm">{{ pl.name }}</p>
            <p class="text-gray-400 text-xs mt-1">{{ pl.tracks?.length || 0 }}곡</p>
          </div>
        </div>
      </div>

    </div>

    <!-- Add track to playlist modal -->
    <div v-if="showAddToPlaylist" class="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4" @click.self="showAddToPlaylist = false">
      <div class="bg-gray-800 rounded-2xl p-6 w-full max-w-md">
        <h3 class="text-lg font-bold text-white mb-4">곡 추가</h3>
        <input v-model="addTrackUrl" type="text" placeholder="YouTube URL" @keyup.enter="addTrackToPlaylist"
          class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-500 mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500">
        <div class="flex gap-2">
          <button @click="showAddToPlaylist = false" class="flex-1 py-3 bg-gray-700 text-gray-300 rounded-xl">취소</button>
          <button @click="addTrackToPlaylist" class="flex-1 py-3 bg-purple-600 text-white rounded-xl font-medium">추가</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useMusicStore } from '@/stores/music'

const authStore = useAuthStore()
const musicStore = useMusicStore()
const categories = ref([])
const selectedCat = ref(null)
const tracks = ref([])
const tracksLoading = ref(false)
const currentTrack = ref(null)
const currentIndex = ref(-1)
const isPlaying = ref(false)
const showMyPlaylists = ref(false)
const playlists = ref([])
const activePlaylist = ref(null)
const showAddToPlaylist = ref(false)
const addTrackUrl = ref('')
const addingTrack = ref(false)

const currentPlaylist = computed(() => {
  if (activePlaylist.value?.tracks) return activePlaylist.value.tracks
  return tracks.value
})

function extractId(track) {
  if (track.youtube_id) return track.youtube_id
  if (track.url) {
    const m = track.url.match(/(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/)
    return m ? m[1] : ''
  }
  return ''
}

function playTrack(track, index) {
  currentTrack.value = track
  currentIndex.value = index
  isPlaying.value = true

  const vid = extractId(track)
  if (!vid) return

  try { axios.post(`/api/music/tracks/${track.id}/play`) } catch (e) {}

  // Update global music store - this is the ONLY player now
  musicStore.play({
    id: track.id || vid,
    title: track.title,
    artist: track.artist || track.channel || '',
    thumbnail: 'https://img.youtube.com/vi/' + vid + '/mqdefault.jpg',
    youtubeId: vid
  }, currentPlaylist.value.map(t => ({
    id: t.id || extractId(t),
    title: t.title,
    artist: t.artist || t.channel || '',
    thumbnail: 'https://img.youtube.com/vi/' + extractId(t) + '/mqdefault.jpg',
    youtubeId: extractId(t)
  })))
}

function playAll() {
  if (!currentPlaylist.value.length) return
  playTrack(currentPlaylist.value[0], 0)
}

function playShuffleAll() {
  if (!currentPlaylist.value.length) return
  const idx = Math.floor(Math.random() * currentPlaylist.value.length)
  playTrack(currentPlaylist.value[idx], idx)
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/music/categories')
    categories.value = data
    if (data.length > 0) await selectCategory(data[0])
  } catch (e) {}
}

async function selectCategory(cat) {
  selectedCat.value = cat
  activePlaylist.value = null
  tracksLoading.value = true
  try {
    const { data } = await axios.get(`/api/music/categories/${cat.id}/tracks`)
    tracks.value = data.tracks
  } catch (e) { tracks.value = [] }
  tracksLoading.value = false
}

async function loadPlaylists() {
  if (!authStore.isLoggedIn) return
  try {
    const { data } = await axios.get('/api/music/playlists')
    playlists.value = data
  } catch (e) {}
}

async function loadPlaylist(pl) {
  try {
    const { data } = await axios.get(`/api/music/playlists/${pl.id}`)
    activePlaylist.value = data
    currentIndex.value = -1
  } catch (e) {}
}

async function addTrackToPlaylist() {
  if (!addTrackUrl.value.trim() || !activePlaylist.value) return
  addingTrack.value = true
  try {
    await axios.post(`/api/music/playlists/${activePlaylist.value.id}/tracks`, { youtube_url: addTrackUrl.value })
    addTrackUrl.value = ''
    showAddToPlaylist.value = false
    await loadPlaylist(activePlaylist.value)
    await loadPlaylists()
  } catch (e) { alert(e.response?.data?.message || '추가 실패') }
  addingTrack.value = false
}

watch(showMyPlaylists, (val) => { if (val) loadPlaylists() })
onMounted(() => { loadCategories(); if (authStore.isLoggedIn) loadPlaylists() })
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
</style>
