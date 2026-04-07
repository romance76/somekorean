<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">

    <!-- 미가입 상태: 소개 페이지 -->
    <div v-if="!isSetup && step === 'intro'">
      <!-- 히어로 -->
      <div class="bg-gradient-to-br from-blue-500 via-cyan-500 to-teal-400 rounded-2xl p-8 text-center text-white mb-6 shadow-lg">
        <div class="text-5xl mb-3">💙</div>
        <h1 class="text-2xl font-black">안심서비스</h1>
        <p class="text-blue-100 text-sm mt-2">미국에서 혼자 계신 한인 분들을 위한<br/>매일 안부 확인 서비스</p>
      </div>

      <!-- 서비스 설명 카드 -->
      <div class="space-y-4 mb-6">
        <div class="bg-white rounded-xl shadow-sm border p-5 flex items-start gap-4">
          <div class="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">✅</div>
          <div>
            <h3 class="font-bold text-gray-800 text-sm">매일 체크인</h3>
            <p class="text-xs text-gray-500 mt-1">하루에 한 번 "잘 지내고 있어요" 버튼을 누르면 보호자에게 자동으로 알림이 갑니다. 포인트도 적립됩니다.</p>
          </div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 flex items-start gap-4">
          <div class="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">🚨</div>
          <div>
            <h3 class="font-bold text-gray-800 text-sm">긴급 SOS</h3>
            <p class="text-xs text-gray-500 mt-1">위급한 상황이 생기면 SOS 버튼 한 번으로 보호자에게 즉시 긴급 알림이 전송됩니다.</p>
          </div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 flex items-start gap-4">
          <div class="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">👨‍👩‍👧</div>
          <div>
            <h3 class="font-bold text-gray-800 text-sm">보호자 연결</h3>
            <p class="text-xs text-gray-500 mt-1">가족이나 지인을 보호자로 등록하면 체크인 여부를 실시간으로 확인할 수 있습니다.</p>
          </div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border p-5 flex items-start gap-4">
          <div class="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">⏰</div>
          <div>
            <h3 class="font-bold text-gray-800 text-sm">미체크인 알림</h3>
            <p class="text-xs text-gray-500 mt-1">정해진 시간까지 체크인하지 않으면 보호자에게 "체크인이 없습니다" 경고가 자동 전송됩니다.</p>
          </div>
        </div>
      </div>

      <div class="text-center">
        <button @click="step='setup'" class="bg-blue-500 text-white font-bold px-8 py-3 rounded-xl text-lg hover:bg-blue-600 shadow-lg transition">💙 안심서비스 시작하기</button>
        <p class="text-xs text-gray-400 mt-2">무료이며 언제든 해제할 수 있습니다</p>
      </div>
    </div>

    <!-- 설정 단계 -->
    <div v-else-if="step === 'setup'">
      <div class="bg-white rounded-2xl shadow-sm border p-6">
        <h2 class="text-lg font-black text-gray-800 mb-4">💙 안심서비스 설정</h2>

        <div class="space-y-4">
          <div>
            <label class="text-sm font-semibold text-gray-700">보호자 이메일</label>
            <input v-model="setupForm.guardian_email" type="email" placeholder="가족/지인 이메일" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-blue-400 outline-none" />
            <p class="text-[10px] text-gray-400 mt-1">체크인/SOS 알림을 받을 분의 이메일</p>
          </div>
          <div>
            <label class="text-sm font-semibold text-gray-700">보호자 전화번호 (선택)</label>
            <input v-model="setupForm.guardian_phone" type="text" placeholder="010-0000-0000" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-blue-400 outline-none" />
          </div>
          <div>
            <label class="text-sm font-semibold text-gray-700">체크인 마감 시간</label>
            <select v-model="setupForm.checkin_deadline" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm outline-none">
              <option value="10:00">오전 10:00</option>
              <option value="12:00">낮 12:00</option>
              <option value="14:00">오후 2:00</option>
              <option value="18:00">오후 6:00</option>
              <option value="20:00">오후 8:00</option>
            </select>
            <p class="text-[10px] text-gray-400 mt-1">이 시간까지 체크인하지 않으면 보호자에게 알림</p>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button @click="saveSetup" :disabled="!setupForm.guardian_email" class="flex-1 bg-blue-500 text-white font-bold py-3 rounded-xl hover:bg-blue-600 disabled:opacity-50">저장하고 시작</button>
          <button @click="step='intro'" class="text-gray-500 px-4">취소</button>
        </div>
      </div>
    </div>

    <!-- 메인 대시보드 (설정 완료 후) -->
    <div v-else>
      <h1 class="text-xl font-black text-gray-800 mb-4">💙 안심서비스</h1>

      <!-- 체크인 카드 -->
      <div class="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl p-6 text-white text-center mb-4 shadow-lg">
        <div class="text-4xl mb-2">{{ checkedIn ? '✅' : '💙' }}</div>
        <h2 class="text-xl font-black">{{ checkedIn ? '오늘 체크인 완료!' : '오늘의 체크인' }}</h2>
        <p class="text-blue-100 text-xs mt-1">{{ checkedIn ? '보호자에게 안부가 전달되었습니다' : '안전하게 잘 지내고 있다는 걸 알려주세요' }}</p>
        <button @click="checkin" :disabled="checkedIn" class="mt-4 bg-white text-blue-600 font-bold px-8 py-3 rounded-xl hover:bg-blue-50 transition disabled:opacity-50 shadow">
          {{ checkedIn ? '✅ 완료' : '체크인하기 (+5P)' }}
        </button>
      </div>

      <!-- 퀵 액션 -->
      <div class="grid grid-cols-3 gap-3 mb-4">
        <button @click="sendSOS" class="bg-red-50 border-2 border-red-200 rounded-xl p-4 text-center hover:bg-red-100 transition">
          <div class="text-2xl mb-1">🚨</div>
          <div class="text-xs font-bold text-red-700">긴급 SOS</div>
        </button>
        <RouterLink to="/elder/checkin" class="bg-white rounded-xl shadow-sm border p-4 text-center hover:shadow-md transition">
          <div class="text-2xl mb-1">📋</div>
          <div class="text-xs font-bold text-gray-700">체크인 기록</div>
        </RouterLink>
        <RouterLink to="/elder/guardian" class="bg-white rounded-xl shadow-sm border p-4 text-center hover:shadow-md transition">
          <div class="text-2xl mb-1">👨‍👩‍👧</div>
          <div class="text-xs font-bold text-gray-700">보호자 화면</div>
        </RouterLink>
      </div>

      <!-- 최근 체크인 기록 -->
      <div class="bg-white rounded-xl shadow-sm border overflow-hidden mb-4">
        <div class="px-4 py-3 border-b font-bold text-sm text-gray-800">📋 최근 체크인</div>
        <div v-if="!recentCheckins.length" class="px-4 py-6 text-center text-sm text-gray-400">아직 기록이 없습니다</div>
        <div v-for="c in recentCheckins" :key="c.id" class="px-4 py-2.5 border-b last:border-0 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-green-500"></span>
            <span class="text-sm text-gray-700">{{ c.created_at?.slice(0, 10) }}</span>
          </div>
          <span class="text-xs text-gray-400">{{ c.created_at?.slice(11, 16) }}</span>
        </div>
      </div>

      <!-- 설정 변경 -->
      <button @click="step='setup'" class="text-xs text-gray-400 hover:text-blue-500">⚙️ 안심서비스 설정 변경</button>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useSiteStore } from '../../stores/site'
