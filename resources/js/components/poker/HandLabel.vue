<template>
  <div
    v-if="name && name !== '-'"
    class="rounded inline-block px-2 py-0.5"
    :class="isWinner ? 'border' : 'border border-transparent'"
    :style="{
      background: `linear-gradient(135deg, ${handColor}dd, ${handColor}88)`,
      borderColor: isWinner ? handColor : 'transparent',
      boxShadow: isWinner ? `0 0 12px ${handColor}88` : 'none'
    }"
  >
    <span class="text-white text-[10px] font-extrabold tracking-wider drop-shadow-md uppercase">
      {{ isWinner ? '🏆 WINNER · ' : '' }}{{ name }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
  isWinner: { type: Boolean, default: false }
})

const HAND_COLORS = {
  '로열 플러시': '#ffd700',
  '스트레이트 플러시': '#ff6b35',
  '포카드': '#e040fb',
  '풀하우스': '#ff9800',
  '플러시': '#29b6f6',
  '스트레이트': '#66bb6a',
  '트리플': '#42a5f5',
  '투페어': '#ab47bc',
  '원페어': '#78909c',
  '하이카드': '#607d8b'
}

const handColor = computed(() => HAND_COLORS[props.name] || '#90a4ae')
</script>
