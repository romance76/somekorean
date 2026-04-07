<template>
  <div
    v-if="show"
    class="fixed top-11 right-2 w-[260px] z-50 rounded-xl overflow-hidden border border-blue-400/25 shadow-[0_8px_32px_rgba(0,0,0,0.5)]"
    style="background: rgba(8,20,40,0.88); backdrop-filter: blur(12px)"
  >
    <!-- Header -->
    <div
      class="flex justify-between items-center px-2.5 py-1.5 border-b border-blue-400/15"
      style="background: rgba(26,58,106,0.5)"
    >
      <span class="text-blue-400 text-[10px] font-bold tracking-wider">🏆 TOURNAMENT</span>
      <button
        class="bg-transparent border-none text-blue-400 cursor-pointer text-xs p-0"
        @click="$emit('close')"
      >
        ✕
      </button>
    </div>

    <!-- Timer -->
    <div class="text-center pt-2 pb-1">
      <div class="text-gray-500 text-[8px] tracking-[2px]">
        LEVEL {{ blindLevel + 1 }} · {{ bl.sb }}/{{ bl.bb }}{{ bl.ante > 0 ? ` (A${bl.ante})` : '' }}
      </div>
      <div
        class="text-4xl font-extrabold font-mono leading-none"
        :class="levelTimer <= 60 ? 'text-red-500' : 'text-emerald-500'"
        :style="levelTimer <= 60 ? 'text-shadow: 0 0 12px rgba(231,76,60,0.3)' : ''"
      >
        {{ formattedTimer }}
      </div>
      <!-- Progress bar -->
      <div class="w-4/5 h-[3px] bg-white/[0.06] rounded-sm mx-auto mt-1 overflow-hidden">
        <div
          class="h-full rounded-sm transition-[width] duration-1000"
          :class="levelTimer <= 60 ? 'bg-red-500' : ''"
          :style="{
            width: timerPercent + '%',
            background: levelTimer > 60 ? 'linear-gradient(90deg, #2ecc71, #5dade2)' : undefined
          }"
        />
      </div>
      <div class="text-gray-600 text-[8px] mt-0.5">
        NEXT: {{ nextBl.sb }}/{{ nextBl.bb }} · 경과 {{ formattedElapsed }}
      </div>
    </div>

    <!-- Stats -->
    <div class="px-2.5 pt-1 pb-1.5">
      <div
        v-for="(stat, i) in statsRows"
        :key="i"
        class="flex justify-between py-0.5 border-b border-white/[0.03]"
      >
        <span class="text-gray-600 text-[8px] tracking-[0.5px]">{{ stat.label }}</span>
        <span
          class="text-[11px] font-bold font-mono"
          :style="{ color: stat.color }"
        >
          {{ stat.value }}
        </span>
      </div>
    </div>

    <!-- Prize -->
    <div class="px-2.5 pt-[3px] pb-1.5 border-t border-white/[0.04]">
      <div class="flex justify-between">
        <span class="text-gray-600 text-[8px]">PRIZE POOL</span>
        <span class="text-amber-400 text-[10px] font-bold">${{ prizePool.toLocaleString() }}</span>
      </div>
      <div class="flex justify-between">
        <span class="text-gray-600 text-[8px]">1st / 입상</span>
        <span class="text-gray-400 text-[9px]">${{ Math.floor(prizePool * 0.25).toLocaleString() }} / {{ paidSlots }}명</span>
      </div>
    </div>

    <!-- Bubble/ITM alert -->
    <div
      v-if="totalRemaining <= paidSlots * 1.2 && totalRemaining > paidSlots"
      class="text-center py-1 px-2.5"
      style="background: rgba(243,156,18,0.15)"
    >
      <span class="text-amber-500 text-[9px] font-bold">
        🫧 BUBBLE -- {{ totalRemaining - paidSlots }}명 남음
      </span>
    </div>
    <div
      v-else-if="totalRemaining <= paidSlots"
      class="text-center py-1 px-2.5"
      style="background: rgba(46,204,113,0.1)"
    >
      <span class="text-emerald-500 text-[9px] font-bold">💰 IN THE MONEY</span>
    </div>

    <!-- Blind schedule mini -->
    <div class="px-2 pt-1 pb-1.5 border-t border-white/[0.04] flex gap-[3px] flex-wrap">
      <span
        v-for="(b, i) in blindScheduleSlice"
        :key="i"
        class="text-[7px] rounded-sm px-[3px] py-[1px]"
        :class="{
          'text-blue-400 bg-blue-400/15': i === blindLevel,
          'text-gray-800': i < blindLevel && i !== blindLevel,
          'text-gray-600': i > blindLevel
        }"
      >
        {{ i + 1 }}:{{ b.sb }}/{{ b.bb }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { fmtTime, fmtElapsed } from '@/composables/useBlindSchedule'

const BLIND_SCHEDULE = [
  { sb: 10, bb: 20, ante: 0, dur: 15 }, { sb: 15, bb: 30, ante: 0, dur: 15 },
  { sb: 25, bb: 50, ante: 5, dur: 15 }, { sb: 50, bb: 100, ante: 10, dur: 15 },
  { sb: 75, bb: 150, ante: 15, dur: 12 }, { sb: 100, bb: 200, ante: 25, dur: 12 },
  { sb: 150, bb: 300, ante: 25, dur: 12 }, { sb: 200, bb: 400, ante: 50, dur: 10 },
  { sb: 300, bb: 600, ante: 75, dur: 10 }, { sb: 400, bb: 800, ante: 100, dur: 10 }
]

const props = defineProps({
  show: { type: Boolean, default: false },
  blindLevel: { type: Number, default: 0 },
  bl: { type: Object, required: true },
  nextBl: { type: Object, required: true },
  levelTimer: { type: Number, default: 0 },
  totalRemaining: { type: Number, default: 0 },
  totalPlayers: { type: Number, default: 90 },
  paidSlots: { type: Number, default: 13 },
  playerChips: { type: Number, default: 0 },
  myRank: { type: Number, default: 1 },
  myBounties: { type: Array, default: () => [] },
  prizePool: { type: Number, default: 0 },
  elapsedTime: { type: Number, default: 0 },
  startChips: { type: Number, default: 15000 },
  buyIn: { type: Number, default: 400 }
})

defineEmits(['close'])

const formattedTimer = computed(() => fmtTime(props.levelTimer))
const formattedElapsed = computed(() => fmtElapsed(props.elapsedTime))

const timerPercent = computed(() => {
  const totalDur = props.bl.dur * 60
  return totalDur > 0 ? (props.levelTimer / totalDur) * 100 : 0
})

const blindScheduleSlice = computed(() => BLIND_SCHEDULE.slice(0, 10))

const avgStack = computed(() => {
  return Math.floor(
    (props.startChips * props.totalPlayers) / Math.max(1, props.totalRemaining)
  )
})

const bountyAmount = computed(() => Math.floor(props.buyIn * 0.1))

const statsRows = computed(() => [
  {
    label: 'REMAINING',
    value: `${props.totalRemaining}/${props.totalPlayers}`,
    color: props.totalRemaining <= props.paidSlots ? '#2ecc71' : '#5dade2'
  },
  {
    label: 'AVG STACK',
    value: avgStack.value.toLocaleString(),
    color: '#e8b730'
  },
  {
    label: 'MY STACK',
    value: props.playerChips.toLocaleString(),
    color: props.playerChips < props.bl.bb * 10 ? '#e74c3c' : '#fff'
  },
  {
    label: 'MY RANK',
    value: `~${props.myRank}위`,
    color: props.myRank <= props.paidSlots ? '#2ecc71' : '#aaa'
  },
  {
    label: 'BOUNTIES',
    value: props.myBounties.length > 0
      ? `${props.myBounties.length} ($${props.myBounties.length * bountyAmount.value})`
      : '0',
    color: props.myBounties.length > 0 ? '#ffd700' : '#556b7f'
  }
])
</script>
