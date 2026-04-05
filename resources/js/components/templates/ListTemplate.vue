<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <!-- BoardBanner -->
      <BoardBanner v-bind="bannerProps" @register="$emit('register')" />

      <!-- 필터 바 슬롯 -->
      <div v-if="$slots['filter-bar']" class="mt-3">
        <slot name="filter-bar" />
      </div>

      <!-- 거리 필터 -->
      <div v-if="showDistanceFilter" class="mt-2 flex items-center gap-2">
        <DistanceFilter :modelValue="distance" @update:modelValue="onDistanceChange" :defaultDistance="defaultDistance" />
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="text-center py-16 text-gray-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
        <p>불러오는 중...</p>
      </div>

      <!-- 컨텐츠 영역 -->
      <template v-else>
        <!-- 2컬럼 레이아웃: 메인 + 사이드바 -->
        <div class="flex gap-5 items-start mt-4">
          <!-- 메인 -->
          <div class="flex-1 min-w-0">
            <!-- 아이템이 있을 때 -->
            <div v-if="items && items.length" class="space-y-3">
              <div v-for="(item, idx) in items" :key="item.id || idx">
                <slot name="item-card" :item="item" :index="idx" />
              </div>
            </div>

            <!-- 빈 상태 -->
            <div v-else>
              <slot name="empty">
                <div class="text-center py-16">
                  <p class="text-4xl mb-3">📭</p>
                  <p class="text-gray-400">데이터가 없습니다</p>
                </div>
              </slot>
            </div>

            <!-- 페이지네이션 -->
            <div v-if="pagination && pagination.last_page > 1" class="flex justify-center mt-6">
              <nav class="flex items-center gap-1">
                <button @click="goPage(pagination.current_page - 1)" :disabled="pagination.current_page <= 1"
                  class="px-3 py-1.5 rounded-lg text-sm border border-gray-200 text-gray-600 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed">
                  이전
                </button>
                <template v-for="p in visiblePages" :key="p">
                  <button v-if="p === '...'" disabled class="px-2 py-1.5 text-sm text-gray-400">...</button>
                  <button v-else @click="goPage(p)"
                    :class="['px-3 py-1.5 rounded-lg text-sm border transition',
                      p === pagination.current_page ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-200 text-gray-600 hover:bg-gray-100']">
                    {{ p }}
                  </button>
                </template>
                <button @click="goPage(pagination.current_page + 1)" :disabled="pagination.current_page >= pagination.last_page"
                  class="px-3 py-1.5 rounded-lg text-sm border border-gray-200 text-gray-600 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed">
                  다음
                </button>
              </nav>
            </div>
          </div>

          <!-- 사이드바 (데스크탑 전용) -->
          <div v-if="$slots.sidebar" class="hidden lg:block flex-shrink-0 sticky top-4" style="width:320px">
            <slot name="sidebar" />
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import BoardBanner from '../board/BoardBanner.vue'
import DistanceFilter from '../DistanceFilter.vue'

const props = defineProps({
  // BoardBanner props
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  emoji: { type: String, default: '' },
  registerLabel: { type: String, default: null },
  count: { type: Number, default: null },
  locationDisplay: { type: String, default: '' },
  theme: { type: String, default: 'blue' },
  // 목록 데이터
  loading: { type: Boolean, default: false },
  items: { type: Array, default: () => [] },
  // 페이지네이션
  pagination: {
    type: Object,
    default: null
    // { current_page, last_page, total }
  },
  // 거리 필터
  showDistanceFilter: { type: Boolean, default: true },
  defaultDistance: { type: Number, default: 25 }
})

const emit = defineEmits(['register', 'page-change', 'distance-change'])

const distance = ref(props.defaultDistance)

// BoardBanner에 전달할 props
const bannerProps = computed(() => ({
  title: props.title,
  subtitle: props.subtitle,
  emoji: props.emoji,
  registerLabel: props.registerLabel,
  count: props.count,
  locationDisplay: props.locationDisplay,
  theme: props.theme
}))

// 보여줄 페이지 번호 계산 (최대 7개)
const visiblePages = computed(() => {
  if (!props.pagination) return []
  const { current_page, last_page } = props.pagination
  if (last_page <= 7) {
    return Array.from({ length: last_page }, (_, i) => i + 1)
  }
  const pages = []
  if (current_page <= 4) {
    for (let i = 1; i <= 5; i++) pages.push(i)
    pages.push('...', last_page)
  } else if (current_page >= last_page - 3) {
    pages.push(1, '...')
    for (let i = last_page - 4; i <= last_page; i++) pages.push(i)
  } else {
    pages.push(1, '...')
    for (let i = current_page - 1; i <= current_page + 1; i++) pages.push(i)
    pages.push('...', last_page)
  }
  return pages
})

function goPage(page) {
  if (page < 1 || page > props.pagination.last_page) return
  emit('page-change', page)
}

function onDistanceChange(val) {
  distance.value = val
  emit('distance-change', val)
}
</script>
