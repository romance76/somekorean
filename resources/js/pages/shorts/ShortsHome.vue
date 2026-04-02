<template>
  <div class="min-h-screen bg-white">
    <div class="flex justify-center items-start pt-2">

      <!-- Main Shorts Container -->
      <div class="relative flex items-center gap-4" style="height: calc(100vh - 100px);">

        <!-- Video Area -->
        <div class="relative bg-black rounded-2xl overflow-hidden shadow-xl" style="width: 380px; height: 100%; max-height: 680px;">

          <div v-if="loading && shorts.length === 0" class="w-full h-full flex items-center justify-center text-gray-400">
            불러오는 중...
          </div>

          <template v-else-if="shorts.length > 0 && currentShort">
            <!-- YouTube Embed -->
            <iframe
              :key="currentShort.id"
              :src="getEmbedUrl(currentShort)"
              class="w-full h-full"
              frameborder="0"
              allow="autoplay; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>

            <!-- Bottom Info Overlay -->
            <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/70 to-transparent pointer-events-none">
              <p class="text-white text-sm font-semibold mb-1">{{ currentShort.description || '' }}</p>
              <p class="text-white text-xs opacity-90 line-clamp-2">{{ currentShort.title }}</p>
              <div class="flex items-center gap-2 mt-2">
                <span v-for="tag in parseTags(currentShort.tags)" :key="tag" class="text-[10px] bg-white/20 text-white px-2 py-0.5 rounded-full">
                  #{{ tag }}
                </span>
              </div>
            </div>
          </template>

          <div v-else class="w-full h-full flex items-center justify-center text-gray-400 text-sm">
            숏츠가 없습니다
          </div>
        </div>

        <!-- Right Action Buttons -->
        <div class="flex flex-col items-center gap-5" v-if="currentShort">
          <!-- Like -->
          <button @click="likeShort" class="flex flex-col items-center gap-1 group">
            <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center group-hover:bg-gray-200 transition"
              :class="{ 'bg-red-50': currentShort.is_liked }">
              <svg class="w-6 h-6" :class="currentShort.is_liked ? 'text-red-500' : 'text-gray-700'" fill="currentColor" viewBox="0 0 24 24">
                <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/>
              </svg>
            </div>
            <span class="text-xs text-gray-600 font-medium">{{ formatCount(currentShort.like_count || 0) }}</span>
          </button>

          <!-- Dislike -->
          <button class="flex flex-col items-center gap-1 group">
            <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center group-hover:bg-gray-200 transition">
              <svg class="w-6 h-6 text-gray-700 rotate-180" fill="currentColor" viewBox="0 0 24 24">
                <path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/>
              </svg>
            </div>
            <span class="text-xs text-gray-600 font-medium">싫어요</span>
          </button>

          <!-- Comment -->
          <button class="flex flex-col items-center gap-1 group">
            <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center group-hover:bg-gray-200 transition">
              <svg class="w-6 h-6 text-gray-700" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21.99 4c0-1.1-.89-2-1.99-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4-.01-18z"/>
              </svg>
            </div>
            <span class="text-xs text-gray-600 font-medium">{{ formatCount(currentShort.view_count || 0) }}</span>
          </button>

          <!-- Share -->
          <button @click="shareShort" class="flex flex-col items-center gap-1 group">
            <div class="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center group-hover:bg-gray-200 transition">
              <svg class="w-6 h-6 text-gray-700" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 11.5l-8.5-8.5v5c-7 1-10 6-11 11 2.5-3.5 6-5.1 11-5.1v5.1l8.5-7.5z"/>
              </svg>
            </div>
            <span class="text-xs text-gray-600 font-medium">공유</span>
          </button>
        </div>

        <!-- Navigation Arrows (far right) -->
        <div class="flex flex-col gap-3 ml-2">
          <button @click="prevShort" :disabled="currentIndex <= 0"
            class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition disabled:opacity-30">
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M5 15l7-7 7 7"/></svg>
          </button>
          <button @click="nextShort"
            class="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center hover:bg-gray-200 transition">
            <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7"/></svg>
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()
const shorts = ref([])
const currentIndex = ref(0)
const loading = ref(true)
const page = ref(1)
const hasMore = ref(true)

