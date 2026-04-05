<template>
  <div>
    <!-- 상위노출 버튼 -->
    <button @click="openModal"
      :class="['flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition',
        isBoosted
          ? 'bg-orange-100 text-orange-600 border border-orange-200'
          : 'bg-orange-500 text-white hover:bg-orange-600']">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
      </svg>
      <span>{{ isBoosted ? '상위노출 중' : '상위노출' }}</span>
    </button>

    <!-- 모달 -->
    <teleport to="body">
      <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showModal = false">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 overflow-hidden">
          <div class="bg-gradient-to-r from-orange-500 to-amber-500 px-5 py-4 text-white">
            <h3 class="text-lg font-bold">상위노출 설정</h3>
            <p class="text-sm text-orange-100 mt-0.5">포인트를 사용하여 게시글을 상위에 노출합니다</p>
          </div>

          <div class="p-5 space-y-2">
            <label v-for="opt in boostOptions" :key="opt.duration"
              class="flex items-center justify-between p-3 rounded-xl border-2 cursor-pointer transition"
              :class="selected === opt.duration ? 'border-orange-400 bg-orange-50' : 'border-gray-200 hover:border-orange-200'">
              <div class="flex items-center gap-3">
                <input type="radio" v-model="selected" :value="opt.duration" class="text-orange-500" />
                <div>
                  <p class="text-sm font-medium text-gray-800">{{ opt.label }}</p>
                  <p class="text-xs text-gray-500">{{ opt.desc }}</p>
                </div>
              </div>
              <span class="text-sm font-bold text-orange-600">{{ opt.points.toLocaleString() }}P</span>
            </label>
          </div>

          <div class="px-5 pb-5 flex gap-2">
            <button @click="showModal = false" class="flex-1 py-2.5 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50">취소</button>
            <button @click="submitBoost" :disabled="!selected || boosting"
              class="flex-1 py-2.5 bg-orange-500 text-white rounded-lg text-sm font-medium hover:bg-orange-600 disabled:opacity-50">
              {{ boosting ? '처리중...' : '상위노출 적용' }}
            </button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const props = defineProps({
  itemType: { type: String, required: true },
  itemId: { type: Number, required: true },
  isBoosted: { type: Boolean, default: false }
})

const emit = defineEmits(['boosted'])

const router = useRouter()
const auth = useAuthStore()

const showModal = ref(false)
const selected = ref(null)
const boosting = ref(false)

const boostOptions = [
  { duration: '1h', label: '1시간', desc: '짧은 프로모션에 적합', points: 50 },
  { duration: '24h', label: '24시간', desc: '하루 동안 상위 노출', points: 300 },
  { duration: '7d', label: '7일', desc: '일주일 노출 효과', points: 1500 },
  { duration: '30d', label: '30일', desc: '한 달 장기 노출', points: 5000 }
]

function openModal() {
  if (!auth.isLoggedIn) {
    router.push('/auth/login')
    return
  }
  selected.value = null
  showModal.value = true
}

async function submitBoost() {
  if (!selected.value || boosting.value) return
  boosting.value = true
  try {
    const { data } = await axios.post('/api/boost', {
      item_type: props.itemType,
      item_id: props.itemId,
      duration: selected.value
    })
    alert(data.message || '상위노출이 적용되었습니다.')
    showModal.value = false
    emit('boosted', { duration: selected.value })
  } catch (e) {
    alert(e.response?.data?.message || '상위노출 적용에 실패했습니다.')
  } finally {
    boosting.value = false
  }
}
</script>
