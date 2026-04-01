<template>
  <div class="flex flex-col bg-gray-100" style="position:fixed;inset:0;">

    <!-- 헤더 -->
    <div class="bg-white shadow-sm px-4 py-3 flex items-center gap-3 flex-shrink-0 z-10">
      <button @click="$router.back()" class="text-gray-500 hover:text-gray-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
      </button>
      <div class="flex-1 min-w-0">
        <p class="font-bold text-gray-800 truncate">{{ room?.name || '채팅방' }}</p>
        <p class="text-xs text-gray-400 truncate">{{ room?.description }}</p>
      </div>
      <!-- 검색 버튼 -->
      <button @click="toggleSearch" class="p-1.5 rounded-full hover:bg-gray-100 transition"
        :class="showSearch ? 'text-blue-500' : 'text-gray-400'">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0"/>
        </svg>
      </button>
      <span class="flex items-center gap-1 text-xs flex-shrink-0" :class="connected ? 'text-green-500' : 'text-gray-400'">
        <span class="w-2 h-2 rounded-full" :class="connected ? 'bg-green-400 animate-pulse' : 'bg-gray-300'"></span>
        {{ connected ? '실시간' : '연결 중' }}
      </span>
    </div>

    <!-- 검색 바 -->
    <transition name="slide-down">
      <div v-if="showSearch" class="bg-white border-b px-3 py-2 flex gap-2 flex-shrink-0">
        <div class="flex-1 relative">
          <input
            ref="searchInput"
            v-model="searchQuery"
            type="text"
            placeholder="채팅 내용 검색..."
            class="w-full border border-gray-200 rounded-full pl-4 pr-8 py-2 text-sm focus:outline-none focus:border-blue-400 bg-gray-50"
            @input="doSearch"
          />
          <button v-if="searchQuery" @click="searchQuery = ''; searchResults = []"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg leading-none">✕</button>
        </div>
        <button @click="toggleSearch" class="text-sm text-gray-400 hover:text-gray-600 px-2">닫기</button>
      </div>
    </transition>

    <!-- 검색 결과 -->
    <div v-if="searchResults.length" class="bg-amber-50 border-b px-3 py-2 flex-shrink-0 max-h-44 overflow-y-auto">
      <p class="text-xs text-amber-700 font-medium mb-1">검색 결과 {{ searchResults.length }}개</p>
      <div v-for="msg in searchResults" :key="msg.id"
        @click="scrollToMessage(msg.id)"
        class="flex items-start gap-2 py-1.5 px-2 rounded-lg hover:bg-amber-100 cursor-pointer transition">
        <div class="w-6 h-6 rounded-full bg-blue-200 flex-shrink-0 flex items-center justify-center text-xs font-bold text-blue-700">
          {{ userName(msg.user)[0] }}
        </div>
        <div class="flex-1 min-w-0">
          <span class="text-xs font-medium text-blue-700">{{ userName(msg.user) }}</span>
          <span class="text-xs text-gray-600 ml-1">{{ msg.message }}</span>
        </div>
        <span class="text-xs text-gray-400 flex-shrink-0">{{ formatDate(msg.created_at) }}</span>
      </div>
    </div>

    <!-- 메시지 목록 -->
    <div ref="msgContainer" class="flex-1 overflow-y-auto px-3 py-2 min-h-0" @click="activeMenu = null">
      <div v-if="loading" class="text-center py-8 text-gray-400">
        <div class="animate-spin w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full mx-auto mb-2"></div>
        불러오는 중...
      </div>
      <div v-else-if="!filteredMessages.length" class="text-center py-16 text-gray-400">
        <div class="text-5xl mb-3">💬</div>
        <p class="text-sm">첫 메시지를 남겨보세요!</p>
      </div>

      <template v-for="(group, dateLabel) in groupedMessages" :key="dateLabel">
        <!-- 날짜 구분선 (텔레그램 스타일) -->
        <div class="flex items-center gap-3 my-4">
          <div class="flex-1 h-px bg-gray-200"></div>
          <span class="text-xs text-gray-500 bg-white border border-gray-200 px-3 py-0.5 rounded-full flex-shrink-0 shadow-sm">
            {{ dateLabel }}
          </span>
          <div class="flex-1 h-px bg-gray-200"></div>
        </div>

        <div v-for="msg in group" :key="msg.id" :id="`msg-${msg.id}`"
          class="flex gap-2 mb-2 rounded-xl px-1 transition-colors duration-500"
          :class="isMe(msg) ? 'justify-end' : 'justify-start'">

          <!-- 상대방 메시지 -->
          <template v-if="!isMe(msg)">
            <div class="w-8 h-8 rounded-full bg-blue-200 flex items-center justify-center text-xs font-bold text-blue-700 flex-shrink-0 mt-1 overflow-hidden">
              <img v-if="msg.user?.avatar" :src="msg.user.avatar" class="w-full h-full object-cover" />
              <span v-else>{{ userName(msg.user)[0] }}</span>
            </div>
            <div class="max-w-[72%]">
              <p class="text-xs text-gray-500 mb-0.5 ml-1">{{ userName(msg.user) }}</p>
              <div class="flex items-end gap-1">
                <div class="bg-white rounded-2xl rounded-tl-none px-3 py-2 shadow-sm text-gray-800 text-sm leading-relaxed">
                  <img v-if="msg.file_type === 'image'" :src="msg.file_url"
                    class="max-w-full rounded-lg max-h-48 object-contain cursor-pointer"
                    @click.stop="openImage(msg.file_url)" />
                  <a v-else-if="msg.file_url" :href="msg.file_url" target="_blank"
                    class="flex items-center gap-1.5 text-blue-600 hover:underline text-sm">
                    📎 {{ msg.file_name || '파일 다운로드' }}
                  </a>
                  <span v-else>{{ msg.message }}</span>
                </div>
                <span class="text-xs text-gray-400 whitespace-nowrap mb-1">{{ formatTime(msg.created_at) }}</span>
                <!-- 더보기 버튼 -->
                <button v-if="auth.isLoggedIn" @click.stop="activeMenu = activeMenu === msg.id ? null : msg.id"
                  class="text-gray-300 hover:text-gray-500 mb-1 flex-shrink-0 p-0.5">
                  <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/>
                  </svg>
                </button>
              </div>
              <!-- 컨텍스트 메뉴 -->
              <div v-if="activeMenu === msg.id"
                class="bg-white rounded-xl shadow-lg border text-sm overflow-hidden mt-1 w-36 z-30 relative">
                <button @click.stop="blockUser(msg.user)"
                  class="flex items-center gap-2 w-full px-3 py-2.5 hover:bg-gray-50 text-gray-700 transition">
                  🚫 차단하기
                </button>
                <div class="h-px bg-gray-100"></div>
                <button @click.stop="reportMessage(msg)"
                  class="flex items-center gap-2 w-full px-3 py-2.5 hover:bg-red-50 text-red-600 transition">
                  🚩 신고하기
                </button>
              </div>
            </div>
          </template>

          <!-- 내 메시지 -->
          <template v-else>
            <div class="max-w-[72%]">
              <div class="flex items-end gap-1 justify-end">
                <span class="text-xs text-gray-400 whitespace-nowrap mb-1">{{ formatTime(msg.created_at) }}</span>
                <div class="bg-blue-500 text-white rounded-2xl rounded-tr-none px-3 py-2 shadow-sm text-sm leading-relaxed">
                  <img v-if="msg.file_type === 'image'" :src="msg.file_url"
                    class="max-w-full rounded-lg max-h-48 object-contain cursor-pointer"
                    @click.stop="openImage(msg.file_url)" />
                  <a v-else-if="msg.file_url" :href="msg.file_url" target="_blank"
                    class="flex items-center gap-1.5 text-blue-100 hover:underline">
                    📎 {{ msg.file_name || '파일' }}
                  </a>
                  <span v-else>{{ msg.message }}</span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </template>
    </div>

    <!-- 입력창 -->
    <div class="bg-white border-t px-3 py-2 flex gap-2 flex-shrink-0"
      style="padding-bottom: calc(0.5rem + env(safe-area-inset-bottom));">
      <label class="p-2 text-gray-400 hover:text-blue-500 cursor-pointer flex items-center flex-shrink-0"
        :class="{ 'opacity-40 pointer-events-none': !auth.isLoggedIn }">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/>
        </svg>
        <input type="file" class="hidden" @change="attachFile"
          accept="image/*,.pdf,.doc,.docx,.zip,.txt" :disabled="!auth.isLoggedIn" />
      </label>
      <input
        v-model="input"
        @keyup.enter="sendMessage"
        type="text"
        placeholder="메시지를 입력하세요..."
        class="flex-1 border border-gray-200 rounded-full px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 bg-gray-50"
        maxlength="500"
        :disabled="!auth.isLoggedIn"
      />
      <button
        @click="auth.isLoggedIn ? sendMessage() : $router.push('/auth/login')"
        :disabled="auth.isLoggedIn && (!input.trim() || sending)"
        class="bg-blue-500 text-white rounded-full px-4 py-2 text-sm font-semibold disabled:opacity-50 flex-shrink-0 transition">
        {{ auth.isLoggedIn ? (sending ? '...' : '전송') : '로그인' }}
      </button>
    </div>

    <!-- 이미지 전체화면 -->
    <div v-if="lightboxUrl" class="fixed inset-0 bg-black/90 z-50 flex items-center justify-center"
      @click="lightboxUrl = null">
      <img :src="lightboxUrl" class="max-w-full max-h-full object-contain rounded" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const route = useRoute()
