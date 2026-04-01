<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="bg-gradient-to-r from-indigo-500 to-indigo-700 text-white px-4 py-6">
      <div class="max-w-2xl mx-auto">
        <router-link to="/elder" class="text-indigo-200 hover:text-white text-base flex items-center gap-1 mb-3">
          <span class="text-lg">&larr;</span> 돌아가기
        </router-link>
        <h1 class="text-2xl font-bold flex items-center gap-2">
          <span class="text-3xl">👨‍👩‍👧</span> 보호자 대시보드
        </h1>
        <p v-if="elderInfo.name" class="mt-2 text-indigo-200 text-lg">
          {{ elderInfo.name }}님의 안전 현황
        </p>
      </div>
    </div>

    <div class="max-w-2xl mx-auto px-4 mt-6 space-y-5">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-indigo-300 border-t-indigo-600 rounded-full animate-spin"></div>
        <p class="mt-3 text-gray-500 text-lg">데이터 로딩 중...</p>
      </div>

      <template v-else>
        <!-- Elder Selection (if guardian of multiple) -->
        <div v-if="!selectedElder" class="bg-white rounded-2xl shadow-md p-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">보호 대상자를 선택하세요</h2>
          <p class="text-gray-500 mb-4">연결된 어르신의 안전 현황을 확인합니다</p>
          <div class="space-y-3">
            <button
              v-for="elder in elderList"
              :key="elder.id"
              @click="selectElder(elder)"
              class="w-full text-left bg-gray-50 hover:bg-indigo-50 border-2 border-gray-200 hover:border-indigo-300 rounded-xl px-5 py-4 transition"
            >
              <span class="text-lg font-bold text-gray-800">{{ elder.name }}</span>
              <span class="block text-base text-gray-500 mt-1">마지막 체크인: {{ elder.last_checkin_at ? formatDateTime(elder.last_checkin_at) : '없음' }}</span>
            </button>
          </div>
          <div v-if="!elderList.length" class="text-center py-6 text-gray-400">
            <p class="text-lg">연결된 어르신이 없습니다</p>
            <p class="text-base mt-2">어르신이 보호자 설정에서 회원님을 등록해야 합니다</p>
          </div>
        </div>

        <template v-if="selectedElder">
          <!-- Real-time SOS Alert Banner -->
          <div v-if="sosAlertData" class="bg-red-600 text-white rounded-2xl shadow-md p-6 text-center animate-pulse">
            <p class="text-3xl mb-2">🚨</p>
            <h2 class="text-2xl font-bold mb-2">긴급 SOS 알림!</h2>
            <p class="text-lg mb-1">{{ sosAlertData.elderName || '어르신' }}님이 SOS를 보냈습니다</p>
            <p class="text-sm opacity-80 mb-4">{{ sosAlertData.time }}</p>
            <div class="flex gap-3 justify-center">
              <button
                @click="callElder(selectedElder, 'audio')"
                class="bg-green-500 hover:bg-green-600 text-white font-bold text-lg px-8 py-3 rounded-xl transition"
              >
                📞 전화하기
              </button>
              <button
                @click="callElder(selectedElder, 'video')"
                class="bg-blue-500 hover:bg-blue-600 text-white font-bold text-lg px-8 py-3 rounded-xl transition"
              >
                📹 영상통화
              </button>
              <button
                @click="sosAlertData = null"
                class="bg-gray-500 hover:bg-gray-600 text-white font-bold text-lg px-6 py-3 rounded-xl transition"
              >
                닫기
              </button>
            </div>
          </div>

          <!-- Call Elder Card -->
          <div class="bg-white rounded-2xl shadow-md p-6">
            <h2 class="text-xl font-bold text-gray-800 mb-3">📞 어르신에게 전화</h2>
            <p class="text-base text-gray-500 mb-4">바로 전화를 걸어 안부를 확인하세요</p>
            <div class="flex gap-3">
              <button
                @click="callElder(selectedElder, 'audio')"
                class="flex-1 bg-green-500 hover:bg-green-600 text-white font-bold text-lg py-4 rounded-xl transition flex items-center justify-center gap-2"
              >
                <span class="text-2xl">📞</span> 음성 통화
              </button>
              <button
                @click="callElder(selectedElder, 'video')"
                class="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-bold text-lg py-4 rounded-xl transition flex items-center justify-center gap-2"
              >
                <span class="text-2xl">📹</span> 영상 통화
              </button>
            </div>
          </div>

          <!-- Current Status Card -->
          <div class="bg-white rounded-2xl shadow-md p-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">현재 상태</h2>
            <div class="grid grid-cols-2 gap-4">
              <!-- Today Checkin -->
              <div class="bg-gray-50 rounded-xl p-4 text-center">
                <p class="text-4xl mb-2">{{ elderInfo.today_checked ? '✅' : statusEmoji }}</p>
                <p class="text-base font-bold" :class="statusColor">
                  {{ elderInfo.today_checked ? '체크인 완료' : statusText }}
                </p>
              </div>
              <!-- Streak -->
              <div class="bg-gray-50 rounded-xl p-4 text-center">
                <p class="text-4xl mb-2">🔥</p>
                <p class="text-base font-bold text-orange-600">
                  연속 {{ elderInfo.streak || 0 }}일
                </p>
              </div>
              <!-- Last Checkin -->
              <div class="bg-gray-50 rounded-xl p-4 text-center col-span-2">
                <p class="text-base text-gray-500 mb-1">마지막 체크인</p>
                <p class="text-lg font-bold text-gray-800">
                  {{ elderInfo.last_checkin_at ? formatDateTime(elderInfo.last_checkin_at) : '기록 없음' }}
                </p>
              </div>
            </div>
          </div>

          <!-- Checkin Calendar -->
          <div class="bg-white rounded-2xl shadow-md p-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">📅 체크인 달력 (최근 30일)</h2>
            <div class="grid grid-cols-7 gap-2 text-center text-sm mb-2">
              <span v-for="d in ['일','월','화','수','목','금','토']" :key="d" class="text-gray-400 font-medium py-1">{{ d }}</span>
            </div>
            <div class="grid grid-cols-7 gap-2 text-center">
              <span v-for="n in calendarStartOffset" :key="'e'+n"></span>
              <button
                v-for="day in calendarDays"
                :key="day.date"
                @click="showDayDetail(day)"
                class="py-2 rounded-xl text-sm transition hover:ring-2 hover:ring-indigo-300"
                :class="{
                  'bg-green-100 text-green-700': day.status === 'checked',
                  'bg-red-100 text-red-600': day.status === 'missed',
                  'bg-gray-50 text-gray-300': day.status === 'future',
                }"
              >
                <span class="block font-bold">{{ day.day }}</span>
                <span class="block text-xs">{{ day.status === 'checked' ? '✅' : day.status === 'missed' ? '❌' : '⬜' }}</span>
              </button>
            </div>
            <!-- Day detail -->
            <div v-if="selectedDay" class="mt-4 bg-indigo-50 rounded-xl p-4">
              <div class="flex items-center justify-between">
                <span class="text-base font-bold text-indigo-800">{{ selectedDay.date }}</span>
                <button @click="selectedDay = null" class="text-gray-400 hover:text-gray-600">&times;</button>
              </div>
              <p v-if="selectedDay.status === 'checked'" class="text-green-600 text-base mt-1">
                ✅ {{ selectedDay.time ? selectedDay.time + '에 체크인' : '체크인 완료' }}
              </p>
              <p v-else-if="selectedDay.status === 'missed'" class="text-red-500 text-base mt-1">
                ❌ 체크인 미응답
              </p>
              <p v-else class="text-gray-400 text-base mt-1">⬜ 아직 도래하지 않은 날짜</p>
            </div>
          </div>

          <!-- SOS History -->
          <div class="bg-white rounded-2xl shadow-md p-6">
            <h2 class="text-xl font-bold text-red-600 mb-4">🚨 SOS 기록</h2>
            <div v-if="sosHistory.length === 0" class="text-center py-6 text-gray-400">
              <p class="text-lg">SOS 기록이 없습니다</p>
              <p class="text-base mt-1">좋은 소식이에요!</p>
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="sos in sosHistory"
                :key="sos.id"
                class="border rounded-xl p-4"
                :class="sos.resolved_at ? 'border-gray-200 bg-gray-50' : 'border-red-300 bg-red-50'"
              >
                <div class="flex items-start justify-between">
                  <div>
                    <p class="font-bold text-base" :class="sos.resolved_at ? 'text-gray-600' : 'text-red-700'">
                      {{ sos.resolved_at ? '해제됨' : '🚨 활성' }}
                    </p>
                    <p class="text-sm text-gray-500 mt-1">
                      {{ formatDateTime(sos.created_at) }}
                    </p>
                    <a
                      v-if="sos.lat && sos.lng"
                      :href="`https://maps.google.com/?q=${sos.lat},${sos.lng}`"
                      target="_blank"
                      class="text-blue-500 text-sm hover:underline mt-1 inline-block"
                    >
                      📍 위치 확인 (Google Maps)
                    </a>
                  </div>
                  <button
                    v-if="!sos.resolved_at"
                    @click="resolveSOS(sos.id)"
                    :disabled="resolvingId === sos.id"
                    class="bg-green-500 hover:bg-green-600 disabled:bg-green-300 text-white font-bold text-sm px-4 py-2 rounded-lg"
                  >
                    {{ resolvingId === sos.id ? '처리중...' : '해제' }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Notifications -->
          <div class="bg-white rounded-2xl shadow-md p-6">
            <h2 class="text-xl font-bold text-gray-800 mb-4">🔔 최근 알림</h2>
            <div v-if="notifications.length === 0" class="text-center py-6 text-gray-400">
              <p class="text-lg">최근 알림이 없습니다</p>
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="(noti, idx) in notifications"
                :key="idx"
                class="flex items-center gap-3 px-4 py-3 rounded-xl"
                :class="{
                  'bg-red-50': noti.type === 'sos',
                  'bg-yellow-50': noti.type === 'missed',
                  'bg-green-50': noti.type === 'checkin',
                }"
              >
                <span class="text-xl">
                  {{ noti.type === 'sos' ? '🚨' : noti.type === 'missed' ? '⚠️' : '✅' }}
                </span>
                <div class="flex-1">
                  <p class="text-base font-medium text-gray-800">{{ noti.message }}</p>
                  <p class="text-sm text-gray-400">{{ formatDateTime(noti.created_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </template>
      </template>
    </div>

    <!-- WebRTC Call Modal -->
    <CallModal
      :callState="callState"
      :callType="callType"
      :callDuration="callDuration"
      :localStream="localStream"
      :remoteStream="remoteStream"
      :remoteUser="remoteUser"
      :isMuted="isMuted"
      :isVideoOff="isVideoOff"
      :formatDuration="formatDuration"
      @answerCall="answerCall"
      @rejectCall="rejectCall"
      @endCall="endCall"
      @toggleMute="toggleMute"
      @toggleVideo="toggleVideo"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'
import { useSocket } from '../../composables/useSocket'
import { useWebRTC } from '../../composables/useWebRTC'
import CallModal from '../../components/CallModal.vue'

const auth = useAuthStore()
const token = localStorage.getItem('sk_token')
const headers = { Authorization: `Bearer ${token}` }

const loading = ref(true)
const elderList = ref([])
const selectedElder = ref(null)
const elderInfo = ref({})
const checkinHistory = ref([])
const sosHistory = ref([])
const notifications = ref([])
const selectedDay = ref(null)
const resolvingId = ref(null)

// WebRTC & Socket
const { isConnected: socketConnected, connect: socketConnect, emit: socketEmit, on: socketOn, off: socketOff, socket: getSocket } = useSocket()
const {
  localStream, remoteStream, peerConnection,
  callState, callType, callDuration,
  isMuted, isVideoOff, remoteUser,
  setSocket, setupSocketListeners, removeSocketListeners,
  startCall, answerCall, rejectCall, endCall,
  toggleMute, toggleVideo, formatDuration,
} = useWebRTC()
const sosAlertData = ref(null) // real-time SOS alert data

// Status helpers
const statusEmoji = computed(() => {
  if (!elderInfo.value.last_checkin_at) return '🔴'
  const hoursAgo = (Date.now() - new Date(elderInfo.value.last_checkin_at).getTime()) / (1000 * 60 * 60)
  if (hoursAgo < 24) return '🟢'
  if (hoursAgo < 48) return '🟡'
  return '🔴'
})

const statusText = computed(() => {
  if (!elderInfo.value.last_checkin_at) return '미응답'
  const hoursAgo = (Date.now() - new Date(elderInfo.value.last_checkin_at).getTime()) / (1000 * 60 * 60)
  if (hoursAgo < 24) return '안전'
  if (hoursAgo < 48) return '확인필요'
  return '미응답'
})

const statusColor = computed(() => {
  if (elderInfo.value.today_checked) return 'text-green-600'
  if (!elderInfo.value.last_checkin_at) return 'text-red-600'
  const hoursAgo = (Date.now() - new Date(elderInfo.value.last_checkin_at).getTime()) / (1000 * 60 * 60)
  if (hoursAgo < 24) return 'text-green-600'
  if (hoursAgo < 48) return 'text-yellow-600'
  return 'text-red-600'
})

// Calendar
const calendarDays = computed(() => {
  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const checkedMap = {}
  checkinHistory.value.forEach(h => {
    const dateStr = new Date(h.checked_at || h.created_at).toISOString().slice(0, 10)
    const timeStr = new Date(h.checked_at || h.created_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
    checkedMap[dateStr] = timeStr
  })
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    let status = 'future'
    if (d <= today) {
      status = checkedMap[dateStr] ? 'checked' : 'missed'
    }
    if (d.toDateString() === today.toDateString() && !checkedMap[dateStr]) {
      status = 'future'
    }
    days.push({ date: dateStr, day: d.getDate(), status, time: checkedMap[dateStr] || '' })
  }
  return days
})

const calendarStartOffset = computed(() => {
  if (!calendarDays.value.length) return 0
  const firstDate = new Date(calendarDays.value[0].date)
  return firstDate.getDay()
})

// Methods
function formatDateTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('ko-KR', {
    month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}

function showDayDetail(day) {
  selectedDay.value = selectedDay.value?.date === day.date ? null : day
}

async function loadGuardianData() {
  loading.value = true
  try {
    // First try to load list of elders this guardian watches
    const userId = auth.user?.id
    const { data } = await axios.get(`/api/elder/guardian/${userId}`, { headers })

    if (data.elders && data.elders.length > 0) {
      elderList.value = data.elders
      if (data.elders.length === 1) {
        selectElder(data.elders[0])
      }
    } else if (data.elder) {
      // Single elder data returned directly
      selectedElder.value = data.elder
      elderInfo.value = {
        name: data.elder.name,
        last_checkin_at: data.last_checkin_at,
        today_checked: data.today_checked,
        streak: data.streak || 0,
      }
      checkinHistory.value = data.checkin_history || []
      sosHistory.value = data.sos_history || []
      notifications.value = data.notifications || data.recent_logs || []
    } else {
      // Data is the elder info itself
      selectedElder.value = data
      elderInfo.value = data
      checkinHistory.value = data.checkin_history || []
      sosHistory.value = data.sos_history || []
      notifications.value = data.notifications || data.recent_logs || []
    }
  } catch (e) {
    console.error('Failed to load guardian data', e)
  } finally {
    loading.value = false
  }
}

async function selectElder(elder) {
  selectedElder.value = elder
  loading.value = true
  try {
    const { data } = await axios.get(`/api/elder/guardian/${elder.id}`, { headers })
    elderInfo.value = {
      name: elder.name,
      last_checkin_at: data.last_checkin_at || elder.last_checkin_at,
      today_checked: data.today_checked ?? false,
      streak: data.streak || 0,
    }
    checkinHistory.value = data.checkin_history || []
    sosHistory.value = data.sos_history || []
    notifications.value = data.notifications || data.recent_logs || []
  } catch (e) {
    console.error('Failed to load elder details', e)
  } finally {
    loading.value = false
  }
}

async function resolveSOS(sosId) {
  resolvingId.value = sosId
  try {
    await axios.post(`/api/elder/sos/${sosId}/resolve`, {}, { headers })
    const sos = sosHistory.value.find(s => s.id === sosId)
    if (sos) sos.resolved_at = new Date().toISOString()
  } catch (e) {
    alert('SOS 해제에 실패했습니다')
  } finally {
    resolvingId.value = null
  }
}

// Call elder directly
function callElder(elder, type = 'audio') {
  if (!elder || !elder.id) return
  startCall(
    { id: String(elder.id), name: elder.name || '어르신', _callerName: auth.user?.name || '보호자' },
    type
  )
}

// Handle incoming SOS socket alert
function handleSOSAlert(data) {
  sosAlertData.value = data
  // Auto-reload SOS history
  if (selectedElder.value) {
    selectElder(selectedElder.value)
  }
}

onMounted(() => {
  loadGuardianData()

  // Socket connection + WebRTC setup
  socketConnect()
  const initWebRTCSocket = () => {
    const s = getSocket()
    if (s) {
      setSocket(s)
      setupSocketListeners()
      // Listen for SOS alerts
      socketOn('elder:sos-alert', handleSOSAlert)
    } else {
      setTimeout(initWebRTCSocket, 500)
    }
  }
  setTimeout(initWebRTCSocket, 500)
})

onUnmounted(() => {
  removeSocketListeners()
  socketOff('elder:sos-alert', handleSOSAlert)
})
</script>
