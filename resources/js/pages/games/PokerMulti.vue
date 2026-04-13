<template>
<div class="select-none h-screen bg-gradient-to-b from-gray-950 via-[#0e1525] to-[#0b1018] overflow-hidden flex flex-col"
  style="font-family:'Noto Sans KR',sans-serif">

  <!-- ═══ 매칭 대기 화면 ═══ -->
  <div v-if="screen==='matching'" class="flex-1 flex items-center justify-center">
    <div class="text-center max-w-sm bg-gray-900 rounded-2xl border border-amber-500/30 p-8">
      <div class="text-5xl mb-4 animate-pulse">🃏</div>
      <h2 class="text-xl font-black text-amber-400 mb-2">멀티플레이어 홀덤</h2>
      <p class="text-gray-400 text-sm mb-6">실시간 대전 — 다른 플레이어와 함께</p>

      <div class="space-y-3 mb-6">
        <div>
          <label class="text-xs text-gray-500 block mb-1">게임 모드</label>
          <div class="flex gap-2">
            <button @click="gameType='normal'" class="flex-1 py-2 rounded-lg font-bold text-sm border-2 transition"
              :class="gameType==='normal' ? 'border-amber-500 bg-amber-500/20 text-amber-400' : 'border-gray-700 text-gray-500'">
              🕐 일반 (15초)
            </button>
            <button @click="gameType='speed'" class="flex-1 py-2 rounded-lg font-bold text-sm border-2 transition"
              :class="gameType==='speed' ? 'border-red-500 bg-red-500/20 text-red-400' : 'border-gray-700 text-gray-500'">
              ⚡ 스피드 (10초)
            </button>
          </div>
        </div>
        <div>
          <label class="text-xs text-gray-500 block mb-1">블라인드</label>
          <select v-model.number="blindLevel" class="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white">
            <option :value="20">10/20 (초보)</option>
            <option :value="50">25/50 (중급)</option>
            <option :value="100">50/100 (상급)</option>
            <option :value="200">100/200 (프로)</option>
          </select>
        </div>
      </div>

      <button v-if="!matching" @click="startMatch"
        class="w-full py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-gray-950 font-black text-base transition">
        🎮 매칭 시작
      </button>

      <div v-else class="space-y-3">
        <div class="flex items-center justify-center gap-2 text-amber-400">
          <div class="w-5 h-5 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></div>
          <span class="font-bold">매칭 중... ({{ queueCount }}명 대기)</span>
        </div>
        <div class="text-xs text-gray-500">{{ matchWait }}초 대기 · 30초 후 AI로 자동 시작</div>
        <button @click="cancelMatch" class="text-gray-500 text-sm hover:text-gray-300">취소</button>
      </div>

      <router-link to="/games/poker" class="block mt-4 text-gray-500 text-sm hover:text-gray-300">← 로비로</router-link>
    </div>
  </div>

  <!-- ═══ 게임 화면 ═══ -->
  <template v-else-if="screen==='game'">
    <div class="bg-gradient-to-b from-[#0a1628] to-[#0d1f38] border-b-2 border-blue-900/60 shrink-0 px-2.5 py-1">
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <span class="text-blue-400 text-sm font-bold font-mono">{{ gameState?.sb }}/{{ gameState?.bb }}</span>
          <span class="text-[10px] px-2 py-0.5 rounded-full font-bold" :class="gameType==='speed' ? 'bg-red-600 text-white' : 'bg-blue-600 text-white'">
            {{ gameType==='speed' ? '⚡스피드' : '🕐일반' }}
          </span>
        </div>
        <div class="text-white text-xs font-mono">{{ gameState?.gameId?.slice(-6) }}</div>
        <button @click="leaveGame" class="bg-red-700 hover:bg-red-600 text-white text-xs font-bold px-3 py-1 rounded">나가기</button>
      </div>
    </div>

    <!-- 테이블 -->
    <div class="flex-1 relative">
      <PokerTable :seats="displaySeats" :community="gameState?.community||[]" :pot="gameState?.pot||0"
        :stage="gameState?.stage||'preflop'" :dealer-idx="gameState?.dealerIdx||0" :showdown="gameState?.status==='showdown'"
        :hand-results="gameState?.result" :game-over="gameState?.status==='finished'" :bl="{sb:gameState?.sb||10,bb:gameState?.bb||20}"
        :act-idx="gameState?.actIdx??-1" :turn-timer="turnCountdown" :turn-timer-max="gameState?.turnTime||15" />
    </div>

    <!-- 액션 버튼 (내 턴일 때만) -->
    <div v-if="isMyTurn" class="bg-gray-900/95 border-t border-gray-800 px-4 py-3 shrink-0">
      <div class="flex items-center justify-center gap-3 max-w-lg mx-auto">
        <button @click="sendAction('fold')" class="bg-red-600 hover:bg-red-500 text-white font-bold px-5 py-2.5 rounded-xl text-sm">폴드</button>
        <button v-if="canCheck" @click="sendAction('check')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-5 py-2.5 rounded-xl text-sm">체크</button>
        <button v-else @click="sendAction('call')" class="bg-blue-600 hover:bg-blue-500 text-white font-bold px-5 py-2.5 rounded-xl text-sm">콜 ({{ callAmount }})</button>
        <button @click="sendAction('allin')" class="bg-amber-600 hover:bg-amber-500 text-white font-bold px-5 py-2.5 rounded-xl text-sm">올인</button>
      </div>
      <div class="flex items-center gap-2 max-w-lg mx-auto mt-2">
        <input type="range" v-model.number="raiseAmount" :min="minRaise" :max="myChips" class="flex-1" />
        <button @click="sendAction('raise', raiseAmount)" class="bg-green-600 hover:bg-green-500 text-white font-bold px-4 py-2 rounded-xl text-sm whitespace-nowrap">
          레이즈 {{ raiseAmount.toLocaleString() }}
        </button>
      </div>
    </div>

    <!-- 결과 오버레이 -->
    <div v-if="gameState?.status==='showdown' && gameState?.result" class="absolute inset-0 bg-black/60 flex items-center justify-center z-50">
      <div class="bg-gray-900 rounded-2xl border border-amber-500/30 p-6 max-w-md text-center">
        <div class="text-3xl mb-2">{{ didIWin ? '🏆' : '😢' }}</div>
        <h3 class="text-xl font-black mb-3" :class="didIWin ? 'text-amber-400' : 'text-gray-400'">
          {{ didIWin ? '승리!' : '패배' }}
        </h3>
        <div v-for="w in gameState.result.winners" :key="w.seatIdx" class="text-sm text-gray-300 mb-1">
          {{ w.name }} — {{ w.hand }} (+{{ w.pot.toLocaleString() }})
        </div>
        <div v-if="gameState.result.showdown" class="mt-3 space-y-1">
          <div v-for="s in gameState.result.showdown" :key="s.seatIdx" class="text-xs text-gray-500">
            {{ s.name }}: {{ s.cards.join(' ') }} → {{ s.hand }}
          </div>
        </div>
        <button @click="startMatch" class="mt-4 bg-amber-500 text-gray-950 font-bold px-6 py-2 rounded-xl">다시 매칭</button>
      </div>
    </div>

    <!-- 인게임 채팅 -->
    <div class="absolute bottom-20 left-2 w-64 z-40">
      <div class="max-h-32 overflow-y-auto mb-1 space-y-0.5">
        <div v-for="(msg, i) in chatMessages" :key="i" class="text-xs bg-black/50 text-white/80 rounded px-2 py-0.5">
          <span class="text-amber-400 font-bold">{{ msg.userName }}:</span> {{ msg.message }}
        </div>
      </div>
      <div class="flex gap-1">
        <input v-model="chatInput" @keyup.enter="sendChat" placeholder="채팅..." maxlength="200"
          class="flex-1 bg-black/50 border border-white/10 rounded px-2 py-1 text-xs text-white outline-none" />
        <button @click="sendChat" class="bg-amber-500/80 text-xs px-2 py-1 rounded font-bold">전송</button>
      </div>
    </div>
  </template>