const currentShort = computed(() => shorts.value[currentIndex.value] || null)

function getAuthHeaders() {
  const token = localStorage.getItem('sk_token')
  return token ? { Authorization: 'Bearer ' + token } : {}
}

function getEmbedUrl(short) {
  if (short.embed_url) {
    const m = short.embed_url.match(/embed\/([^?&/]+)/)
    if (m) return `https://www.youtube.com/embed/${m[1]}?autoplay=1&mute=0&loop=1&playlist=${m[1]}&rel=0&controls=1&playsinline=1`
    return short.embed_url
  }
  const m = (short.url || '').match(/(?:shorts\/|watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/)
  if (m) return `https://www.youtube.com/embed/${m[1]}?autoplay=1&mute=0&loop=1&playlist=${m[1]}&rel=0&controls=1&playsinline=1`
  return ''
}

function parseTags(tags) {
  if (!tags) return []
  if (Array.isArray(tags)) return tags.slice(0, 3)
  try { return JSON.parse(tags).slice(0, 3) } catch { return [] }
}

function formatCount(n) {
  if (n >= 10000) return (n / 10000).toFixed(1) + '만'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n
}

async function loadShorts() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/shorts', {
      params: { page: page.value, per_page: 20, sort: 'random' },
      headers: getAuthHeaders()
    })
    const items = data.data || data || []
    if (items.length === 0) hasMore.value = false
    shorts.value.push(...items)
  } catch (e) {
    console.error('Failed to load shorts', e)
  } finally {
    loading.value = false
  }
}

function nextShort() {
  if (currentIndex.value < shorts.value.length - 1) {
    currentIndex.value++
    trackView()
    // Load more when near end
    if (currentIndex.value >= shorts.value.length - 3 && hasMore.value) {
      page.value++
      loadShorts()
    }
  }
}

function prevShort() {
  if (currentIndex.value > 0) currentIndex.value--
}

async function likeShort() {
  if (!currentShort.value) return
  try {
    const { data } = await axios.post(`/api/shorts/${currentShort.value.id}/like`, {}, { headers: getAuthHeaders() })
    currentShort.value.like_count = data.like_count ?? currentShort.value.like_count
    currentShort.value.is_liked = !currentShort.value.is_liked
  } catch {}
}

async function trackView() {
  if (!currentShort.value) return
  try {
    await axios.post(`/api/shorts/${currentShort.value.id}/view`, {}, { headers: getAuthHeaders() })
  } catch {}
}

function shareShort() {
  if (!currentShort.value) return
  const url = currentShort.value.url || window.location.href
  if (navigator.share) {
    navigator.share({ title: currentShort.value.title, url })
  } else {
    navigator.clipboard.writeText(url)
    alert('링크가 복사되었습니다!')
  }
}

// Keyboard navigation
function onKeyDown(e) {
  if (e.key === 'ArrowDown' || e.key === 'j') nextShort()
  if (e.key === 'ArrowUp' || e.key === 'k') prevShort()
}

// Mouse wheel navigation
function onWheel(e) {
  if (e.deltaY > 30) nextShort()
  else if (e.deltaY < -30) prevShort()
}

let wheelThrottle = false
function onWheelThrottled(e) {
  if (wheelThrottle) return
  wheelThrottle = true
  onWheel(e)
  setTimeout(() => { wheelThrottle = false }, 800)
}

onMounted(() => {
  loadShorts()
  window.addEventListener('keydown', onKeyDown)
  window.addEventListener('wheel', onWheelThrottled, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
  window.removeEventListener('wheel', onWheelThrottled)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
