<template>
<!-- 채팅 버튼 (접힌 상태) -->
<Teleport to="body">
  <button v-if="chatStore.hasRooms && !chatStore.isOpen" @click="chatStore.toggleOpen()"
    class="fixed bottom-20 right-4 z-[90] w-14 h-14 bg-amber-500 hover:bg-amber-600 text-white rounded-full shadow-xl flex items-center justify-center transition-all hover:scale-110">
    <span class="text-2xl">💬</span>
    <span v-if="totalUnread" class="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center">
      {{ totalUnread > 9 ? '9+' : totalUnread }}
    </span>
  </button>

  <!-- 채팅 팝업 -->
  <div v-if="chatStore.hasRooms && chatStore.isOpen"
    class="fixed z-[91] bg-white flex flex-col overflow-hidden
           inset-0 sm:inset-auto sm:bottom-20 sm:right-4 sm:w-[360px] sm:h-[500px] sm:rounded-2xl sm:shadow-2xl sm:border sm:border-gray-200"
    style="max-height: 100vh;">

    <!-- 탭 헤더 -->
    <div class="bg-amber-500 flex-shrink-0 safe-top">
      <div class="flex items-center justify-between px-3 py-2">
        <div class="flex items-center gap-1 flex-1 overflow-x-auto scrollbar-hide">
          <button v-for="room in chatStore.openRooms" :key="room.id"
            @click="chatStore.activeRoomId = room.id"
            class="flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-bold whitespace-nowrap transition flex-shrink-0"
            :class="chatStore.activeRoomId === room.id ? 'bg-white/30 text-white' : 'text-white/70 hover:text-white hover:bg-white/10'">
            <span>{{ room.type === 'club' ? '👥' : '💬' }}</span>
            <span class="max-w-[80px] truncate">{{ room.name }}</span>
            <button @click.stop="chatStore.closeRoom(room.id)" class="ml-0.5 text-white/50 hover:text-white text-[10px]">✕</button>
          </button>
        </div>
        <button @click="chatStore.minimize()" class="w-7 h-7 rounded-full hover:bg-amber-600 flex items-center justify-center text-white transition ml-1 flex-shrink-0">−</button>
      </div>
    </div>

    <!-- 활성 채팅방 -->
    <template v-if="chatStore.activeRoom">
      <!-- 메시지 영역 -->
      <div ref="msgContainer" class="flex-1 overflow-y-auto p-3 space-y-2 bg-gray-50">
        <div v-if="!messages.length && !loading" class="text-center py-8 text-gray-400 text-xs">
          아직 메시지가 없습니다.<br>첫 메시지를 보내보세요!
        </div>
        <div v-for="msg in sortedMessages" :key="msg.id"
          :class="msg.user_id === userId ? 'flex justify-end' : 'flex justify-start'">
          <div class="max-w-[75%]">
            <div v-if="msg.user_id !== userId" class="text-[10px] text-gray-400 mb-0.5 ml-1">
              {{ msg.user?.nickname || msg.user?.name || '알수없음' }}
            </div>
            <div class="px-3 py-2 rounded-2xl text-sm break-words"
              :class="msg.user_id === userId
                ? 'bg-amber-400 text-amber-900 rounded-br-md'
                : 'bg-white border border-gray-200 text-gray-700 rounded-bl-md shadow-sm'">
              <img v-if="msg.type === 'image' && msg.file_url" :src="msg.file_url" class="max-w-full rounded-lg max-h-32 mb-1" />
              <span v-if="msg.content">{{ msg.content }}</span>
            </div>
            <div class="text-[9px] mt-0.5 px-1"
              :class="msg.user_id === userId ? 'text-right text-gray-400' : 'text-gray-300'">
              {{ formatTime(msg.created_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 입력 -->
      <div class="border-t bg-white px-3 py-2 flex-shrink-0 safe-bottom">
        <form @submit.prevent="sendMessage" class="flex items-center gap-2">
          <input v-model="newMessage" type="text" placeholder="메시지 입력..."
            class="flex-1 border border-gray-200 rounded-full px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-amber-400"
            :disabled="sending" maxlength="2000" />
          <button type="submit" :disabled="!newMessage.trim() || sending"
            class="w-9 h-9 bg-amber-500 hover:bg-amber-600 text-white rounded-full flex items-center justify-center transition disabled:opacity-40 flex-shrink-0">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>
          </button>
        </form>
      </div>
    </template>
  </div>
</Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import axios from 'axios'

const auth = useAuthStore()
const chatStore = useChatStore()
const userId = computed(() => auth.user?.id)

const messages = ref([])
const newMessage = ref('')
const loading = ref(false)
const sending = ref(false)
const msgContainer = ref(null)
const totalUnread = ref(0)

let pollTimer = null
let echoChannels = {}

const sortedMessages = computed(() =>
  [...messages.value].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
)

function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '방금'
  if (diff < 3600000) return Math.floor(diff / 60000) + '분 전'
  if (d.toDateString() === now.toDateString())
    return d.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
  return d.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => { if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight })
}

async function loadMessages(roomId) {
  if (!roomId) return
  loading.value = true
  try {
    const { data } = await axios.get(`/api/chat/rooms/${roomId}/messages`)
    messages.value = data.data?.data || data.data || []
    scrollToBottom()
  } catch {}
  loading.value = false
}

async function sendMessage() {
  if (!newMessage.value.trim() || sending.value || !chatStore.activeRoomId) return
  sending.value = true
  try {
    const { data } = await axios.post(`/api/chat/rooms/${chatStore.activeRoomId}/messages`, {
      content: newMessage.value.trim()
    })
    const sent = Array.isArray(data.data) ? data.data : [data.data]
    sent.forEach(m => { if (!messages.value.find(x => x.id === m.id)) messages.value.push(m) })
    newMessage.value = ''
    scrollToBottom()
  } catch {}
  sending.value = false
}

// Echo 실시간
function setupEcho(roomId) {
  if (!roomId || typeof window.Echo === 'undefined' || echoChannels[roomId]) return
  try {
    echoChannels[roomId] = window.Echo.channel(`chat.${roomId}`)
    echoChannels[roomId].listen('.message.sent', (event) => {
      const msg = event.message || event
      if (msg && chatStore.activeRoomId === roomId) {
        if (!messages.value.find(m => m.id === msg.id)) {
          messages.value.push(msg)
          scrollToBottom()
        }
      }
      if (!chatStore.isOpen) totalUnread.value++
    })
  } catch {}
}

function cleanupEcho(roomId) {
  if (echoChannels[roomId] && typeof window.Echo !== 'undefined') {
    try { window.Echo.leave(`chat.${roomId}`) } catch {}
    delete echoChannels[roomId]
  }
}

// 방 변경 시 메시지 로드
watch(() => chatStore.activeRoomId, (roomId) => {
  if (roomId) {
    loadMessages(roomId)
    setupEcho(roomId)
  }
})

// 팝업 열릴 때
watch(() => chatStore.isOpen, (open) => {
  if (open) {
    totalUnread.value = 0
    if (chatStore.activeRoomId) loadMessages(chatStore.activeRoomId)
  }
})

// 방 추가/제거 시 Echo 관리
watch(() => chatStore.openRooms, (rooms) => {
  rooms.forEach(r => setupEcho(r.id))
}, { deep: true })

// 폴링
function startPolling() {
  pollTimer = setInterval(async () => {
    if (!chatStore.isOpen || !chatStore.activeRoomId) return
    try {
      const { data } = await axios.get(`/api/chat/rooms/${chatStore.activeRoomId}/messages`)
      const msgs = data.data?.data || data.data || []
      let added = false
      msgs.forEach(m => {
        if (!messages.value.find(x => x.id === m.id)) { messages.value.push(m); added = true }
      })
      if (added) scrollToBottom()
    } catch {}
  }, 5000)
}

onMounted(() => startPolling())
onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  Object.keys(echoChannels).forEach(cleanupEcho)
})
</script>

<style scoped>
.safe-top { padding-top: env(safe-area-inset-top, 0px); }
.safe-bottom { padding-bottom: env(safe-area-inset-bottom, 0px); }
.scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
.scrollbar-hide::-webkit-scrollbar { display: none; }
</style>
