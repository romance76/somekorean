<template>
<!-- 음악 페이지: 오른쪽 사이드바 영역에 인라인 표시 -->
<!-- 다른 페이지: fixed 플로팅 -->
<Teleport to="body">
  <div v-if="music.hasTrack && !hideUI">

    <!-- ═══ 최소화 (다른 페이지에서) ═══ -->
    <div v-if="viewState === 'mini'"
      class="fixed bottom-20 right-4 z-[9998] w-14 h-14 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 shadow-xl flex items-center justify-center cursor-pointer hover:scale-110 transition-all animate-pulse-slow"
      @click="viewState = 'float'">
      <span class="text-white text-xl">{{ music.isPlaying ? '🎵' : '⏸' }}</span>
      <svg class="absolute inset-0 w-14 h-14 -rotate-90 pointer-events-none" viewBox="0 0 56 56">
        <circle cx="28" cy="28" r="26" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="2" />
        <circle cx="28" cy="28" r="26" fill="none" stroke="#a78bfa" stroke-width="2.5"
          :stroke-dasharray="163" :stroke-dashoffset="163 - (163 * music.progress / 100)" stroke-linecap="round" />
      </svg>
    </div>

    <!-- ═══ 플로팅 플레이어 (다른 페이지에서 펼침) ═══ -->
    <div v-if="viewState === 'float'"
      class="fixed bottom-20 right-4 z-[9998] w-[320px] bg-[#1a1a2e] rounded-2xl shadow-2xl border border-white/10 flex flex-col overflow-hidden"
      style="max-height:70vh;">
      <div class="px-3 py-2 flex items-center justify-between bg-gradient-to-r from-indigo-700 to-purple-700 flex-shrink-0">
        <p class="text-white text-xs font-bold truncate flex-1 mr-2">🎵 {{ music.currentTrack?.title }}</p>
        <button @click="viewState = 'mini'" class="w-6 h-6 rounded hover:bg-white/20 text-white/70 hover:text-white flex items-center justify-center text-sm">−</button>
        <button @click="closePlayer" class="w-6 h-6 rounded hover:bg-white/20 text-white/70 hover:text-white flex items-center justify-center text-xs ml-0.5">✕</button>
      </div>
      <!-- 컨트롤 -->
      <div class="px-3 py-2 flex items-center gap-2 flex-shrink-0">
        <button @click="doPrev" class="w-7 h-7 rounded-full text-gray-400 hover:text-white flex items-center justify-center text-xs">⏮</button>
        <button @click="togglePlay" class="w-9 h-9 rounded-full bg-indigo-600 text-white flex items-center justify-center hover:bg-indigo-500 text-sm">{{ music.isPlaying ? '⏸' : '▶' }}</button>
        <button @click="doNext" class="w-7 h-7 rounded-full text-gray-400 hover:text-white flex items-center justify-center text-xs">⏭</button>
        <div class="flex-1 h-1 bg-gray-700 rounded-full mx-1">
          <div class="h-full bg-indigo-500 rounded-full transition-all" :style="{ width: music.progress + '%' }"></div>
        </div>
        <span class="text-gray-500 text-[10px]">🔊</span>
        <input type="range" min="0" max="100" v-model="volume" @input="setVolume"
          class="w-12 h-1 accent-indigo-500" style="appearance:auto;" />
      </div>
      <!-- 미니 플레이리스트 -->
      <div v-if="music.playlist.length" class="overflow-y-auto max-h-[200px] px-1 pb-1 border-t border-white/10">
        <div v-for="(track, idx) in music.playlist" :key="track.id || idx" @click="playFromList(track)"
          class="flex items-center gap-2 px-2 py-1 rounded cursor-pointer transition text-[11px]"
          :class="music.currentIndex === idx ? 'bg-indigo-900/50 text-indigo-300' : 'text-gray-400 hover:bg-white/5'">
          <span class="w-4 text-right text-gray-600">{{ idx + 1 }}</span>
          <span class="truncate flex-1">{{ track.title }}</span>
          <span v-if="music.currentIndex === idx && music.isPlaying" class="text-indigo-400">♪</span>
        </div>
      </div>
    </div>
  </div>

  <!-- 숨겨진 YouTube Player (항상 존재) -->
  <div v-if="music.hasTrack && music.currentTrack?.youtubeId"
    class="fixed w-1 h-1 overflow-hidden" style="top:-9999px;left:-9999px;">
    <div id="yt-mini-player"></div>
  </div>
</Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useMusicStore } from '../stores/music'

const music = useMusicStore()
const route = useRoute()
const volume = ref(80)
let ytPlayer = null
let progressTimer = null
let currentVideoId = null

const isShortsPage = computed(() => route.path.startsWith('/shorts'))
const isMusicPage = computed(() => route.path.startsWith('/music'))
const hideUI = computed(() => isShortsPage.value)

// 음악 페이지 = 숨김 (MusicHome에서 인라인 표시), 다른 페이지 = mini/float
const viewState = ref('mini')

