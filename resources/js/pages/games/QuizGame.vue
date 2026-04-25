<template>
  <div class="min-h-screen bg-gradient-to-b from-purple-600 to-indigo-700 pb-20">
    <div class="px-4 py-5 text-white">
      <RouterLink to="/games" class="inline-block bg-white/20 hover:bg-white/30 text-white text-sm font-bold px-3 py-2 rounded-lg mb-4">← 목록</RouterLink>
      <h1 class="text-2xl font-bold">🧠 일일 퀴즈</h1>
      <p class="text-purple-200 text-sm mt-1">매일 새로운 퀴즈로 포인트를 획득하세요!</p>
    </div>

    <div class="px-4">
      <div class="bg-white rounded-2xl p-8 text-center shadow-xl">
        <div class="text-6xl mb-3">🚧</div>
        <h2 class="text-xl font-bold text-gray-800 mb-2">일일 퀴즈 준비중</h2>
        <p class="text-gray-500 text-sm mb-6">
          새로운 매일 갱신 퀴즈 시스템을 준비하고 있습니다.<br>
          그동안 다른 퀴즈 게임을 즐겨보세요!
        </p>
        <div class="space-y-2">
          <RouterLink to="/games/flag" class="block bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-bold py-3 rounded-xl hover:from-blue-600 hover:to-indigo-600 transition">
            🌍 국기 퀴즈
          </RouterLink>
          <RouterLink to="/games/animals" class="block bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold py-3 rounded-xl hover:from-green-600 hover:to-emerald-600 transition">
            🦁 동물 퀴즈
          </RouterLink>
          <RouterLink to="/games/idiom" class="block bg-gradient-to-r from-amber-500 to-orange-500 text-white font-bold py-3 rounded-xl hover:from-amber-600 hover:to-orange-600 transition">
            📖 사자성어 퀴즈
          </RouterLink>
          <RouterLink to="/games/wordcard" class="block bg-gradient-to-r from-pink-500 to-rose-500 text-white font-bold py-3 rounded-xl hover:from-pink-600 hover:to-rose-600 transition">
            🎴 단어 카드
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
</script>
