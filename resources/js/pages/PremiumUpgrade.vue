<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-10 px-4">
    <!-- Header -->
    <div class="max-w-3xl mx-auto text-center mb-8">
      <div class="text-4xl mb-3">&#x1FA99;</div>
      <h1 class="text-3xl font-bold mb-2">포인트 충전</h1>
      <p class="text-gray-500">포인트를 충전하여 다양한 서비스를 이용하세요</p>
    </div>

    <!-- 현재 보유 포인트 -->
    <div class="max-w-3xl mx-auto mb-8">
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500 mb-1">현재 보유 포인트</p>
          <p class="text-3xl font-bold text-blue-600">{{ currentBalance.toLocaleString() }}P</p>
        </div>
        <div class="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center">
          <span class="text-2xl">&#x1FA99;</span>
        </div>
      </div>
    </div>

    <!-- 테스트 모드 알림 -->
    <div class="max-w-3xl mx-auto mb-6">
      <div class="bg-yellow-50 border border-yellow-200 rounded-xl px-5 py-3 flex items-start gap-3">
        <span class="text-yellow-500 text-lg mt-0.5">&#9888;</span>
        <div>
          <p class="text-sm font-semibold text-yellow-800">테스트 모드입니다</p>
          <p class="text-xs text-yellow-600 mt-1">
            카드번호: <span class="font-mono font-bold">4242 4242 4242 4242</span> / 만료일: 아무 미래 날짜 / CVC: 아무 3자리
          </p>
        </div>
      </div>
    </div>

    <!-- 패키지 목록 -->
    <div class="max-w-3xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-4 mb-10">
      <div
        v-for="pkg in packages"
        :key="pkg.id"
        @click="selectPackage(pkg)"
        :class="[
          'bg-white rounded-2xl shadow-sm border-2 p-6 cursor-pointer transition-all hover:shadow-md',
          selectedPackage?.id === pkg.id ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-100 hover:border-blue-200'
        ]"
      >
        <div class="flex items-center justify-between mb-3">
          <span class="text-2xl font-bold text-gray-800">${{ (pkg.amount / 100).toFixed(0) }}</span>
          <span v-if="pkg.bonus > 0" class="bg-red-100 text-red-600 text-xs font-bold px-2.5 py-1 rounded-full">
            +{{ pkg.bonus }}% 보너스
          </span>
        </div>
        <p class="text-xl font-bold text-blue-600 mb-1">{{ pkg.points.toLocaleString() }}P</p>
        <p class="text-sm text-gray-400">{{ pkg.label }}</p>
      </div>
    </div>

    <!-- Stripe 결제 폼 -->
    <div v-if="selectedPackage" class="max-w-3xl mx-auto mb-10">
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 class="text-lg font-bold mb-1">결제 정보 입력</h3>
        <p class="text-sm text-gray-500 mb-5">
          {{ selectedPackage.label }} 패키지를 선택하셨습니다
        </p>

        <!-- Stripe Card Element -->
        <div class="mb-5">
          <label class="block text-sm font-medium text-gray-700 mb-2">카드 정보</label>
          <div
            id="card-element"
            class="border border-gray-300 rounded-lg px-4 py-3 bg-white focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500"
          ></div>
          <p v-if="cardError" class="text-red-500 text-sm mt-2">{{ cardError }}</p>
        </div>

        <button
          @click="handlePayment"
          :disabled="processing"
          :class="[
            'w-full py-3.5 rounded-xl font-bold text-white transition-all',
            processing ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          ]"
        >
          <span v-if="processing" class="flex items-center justify-center gap-2">
            <span class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            결제 처리 중...
          </span>
          <span v-else>${{ (selectedPackage.amount / 100).toFixed(0) }} 결제하기</span>
        </button>
      </div>
    </div>

    <!-- 결제 성공 모달 -->
    <div v-if="paymentSuccess" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-8 max-w-sm w-full text-center">
        <div class="text-5xl mb-4">&#127881;</div>
        <h3 class="text-xl font-bold mb-2">결제 완료!</h3>
        <p class="text-gray-500 mb-1">{{ successPoints.toLocaleString() }}P가 충전되었습니다</p>
        <p class="text-sm text-gray-400 mb-6">현재 잔액: {{ currentBalance.toLocaleString() }}P</p>
        <button
          @click="paymentSuccess = false"
          class="w-full py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition"
        >확인</button>
      </div>
    </div>

    <!-- 결제 내역 -->
    <div class="max-w-3xl mx-auto">
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h3 class="text-lg font-bold mb-4">결제 내역</h3>
        <div v-if="historyLoading" class="flex justify-center py-8">
          <div class="w-6 h-6 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <div v-else-if="history.length === 0" class="text-center py-8 text-gray-400">
          <p class="text-3xl mb-2">&#128203;</p>
          <p>결제 내역이 없습니다</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-left text-gray-500 border-b border-gray-100">
                <th class="pb-3 font-medium">날짜</th>
                <th class="pb-3 font-medium">항목</th>
                <th class="pb-3 font-medium text-right">금액</th>
                <th class="pb-3 font-medium text-right">포인트</th>
                <th class="pb-3 font-medium text-center">상태</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in history" :key="item.id" class="border-b border-gray-50">
                <td class="py-3 text-gray-600">{{ formatDate(item.paid_at || item.created_at) }}</td>
                <td class="py-3 text-gray-800">{{ formatItemName(item.item_name) }}</td>
                <td class="py-3 text-right font-medium">${{ Number(item.amount).toFixed(2) }}</td>
                <td class="py-3 text-right text-blue-600 font-medium">{{ getPointsByPackage(item.item_name).toLocaleString() }}P</td>
                <td class="py-3 text-center">
                  <span :class="[
                    'text-xs font-medium px-2 py-1 rounded-full',
                    item.status === 'completed' ? 'bg-green-100 text-green-700' :
                    item.status === 'refunded' ? 'bg-red-100 text-red-600' :
                    'bg-yellow-100 text-yellow-700'
                  ]">
                    {{ statusLabel(item.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import axios from 'axios'

// ─── State ──────────────────────────────────────────────────────────
const packages = ref([])
const selectedPackage = ref(null)
const currentBalance = ref(0)
const processing = ref(false)
const cardError = ref('')
const paymentSuccess = ref(false)
const successPoints = ref(0)
const history = ref([])
const historyLoading = ref(false)

// Stripe 인스턴스
let stripe = null
let elements = null
let cardElement = null

// Stripe publishable key (서버에서 받아옴 또는 하드코딩)
const STRIPE_PK = 'pk_test_51THnmRPg1ubIggWTCCl54BiED9Q9ZE0ZvrUTtK5ddJBU3EcLCfZUKYWvPIM2acKqbDo1S76auDkfD0RlEeuIdFty00helczpYq'

// ─── Stripe 초기화 ──────────────────────────────────────────────────
function loadStripeJs() {
  return new Promise((resolve, reject) => {
    if (window.Stripe) {
      resolve(window.Stripe)
      return
    }
    const script = document.createElement('script')
    script.src = 'https://js.stripe.com/v3/'
    script.onload = () => resolve(window.Stripe)
    script.onerror = () => reject(new Error('Stripe.js 로드 실패'))
    document.head.appendChild(script)
  })
}

async function initStripe() {
  try {
    const Stripe = await loadStripeJs()
    stripe = Stripe(STRIPE_PK)
    elements = stripe.elements({ locale: 'ko' })
  } catch (e) {
    console.error('Stripe 초기화 실패:', e)
  }
}

function mountCardElement() {
  if (!elements) return
  // 기존 element 제거
  if (cardElement) {
    cardElement.destroy()
    cardElement = null
  }
  cardElement = elements.create('card', {
    style: {
      base: {
        fontSize: '16px',
        color: '#1f2937',
        '::placeholder': { color: '#9ca3af' },
      },
      invalid: { color: '#ef4444' },
    },
  })
  nextTick(() => {
    const el = document.getElementById('card-element')
    if (el) {
      cardElement.mount('#card-element')
      cardElement.on('change', (event) => {
        cardError.value = event.error ? event.error.message : ''
      })
    }
  })
}

// 패키지 선택 시 카드 element 마운트
watch(selectedPackage, (val) => {
  if (val) {
    nextTick(() => mountCardElement())
  }
})

// ─── API ─────────────────────────────────────────────────────────────
async function loadPackages() {
  try {
    const { data } = await axios.get('/api/payments/packages')
    packages.value = data
  } catch {
    // 기본 패키지 (백엔드 연결 실패 시)
    packages.value = [
      { id: 'pkg_5', amount: 500, points: 1000, bonus: 0, label: '$5 - 1,000P' },
      { id: 'pkg_10', amount: 1000, points: 2500, bonus: 25, label: '$10 - 2,500P (+25%)' },
      { id: 'pkg_25', amount: 2500, points: 7000, bonus: 40, label: '$25 - 7,000P (+40%)' },
      { id: 'pkg_50', amount: 5000, points: 16000, bonus: 60, label: '$50 - 16,000P (+60%)' },
    ]
  }
}

async function loadBalance() {
  try {
    const { data } = await axios.get('/api/wallet/balance')
    currentBalance.value = data.coin_balance || data.coin || 0
  } catch {
    currentBalance.value = 0
  }
}

async function loadHistory() {
  historyLoading.value = true
  try {
    const { data } = await axios.get('/api/payments/history')
    history.value = data.data || []
  } catch {
    history.value = []
  } finally {
    historyLoading.value = false
  }
}

function selectPackage(pkg) {
  selectedPackage.value = pkg
  cardError.value = ''
}

// ─── 결제 처리 ──────────────────────────────────────────────────────
async function handlePayment() {
  if (!stripe || !cardElement) {
    cardError.value = 'Stripe가 아직 로드되지 않았습니다. 잠시 후 다시 시도해주세요.'
    return
  }
  if (processing.value) return

  processing.value = true
  cardError.value = ''

  try {
    // 1. 서버에서 PaymentIntent 생성
    const { data: intentData } = await axios.post('/api/payments/create-intent', {
      package_id: selectedPackage.value.id,
    })

    if (!intentData.clientSecret) {
      throw new Error('결제 생성에 실패했습니다')
    }

    // 2. Stripe로 카드 결제 확인
    const { error, paymentIntent } = await stripe.confirmCardPayment(intentData.clientSecret, {
      payment_method: { card: cardElement },
    })

    if (error) {
      cardError.value = error.message
      return
    }

    if (paymentIntent.status === 'succeeded') {
      // 3. 서버에 결제 확인 요청
      const { data: confirmData } = await axios.post('/api/payments/confirm', {
        payment_intent_id: paymentIntent.id,
      })

      if (confirmData.success) {
        successPoints.value = confirmData.points || intentData.points
        currentBalance.value = confirmData.balance || (currentBalance.value + successPoints.value)
        paymentSuccess.value = true
        selectedPackage.value = null

        // 내역 새로고침
        loadHistory()
      } else {
        cardError.value = confirmData.error || '결제 확인에 실패했습니다'
      }
    }
  } catch (e) {
    cardError.value = e.response?.data?.error || e.message || '결제 중 오류가 발생했습니다'
  } finally {
    processing.value = false
  }
}

// ─── Helpers ─────────────────────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' })
}

function formatItemName(name) {
  const map = {
    pkg_5: '$5 포인트 충전',
    pkg_10: '$10 포인트 충전',
    pkg_25: '$25 포인트 충전',
    pkg_50: '$50 포인트 충전',
  }
  return map[name] || name
}

function getPointsByPackage(name) {
  const map = { pkg_5: 1000, pkg_10: 2500, pkg_25: 7000, pkg_50: 16000 }
  return map[name] || 0
}

function statusLabel(status) {
  const map = { completed: '완료', pending: '대기', failed: '실패', refunded: '환불' }
  return map[status] || status
}

// ─── Lifecycle ──────────────────────────────────────────────────────
onMounted(async () => {
  await initStripe()
  loadPackages()
  loadBalance()
  loadHistory()
})
</script>