// 음악 페이지 나가면 mini, 음악 페이지 들어오면 숨김 처리는 hideUI가 아닌 isMusicPage
watch(isMusicPage, (isMp) => {
  if (!isMp && music.hasTrack) viewState.value = 'mini'
})

// YouTube IFrame API
function loadYTApi() {
  if (window.YT?.Player) return Promise.resolve()
  return new Promise(resolve => {
    if (document.getElementById('yt-api-script')) {
      const check = setInterval(() => { if (window.YT?.Player) { clearInterval(check); resolve() } }, 100)
      return
    }
    const tag = document.createElement('script')
    tag.id = 'yt-api-script'
    tag.src = 'https://www.youtube.com/iframe_api'
    document.head.appendChild(tag)
    window.onYouTubeIframeAPIReady = resolve
  })
}

async function createPlayer(videoId, startAt = 0) {
  await loadYTApi()
  await nextTick()

  const el = document.getElementById('yt-mini-player')
  if (!el) { setTimeout(() => createPlayer(videoId, startAt), 500); return }

  // 기존 플레이어 파괴
  if (ytPlayer) { try { ytPlayer.destroy() } catch {}; ytPlayer = null }

  ytPlayer = new window.YT.Player('yt-mini-player', {
    width: '1', height: '1',
    videoId,
    playerVars: { autoplay: 1, controls: 0, playsinline: 1, origin: window.location.origin },
    events: {
      onReady: (e) => {
        e.target.setVolume(volume.value)
        if (startAt > 0) e.target.seekTo(startAt, true)
        e.target.playVideo()
        currentVideoId = videoId
        music.isPlaying = true
        startProgressTimer()
      },
      onStateChange: (e) => {
        if (e.data === window.YT.PlayerState.ENDED) {
          music.next()
          nextTick(() => { if (music.currentTrack?.youtubeId) loadNewVideo(music.currentTrack.youtubeId) })
        }
        if (e.data === window.YT.PlayerState.PLAYING) music.isPlaying = true
        if (e.data === window.YT.PlayerState.PAUSED) music.isPlaying = false
      },
      onError: () => {
        // 에러 시 다음 곡
        setTimeout(() => { music.next(); nextTick(() => { if (music.currentTrack?.youtubeId) loadNewVideo(music.currentTrack.youtubeId) }) }, 1000)
      }
    }
  })
}

function loadNewVideo(videoId, startAt = 0) {
  if (!ytPlayer?.loadVideoById) { createPlayer(videoId, startAt); return }
  ytPlayer.loadVideoById({ videoId, startSeconds: startAt })
  currentVideoId = videoId
}

function togglePlay() {
  if (!ytPlayer) return
  try {
    const st = ytPlayer.getPlayerState()
    if (st === 1) ytPlayer.pauseVideo()
    else ytPlayer.playVideo()
  } catch {}
}

function doPrev() {
  music.prev()
  nextTick(() => { if (music.currentTrack?.youtubeId) loadNewVideo(music.currentTrack.youtubeId) })
}

function doNext() {
  music.next()
  nextTick(() => { if (music.currentTrack?.youtubeId) loadNewVideo(music.currentTrack.youtubeId) })
}

function playFromList(track) {
  music.play(track)
  loadNewVideo(track.youtubeId, 0)
}

function closePlayer() {
  if (ytPlayer?.stopVideo) try { ytPlayer.stopVideo() } catch {}
  music.stop()
  viewState.value = 'mini'
}

function setVolume() {
  if (ytPlayer?.setVolume) ytPlayer.setVolume(volume.value)
}

function startProgressTimer() {
  if (progressTimer) clearInterval(progressTimer)
  progressTimer = setInterval(() => {
    try {
      if (!ytPlayer?.getCurrentTime || !ytPlayer?.getDuration) return
      const cur = ytPlayer.getCurrentTime()
      const dur = ytPlayer.getDuration()
      if (dur > 0) music.setProgress((cur / dur) * 100, cur, dur)
    } catch {}
  }, 1000)
}

// 트랙 변경
watch(() => music.currentTrack?.youtubeId, (vid) => {
  if (!vid) return
  if (viewState.value === 'mini' && !isMusicPage.value) viewState.value = 'float'
  nextTick(() => {
    if (currentVideoId === vid && ytPlayer?.playVideo) { ytPlayer.playVideo(); return }
    if (ytPlayer?.loadVideoById) loadNewVideo(vid, 0)
    else createPlayer(vid, 0)
  })
})

watch(isShortsPage, (isShorts) => {
  if (isShorts && ytPlayer?.pauseVideo) { ytPlayer.pauseVideo(); music.isPlaying = false }
})

onMounted(() => {
  if (music.currentTrack?.youtubeId) {
    nextTick(() => createPlayer(music.currentTrack.youtubeId, music.currentTime || 0))
  }
})

onUnmounted(() => { if (progressTimer) clearInterval(progressTimer) })
</script>

<style scoped>
@keyframes pulse-slow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0.4); }
  50% { box-shadow: 0 0 0 8px rgba(99,102,241,0); }
}
.animate-pulse-slow { animation: pulse-slow 2s infinite; }
input[type="range"] { height: 4px; }
</style>
