<template>
<div>
  <h1 class="text-xl font-bold text-gray-800 mb-6">&spades;&xFE0F; &#54252;&#52964; &#44288;&#47532;</h1>

  <!-- Overview Cards -->
  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mb-6">
    <div v-for="s in overviewCards" :key="s.label" class="bg-white rounded-xl p-4 border shadow-sm">
      <div class="text-gray-400 text-xs mb-1">{{ s.label }}</div>
      <div class="text-lg font-bold" :class="s.color">{{ s.value }}</div>
    </div>
  </div>

  <!-- Wallet Management -->
  <div class="bg-white rounded-xl border shadow-sm mb-6">
    <div class="p-4 border-b flex justify-between items-center">
      <h2 class="font-bold text-gray-800">&#128176; &#51648;&#44049; &#44288;&#47532;</h2>
      <div class="text-xs text-gray-400">&#52509; {{ wallets.length }}&#44148;</div>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-gray-500 text-xs">
            <th class="px-4 py-2 text-left">&#50976;&#51200;</th>
            <th class="px-4 py-2 text-left">&#51060;&#47700;&#51068;</th>
            <th class="px-4 py-2 text-right">&#52841; &#51092;&#44256;</th>
            <th class="px-4 py-2 text-right">&#52509; &#51077;&#44552;</th>
            <th class="px-4 py-2 text-right">&#52509; &#52636;&#44552;</th>
            <th class="px-4 py-2 text-center">&#51312;&#51221;</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="w in wallets" :key="w.id" class="border-t hover:bg-gray-50">
            <td class="px-4 py-2 font-semibold text-gray-800">{{ w.user?.name || w.user?.nickname || '?' }}</td>
            <td class="px-4 py-2 text-gray-400 text-xs">{{ w.user?.email || '-' }}</td>
            <td class="px-4 py-2 text-right font-mono font-bold text-amber-600">{{ (w.chips_balance || 0).toLocaleString() }}</td>
            <td class="px-4 py-2 text-right font-mono text-emerald-600">{{ (w.total_deposited || 0).toLocaleString() }}</td>
            <td class="px-4 py-2 text-right font-mono text-red-500">{{ (w.total_withdrawn || 0).toLocaleString() }}</td>
            <td class="px-4 py-2 text-center">
              <button @click="openAdjust(w)" class="text-xs text-blue-600 hover:underline font-bold">&#51312;&#51221;</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="wallets.length === 0" class="p-8 text-center text-gray-400 text-sm">&#51648;&#44049; &#45936;&#51060;&#53552;&#44032; &#50630;&#49845;&#45768;&#45796;.</div>
  </div>

  <!-- Settings -->
  <div class="bg-white rounded-xl border shadow-sm">
    <div class="p-4 border-b"><h2 class="font-bold text-gray-800">&#9881;&#65039; &#54252;&#52964; &#49444;&#51221;</h2></div>
    <div class="p-4 space-y-4 max-w-lg">
      <div v-for="f in settingsFields" :key="f.key" class="flex items-center justify-between">
        <label class="text-sm text-gray-600">{{ f.label }}</label>
        <input v-if="f.type === 'number'" v-model.number="settings[f.key]" type="number"
          class="w-32 border rounded px-3 py-1.5 text-sm text-right focus:border-amber-400 focus:outline-none" />
        <label v-else class="relative inline-flex items-center cursor-pointer">
          <input v-model="settings[f.key]" type="checkbox" class="sr-only peer">
          <div class="w-9 h-5 bg-gray-200 peer-checked:bg-amber-500 rounded-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-full"></div>
        </label>
      </div>
      <div class="pt-2">
        <button @click="saveSettings" :disabled="saving"
          class="bg-amber-500 hover:bg-amber-400 disabled:bg-gray-300 text-white px-6 py-2 rounded-lg text-sm font-bold transition">
          {{ saving ? '&#51200;&#51109; &#51473;...' : '&#49444;&#51221; &#51200;&#51109;' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Adjust Modal -->
  <div v-if="adjustWallet" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="adjustWallet = null">
    <div class="bg-white rounded-xl p-6 w-80 shadow-xl">
      <h3 class="font-bold text-gray-800 mb-4">&#52841; &#51092;&#44256; &#51312;&#51221;</h3>
      <div class="text-sm text-gray-500 mb-1">{{ adjustWallet.user?.name || '?' }}</div>
      <div class="text-xs text-gray-400 mb-3">&#54788;&#51116; &#51092;&#44256;: <span class="font-bold text-amber-600">{{ (adjustWallet.chips_balance || 0).toLocaleString() }}</span></div>
      <input v-model.number="adjustAmount" type="number"
        class="w-full border rounded px-3 py-2 mb-2 text-sm focus:border-amber-400 focus:outline-none"
        placeholder="&#49352; &#51091;&#44256; &#51077;&#47141;" />
      <div class="text-xs text-gray-400 mb-4">
        &#52264;&#51060;: <span :class="adjustAmount - (adjustWallet.chips_balance || 0) >= 0 ? 'text-emerald-500' : 'text-red-500'" class="font-bold">
          {{ adjustAmount - (adjustWallet.chips_balance || 0) >= 0 ? '+' : '' }}{{ (adjustAmount - (adjustWallet.chips_balance || 0)).toLocaleString() }}
        </span>
      </div>
      <div class="flex gap-2">
        <button @click="submitAdjust" :disabled="adjusting"
          class="flex-1 bg-amber-500 hover:bg-amber-400 disabled:bg-gray-300 text-white py-2 rounded-lg font-bold text-sm transition">
          {{ adjusting ? '&#52376;&#47532; &#51473;...' : '&#51200;&#51109;' }}
        </button>
        <button @click="adjustWallet = null" class="flex-1 bg-gray-200 text-gray-600 py-2 rounded-lg font-bold text-sm hover:bg-gray-300 transition">&#52712;&#49548;</button>
      </div>
      <div v-if="adjustError" class="text-xs text-red-500 mt-2 text-center">{{ adjustError }}</div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const overview = ref({})
const wallets = ref([])
const settings = ref({
  min_deposit: 1000,
  min_withdraw: 1000,
  withdraw_fee_pct: 5,
  max_buy_in: 10000,
  enabled: true,
})
const saving = ref(false)
const adjustWallet = ref(null)
const adjustAmount = ref(0)
const adjusting = ref(false)
const adjustError = ref('')

const overviewCards = computed(() => [
  { label: '\uCD1D \uAC8C\uC784', value: (overview.value.total_games || 0).toLocaleString(), color: 'text-blue-600' },
  { label: '\uCD1D \uC9C0\uAC11', value: (overview.value.total_wallets || 0).toLocaleString(), color: 'text-gray-800' },
  { label: '\uCD1D \uC785\uAE08', value: (overview.value.total_deposited || 0).toLocaleString(), color: 'text-emerald-600' },
  { label: '\uCD1D \uCD9C\uAE08', value: (overview.value.total_withdrawn || 0).toLocaleString(), color: 'text-red-500' },
  { label: '\uC720\uD1B5 \uCE69', value: (overview.value.chips_in_circulation || 0).toLocaleString(), color: 'text-amber-600' },
  { label: '\uD65C\uC131 \uC720\uC800', value: (overview.value.active_players || 0).toLocaleString(), color: 'text-purple-600' },
])

const settingsFields = [
  { key: 'min_deposit', label: '\uCD5C\uC18C \uC785\uAE08', type: 'number' },
  { key: 'min_withdraw', label: '\uCD5C\uC18C \uCD9C\uAE08', type: 'number' },
  { key: 'withdraw_fee_pct', label: '\uCD9C\uAE08 \uC218\uC218\uB8CC (%)', type: 'number' },
  { key: 'max_buy_in', label: '\uCD5C\uB300 \uBC14\uC774\uC778', type: 'number' },
  { key: 'enabled', label: '\uD3EC\uCEE4 \uD65C\uC131\uD654', type: 'toggle' },
]

onMounted(async () => {
  try {
    const [ov, wl, st] = await Promise.all([
      axios.get('/api/admin/poker/overview'),
      axios.get('/api/admin/poker/wallets'),
      axios.get('/api/admin/poker/settings'),
    ])
    if (ov.data.success) overview.value = ov.data.data
    if (wl.data.success) wallets.value = wl.data.data?.data || wl.data.data || []
    if (st.data.success) Object.assign(settings.value, st.data.data)
  } catch (e) {
    console.error('Admin poker load failed', e)
  }
})

function openAdjust(w) {
  adjustWallet.value = w
  adjustAmount.value = w.chips_balance || 0
  adjustError.value = ''
}

async function submitAdjust() {
  adjusting.value = true
  adjustError.value = ''
  try {
    await axios.put(`/api/admin/poker/wallets/${adjustWallet.value.id}`, { chips_balance: adjustAmount.value })
    adjustWallet.value.chips_balance = adjustAmount.value
    adjustWallet.value = null
  } catch (e) {
    adjustError.value = e.response?.data?.message || e.message
  } finally {
    adjusting.value = false
  }
}

async function saveSettings() {
  saving.value = true
  try {
    await axios.put('/api/admin/poker/settings', settings.value)
    alert('\uC124\uC815\uC774 \uC800\uC7A5\uB418\uC5C8\uC2B5\uB2C8\uB2E4.')
  } catch (e) {
    alert('\uC800\uC7A5 \uC2E4\uD328: ' + (e.response?.data?.message || e.message))
  } finally {
    saving.value = false
  }
}
</script>
