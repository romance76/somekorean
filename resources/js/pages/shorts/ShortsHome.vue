<template>
  <div class="shorts-page">
    <div ref="scrollContainer" class="shorts-scroll" @scroll="onScroll">
      <div v-for="(short, idx) in shorts" :key="short.id" class="shorts-slide">
        <div class="shorts-content">
          <!-- Video -->
          <div class="shorts-video">
            <iframe
              v-if="Math.abs(idx - currentIndex) <= 1"
              :src="idx === currentIndex ? getEmbedUrl(short) : ''"
              class="w-full h-full"
              frameborder="0"
              allow="autoplay; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
            <img v-else-if="short.thumbnail" :src="short.thumbnail" class="w-full h-full object-cover"
              @error="e => { e.target.style.display='none' }" />
            <div v-else class="w-full h-full flex items-center justify-center bg-black text-white">
              <svg class="w-16 h-16 opacity-30" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </div>

            <!-- Bottom overlay -->
            <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/70 to-transparent">
              <h3 class="text-white text-sm font-semibold line-clamp-2">{{ short.title }}</h3>
              <div v-if="short.tags?.length" class="flex flex-wrap gap-1 mt-1">
                <span v-for="tag in short.tags.slice(0, 3)" :key="tag"
                  class="text-xs bg-white/20 text-white px-2 py-0.5 rounded-full">#{{ tag }}</span>
              </div>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="shorts-actions">
            <button @click="toggleLike(short)" class="action-btn" :class="{ 'text-red-500': short.is_liked }">
              <svg class="w-7 h-7" :fill="short.is_liked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
              </svg>
              <span class="text-xs mt-1">{{ formatCount(short.likes_count || 0) }}</span>
            </button>

            <button @click="openComments(short)" class="action-btn">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
              </svg>
              <span class="text-xs mt-1">{{ formatCount(short.comments_count || 0) }}</span>
            </button>

            <button @click="shareShort(short)" class="action-btn">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
              </svg>
              <span class="text-xs mt-1">공유</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="shorts-slide flex items-center justify-center">
        <div class="animate-spin rounded-full h-10 w-10 border-2 border-gray-300 border-t-blue-500"></div>
      </div>

      <!-- Empty -->
      <div v-if="!loading && shorts.length === 0" class="shorts-slide flex items-center justify-center">
        <div class="text-center text-gray-400">
          <svg class="w-16 h-16 mx-auto mb-4 opacity-30" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          <p class="text-sm">숏츠가 없습니다</p>
        </div>
      </div>
    </div>

    <!-- Navigation arrows -->
    <div class="shorts-nav">
      <button @click="goPrev" :disabled="currentIndex === 0"
        class="nav-arrow" :class="{ 'opacity-30': currentIndex === 0 }">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 15l7-7 7 7"/>
        </svg>
      </button>
      <button @click="goNext" :disabled="currentIndex >= shorts.length - 1"
        class="nav-arrow" :class="{ 'opacity-30': currentIndex >= shorts.length - 1 }">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const shorts = ref([])
const currentIndex = ref(0)
const loading = ref(false)
const page = ref(1)
const hasMore = ref(true)
const scrollContainer = ref(null)

async function fetchShorts() {
  if (loading.value || !hasMore.value) return
  loading.value = true
  try {
    const { data } = await axios.get('/api/shorts', {
      params: { sort: 'random', page: page.value, per_page: 10 }
    })
    const raw = data.data || data
    const items = Array.isArray(raw) ? raw : (raw.data || [])
    if (items.length === 0) { hasMore.value = false }
    else { shorts.value.push(...items); page.value++ }
  } catch {}
  loading.value = false
}

