<template>
<div class="h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-purple-800 text-white overflow-hidden flex flex-col">
  <!-- 상단 바 -->
  <div class="bg-black/50 backdrop-blur-md border-b border-white/10 px-4 py-2 flex items-center justify-between shrink-0">
    <div>
      <div class="text-[10px] opacity-60">JACKPOT</div>
      <div class="text-amber-300 font-black text-lg tracking-wide">{{ jackpot }}</div>
    </div>
    <div class="flex gap-2">
      <button class="bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded text-xs">카드 확대</button>
      <button @click="$router.push('/poker7')" class="bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded text-xs">방 이동</button>
      <button @click="leave" class="bg-red-500/80 hover:bg-red-600 px-3 py-1.5 rounded text-xs">나가기</button>
    </div>
  </div>

  <!-- 메인 테이블 (2-1-2 레이아웃) -->
  <div class="flex-1 relative p-4">
    <!-- 상단 중앙 좌석 (seat 4 = 맞은편) -->
    <div class="absolute top-4 left-1/2 -translate-x-1/2">
      <PlayerSeat :seat="seatByNumber(4)" position="top" />
    </div>

    <!-- 왼쪽 상단 (seat 3) -->
    <div class="absolute top-16 left-6">
      <PlayerSeat :seat="seatByNumber(3)" position="left-top" />
    </div>

    <!-- 왼쪽 하단 (seat 2) -->
    <div class="absolute bottom-40 left-6">
      <PlayerSeat :seat="seatByNumber(2)" position="left-bottom" />
    </div>

    <!-- 오른쪽 상단 (seat 5) -->
    <div class="absolute top-16 right-6">
      <PlayerSeat :seat="seatByNumber(5)" position="right-top" />
    </div>

    <!-- 오른쪽 하단 (seat 6) -->
    <div class="absolute bottom-40 right-6">
      <PlayerSeat :seat="seatByNumber(6)" position="right-bottom" />
    </div>

    <!-- 중앙 Pot -->
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
      <div class="bg-black/40 backdrop-blur-sm rounded-xl px-6 py-3 border border-amber-500/30">
        <div class="text-[10px] text-amber-300">POT</div>
        <div class="text-2xl font-black text-amber-400">{{ formatGm(state?.game?.pot) }}</div>
        <div class="text-xs opacity-60 mt-1">
          Call: {{ formatGm(state?.game?.current_bet) }}
        </div>
        <div v-if="state?.game?.current_round" class="text-[10px] opacity-70 mt-1">라운드 {{ state.game.current_round }}/4</div>
      </div>
    </div>

    <!-- 족보 팝업 토글 -->
    <button @click="showRanking=!showRanking" class="absolute top-20 right-48 bg-white/10 hover:bg-white/20 px-2 py-1 rounded text-xs">
      족보
    </button>
    <div v-if="showRanking" class="absolute top-32 right-48 bg-black/70 backdrop-blur-md border border-amber-500/30 rounded-lg p-3 text-xs w-48 z-10">
      <div class="font-bold text-amber-300 mb-2 flex justify-between">
        족보 <button @click="showRanking=false" class="opacity-60">✕</button>
      </div>
      <div class="space-y-0.5">
        <div v-for="(r, i) in rankings" :key="i" class="flex justify-between"><span class="opacity-70">{{ i+1 }}</span><span>{{ r }}</span></div>
      </div>
    </div>

    <!-- 본인 좌석 (하단 중앙 seat 1 또는 mySeat) -->
    <div class="absolute bottom-4 left-1/2 -translate-x-1/2">
      <PlayerSeat :seat="myActualSeat" position="self" />
    </div>

    <!-- 감정표현 -->
    <button class="absolute bottom-8 left-6 bg-white/10 hover:bg-white/20 rounded-full px-3 py-2 text-xs">
      💬 감정표현
    </button>
  </div>

  <!-- 하단 액션 바 -->
  <div class="bg-black/50 backdrop-blur-md border-t border-white/10 px-4 py-3 shrink-0">
    <div v-if="canStart" class="flex justify-center">
      <button @click="startGame" :disabled="busy"
        class="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 font-black px-8 py-3 rounded-lg text-lg disabled:opacity-50">
        {{ busy ? '시작중...' : '🎲 게임 시작' }}
      </button>
    </div>
    <div v-else-if="isMyTurn" class="grid grid-cols-6 gap-2">
      <button v-for="act in actions" :key="act.key" @click="action(act.key)"
        class="bg-gradient-to-b from-amber-500 to-amber-600 hover:from-amber-400 font-black py-3 rounded-lg text-sm">
        {{ act.label }}
      </button>
    </div>
    <div v-else class="text-center text-sm opacity-60">
      {{ state?.game ? '상대방 턴을 기다리는 중...' : '게임 시작 대기' }}
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const roomId = route.params.id
const state = ref(null)
const busy = ref(false)
const showRanking = ref(false)

