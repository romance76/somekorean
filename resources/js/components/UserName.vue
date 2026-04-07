<template>
<button @click.stop="openPopup" class="hover:text-amber-700 hover:underline transition cursor-pointer" :class="className || 'text-gray-600'">
  <slot>{{ name }}</slot>
</button>
</template>
<script setup>
const props = defineProps({ userId: [Number, String], name: String, className: String })
function openPopup() {
  if (window.openUserPopup && props.userId) window.openUserPopup(props.userId)
}
</script>
