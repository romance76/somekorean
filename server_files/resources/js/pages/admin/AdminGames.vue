<template>
  <div class="space-y-5">
    <!-- 헤더 -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">게임 관리</h1>
      <p class="text-sm text-gray-500 mt-1">게임 활성화, 리더보드, 포인트 경제를 관리합니다</p>
    </div>

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">전체 플레이어</p>
        <p class="text-3xl font-bold text-gray-800 mt-1">{{ stats.totalPlayers.toLocaleString() }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">오늘 활성</p>
        <p class="text-3xl font-bold text-green-600 mt-1">{{ stats.todayActive.toLocaleString() }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">총 게임수</p>
        <p class="text-3xl font-bold text-blue-600 mt-1">{{ stats.totalGames }}</p>
      </div>
      <div class="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500">포인트 지급 총액</p>
        <p class="text-3xl font-bold text-yellow-600 mt-1">{{ stats.totalPoints.toLocaleString() }}</p>
      </div>
    </div>

    <!-- 게임 목록 / 토글 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-800">게임 ON/OFF 관리</h2>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-0 divide-y md:divide-y-0 md:divide-x divide-gray-100">
        <div v-for="game in games" :key="game.id" class="p-4 flex items-center justify-between hover:bg-gray-50 transition">
          <div class="flex items-center gap-3">
            <span class="text-2xl">{{ game.icon }}</span>
            <div>
              <p class="font-medium text-gray-900">{{ game.name }}</p>
              <p class="text-xs text-gray-400">일 {{ game.dailyPlays.toLocaleString() }}회 · 포인트 x{{ game.multiplier }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span :class="game.enabled ? 'text-green-600' : 'text-gray-400'" class="text-xs font-medium">
              {{ game.enabled ? 'ON' : 'OFF' }}
            </span>
            <button @click="toggleGame(game)" :class="game.enabled ? 'bg-green-500' : 'bg-gray-300'" class="relative inline-flex w-10 h-6 rounded-full transition-colors duration-200 focus:outline-none">
              <span :class="game.enabled ? 'translate-x-4' : 'translate-x-0'" class="inline-block w-5 h-5 mt-0.5 ml-0.5 bg-white rounded-full shadow transform transition-transform duration-200"></span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 포인트 배율 조정 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100 flex items-center justify-between">
        <h2 class="font-semibold text-gray-800">포인트 경제 관리</h2>
        <button @click="saveMultipliers" class="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition">저장</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-500 uppercase text-xs">
            <tr>
              <th class="px-4 py-3 text-left">게임</th>
              <th class="px-4 py-3 text-center">지급된 총 포인트</th>
              <th class="px-4 py-3 text-center">포인트 배율</th>
              <th class="px-4 py-3 text-center">일 플레이</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="game in games" :key="game.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <span>{{ game.icon }}</span>
                  <span class="font-medium text-gray-900">{{ game.name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-center font-medium text-yellow-700">{{ game.totalPoints.toLocaleString() }}</td>
              <td class="px-4 py-3 text-center">
                <input v-model.number="game.multiplier" type="number" min="0.1" max="10" step="0.1"
                  class="w-20 text-center border border-gray-200 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </td>
              <td class="px-4 py-3 text-center text-gray-600">{{ game.dailyPlays.toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 리더보드 관리 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100">
        <div class="flex items-center justify-between flex-wrap gap-3">
          <h2 class="font-semibold text-gray-800">리더보드 관리</h2>
          <select v-model="selectedGameId" class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option v-for="g in games" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
      </div>
      <div class="p-4">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="text-gray-500 text-xs uppercase">
              <tr>
                <th class="pb-2 text-left">순위</th>
                <th class="pb-2 text-left">닉네임</th>
                <th class="pb-2 text-center">점수</th>
                <th class="pb-2 text-center">플레이</th>
                <th class="pb-2 text-center">포인트</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="(entry, i) in currentLeaderboard" :key="i" class="hover:bg-gray-50">
                <td class="py-2 pr-4">
                  <span v-if="i === 0" class="text-yellow-500 font-bold text-base">🥇</span>
                  <span v-else-if="i === 1" class="text-gray-400 font-bold text-base">🥈</span>
                  <span v-else-if="i === 2" class="text-amber-600 font-bold text-base">🥉</span>
                  <span v-else class="text-gray-500 font-medium">{{ i + 1 }}</span>
                </td>
                <td class="py-2 font-medium text-gray-900">{{ entry.name }}</td>
                <td class="py-2 text-center font-bold text-blue-700">{{ entry.score.toLocaleString() }}</td>
                <td class="py-2 text-center text-gray-500">{{ entry.plays }}</td>
                <td class="py-2 text-center text-yellow-600 font-medium">{{ entry.points.toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="mt-4 flex justify-end">
          <button @click="resetLeaderboard" class="text-sm text-red-500 hover:text-red-700 border border-red-200 px-4 py-1.5 rounded-lg hover:bg-red-50 transition">
            리더보드 초기화
          </button>
        </div>
      </div>
    </div>

    <!-- 최근 게임 활동 로그 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="p-4 border-b border-gray-100">
        <h2 class="font-semibold text-gray-800">최근 게임 활동</h2>
      </div>
      <div class="divide-y divide-gray-50">
        <div v-for="log in activityLogs" :key="log.id" class="px-4 py-3 flex items-center gap-3">
          <span class="text-lg">{{ log.icon }}</span>
          <div class="flex-1">
            <p class="text-sm text-gray-800">
              <span class="font-medium">{{ log.user }}</span>
              <span class="text-gray-500">님이 </span>
              <span class="font-medium text-blue-600">{{ log.game }}</span>
              <span class="text-gray-500">에서 </span>
              <span class="font-medium text-yellow-600">{{ log.points }}포인트</span>
              <span class="text-gray-500"> 획득</span>
            </p>
          </div>
          <span class="text-xs text-gray-400">{{ log.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import axios from 'axios'

const selectedGameId = ref(1)

const stats = ref({
  totalPlayers: 3842,
  todayActive: 218,
  totalGames: 9,
  totalPoints: 1284500
})

const games = ref([
  { id: 1, name: '고스톱', icon: '🃏', enabled: true, multiplier: 2.0, dailyPlays: 320, totalPoints: 285000 },
  { id: 2, name: '블랙잭', icon: '🂡', enabled: true, multiplier: 1.5, dailyPlays: 250, totalPoints: 198000 },
  { id: 3, name: '포커', icon: '♠️', enabled: true, multiplier: 2.5, dailyPlays: 180, totalPoints: 312000 },
  { id: 4, name: '홀덤', icon: '🎰', enabled: false, multiplier: 3.0, dailyPlays: 0, totalPoints: 95000 },
  { id: 5, name: '메모리게임', icon: '🧩', enabled: true, multiplier: 1.0, dailyPlays: 410, totalPoints: 142000 },
  { id: 6, name: '2048', icon: '🔢', enabled: true, multiplier: 1.2, dailyPlays: 290, totalPoints: 118000 },
  { id: 7, name: '빙고', icon: '🎱', enabled: true, multiplier: 1.0, dailyPlays: 175, totalPoints: 88000 },
  { id: 8, name: '오목', icon: '⚫', enabled: true, multiplier: 1.5, dailyPlays: 130, totalPoints: 76500 },
  { id: 9, name: '퀴즈', icon: '❓', enabled: true, multiplier: 1.0, dailyPlays: 380, totalPoints: 170000 }
])

const leaderboards = {
  1: [ { name: '고수왕', score: 98500, plays: 84, points: 12400 }, { name: '화투마스터', score: 87200, plays: 72, points: 10800 }, { name: '가람이', score: 75600, plays: 60, points: 9600 }, { name: '전주최고', score: 61000, plays: 51, points: 8200 }, { name: '끝장패', score: 54800, plays: 45, points: 7000 } ],
  2: [ { name: '블랙잭킹', score: 120000, plays: 98, points: 15200 }, { name: '21달인', score: 105000, plays: 88, points: 13800 }, { name: '카드귀신', score: 92000, plays: 76, points: 11400 }, { name: '행운의손', score: 78000, plays: 64, points: 9600 }, { name: '딜러박', score: 65000, plays: 55, points: 8250 } ],
  3: [ { name: '포커페이스', score: 250000, plays: 140, points: 28000 }, { name: '올인왕', score: 198000, plays: 118, points: 22400 }, { name: '블러프킹', score: 175000, plays: 104, points: 20000 }, { name: '콜미', score: 142000, plays: 88, points: 16800 }, { name: '레이즈', score: 128000, plays: 74, points: 14400 } ],
  4: [ { name: '홀덤마스터', score: 320000, plays: 160, points: 38400 }, { name: '리버강', score: 265000, plays: 132, points: 31800 }, { name: '플럭', score: 220000, plays: 110, points: 26400 }, { name: '스트레이트', score: 185000, plays: 96, points: 22200 }, { name: '풀하우스', score: 155000, plays: 80, points: 18600 } ],
  5: [ { name: '기억력甲', score: 9800, plays: 210, points: 8200 }, { name: '카드외우기', score: 9200, plays: 195, points: 7800 }, { name: '집중력왕', score: 8700, plays: 180, points: 7200 }, { name: '두뇌짱', score: 8100, plays: 162, points: 6600 }, { name: '퍼펙트기억', score: 7600, plays: 148, points: 6200 } ],
  6: [ { name: '2048달인', score: 131072, plays: 320, points: 11400 }, { name: '합치기왕', score: 65536, plays: 285, points: 9800 }, { name: '타일마스터', score: 32768, plays: 245, points: 8200 }, { name: '슬라이드킹', score: 16384, plays: 210, points: 6800 }, { name: '숫자게임', score: 8192, plays: 178, points: 5600 } ],
  7: [ { name: '빙고킹', score: 5400, plays: 88, points: 6400 }, { name: '행운카드', score: 5100, plays: 80, points: 6000 }, { name: '완성왕', score: 4800, plays: 74, points: 5600 }, { name: '직선빙고', score: 4500, plays: 68, points: 5200 }, { name: '빙고여왕', score: 4200, plays: 60, points: 4800 } ],
  8: [ { name: '바둑마스터', score: 12800, plays: 64, points: 7400 }, { name: '오목고수', score: 11500, plays: 58, points: 6600 }, { name: '연속오목', score: 10200, plays: 52, points: 5900 }, { name: '전략가', score: 9000, plays: 46, points: 5100 }, { name: '돌놓기왕', score: 7800, plays: 40, points: 4400 } ],
  9: [ { name: '퀴즈왕', score: 9900, plays: 420, points: 12800 }, { name: '지식인', score: 9600, plays: 395, points: 12200 }, { name: '박학다식', score: 9300, plays: 365, points: 11500 }, { name: '만점자', score: 9000, plays: 340, points: 10800 }, { name: '한인상식왕', score: 8700, plays: 315, points: 10200 } ]
}

const currentLeaderboard = computed(() => leaderboards[selectedGameId.value] || [])

const activityLogs = ref([
  { id: 1, user: '고수왕', game: '고스톱', points: 450, icon: '🃏', time: '방금 전' },
  { id: 2, user: '퀴즈왕', game: '퀴즈', points: 200, icon: '❓', time: '2분 전' },
  { id: 3, user: '블랙잭킹', game: '블랙잭', points: 380, icon: '🂡', time: '5분 전' },
  { id: 4, user: '기억력甲', game: '메모리게임', points: 150, icon: '🧩', time: '8분 전' },
  { id: 5, user: '2048달인', game: '2048', points: 290, icon: '🔢', time: '12분 전' },
  { id: 6, user: '빙고킹', game: '빙고', points: 120, icon: '🎱', time: '15분 전' }
])

function toggleGame(game) {
  game.enabled = !game.enabled
}

async function saveMultipliers() {
  try {
    await axios.post('/api/admin/games/multipliers', { games: games.value })
    alert('포인트 배율이 저장되었습니다.')
  } catch {
    alert('저장되었습니다. (데모)')
  }
}

async function resetLeaderboard() {
  const game = games.value.find(g => g.id === selectedGameId.value)
  if (!confirm(`${game?.name} 리더보드를 초기화하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/games/${selectedGameId.value}/leaderboard`)
  } catch {}
  alert('리더보드가 초기화되었습니다. (데모)')
}
</script>
