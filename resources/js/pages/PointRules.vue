<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="max-w-3xl mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-red-600 to-red-500 text-white px-6 py-6 rounded-2xl">
        <h1 class="text-xl font-black">{{ $t('points.rules_title') }}</h1>
        <p class="text-red-200 text-sm mt-0.5">{{ $t('points.rules_subtitle') }}</p>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 py-6 space-y-5">

      <!-- Earning Rules -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="bg-green-50 px-5 py-3 flex items-center gap-2">
          <span class="text-xl">💰</span>
          <h2 class="font-black text-green-800 text-base">{{ $t('points.earning_rules') }}</h2>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="rule in earningRules" :key="rule.action" class="flex items-center justify-between px-5 py-3.5">
            <div class="flex items-center gap-3">
              <span class="text-xl w-8 text-center">{{ rule.icon }}</span>
              <div>
                <p class="text-sm font-semibold text-gray-800">{{ rule.action }}</p>
                <p class="text-xs text-gray-500">{{ rule.desc }}</p>
              </div>
            </div>
            <div class="text-right flex-shrink-0 ml-4">
              <span class="font-black text-green-600 text-base">+{{ rule.points }}P</span>
              <p v-if="rule.limit" class="text-xs text-gray-400">{{ rule.limit }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Spending Rules -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="bg-red-50 px-5 py-3 flex items-center gap-2">
          <span class="text-xl">🛒</span>
          <h2 class="font-black text-red-800 text-base">{{ $t('points.spending_rules') }}</h2>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="rule in spendingRules" :key="rule.action" class="flex items-center justify-between px-5 py-3.5">
            <div class="flex items-center gap-3">
              <span class="text-xl w-8 text-center">{{ rule.icon }}</span>
              <div>
                <p class="text-sm font-semibold text-gray-800">{{ rule.action }}</p>
                <p class="text-xs text-gray-500">{{ rule.desc }}</p>
              </div>
            </div>
            <div class="text-right flex-shrink-0 ml-4">
              <span class="font-black text-red-600 text-base">-{{ rule.points }}P</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Game Point Conversion -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="bg-blue-50 px-5 py-3 flex items-center gap-2">
          <span class="text-xl">🎮</span>
          <h2 class="font-black text-blue-800 text-base">{{ $t('points.game_conversion') }}</h2>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="rule in gameRules" :key="rule.action" class="flex items-center justify-between px-5 py-3.5">
            <div class="flex items-center gap-3">
              <span class="text-xl w-8 text-center">{{ rule.icon }}</span>
              <div>
                <p class="text-sm font-semibold text-gray-800">{{ rule.action }}</p>
                <p class="text-xs text-gray-500">{{ rule.desc }}</p>
              </div>
            </div>
            <div class="text-right flex-shrink-0 ml-4">
              <span class="font-black text-blue-600 text-base">{{ rule.rate }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Back -->
      <div class="text-center">
        <router-link to="/points" class="text-sm text-red-600 font-semibold hover:underline">
          {{ $t('points.back_to_dashboard') }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useLangStore } from '../stores/lang'

const { $t } = useLangStore()

const earningRules = [
  { icon: '📝', action: '게시글 작성', desc: '게시판에 글 작성', points: 10, limit: '1일 10회' },
  { icon: '💬', action: '댓글 작성', desc: '게시글에 댓글 달기', points: 3, limit: '1일 30회' },
  { icon: '👍', action: '좋아요 받기', desc: '내 글/댓글에 좋아요', points: 2, limit: '' },
  { icon: '✅', action: '출석 체크', desc: '매일 출석 체크', points: 10, limit: '1일 1회' },
  { icon: '🎰', action: '일일 룰렛', desc: '매일 룰렛 돌리기', points: '1~100', limit: '1일 1회' },
  { icon: '❓', action: 'Q&A 답변', desc: '질문에 답변 달기', points: 5, limit: '1일 10회' },
  { icon: '🍳', action: '레시피 등록', desc: '새 레시피 작성', points: 15, limit: '1일 5회' },
  { icon: '⭐', action: '답변 채택', desc: 'Q&A에서 채택됨', points: 20, limit: '' },
  { icon: '🏪', action: '업소 리뷰', desc: '업소에 리뷰 작성', points: 5, limit: '1일 5회' },
  { icon: '👋', action: '회원가입', desc: '첫 가입 보너스', points: 100, limit: '1회' },
]

const spendingRules = [
  { icon: '📌', action: '게시글 끌어올리기', desc: '게시글 상단 고정', points: 50 },
  { icon: '🔔', action: '긴급 알림', desc: '장터/구인 긴급 알림', points: 100 },
  { icon: '🎨', action: '프로필 꾸미기', desc: '특별 배지, 닉네임 색상', points: 200 },
  { icon: '🎮', action: '게임 참가', desc: '포인트 게임 참가비', points: '10~100' },
]

const gameRules = [
  { icon: '🔄', action: '포인트 -> 게임머니', desc: '게임에서 사용 가능', rate: '1P = 1G' },
  { icon: '🔄', action: '게임머니 -> 포인트', desc: '게임 수익 전환', rate: '1G = 1P' },
  { icon: '🏆', action: '게임 승리 보너스', desc: '승리 시 추가 보상', rate: '+10~50%' },
  { icon: '📊', action: '리더보드 보상', desc: '주간 랭킹 보상', rate: '1~3위' },
]
</script>
