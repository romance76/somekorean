<template>
  <div class="min-h-screen bg-gradient-to-b from-green-50 to-white flex flex-col">
    <!-- Header -->
    <div class="bg-white shadow-sm px-4 py-4">
      <router-link to="/elder" class="text-blue-500 text-lg font-medium flex items-center gap-1">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        {{ $t('common.back') }}
      </router-link>
    </div>

    <div class="flex-1 flex flex-col items-center justify-center px-6 py-8 max-w-lg mx-auto w-full">
      <!-- Greeting -->
      <p class="text-5xl mb-4">{{ greetingEmoji }}</p>
      <h1 class="text-2xl font-bold text-gray-800 mb-2">{{ greetingText }}</h1>
      <p class="text-xl text-gray-500 mb-8">{{ todayDate }}</p>

      <!-- Already checked in -->
      <div v-if="alreadyChecked" class="text-center mb-8">
        <div class="text-7xl mb-4">🎉</div>
        <p class="text-2xl font-bold text-green-600 mb-2">{{ $t('elder.checkin_complete') }}</p>
        <p class="text-lg text-gray-500">{{ lastCheckinTime }} {{ $t('elder.checked_at') }}</p>
        <div v-if="streakDays > 1" class="mt-4 bg-orange-50 rounded-2xl px-6 py-3 inline-block">
          <span class="text-xl font-bold text-orange-600">{{ $t('elder.streak') }} {{ streakDays }}{{ $t('elder.days') }}!</span>
        </div>
      </div>

      <!-- Just checked in success -->
      <div v-else-if="justCheckedIn" class="text-center mb-8">
        <div class="text-7xl mb-4 animate-bounce">✅</div>
        <p class="text-2xl font-bold text-green-600 mb-2">{{ $t('elder.checkin_success') }}</p>
        <p class="text-lg text-gray-500">+5P {{ $t('elder.points_earned') }}</p>
      </div>

      <!-- Checkin Button -->
      <div v-else class="text-center w-full">
        <button @click="doCheckin" :disabled="checking"
          class="w-48 h-48 mx-auto rounded-full bg-green-500 hover:bg-green-600 active:scale-95 text-white flex flex-col items-center justify-center shadow-2xl transition-all disabled:opacity-50">
          <span class="text-5xl mb-2">👋</span>
          <span class="text-2xl font-black">{{ checking ? $t('common.processing') : $t('elder.checkin') }}</span>
        </button>
        <p class="text-lg text-gray-400 mt-6">{{ $t('elder.tap_to_checkin') }}</p>
      </div>

      <!-- Calendar View -->
      <div class="w-full mt-8 bg-white rounded-2xl shadow-md p-5">
        <h2 class="text-lg font-bold text-gray-800 mb-4 text-center">{{ $t('elder.checkin_history') }}</h2>
        <div class="grid grid-cols-7 gap-1 text-center">
          <div v-for="day in ['일','월','화','수','목','금','토']" :key="day" class="text-xs font-bold text-gray-400 py-1">{{ day }}</div>
          <div v-for="(day, idx) in calendarDays" :key="idx"
            class="aspect-square flex items-center justify-center rounded-lg text-sm font-medium"
            :class="dayClass(day)">
            {{ day?.date || '' }}
          </div>
        </div>
      </div>

      <!-- Streak Display -->
      <div v-if="streakDays > 0" class="w-full mt-4 bg-orange-50 rounded-2xl p-5 text-center">
        <p class="text-3xl font-black text-orange-600">🔥 {{ streakDays }}</p>
        <p class="text-lg text-orange-700 mt-1">{{ $t('elder.consecutive_days') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const auth = useAuthStore()
const { $t } = useLangStore()

const alreadyChecked = ref(false)
const justCheckedIn = ref(false)
const checking = ref(false)
const streakDays = ref(0)
const lastCheckinTime = ref('')
const checkinDates = ref([])

const todayDate = computed(() =>
  new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })
)

const greetingEmoji = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return '🌅'
  if (h < 18) return '☀️'
  return '🌙'
})

const greetingText = computed(() => {
  const h = new Date().getHours()
  const name = auth.user?.name || $t('elder.member')
  if (h < 12) return `${$t('elder.good_morning')}, ${name}${$t('elder.greeting_suffix')}`
  if (h < 18) return `${$t('elder.good_afternoon')}, ${name}${$t('elder.greeting_suffix')}`
  return `${$t('elder.good_evening')}, ${name}${$t('elder.greeting_suffix')}`
})

const calendarDays = computed(() => {
  const now = new Date()
  const year = now.getFullYear()
  const month = now.getMonth()
  const firstDay = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const days = []
  for (let i = 0; i < firstDay; i++) days.push(null)
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`
    days.push({ date: d, checked: checkinDates.value.includes(dateStr), isToday: d === now.getDate() })
  }
  return days
})

function dayClass(day) {
  if (!day) return ''
  if (day.checked) return 'bg-green-500 text-white'
  if (day.isToday) return 'bg-blue-100 text-blue-600 font-bold'
  return 'text-gray-600'
}

async function loadStatus() {
  try {
    const { data } = await axios.get('/api/elder/checkin/status')
    alreadyChecked.value = data.checked_in_today || false
    streakDays.value = data.streak || 0
    lastCheckinTime.value = data.last_checkin ? new Date(data.last_checkin).toLocaleTimeString('ko-KR') : ''
    checkinDates.value = data.dates || []
  } catch { /* ignore */ }
}

async function doCheckin() {
  checking.value = true
  try {
    const { data } = await axios.post('/api/elder/checkin')
    justCheckedIn.value = true
    streakDays.value = data.streak || streakDays.value + 1
    auth.refreshPoints()
    setTimeout(() => { alreadyChecked.value = true }, 2000)
  } catch (e) {
    if (e.response?.status === 409) alreadyChecked.value = true
    else alert(e.response?.data?.message || $t('elder.checkin_failed'))
  } finally {
    checking.value = false
  }
}

onMounted(loadStatus)
</script>
