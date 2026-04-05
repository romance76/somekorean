import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useMusicStore = defineStore('music', () => {
  // ── State ──
  const currentTrack = ref(null) // { id, title, artist, thumbnail, youtubeId }
  const playlist = ref([])
  const isPlaying = ref(false)
  const volume = ref(parseInt(localStorage.getItem('sk_volume') || '80', 10))
  const currentTime = ref(0)
  const duration = ref(0)
  const currentIndex = ref(-1)

  // ── Computed ──
  const hasTrack = computed(() => !!currentTrack.value)
  const progress = computed(() => duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0)

  // ── Actions ──
  function play(track, list = null) {
    if (list) playlist.value = list
    currentTrack.value = track
    const idx = playlist.value.findIndex(t => t.id === track.id)
    if (idx >= 0) currentIndex.value = idx
    isPlaying.value = true
  }

  function pause() {
    isPlaying.value = false
  }

  function resume() {
    isPlaying.value = true
  }

  function toggle() {
    isPlaying.value = !isPlaying.value
  }

  function next() {
    if (playlist.value.length === 0) return
    currentIndex.value = (currentIndex.value + 1) % playlist.value.length
    currentTrack.value = playlist.value[currentIndex.value]
    isPlaying.value = true
  }

  function prev() {
    if (playlist.value.length === 0) return
    currentIndex.value = (currentIndex.value - 1 + playlist.value.length) % playlist.value.length
    currentTrack.value = playlist.value[currentIndex.value]
    isPlaying.value = true
  }

  function stop() {
    isPlaying.value = false
    currentTrack.value = null
    currentIndex.value = -1
    currentTime.value = 0
    duration.value = 0
  }

  function setVolume(v) {
    volume.value = Math.max(0, Math.min(100, v))
    localStorage.setItem('sk_volume', String(volume.value))
  }

  function addToPlaylist(track) {
    if (!playlist.value.find(t => t.id === track.id)) {
      playlist.value.push(track)
    }
  }

  function removeFromPlaylist(trackId) {
    playlist.value = playlist.value.filter(t => t.id !== trackId)
  }

  return {
    currentTrack, playlist, isPlaying, volume,
    currentTime, duration, currentIndex,
    hasTrack, progress,
    play, pause, resume, toggle, next, prev, stop,
    setVolume, addToPlaylist, removeFromPlaylist,
  }
})
