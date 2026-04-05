<template>
  <div class="flex items-center gap-2 text-sm">
    <span class="text-gray-500">📍</span>
    <select v-model="radius" @change="$emit('update:modelValue', Number(radius))"
      class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400 bg-white">
      <option :value="5">5mi</option>
      <option :value="10">10mi</option>
      <option :value="25">25mi</option>
      <option :value="50">50mi</option>
      <option :value="0">전국</option>
    </select>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 25 },
  defaultDistance: { type: Number, default: 25 }
})

defineEmits(['update:modelValue'])

const radius = ref(props.modelValue ?? props.defaultDistance)

watch(() => props.modelValue, (val) => {
  radius.value = val
})
</script>
