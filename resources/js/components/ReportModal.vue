<template>
<Teleport to="body">
  <div v-if="show" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div class="bg-white rounded-2xl w-full max-w-sm shadow-xl overflow-hidden">
      <!-- 헤더 -->
      <div class="px-5 py-3 border-b bg-red-50">
        <h3 class="font-bold text-base text-gray-800">🚨 신고하기</h3>
      </div>

      <div class="px-5 py-4 space-y-3 max-h-[60vh] overflow-y-auto">
        <!-- 공통 사유 -->
        <label v-for="r in reasons" :key="r.value"
          class="flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition"
          :class="selected === r.value ? 'bg-red-50 border border-red-200' : 'hover:bg-gray-50 border border-transparent'">
          <input type="radio" :value="r.value" v-model="selected" class="accent-red-500" />
          <span class="text-sm text-gray-700">{{ r.label }}</span>
        </label>

        <!-- 기타 textarea -->
        <div v-if="selected === 'other'" class="mt-2">
          <textarea v-model="customReason" rows="3" maxlength="500" placeholder="신고 사유를 입력해주세요..."
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none outline-none focus:ring-2 focus:ring-red-400 focus:border-red-400"></textarea>
          <div class="text-right text-[10px] text-gray-400 mt-0.5">{{ customReason.length }}/500</div>
        </div>
      </div>

      <!-- 버튼 -->
      <div class="flex gap-2 px-5 py-3 border-t">
        <button @click="$emit('close')" class="flex-1 bg-gray-100 text-gray-700 font-bold py-2.5 rounded-lg text-sm hover:bg-gray-200">취소</button>
        <button @click="doSubmit" :disabled="!selected || loading"
          class="flex-1 bg-red-500 text-white font-bold py-2.5 rounded-lg text-sm hover:bg-red-600 disabled:opacity-40">
          {{ loading ? '접수중...' : '신고 접수' }}
        </button>
      </div>
    </div>
  </div>
</Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useReport } from '../composables/useSocialActions'

const props = defineProps({
  show: Boolean,
  reportableType: String,
  reportableId: [Number, String],
  contentType: { type: String, default: 'general' }, // general, trade, post, user
})
const emit = defineEmits(['close', 'reported'])

const { loading, submit } = useReport()
const selected = ref('')
const customReason = ref('')

// 사유 목록 (contentType에 따라 다름)
const baseReasons = [
  { value: 'spam', label: '스팸 또는 광고' },
  { value: 'inappropriate', label: '부적절한 내용' },
  { value: 'false_info', label: '허위 정보' },
  { value: 'harassment', label: '괴롭힘 또는 따돌림' },
  { value: 'privacy', label: '개인정보 침해' },
]

const tradeReasons = [
  { value: 'scam', label: '사기 의심' },
  { value: 'fake_listing', label: '허위 매물' },
]

const postReasons = [
  { value: 'sexual', label: '성적인 콘텐츠' },
  { value: 'violence', label: '폭력적 또는 혐오스러운 콘텐츠' },
]

const userReasons = [
  { value: 'hate', label: '증오 또는 악의적 콘텐츠' },
  { value: 'harmful', label: '유해하거나 위험한 행위' },
]

const reasons = computed(() => {
  const extra = {
    trade: tradeReasons,
    post: postReasons,
    user: userReasons,
  }[props.contentType] || []
  return [...baseReasons, ...extra, { value: 'other', label: '기타' }]
})

// 모달 열릴 때 리셋
watch(() => props.show, (v) => {
  if (v) { selected.value = ''; customReason.value = '' }
})

async function doSubmit() {
  if (!selected.value) return
  const reason = selected.value === 'other'
    ? (customReason.value.trim() || '기타')
    : reasons.value.find(r => r.value === selected.value)?.label || selected.value
  const ok = await submit(props.reportableType, props.reportableId, reason, customReason.value)
  if (ok) emit('reported')
}
</script>
