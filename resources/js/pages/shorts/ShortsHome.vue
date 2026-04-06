<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-black text-gray-800">📱 숏츠</h1>
      <RouterLink v-if="auth.isLoggedIn" to="/shorts/upload" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm hover:bg-amber-500">+ 업로드</RouterLink>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="!shorts.length" class="text-center py-12 text-gray-400">숏츠가 없습니다</div>
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      <div v-for="s in shorts" :key="s.id" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition cursor-pointer group" @click="playShort(s)">
        <div class="relative aspect-[9/16] bg-gray-900">
          <img :src="s.thumbnail_url" class="w-full h-full object-cover" @error="e => e.target.src=''" />
          <div class="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition flex items-center justify-center">
            <div class="w-12 h-12 bg-white/80 rounded-full flex items-center justify-center text-2xl">▶</div>
          </div>
          <div class="absolute bottom-2 left-2 right-2">
            <div class="text-white text-xs font-bold line-clamp-2 drop-shadow">{{ s.title }}</div>
          </div>
        </div>
        <div class="p-2">
          <div class="flex items-center justify-between text-[10px] text-gray-400">
            <span>{{ s.user?.name || '익명' }}</span>
            <span>❤️ {{ s.like_count }} · 👁 {{ s.view_count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 비디오 모달 -->
    <div v-if="activeShort" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center" @click.self="activeShort=null">
      <div class="bg-black rounded-2xl overflow-hidden max-w-md w-full max-h-[90vh] relative">
        <button @click="activeShort=null" class="absolute top-3 right-3 z-10 text-white text-2xl">✕</button>
        <div class="aspect-[9/16]">
          <iframe :src="`https://www.youtube.com/embed/${activeShort.youtube_id}?autoplay=1`"
            class="w-full h-full" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
        </div>
        <div class="p-4 text-white">
          <div class="text-sm font-bold">{{ activeShort.title }}</div>
          <div class="flex items-center gap-4 mt-2 text-xs text-gray-300">
            <button @click="toggleLike" :class="liked ? 'text-red-400' : ''">{{ liked ? '❤️' : '🤍' }} {{ activeShort.like_count }}</button>
            <span>👁 {{ activeShort.view_count }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'
const auth = useAuthStore()
const shorts = ref([])
const loading = ref(true)
const activeShort = ref(null)
const liked = ref(false)

function playShort(s) { activeShort.value = s; liked.value = false }

async function toggleLike() {
  if (!auth.isLoggedIn || !activeShort.value) return
  try {
    const { data } = await axios.post(`/api/shorts/${activeShort.value.id}/like`)
    liked.value = data.liked
    activeShort.value.like_count += data.liked ? 1 : -1
  } catch {}
}

onMounted(async () => {
  try { const { data } = await axios.get('/api/shorts'); shorts.value = data.data?.data || [] } catch {}
  loading.value = false
})
</script>
