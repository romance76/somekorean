<template>
<div v-if="music.hasTrack && !hideUI" ref="playerContainer"
  class="fixed z-[9998]"
  :style="{ right: posRight + 'px', top: posTop + 'px' }">

  <!-- ═══ 최소화 상태 ═══ -->
  <div v-if="state === 'mini'" @click="state = 'normal'"
    class="w-14 h-14 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 shadow-xl flex items-center justify-center cursor-pointer hover:scale-110 transition-all animate-pulse-slow relative">
    <span class="text-white text-xl">{{ music.isPlaying ? '🎵' : '⏸' }}</span>
    <svg class="absolute inset-0 w-14 h-14 -rotate-90 pointer-events-none" viewBox="0 0 56 56">
      <circle cx="28" cy="28" r="26" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2" />
      <circle cx="28" cy="28" r="26" fill="none" stroke="#a78bfa" stroke-width="2.5"
        :stroke-dasharray="163" :stroke-dashoffset="163 - (163 * music.progress / 100)" stroke-linecap="round" />
    </svg>
  </div>

  <!-- ═══ 일반 상태 ═══ -->
  <div v-else class="w-[320px] bg-[#1a1a2e] rounded-2xl shadow-2xl overflow-hidden border border-white/10 flex flex-col" style="max-height:75vh;">

    <!-- 드래그 헤더 -->
    <div @mousedown="startDrag" @touchstart.passive="startDrag"
      class="px-3 py-2 flex items-center justify-between cursor-move bg-gradient-to-r from-indigo-700 to-purple-700 select-none flex-shrink-0">
      <div class="flex items-center gap-2 flex-1 min-w-0">
        <span class="text-sm">🎵</span>
        <p class="text-white text-xs font-bold truncate">{{ music.currentTrack?.title }}</p>
      </div>
      <div class="flex items-center gap-0.5 flex-shrink-0">
        <button @click.stop="state = 'mini'" class="w-6 h-6 rounded hover:bg-white/20 text-white/70 hover:text-white flex items-center justify-center text-sm" title="최소화">−</button>
        <button @click.stop="closePlayer" class="w-6 h-6 rounded hover:bg-white/20 text-white/70 hover:text-white flex items-center justify-center text-xs" title="닫기">✕</button>
      </div>
    </div>

    <!-- YouTube 영상 -->
    <div class="aspect-video bg-black flex-shrink-0 relative">
      <div id="yt-mini-player" class="w-full h-full"></div>
    </div>

    <!-- 컨트롤 -->
    <div class="px-3 py-2 flex items-center gap-2 flex-shrink-0">
      <button @click="music.prev(); playPrev()" class="w-7 h-7 rounded-full text-gray-400 hover:text-white flex items-center justify-center text-xs">⏮</button>
      <button @click="togglePlay" class="w-9 h-9 rounded-full bg-indigo-600 text-white flex items-center justify-center hover:bg-indigo-500 text-sm">{{ music.isPlaying ? '⏸' : '▶' }}</button>
      <button @click="music.next(); playNext()" class="w-7 h-7 rounded-full text-gray-400 hover:text-white flex items-center justify-center text-xs">⏭</button>
      <div class="flex-1"></div>
      <span class="text-gray-500 text-[10px]">🔊</span>
      <input type="range" min="0" max="100" v-model="volume" @input="setVolume" @click.stop
        class="w-16 h-1 accent-indigo-500" style="appearance:auto;" />
    </div>

    <!-- 프로그레스 -->
    <div class="h-0.5 bg-gray-800 flex-shrink-0">
      <div class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all" :style="{ width: music.progress + '%' }"></div>
    </div>

    <!-- 플레이리스트 -->
    <div v-if="music.playlist.length" class="flex-shrink-0 border-t border-white/10">
      <button @click="showPL = !showPL" class="w-full px-3 py-1.5 text-[10px] text-gray-400 hover:text-gray-200 flex items-center justify-between">
        <span>다음 곡 ({{ music.playlist.length }}곡)</span>
        <span>{{ showPL ? '▲' : '▼' }}</span>
      </button>
    </div>
    <div v-if="showPL && music.playlist.length" class="overflow-y-auto max-h-[180px] px-1 pb-1 music-scroll">
      <div v-for="(track, idx) in music.playlist" :key="track.id || idx"
        @click="playFromList(track)"
        class="flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer transition"
        :class="music.currentIndex === idx ? 'bg-indigo-900/50' : 'hover:bg-white/5'">
        <span class="text-gray-500 text-[10px] w-4 text-right">{{ idx + 1 }}</span>
        <div class="flex-1 min-w-0">
          <p class="text-[11px] truncate" :class="music.currentIndex === idx ? 'text-indigo-400 font-semibold' : 'text-gray-300'">{{ track.title }}</p>
        </div>
        <span v-if="music.currentIndex === idx && music.isPlaying" class="text-indigo-400 text-xs">♪</span>
      </div>
    </div>
  </div>
</div>

<!-- YouTube API용 숨겨진 플레이어 (hideUI 상태에서도 오디오 유지) -->
<div v-if="music.hasTrack && hideUI && music.currentTrack?.youtubeId" class="fixed -top-[9999px] -left-[9999px] w-1 h-1">
  <div id="yt-mini-player"></div>
</div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useMusicStore } from '../stores/music'

const music = useMusicStore()
const route = useRoute()
const state = ref('mini')
const volume = ref(80)
const showPL = ref(true)
let ytPlayer = null
let progressTimer = null
let currentVideoId = null
let ignoreStateChange = false

