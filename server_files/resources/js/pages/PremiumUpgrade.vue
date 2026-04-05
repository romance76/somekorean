<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-16 px-4">
    <div class="max-w-5xl mx-auto text-center mb-12">
      <div class="text-5xl mb-4">👑</div>
      <h1 class="text-4xl font-bold mb-3">프리미엄 업그레이드</h1>
      <p class="text-gray-500 text-lg">내 업소를 더 많은 한인들에게 알리세요</p>
    </div>
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="plan in plans" :key="plan.id"
        :class="['bg-white rounded-3xl shadow-lg p-8 relative transition hover:shadow-xl',
          plan.recommended ? 'ring-2 ring-blue-600 scale-105' : '']">
        <div v-if="plan.recommended" class="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white text-sm px-4 py-1 rounded-full font-semibold">가장 인기</div>
        <div class="text-4xl mb-3">{{ plan.icon }}</div>
        <h3 class="text-xl font-bold mb-1">{{ plan.name }}</h3>
        <div class="text-3xl font-bold text-blue-600 mb-1">${{ plan.price }}<span class="text-base text-gray-400 font-normal">/월</span></div>
        <p class="text-gray-400 text-sm mb-6">약 ₩{{ Math.round(plan.price * 1350).toLocaleString() }}/월</p>
        <ul class="space-y-3 mb-8">
          <li v-for="f in plan.features" :key="f" class="flex items-start gap-2 text-sm">
            <span class="text-green-500 font-bold mt-0.5">✓</span>
            <span>{{ f }}</span>
          </li>
        </ul>
        <button @click="selectPlan(plan)" :class="['w-full py-3 rounded-xl font-bold transition',
          plan.recommended ? 'bg-blue-600 text-white hover:bg-blue-700' : 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50']">
          {{ plan.id === currentPlan ? '현재 플랜' : '선택하기' }}
        </button>
      </div>
    </div>
    <div class="max-w-2xl mx-auto mt-12 bg-white rounded-2xl shadow p-8">
      <h3 class="font-bold text-lg mb-4">자주 묻는 질문</h3>
      <div v-for="faq in faqs" :key="faq.q" class="mb-4">
        <button @click="faq.open = !faq.open" class="w-full text-left font-semibold text-gray-800 flex justify-between">
          {{ faq.q }} <span>{{ faq.open ? '▲' : '▼' }}</span>
        </button>
        <p v-if="faq.open" class="text-gray-500 text-sm mt-2">{{ faq.a }}</p>
      </div>
    </div>
    <!-- Modal -->
    <div v-if="selectedPlan" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-8 max-w-md w-full">
        <h3 class="text-xl font-bold mb-2">{{ selectedPlan.name }} 플랜 신청</h3>
        <p class="text-gray-500 text-sm mb-4">카드 결제 연동은 준비 중입니다. 하단 계좌로 선결제 후 이메일로 문의해주세요.</p>
        <div class="bg-gray-50 rounded-xl p-4 text-sm mb-4">
          <p>💳 <strong>결제 금액:</strong> ${{ selectedPlan.price }}/월</p>
          <p class="mt-1">📧 <strong>문의:</strong> admin@somekorean.com</p>
        </div>
        <button @click="selectedPlan=null" class="w-full border-2 border-gray-200 py-2.5 rounded-xl font-semibold hover:bg-gray-50">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const currentPlan = ref('free')
const selectedPlan = ref(null)

const plans = [
  {
    id: 'basic', name: 'Basic', price: 29, icon: '🌟',
    features: ['사진 10장 등록', '소개글 작성', '영업시간 상세 관리', '기본 통계 (조회수)', '리뷰 답변']
  },
  {
    id: 'standard', name: 'Standard', price: 59, icon: '⭐', recommended: true,
    features: ['사진 20장 등록', '이벤트 등록 (월 4개)', '상세 통계 (클릭/방문)', '검색 결과 상단 노출', '메뉴/서비스 목록', '우선 고객 지원']
  },
  {
    id: 'premium', name: 'Premium', price: 99, icon: '👑',
    features: ['모든 Standard 기능', '무제한 이벤트 등록', '광고 배너 노출', '홈 추천 업소 등재', '맞춤형 마케팅 지원', '전담 매니저 배정']
  }
]

const faqs = ref([
  { q: '언제부터 프리미엄 혜택을 받을 수 있나요?', a: '결제 확인 후 24시간 이내 활성화됩니다.', open: false },
  { q: '해지하면 어떻게 되나요?', a: '해지 시 다음 결제일부터 기본 플랜으로 전환됩니다. 이미 결제된 금액은 환불되지 않습니다.', open: false },
  { q: '업소가 여러 개인 경우 어떻게 하나요?', a: '업소당 별도 구독이 필요합니다.', open: false },
])

function selectPlan(plan) {
  selectedPlan.value = plan
}
</script>
