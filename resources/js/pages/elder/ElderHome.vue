<template>
  <div class="min-h-screen bg-gray-50 pb-24">
    <div class="max-w-2xl mx-auto px-4 pt-4">
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-600 to-blue-800 text-white px-6 py-6 rounded-2xl shadow-lg">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-black">{{ $t('elder.title') }}</h1>
            <p class="text-lg opacity-80 mt-1">{{ $t('elder.subtitle') }}</p>
          </div>
          <button @click="showSettings = true"
            class="bg-white/20 hover:bg-white/30 rounded-xl px-4 py-2 text-lg font-bold transition">
            {{ $t('elder.settings') }}
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-2xl mx-auto px-4 mt-6 space-y-5">
      <!-- Greeting -->
      <div class="bg-white rounded-2xl shadow-md p-6 text-center">
        <p class="text-3xl font-bold text-gray-800 mb-2">
          {{ $t('elder.greeting') }}, {{ auth.user?.name || auth.user?.nickname || $t('elder.member') }}{{ $t('elder.greeting_suffix') }}
        </p>
        <p class="text-xl text-gray-500">{{ currentDateTime }}</p>
      </div>

      <!-- Check-in Button -->
      <div class="bg-white rounded-2xl shadow-md p-6 text-center">
        <div v-if="todayCheckedIn" class="mb-3">
          <p class="text-green-600 font-bold text-xl mb-1">{{ $t('elder.checked_in') }}</p>
          <p class="text-lg text-gray-500">{{ lastCheckinTime }}</p>
        </div>
        <router-link to="/elder/checkin"
          class="block w-full text-center font-bold text-2xl py-6 rounded-2xl transition shadow-md"
          :class="todayCheckedIn
            ? 'bg-green-100 text-green-700 hover:bg-green-200'
            : 'bg-green-500 hover:bg-green-600 text-white'">
          {{ todayCheckedIn ? $t('elder.safe_today') : $t('elder.go_checkin') }}
        </router-link>
        <p v-if="!todayCheckedIn" class="text-lg text-gray-400 mt-3">{{ $t('elder.checkin_reward') }}</p>
      </div>

      <!-- SOS Button -->
      <div class="bg-white rounded-2xl shadow-md p-6 text-center">
        <button @click="sendSOS" :disabled="sosLoading"
          class="w-full bg-red-600 hover:bg-red-700 text-white text-2xl font-black py-6 rounded-2xl shadow-lg transition disabled:opacity-50">
          {{ sosLoading ? $t('elder.sending_sos') : $t('elder.sos_button') }}
        </button>
        <p class="text-lg text-gray-400 mt-3">{{ $t('elder.sos_desc') }}</p>
      </div>

      <!-- Medication Reminders -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">{{ $t('elder.medication') }}</h2>
        <div v-if="!medications.length" class="text-center py-6 text-gray-400 text-lg">
          {{ $t('elder.no_medication') }}
        </div>
        <div v-else class="space-y-3">
          <div v-for="med in medications" :key="med.id"
            class="flex items-center gap-4 p-4 rounded-xl border-2"
            :class="med.taken ? 'border-green-200 bg-green-50' : 'border-gray-200'">
            <button @click="toggleMed(med)"
              class="w-8 h-8 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition text-lg"
              :class="med.taken ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300'">
              <svg v-if="med.taken" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </button>
            <div class="flex-1">
              <p class="font-bold text-gray-800 text-lg">{{ med.name }}</p>
              <p class="text-gray-500">{{ med.time }} · {{ med.dosage }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Health Notes -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">{{ $t('elder.health_notes') }}</h2>
        <textarea v-model="healthNote" rows="4" :placeholder="$t('elder.health_notes_placeholder')"
          class="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-lg focus:outline-none focus:border-blue-400 resize-none transition" />
        <button @click="saveHealthNote" :disabled="savingNote"
          class="mt-3 bg-blue-600 text-white px-6 py-3 rounded-xl text-lg font-bold hover:bg-blue-700 disabled:opacity-50 transition">
          {{ savingNote ? $t('common.saving') : $t('common.save') }}
        </button>
      </div>

      <!-- Guardian Info -->
      <div class="bg-white rounded-2xl shadow-md p-6">
        <h2 class="text-xl font-bold text-gray-800 mb-4">{{ $t('elder.guardian_info') }}</h2>
        <div v-if="guardian" class="flex items-center gap-4">
          <div class="w-14 h-14 rounded-full bg-blue-100 flex items-center justify-center text-2xl font-bold text-blue-600">
            {{ (guardian.name || '?')[0] }}
          </div>
          <div>
            <p class="font-bold text-gray-800 text-lg">{{ guardian.name }}</p>
            <p class="text-gray-500">{{ guardian.phone }}</p>
            <p class="text-gray-400 text-sm">{{ guardian.relationship }}</p>
          </div>
        </div>
        <div v-else class="text-center py-6 text-gray-400 text-lg">
          {{ $t('elder.no_guardian') }}
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettings" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showSettings = false">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-gray-800 text-xl mb-4">{{ $t('elder.settings') }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-lg font-medium text-gray-700 mb-1">{{ $t('elder.checkin_time') }}</label>
            <input v-model="settingsForm.checkin_time" type="time"
              class="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-lg focus:outline-none focus:border-blue-400 transition" />
          </div>
          <div>
            <label class="block text-lg font-medium text-gray-700 mb-1">{{ $t('elder.guardian_phone') }}</label>
            <input v-model="settingsForm.guardian_phone" type="tel" placeholder="010-1234-5678"
              class="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-lg focus:outline-none focus:border-blue-400 transition" />
          </div>
        </div>
        <div class="flex gap-3 mt-6">
          <button @click="showSettings = false" class="flex-1 py-3 border-2 border-gray-200 rounded-xl text-lg font-bold text-gray-600 hover:bg-gray-50 transition">
            {{ $t('common.cancel') }}
          </button>
          <button @click="saveSettings" class="flex-1 py-3 bg-blue-600 text-white rounded-xl text-lg font-bold hover:bg-blue-700 transition">
            {{ $t('common.save') }}
          </button>
        </div>
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

const todayCheckedIn = ref(false)
const lastCheckinTime = ref('')
const medications = ref([])
const healthNote = ref('')
const savingNote = ref(false)
const guardian = ref(null)
const sosLoading = ref(false)
const showSettings = ref(false)
const settingsForm = ref({ checkin_time: '09:00', guardian_phone: '' })

const currentDateTime = computed(() => {
  return new Date().toLocaleDateString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'long',
  })
})

