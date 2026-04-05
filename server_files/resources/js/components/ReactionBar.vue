<template>
  <div class="flex items-center justify-center gap-3 py-4">
    <!-- 좋아요 -->
    <button @click="toggleLike"
      :class="['flex items-center gap-1.5 px-5 py-2 rounded-full border-2 transition font-medium text-sm',
        localLiked ? 'border-red-500 bg-red-50 text-red-600' : 'border-gray-200 text-gray-500 hover:border-red-300']">
      <svg class="w-4 h-4" :fill="localLiked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
      </svg>
      <span>추천 {{ localLikes }}</span>
    </button>

    <!-- 북마크 -->
    <button @click="toggleBookmark"
      :class="['flex items-center gap-1.5 px-4 py-2 rounded-full border-2 transition text-sm',
        localBookmarked ? 'border-yellow-400 bg-yellow-50 text-yellow-600' : 'border-gray-200 text-gray-500 hover:border-yellow-300']">
      <svg class="w-4 h-4" :fill="localBookmarked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/>
      </svg>
      <span>{{ localBookmarked ? '저장됨' : '저장' }}</span>
    </button>

    <!-- 공유 -->
    <button @click="shareItem"
      class="flex items-center gap-1.5 px-4 py-2 rounded-full border-2 border-gray-200 text-gray-500 hover:border-blue-300 transition text-sm">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
      </svg>
      <span>공유</span>
    </button>

    <!-- 신고 -->
    <button @click="showReportModal = true"
      class="flex items-center gap-1.5 px-4 py-2 rounded-full border-2 border-gray-200 text-gray-500 hover:border-red-300 transition text-sm">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"/>
      </svg>
      <span>신고</span>
    </button>

    <!-- 신고 모달 -->
    <teleport to="body">
      <div v-if="showReportModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showReportModal = false">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-5">
          <h3 class="text-lg font-bold text-gray-800 mb-4">신고하기</h3>
          <div class="space-y-2 mb-4">
            <label v-for="r in reportReasons" :key="r.value"
              class="flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition"
              :class="reportReason === r.value ? 'border-red-400 bg-red-50' : 'border-gray-200 hover:border-gray-300'">
              <input type="radio" v-model="reportReason" :value="r.value" class="text-red-600" />
              <span class="text-sm text-gray-700">{{ r.label }}</span>
            </label>
          </div>
          <textarea v-model="reportDetail" rows="2" placeholder="추가 설명 (선택)"
            class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-red-500 resize-none"></textarea>
          <div class="flex gap-2">
            <button @click="showReportModal = false" class="flex-1 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50">취소</button>
            <button @click="submitReport" :disabled="!reportReason || reportLoading"
              class="flex-1 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50">
              {{ reportLoading ? '처리중...' : '신고하기' }}
            </button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const props = defineProps({
  itemType: { type: String, required: true },   // 'post', 'market', 'job' 등
  itemId: { type: Number, required: true },
  likes: { type: Number, default: 0 },
  isLiked: { type: Boolean, default: false },
  isBookmarked: { type: Boolean, default: false }
})

const emit = defineEmits(['liked', 'bookmarked'])

const router = useRouter()
const auth = useAuthStore()

const localLikes = ref(props.likes)
const localLiked = ref(props.isLiked)
const localBookmarked = ref(props.isBookmarked)

watch(() => props.likes, (v) => { localLikes.value = v })
watch(() => props.isLiked, (v) => { localLiked.value = v })
watch(() => props.isBookmarked, (v) => { localBookmarked.value = v })

// 신고 관련
const showReportModal = ref(false)
const reportReason = ref('')
const reportDetail = ref('')
const reportLoading = ref(false)

const reportReasons = [
  { value: 'spam', label: '스팸/광고' },
  { value: 'scam', label: '사기/허위정보' },
  { value: 'inappropriate', label: '부적절한 콘텐츠' },
  { value: 'hate', label: '혐오/차별 표현' },
  { value: 'false_info', label: '허위 정보' },
  { value: 'other', label: '기타' }
]

// itemType -> API report type 매핑
const reportTypeMap = {
  post: 'post',
  market: 'market_item',
  job: 'job_post',
  event: 'post',
  news: 'post',
  recipe: 'post',
  realestate: 'post',
  qa_question: 'post',
  business: 'business'
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/${props.itemType}s/${props.itemId}/like`)
    localLiked.value = data.liked
    localLikes.value = data.like_count ?? (localLiked.value ? localLikes.value + 1 : localLikes.value - 1)
    emit('liked', { liked: localLiked.value, like_count: localLikes.value })
  } catch (e) {
    console.error('좋아요 실패:', e)
  }
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/${props.itemType}s/${props.itemId}/bookmark`)
    localBookmarked.value = data.bookmarked
    emit('bookmarked', { bookmarked: localBookmarked.value })
  } catch (e) {
    console.error('북마크 실패:', e)
  }
}

function shareItem() {
  const url = window.location.href
  if (navigator.share) {
    navigator.share({ title: document.title, url })
  } else if (navigator.clipboard) {
    navigator.clipboard.writeText(url)
    alert('링크가 복사되었습니다.')
  }
}

async function submitReport() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  if (!reportReason.value) return
  reportLoading.value = true
  try {
    await axios.post('/api/reports', {
      type: reportTypeMap[props.itemType] || 'post',
      id: props.itemId,
      reason: reportReason.value,
      detail: reportDetail.value || null
    })
    alert('신고가 접수되었습니다.')
    showReportModal.value = false
    reportReason.value = ''
    reportDetail.value = ''
  } catch (e) {
    alert(e.response?.data?.message || '신고 처리 중 오류가 발생했습니다.')
  } finally {
    reportLoading.value = false
  }
}
</script>
