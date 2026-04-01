<template>
  <div :class="['detail-page-header', `bg-gradient-to-r ${gradientFrom} ${gradientTo}`]">
    <div class="max-w-[1200px] mx-auto px-4 py-5">
      <!-- Back + Category row -->
      <div class="flex items-center gap-2 mb-3">
        <button
          @click="handleBack"
          class="flex items-center gap-1 text-white/80 hover:text-white text-sm transition-colors"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
          </svg>
          {{ backLabel }}
        </button>
        <span v-if="category" class="bg-white/20 text-white text-xs px-2 py-0.5 rounded-full font-medium">
          {{ category }}
        </span>
        <span v-if="badge" :class="['text-xs px-2 py-0.5 rounded-full font-medium', badgeClass || 'bg-yellow-400 text-yellow-900']">
          {{ badge }}
        </span>
      </div>

      <!-- Title -->
      <h1 class="text-xl font-black text-white leading-snug mb-2">{{ title }}</h1>

      <!-- Meta info -->
      <div v-if="meta" class="flex items-center gap-3 text-white/70 text-sm flex-wrap">
        <span v-if="meta.author">{{ meta.author }}</span>
        <span v-if="meta.author && meta.date">·</span>
        <span v-if="meta.date">{{ meta.date }}</span>
        <span v-if="meta.views" class="flex items-center gap-1">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
          {{ meta.views }}
        </span>
        <span v-if="meta.extra">{{ meta.extra }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: { type: String, default: '' },
  backLabel: { type: String, default: '← 목록' },
  backTo: { type: String, default: null },
  category: { type: String, default: null },
  badge: { type: String, default: null },
  badgeClass: { type: String, default: null },
  meta: { type: Object, default: null },
  gradientFrom: { type: String, default: 'from-blue-600' },
  gradientTo: { type: String, default: 'to-blue-500' },
})

const router = useRouter()

function handleBack() {
  if (props.backTo) {
    router.push(props.backTo)
  } else {
    router.back()
  }
}
</script>

<style scoped>
.detail-page-header {
  margin-bottom: 24px;
  border-radius: 0;
}
@media (min-width: 640px) {
  .detail-page-header {
    border-radius: 12px;
    margin: 0 0 24px 0;
  }
}
</style>
