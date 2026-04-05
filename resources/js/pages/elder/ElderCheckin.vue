<template>
  <div class="min-h-screen bg-gradient-to-b from-green-50 to-white flex flex-col">
    <!-- Header -->
    <div class="bg-white shadow-sm px-4 py-4">
      <router-link to="/elder" class="text-blue-500 text-lg font-medium flex items-center gap-1">
        <span class="text-xl">&larr;</span> 돌아가기
      </router-link>
    </div>

    <div class="flex-1 flex flex-col items-center justify-center px-6 py-8 max-w-lg mx-auto w-full">
      <!-- Greeting -->
      <p class="text-5xl mb-4">{{ greetingEmoji }}</p>
      <h1 class="text-2xl font-bold text-gray-800 mb-2">{{ greetingText }}</h1>
      <p class="text-xl text-gray-500 mb-8">{{ todayDate }}</p>

      <!-- Already checked in -->
      <div v-if="alreadyChecked" class="text-center mb-8">
        <div class="text-7xl mb-4">&#x1F389;</div>
        <p class="text-2xl font-bold text-green-600 mb-2">오늘 체크인 완료!</p>
        <p class="text-lg text-gray-500">{{ formatTime(lastCheckinAt) }}에 체크인했어요</p>
        <div v-if="streakDays > 1" class="mt-4 bg-orange-50 rounded-2xl px-6 py-3 inline-block">
          <span class="text-xl font-bold text-orange-600">연속 {{ streakDays }}일 체크인 중!</span>
        </div>
        <div class="mt-4 bg-blue-50 rounded-2xl px-6 py-3 inline-block">
          <span class="text-lg text-blue-600">포인트 5점이 적립되었어요</span>
        </div>
      </div>

      <!-- Checkin success animation -->
      <div v-else-if="justCheckedIn" class="text-center mb-8">
        <div class="text-7xl mb-4 animate-bounce">&#x1F389;</div>
        <p class="text-2xl font-bold text-green-600 mb-2">체크인 완료!</p>
        <p class="text-lg text-gray-500">포인트 5점이 적립되었어요</p>
        <div v-if="streakDays > 1" class="mt-4 bg-orange-50 rounded-2xl px-6 py-3 inline-block">
          <span class="text-xl font-bold text-orange-600">연속 {{ streakDays }}일 체크인 중!</span>
        </div>
      </div>

      <!-- Checkin button -->
      <div v-else class="text-center">
        <button
          @click="doCheckin"
          :disabled="checkinLoading"
          class="w-72 h-24 bg-green-500 hover:bg-green-600 disabled:bg-green-300 active:scale-95 text-white font-bold text-2xl rounded-2xl shadow-lg transition transform"
        >
          {{ checkinLoading ? '처리 중...' : '괜찮아요!' }}
        </button>
        <p class="mt-4 text-lg text-gray-400">버튼을 누르면 보호자에게 알림이 갑니다</p>
      </div>
    </div>

    <!-- 7-Day Calendar View -->
    <div class="max-w-lg mx-auto w-full px-6 pb-6">
      <div class="bg-white rounded-2xl shadow-md p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-800">최근 7일 기록</h2>
          <span v-if="streakDays > 0" class="text-orange-500 font-bold text-lg">
            연속 {{ streakDays }}일
          </span>
        </div>

        <!-- 7-Day Mini Calendar -->
        <div class="grid grid-cols-7 gap-2 text-center mb-4">
          <div
            v-for="day in calendarWeek"
            :key="day.date"
            class="flex flex-col items-center"
          >
            <span class="text-base text-gray-400 mb-1">{{ day.dayLabel }}</span>
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold"
              :class="{
                'bg-green-100 text-green-700': day.checked,
                'bg-red-100 text-red-600': !day.checked && !day.isFuture && !day.isToday,
                'bg-blue-100 text-blue-600 ring-2 ring-blue-400': day.isToday && !day.checked,
                'bg-green-500 text-white ring-2 ring-green-400': day.isToday && day.checked,
                'bg-gray-50 text-gray-300': day.isFuture,
              }"
            >
              {{ day.dayNum }}
            </div>
            <span class="text-sm mt-1">
              <template v-if="day.checked">&#x2705;</template>
              <template v-else-if="day.isFuture">&#x2B1C;</template>
              <template v-else-if="day.isToday">&#x2753;</template>
              <template v-else>&#x274C;</template>
            </span>
          </div>
        </div>

        <!-- Detail List -->
        <div class="space-y-2">
          <div
            v-for="day in recentDays"
            :key="day.date"
            class="flex items-center justify-between bg-gray-50 rounded-xl px-4 py-3"
          >
            <span class="text-lg text-gray-700">{{ day.label }}</span>
            <span v-if="day.checked" class="text-green-600 font-bold text-lg">{{ day.time }}</span>
            <span v-else-if="day.isFuture" class="text-gray-300 text-lg">예정</span>
            <span v-else class="text-red-500 font-bold text-lg">미응답</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const token = localStorage.getItem('sk_token')
