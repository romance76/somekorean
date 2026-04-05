<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <!-- 로딩 -->
      <div v-if="!item" class="text-center py-20 text-gray-400">불러오는 중...</div>

      <template v-else>
        <!-- Breadcrumb -->
        <nav v-if="breadcrumb && breadcrumb.length" class="flex items-center gap-1 text-sm text-gray-500 mb-3">
          <template v-for="(crumb, idx) in breadcrumb" :key="idx">
            <span v-if="idx > 0" class="text-gray-300">/</span>
            <router-link v-if="crumb.to" :to="crumb.to" class="hover:text-blue-600 transition">{{ crumb.label }}</router-link>
            <span v-else class="text-gray-700 font-medium">{{ crumb.label }}</span>
          </template>
        </nav>

        <!-- 2컬럼 레이아웃 -->
        <div class="flex gap-5 items-start">
          <!-- 메인 컬럼 -->
          <div class="flex-1 min-w-0">
            <!-- 헤더 슬롯 -->
            <div v-if="$slots.header">
              <slot name="header" />
            </div>

            <!-- 본문 슬롯 -->
            <div v-if="$slots.body">
              <slot name="body" />
            </div>

            <!-- 좋아요/북마크/공유/신고 반응 바 -->
            <ReactionBar v-if="showReactions && item"
              :itemType="reactionType"
              :itemId="item.id"
              :likes="item.like_count || 0"
              :isLiked="!!item.is_liked"
              :isBookmarked="!!item.is_bookmarked"
              @liked="(e) => $emit('liked', e)"
              @bookmarked="(e) => $emit('bookmarked', e)"
            />

            <!-- 본문 아래 추가 영역 -->
            <div v-if="$slots['after-body']">
              <slot name="after-body" />
            </div>

            <!-- 댓글 섹션 -->
            <CommentSection v-if="showComments && item"
              :commentableType="commentType"
              :commentableId="item.id"
              class="mb-4"
            />
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
import ReactionBar from '../ReactionBar.vue'
import CommentSection from '../CommentSection.vue'

const props = defineProps({
  item: { type: Object, default: null },
  breadcrumb: {
    type: Array,
    default: () => []
    // [{ label: '이벤트', to: '/events' }, { label: '상세' }]
  },
  showReactions: { type: Boolean, default: true },
  showComments: { type: Boolean, default: true },
  // ReactionBar / CommentSection에서 사용할 타입 (기본값은 'post')
  reactionType: { type: String, default: 'post' },
  commentType: { type: String, default: 'post' }
})

defineEmits(['liked', 'bookmarked'])
</script>
