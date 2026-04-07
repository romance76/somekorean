<template>
  <div v-if="amount && amount > 0" class="flex items-center gap-[3px]">
    <div class="relative" :style="{ width: '20px', height: Math.min(chipCount * 5 + 4, 34) + 'px' }">
      <div
        v-for="i in chipCount"
        :key="i"
        class="absolute left-0 w-5 h-[6px] rounded-full border border-white/30 shadow-sm"
        :style="{
          bottom: (i - 1) * 4 + 'px',
          background: chipGradient
        }"
      />
    </div>
    <span class="text-white text-[10px] font-bold drop-shadow-lg font-mono">
      {{ label }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  amount: { type: Number, default: 0 },
  bb: { type: Number, default: 20 }
})

const label = computed(() => {
  if (props.amount >= 10000) return Math.round(props.amount / 1000) + 'K'
  if (props.amount >= 1000) return Math.round(props.amount / 1000) + 'K'
  return props.amount.toString()
})

const chipCount = computed(() => Math.min(Math.ceil(props.amount / props.bb), 6))

const chipGradient = computed(() => {
  if (props.amount >= props.bb * 20) return 'linear-gradient(180deg, #e74c3c, #c0392b)'
  if (props.amount >= props.bb * 5) return 'linear-gradient(180deg, #27ae60, #1e8449)'
  return 'linear-gradient(180deg, #2980b9, #1f6dad)'
})
</script>
