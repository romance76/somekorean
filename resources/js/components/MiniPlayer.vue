<template>
  <!-- Only show when there is a track AND not on /music page -->
  <div v-if="music.hasTrack && !isMusicPage" class="mini-player-wrap" @mouseenter="expanded = true" @mouseleave="expanded = false">
    
    <!-- Collapsed: thin bar -->
    <div v-if="!expanded" class="mini-bar">
      <div class="mini-progress" :style="{ width: music.progress + '%' }"></div>
      <div class="mini-bar-content">
        <span class="mini-icon">&#127925;</span>
        <span class="mini-title">{{ music.currentTrack?.title }}</span>
      </div>
    </div>

    <!-- Expanded: full mini player -->
    <div v-else class="mini-expanded">
      <div class="mini-progress-full" :style="{ width: music.progress + '%' }"></div>
      <div class="mini-content">
        <img v-if="music.currentTrack?.thumbnail" :src="music.currentTrack.thumbnail" class="mini-thumb" />
        <div v-else class="mini-thumb mini-thumb-empty">&#127925;</div>
        <div class="mini-info">
          <p class="mini-song">{{ music.currentTrack?.title }}</p>
          <p class="mini-artist">{{ music.currentTrack?.artist || '' }}</p>
        </div>
        <div class="mini-controls">
          <button @click="music.prev()" class="mini-btn">&#9198;</button>
          <button @click="music.toggle()" class="mini-btn mini-btn-play">{{ music.isPlaying ? '\u23F8' : '\u25B6' }}</button>
          <button @click="music.next()" class="mini-btn">&#9197;</button>
          <button @click="music.stop()" class="mini-btn mini-btn-close">&times;</button>
        </div>
      </div>
    </div>

    <!-- Hidden YouTube iframe for audio -->
    <iframe
      v-if="music.currentTrack?.youtubeId"
      :id="'mini-yt-' + music.currentTrack.youtubeId"
      :src="ytSrc"
      class="mini-iframe"
      allow="autoplay; encrypted-media"
    ></iframe>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { useRoute } from "vue-router"
import { useMusicStore } from "../stores/music"

const music = useMusicStore()
const route = useRoute()
const expanded = ref(false)

const isMusicPage = computed(() => route.path.startsWith("/music"))

const ytSrc = computed(() => {
  if (!music.currentTrack?.youtubeId) return ""
  const vid = music.currentTrack.youtubeId
  const autoplay = music.isPlaying ? 1 : 0
  return `https://www.youtube.com/embed/${vid}?autoplay=${autoplay}&loop=1&playlist=${vid}&enablejsapi=1`
})

// When play/pause toggles, communicate with iframe via postMessage
watch(() => music.isPlaying, (playing) => {
  const iframe = document.querySelector("[id^=mini-yt-]")
  if (iframe && iframe.contentWindow) {
    const cmd = playing ? "playVideo" : "pauseVideo"
    iframe.contentWindow.postMessage(JSON.stringify({ event: "command", func: cmd }), "*")
  }
})
</script>

<style scoped>
.mini-player-wrap {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  transition: all 0.3s ease;
}

.mini-bar {
  height: 28px;
  background: #1a1a2e;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
  cursor: pointer;
}
.mini-progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 2px;
  background: #6366f1;
  transition: width 0.3s;
}
.mini-bar-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  width: 100%;
}
.mini-icon { font-size: 12px; }
.mini-title {
  font-size: 11px;
  color: #ccc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-expanded {
  background: #1a1a2e;
  padding: 10px 16px;
  position: relative;
  overflow: hidden;
  border-top: 1px solid #2a2a4e;
}
.mini-progress-full {
  position: absolute;
  top: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  transition: width 0.3s;
}
.mini-content {
  display: flex;
  align-items: center;
  gap: 12px;
}
.mini-thumb {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}
.mini-thumb-empty {
  background: #2a2a4e;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.mini-info {
  flex: 1;
  min-width: 0;
}
.mini-song {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mini-artist {
  font-size: 11px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mini-controls {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}
.mini-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: #ccc;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.mini-btn:hover { background: #2a2a4e; color: #fff; }
.mini-btn-play {
  width: 42px;
  height: 42px;
  background: #6366f1;
  color: #fff;
  font-size: 18px;
}
.mini-btn-play:hover { background: #5558e6; }
.mini-btn-close {
  font-size: 14px;
  color: #666;
}
.mini-btn-close:hover { color: #f87171; background: #2a2a4e; }

.mini-iframe {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
</style>
