<template>
<div class="select-none h-screen bg-gradient-to-b from-gray-950 via-[#0e1525] to-[#0b1018] flex flex-col overflow-hidden"
  style="font-family:'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif;">

  <!-- ===== RESULT SCREEN ===== -->
  <div v-if="tourneyOver" class="min-h-screen flex items-center justify-center p-4">
    <div class="text-center max-w-md bg-gray-900 rounded-2xl border border-amber-400/30 p-8 space-y-4">
      <div class="text-5xl">{{ inMoney ? '&#127942;' : '&#128148;' }}</div>
      <h2 :class="inMoney ? 'text-amber-400' : 'text-red-500'" class="text-2xl font-black">
        {{ inMoney ? '&#51077;&#49345; &#52629;&#54616;&#54633;&#45768;&#45796;!' : '&#53448;&#46973;' }}
      </h2>
      <div class="text-5xl font-black font-mono" :class="inMoney ? 'text-green-400' : 'text-red-400'">
        {{ finalPlace }}&#50948;
      </div>
      <div class="text-sm text-gray-400">/ {{ config.totalPlayers }}&#47749; &#51473;</div>

      <div v-if="inMoney" class="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
        <div class="text-green-400 font-bold">&#128176; &#49345;&#44552; &#54925;&#46301;!</div>
        <div class="text-green-300 text-lg font-bold font-mono">{{ calcPrize().toLocaleString() }} &#52841;</div>
      </div>

      <div v-if="myBounties.length > 0" class="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
        <div class="text-yellow-400 font-bold">&#128176; &#48148;&#50868;&#54000; {{ myBounties.length }}&#47749; &#51228;&#44144;</div>
        <div class="flex gap-1 justify-center flex-wrap mt-1">
          <span v-for="(b, i) in myBounties" :key="i"
            class="bg-amber-400/10 border border-amber-400/20 rounded-md px-2 py-0.5 text-[11px] text-amber-400">
            {{ b.emoji }} {{ b.name }}
          </span>
        </div>
        <div class="text-yellow-300 text-sm font-mono mt-1">+{{ (myBounties.length * Math.floor(config.buyIn * 0.1)).toLocaleString() }} &#52841;</div>
      </div>

      <div class="text-gray-600 text-sm">&#54540;&#47112;&#51060; &#54592;&#46300;: {{ handNum }} | &#52572;&#44256; &#48660;&#46972;&#51064;&#46300;: {{ bl.sb }}/{{ bl.bb }}</div>

      <div class="flex gap-3 justify-center pt-2">
        <button @click="handleRestart"
          class="px-8 py-3 rounded-xl bg-amber-500 hover:bg-amber-400 text-gray-950 font-bold text-base transition">
          &#45796;&#49884; &#46020;&#51204;
        </button>
        <router-link to="/games/poker"
          class="px-8 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 font-bold text-base border border-gray-700 transition">
          &#47196;&#48708;&#47196;
        </router-link>
      </div>
    </div>
  </div>

  <!-- ===== GAME SCREEN ===== -->
  <template v-else-if="screen === 'game'">
    <!-- Top bar -->
    <div class="bg-gradient-to-b from-[#0a1628] to-[#0d1f38] border-b-2 border-blue-900/60 shrink-0 px-2.5 py-1.5">
      <div class="flex justify-between items-center flex-wrap gap-1">
        <div class="flex items-center gap-1.5">
          <div class="bg-red-700 rounded px-2 py-0.5 text-[11px] font-extrabold text-white tracking-wider">LEVEL {{ blindLevel + 1 }}</div>
          <div class="text-blue-400 text-sm font-bold font-mono">{{ bl.sb.toLocaleString() }}/{{ bl.bb.toLocaleString() }}</div>
          <div v-if="bl.ante > 0" class="text-gray-500 text-[10px]">&#50532;&#54000; {{ bl.ante }}</div>
          <div :class="levelTimer <= 60 ? 'bg-red-500/30 border-red-500' : 'bg-white/5 border-white/10'" class="rounded px-2 py-0.5 border">
            <span :class="levelTimer <= 60 ? 'text-red-500' : 'text-emerald-400'" class="text-sm font-bold font-mono">{{ fmtTime(levelTimer) }}</span>
          </div>
        </div>
        <div class="flex items-center gap-1.5">
          <div :class="totalRemaining <= paidSlots ? 'text-emerald-400' : totalRemaining <= paidSlots * 1.2 ? 'text-amber-500' : 'text-gray-500'" class="text-[11px]">
            <span class="font-bold text-sm">{{ totalRemaining }}</span>/{{ config.totalPlayers }}&#47749;
          </div>
          <div v-if="myBounties.length > 0" class="text-amber-300 text-[11px] font-bold">&#128176;x{{ myBounties.length }}</div>
          <button @click="showMonitor = !showMonitor"
            :class="showMonitor ? 'bg-blue-500/20' : 'bg-transparent'"
            class="border border-blue-500/30 rounded px-2 py-0.5 text-blue-400 text-[10px] font-bold hover:bg-blue-500/10 transition">
            {{ showMonitor ? '&#9650; &#45803;&#44592;' : '&#9660; &#47784;&#45768;&#53552;' }}
          </button>
          <button @click="showCoach = !showCoach"
            :class="showCoach ? 'bg-amber-500/15' : 'bg-transparent'"
            class="border border-amber-500/20 rounded px-2 py-0.5 text-amber-400 text-[10px] hover:bg-amber-500/10 transition">
            &#128161;
          </button>
        </div>
      </div>
    </div>

    <!-- Monitor overlay -->
    <PokerMonitor :show="showMonitor" :blind-level="blindLevel" :bl="bl" :next-bl="nextBl"
      :level-timer="levelTimer" :total-remaining="totalRemaining" :total-players="config.totalPlayers"
      :paid-slots="paidSlots" :player-chips="playerSeat?.chips || 0" :my-rank="myRank"
      :my-bounties="myBounties" :prize-pool="prizePool" :elapsed-time="elapsedTime"
      :start-chips="config.startChips" @close="showMonitor = false" />

    <!-- Main area: Table (left) + Side panel (right) -->
    <div class="flex-1 min-h-0 flex">
      <!-- 테이블 (70%) -->
      <div class="flex-[7] min-h-0 pt-1">
        <PokerTable :seats="seats" :community="community" :pot="pot" :stage="stage"
          :dealer-idx="dealerIdx" :showdown="showdown" :hand-results="handResults"
          :game-over="gameOver" :bl="bl" :act-idx="actIdx" :chat-bubbles="chatBubbles"
          :current-bet-level="currentBetLevel" :blind-level="blindLevel" :total-remaining="totalRemaining"
          :paid-slots="paidSlots" :fold-reveals="foldReveals" :is-player-turn="isPlayerTurn" />
      </div>

      <!-- 사이드 패널 (30%) — 코칭 + 폴드 + 로그 -->
      <div class="flex-[3] min-w-[220px] max-w-[300px] bg-gray-950/80 border-l border-gray-800/50 flex flex-col overflow-hidden hidden lg:flex">
        <!-- 코칭 -->
        <div v-if="showCoach && coachTips && !gameOver" class="p-3 border-b border-gray-800/50">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-1.5">
              <span class="bg-blue-500/20 border border-blue-500/30 rounded px-1.5 py-0.5 text-blue-400 text-[10px] font-bold">{{ coachTips.posName }}</span>
              <span class="text-gray-400 text-[10px]">{{ coachTips.posFullName }}</span>
            </div>
            <span :class="coachTips.m <= 10 ? 'text-red-400' : 'text-gray-400'" class="text-[10px] font-mono">{{ coachTips.m }}BB</span>
          </div>
          <!-- 승률 바 -->
          <div class="mb-2">
            <div class="flex justify-between items-center mb-1">
              <span class="text-gray-400 text-[10px]">승률</span>
              <span :class="coachTips.equity >= 60 ? 'text-emerald-400' : coachTips.equity >= 40 ? 'text-amber-400' : 'text-red-400'" class="text-lg font-black">{{ coachTips.equity }}%</span>
            </div>
            <div class="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div :class="coachTips.equity >= 60 ? 'bg-emerald-500' : coachTips.equity >= 40 ? 'bg-amber-500' : 'bg-red-500'" class="h-full rounded-full transition-all" :style="{ width: coachTips.equity + '%' }" />
            </div>
          </div>
          <!-- 팟오즈 -->
          <div v-if="coachTips.toCall > 0" class="bg-black/30 rounded px-2 py-1 mb-2 text-[10px] text-gray-300">
            팟오즈: {{ coachTips.toCall }}/{{ coachTips.pot + coachTips.toCall }} = <span class="text-blue-400 font-bold">{{ coachTips.potOddsPct }}%</span>
          </div>
          <!-- 추천 -->
          <div class="rounded px-2 py-1.5" :style="{ background: coachTips.rec.color + '15', border: '1px solid ' + coachTips.rec.color + '30' }">
            <span :style="{ color: coachTips.rec.color }" class="text-sm font-black">→ {{ coachTips.rec.action }}</span>
            <div class="text-gray-400 text-[10px] mt-0.5 leading-tight">{{ coachTips.rec.reason }}</div>
          </div>
          <!-- 핸드 설명 -->
          <div v-if="coachTips.handDesc || coachTips.madeHand" class="text-gray-400 text-[9px] mt-1.5">
            {{ coachTips.madeHand ? '메이드: ' + coachTips.madeHand : coachTips.handDesc }}
          </div>
        </div>

        <!-- 폴드 카드 -->
        <div class="flex-1 overflow-y-auto p-3">
          <div v-if="foldReveals.length > 0" class="mb-2">
            <div class="text-amber-600 text-[10px] font-bold mb-1.5">🃏 폴드 카드</div>
            <div v-for="(fr, i) in foldReveals.slice(-5)" :key="i" class="flex items-start gap-2 mb-2">
              <span class="text-sm shrink-0">{{ fr.emoji }}</span>
              <div class="min-w-0">
                <div class="text-gray-300 text-[10px] font-bold">{{ fr.name }} <span class="text-gray-500">({{ fr.posLabel }})</span></div>
                <div class="text-amber-700 text-[9px] leading-tight">{{ fr.reason }}</div>
              </div>
            </div>
          </div>
          <!-- 로그 -->
          <div v-if="lastAction && !gameOver" class="text-gray-400 text-[10px]">{{ lastAction }}</div>
          <div v-if="bustMsg" class="text-red-400 text-[10px] mt-1">{{ bustMsg }}</div>
        </div>
      </div>
    </div>

    <!-- Bottom: 결과 + 액션 버튼 -->
    <div class="shrink-0">
      <div v-if="handResults && gameOver" class="text-center py-1">
        <span :class="handResults.winners[0]?.name === '\uB098' ? 'text-emerald-400' : 'text-red-400'" class="text-sm font-bold">{{ handResults.msg }}</span>
      </div>
      <PokerActions :is-player-turn="isPlayerTurn" :game-over="gameOver" :tourney-over="tourneyOver"
        :can-check="canCheck" :call-amt="callAmt" :current-bet-level="currentBetLevel"
        :player-chips="playerSeat?.chips || 0" :blind-b-b="bl.bb" :raise-amt="raiseAmt"
        @action="doPlayerAction" @update-raise="raiseAmt = $event" @next-hand="nextHand" />
    </div>
  </template>

  <!-- Loading -->
  <div v-else class="min-h-screen flex items-center justify-center">
    <div class="text-gray-500 text-sm">&#47196;&#46377; &#51473;...</div>
  </div>