const jackpot = '534,596,900,300,000'
const rankings = ['로티플','스티플','포카드','풀하우스','플러시','마운틴','백스트레이트','스트레이트','트리플','투페어','원페어','탑']
const actions = [
  { key: 'fold',    label: '다이' },
  { key: 'bbing',   label: '뻥' },
  { key: 'ttadang', label: '따당' },
  { key: 'check',   label: '체크' },
  { key: 'quarter', label: '쿼터' },
  { key: 'half',    label: '하프' },
]

const canStart = computed(() => {
  if (!state.value) return false
  if (state.value.game) return false
  if (state.value.room?.host_id !== (window.__userId || currentUserId.value)) return false
  return (state.value.seats?.length || 0) >= 2
})

const currentUserId = ref(null)
const myActualSeat = computed(() => state.value?.seats?.find(s => s.is_self))
const isMyTurn = computed(() =>
  state.value?.game && myActualSeat.value?.seat_number === state.value.game.current_turn_seat
)

function seatByNumber(n) {
  return state.value?.seats?.find(s => s.seat_number === n) || null
}

function formatGm(n) {
  n = Number(n || 0)
  if (n >= 100000000) return (n / 100000000).toFixed(1) + '억'
  if (n >= 10000) return Math.round(n / 10000).toLocaleString() + '만'
  return n.toLocaleString()
}

let timer = null
async function loadState() {
  try {
    const { data } = await axios.get(`/api/poker7/rooms/${roomId}/state`)
    state.value = data.data
    if (!currentUserId.value) {
      const s = state.value.seats?.find(x => x.is_self)
      if (s) currentUserId.value = s.user.id
    }
  } catch (e) {
    if (e.response?.status === 404) router.push('/poker7')
  }
}

async function startGame() {
  busy.value = true
  try { await axios.post(`/api/poker7/rooms/${roomId}/start`); await loadState() }
  catch (e) { alert(e.response?.data?.message || '시작 실패') }
  busy.value = false
}

async function leave() {
  if (!confirm('방을 나가시겠습니까? 남은 칩은 게임머니로 반환됩니다')) return
  try {
    await axios.post(`/api/poker7/rooms/${roomId}/leave`)
    router.push('/poker7')
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

function action(key) {
  alert(`'${key}' 액션은 다음 단계에서 구현 예정입니다`)
}

// 인라인 PlayerSeat 렌더러
const PlayerSeat = {
  props: { seat: Object, position: String },
  setup(p) {
    return () => {
      if (!p.seat) {
        return h('div', { class: 'w-28 h-24 rounded-lg bg-white/5 border border-dashed border-white/20 flex items-center justify-center text-[10px] opacity-50' }, '빈 자리')
      }
      const s = p.seat
      const isSelf = p.position === 'self'
      return h('div', { class: `flex gap-2 items-center ${isSelf ? 'flex-row' : 'flex-col'}` }, [
        // 아바타 박스
        h('div', { class: 'flex flex-col items-center' }, [
          h('div', { class: `relative ${isSelf ? 'w-16 h-16' : 'w-14 h-14'} rounded-full bg-gradient-to-br from-amber-400 to-orange-600 border-2 ${s.state==='folded' ? 'border-gray-600 opacity-50' : 'border-amber-300'} flex items-center justify-center font-bold text-white` }, [
            (s.user?.name || '?')[0]?.toUpperCase(),
            s.state === 'folded' ? h('div', { class: 'absolute inset-0 bg-black/60 rounded-full flex items-center justify-center text-[10px]' }, 'DIE') : null,
          ]),
          h('div', { class: 'text-[10px] mt-1 font-semibold' }, s.user?.name),
          h('div', { class: 'text-[10px] text-amber-300 font-bold' }, formatGm(s.stack)),
        ]),
        // 카드 영역
        h('div', { class: 'flex gap-0.5' }, (s.cards || []).map(c =>
          h('div', {
            class: `w-6 h-9 rounded ${c ? 'bg-white text-gray-900' : 'bg-gradient-to-br from-blue-700 to-blue-900'} border border-white/30 text-[9px] font-bold flex items-center justify-center`,
          }, c ? `${c.r}${cardSuit(c.s)}` : '')
        )),
        // 베팅 칩
        s.current_bet ? h('div', { class: 'text-[10px] bg-amber-500/80 text-amber-900 rounded-full px-2 py-0.5 font-bold' }, formatGm(s.current_bet)) : null,
      ])
    }
  }
}

function cardSuit(s) {
  return { S: '♠', H: '♥', D: '♦', C: '♣' }[s] || ''
}

onMounted(() => {
  loadState()
  timer = setInterval(loadState, 3000) // 폴링 (차후 WebSocket 전환)
})
onUnmounted(() => clearInterval(timer))
</script>
