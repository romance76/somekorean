<template>
  <!-- Heart -->
  <svg v-if="suit === '♥'" :width="size" :height="size" viewBox="0 0 100 100">
    <path d="M50 88 C25 65,0 45,0 28 A25 25 0 0 1 50 20 A25 25 0 0 1 100 28 C100 45,75 65,50 88Z" :fill="color" />
  </svg>

  <!-- Diamond -->
  <svg v-else-if="suit === '♦'" :width="Math.round(size * 1.15)" :height="Math.round(size * 1.15)" viewBox="0 0 100 100">
    <path d="M50 2 Q78 30,96 50 Q78 70,50 98 Q22 70,4 50 Q22 30,50 2Z" :fill="color" />
  </svg>

  <!-- Club -->
  <svg v-else-if="suit === '♣'" :width="size" :height="size" viewBox="0 0 100 100">
    <circle cx="50" cy="30" r="22" :fill="color" />
    <circle cx="28" cy="58" r="22" :fill="color" />
    <circle cx="72" cy="58" r="22" :fill="color" />
    <rect x="45" y="55" width="10" height="30" :fill="color" />
  </svg>

  <!-- Spade (default) -->
  <svg v-else :width="size" :height="size" viewBox="0 0 100 100">
    <path d="M50 5 C50 5,0 45,0 62 A25 25 0 0 0 42 80 L38 95 62 95 58 80 A25 25 0 0 0 100 62 C100 45,50 5,50 5Z" :fill="color" />
  </svg>
</template>

<script setup>
defineProps({
  suit: { type: String, required: true },
  size: { type: Number, default: 24 },
  color: { type: String, default: '#1a1a2e' }
})
</script>