</div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePokerGame } from '@/composables/usePokerGame'
import { usePokerWallet } from '@/composables/usePokerWallet'
import PokerTable from '@/components/poker/PokerTable.vue'
import PokerMonitor from '@/components/poker/PokerMonitor.vue'
import PokerActions from '@/components/poker/PokerActions.vue'
// PokerCoaching now inlined in bottom panel for compact layout

const router = useRouter()
const { saveGame } = usePokerWallet()

const {
  screen, config, blindLevel, totalRemaining, myRank, handNum, tourneyLog, myBounties, chatBubbles,
  seats, dealerIdx, community, pot, stage, actIdx, lastAction, isPlayerTurn, gameOver, showdown,
  raiseAmt, coachTips, showCoach, showMonitor, bustMsg, handResults, tourneyOver, finalPlace,
  currentBetLevel, levelTimer, elapsedTime, foldReveals, termTip,
  bl, nextBl, paidSlots, prizePool, prizes,
  startTournament, doPlayerAction, nextHand, resetTournament, cleanup,
  BLIND_SCHEDULE, fmtTime, fmtElapsed,
} = usePokerGame()

const playerSeat = computed(() => seats.value.find(s => s.isPlayer))
const canCheck = computed(() => currentBetLevel.value <= (playerSeat.value?.bet || 0))
const callAmt = computed(() => Math.max(0, currentBetLevel.value - (playerSeat.value?.bet || 0)))
const inMoney = computed(() => finalPlace.value <= paidSlots.value)