async function loadData() {
  try {
    const { data } = await axios.get('/api/elder/status')
    todayCheckedIn.value = data.checked_in_today || false
    lastCheckinTime.value = data.last_checkin ? new Date(data.last_checkin).toLocaleTimeString('ko-KR') : ''
    medications.value = data.medications || []
    healthNote.value = data.health_note || ''
    guardian.value = data.guardian || null
    if (data.settings) {
      settingsForm.value = { ...settingsForm.value, ...data.settings }
    }
  } catch { /* ignore */ }
}

async function sendSOS() {
  if (!confirm($t('elder.sos_confirm'))) return
  sosLoading.value = true
  try {
    await axios.post('/api/elder/sos')
    alert($t('elder.sos_sent'))
  } catch (e) {
    alert(e.response?.data?.message || $t('elder.sos_failed'))
  } finally {
    sosLoading.value = false
  }
}

async function toggleMed(med) {
  try {
    await axios.post(`/api/elder/medications/${med.id}/toggle`)
    med.taken = !med.taken
  } catch { /* ignore */ }
}

async function saveHealthNote() {
  savingNote.value = true
  try {
    await axios.post('/api/elder/health-note', { note: healthNote.value })
  } catch { /* ignore */ }
  savingNote.value = false
}

async function saveSettings() {
  try {
    await axios.put('/api/elder/settings', settingsForm.value)
    showSettings.value = false
  } catch (e) {
    alert(e.response?.data?.message || $t('common.save_failed'))
  }
}

onMounted(loadData)
</script>
