<template>
<div class="flex gap-3">
  <div class="flex-shrink-0 mt-0.5" :class="isReply ? 'w-6 h-6' : 'w-8 h-8'">
    <div class="w-full h-full bg-amber-100 rounded-full flex items-center justify-center font-bold text-amber-700"
      :class="isReply ? 'text-[10px]' : 'text-xs'">{{ (comment.user?.name||'?')[0] }}</div>
  </div>
  <div class="flex-1 min-w-0">
    <!-- 헤더: 이름 + 날짜 + 신고 -->
    <div class="flex items-center gap-2">
      <UserName :userId="comment.user?.id" :name="comment.user?.name" :className="isReply ? 'text-xs font-bold text-gray-800' : 'text-sm font-bold text-gray-800'" />
      <span class="text-[10px] text-gray-400">{{ relativeDate }}</span>
      <span class="text-[10px] text-gray-300">{{ fullDate }}</span>
      <button @click="reportComment" class="ml-auto text-gray-300 hover:text-red-400 text-xs" title="신고">🚩</button>
    </div>
    <!-- 내용 -->
    <div class="text-sm text-gray-700 mt-0.5 whitespace-pre-wrap leading-relaxed">{{ comment.content }}</div>
    <!-- 액션: 좋아요 싫어요 답글 -->
    <div class="flex items-center gap-3 mt-1.5">
      <button @click="vote('like')" class="flex items-center gap-1 text-xs hover:bg-gray-100 px-1.5 py-0.5 rounded-full" :class="myVote==='like' ? 'text-blue-600' : 'text-gray-400'">
        👍 <span v-if="localLikes">{{ localLikes }}</span>
      </button>
      <button @click="vote('dislike')" class="flex items-center gap-1 text-xs hover:bg-gray-100 px-1.5 py-0.5 rounded-full" :class="myVote==='dislike' ? 'text-red-500' : 'text-gray-400'">
        👎 <span v-if="localDislikes">{{ localDislikes }}</span>
      </button>
      <button v-if="!isReply" @click="$emit('reply', comment.id, comment.user?.name)" class="text-xs text-gray-500 font-bold hover:bg-gray-100 px-2 py-0.5 rounded-full">답글</button>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useModal } from '../composables/useModal'
import axios from 'axios'

const props = defineProps({ comment: Object, type: String, typeId: [Number, String], isReply: Boolean })
const emit = defineEmits(['reply', 'refresh'])
const auth = useAuthStore()
const { showAlert, showConfirm } = useModal()

const localLikes = ref(props.comment.likes || 0)
const localDislikes = ref(props.comment.dislikes || 0)
const myVote = ref(null)

const relativeDate = computed(() => {
  if (!props.comment.created_at) return ''
  const h = Math.floor((Date.now() - new Date(props.comment.created_at).getTime()) / 3600000)
  if (h < 1) return '방금'
  if (h < 24) return h + '시간 전'
  return Math.floor(h / 24) + '일 전'
})

const fullDate = computed(() => {
  if (!props.comment.created_at) return ''
  const d = new Date(props.comment.created_at)
  return `${d.getFullYear()}.${d.getMonth()+1}.${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
})

async function vote(type) {
  if (!auth.isLoggedIn) { await showAlert('로그인이 필요합니다.', '알림'); return }
  try {
    const { data } = await axios.post(`/api/comments/${props.comment.id}/vote`, { vote: type })
    localLikes.value = data.likes
    localDislikes.value = data.dislikes
    myVote.value = data.action === 'removed' ? null : data.action
  } catch {}
}

async function reportComment() {
  if (!auth.isLoggedIn) { await showAlert('로그인이 필요합니다.', '알림'); return }
  const ok = await showConfirm('이 댓글을 신고하시겠습니까?', '신고')
  if (!ok) return
  try {
    await axios.post('/api/reports', {
      reportable_type: 'comment',
      reportable_id: props.comment.id,
      reason: '부적절한 댓글',
    })
    await showAlert('신고가 접수되었습니다.', '완료')
  } catch (e) {
    await showAlert(e.response?.data?.message || '신고 실패', '오류')
  }
}
</script>