</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usePokerSound } from '@/composables/usePokerSound'
import PokerTable from '@/components/poker/PokerTable.vue'
import axios from 'axios'

const router = useRouter()
const auth = useAuthStore()
const { soundDeal, soundBet, soundFold, soundCheck, soundAllIn, soundWin, soundLose, soundMyTurn, soundFlop, resumeAudio } = usePokerSound()

const screen = ref('matching')
const gameType = ref('normal')
const blindLevel = ref(20)
const matching = ref(false)
const queueCount = ref(0)
const gameState = ref(null)
const chatMessages = ref([])
const chatInput = ref('')
const turnCountdown = ref(0)
const raiseAmount = ref(40)
const matchWait = ref(0)

let matchInterval = null
let waitCounter = null
let timeoutInterval = null
let echoChannel = null

const myId = computed(() => auth.user?.id)
const mySeat = computed(() => gameState.value?.seats?.find(s => s.id === myId.value))
const myChips = computed(() => mySeat.value?.chips || 0)
const isMyTurn = computed(() => {
  if (!gameState.value || gameState.value.status !== 'playing') return false
  return gameState.value.seats[gameState.value.actIdx]?.id === myId.value
})
const canCheck = computed(() => {
  if (!mySeat.value || !gameState.value) return false
  return gameState.value.betLevel <= (mySeat.value.bet || 0)
})
const callAmount = computed(() => Math.max(0, (gameState.value?.betLevel || 0) - (mySeat.value?.bet || 0)))
const minRaise = computed(() => Math.max((gameState.value?.betLevel || 0) * 2, (gameState.value?.bb || 20) * 2))
const didIWin = computed(() => gameState.value?.result?.winners?.some(w => gameState.value.seats[w.seatIdx]?.id === myId.value))

