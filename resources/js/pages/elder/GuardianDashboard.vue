<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="max-w-3xl mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-indigo-600 to-indigo-800 text-white px-6 py-6 rounded-2xl">
        <router-link to="/elder" class="text-indigo-200 hover:text-white text-base flex items-center gap-1 mb-3">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          {{ $t('common.back') }}
        </router-link>
        <h1 class="text-2xl font-black">{{ $t('elder.guardian_dashboard') }}</h1>
        <p class="text-indigo-200 text-lg mt-1">{{ $t('elder.guardian_subtitle') }}</p>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 mt-6 space-y-5">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-12">
        <svg class="w-8 h-8 animate-spin mx-auto mb-3 text-indigo-400" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <p class="text-gray-500 text-lg">{{ $t('common.loading') }}</p>
      </div>

      <template v-else>
        <!-- SOS Alert Banner -->
        <div v-if="activeSOSAlert" class="bg-red-600 text-white rounded-2xl shadow-lg p-6 text-center animate-pulse">
          <p class="text-4xl mb-2">🚨</p>
          <h2 class="text-2xl font-bold mb-2">{{ $t('elder.sos_alert') }}</h2>
          <p class="text-xl mb-1">{{ activeSOSAlert.elder_name }}{{ $t('elder.sent_sos') }}</p>
          <p class="text-lg opacity-80">{{ formatTime(activeSOSAlert.created_at) }}</p>
          <button @click="acknowledgeAlert(activeSOSAlert.id)"
            class="mt-4 bg-white text-red-600 px-6 py-3 rounded-xl font-bold text-lg hover:bg-red-50 transition">
            {{ $t('elder.acknowledge') }}
          </button>
        </div>

        <!-- Ward List -->
        <div class="bg-white rounded-2xl shadow-md overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h2 class="text-lg font-bold text-gray-800">{{ $t('elder.wards') }}</h2>
          </div>
          <div v-if="!wards.length" class="text-center py-10 text-gray-400 text-lg">
            {{ $t('elder.no_wards') }}
          </div>
          <div v-else>
            <div v-for="ward in wards" :key="ward.id"
              class="px-6 py-4 border-b border-gray-50 last:border-0 flex items-center gap-4">
              <div class="w-14 h-14 rounded-full flex-shrink-0 flex items-center justify-center text-2xl font-bold"
                :class="ward.checked_in_today ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'">
                {{ (ward.name || '?')[0] }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-bold text-gray-800 text-lg">{{ ward.name }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-sm font-semibold px-2 py-0.5 rounded-full"
                    :class="ward.checked_in_today ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'">
                    {{ ward.checked_in_today ? $t('elder.checked_in') : $t('elder.not_checked_in') }}
                  </span>
                  <span class="text-sm text-gray-400">{{ $t('elder.last_checkin') }}: {{ formatTime(ward.last_checkin) || $t('elder.none') }}</span>
                </div>
              </div>
              <!-- Alert badge -->
              <div v-if="!ward.checked_in_today && isLateCheckin(ward)"
                class="bg-red-500 text-white text-xs font-bold px-3 py-1.5 rounded-full animate-pulse flex-shrink-0">
                {{ $t('elder.missed') }}
              </div>
            </div>
          </div>
        </div>

        <!-- SOS Log -->
        <div class="bg-white rounded-2xl shadow-md overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100">
            <h2 class="text-lg font-bold text-gray-800">{{ $t('elder.sos_log') }}</h2>
          </div>
          <div v-if="!sosLogs.length" class="text-center py-10 text-gray-400 text-lg">
            {{ $t('elder.no_sos') }}
          </div>
          <div v-else>
            <div v-for="sos in sosLogs" :key="sos.id"
              class="px-6 py-4 border-b border-gray-50 last:border-0 flex items-center gap-4">
              <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
                :class="sos.acknowledged ? 'bg-gray-100 text-gray-500' : 'bg-red-100 text-red-600'">
                🚨
              </div>
              <div class="flex-1">
                <p class="font-semibold text-gray-800">{{ sos.elder_name }}</p>
                <p class="text-sm text-gray-500">{{ formatTime(sos.created_at) }}</p>
              </div>
              <span class="text-xs font-semibold px-2 py-1 rounded-full"
                :class="sos.acknowledged ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'">
                {{ sos.acknowledged ? $t('elder.resolved') : $t('elder.active') }}
              </span>
            </div>
          </div>
        </div>

        <!-- Ward Health Info -->
        <div v-for="ward in wards" :key="'health-'+ward.id" class="bg-white rounded-2xl shadow-md p-6">
          <h3 class="text-lg font-bold text-gray-800 mb-3">{{ ward.name }} - {{ $t('elder.health_info') }}</h3>
          <div class="space-y-2">
            <div v-if="ward.health_note" class="bg-blue-50 rounded-xl p-4">
              <p class="text-sm text-blue-800">{{ ward.health_note }}</p>
            </div>
            <div v-if="ward.medications?.length" class="space-y-1.5">
              <p class="text-sm font-semibold text-gray-600">{{ $t('elder.medication') }}:</p>
              <div v-for="med in ward.medications" :key="med.id" class="text-sm text-gray-600 flex items-center gap-2">
                <span :class="med.taken ? 'text-green-500' : 'text-gray-300'">{{ med.taken ? '✅' : '⬜' }}</span>
                {{ med.name }} ({{ med.time }})
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const { $t } = useLangStore()

const loading = ref(true)
const wards = ref([])
const sosLogs = ref([])
const activeSOSAlert = ref(null)

function formatTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function isLateCheckin(ward) {
  if (ward.checked_in_today) return false
  const now = new Date()
  return now.getHours() >= 12
}

async function loadData() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/elder/guardian/dashboard')
    wards.value = data.wards || []
    sosLogs.value = data.sos_logs || []
    activeSOSAlert.value = data.active_sos || null
  } catch { /* ignore */ }
  loading.value = false
}

async function acknowledgeAlert(id) {
  try {
    await axios.post(`/api/elder/sos/${id}/acknowledge`)
    activeSOSAlert.value = null
    await loadData()
  } catch { /* ignore */ }
}

onMounted(loadData)
</script>
