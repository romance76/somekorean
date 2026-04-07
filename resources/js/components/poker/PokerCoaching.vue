<template>
  <div
    v-if="hasFoldReveals || hasCoaching"
    class="flex gap-1.5 px-2.5 py-1 shrink-0"
  >
    <!-- LEFT: Fold reveals -->
    <div
      v-if="hasFoldReveals"
      class="rounded-lg px-2 py-[5px] min-w-0 border"
      :class="hasFoldReveals && hasCoaching ? 'flex-[0_0_40%]' : 'flex-1'"
      style="background: rgba(40,30,15,0.4); border-color: rgba(200,150,50,0.15)"
    >
      <div class="text-amber-600 text-[9px] font-bold tracking-wider mb-[3px]">
        🃏 폴드 카드
      </div>
      <div
        v-for="(fr, i) in recentFolds"
        :key="i"
        class="flex items-center gap-[5px] mb-[3px]"
      >
        <span class="text-[11px] shrink-0">{{ fr.emoji }}</span>
        <div class="flex gap-[1px] shrink-0">
          <PokerCard
            v-for="(c, j) in fr.cards"
            :key="j"
            :card="c"
            tiny
          />
        </div>
        <div class="min-w-0 overflow-hidden">
          <div class="text-gray-400 text-[9px] font-semibold whitespace-nowrap overflow-hidden text-ellipsis">
            {{ fr.name }} ({{ fr.posLabel }})
          </div>
          <div class="text-amber-700 text-[8px] leading-tight line-clamp-2">
            {{ fr.reason }}
          </div>
        </div>
      </div>
    </div>

    <!-- RIGHT: Smart Coaching -->
    <div
      v-if="hasCoaching"
      class="flex-1 rounded-lg px-2.5 py-1.5 min-w-0 border"
      style="background: rgba(15,25,40,0.6); border-color: rgba(93,173,226,0.15)"
    >
      <!-- Row 1: Position + Stack -->
      <div class="flex justify-between items-center mb-1">
        <div class="flex items-center gap-1">
          <span class="bg-blue-400/20 border border-blue-400/30 rounded px-1.5 py-[1px] text-blue-400 text-[10px] font-bold">
            {{ coachTips.posName }}
          </span>
          <span class="text-gray-400 text-[9px]">{{ coachTips.posFullName }}</span>
        </div>
        <div
          class="text-[9px] font-semibold"
          :class="{
            'text-red-500': coachTips.m <= 10,
            'text-amber-500': coachTips.m > 10 && coachTips.m <= 20,
            'text-gray-400': coachTips.m > 20
          }"
        >
          {{ coachTips.m }}BB
        </div>
      </div>

      <!-- Row 2: Equity bar + percentage -->
      <div class="mb-1">
        <div class="flex justify-between items-center mb-0.5">
          <span class="text-gray-400 text-[9px]">승률</span>
          <span
            class="text-sm font-extrabold"
            :class="{
              'text-green-500': coachTips.equity >= 60,
              'text-amber-500': coachTips.equity >= 40 && coachTips.equity < 60,
              'text-red-500': coachTips.equity < 40
            }"
          >
            {{ coachTips.equity }}%
          </span>
        </div>
        <div class="w-full h-1.5 bg-white/[0.08] rounded overflow-hidden">
          <div
            class="h-full rounded transition-[width] duration-500"
            :style="{
              width: coachTips.equity + '%',
              background: equityGradient
            }"
          />
        </div>
      </div>

      <!-- Row 3: Pot odds (if facing bet) -->
      <div
        v-if="coachTips.toCall > 0"
        class="flex justify-between items-center mb-[3px] bg-black/20 rounded px-1.5 py-0.5"
      >
        <span class="text-gray-400 text-[9px]">팟오즈</span>
        <span class="text-gray-300 text-[9px]">
          {{ coachTips.toCall }} 콜 / {{ coachTips.pot + coachTips.toCall }} 팟 =
          <span class="text-blue-400 font-bold">{{ coachTips.potOddsPct }}%</span> 필요
        </span>
      </div>

      <!-- Row 4: Recommendation -->
      <div
        class="flex items-center gap-1.5 rounded-md px-2 py-1"
        :style="{
          background: coachTips.rec.color + '15',
          border: '1px solid ' + coachTips.rec.color + '30'
        }"
      >
        <span
          class="text-xs font-extrabold shrink-0"
          :style="{ color: coachTips.rec.color }"
        >
          → {{ coachTips.rec.action }}
        </span>
        <span class="text-gray-400 text-[9px] leading-tight">
          {{ coachTips.rec.reason }}
        </span>
      </div>

      <!-- Row 5: Hand description -->
      <div
        v-if="coachTips.handDesc || coachTips.madeHand"
        class="text-gray-500 text-[8px] mt-[3px]"
      >
        {{ coachTips.madeHand ? `메이드: ${coachTips.madeHand}` : coachTips.handDesc }}
        {{ situationLabel }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import PokerCard from './PokerCard.vue'

const props = defineProps({
  coachTips: { type: Object, default: null },
  foldReveals: { type: Array, default: () => [] },
  showCoach: { type: Boolean, default: true },
  gameOver: { type: Boolean, default: false }
})

const hasFoldReveals = computed(() => props.foldReveals.length > 0)
const hasCoaching = computed(() => props.showCoach && props.coachTips && !props.gameOver)

// Show last 3 fold reveals
const recentFolds = computed(() => props.foldReveals.slice(-3))

const equityGradient = computed(() => {
  if (!props.coachTips) return 'linear-gradient(90deg, #ef4444, #dc2626)'
  if (props.coachTips.equity >= 60) return 'linear-gradient(90deg, #22c55e, #16a34a)'
  if (props.coachTips.equity >= 40) return 'linear-gradient(90deg, #f59e0b, #d97706)'
  return 'linear-gradient(90deg, #ef4444, #dc2626)'
})

const situationLabel = computed(() => {
  if (!props.coachTips) return ''
  if (props.coachTips.situation === 'bubble') return '| 🫧 버블 근처!'
  if (props.coachTips.situation === 'itm') return '| 💰 인더머니'
  return ''
})
</script>
