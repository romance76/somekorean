<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-black text-gray-800">💰 지갑 관리</h1>
      <div class="text-sm text-gray-400">게임 화폐 현황</div>
    </div>

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-pink-50 rounded-2xl p-4 border border-pink-100">
        <div class="text-2xl font-black text-pink-600">{{ stats.total_star?.toLocaleString() || 0 }}</div>
        <div class="text-sm text-pink-400 mt-1">⭐ 총 STAR 발행</div>
      </div>
      <div class="bg-blue-50 rounded-2xl p-4 border border-blue-100">
        <div class="text-2xl font-black text-blue-600">{{ stats.total_gem?.toLocaleString() || 0 }}</div>
        <div class="text-sm text-blue-400 mt-1">💎 총 GEM 발행</div>
      </div>
      <div class="bg-yellow-50 rounded-2xl p-4 border border-yellow-100">
        <div class="text-2xl font-black text-yellow-600">{{ stats.total_coin?.toLocaleString() || 0 }}</div>
        <div class="text-sm text-yellow-500 mt-1">🪙 총 COIN 유통</div>
      </div>
      <div class="bg-purple-50 rounded-2xl p-4 border border-purple-100">
        <div class="text-2xl font-black text-purple-600">{{ stats.total_wallets || 0 }}</div>
        <div class="text-sm text-purple-400 mt-1">👛 지갑 보유 유저</div>
      </div>
    </div>

    <!-- 탭 -->
    <div class="flex gap-2 mb-4">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        class="px-4 py-2 rounded-xl text-sm font-semibold transition"
        :class="activeTab === tab.key ? 'bg-indigo-500 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'">
        {{ tab.label }}
      </button>
    </div>

    <!-- 유저 지갑 목록 -->
    <div v-if="activeTab === 'wallets'" class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 flex items-center gap-3">
        <input v-model="walletSearch" type="text" placeholder="유저 검색..."
          class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-indigo-400 w-48" />
        <span class="text-sm text-gray-400">총 {{ wallets.length }}개</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left px-5 py-3 text-gray-500 font-medium">유저</th>
              <th class="text-right px-4 py-3 text-pink-400">⭐ STAR</th>
              <th class="text-right px-4 py-3 text-blue-400">💎 GEM</th>
              <th class="text-right px-4 py-3 text-yellow-500">🪙 COIN</th>
              <th class="text-right px-4 py-3 text-purple-400">🎰 CHIP</th>
              <th class="text-right px-4 py-3 text-gray-400">총 획득</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="w in filteredWallets" :key="w.user_id" class="hover:bg-gray-50">
              <td class="px-5 py-3 font-medium text-gray-800">{{ w.nickname || w.username || w.user_id }}</td>
              <td class="text-right px-4 py-3 text-gray-600">{{ w.star_balance?.toLocaleString() || 0 }}</td>
              <td class="text-right px-4 py-3 text-gray-600">{{ w.gem_balance?.toLocaleString() || 0 }}</td>
              <td class="text-right px-4 py-3 font-semibold text-yellow-600">{{ w.coin_balance?.toLocaleString() || 0 }}</td>
              <td class="text-right px-4 py-3 text-gray-600">{{ w.chip_balance?.toLocaleString() || 0 }}</td>
              <td class="text-right px-4 py-3 text-gray-400">{{ w.lifetime_earned?.toLocaleString() || 0 }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 최근 거래 -->
    <div v-if="activeTab === 'transactions'" class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="text-left px-5 py-3 text-gray-500 font-medium">유저</th>
              <th class="text-left px-4 py-3 text-gray-500">타입</th>
              <th class="text-right px-4 py-3 text-gray-500">금액</th>
              <th class="text-left px-4 py-3 text-gray-500">설명</th>
              <th class="text-right px-4 py-3 text-gray-500">시간</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="tx in transactions" :key="tx.id" class="hover:bg-gray-50">
              <td class="px-5 py-3 text-gray-700">{{ tx.user_id }}</td>
              <td class="px-4 py-3">
                <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="txTypeClass(tx.type)">{{ tx.type }}</span>
              </td>
              <td class="text-right px-4 py-3 font-semibold" :class="tx.amount > 0 ? 'text-green-600' : 'text-red-500'">
                {{ tx.amount > 0 ? '+' : '' }}{{ tx.amount }} {{ currencyIcon(tx.currency) }}
              </td>
              <td class="px-4 py-3 text-gray-400 text-xs">{{ tx.description }}</td>
              <td class="text-right px-4 py-3 text-xs text-gray-400">{{ formatDate(tx.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 게임 카테고리 관리 -->
    <div v-if="activeTab === 'games'" class="bg-white rounded-2xl shadow-sm overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100">
        <h3 class="font-bold text-gray-700">연령별 게임 카테고리</h3>
      </div>
      <div class="p-5 space-y-4">
        <div v-for="cat in gameCategories" :key="cat.id" class="border border-gray-100 rounded-xl p-4">
          <div class="flex items-center gap-3 mb-3">
            <span class="text-2xl">{{ cat.icon }}</span>
            <div>
              <h4 class="font-bold text-gray-800">{{ cat.name }}</h4>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                :class="ageGroupClass(cat.age_group)">{{ cat.age_group }}</span>
            </div>
            <div class="ml-auto">
              <span class="text-sm text-gray-400">{{ cat.games?.length || 0 }}개 게임</span>
            </div>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <div v-for="game in cat.games" :key="game.id"
              class="flex items-center gap-2 p-2 bg-gray-50 rounded-lg text-xs">
              <span :class="game.is_active ? 'text-green-400' : 'text-gray-300'">●</span>
              <span class="font-medium text-gray-700 truncate">{{ game.name }}</span>
              <span class="ml-auto text-gray-400">{{ game.type }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const activeTab = ref('wallets')
const tabs = [
  { key: 'wallets', label: '💰 유저 지갑' },
  { key: 'transactions', label: '📋 최근 거래' },
  { key: 'games', label: '🎮 게임 관리' },
]
const stats = ref({})
const wallets = ref([])
const transactions = ref([])
const gameCategories = ref([])
const walletSearch = ref('')

const filteredWallets = computed(() => {
  if (!walletSearch.value) return wallets.value
  const q = walletSearch.value.toLowerCase()
  return wallets.value.filter(w =>
    (w.username || '').toLowerCase().includes(q) ||
    (w.nickname || '').toLowerCase().includes(q) ||
    String(w.user_id).includes(q)
  )
})

function txTypeClass(t) {
  return {
    earn: 'bg-green-100 text-green-700',
    spend: 'bg-red-100 text-red-600',
    bonus: 'bg-yellow-100 text-yellow-700',
    daily: 'bg-blue-100 text-blue-600',
    signup: 'bg-purple-100 text-purple-700',
    convert: 'bg-gray-100 text-gray-600',
  }[t] || 'bg-gray-100 text-gray-600'
}

function currencyIcon(c) {
  return { star: '⭐', gem: '💎', coin: '🪙', chip: '🎰' }[c] || ''
}

function ageGroupClass(g) {
  return {
    baby: 'bg-pink-100 text-pink-600',
    kids: 'bg-green-100 text-green-600',
    teen: 'bg-blue-100 text-blue-600',
    adult: 'bg-yellow-100 text-yellow-700',
    senior: 'bg-purple-100 text-purple-600',
  }[g] || 'bg-gray-100 text-gray-600'
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('ko-KR', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function loadData() {
  try {
    const [walletsRes, txRes, catRes] = await Promise.allSettled([
      axios.get('/api/admin/wallets'),
      axios.get('/api/admin/wallet-transactions'),
      axios.get('/api/game-categories'),
    ])
    if (walletsRes.status === 'fulfilled') {
      const d = walletsRes.value.data
      wallets.value = d.wallets || []
      stats.value = d.stats || {}
    }
    if (txRes.status === 'fulfilled') transactions.value = txRes.value.data.data || txRes.value.data || []
    if (catRes.status === 'fulfilled') gameCategories.value = catRes.value.data || []
  } catch (e) { console.error(e) }
}

onMounted(loadData)
</script>
