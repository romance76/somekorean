<template>
  <!-- 개별 mypage 서브페이지 플레이스홀더 (Phase 2-C 묶음 3).
       다음 단계에서 UserDashboard.vue 의 해당 탭 로직을 개별 페이지로 마이그레이션.
       지금은 기존 UserDashboard 전체 페이지로 리다이렉트 가이드만 제공. -->
  <div class="bg-white rounded-xl shadow-sm p-6">
    <div class="flex items-center gap-3 mb-4">
      <span class="text-3xl">{{ icon }}</span>
      <div>
        <h3 class="text-lg font-bold">{{ title }}</h3>
        <p class="text-xs text-gray-500">이 페이지는 Phase 2-C 묶음 3 로 통합 마이그레이션 예정입니다.</p>
      </div>
    </div>
    <div class="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm">
      <p class="mb-2">임시로 기존 대시보드로 이동합니다:</p>
      <router-link :to="{ path: '/dashboard', query: { tab: defaultTab } }" class="inline-block px-4 py-2 bg-amber-400 hover:bg-amber-500 text-white rounded-lg font-semibold">
        기존 대시보드로 이동 →
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const labels = {
  posts: { icon: '📝', title: '내 글', tab: 'posts' },
  comments: { icon: '💬', title: '내 댓글', tab: 'posts' },
  market: { icon: '🛒', title: '내 장터', tab: 'market' },
  realestate: { icon: '🏠', title: '내 부동산', tab: 'realestate' },
  jobs: { icon: '💼', title: '내 구인', tab: 'jobs' },
  groupbuy: { icon: '🤝', title: '공동구매', tab: 'posts' },
  clubs: { icon: '👥', title: '동호회', tab: 'posts' },
  events: { icon: '🎉', title: '이벤트', tab: 'posts' },
  business: { icon: '🏪', title: '내 업소', tab: 'mybiz' },
  resume: { icon: '📄', title: '이력서', tab: 'resume' },
  bookmarks: { icon: '🔖', title: '북마크', tab: 'bookmarks' },
  friends: { icon: '👫', title: '친구', tab: 'profile' },
  messages: { icon: '✉️', title: '쪽지', tab: 'messages' },
  chats: { icon: '💭', title: '채팅', tab: 'profile' },
  calls: { icon: '📞', title: '통화내역', tab: 'calls' },
  notifications: { icon: '🔔', title: '알림', tab: 'profile' },
  points: { icon: '💰', title: '포인트', tab: 'points' },
  payments: { icon: '💳', title: '결제 이력', tab: 'payments' },
  ads: { icon: '📢', title: '광고 신청', tab: 'ads' },
  profile: { icon: '👤', title: '프로필', tab: 'profile' },
  security: { icon: '🔒', title: '보안·세션', tab: 'profile' },
  'notification-settings': { icon: '🔔', title: '알림 설정', tab: 'profile' },
  privacy: { icon: '🛡️', title: '개인정보', tab: 'profile' },
  elder: { icon: '💙', title: '안심서비스', tab: 'elder' },
}

const slug = computed(() => route.path.split('/').pop() || 'profile')
const meta = computed(() => labels[slug.value] || { icon: '📋', title: 'MyPage', tab: 'profile' })
const icon = computed(() => meta.value.icon)
const title = computed(() => meta.value.title)
const defaultTab = computed(() => meta.value.tab)
</script>