const headers = { Authorization: `Bearer ${token}` }

const alreadyChecked = ref(false)
const justCheckedIn = ref(false)
const checkinLoading = ref(false)
const lastCheckinAt = ref(null)
const streakDays = ref(0)
const checkinHistory = ref([])
const loading = ref(true)

const greetingEmoji = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '&#x1F44B;'
  if (h < 18) return '&#x2600;&#xFE0F;'
  return '&#x1F319;'
})

const greetingText = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '좋은 아침이에요!'
  if (h < 18) return '좋은 오후에요!'
  return '좋은 저녁이에요!'
})

const todayDate = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
})

// 7-day mini calendar
const calendarWeek = computed(() => {
  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const dayLabels = ['일','월','화','수','목','금','토']
  const checkedMap = {}
  checkinHistory.value.forEach(h => {
    const dateStr = new Date(h.checked_at || h.created_at).toISOString().slice(0, 10)
    checkedMap[dateStr] = true
  })
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    const isToday = i === 0
    days.push({
      date: dateStr,
      dayNum: d.getDate(),
      dayLabel: dayLabels[d.getDay()],
      checked: !!checkedMap[dateStr],
      isToday,
      isFuture: false,
    })
  }
  return days
})

const recentDays = computed(() => {
  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const checkedMap = {}
  checkinHistory.value.forEach(h => {
    const dateStr = new Date(h.checked_at || h.created_at).toISOString().slice(0, 10)
    const timeStr = new Date(h.checked_at || h.created_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
    checkedMap[dateStr] = timeStr
  })
  for (let i = 0; i < 7; i++) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    const label = i === 0 ? '오늘' : i === 1 ? '어제' : d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', weekday: 'short' })
    days.push({
      date: dateStr,
      label,
      checked: !!checkedMap[dateStr],
      time: checkedMap[dateStr] || '',
      isFuture: false,
    })
  }
  return days
})

function formatTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

async function loadData() {
  try {
    const [settingsRes, historyRes] = await Promise.all([
      axios.get('/api/elder/settings', { headers }),
      axios.get('/api/elder/checkin-history', { headers }),
    ])

    const s = settingsRes.data.settings || settingsRes.data
    lastCheckinAt.value = s.last_checkin_at
    if (s.last_checkin_at) {
      const today = new Date().toISOString().slice(0, 10)
      const last = new Date(s.last_checkin_at).toISOString().slice(0, 10)
      if (today === last) alreadyChecked.value = true
    }

    checkinHistory.value = historyRes.data.data || historyRes.data.logs || historyRes.data || []
    calculateStreak()
  } catch (e) {
    console.error('Failed to load data', e)
  } finally {
    loading.value = false
  }
}

function calculateStreak() {
  const checkedDates = new Set(
    checkinHistory.value.map(h => new Date(h.checked_at || h.created_at).toISOString().slice(0, 10))
  )
  let streak = 0
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  for (let i = 0; i < 365; i++) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const dateStr = d.toISOString().slice(0, 10)
    if (checkedDates.has(dateStr)) {
      streak++
    } else if (i > 0) {
      break
    }
  }
  streakDays.value = streak
}

async function doCheckin() {
  checkinLoading.value = true
  try {
    await axios.post('/api/elder/checkin', {}, { headers })
    justCheckedIn.value = true
    lastCheckinAt.value = new Date().toISOString()

    // Reload history for streak
    try {
      const { data } = await axios.get('/api/elder/checkin-history', { headers })
      checkinHistory.value = data.data || data.logs || data || []
    } catch (_) {}
    calculateStreak()
  } catch (e) {
    if (e.response?.status === 409 || e.response?.data?.message?.includes('already')) {
      alreadyChecked.value = true
    } else {
      alert('체크인에 실패했습니다. 다시 시도해주세요.')
    }
  } finally {
    checkinLoading.value = false
  }
}

onMounted(loadData)
</script>
