<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="max-w-3xl mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-5 rounded-2xl">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-black">{{ $t('messages.inbox') }}</h1>
            <p class="text-blue-200 text-sm mt-0.5">{{ $t('messages.subtitle') }}</p>
          </div>
          <button @click="showCompose = true"
            class="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-xl text-sm font-bold transition">
            + {{ $t('messages.compose') }}
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 py-4">
      <!-- Compose Modal -->
      <div v-if="showCompose" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showCompose = false">
        <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
          <h3 class="font-bold text-gray-800 text-lg mb-4">{{ $t('messages.compose') }}</h3>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('messages.recipient') }}</label>
              <input v-model="composeForm.username" type="text" :placeholder="$t('messages.recipient_placeholder')"
                class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('messages.content') }}</label>
              <textarea v-model="composeForm.content" rows="5" :placeholder="$t('messages.content_placeholder')"
                class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition resize-none" />
            </div>
            <div v-if="composeError" class="text-red-600 text-sm bg-red-50 p-3 rounded-xl">{{ composeError }}</div>
            <div class="flex justify-end gap-2">
              <button @click="showCompose = false; composeError = ''"
                class="px-4 py-2 border border-gray-200 text-gray-600 rounded-xl text-sm hover:bg-gray-50 transition">
                {{ $t('common.cancel') }}
              </button>
              <button @click="sendMessage" :disabled="sending"
                class="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 disabled:opacity-50 transition">
                {{ sending ? $t('common.processing') : $t('messages.send') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Thread view modal -->
      <div v-if="activeThread" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="activeThread = null">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[80vh] flex flex-col">
          <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between flex-shrink-0">
            <h3 class="font-bold text-gray-800">{{ activeThread.other_user?.name }}</h3>
            <button @click="activeThread = null" class="text-gray-400 hover:text-gray-600">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div v-for="msg in threadMessages" :key="msg.id"
              class="flex gap-2" :class="msg.is_sender ? 'flex-row-reverse' : ''">
              <div class="px-3.5 py-2.5 rounded-2xl text-sm max-w-[75%]"
                :class="msg.is_sender ? 'bg-blue-600 text-white rounded-tr-md' : 'bg-gray-100 text-gray-800 rounded-tl-md'">
                {{ msg.content }}
              </div>
            </div>
          </div>
          <div class="px-4 py-3 border-t border-gray-100 flex gap-2 flex-shrink-0">
            <input v-model="replyContent" type="text" :placeholder="$t('messages.reply_placeholder')"
              class="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition"
              @keyup.enter="sendReply" />
            <button @click="sendReply" :disabled="!replyContent.trim()"
              class="bg-blue-600 text-white px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-blue-700 disabled:opacity-50 transition">
              {{ $t('messages.send') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-16 text-gray-400">
        <svg class="w-8 h-8 animate-spin mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        {{ $t('common.loading') }}
      </div>

      <!-- Empty -->
      <div v-else-if="!conversations.length" class="text-center py-16">
        <svg class="w-16 h-16 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 19v-8.93a2 2 0 01.89-1.664l7-4.666a2 2 0 012.22 0l7 4.666A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76"/>
        </svg>
        <p class="text-gray-400">{{ $t('messages.no_messages') }}</p>
      </div>

      <!-- Conversation List -->
      <div v-else class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div v-for="conv in conversations" :key="conv.id" @click="openThread(conv)"
          class="px-5 py-4 border-b border-gray-50 last:border-0 cursor-pointer hover:bg-gray-50 transition flex items-center gap-3"
          :class="!conv.is_read ? 'bg-blue-50/50' : ''">
          <div class="w-11 h-11 rounded-full flex-shrink-0 overflow-hidden bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
            <img v-if="conv.other_user?.avatar" :src="conv.other_user.avatar" class="w-full h-full object-cover"
              @error="e => e.target.style.display='none'" />
            <span v-else class="text-white font-bold">{{ (conv.other_user?.name || '?')[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-0.5">
              <p class="font-bold text-gray-800 text-sm truncate" :class="!conv.is_read ? 'text-gray-900' : ''">
                {{ conv.other_user?.name || $t('messages.unknown') }}
              </p>
              <span class="text-xs text-gray-400 flex-shrink-0 ml-2">{{ timeAgo(conv.updated_at) }}</span>
            </div>
            <p class="text-sm truncate" :class="!conv.is_read ? 'text-gray-700 font-medium' : 'text-gray-500'">
              {{ conv.last_message || conv.content }}
            </p>
          </div>
          <div v-if="!conv.is_read" class="w-2.5 h-2.5 bg-blue-500 rounded-full flex-shrink-0"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const route = useRoute()
const { $t } = useLangStore()

const conversations = ref([])
const loading = ref(true)
const showCompose = ref(false)
const composeForm = ref({ username: '', content: '' })
const composeError = ref('')
const sending = ref(false)
const activeThread = ref(null)
const threadMessages = ref([])
const replyContent = ref('')

function timeAgo(d) {
  if (!d) return ''
  const diff = Date.now() - new Date(d).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return $t('time.just_now')
  if (m < 60) return `${m}분`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}시간`
  const days = Math.floor(h / 24)
  return `${days}일`
}

async function loadMessages() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/messages')
    conversations.value = data.data || data || []
  } catch { /* ignore */ }
  loading.value = false
}

async function sendMessage() {
  if (!composeForm.value.username || !composeForm.value.content) return
  sending.value = true
  composeError.value = ''
  try {
    await axios.post('/api/messages', composeForm.value)
    showCompose.value = false
    composeForm.value = { username: '', content: '' }
    await loadMessages()
  } catch (e) {
    composeError.value = e.response?.data?.message || $t('messages.send_failed')
  } finally {
    sending.value = false
  }
}

async function openThread(conv) {
  activeThread.value = conv
  try {
    const { data } = await axios.get(`/api/messages/${conv.id || conv.other_user?.id}`)
    threadMessages.value = data.data || data || []
    // Mark as read
    if (!conv.is_read) {
      await axios.post(`/api/messages/${conv.id}/read`).catch(() => {})
      conv.is_read = true
    }
  } catch { threadMessages.value = [] }
}

async function sendReply() {
  if (!replyContent.value.trim() || !activeThread.value) return
  try {
    const { data } = await axios.post('/api/messages', {
      username: activeThread.value.other_user?.username,
      content: replyContent.value,
    })
    threadMessages.value.push(data.message || data)
    replyContent.value = ''
  } catch (e) {
    alert(e.response?.data?.message || $t('messages.send_failed'))
  }
}

onMounted(() => {
  loadMessages()
  // Pre-fill recipient if from query
  if (route.query.to) {
    composeForm.value.username = route.query.to
    showCompose.value = true
  }
})
</script>
