<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-black text-gray-800">👥 동호회</h1>
      <RouterLink v-if="auth.isLoggedIn" to="/clubs" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm hover:bg-amber-500">+ 동호회 만들기</RouterLink>
    </div>

    <!-- 필터 -->
    <div class="flex gap-2 mb-4">
      <button v-for="t in types" :key="t.value" @click="type=t.value; loadClubs()"
        class="px-3 py-1.5 rounded-full text-xs font-bold transition"
        :class="type===t.value ? 'bg-amber-400 text-amber-900' : 'bg-white border text-gray-500 hover:bg-amber-50'">{{ t.label }}</button>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="!clubs.length" class="text-center py-12 text-gray-400">등록된 동호회가 없습니다</div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <RouterLink v-for="club in clubs" :key="club.id" :to="`/clubs/${club.id}`"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md hover:-translate-y-0.5 transition-all">
        <div class="flex items-center gap-3 mb-3">
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center text-2xl">👥</div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-bold text-gray-800 truncate">{{ club.name }}</div>
            <div class="text-[10px] text-gray-400">{{ club.category }} · {{ club.type === 'online' ? '온라인' : '지역' }}</div>
          </div>
        </div>
        <div class="text-xs text-gray-500 line-clamp-2 mb-2">{{ club.description }}</div>
        <div class="flex items-center justify-between text-[10px] text-gray-400">
          <span>👥 {{ club.member_count }}명</span>
          <span class="px-2 py-0.5 rounded-full" :class="club.type==='online' ? 'bg-blue-50 text-blue-600' : 'bg-green-50 text-green-600'">
            {{ club.type === 'online' ? '🌐 온라인' : '📍 지역' }}
          </span>
        </div>
      </RouterLink>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'
const auth = useAuthStore()
const clubs = ref([])
const loading = ref(true)
const type = ref('')
const types = [
  { value: '', label: '전체' },
  { value: 'online', label: '🌐 온라인' },
  { value: 'local', label: '📍 지역' },
]
async function loadClubs() {
  loading.value = true
  try {
    const params = {}
    if (type.value) params.type = type.value
    const { data } = await axios.get('/api/clubs', { params })
    clubs.value = data.data?.data || data.data || []
  } catch {}
  loading.value = false
}
onMounted(loadClubs)
</script>
