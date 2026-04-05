<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">

      <!-- Page Header -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4 mb-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-lg font-bold text-gray-800 dark:text-white flex items-center gap-2">
              <span v-if="emoji" class="text-xl">{{ emoji }}</span>
              {{ title }}
              <span v-if="totalCount !== null" class="text-sm font-normal text-gray-400">({{ totalCount.toLocaleString() }})</span>
            </h1>
            <p v-if="subtitle" class="text-sm text-gray-500 mt-0.5">{{ subtitle }}</p>
          </div>
          <slot name="header-right" />
        </div>

        <!-- Category Tabs -->
        <div v-if="categories && categories.length" class="flex gap-1 mt-3 overflow-x-auto scrollbar-hide">
          <button v-for="cat in categories" :key="cat.value"
            @click="$emit('category-change', cat.value)"
            class="px-3 py-1.5 text-xs font-medium rounded-full whitespace-nowrap transition"
            :class="activeCategory === cat.value
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'">
            {{ cat.label }}
          </button>
        </div>
      </div>

      <!-- Toolbar: Search + Sort + View Toggle + Distance -->
      <div class="flex flex-wrap items-center gap-2 mb-4">
        <!-- Search within list -->
        <div v-if="hasSearch" class="flex-1 min-w-[200px]">
          <div class="relative">
            <input :value="searchQuery" @input="$emit('search', $event.target.value)"
              type="text" :placeholder="searchPlaceholder || '\uAC80\uC0C9...'"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-800 dark:text-white rounded-lg px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
            <svg class="w-4 h-4 absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </div>
        </div>

        <!-- Sort options -->
        <div v-if="sortOptions && sortOptions.length" class="flex gap-1">
          <button v-for="opt in sortOptions" :key="opt.value"
            @click="$emit('sort-change', opt.value)"
            class="px-2.5 py-1.5 text-xs font-medium rounded-lg transition"
            :class="activeSort === opt.value
              ? 'bg-blue-100 text-blue-700'
              : 'bg-white text-gray-500 hover:bg-gray-100 border border-gray-200'">
            {{ opt.label }}
          </button>
        </div>

        <!-- View toggle (grid/list) -->
        <div v-if="hasViewToggle" class="flex border border-gray-200 rounded-lg overflow-hidden">
          <button @click="$emit('view-change', 'list')"
            class="px-2 py-1.5 text-xs transition"
            :class="viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-500'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
          <button @click="$emit('view-change', 'grid')"
            class="px-2 py-1.5 text-xs transition"
            :class="viewMode === 'grid' ? 'bg-blue-600 text-white' : 'bg-white text-gray-500'">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/>
            </svg>
          </button>
        </div>

        <!-- Distance filter -->
        <div v-if="hasDistance" class="flex items-center gap-1">
          <slot name="distance-filter" />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-16 text-gray-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
        <p class="text-sm">\uBD88\uB7EC\uC624\uB294 \uC911...</p>
      </div>

      <!-- Content Area -->
      <template v-else>
        <div class="flex gap-5 items-start">
          <!-- Main column -->
          <div class="flex-1 min-w-0">
            <!-- Items exist -->
            <div v-if="items && items.length">
              <!-- Grid view -->
              <div v-if="viewMode === 'grid'"
                class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                <div v-for="(item, idx) in items" :key="item.id || idx">
                  <slot name="grid-card" :item="item" :index="idx">
                    <slot name="item-card" :item="item" :index="idx" />
                  </slot>
                </div>
              </div>
              <!-- List view -->
              <div v-else class="space-y-3">
                <div v-for="(item, idx) in items" :key="item.id || idx">
                  <slot name="item-card" :item="item" :index="idx" />
                </div>
              </div>
            </div>

            <!-- Empty state -->
            <div v-else>
              <slot name="empty">
                <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
                  <p class="text-4xl mb-3">\uD83D\uDCED</p>
                  <p class="text-gray-400 text-sm">\uB370\uC774\uD130\uAC00 \uC5C6\uC2B5\uB2C8\uB2E4</p>
                </div>
              </slot>
            </div>

            <!-- Pagination -->
            <div v-if="pagination && pagination.last_page > 1" class="flex justify-center mt-6">
              <nav class="flex items-center gap-1">
                <button @click="goPage(pagination.current_page - 1)" :disabled="pagination.current_page <= 1"
                  class="px-3 py-1.5 rounded-lg text-sm border border-gray-200 text-gray-600 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed">
                  \uC774\uC804
                </button>
                <template v-for="pg in visiblePages" :key="pg">
                  <button v-if="pg === '...'" disabled class="px-2 py-1.5 text-sm text-gray-400">...</button>
                  <button v-else @click="goPage(pg)"
                    class="px-3 py-1.5 rounded-lg text-sm border transition"
                    :class="pg === pagination.current_page ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-200 text-gray-600 hover:bg-gray-100'">
                    {{ pg }}
                  </button>
                </template>
                <button @click="goPage(pagination.current_page + 1)" :disabled="pagination.current_page >= pagination.last_page"
                  class="px-3 py-1.5 rounded-lg text-sm border border-gray-200 text-gray-600 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed">
                  \uB2E4\uC74C
                </button>
              </nav>
            </div>

            <!-- Infinite scroll sentinel -->
            <div v-if="hasInfiniteScroll && items.length && !allLoaded" ref="sentinelRef"
              class="text-center py-4 text-gray-400 text-sm">
              \uB354 \uBD88\uB7EC\uC624\uB294 \uC911...
            </div>
          </div>

          <!-- Sidebar (desktop) -->
          <div v-if="$slots.sidebar" class="hidden lg:block flex-shrink-0 sticky top-16" style="width:320px">
            <slot name="sidebar" />
          </div>
        </div>
      </template>

      <!-- Floating Write Button -->
      <slot name="write-button">
        <RouterLink v-if="hasWrite && auth.isLoggedIn" :to="writeTo"
          class="fixed bottom-20 right-4 md:bottom-6 md:right-6 w-12 h-12 bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-700 transition z-40">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
        </RouterLink>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()