function calcPrize() {
  if (finalPlace.value > paidSlots.value) return 0
  const pool = prizePool.value
  if (finalPlace.value === 1) return Math.floor(pool * 0.25)
  if (finalPlace.value === 2) return Math.floor(pool * 0.16)
  if (finalPlace.value === 3) return Math.floor(pool * 0.11)
  if (finalPlace.value <= 6) return Math.floor(pool * 0.07)
  if (finalPlace.value <= 10) return Math.floor(pool * 0.04)
  return Math.floor(pool * 0.02)
}

function handleRestart() {
  resetTournament()
  const saved = sessionStorage.getItem('pokerConfig')
  if (saved) {
    try { Object.assign(config.value, JSON.parse(saved)) } catch (e) { /* use defaults */ }
  }
  startTournament()
}

function saveResult() {
  if (!tourneyOver.value) return
  const prize = calcPrize()
  const bountyTotal = myBounties.value.length * Math.floor(config.value.buyIn * 0.1)
  saveGame({
    buy_in: config.value.buyIn,
    total_players: config.value.totalPlayers,
    final_place: finalPlace.value,
    prize_won: prize,
    bounties: myBounties.value.length,
    bounty_earnings: bountyTotal,
    hands_played: handNum.value,
    elapsed_seconds: elapsedTime.value,
    blind_level: blindLevel.value,
  }).catch(() => {})
}

let tourneyWatcher = null

onMounted(() => {
  // Read config from sessionStorage (set by PokerLobby)
  const saved = sessionStorage.getItem('pokerConfig')
  if (saved) {
    try { Object.assign(config.value, JSON.parse(saved)) } catch (e) { /* use defaults */ }
  }
  startTournament()

  // Watch for tournament end to save results
  tourneyWatcher = setInterval(() => {
    if (tourneyOver.value) {
      saveResult()
      if (tourneyWatcher) { clearInterval(tourneyWatcher); tourneyWatcher = null }
    }
  }, 500)
})

onUnmounted(() => {
  cleanup()
  if (tourneyWatcher) { clearInterval(tourneyWatcher); tourneyWatcher = null }
})
</script>
