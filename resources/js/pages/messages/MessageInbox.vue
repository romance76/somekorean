<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-black text-gray-800">✉️ 쪽지함</h1>
      <div class="flex items-center gap-2">
        <span v-if="unreadCount" class="bg-red-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">{{ unreadCount }}</span>
        <button @click="showCompose=true" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm hover:bg-amber-500">✏️ 새 쪽지</button>
      </div>
    </div>

    <!-- 받은/보낸 탭 -->
    <div class="flex gap-1 mb-4 bg-white rounded-lg p-1 shadow-sm border">
      <button @click="tab='received'; loadMessages()" class="flex-1 text-sm font-bold py-2 rounded-lg transition"
        :class="tab==='received' ? 'bg-amber-400 text-amber-900' : 'text-gray-500 hover:bg-gray-50'">📥 받은 쪽지</button>
      <button @click="tab='sent'; loadMessages()" class="flex-1 text-sm font-bold py-2 rounded-lg transition"
        :class="tab==='sent' ? 'bg-blue-500 text-white' : 'text-gray-500 hover:bg-gray-50'">📤 보낸 쪽지</button>
    </div>

    <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
    <div v-else-if="!messages.length" class="text-center py-12 text-gray-400">{{ tab==='received' ? '받은 쪽지가 없습니다' : '보낸 쪽지가 없습니다' }}</div>
    <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-for="msg in messages" :key="msg.id" @click="openMsg(msg)"
        class="px-4 py-3 border-b last:border-0 cursor-pointer hover:bg-amber-50/50 transition"
        :class="tab==='received' && !msg.is_read ? 'bg-amber-50' : ''">
        <div class="flex items-center gap-2 mb-1">
          <span v-if="tab==='received' && !msg.is_read" class="w-2 h-2 bg-amber-500 rounded-full flex-shrink-0"></span>
          <div class="w-7 h-7 bg-amber-100 rounded-full flex items-center justify-center text-[11px] font-bold text-amber-700 flex-shrink-0">
            {{ (tab==='received' ? msg.sender?.name : msg.receiver?.name || '?')[0] }}
          </div>
          <span class="text-sm font-semibold text-gray-800">{{ tab==='received' ? msg.sender?.name : msg.receiver?.name || '알 수 없음' }}</span>
          <span v-if="tab==='sent'" class="text-[10px] text-blue-400">보냄</span>
          <span class="text-[10px] text-gray-400 ml-auto">{{ formatDate(msg.created_at) }}</span>
        </div>
        <div class="text-sm text-gray-600 truncate pl-9">{{ msg.content }}</div>
      </div>
    </div>

    <!-- 쪽지 상세 모달 -->
    <div v-if="activeMsg" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" @click.self="activeMsg=null">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
        <div class="bg-gradient-to-r px-5 py-3 flex items-center justify-between"
          :class="tab==='received' ? 'from-amber-400 to-orange-400' : 'from-blue-500 to-blue-600'">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-white/30 flex items-center justify-center text-sm font-bold"
              :class="tab==='received' ? 'text-amber-900' : 'text-white'">
              {{ (tab==='received' ? activeMsg.sender?.name : activeMsg.receiver?.name || '?')[0] }}
            </div>
            <div>
              <div class="text-sm font-bold" :class="tab==='received' ? 'text-amber-900' : 'text-white'">
                {{ tab==='received' ? activeMsg.sender?.name : activeMsg.receiver?.name }}
              </div>
              <div class="text-[10px]" :class="tab==='received' ? 'text-amber-800/70' : 'text-white/70'">{{ formatDate(activeMsg.created_at) }}</div>
            </div>
          </div>
          <button @click="activeMsg=null" class="text-sm" :class="tab==='received' ? 'text-amber-900/50 hover:text-amber-900' : 'text-white/50 hover:text-white'">✕</button>
        </div>
        <div class="p-5">
          <div class="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed mb-4">{{ activeMsg.content }}</div>
          <div v-if="tab==='received'" class="flex gap-2">
            <button @click="replyToMsg(activeMsg)" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm flex-1 hover:bg-amber-500">↩️ 답장</button>
            <button @click="activeMsg=null" class="text-gray-500 px-4 py-2">닫기</button>
          </div>
          <div v-else class="text-right">
            <button @click="activeMsg=null" class="text-gray-500 px-4 py-2">닫기</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 쪽지 작성 모달 -->
    <div v-if="showCompose" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" @click.self="showCompose=false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 px-5 py-3 flex items-center justify-between">
          <span class="text-white font-bold text-sm">✏️ 새 쪽지</span>
          <button @click="showCompose=false" class="text-white/50 hover:text-white text-sm">✕</button>
        </div>
        <div class="p-5">
          <label class="text-xs font-bold text-gray-600 mb-1 block">받는 사람 (사용자 ID)</label>
          <input v-model="composeForm.receiver_id" type="number" placeholder="받는 사람 ID" class="w-full border rounded-lg px-3 py-2 text-sm mb-3 focus:ring-2 focus:ring-blue-400 outline-none" />
          <label class="text-xs font-bold text-gray-600 mb-1 block">내용</label>
          <textarea v-model="composeForm.content" rows="5" maxlength="500" placeholder="쪽지 내용을 입력하세요..." class="w-full border rounded-lg px-3 py-2 text-sm mb-1 resize-none focus:ring-2 focus:ring-blue-400 outline-none"></textarea>
          <div class="text-right text-[10px] text-gray-400 mb-3">{{ composeForm.content.length }}/500</div>
          <div v-if="composeError" class="text-red-500 text-sm mb-2">{{ composeError }}</div>
          <div class="flex gap-2">
            <button @click="showCompose=false" class="bg-gray-100 text-gray-600 font-bold px-4 py-2 rounded-lg text-sm hover:bg-gray-200">취소</button>
            <button @click="sendMessage" :disabled="sending" class="bg-blue-500 text-white font-bold px-4 py-2 rounded-lg text-sm flex-1 hover:bg-blue-600 disabled:opacity-50">{{ sending ? '전송중...' : '보내기' }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

const messages = ref([])
const loading = ref(true)
const activeMsg = ref(null)
const showCompose = ref(false)
const sending = ref(false)
const composeError = ref('')
const composeForm = reactive({ receiver_id: '', content: '' })
const tab = ref('received')
const unreadCount = ref(0)

function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt), now = new Date()
  const m = d.getMonth() + 1, day = d.getDate()
  const hh = String(d.getHours()).padStart(2, '0'), mm = String(d.getMinutes()).padStart(2, '0')
  if (d.getFullYear() === now.getFullYear() && m === now.getMonth() + 1 && day === now.getDate()) return `오늘 ${hh}:${mm}`
  if (d.getFullYear() === now.getFullYear()) return `${m}/${day} ${hh}:${mm}`
  return `${d.getFullYear()}.${m}.${day} ${hh}:${mm}`
}

async function loadMessages() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/messages', { params: { tab: tab.value } })
    messages.value = data.data?.data || data.data || []
    if (data.unread_count !== undefined) unreadCount.value = data.unread_count
  } catch {}
  loading.value = false
}

async function openMsg(msg) {
  activeMsg.value = msg
  if (tab.value === 'received' && !msg.is_read) {
    msg.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
    try { await axios.post(`/api/messages/${msg.id}/read`) } catch {}
  }
}

function replyToMsg(msg) {
  activeMsg.value = null
  showCompose.value = true
  composeForm.receiver_id = msg.sender_id || msg.sender?.id || ''
  composeForm.content = ''
}

async function sendMessage() {
  if (!composeForm.receiver_id || !composeForm.content.trim()) { composeError.value = '받는 사람과 내용을 입력하세요'; return }
  sending.value = true; composeError.value = ''
  try {
    await axios.post('/api/messages', { receiver_id: composeForm.receiver_id, content: composeForm.content })
    showCompose.value = false; composeForm.receiver_id = ''; composeForm.content = ''
    if (tab.value === 'sent') await loadMessages()
  } catch (e) { composeError.value = e.response?.data?.message || '전송 실패' }
  sending.value = false
}

onMounted(() => loadMessages())
</script>
