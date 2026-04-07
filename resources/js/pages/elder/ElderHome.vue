<template>
<div class="min-h-screen bg-gray-50">

  <!-- ═══ 랜딩 페이지 (비로그인 또는 미설정) ═══ -->
  <div v-if="page === 'landing'">
    <!-- 히어로 -->
    <div class="bg-gradient-to-br from-blue-600 via-cyan-500 to-teal-400 text-white">
      <div class="max-w-5xl mx-auto px-4 py-16 text-center">
        <div class="inline-flex items-center gap-2 bg-white/20 rounded-full px-4 py-1.5 text-sm font-bold mb-4">💙 SomeKorean 안심서비스</div>
        <h1 class="text-3xl md:text-4xl font-black leading-tight">미국에서 혼자 계신<br/>한인 분들의 안전을 지킵니다</h1>
        <p class="text-blue-100 mt-4 max-w-xl mx-auto">매일 한 번의 체크인으로 가족에게 안부를 전하고, 위급 시 한 번의 터치로 도움을 요청하세요.</p>
        <div class="mt-8 flex justify-center gap-3">
          <button v-if="auth.isLoggedIn" @click="page='setup'" class="bg-white text-blue-600 font-bold px-8 py-3 rounded-xl text-lg hover:bg-blue-50 shadow-lg transition">시작하기</button>
          <RouterLink v-else to="/register" class="bg-white text-blue-600 font-bold px-8 py-3 rounded-xl text-lg hover:bg-blue-50 shadow-lg transition">회원가입하고 시작</RouterLink>
          <a href="#how" class="border-2 border-white/50 text-white font-bold px-8 py-3 rounded-xl text-lg hover:bg-white/10 transition">자세히 보기 ↓</a>
        </div>
      </div>
    </div>

    <div class="max-w-5xl mx-auto px-4">
      <!-- 이용 흐름 -->
      <div id="how" class="py-12">
        <h2 class="text-2xl font-black text-gray-800 text-center mb-8">어떻게 이용하나요?</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-3">1️⃣</div>
            <h3 class="font-bold text-gray-800 text-sm">보호자 등록</h3>
            <p class="text-xs text-gray-500 mt-1">가족이나 지인의 이메일을 등록하세요</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-3">2️⃣</div>
            <h3 class="font-bold text-gray-800 text-sm">매일 체크인</h3>
            <p class="text-xs text-gray-500 mt-1">하루 한 번 "잘 지내요" 버튼을 눌러주세요</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-3">3️⃣</div>
            <h3 class="font-bold text-gray-800 text-sm">자동 알림</h3>
            <p class="text-xs text-gray-500 mt-1">보호자에게 체크인 결과가 자동 전달됩니다</p>
          </div>
          <div class="text-center">
            <div class="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-3">4️⃣</div>
            <h3 class="font-bold text-gray-800 text-sm">긴급 SOS</h3>
            <p class="text-xs text-gray-500 mt-1">위급 시 한 번의 터치로 보호자에게 긴급 알림</p>
          </div>
        </div>
      </div>

      <!-- 주요 기능 -->
      <div class="py-12 border-t">
        <h2 class="text-2xl font-black text-gray-800 text-center mb-8">주요 기능</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div class="bg-white rounded-2xl shadow-sm border p-6 flex items-start gap-4">
            <div class="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">✅</div>
            <div>
              <h3 class="font-bold text-gray-800">매일 체크인</h3>
              <p class="text-sm text-gray-500 mt-1">하루 한 번 버튼만 누르면 됩니다. 포인트도 적립되고, 보호자에게 자동으로 안부가 전달됩니다.</p>
            </div>
          </div>
          <div class="bg-white rounded-2xl shadow-sm border p-6 flex items-start gap-4">
            <div class="w-14 h-14 bg-red-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">🚨</div>
            <div>
              <h3 class="font-bold text-gray-800">긴급 SOS</h3>
              <p class="text-sm text-gray-500 mt-1">넘어지거나, 아프거나, 위험한 상황에서 SOS 버튼 한 번으로 보호자에게 즉시 알림이 갑니다.</p>
            </div>
          </div>
          <div class="bg-white rounded-2xl shadow-sm border p-6 flex items-start gap-4">
            <div class="w-14 h-14 bg-amber-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">⏰</div>
            <div>
              <h3 class="font-bold text-gray-800">미체크인 자동 경고</h3>
              <p class="text-sm text-gray-500 mt-1">설정한 시간까지 체크인하지 않으면 보호자에게 "오늘 체크인이 없습니다" 알림이 자동 전송됩니다.</p>
            </div>
          </div>
          <div class="bg-white rounded-2xl shadow-sm border p-6 flex items-start gap-4">
            <div class="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center text-2xl flex-shrink-0">👨‍👩‍👧</div>
            <div>
              <h3 class="font-bold text-gray-800">보호자 대시보드</h3>
              <p class="text-sm text-gray-500 mt-1">가족이 보호자로 등록하면 체크인 기록, SOS 이력을 한눈에 확인할 수 있습니다.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 대상 -->
      <div class="py-12 border-t">
        <h2 class="text-2xl font-black text-gray-800 text-center mb-3">이런 분들에게 추천합니다</h2>
        <p class="text-center text-gray-500 text-sm mb-8">무료이며 언제든 해제할 수 있습니다</p>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div class="bg-blue-50 rounded-xl p-5 text-center">
            <div class="text-3xl mb-2">🏠</div>
            <div class="font-bold text-gray-800 text-sm">독거 어르신</div>
            <div class="text-xs text-gray-500 mt-1">미국에서 혼자 생활하시는 한인 어르신</div>
          </div>
          <div class="bg-blue-50 rounded-xl p-5 text-center">
            <div class="text-3xl mb-2">🎓</div>
            <div class="font-bold text-gray-800 text-sm">유학생</div>
            <div class="text-xs text-gray-500 mt-1">부모님이 한국에 계신 유학생</div>
          </div>
          <div class="bg-blue-50 rounded-xl p-5 text-center">
            <div class="text-3xl mb-2">💼</div>
            <div class="font-bold text-gray-800 text-sm">1인 가구</div>
            <div class="text-xs text-gray-500 mt-1">혼자 살고 있는 직장인/프리랜서</div>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="py-12 border-t text-center">
        <div class="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl p-8 text-white">
          <h2 class="text-2xl font-black">지금 바로 시작하세요</h2>
          <p class="text-blue-100 text-sm mt-2">설정은 1분이면 됩니다</p>
          <button v-if="auth.isLoggedIn" @click="page='setup'" class="mt-5 bg-white text-blue-600 font-bold px-8 py-3 rounded-xl text-lg hover:bg-blue-50 shadow-lg">💙 안심서비스 시작하기</button>
          <RouterLink v-else to="/login" class="mt-5 inline-block bg-white text-blue-600 font-bold px-8 py-3 rounded-xl text-lg hover:bg-blue-50 shadow-lg">로그인하고 시작하기</RouterLink>
        </div>
      </div>
    </div>
  </div>

  <!-- ═══ 설정 단계 ═══ -->
  <div v-else-if="page === 'setup'" class="max-w-xl mx-auto px-4 py-8">
    <div class="bg-white rounded-2xl shadow-sm border p-6">
      <h2 class="text-lg font-black text-gray-800 mb-1">💙 안심서비스 설정</h2>
      <p class="text-xs text-gray-400 mb-5">보호자 정보와 체크인 시간을 설정하세요</p>
      <div class="space-y-4">
        <div>
          <label class="text-sm font-semibold text-gray-700">보호자 이메일 *</label>
          <input v-model="setupForm.guardian_email" type="email" placeholder="가족/지인 이메일" class="w-full border rounded-lg px-3 py-2.5 mt-1 text-sm focus:ring-2 focus:ring-blue-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">보호자 전화번호</label>
          <input v-model="setupForm.guardian_phone" type="text" placeholder="010-0000-0000" class="w-full border rounded-lg px-3 py-2.5 mt-1 text-sm focus:ring-2 focus:ring-blue-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">체크인 마감 시간</label>
          <select v-model="setupForm.checkin_deadline" class="w-full border rounded-lg px-3 py-2.5 mt-1 text-sm outline-none">
            <option value="10:00">오전 10:00</option><option value="12:00">낮 12:00</option><option value="14:00">오후 2:00</option><option value="18:00">오후 6:00</option><option value="20:00">오후 8:00</option>
          </select>
        </div>
      </div>
      <div class="flex gap-3 mt-6">
        <button @click="saveSetup" :disabled="!setupForm.guardian_email" class="flex-1 bg-blue-500 text-white font-bold py-3 rounded-xl hover:bg-blue-600 disabled:opacity-50">저장하고 시작</button>
        <button @click="page='landing'" class="text-gray-500 px-4">취소</button>
      </div>
    </div>
  </div>

  <!-- ═══ 대시보드 ═══ -->
  <div v-else class="max-w-3xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">💙 안심서비스</h1>

    <div class="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl p-6 text-white text-center mb-4 shadow-lg">
      <div class="text-4xl mb-2">{{ checkedIn ? '✅' : '💙' }}</div>
      <h2 class="text-xl font-black">{{ checkedIn ? '오늘 체크인 완료!' : '오늘의 체크인' }}</h2>
      <p class="text-blue-100 text-xs mt-1">{{ checkedIn ? '보호자에게 안부가 전달되었습니다' : '안전하게 잘 지내고 있다는 걸 알려주세요' }}</p>
      <button @click="checkin" :disabled="checkedIn" class="mt-4 bg-white text-blue-600 font-bold px-8 py-3 rounded-xl hover:bg-blue-50 transition disabled:opacity-50 shadow">
        {{ checkedIn ? '✅ 완료' : '체크인하기 (+5P)' }}
      </button>
    </div>

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

    <button @click="page='setup'" class="text-xs text-gray-400 hover:text-blue-500">⚙️ 설정 변경</button>
  </div>
</div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useSiteStore } from '../../stores/site'
import axios from 'axios'

const auth = useAuthStore()
const siteStore = useSiteStore()
const page = ref('landing')
const checkedIn = ref(false)
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
    page.value = 'dashboard'
    siteStore.toast('안심서비스가 설정되었습니다!', 'success')
  } catch (e) { siteStore.toast(e.response?.data?.message || '설정 실패', 'error') }
}

async function loadCheckins() {
  try { const { data } = await axios.get('/api/elder/checkin-history'); recentCheckins.value = (data.data?.data || data.data || []).slice(0, 7) } catch {}
}

onMounted(async () => {
  if (!auth.isLoggedIn) { page.value = 'landing'; return }
  try {
    const { data } = await axios.get('/api/elder/settings')
    if (data.data?.guardian_email || data.data?.id) {
      page.value = 'dashboard'
      if (data.data.guardian_email) setupForm.guardian_email = data.data.guardian_email
      if (data.data.guardian_phone) setupForm.guardian_phone = data.data.guardian_phone
      if (data.data.checkin_deadline) setupForm.checkin_deadline = data.data.checkin_deadline
    } else {
      page.value = 'landing'
    }
  } catch { page.value = 'landing' }
  loadCheckins()
})
</script>
