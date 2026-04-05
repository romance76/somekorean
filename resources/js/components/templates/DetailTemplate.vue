<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">

      <!-- Loading -->
      <div v-if="loading" class="text-center py-20 text-gray-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
        <p class="text-sm">\uBD88\uB7EC\uC624\uB294 \uC911...</p>
      </div>

      <template v-else-if="item">
        <!-- Back button + Breadcrumb -->
        <div class="flex items-center gap-2 mb-4">
          <button @click="$router.back()"
            class="flex items-center gap-1 text-sm text-gray-500 hover:text-blue-600 transition">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            \uB4A4\uB85C
          </button>
          <nav v-if="breadcrumb && breadcrumb.length" class="flex items-center gap-1 text-sm text-gray-500">
            <span class="text-gray-300 mx-1">/</span>
            <template v-for="(crumb, idx) in breadcrumb" :key="idx">
              <span v-if="idx > 0" class="text-gray-300 mx-0.5">/</span>
              <RouterLink v-if="crumb.to" :to="crumb.to" class="hover:text-blue-600 transition">{{ crumb.label }}</RouterLink>
              <span v-else class="text-gray-700 dark:text-gray-300 font-medium">{{ crumb.label }}</span>
            </template>
          </nav>
        </div>

        <!-- Two-column layout -->
        <div class="flex gap-5 items-start">
          <!-- Main column -->
          <div class="flex-1 min-w-0 space-y-4">

            <!-- Author info -->
            <div v-if="showAuthor && item.user" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm font-bold flex-shrink-0 overflow-hidden">
                  <img v-if="item.user.avatar" :src="item.user.avatar" class="w-full h-full object-cover"
                    @error="e => e.target.style.display='none'" />
                  <span v-if="!item.user.avatar">{{ (item.user.name || '?')[0] }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-gray-800 dark:text-white">{{ item.user.name || item.user.nickname }}</p>
                  <p class="text-xs text-gray-400">{{ formatDate(item.created_at) }}</p>
                </div>
                <div class="text-xs text-gray-400 flex items-center gap-3">
                  <span v-if="item.view_count !== undefined" class="flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                    </svg>
                    {{ item.view_count }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Header slot -->
            <slot name="header" />

            <!-- Image Gallery -->
            <div v-if="images && images.length" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
              <div class="relative">
                <img :src="images[activeImage]" class="w-full max-h-96 object-contain bg-gray-100 dark:bg-gray-900"
                  @error="onImageError" />
                <!-- Gallery dots -->
                <div v-if="images.length > 1" class="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
                  <button v-for="(img, idx) in images" :key="idx"
                    @click="activeImage = idx"
                    class="w-2 h-2 rounded-full transition"
                    :class="idx === activeImage ? 'bg-blue-600' : 'bg-white/60'" />
                </div>
              </div>
              <!-- Thumbnails -->
              <div v-if="images.length > 1" class="flex gap-1 p-2 overflow-x-auto">
                <img v-for="(img, idx) in images" :key="idx"
                  :src="img" @click="activeImage = idx"
                  class="w-16 h-16 object-cover rounded cursor-pointer border-2 transition"
                  :class="idx === activeImage ? 'border-blue-500' : 'border-transparent'"
                  @error="onImageError" />
              </div>
            </div>

            <!-- Body content slot -->
            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
              <slot name="body" />
            </div>

            <!-- Like / Bookmark / Share / Report bar -->
            <div v-if="showActions" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-3">
              <div class="flex items-center justify-center gap-6">
                <button @click="$emit('like')" class="flex items-center gap-1.5 text-sm transition"
                  :class="item.is_liked ? 'text-red-500' : 'text-gray-400 hover:text-red-500'">
                  <svg class="w-5 h-5" :fill="item.is_liked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
                  </svg>
                  {{ item.like_count || 0 }}
                </button>
                <button @click="$emit('bookmark')" class="flex items-center gap-1.5 text-sm transition"
                  :class="item.is_bookmarked ? 'text-yellow-500' : 'text-gray-400 hover:text-yellow-500'">
                  <svg class="w-5 h-5" :fill="item.is_bookmarked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
                  </svg>
                  \uBD81\uB9C8\uD06C
                </button>
                <button @click="handleShare" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-blue-500 transition">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
                  </svg>
                  \uACF5\uC720
                </button>
                <button @click="$emit('report')" class="flex items-center gap-1.5 text-sm text-gray-400 hover:text-red-400 transition">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                  </svg>
                  \uC2E0\uACE0
                </button>
              </div>
            </div>

            <!-- After body slot -->
            <slot name="after-body" />

            <!-- Comment Section -->
            <CommentSection v-if="showComments && item"
              :commentableType="commentType"
              :commentableId="item.id"
            />
          </div>

          <!-- Sidebar (desktop) -->
          <div v-if="$slots.sidebar" class="hidden lg:block flex-shrink-0 sticky top-16" style="width:320px">
            <slot name="sidebar" />
          </div>
        </div>

        <!-- Related items slot -->
        <div v-if="$slots.related" class="mt-6">
          <slot name="related" />
        </div>
      </template>

      <!-- Not found -->
      <div v-else-if="!loading" class="text-center py-20">
        <p class="text-4xl mb-3">\uD83D\uDE1E</p>
        <p class="text-gray-400">\uCEE8\uD150\uCE20\uB97C \uCC3E\uC744 \uC218 \uC5C6\uC2B5\uB2C8\uB2E4</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CommentSection from '../CommentSection.vue'

const props = defineProps({
  item: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  breadcrumb: { type: Array, default: () => [] },
  images: { type: Array, default: null },
  showAuthor: { type: Boolean, default: true },
  showActions: { type: Boolean, default: true },
  showComments: { type: Boolean, default: true },
  commentType: { type: String, default: 'post' },
})

defineEmits(['like', 'bookmark', 'report'])

const activeImage = ref(0)

// Default emoji+gradient fallback for broken images
function onImageError(e) {
  e.target.src = ''
  e.target.style.display = 'none'
  // Show parent fallback if available
  const parent = e.target.parentElement
  if (parent) {
    parent.classList.add('bg-gradient-to-br', 'from-blue-400', 'to-purple-500')
    parent.innerHTML = '<div class="flex items-center justify-center h-full text-6xl text-white/80">\uD83D\uDCF0</div>'
  }
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  const now = new Date()
  const diff = (now - date) / 1000
  if (diff < 60) return '\uBC29\uAE08 \uC804'
  if (diff < 3600) return `${Math.floor(diff / 60)}\uBD84 \uC804`
  if (diff < 86400) return `${Math.floor(diff / 3600)}\uC2DC\uAC04 \uC804`
  if (diff < 604800) return `${Math.floor(diff / 86400)}\uC77C \uC804`
  return date.toLocaleDateString('ko-KR')
}

function handleShare() {
  if (navigator.share) {
    navigator.share({ title: document.title, url: window.location.href })
  } else {
    navigator.clipboard.writeText(window.location.href)
    alert('URL\uC774 \uBCF5\uC0AC\uB418\uC5C8\uC2B5\uB2C8\uB2E4')
  }
}
</script>