const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  emoji: { type: String, default: '' },
  totalCount: { type: Number, default: null },
  loading: { type: Boolean, default: false },
  items: { type: Array, default: () => [] },

  // Categories
  categories: { type: Array, default: null }, // [{ value, label }]
  activeCategory: { type: [String, Number], default: null },

  // Search
  hasSearch: { type: Boolean, default: true },
  searchQuery: { type: String, default: '' },
  searchPlaceholder: { type: String, default: null },

  // Sort
  sortOptions: { type: Array, default: null }, // [{ value, label }]
  activeSort: { type: String, default: '' },

  // View
  hasViewToggle: { type: Boolean, default: false },
  viewMode: { type: String, default: 'list' },

  // Distance
  hasDistance: { type: Boolean, default: false },

  // Write button
  hasWrite: { type: Boolean, default: false },
  writeTo: { type: String, default: '' },

  // Pagination
  pagination: { type: Object, default: null },

  // Infinite scroll
  hasInfiniteScroll: { type: Boolean, default: false },
  allLoaded: { type: Boolean, default: false },
})

const emit = defineEmits([
  'category-change', 'search', 'sort-change', 'view-change',
  'page-change', 'load-more',
])

// Visible page numbers (max 7)
const visiblePages = computed(() => {
  if (!props.pagination) return []
  const { current_page, last_page } = props.pagination
  if (last_page <= 7) return Array.from({ length: last_page }, (_, i) => i + 1)
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
  if (!props.pagination) return
  if (page < 1 || page > props.pagination.last_page) return
  emit('page-change', page)
}

// Infinite scroll observer
const sentinelRef = ref(null)
let observer = null

onMounted(() => {
  if (props.hasInfiniteScroll) {
    observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && !props.loading && !props.allLoaded) {
        emit('load-more')
      }
    }, { rootMargin: '200px' })

    if (sentinelRef.value) observer.observe(sentinelRef.value)
  }
})

onUnmounted(() => {
  if (observer) observer.disconnect()
})
</script>