const displaySeats = computed(() => {
  if (!gameState.value?.seats) return []
  return gameState.value.seats.map(s => ({
    ...s,
    name: s.name,
    isPlayer: s.id === myId.value,
    emoji: s.id === myId.value ? '😎' : '👤',
    color: s.id === myId.value ? '#f59e0b' : '#6b7280',
    showCards: s.id === myId.value || gameState.value.status === 'showdown',
    isOut: false,
  }))
})

// ── 매칭 ──
async function startMatch() {
  matching.value = true
  screen.value = 'matching'
  gameState.value = null
  resumeAudio()

  matchWait.value = 0
  waitCounter = setInterval(() => matchWait.value++, 1000)
  pollMatch()
  matchInterval = setInterval(pollMatch, 3000) // 3초마다 폴링
}

async function pollMatch() {
  try {
    const { data } = await axios.post('/api/poker/multi/quick-match', {
      type: gameType.value,
      bb: blindLevel.value,
    })

    queueCount.value = data.queue_count || 0

    if (data.status === 'started') {
      matching.value = false
      if (matchInterval) { clearInterval(matchInterval); matchInterval = null }
      gameState.value = data.state
      screen.value = 'game'
      soundDeal()
      startEcho(data.gameId)
      startTimeoutPoller(data.gameId)
    }
  } catch (e) {
    console.error('Match error:', e)
  }
}

function cancelMatch() {
  matching.value = false
  matchWait.value = 0
  if (matchInterval) { clearInterval(matchInterval); matchInterval = null }
  if (waitCounter) { clearInterval(waitCounter); waitCounter = null }
}

// ── Echo WebSocket 연결 ──
function startEcho(gameId) {
  if (!window.Echo) return
  echoChannel = window.Echo.join(`poker.${gameId}`)
    .listen('.game.action', (e) => {
      gameState.value = e.state
      if (e.action?.action === 'fold') soundFold()
      else if (e.action?.action === 'call' || e.action?.action === 'raise') soundBet()
      else if (e.action?.action === 'allin') soundAllIn()
      else if (e.action?.type === 'game_start') soundDeal()

      // 스테이지 변경 시
      if (['flop', 'turn', 'river'].includes(e.state?.stage)) soundFlop()
    })
    .listen('.game.chat', (e) => {
      chatMessages.value.push(e)
      if (chatMessages.value.length > 50) chatMessages.value.shift()
    })
}

// ── 타임아웃 폴링 ──
function startTimeoutPoller(gameId) {
  timeoutInterval = setInterval(async () => {
    if (!gameState.value || gameState.value.status !== 'playing') return
    try {
      const { data } = await axios.get(`/api/poker/multi/game/${gameId}/timeout`)
      turnCountdown.value = data.remaining || 0
      if (data.ai_acted && data.state) {
        gameState.value = data.state
        soundBet()
      } else if (data.timeout) {
        const { data: fresh } = await axios.get(`/api/poker/multi/game/${gameId}`)
        gameState.value = fresh.data
      }
    } catch {}
  }, 1000)
}

// ── 액션 전송 ──
async function sendAction(action, amount = 0) {
  if (!isMyTurn.value || !gameState.value) return
  try {
    const { data } = await axios.post(`/api/poker/multi/game/${gameState.value.gameId}/action`, { action, amount })
    if (data.success) {
      gameState.value = data.data
      if (action === 'fold') soundFold()
      else if (action === 'check') soundCheck()
      else if (action === 'call' || action === 'raise') soundBet()
      else if (action === 'allin') soundAllIn()
    }
  } catch (e) {
    alert(e.response?.data?.message || '액션 실패')
  }
}

// ── 채팅 ──
async function sendChat() {
  if (!chatInput.value.trim() || !gameState.value) return
  try {
    await axios.post(`/api/poker/multi/game/${gameState.value.gameId}/chat`, { message: chatInput.value.trim() })
    chatMessages.value.push({ userName: auth.user?.nickname || auth.user?.name, message: chatInput.value.trim() })
    chatInput.value = ''
  } catch {}
}

function leaveGame() {
  if (confirm('게임을 나가시겠습니까?')) {
    cleanup()
    router.push('/games/poker')
  }
}

function cleanup() {
  if (matchInterval) { clearInterval(matchInterval); matchInterval = null }
  if (waitCounter) { clearInterval(waitCounter); waitCounter = null }
  if (timeoutInterval) { clearInterval(timeoutInterval); timeoutInterval = null }
  if (echoChannel) { echoChannel.leave(); echoChannel = null }
}

// 내 턴 알림
watch(isMyTurn, (v) => { if (v) soundMyTurn() })
// 승패 사운드
watch(() => gameState.value?.status, (s) => {
  if (s === 'showdown') { didIWin.value ? soundWin() : soundLose() }
})

onMounted(resumeAudio)
onUnmounted(cleanup)
</script>
