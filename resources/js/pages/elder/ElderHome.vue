<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <h1 class="text-2xl font-black text-gray-800 mb-5">💙 안심서비스</h1>

    <!-- 체크인 카드 -->
    <div class="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl p-6 text-white text-center mb-5 shadow-lg">
      <div class="text-5xl mb-3">✅</div>
      <h2 class="text-xl font-black">오늘의 체크인</h2>
      <p class="text-blue-100 text-sm mt-1">안전하게 잘 지내고 있다는 걸 알려주세요</p>
      <button @click="checkin" :disabled="checkedIn" class="mt-4 bg-white text-blue-600 font-bold px-8 py-3 rounded-xl text-lg hover:bg-blue-50 transition disabled:opacity-50 disabled:cursor-not-allowed shadow">
        {{ checkedIn ? '✅ 오늘 완료!' : '체크인하기 (+5P)' }}
      </button>
    </div>

    <!-- SOS -->
    <div class="bg-red-50 border-2 border-red-200 rounded-2xl p-5 text-center mb-5">
      <div class="text-4xl mb-2">🚨</div>
      <h3 class="text-lg font-black text-red-700">긴급 SOS</h3>
      <p class="text-xs text-red-500 mt-1">위급 상황 시 보호자에게 알림이 전송됩니다</p>
      <button @click="sendSOS" class="mt-3 bg-red-500 text-white font-bold px-8 py-3 rounded-xl text-lg hover:bg-red-600 transition shadow">
        🚨 SOS 보내기
      </button>
    </div>

    <!-- 퀵 링크 -->
    <div class="grid grid-cols-2 gap-3">
      <RouterLink to="/elder/checkin" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center hover:shadow-md transition">
        <div class="text-2xl mb-1">📋</div>
        <div class="text-sm font-bold text-gray-700">체크인 기록</div>
      </RouterLink>
      <RouterLink to="/elder/guardian" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 text-center hover:shadow-md transition">
        <div class="text-2xl mb-1">👨‍👩‍👧</div>
        <div class="text-sm font-bold text-gray-700">보호자 화면</div>
      </RouterLink>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useSiteStore } from '../../stores/site'
import axios from 'axios'
const siteStore = useSiteStore()
const checkedIn = ref(false)

async function checkin() {
  try {
    await axios.post('/api/elder/checkin', { lat: null, lng: null })
    checkedIn.value = true
    siteStore.toast('체크인 완료! +5P', 'success')
  } catch (e) { siteStore.toast(e.response?.data?.message || '체크인 실패', 'error') }
}

async function sendSOS() {
  if (!confirm('정말 SOS를 보내시겠습니까? 보호자에게 긴급 알림이 전송됩니다.')) return
  try {
    await axios.post('/api/elder/sos', { message: '긴급 도움 요청' })
    siteStore.toast('🚨 SOS가 전송되었습니다', 'error')
  } catch (e) { siteStore.toast('SOS 전송 실패', 'error') }
}

onMounted(async () => {
  try { await axios.get('/api/elder/settings') } catch {}
})
</script>
