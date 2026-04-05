<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="max-w-3xl mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-5 rounded-2xl">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-black">{{ $t('chat.title') }}</h1>
            <p class="text-blue-200 text-sm mt-0.5">{{ $t('chat.subtitle') }}</p>
          </div>
          <button @click="showNewChat = true"
            class="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-xl text-sm font-bold transition">
            + {{ $t('chat.new_chat') }}
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 py-4 space-y-3">
      <!-- Search -->
      <div class="relative">
        <svg class="w-5 h-5 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input v-model="search" type="text" :placeholder="$t('chat.search_placeholder')"
          class="w-full border border-gray-200 rounded-xl pl-10 pr-4 py-3 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition" />
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
      <div v-else-if="!filteredRooms.length" class="text-center py-16">
        <svg class="w-16 h-16 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
        </svg>
        <p class="text-gray-400">{{ $t('chat.no_rooms') }}</p>
      </div>

      <!-- Room List -->
      <div v-else class="space-y-2">
        <router-link v-for="room in filteredRooms" :key="room.id" :to="`/chat/${room.id || room.slug}`"
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex items-center gap-3 hover:shadow-md transition block">
          <div class="w-12 h-12 rounded-full flex-shrink-0 overflow-hidden flex items-center justify-center"
            :class="roomGradient(room)">
            <img v-if="room.other_user?.avatar" :src="room.other_user.avatar" class="w-full h-full object-cover"
              @error="e => e.target.style.display='none'" />
            <span v-else class="text-white font-bold text-lg">{{ room.icon || (room.name || '?')[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-0.5">
              <h3 class="font-bold text-gray-800 text-sm truncate">{{ room.name || room.other_user?.name || $t('chat.unknown') }}</h3>
              <span class="text-xs text-gray-400 flex-shrink-0 ml-2">{{ timeAgo(room.last_message_at || room.updated_at) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <p class="text-sm text-gray-500 truncate flex-1">{{ room.last_message?.content || room.description || $t('chat.no_messages') }}</p>
              <span v-if="room.unread_count" class="ml-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full flex-shrink-0">
                {{ room.unread_count > 99 ? '99+' : room.unread_count }}
              </span>
            </div>
          </div>
        </router-link>
      </div>
    </div>

    <!-- New Chat Modal -->
    <div v-if="showNewChat" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showNewChat = false">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-gray-800 text-lg mb-4">{{ $t('chat.new_chat') }}</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('chat.room_name') }}</label>
            <input v-model="newRoomName" type="text" :placeholder="$t('chat.room_name_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">{{ $t('chat.description') }}</label>
            <input v-model="newRoomDesc" type="text" :placeholder="$t('chat.description_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition" />
          </div>
          <div class="flex justify-end gap-2">
            <button @click="showNewChat = false" class="px-4 py-2 text-gray-600 border border-gray-200 rounded-xl text-sm hover:bg-gray-50 transition">
              {{ $t('common.cancel') }}
            </button>
            <button @click="createRoom" :disabled="!newRoomName || creatingRoom"
              class="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 disabled:opacity-50 transition">
              {{ creatingRoom ? $t('common.processing') : $t('chat.create') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const { $t } = useLangStore()
const router = useRouter()

const rooms = ref([])
const search = ref('')
const loading = ref(true)
const showNewChat = ref(false)
const newRoomName = ref('')
const newRoomDesc = ref('')
const creatingRoom = ref(false)

const filteredRooms = computed(() => {
  if (!search.value) return rooms.value
  const q = search.value.toLowerCase()
  return rooms.value.filter(r =>
    (r.name || '').toLowerCase().includes(q) ||
    (r.other_user?.name || '').toLowerCase().includes(q) ||
    (r.description || '').toLowerCase().includes(q)
  )
})

function roomGradient(room) {
  const types = {
    regional: 'bg-gradient-to-br from-blue-400 to-blue-600',
    theme: 'bg-gradient-to-br from-purple-400 to-pink-500',
    dm: 'bg-gradient-to-br from-green-400 to-green-600',
  }
  return types[room.type] || 'bg-gradient-to-br from-blue-400 to-blue-600'
}

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

async function loadRooms() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/chat/rooms')
    rooms.value = data.data || data || []
  } catch { /* ignore */ }
  loading.value = false
}

async function createRoom() {
  if (!newRoomName.value) return
  creatingRoom.value = true
  try {
    const { data } = await axios.post('/api/chat/rooms', {
      name: newRoomName.value,
      description: newRoomDesc.value,
    })
    showNewChat.value = false
    newRoomName.value = ''
    newRoomDesc.value = ''
    const id = data.id || data.room?.id || data.slug
    router.push(`/chat/${id}`)
  } catch (e) {
    alert(e.response?.data?.message || $t('chat.create_failed'))
  } finally {
    creatingRoom.value = false
  }
}

onMounted(loadRooms)
</script>