const isShortsPage = computed(() => route.path.startsWith('/shorts'))
const hideUI = computed(() => isShortsPage.value)

// 위치 — 우측 상단에서 시작 (right/top 기준)
const posRight = ref(16)
const posTop = ref(80)
let dragging = false
let dragStart = { x: 0, y: 0 }
let posStart = { right: 0, top: 0 }

function startDrag(e) {
  dragging = true
  const ev = e.touches ? e.touches[0] : e
  dragStart = { x: ev.clientX, y: ev.clientY }
  posStart = { right: posRight.value, top: posTop.value }
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag, { passive: false })
  document.addEventListener('touchend', stopDrag)
}

function onDrag(e) {
  if (!dragging) return
  const ev = e.touches ? e.touches[0] : e
  const dx = ev.clientX - dragStart.x
  const dy = ev.clientY - dragStart.y
  posRight.value = Math.max(0, Math.min(window.innerWidth - 340, posStart.right - dx))
  posTop.value = Math.max(0, Math.min(window.innerHeight - 100, posStart.top + dy))
}

function stopDrag() {
  dragging = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
}

// YouTube IFrame API
function loadYTApi() {
  if (window.YT?.Player) return Promise.resolve()
  return new Promise(resolve => {
    if (document.getElementById('yt-api-script')) { window.onYouTubeIframeAPIReady = resolve; return }
    const tag = document.createElement('script')
    tag.id = 'yt-api-script'
    tag.src = 'https://www.youtube.com/iframe_api'
    document.head.appendChild(tag)
    window.onYouTubeIframeAPIReady = resolve
  })
}

async function createPlayer(videoId, startAt = 0) {
  await loadYTApi()
  const el = document.getElementById('yt-mini-player')
  if (!el) { setTimeout(() => createPlayer(videoId, startAt), 500); return }

  if (ytPlayer && ytPlayer.destroy) {
    try { ytPlayer.destroy() } catch {}
    ytPlayer = null
  }

  ytPlayer = new window.YT.Player('yt-mini-player', {
    width: '100%', height: '100%',
    videoId,
    playerVars: { autoplay: 1, controls: 1, modestbranding: 1, rel: 0, playsinline: 1 },
    events: {
      onReady: (e) => {
        e.target.setVolume(volume.value)
        if (startAt > 0) e.target.seekTo(startAt, true)
        currentVideoId = videoId
        startProgressTimer()
      },
      onStateChange: (e) => {
        if (ignoreStateChange) return
        if (e.data === window.YT.PlayerState.ENDED) {
          music.next()
          nextTick(() => { if (music.currentTrack?.youtubeId) loadVideo(music.currentTrack.youtubeId) })
        }
      }
    }
  })
}

function loadVideo(videoId, startAt = 0) {
  if (!ytPlayer?.loadVideoById) { createPlayer(videoId, startAt); return }
  if (currentVideoId === videoId && startAt === 0) return
  ytPlayer.loadVideoById({ videoId, startSeconds: startAt })
  currentVideoId = videoId
}

function togglePlay() {
  if (!ytPlayer?.getPlayerState) return
  const st = ytPlayer.getPlayerState()
  if (st === 1) { ytPlayer.pauseVideo(); music.isPlaying = false }
  else { ytPlayer.playVideo(); music.isPlaying = true }
}

function playFromList(track) {
  music.play(track)
  loadVideo(track.youtubeId, 0)
}

function playPrev() {
  nextTick(() => { if (music.currentTrack?.youtubeId) loadVideo(music.currentTrack.youtubeId) })
}

function playNext() {
  nextTick(() => { if (music.currentTrack?.youtubeId) loadVideo(music.currentTrack.youtubeId) })
}

function closePlayer() {
  if (ytPlayer?.stopVideo) ytPlayer.stopVideo()
  music.stop()
  state.value = 'mini'
}

function setVolume() {
  if (ytPlayer?.setVolume) ytPlayer.setVolume(volume.value)
}

function startProgressTimer() {
  if (progressTimer) clearInterval(progressTimer)
  progressTimer = setInterval(() => {
    if (!ytPlayer?.getCurrentTime || !ytPlayer?.getDuration) return
    try {
      const cur = ytPlayer.getCurrentTime()
      const dur = ytPlayer.getDuration()
      if (dur > 0) music.setProgress((cur / dur) * 100, cur, dur)
    } catch {}
  }, 1000)
}

// 트랙 변경 시
watch(() => music.currentTrack?.youtubeId, (vid) => {
  if (!vid) return
  if (state.value === 'mini') state.value = 'normal'
  nextTick(() => {
    if (ytPlayer?.loadVideoById) loadVideo(vid, 0)
    else createPlayer(vid, 0)
  })
})

watch(isShortsPage, (isShorts) => {
  if (isShorts && music.isPlaying) {
    if (ytPlayer?.pauseVideo) ytPlayer.pauseVideo()
    music.isPlaying = false
  }
})

onMounted(() => {
  if (music.currentTrack?.youtubeId) {
    state.value = 'normal'
    nextTick(() => createPlayer(music.currentTrack.youtubeId, music.currentTime || 0))
  }
})

onUnmounted(() => {
  if (progressTimer) clearInterval(progressTimer)
})
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0.4); }
  50% { box-shadow: 0 0 0 8px rgba(99,102,241,0); }
}
.animate-pulse-slow { animation: pulse-slow 2s infinite; }
input[type="range"] { height: 4px; }
.music-scroll::-webkit-scrollbar { width: 4px; }
.music-scroll::-webkit-scrollbar-thumb { background: #4338ca; border-radius: 2px; }
</style>
