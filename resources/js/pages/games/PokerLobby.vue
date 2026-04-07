<template>
<div class="min-h-screen bg-gray-950 text-white">
  <div class="max-w-5xl mx-auto px-4 py-6 space-y-5">

    <!-- Header -->
    <div class="text-center">
      <div class="flex items-center justify-center gap-2 mb-1">
        <span class="text-3xl">🎰</span>
        <h1 class="text-2xl font-black text-amber-400">SomeKorean 포커</h1>
      </div>
      <p class="text-xs text-blue-400 tracking-[0.3em] font-bold">POKER PLATFORM</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- ===== MAIN (LEFT 2/3) ===== -->
      <div class="lg:col-span-2 space-y-4">

        <!-- 🏆 토너먼트 -->
        <div class="bg-gray-900 rounded-xl border border-amber-400/20 p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-bold text-amber-400">🏆 토너먼트</h2>
            <span class="text-xs text-gray-500">실시간 업데이트</span>
          </div>

          <!-- 예정된 토너먼트 -->
          <div v-if="upcomingTournaments.length" class="space-y-2 mb-4">
            <div v-for="t in upcomingTournaments" :key="t.id"
              class="bg-gray-800 rounded-lg p-3 flex items-center justify-between gap-3 hover:bg-gray-750 transition">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span :class="typeBadgeClass(t.type)" class="text-[10px] px-1.5 py-0.5 rounded font-bold">{{ t.type }}</span>
                  <span class="text-white text-sm font-bold truncate">{{ t.title }}</span>
                </div>
                <div class="flex items-center gap-3 text-xs text-gray-400">
                  <span>💰 {{ t.buy_in.toLocaleString() }} 칩</span>
                  <span>👥 {{ t.registered_count || 0 }}/{{ t.max_players }}명</span>
                  <span>🟢 {{ t.online_count || 0 }} 온라인</span>
                </div>
              </div>
              <div class="text-right shrink-0">
                <div class="text-amber-400 text-xs font-mono font-bold mb-1">{{ formatTournamentTime(t.scheduled_at) }}</div>
                <router-link :to="'/games/poker/tournament/' + t.id"
                  class="bg-amber-500 hover:bg-amber-400 text-gray-950 text-xs font-bold px-3 py-1.5 rounded-lg inline-block transition">
                  {{ isRegistered(t.id) ? '대기실 입장' : '참가 신청' }}
                </router-link>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-600 text-sm">예정된 토너먼트가 없습니다</div>

          <!-- 진행 중인 토너먼트 -->
          <div v-if="runningTournaments.length">
            <div class="text-xs text-gray-500 font-bold mb-2 mt-2">🔴 진행 중</div>
            <div v-for="t in runningTournaments" :key="t.id"
              class="bg-red-950/30 border border-red-500/20 rounded-lg p-3 flex items-center justify-between mb-2">
              <div>
                <span class="text-white text-sm font-bold">{{ t.title }}</span>
                <div class="text-xs text-gray-400">👥 {{ t.remaining_count || 0 }}명 남음</div>
              </div>
              <button class="bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs px-3 py-1.5 rounded-lg">👁️ 관전</button>
            </div>
          </div>
        </div>

        <!-- 🎮 게임 모드 -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <router-link to="/games/poker/play" class="bg-gray-900 rounded-xl border border-blue-400/20 p-4 hover:border-blue-400/40 transition block">
            <div class="text-2xl mb-2">🎮</div>
            <div class="text-sm font-bold text-blue-400">솔로 AI 연습</div>
            <div class="text-xs text-gray-500 mt-1">AI 상대 토너먼트 연습</div>
          </router-link>
          <router-link to="/games/blackjack" class="bg-gray-900 rounded-xl border border-green-400/20 p-4 hover:border-green-400/40 transition block">
            <div class="text-2xl mb-2">🃏</div>
            <div class="text-sm font-bold text-green-400">블랙잭</div>
            <div class="text-xs text-gray-500 mt-1">솔로 블랙잭 게임</div>
          </router-link>
          <router-link to="/games/poker/tutorial" class="bg-gray-900 rounded-xl border border-purple-400/20 p-4 hover:border-purple-400/40 transition block">
            <div class="text-2xl mb-2">📚</div>
            <div class="text-sm font-bold text-purple-400">룰 & 튜토리얼</div>
            <div class="text-xs text-gray-500 mt-1">핸드 랭킹, 포지션 가이드</div>
          </router-link>
        </div>
      </div>

      <!-- ===== SIDEBAR (RIGHT 1/3) ===== -->
      <div class="space-y-4">

        <!-- 💰 칩 지갑 -->
        <div class="bg-gray-900 rounded-xl border border-amber-400/20 p-4">
          <h2 class="text-sm font-bold text-amber-400 mb-3">💰 칩 지갑</h2>
          <div v-if="wallet" class="text-center mb-3">
            <div class="text-3xl font-black text-amber-400 font-mono">{{ (wallet.chips_balance || 0).toLocaleString() }}</div>
            <div class="text-xs text-gray-500">보유 칩</div>
            <div class="text-xs text-gray-400 mt-1">포인트: <span class="text-amber-300 font-bold">{{ (auth.user?.points || 0).toLocaleString() }}P</span></div>
          </div>
          <div class="flex gap-2">
            <input v-model.number="walletAmount" type="number" min="1000" step="1000"
              class="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white text-center focus:border-amber-400 focus:outline-none"
              placeholder="금액">
            <button @click="handleDeposit" :disabled="walletLoading || !walletAmount"
              class="bg-green-600 hover:bg-green-500 disabled:bg-gray-700 text-white text-xs font-bold px-3 py-2 rounded-lg">입금</button>
            <button @click="handleWithdraw" :disabled="walletLoading || !walletAmount"
              class="bg-red-600 hover:bg-red-500 disabled:bg-gray-700 text-white text-xs font-bold px-3 py-2 rounded-lg">출금</button>
          </div>
          <div v-if="walletError" class="text-xs text-red-400 mt-2 text-center">{{ walletError }}</div>
        </div>

        <!-- 📊 내 기록 -->
        <div class="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <h2 class="text-sm font-bold text-amber-400 mb-3">📊 내 기록</h2>
          <div class="space-y-2">
            <div v-for="s in statsDisplay" :key="s.label" class="flex justify-between text-xs">
              <span class="text-gray-500">{{ s.label }}</span>
              <span :class="s.color" class="font-bold font-mono">{{ s.value }}</span>
            </div>
          </div>
        </div>

        <!-- 🏅 리더보드 -->
        <div class="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <h2 class="text-sm font-bold text-amber-400 mb-3">🏅 리더보드</h2>
          <div v-if="leaderboard.length" class="space-y-2">
            <div v-for="(e, i) in leaderboard.slice(0, 5)" :key="i" class="flex items-center gap-2 text-xs">
              <span class="w-5 text-center font-bold" :class="i===0?'text-amber-400':i===1?'text-gray-300':i===2?'text-orange-400':'text-gray-500'">
                {{ ['🏆','🥈','🥉'][i] || (i+1) }}
              </span>
              <span class="flex-1 text-gray-300 truncate">{{ e.user?.name || e.user?.nickname || '?' }}</span>
              <span class="text-amber-400 font-bold font-mono">{{ (e.total_prize_won || 0).toLocaleString() }}</span>
            </div>
          </div>
          <div v-else class="text-xs text-gray-600 text-center py-2">데이터 없음</div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usePokerWallet } from '@/composables/usePokerWallet'
