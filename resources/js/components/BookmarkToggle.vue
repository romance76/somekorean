<template>
  <button @click.stop.prevent="$emit('toggle')" class="transition hover:scale-110" :title="active ? '북마크 해제' : '북마크'">
    <svg viewBox="0 0 24 24" :class="[sizeClass, active ? 'fill-red-500 text-red-500' : 'fill-none text-gray-300 hover:text-red-400']"
      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M19 21l-7-4-7 4V5a2 2 0 012-2h10a2 2 0 012 2z"/>
    </svg>
  </button>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({
  active: { type: Boolean, default: false },
  size: { type: String, default: 'md' }, // sm, md, lg
})
defineEmits(['toggle'])
const sizeClass = computed(() => ({ sm: 'w-4 h-4', md: 'w-5 h-5', lg: 'w-6 h-6' }[props.size] || 'w-5 h-5'))
</script>
<script>
export default { name: 'BookmarkToggle' }
</script>
