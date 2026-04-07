<template>
<div class="min-h-screen bg-gray-950 text-white">
  <div class="max-w-4xl mx-auto px-4 py-6 space-y-6">

    <!-- Header -->
    <div class="text-center">
      <div class="flex items-center justify-center gap-2 mb-1">
        <button @click="$router.back()" class="text-white/50 hover:text-white text-lg absolute left-4">&#9664;</button>
        <span class="text-3xl">&#127942;</span>
        <h1 class="text-2xl font-black text-amber-400 tracking-wider">&#53664;&#45320;&#47676;&#53944; &#54252;&#52964;</h1>
      </div>
      <p class="text-xs text-blue-400 tracking-[0.3em] font-bold">TOURNAMENT SIMULATOR</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- Left Column -->
      <div class="lg:col-span-2 space-y-4">

        <!-- Wallet Widget -->
        <div class="bg-gray-900 rounded-xl border border-amber-400/20 p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-bold text-amber-400">&#128176; &#52841; &#51648;&#44049;</h2>
            <div v-if="wallet" class="text-xs text-gray-400">
              &#54252;&#51064;&#53944;: <span class="text-amber-300 font-bold">{{ (auth.user?.points || 0).toLocaleString() }}P</span>
            </div>
          </div>
          <div v-if="wallet" class="text-center mb-3">
            <div class="text-3xl font-black text-amber-400 font-mono">{{ wallet.chip_balance?.toLocaleString() || '0' }}</div>
            <div class="text-xs text-gray-500">&#48372;&#50976; &#52841;</div>
          </div>
          <div v-else class="text-center mb-3 py-2">
            <div class="text-sm text-gray-500">&#47196;&#44536;&#51064; &#54980; &#51060;&#50857; &#44032;&#45733;</div>
          </div>
          <div class="flex gap-2">
            <div class="flex-1">
              <input v-model.number="walletAmount" type="number" min="100" step="100"
                class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white text-center focus:border-amber-400 focus:outline-none"
                placeholder="&#44552;&#50529;">
            </div>
            <button @click="handleDeposit" :disabled="walletLoading || !walletAmount"
              class="bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-white text-xs font-bold px-4 py-2 rounded-lg transition">
              &#51077;&#44552;
            </button>
            <button @click="handleWithdraw" :disabled="walletLoading || !walletAmount"
              class="bg-red-600 hover:bg-red-700 disabled:bg-gray-700 text-white text-xs font-bold px-4 py-2 rounded-lg transition">
              &#52636;&#44552;
            </button>
          </div>
          <div v-if="walletError" class="text-xs text-red-400 mt-2 text-center">{{ walletError }}</div>
        </div>

        <!-- Tournament Setup -->
        <div class="bg-gray-900 rounded-xl border border-blue-400/20 p-4">
          <h2 class="text-sm font-bold text-blue-400 mb-4">&#9881;&#65039; &#45824;&#54924; &#49444;&#51221;</h2>

          <!-- Buy-in -->
          <div class="mb-4">
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-400">&#48148;&#51060;&#51064;</span>
              <span class="text-amber-400 font-bold font-mono">{{ config.buyIn.toLocaleString() }} &#52841;</span>
            </div>
            <input v-model.number="config.buyIn" type="range" min="50" max="10000" step="50"
              class="w-full accent-amber-400">
          </div>

          <!-- Total Players -->
          <div class="mb-4">
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-400">&#52280;&#44032; &#51064;&#50896;</span>
              <span class="text-blue-400 font-bold font-mono">{{ config.totalPlayers }}&#47749;</span>
            </div>
            <input v-model.number="config.totalPlayers" type="range" min="18" max="1000" step="9"
              class="w-full accent-blue-400">
          </div>

          <!-- Start Chips -->
          <div class="mb-4">
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-400">&#49884;&#51089; &#52841;</span>
              <span class="text-green-400 font-bold font-mono">{{ config.startChips.toLocaleString() }}</span>
            </div>
            <input v-model.number="config.startChips" type="range" min="5000" max="100000" step="1000"
              class="w-full accent-green-400">
          </div>

          <!-- Summary -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-4">
            <div class="bg-gray-800 rounded-lg p-2 text-center">
              <div class="text-[10px] text-gray-500">&#52509; &#49345;&#44552;</div>
              <div class="text-sm font-bold text-amber-400 font-mono">{{ prizePool.toLocaleString() }}</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-2 text-center">
              <div class="text-[10px] text-gray-500">&#51077;&#49345;&#44428;</div>
              <div class="text-sm font-bold text-green-400 font-mono">{{ paidSlots }}&#47749;</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-2 text-center">
              <div class="text-[10px] text-gray-500">&#53580;&#51060;&#48660; &#49688;</div>
              <div class="text-sm font-bold text-blue-400 font-mono">{{ tableCount }}</div>
            </div>
            <div class="bg-gray-800 rounded-lg p-2 text-center">
              <div class="text-[10px] text-gray-500">&#49884;&#51089; &#48660;&#46972;&#51064;&#46300;</div>
              <div class="text-sm font-bold text-white font-mono">10/20</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column -->
      <div class="space-y-4">

        <!-- Stats Panel -->
        <div class="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <h2 class="text-sm font-bold text-amber-400 mb-3">&#128202; &#45236; &#44592;&#47197;</h2>
          <div class="space-y-2">
            <div class="flex justify-between text-xs">
              <span class="text-gray-500">&#52280;&#44032; &#54943;&#49688;</span>
              <span class="text-white font-bold font-mono">{{ myStats.gamesPlayed || 0 }}</span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-500">&#52572;&#44256; &#49457;&#51201;</span>
              <span class="text-amber-400 font-bold font-mono">{{ myStats.bestPlacement ? myStats.bestPlacement + '&#50948;' : '-' }}</span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-500">&#52509; &#49345;&#44552;</span>
              <span class="text-green-400 font-bold font-mono">{{ (myStats.totalWinnings || 0).toLocaleString() }}</span>
            </div>
            <div class="flex justify-between text-xs">
              <span class="text-gray-500">&#48148;&#50868;&#54000;</span>
              <span class="text-yellow-400 font-bold font-mono">{{ myStats.bounties || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Leaderboard Preview -->
        <div class="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <div class="flex items-center justify-between mb-3">
            <h2 class="text-sm font-bold text-amber-400">&#127941; &#47532;&#45908;&#48372;&#46300;</h2>
            <RouterLink to="/games/leaderboard" class="text-xs text-blue-400 hover:text-blue-300">&#51204;&#52404; &#48372;&#44592; &#8594;</RouterLink>
          </div>
          <div v-if="leaderboard.length" class="space-y-2">
            <div v-for="(entry, i) in leaderboard.slice(0, 5)" :key="i"
              class="flex items-center gap-2 text-xs">
              <span class="w-5 text-center font-bold" :class="i === 0 ? 'text-amber-400' : i === 1 ? 'text-gray-300' : i === 2 ? 'text-orange-400' : 'text-gray-500'">
                {{ i === 0 ? '&#127942;' : i === 1 ? '&#129352;' : i === 2 ? '&#129353;' : (i + 1) }}
              </span>
              <span class="flex-1 text-gray-300 truncate">{{ entry.user_name || entry.name || '&#51061;&#47749;' }}</span>
              <span class="text-amber-400 font-bold font-mono">{{ (entry.total_winnings || 0).toLocaleString() }}</span>
            </div>
          </div>
          <div v-else class="text-xs text-gray-600 text-center py-3">&#50500;&#51649; &#45936;&#51060;&#53552; &#50630;&#51020;</div>
        </div>

        <!-- Prize Structure -->
        <div class="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <h2 class="text-sm font-bold text-amber-400 mb-3">&#128176; &#49345;&#44552; &#44396;&#51312;</h2>
          <div class="space-y-1">
            <div v-for="p in prizes" :key="p.place" class="flex justify-between text-xs">
              <span class="text-gray-400">{{ p.place }}</span>
              <span class="text-amber-400 font-mono">{{ Math.floor(prizePool * p.pct / 100).toLocaleString() }} ({{ p.pct }}%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-col sm:flex-row gap-3 justify-center pt-2 pb-8">
      <button @click="startGame"
        class="bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-gray-950 font-black text-lg px-8 py-3 rounded-xl shadow-lg shadow-amber-500/20 transition-all hover:scale-105">
        &#127918; &#45824;&#54924; &#49884;&#51089;
      </button>
      <RouterLink to="/games/poker/tutorial"
        class="bg-gray-800 hover:bg-gray-700 text-blue-400 font-bold text-sm px-6 py-3 rounded-xl border border-blue-400/20 transition text-center">
        &#128218; &#47344; &amp; &#53916;&#53664;&#47532;&#50620;
      </RouterLink>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePokerWallet } from '@/composables/usePokerWallet'

const router = useRouter()
const auth = useAuthStore()
const {
  wallet, stats, leaderboard, loading: walletLoading, error: walletError,
  fetchWallet, deposit, withdraw, fetchStats, fetchLeaderboard
} = usePokerWallet()

const walletAmount = ref(500)

const config = ref({
  buyIn: 400,
  totalPlayers: 90,
  startChips: 15000,
})

const myStats = computed(() => stats.value || {})
const prizePool = computed(() => config.value.buyIn * config.value.totalPlayers)
const paidSlots = computed(() => Math.max(1, Math.floor(config.value.totalPlayers * 0.15)))
const tableCount = computed(() => Math.ceil(config.value.totalPlayers / 9))

const prizes = computed(() => {
  const ps = paidSlots.value
  const p = []
  if (ps >= 10) {
    p.push({ place: '1st', pct: 25 }, { place: '2nd', pct: 16 }, { place: '3rd', pct: 11 })
    p.push({ place: '4~6th', pct: 7 }, { place: '7~10th', pct: 4 })
    const rem = 100 - 25 - 16 - 11 - 7 * 3 - 4 * 4
    if (ps > 10) p.push({ place: `11~${ps}th`, pct: Math.max(1, Math.round(rem / (ps - 10))) })
  } else {
    p.push({ place: '1st', pct: 50 }, { place: '2nd', pct: 30 }, { place: '3rd', pct: 20 })
  }
  return p
})

async function handleDeposit() {
  if (!walletAmount.value || walletAmount.value < 100) return
  await deposit(walletAmount.value)
}

async function handleWithdraw() {
  if (!walletAmount.value || walletAmount.value < 100) return
  await withdraw(walletAmount.value)
}

function startGame() {
  sessionStorage.setItem('pokerConfig', JSON.stringify(config.value))
  router.push('/games/poker/play')
}

onMounted(async () => {
  if (auth.isLoggedIn) {
    await Promise.all([fetchWallet(), fetchStats(), fetchLeaderboard()])
  }
})
</script>