const auth  = useAuthStore()
const slug  = route.params.id

const room          = ref(null)
const messages      = ref([])
const blockedIds    = ref([])
const input         = ref('')
const sending       = ref(false)
const loading       = ref(true)
const connected     = ref(false)
const msgContainer  = ref(null)
const showSearch    = ref(false)
const searchQuery   = ref('')
const searchResults = ref([])
const searchInput   = ref(null)
const activeMenu    = ref(null)
const lightboxUrl   = ref(null)

let channel       = null
let searchTimeout = null

// 차단된 유저 메시지 필터
const filteredMessages = computed(() =>
  messages.value.filter(m => !blockedIds.value.includes(m.user?.id ?? m.user_id))
)

// 날짜별 그룹핑
const groupedMessages = computed(() => {
  const groups = {}
  filteredMessages.value.forEach(msg => {
    const key = formatDate(msg.created_at)
    if (!groups[key]) groups[key] = []
    groups[key].push(msg)
  })
  return groups
})

function formatDate(dt) {
  if (!dt) return ''
  const d    = new Date(dt)
  const today = new Date()
  const yest  = new Date(today)
  yest.setDate(yest.getDate() - 1)
  if (d.toDateString() === today.toDateString()) return '오늘'
  if (d.toDateString() === yest.toDateString())  return '어제'
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' })
}

function formatTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

function userName(user) {
  return user?.name || user?.username || '?'
}

function isMe(msg) {
  return msg.user?.id === auth.user?.id || msg.user_id === auth.user?.id
}

function openImage(url) {
  lightboxUrl.value = url
}

async function scrollBottom() {
  await nextTick()
  if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
}

async function scrollToMessage(msgId) {
  searchResults.value = []
  showSearch.value    = false
  await nextTick()
  const el = document.getElementById(`msg-${msgId}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    el.style.backgroundColor = '#fef9c3'
    setTimeout(() => { el.style.backgroundColor = '' }, 2000)
  }
}

function toggleSearch() {
  showSearch.value = !showSearch.value
  if (showSearch.value) {
    nextTick(() => searchInput.value?.focus())
  } else {
    searchQuery.value   = ''
    searchResults.value = []
  }
}

function doSearch() {
  clearTimeout(searchTimeout)
  if (!searchQuery.value || searchQuery.value.length < 2) {
    searchResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    try {
      const { data } = await axios.get(`/api/chat/rooms/${slug}/search`, { params: { q: searchQuery.value } })
      searchResults.value = data
    } catch {}
  }, 300)
}

async function sendMessage() {
  if (!input.value.trim() || sending.value) return
  const text    = input.value.trim()
  input.value   = ''
  sending.value = true
  try {
    const socketId = window.Echo?.socketId?.()
    const headers  = socketId ? { 'X-Socket-ID': socketId } : {}
    const { data } = await axios.post(`/api/chat/rooms/${slug}/messages`, { message: text }, { headers })
    messages.value.push(data)
    await scrollBottom()
  } catch {
    input.value = text
  } finally {
    sending.value = false
  }
}

async function attachFile(e) {
  const file = e.target.files[0]
  if (!file || !auth.isLoggedIn) return
  const fd = new FormData()
  fd.append('file', file)
  sending.value = true
  try {
    const socketId = window.Echo?.socketId?.()
    const headers  = socketId ? { 'X-Socket-ID': socketId } : {}
    const { data } = await axios.post(`/api/chat/rooms/${slug}/messages`, fd, { headers })
    messages.value.push(data)
    await scrollBottom()
  } catch {
    alert('파일 전송 실패. 파일 크기는 10MB 이하여야 합니다.')
  } finally {
    sending.value = false
    e.target.value = ''
  }
}

async function blockUser(user) {
  activeMenu.value = null
  if (!user?.id || !auth.isLoggedIn) return
  if (!confirm(`${userName(user)}님을 차단하시겠습니까?\n해당 유저의 메시지가 보이지 않습니다.`)) return
  try {
    await axios.post(`/api/chat/block/${user.id}`)
    blockedIds.value.push(user.id)
  } catch {}
}

async function reportMessage(msg) {
  activeMenu.value = null
  if (!auth.isLoggedIn) return
  try {
    await axios.post(`/api/chat/report/${msg.id}`)
    alert('신고가 접수되었습니다. 관리자가 검토합니다.')
  } catch {}
}

onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/chat/rooms/${slug}`)
    room.value       = data.room
    messages.value   = data.messages ?? []
    blockedIds.value = data.blocked_ids ?? []
    await scrollBottom()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }

  if (!window.Echo || !room.value?.id) return
  channel = window.Echo.channel(`chat.${room.value.id}`)
  channel
    .listen('.message.sent', (data) => {
      if (!messages.value.some(m => m.id === data.id)) {
        messages.value.push(data)
        scrollBottom()
      }
    })
    .subscribed(() => { connected.value = true })
    .error(() => { connected.value = false })
})

onUnmounted(() => {
  if (room.value?.id) window.Echo?.leaveChannel(`chat.${room.value.id}`)
  clearTimeout(searchTimeout)
})
</script>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
