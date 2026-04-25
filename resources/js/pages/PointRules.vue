<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <button @click="$router.back()" class="text-sm text-gray-500 hover:text-amber-600 mb-3">← 돌아가기</button>
    <h1 class="text-xl font-black text-gray-800 mb-1">📋 포인트 적립·사용 규칙</h1>
    <p class="text-xs text-gray-500 mb-4">관리자 설정과 실시간 동기화되는 공식 규칙입니다.</p>

    <div v-if="loading" class="text-center text-gray-400 py-12">로딩 중...</div>
    <div v-else class="space-y-4">
      <section v-for="section in visibleSections" :key="section.key"
        class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="px-4 py-3 border-b font-bold text-sm" :class="section.headerClass">
          {{ section.title }}
        </div>
        <div class="divide-y">
          <div v-for="rule in section.rules" :key="rule.key"
            class="px-4 py-2.5 flex items-start justify-between gap-3 text-sm">
            <div class="flex-1">
              <div class="text-gray-800">{{ rule.label || rule.key }}</div>
              <div v-if="rule.description" class="text-[11px] text-gray-400">{{ rule.description }}</div>
            </div>
            <span class="font-bold whitespace-nowrap" :class="section.valueClass">
              {{ formatValue(rule, section.key) }}
            </span>
          </div>
        </div>
      </section>

      <div v-if="!visibleSections.length" class="text-sm text-gray-400 text-center py-8">
        아직 등록된 규칙이 없습니다.
      </div>

      <p class="text-[11px] text-gray-400 mt-2 text-center">
        📌 관리자 설정이 변경되면 이 페이지도 즉시 반영됩니다.
      </p>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const loading = ref(true)
const grouped = ref({})

// 카테고리별 렌더링 메타
const SECTION_META = {
  earn:     { title: '💰 포인트 적립',       headerClass: 'bg-green-50 text-green-800',  valueClass: 'text-green-600',  prefix: '+' },
  spend:    { title: '🛒 포인트 사용',       headerClass: 'bg-red-50 text-red-800',      valueClass: 'text-red-500',    prefix: '-' },
  game:     { title: '🎮 게임 포인트',       headerClass: 'bg-amber-50 text-amber-800',  valueClass: 'text-amber-600',  prefix: ''  },
  market:   { title: '🛍️ 중고장터 규칙',    headerClass: 'bg-indigo-50 text-indigo-800', valueClass: 'text-indigo-600', prefix: ''  },
  image:    { title: '🖼️ 이미지 업로드',    headerClass: 'bg-sky-50 text-sky-800',      valueClass: 'text-sky-600',    prefix: ''  },
  auction:  { title: '🏷️ 옥션',             headerClass: 'bg-rose-50 text-rose-800',    valueClass: 'text-rose-600',   prefix: ''  },
}

const visibleSections = computed(() => {
  const order = ['earn', 'spend', 'game', 'market', 'image', 'auction']
  return order
    .filter(k => (grouped.value[k] || []).length)
    .map(k => ({
      key: k,
      ...SECTION_META[k],
      rules: grouped.value[k] || [],
    }))
})

function formatValue(rule, sectionKey) {
  const v = rule.value
  if (v == null || v === '') return '-'
  // 숫자면 포인트 표기, 아니면 그대로
  const meta = SECTION_META[sectionKey]
  const n = Number(v)
  if (!isNaN(n)) {
    // 가격(spend) 는 - 프리픽스, earn 은 +
    const prefix = meta?.prefix ?? ''
    return `${prefix}${n.toLocaleString()}P`
  }
  return v
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/point-rules')
    grouped.value = data.data || {}
  } catch {
    grouped.value = {}
  }
  loading.value = false
})
</script>
