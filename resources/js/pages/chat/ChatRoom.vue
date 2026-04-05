<template>
  <div class="flex flex-col bg-gray-50" style="position: fixed; inset: 0;">
    <!-- Header -->
    <div class="bg-white shadow-sm px-4 py-3 flex items-center gap-3 flex-shrink-0 z-10">
      <button @click="$router.back()" class="text-gray-500 hover:text-gray-700 transition">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="flex-1 min-w-0">
        <p class="font-bold text-gray-800 truncate text-sm">{{ room?.name || $t('chat.room') }}</p>
        <p class="text-xs text-gray-400 truncate">{{ room?.description }}</p>
      </div>
      <span class="flex items-center gap-1 text-xs flex-shrink-0" :class="connected ? 'text-green-500' : 'text-gray-400'">
        <span class="w-2 h-2 rounded-full" :class="connected ? 'bg-green-400 animate-pulse' : 'bg-gray-300'"></span>
        {{ connected ? $t('chat.live') : $t('chat.connecting') }}
      </span>
    </div>

    <!-- Messages -->
    <div ref="msgContainer" class="flex-1 overflow-y-auto px-3 py-2 min-h-0">
      <div v-if="loading" class="text-center py-8 text-gray-400">
        <svg class="w-8 h-8 animate-spin mx-auto mb-2 text-gray-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        {{ $t('common.loading') }}
      </div>

      <div v-else-if="!messages.length" class="text-center py-16 text-gray-400">
        <svg class="w-16 h-16 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
        <p class="text-sm">{{ $t('chat.first_message') }}</p>
      </div>

      <template v-else>
        <div v-for="msg in messages" :key="msg.id" class="mb-3" :id="`msg-${msg.id}`">
          <!-- Date separator -->
          <div v-if="msg._showDate" class="flex items-center gap-3 my-4">
            <div class="flex-1 h-px bg-gray-200"></div>
            <span class="text-xs text-gray-500 bg-white border border-gray-200 px-3 py-0.5 rounded-full flex-shrink-0">
              {{ formatDateLabel(msg.created_at) }}
            </span>
            <div class="flex-1 h-px bg-gray-200"></div>
          </div>

          <!-- Message bubble -->
          <div class="flex gap-2" :class="isMyMsg(msg) ? 'flex-row-reverse' : ''">
            <!-- Avatar (others only) -->
            <div v-if="!isMyMsg(msg)" class="w-8 h-8 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center flex-shrink-0 overflow-hidden">
              <img v-if="msg.user?.avatar" :src="msg.user.avatar" class="w-full h-full object-cover"
                @error="e => e.target.style.display='none'" />
              <span v-else class="text-white text-xs font-bold">{{ (msg.user?.name || '?')[0] }}</span>
            </div>

            <div :class="isMyMsg(msg) ? 'items-end' : 'items-start'" class="flex flex-col max-w-[75%]">
              <span v-if="!isMyMsg(msg)" class="text-xs text-gray-500 mb-0.5 ml-1">{{ msg.user?.name || msg.user?.nickname }}</span>
              <div class="px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed break-words"
                :class="isMyMsg(msg) ? 'bg-blue-600 text-white rounded-tr-md' : 'bg-white text-gray-800 rounded-tl-md shadow-sm border border-gray-100'">
                <!-- Image -->
                <img v-if="msg.image" :src="msg.image" class="max-w-full rounded-lg mb-1"
                  @error="e => e.target.style.display='none'" />
                <span>{{ msg.message || msg.content }}</span>
              </div>
              <span class="text-[10px] text-gray-400 mt-0.5 mx-1">{{ formatTime(msg.created_at) }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>

    <!-- Input -->
    <div class="bg-white border-t border-gray-200 px-3 py-2 flex items-end gap-2 flex-shrink-0">
      <!-- Image upload -->
      <button @click="$refs.imgInput.click()" class="p-2 text-gray-400 hover:text-blue-500 transition flex-shrink-0">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
      </button>
      <input type="file" ref="imgInput" accept="image/*" class="hidden" @change="onImageSelect" />

      <!-- Text input -->
      <div class="flex-1 relative">
        <textarea v-model="newMessage" rows="1" :placeholder="$t('chat.message_placeholder')"
          class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition max-h-24"
          @keydown.enter.exact.prevent="sendMessage"
          ref="inputRef" />
      </div>

      <!-- Send -->
      <button @click="sendMessage" :disabled="!newMessage.trim() && !selectedImage"
        class="bg-blue-600 text-white p-2.5 rounded-xl hover:bg-blue-700 disabled:opacity-40 transition flex-shrink-0">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const route = useRoute()
const auth = useAuthStore()
const { $t } = useLangStore()

const room = ref(null)
const messages = ref([])
const newMessage = ref('')
const loading = ref(true)
const connected = ref(false)
const selectedImage = ref(null)
const msgContainer = ref(null)
const inputRef = ref(null)
const imgInput = ref(null)

let pollInterval = null

function isMyMsg(msg) {
  return msg.user_id === auth.user?.id || msg.user?.id === auth.user?.id
}

function formatTime(d) {
  if (!d) return ''
  return new Date(d).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

function formatDateLabel(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' })
}

function processMessages(msgs) {
  let lastDate = ''
  return msgs.map(m => {
    const date = new Date(m.created_at).toDateString()
    m._showDate = date !== lastDate
    lastDate = date
    return m
  })
}

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) {
      msgContainer.value.scrollTop = msgContainer.value.scrollHeight
    }
  })
}

async function loadRoom() {
  loading.value = true
  try {
    const roomId = route.params.id
    const [roomRes, msgsRes] = await Promise.all([
      axios.get(`/api/chat/rooms/${roomId}`),
      axios.get(`/api/chat/rooms/${roomId}/messages`),
    ])
    room.value = roomRes.data.room || roomRes.data
    messages.value = processMessages(msgsRes.data.data || msgsRes.data || [])
    scrollToBottom()
    connected.value = true
  } catch {
    room.value = null
  }
  loading.value = false
}

async function sendMessage() {
  const content = newMessage.value.trim()
  if (!content && !selectedImage.value) return

  const fd = new FormData()
  if (content) fd.append('message', content)
  if (selectedImage.value) fd.append('image', selectedImage.value)

  newMessage.value = ''
  selectedImage.value = null

  try {
    const { data } = await axios.post(`/api/chat/rooms/${route.params.id}/messages`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const msg = data.message || data
    messages.value = processMessages([...messages.value, msg])
    scrollToBottom()
  } catch (e) {
    alert(e.response?.data?.message || $t('chat.send_failed'))
  }
}

function onImageSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    alert($t('chat.file_too_large'))
    return
  }
  selectedImage.value = file
  sendMessage()
}

async function pollMessages() {
  if (!route.params.id) return
  try {
    const { data } = await axios.get(`/api/chat/rooms/${route.params.id}/messages`, {
      params: { after: messages.value.length ? messages.value[messages.value.length - 1].id : 0 },
    })
    const newMsgs = data.data || data || []
    if (newMsgs.length) {
      messages.value = processMessages([...messages.value, ...newMsgs])
      scrollToBottom()
    }
  } catch { /* ignore */ }
}

onMounted(() => {
  loadRoom()
  pollInterval = setInterval(pollMessages, 3000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})

watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) loadRoom()
})
</script>