function getEmbedUrl(short) {
  const url = short.embed_url || short.url || ''
  if (!url) return ''
  let videoId = ''
  if (url.includes('youtube.com/embed/')) videoId = url.split('embed/')[1]?.split(/[?&#]/)[0]
  else if (url.includes('youtube.com/shorts/')) videoId = url.split('shorts/')[1]?.split(/[?&#]/)[0]
  else if (url.includes('youtube.com/watch')) { try { videoId = new URL(url).searchParams.get('v') } catch {} }
  else if (url.includes('youtu.be/')) videoId = url.split('youtu.be/')[1]?.split(/[?&#]/)[0]
  if (videoId) return `https://www.youtube.com/embed/${videoId}?autoplay=1&loop=1&playlist=${videoId}&mute=0&controls=1&rel=0`
  return url
}

function onScroll() {
  const c = scrollContainer.value
  if (!c) return
  const newIndex = Math.round(c.scrollTop / c.clientHeight)
  if (newIndex !== currentIndex.value) {
    currentIndex.value = newIndex
    trackView(shorts.value[newIndex])
  }
  if (newIndex >= shorts.value.length - 3) fetchShorts()
}

function goNext() {
  if (currentIndex.value >= shorts.value.length - 1) return
  scrollContainer.value?.scrollTo({ top: (currentIndex.value + 1) * scrollContainer.value.clientHeight, behavior: 'smooth' })
}

function goPrev() {
  if (currentIndex.value <= 0) return
  scrollContainer.value?.scrollTo({ top: (currentIndex.value - 1) * scrollContainer.value.clientHeight, behavior: 'smooth' })
}

function onKeydown(e) {
  if (e.key === 'ArrowDown') { e.preventDefault(); goNext() }
  if (e.key === 'ArrowUp') { e.preventDefault(); goPrev() }
}

async function toggleLike(short) {
  try {
    const { data } = await axios.post(`/api/shorts/${short.id}/like`)
    short.is_liked = !short.is_liked
    short.likes_count = data.likes_count ?? (short.is_liked ? (short.likes_count || 0) + 1 : Math.max((short.likes_count || 1) - 1, 0))
  } catch {}
}

function openComments() { alert('댓글 기능은 준비 중입니다.') }

async function shareShort(short) {
  const url = `${window.location.origin}/shorts/${short.id}`
  if (navigator.share) {
    try { await navigator.share({ title: short.title, url }) } catch {}
  } else if (navigator.clipboard) {
    await navigator.clipboard.writeText(url)
    alert('링크가 복사되었습니다!')
  }
}

async function trackView(short) {
  if (!short) return
  try { await axios.post(`/api/shorts/${short.id}/view`) } catch {}
}

function formatCount(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}

onMounted(() => {
  fetchShorts()
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
.shorts-page { position: fixed; top: 48px; left: 0; right: 0; bottom: 0; background: #fff; z-index: 10; }
@media (min-width: 768px) { .shorts-page { top: 84px; } }
.shorts-scroll { height: 100%; overflow-y: scroll; scroll-snap-type: y mandatory; -ms-overflow-style: none; scrollbar-width: none; }
.shorts-scroll::-webkit-scrollbar { display: none; }
.shorts-slide { height: 100%; scroll-snap-align: start; display: flex; align-items: center; justify-content: center; }
.shorts-content { position: relative; display: flex; align-items: center; gap: 16px; height: 100%; padding: 16px 0; }
.shorts-video { position: relative; width: 405px; height: 100%; max-height: 720px; background: #000; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.12); }
.shorts-actions { display: flex; flex-direction: column; align-items: center; gap: 20px; padding: 8px 0; }
.action-btn { display: flex; flex-direction: column; align-items: center; justify-content: center; color: #333; cursor: pointer; transition: transform 0.15s; background: none; border: none; padding: 8px; }
.action-btn:hover { transform: scale(1.15); }
.shorts-nav { position: fixed; right: 24px; top: 50%; transform: translateY(-50%); display: flex; flex-direction: column; gap: 8px; z-index: 20; }
.nav-arrow { width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,0.9); border: 1px solid #e5e7eb; display: flex; align-items: center; justify-content: center; cursor: pointer; color: #333; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: background 0.15s; }
.nav-arrow:hover { background: #f3f4f6; }
@media (max-width: 640px) {
  .shorts-content { padding: 0; }
  .shorts-video { width: 100%; max-height: none; border-radius: 0; box-shadow: none; }
  .shorts-actions { position: absolute; right: 12px; bottom: 80px; z-index: 15; }
  .action-btn { color: #fff; filter: drop-shadow(0 1px 2px rgba(0,0,0,0.5)); }
  .shorts-nav { right: 12px; }
  .nav-arrow { width: 36px; height: 36px; background: rgba(255,255,255,0.7); }
}
</style>