import axios from 'axios'

const siteStore = useSiteStore()
const checkedIn = ref(false)
const isSetup = ref(false)
const step = ref('intro') // intro, setup, dashboard
const recentCheckins = ref([])
const setupForm = reactive({ guardian_email: '', guardian_phone: '', checkin_deadline: '12:00' })

async function checkin() {
  try {
    await axios.post('/api/elder/checkin', { lat: null, lng: null })
    checkedIn.value = true
    siteStore.toast('체크인 완료! +5P', 'success')
    loadCheckins()
  } catch (e) { siteStore.toast(e.response?.data?.message || '체크인 실패', 'error') }
}

async function sendSOS() {
  if (!confirm('정말 SOS를 보내시겠습니까?\n보호자에게 긴급 알림이 전송됩니다.')) return
  try {
    await axios.post('/api/elder/sos', { message: '긴급 도움 요청' })
    siteStore.toast('🚨 SOS가 전송되었습니다', 'error')
  } catch (e) { siteStore.toast('SOS 전송 실패', 'error') }
}

async function saveSetup() {
  try {
    await axios.put('/api/elder/settings', setupForm)
    isSetup.value = true
    step.value = 'dashboard'
    siteStore.toast('안심서비스가 설정되었습니다!', 'success')
  } catch (e) { siteStore.toast(e.response?.data?.message || '설정 실패', 'error') }
}

async function loadCheckins() {
  try { const { data } = await axios.get('/api/elder/checkin-history'); recentCheckins.value = (data.data?.data || data.data || []).slice(0, 7) } catch {}
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/elder/settings')
    if (data.data?.guardian_email || data.data?.id) {
      isSetup.value = true
      step.value = 'dashboard'
      if (data.data.guardian_email) setupForm.guardian_email = data.data.guardian_email
      if (data.data.guardian_phone) setupForm.guardian_phone = data.data.guardian_phone
      if (data.data.checkin_deadline) setupForm.checkin_deadline = data.data.checkin_deadline
    }
  } catch {}
  loadCheckins()
})
</script>