import axios from 'axios'

const auth = useAuthStore()
const {
  wallet, stats, leaderboard, loading: walletLoading, error: walletError,
  fetchWallet, deposit, withdraw, fetchStats, fetchLeaderboard
} = usePokerWallet()

const walletAmount = ref(1000)
const upcomingTournaments = ref([])
const runningTournaments = ref([])
const myEntries = ref([]) // tournament IDs I'm registered for

const statsDisplay = computed(() => {
  const s = stats.value || {}
  return [
    { label: '참가 횟수', value: s.games_played || 0, color: 'text-white' },
    { label: '최고 성적', value: s.best_place ? s.best_place + '위' : '-', color: 'text-amber-400' },
    { label: '총 상금', value: (s.total_prize_won || 0).toLocaleString(), color: 'text-green-400' },
    { label: '바운티', value: s.total_bounties || 0, color: 'text-yellow-400' },
  ]
})

function typeBadgeClass(type) {
  const m = { freeroll: 'bg-green-500/20 text-green-400', micro: 'bg-blue-500/20 text-blue-400', regular: 'bg-amber-500/20 text-amber-400', high_roller: 'bg-red-500/20 text-red-400' }
  return m[type] || m.regular
}

function formatTournamentTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  const now = new Date()
  const isToday = d.toDateString() === now.toDateString()
  const tomorrow = new Date(now); tomorrow.setDate(tomorrow.getDate() + 1)
  const isTomorrow = d.toDateString() === tomorrow.toDateString()
  const time = d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false })
  if (isToday) return `오늘 ${time}`
  if (isTomorrow) return `내일 ${time}`
  return d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }) + ' ' + time
}

function isRegistered(tournamentId) {
  return myEntries.value.includes(tournamentId)
}

async function fetchTournaments() {
  try {
    const { data } = await axios.get('/api/poker/tournaments')
    if (data.success) {
      upcomingTournaments.value = data.data.upcoming || []
      runningTournaments.value = data.data.running || []
    }
  } catch (e) { console.error(e) }
}

async function fetchMyEntries() {
  // Check which tournaments I'm in
  upcomingTournaments.value.forEach(async (t) => {
    try {
      const { data } = await axios.get(`/api/poker/tournaments/${t.id}`)
      if (data.success) {
        const me = data.data.entries?.find(e => e.user_id === auth.user?.id)
        if (me) myEntries.value.push(t.id)
      }
    } catch (e) { /* ignore */ }
  })
}

async function handleDeposit() {
  if (!walletAmount.value || walletAmount.value < 1000) return
  const result = await deposit(walletAmount.value)
  if (result?.success) auth.user.points = result.data.points
}

async function handleWithdraw() {
  if (!walletAmount.value || walletAmount.value < 1000) return
  const result = await withdraw(walletAmount.value)
  if (result?.success) auth.user.points = result.data.points
}

let echoChannel = null

onMounted(async () => {
  if (auth.isLoggedIn) {
    await Promise.all([fetchWallet(), fetchStats(), fetchLeaderboard(), fetchTournaments()])
    await fetchMyEntries()
  } else {
    await fetchTournaments()
  }

  // Real-time lobby updates
  if (window.Echo) {
    echoChannel = window.Echo.channel('poker.lobby')
    echoChannel.listen('.tournament.updated', () => { fetchTournaments() })
    echoChannel.listen('.lobby.updated', () => { fetchTournaments() })
  }
})

onUnmounted(() => {
  if (echoChannel) { window.Echo.leave('poker.lobby') }
})
</script>
