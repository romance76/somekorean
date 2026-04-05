<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-3xl mx-auto px-4 py-6">
      <h1 class="text-2xl font-black text-gray-900 mb-5">{{ $t('points.dashboard') }}</h1>

      <!-- Balance Cards -->
      <div class="grid grid-cols-2 gap-3 mb-6">
        <div class="bg-gradient-to-br from-red-500 to-red-600 text-white rounded-2xl p-5 text-center">
          <p class="text-xs opacity-80 mb-1">{{ $t('points.points') }}</p>
          <p class="text-3xl font-black">{{ (balance.points || 0).toLocaleString() }}</p>
          <p class="text-xs opacity-70 mt-1">P</p>
        </div>
        <div class="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl p-5 text-center">
          <p class="text-xs opacity-80 mb-1">{{ $t('points.game_money') }}</p>
          <p class="text-3xl font-black">{{ (balance.cash || 0).toLocaleString() }}</p>
          <p class="text-xs opacity-70 mt-1">G</p>
        </div>
      </div>

      <!-- Daily Spin -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4 text-center">
        <h2 class="font-bold text-gray-800 mb-3">{{ $t('points.daily_spin') }}</h2>
        <div v-if="!spunToday" class="space-y-4">
          <div class="w-40 h-40 mx-auto rounded-full border-8 border-dashed border-yellow-400 flex items-center justify-center relative"
            :class="spinning ? 'animate-spin' : ''"
            @click="doSpin">
            <div class="text-center">
              <p class="text-4xl">🎰</p>
              <p class="text-xs text-gray-500 mt-1">{{ $t('points.tap_to_spin') }}</p>
            </div>
          </div>
          <div v-if="spinResult" class="bg-yellow-50 border border-yellow-200 rounded-xl p-4">
            <p class="text-yellow-800 font-bold text-lg">+{{ spinResult }}P {{ $t('points.earned') }}</p>
          </div>
        </div>
        <div v-else class="py-6">
          <p class="text-green-600 font-bold text-lg mb-1">{{ $t('points.already_spun') }}</p>
          <p class="text-sm text-gray-400">{{ $t('points.come_back_tomorrow') }}</p>
        </div>
      </div>

      <!-- Check-in -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-4">
        <div v-if="!checkedIn" class="flex items-center justify-between">
          <div>
            <p class="font-bold text-gray-800">{{ $t('points.daily_checkin') }}</p>
            <p class="text-xs text-gray-500 mt-0.5">{{ $t('points.checkin_desc') }}</p>
          </div>
          <button @click="doCheckin" :disabled="checkingIn"
            class="bg-yellow-500 text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-yellow-600 disabled:opacity-50 transition">
            {{ checkingIn ? $t('common.processing') : $t('points.checkin_button') }}
          </button>
        </div>
        <div v-else class="text-center text-green-600 font-bold py-2">
          {{ $t('points.checkin_done') }}
        </div>
      </div>

      <!-- Transaction History -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 class="font-bold text-gray-800 text-sm">{{ $t('points.history') }}</h2>
          <router-link to="/point-rules" class="text-xs text-red-600 font-semibold hover:underline">
            {{ $t('points.rules_link') }}
          </router-link>
        </div>
        <div v-if="!transactions.length" class="text-center py-10 text-gray-400 text-sm">{{ $t('points.no_history') }}</div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left px-5 py-2.5 text-xs font-semibold text-gray-500">{{ $t('points.date') }}</th>
              <th class="text-left px-5 py-2.5 text-xs font-semibold text-gray-500">{{ $t('points.type') }}</th>
              <th class="text-right px-5 py-2.5 text-xs font-semibold text-gray-500">{{ $t('points.amount') }}</th>
              <th class="text-left px-5 py-2.5 text-xs font-semibold text-gray-500 hidden sm:table-cell">{{ $t('points.reason') }}</th>
              <th class="text-right px-5 py-2.5 text-xs font-semibold text-gray-500 hidden sm:table-cell">{{ $t('points.balance') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="t in transactions" :key="t.id" class="hover:bg-gray-50 transition">
              <td class="px-5 py-3 text-gray-600">{{ formatDate(t.created_at) }}</td>
              <td class="px-5 py-3">
                <span class="text-xs font-semibold px-2 py-0.5 rounded-full"
                  :class="t.amount > 0 ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'">
                  {{ t.type || (t.amount > 0 ? $t('points.earn') : $t('points.spend')) }}
                </span>
              </td>
              <td class="px-5 py-3 text-right font-bold" :class="t.amount > 0 ? 'text-green-600' : 'text-red-600'">
                {{ t.amount > 0 ? '+' : '' }}{{ t.amount?.toLocaleString() }}P
              </td>
              <td class="px-5 py-3 text-gray-500 hidden sm:table-cell">{{ t.reason || t.description }}</td>
              <td class="px-5 py-3 text-right text-gray-600 hidden sm:table-cell">{{ t.balance?.toLocaleString() }}P</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const auth = useAuthStore()
const { $t } = useLangStore()

const balance = ref({ points: 0, cash: 0, level: '' })
const transactions = ref([])
const checkedIn = ref(false)
const checkingIn = ref(false)
const spunToday = ref(false)
const spinning = ref(false)
const spinResult = ref(null)

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}

async function loadData() {
  try {
    const [balRes, txRes] = await Promise.all([
      axios.get('/api/points/balance'),
      axios.get('/api/points/history'),
    ])
    balance.value = balRes.data
    transactions.value = txRes.data.data || txRes.data || []
    checkedIn.value = balRes.data.checked_in_today || false
    spunToday.value = balRes.data.spun_today || false
  } catch { /* ignore */ }
}

async function doCheckin() {
  checkingIn.value = true
  try {
    await axios.post('/api/points/checkin')
    checkedIn.value = true
    auth.refreshPoints()
    await loadData()
  } catch (e) {
    alert(e.response?.data?.message || $t('points.checkin_failed'))
  } finally {
    checkingIn.value = false
  }
}

async function doSpin() {
  if (spinning.value || spunToday.value) return
  spinning.value = true
  spinResult.value = null
  try {
    const { data } = await axios.post('/api/points/spin')
    setTimeout(() => {
      spinning.value = false
      spinResult.value = data.points || data.amount || 0
      spunToday.value = true
      auth.refreshPoints()
      loadData()
    }, 2000)
  } catch (e) {
    spinning.value = false
    alert(e.response?.data?.message || $t('points.spin_failed'))
  }
}

onMounted(loadData)
</script>
