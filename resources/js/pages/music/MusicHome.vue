<template>
  <div class="min-h-screen bg-gray-900 pb-24">
    <div class="max-w-5xl mx-auto px-4 pt-4">
      <!-- Banner -->
      <div class="bg-gradient-to-r from-purple-700 to-indigo-600 text-white px-6 py-5 rounded-2xl mb-4">
        <h1 class="text-xl font-black">{{ $t('music.title') }}</h1>
        <p class="text-sm opacity-80 mt-0.5">{{ $t('music.subtitle') }}</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <!-- Left: Categories -->
        <div class="lg:col-span-3">
          <div class="bg-gray-800 rounded-2xl p-3 sticky top-20">
            <h3 class="text-xs font-bold text-gray-500 uppercase px-2 mb-2">{{ $t('music.categories') }}</h3>
            <div class="space-y-1">
              <button v-for="cat in categories" :key="cat.id" @click="selectCategory(cat)"
                class="w-full text-left px-3 py-2.5 rounded-xl text-sm font-medium transition flex items-center gap-2"
                :class="selectedCat?.id === cat.id ? 'bg-purple-600 text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-white'">
                <span>{{ cat.emoji || '🎵' }}</span>
                <span class="truncate">{{ cat.name }}</span>
              </button>
            </div>

            <!-- My Playlists -->
            <div class="border-t border-gray-700 my-3 pt-3">
              <h3 class="text-xs font-bold text-gray-500 uppercase px-2 mb-2">{{ $t('music.my_playlists') }}</h3>
              <div v-for="pl in playlists" :key="pl.id" @click="loadPlaylist(pl)"
                class="w-full text-left px-3 py-2 rounded-xl text-sm font-medium transition flex items-center justify-between cursor-pointer"
                :class="activePlaylist?.id === pl.id ? 'bg-yellow-600 text-white' : 'text-gray-400 hover:bg-gray-700 hover:text-white'">
                <span class="flex items-center gap-2 truncate">
                  <span>⭐</span>
                  <span class="truncate">{{ pl.name }}</span>
                </span>
                <span class="text-xs opacity-60">{{ pl.tracks_count || 0 }}</span>
              </div>
              <button v-if="authStore.isLoggedIn" @click="showCreatePlaylist = true"
                class="w-full text-left px-3 py-2 rounded-xl text-xs text-gray-500 hover:text-purple-400 transition mt-1">
                + {{ $t('music.new_playlist') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Center: Tracks -->
        <div class="lg:col-span-6">
          <div class="bg-gray-800 rounded-2xl p-4">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-white font-bold text-sm">{{ selectedCat?.name || activePlaylist?.name || $t('music.all_tracks') }}</h2>
              <span class="text-xs text-gray-500">{{ tracks.length }}{{ $t('music.track_count') }}</span>
            </div>

            <div v-if="loadingTracks" class="text-center py-12 text-gray-500">
              <svg class="w-8 h-8 animate-spin mx-auto mb-3 text-gray-600" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
            </div>

            <div v-else-if="!tracks.length" class="text-center py-12 text-gray-500">
              <p>{{ $t('music.no_tracks') }}</p>
            </div>

            <div v-else class="space-y-1">
              <div v-for="(track, idx) in tracks" :key="track.id"
                @click="playTrack(track)"
                class="flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition"
                :class="currentTrack?.id === track.id ? 'bg-purple-600/30' : 'hover:bg-gray-700/50'">
                <span class="text-xs text-gray-500 w-6 text-right flex-shrink-0">{{ idx + 1 }}</span>
                <div class="w-10 h-10 rounded-lg bg-gray-700 flex items-center justify-center flex-shrink-0 overflow-hidden">
                  <img v-if="track.thumbnail" :src="track.thumbnail" class="w-full h-full object-cover"
                    @error="e => e.target.style.display='none'" />
                  <span v-else class="text-gray-500 text-lg">🎵</span>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium truncate" :class="currentTrack?.id === track.id ? 'text-purple-300' : 'text-white'">
                    {{ track.title }}
                  </p>
                  <p class="text-xs text-gray-500 truncate">{{ track.artist }}</p>
                </div>
                <!-- Playing indicator -->
                <div v-if="currentTrack?.id === track.id && isPlaying" class="flex gap-0.5 flex-shrink-0">
                  <span class="w-0.5 h-3 bg-purple-400 rounded-full animate-pulse"></span>
                  <span class="w-0.5 h-4 bg-purple-400 rounded-full animate-pulse" style="animation-delay: 0.2s"></span>
                  <span class="w-0.5 h-2 bg-purple-400 rounded-full animate-pulse" style="animation-delay: 0.4s"></span>
                </div>
                <!-- Add to playlist -->
                <button v-if="authStore.isLoggedIn" @click.stop="addToPlaylist(track)"
                  class="text-gray-600 hover:text-purple-400 transition flex-shrink-0">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: Now Playing -->
        <div class="lg:col-span-3">
          <div class="bg-gray-800 rounded-2xl p-4 sticky top-20">
            <h3 class="text-xs font-bold text-gray-500 uppercase mb-3">{{ $t('music.now_playing') }}</h3>
            <div v-if="currentTrack" class="text-center">
              <div class="w-full aspect-square rounded-xl bg-gray-700 mb-3 overflow-hidden">
                <img v-if="currentTrack.thumbnail" :src="currentTrack.thumbnail" class="w-full h-full object-cover"
                  @error="e => e.target.style.display='none'" />
                <div v-else class="w-full h-full flex items-center justify-center text-4xl text-gray-600">🎵</div>
              </div>
              <p class="text-white font-bold text-sm truncate">{{ currentTrack.title }}</p>
              <p class="text-gray-400 text-xs truncate mb-3">{{ currentTrack.artist }}</p>
              <div class="flex justify-center gap-4">
                <button @click="prevTrack" class="text-gray-400 hover:text-white transition">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
                </button>
                <button @click="togglePlay" class="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center text-white hover:bg-purple-700 transition">
                  <svg v-if="isPlaying" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M6 4h4v16H6zm8 0h4v16h-4z"/></svg>
                  <svg v-else class="w-5 h-5 ml-0.5" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                </button>
                <button @click="nextTrack" class="text-gray-400 hover:text-white transition">
                  <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
                </button>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-600 text-sm">
              {{ $t('music.select_track') }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Playlist Modal -->
    <div v-if="showCreatePlaylist" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4" @click.self="showCreatePlaylist = false">
      <div class="bg-gray-800 rounded-2xl p-6 w-full max-w-md">
        <h3 class="text-white font-bold mb-4">{{ $t('music.new_playlist') }}</h3>
        <input v-model="newPlaylistName" type="text" :placeholder="$t('music.playlist_name')"
          class="w-full bg-gray-700 border border-gray-600 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition" />
        <div class="flex justify-end gap-2 mt-4">
          <button @click="showCreatePlaylist = false" class="px-4 py-2 text-gray-400 hover:text-white transition">{{ $t('common.cancel') }}</button>
          <button @click="createPlaylist" :disabled="!newPlaylistName"
            class="px-4 py-2 bg-purple-600 text-white rounded-xl text-sm font-bold hover:bg-purple-700 disabled:opacity-50 transition">
            {{ $t('common.create') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const authStore = useAuthStore()
const { $t } = useLangStore()

const categories = ref([])
const tracks = ref([])
const playlists = ref([])
const selectedCat = ref(null)
const activePlaylist = ref(null)
const currentTrack = ref(null)
const isPlaying = ref(false)
const loadingTracks = ref(false)
const showCreatePlaylist = ref(false)
const newPlaylistName = ref('')

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/music/categories')
    categories.value = data.data || data || []
    if (categories.value.length) selectCategory(categories.value[0])
  } catch { /* ignore */ }
}

async function selectCategory(cat) {
  selectedCat.value = cat
  activePlaylist.value = null
  loadingTracks.value = true
  try {
    const { data } = await axios.get(`/api/music/categories/${cat.id}/tracks`)
    tracks.value = data.data || data || []
  } catch { tracks.value = [] }
  loadingTracks.value = false
}

async function loadPlaylist(pl) {
  activePlaylist.value = pl
  selectedCat.value = null
  loadingTracks.value = true
  try {
    const { data } = await axios.get(`/api/music/playlists/${pl.id}`)
    tracks.value = data.tracks || data.data || []
  } catch { tracks.value = [] }
  loadingTracks.value = false
}

async function loadPlaylists() {
  if (!authStore.isLoggedIn) return
  try {
    const { data } = await axios.get('/api/music/playlists')
    playlists.value = data.data || data || []
  } catch { /* ignore */ }
}

async function createPlaylist() {
  if (!newPlaylistName.value) return
  try {
    await axios.post('/api/music/playlists', { name: newPlaylistName.value })
    showCreatePlaylist.value = false
    newPlaylistName.value = ''
    await loadPlaylists()
  } catch (e) {
    alert(e.response?.data?.message || $t('music.create_failed'))
  }
}

async function addToPlaylist(track) {
  if (!playlists.value.length) {
    showCreatePlaylist.value = true
    return
  }
  const plId = playlists.value[0].id
  try {
    await axios.post(`/api/music/playlists/${plId}/tracks`, { track_id: track.id })
  } catch { /* ignore */ }
}

function playTrack(track) {
  currentTrack.value = track
  isPlaying.value = true
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
}

function nextTrack() {
  if (!currentTrack.value || !tracks.value.length) return
  const idx = tracks.value.findIndex(t => t.id === currentTrack.value.id)
  const next = tracks.value[(idx + 1) % tracks.value.length]
  playTrack(next)
}

function prevTrack() {
  if (!currentTrack.value || !tracks.value.length) return
  const idx = tracks.value.findIndex(t => t.id === currentTrack.value.id)
  const prev = tracks.value[(idx - 1 + tracks.value.length) % tracks.value.length]
  playTrack(prev)
}

onMounted(() => {
  loadCategories()
  loadPlaylists()
})
</script>
