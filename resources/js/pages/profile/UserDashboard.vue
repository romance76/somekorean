<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-4xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">📊 내 대시보드</h1>

    <div v-if="auth.user" class="space-y-4">
      <!-- 포인트 카드 -->
      <div class="bg-gradient-to-r from-amber-400 to-orange-400 rounded-xl p-5 text-amber-900">
        <div class="text-sm font-semibold opacity-80">내 포인트</div>
        <div class="text-3xl font-black mt-1">{{ (auth.user.points || 0).toLocaleString() }}P</div>
        <div class="flex gap-3 mt-3">
          <RouterLink to="/points" class="bg-white/30 px-4 py-1.5 rounded-lg text-sm font-bold hover:bg-white/50 transition">포인트 내역</RouterLink>
          <RouterLink to="/points/rules" class="bg-white/30 px-4 py-1.5 rounded-lg text-sm font-bold hover:bg-white/50 transition">적립 규칙</RouterLink>
        </div>
      </div>

      <!-- 퀵 링크 -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <RouterLink to="/profile/edit" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center hover:shadow-md transition">
          <div class="text-2xl mb-1">👤</div><div class="text-xs font-bold text-gray-700">프로필 수정</div>
        </RouterLink>
        <RouterLink to="/bookmarks" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center hover:shadow-md transition">
          <div class="text-2xl mb-1">🔖</div><div class="text-xs font-bold text-gray-700">북마크</div>
        </RouterLink>
        <RouterLink to="/friends" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center hover:shadow-md transition">
          <div class="text-2xl mb-1">👫</div><div class="text-xs font-bold text-gray-700">친구</div>
        </RouterLink>
        <RouterLink to="/messages" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center hover:shadow-md transition">
          <div class="text-2xl mb-1">✉️</div><div class="text-xs font-bold text-gray-700">쪽지</div>
        </RouterLink>
      </div>

      <!-- 내 정보 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 class="font-bold text-sm text-amber-900 mb-3">📋 내 정보</h3>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex justify-between"><span>이름</span><span class="font-semibold text-gray-800">{{ auth.user.name }}</span></div>
          <div class="flex justify-between"><span>이메일</span><span class="font-semibold text-gray-800">{{ auth.user.email }}</span></div>
          <div class="flex justify-between"><span>닉네임</span><span class="font-semibold text-gray-800">{{ auth.user.nickname || '-' }}</span></div>
          <div class="flex justify-between"><span>위치</span><span class="font-semibold text-gray-800">{{ auth.user.city ? auth.user.city + ', ' + auth.user.state : '-' }}</span></div>
          <div class="flex justify-between"><span>언어</span><span class="font-semibold text-gray-800">{{ auth.user.language === 'ko' ? '한국어' : 'English' }}</span></div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { useAuthStore } from '../../stores/auth'
const auth = useAuthStore()
</script>
