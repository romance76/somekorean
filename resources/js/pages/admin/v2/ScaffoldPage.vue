<template>
  <!-- 관리자 v2 범용 스캐폴드 플레이스홀더 (Phase 2-C) -->
  <div class="bg-white rounded-xl shadow-sm p-8">
    <div class="flex items-center gap-3 mb-4">
      <span class="text-3xl">{{ icon }}</span>
      <div>
        <h3 class="text-xl font-bold">{{ title }}</h3>
        <p class="text-xs text-gray-500">{{ description }}</p>
      </div>
    </div>
    <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm">
      <p class="font-semibold mb-2">📋 Phase 2-C 묶음 {{ bundle }}</p>
      <p class="mb-3">{{ note }}</p>
      <ul class="list-disc pl-5 space-y-1 text-xs text-gray-700">
        <li v-for="task in tasks" :key="task">{{ task }}</li>
      </ul>
      <div class="mt-4 pt-3 border-t border-amber-200">
        <router-link v-if="fallback" :to="fallback" class="inline-block px-3 py-1.5 bg-amber-400 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold">
          기존 페이지 → {{ fallback }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  bundle: { type: Number, default: 0 },
  icon: { type: String, default: '🚧' },
  title: { type: String, default: 'Scaffold' },
  description: { type: String, default: '' },
  note: { type: String, default: '이 페이지는 다음 세션에서 구현 예정입니다.' },
  tasks: { type: Array, default: () => [] },
  fallback: { type: String, default: null },
})
</script>
