<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between"><h2 class="text-lg font-bold text-gray-800">게임 관리</h2></div>
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div v-for="stat in statsCards" :key="stat.label" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">{{ stat.label }}</div>
        <div class="text-2xl font-black text-gray-800">{{ (stat.value || 0).toLocaleString() }}</div>
      </div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100"><h3 class="font-bold text-gray-800 text-sm">게임 목록</h3></div>
      <div class="overflow-x-auto"><table class="w-full text-sm"><thead class="bg-gray-50 border-b border-gray-200"><tr>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">게임명</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">카테고리</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">플레이수</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">상태</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">관리</th>
      </tr></thead><tbody class="divide-y divide-gray-50">
        <tr v-for="game in games" :key="game.id" class="hover:bg-gray-50">
          <td class="px-4 py-3 font-medium text-gray-800">{{ game.name || game.title }}</td>
          <td class="px-4 py-3 text-gray-600 text-xs">{{ game.category || '-' }}</td>
          <td class="px-4 py-3 text-right text-gray-700">{{ (game.play_count || 0).toLocaleString() }}</td>
          <td class="px-4 py-3"><span class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="game.is_active ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-500'">{{ game.is_active ? '활성' : '비활성' }}</span></td>
          <td class="px-4 py-3 text-right">
            <button @click="toggleGame(game)" class="text-xs px-2 py-1 rounded bg-yellow-50 text-yellow-600 hover:bg-yellow-100">{{ game.is_active ? '비활성' : '활성' }}</button>
          </td>
        </tr>
      </tbody></table></div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
const games = ref([]), stats = ref({})
const statsCards = computed(() => [
  { label: '전체 게임', value: stats.value.total_games },
  { label: '오늘 플레이', value: stats.value.plays_today },
  { label: '활성 유저', value: stats.value.active_players },
  { label: '총 포인트', value: stats.value.total_points },
])
async function loadGames() { try { const { data } = await axios.get('/api/admin/games'); games.value = data.games || data.data || []; stats.value = data.stats || {} } catch {} }
async function toggleGame(g) { try { await axios.post(`/api/admin/games/${g.id}/toggle`); g.is_active = !g.is_active } catch {} }
onMounted(loadGames)
</script>
