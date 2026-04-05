<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="max-w-3xl mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-5 rounded-2xl">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-black">{{ $t('friends.title') }}</h1>
            <p class="text-blue-200 text-sm mt-0.5">{{ friends.length }}{{ $t('friends.count_suffix') }}</p>
          </div>
          <span v-if="pendingRequests.length" class="bg-white/20 text-white text-sm font-bold px-3 py-1.5 rounded-xl">
            {{ $t('friends.requests') }} {{ pendingRequests.length }}{{ $t('common.count_suffix') }}
          </span>
        </div>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 py-4 space-y-4">
      <!-- Tabs -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-1 flex gap-1">
        <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
          class="flex-1 py-2.5 text-sm font-bold rounded-xl transition"
          :class="activeTab === tab.key ? 'bg-blue-600 text-white shadow-sm' : 'text-gray-500 hover:bg-gray-50'">
          {{ tab.label }}
          <span v-if="tab.count > 0"
            class="ml-1 text-xs px-1.5 py-0.5 rounded-full"
            :class="activeTab === tab.key ? 'bg-white/20' : 'bg-gray-100'">
            {{ tab.count }}
          </span>
        </button>
      </div>

      <!-- Friends Tab: Search -->
      <div v-if="activeTab === 'friends'" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
        <h2 class="font-bold text-gray-800 text-sm mb-3">{{ $t('friends.find') }}</h2>
        <div class="flex gap-2">
          <input v-model="searchQuery" type="text" :placeholder="$t('friends.search_placeholder')"
            class="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition"
            @keyup.enter="searchUsers" />
          <button @click="searchUsers" class="bg-blue-600 text-white px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-blue-700 transition">
            {{ $t('common.search') }}
          </button>
        </div>
        <!-- Search Results -->
        <div v-if="searchResults.length" class="mt-3 space-y-2">
          <div v-for="u in searchResults" :key="u.id"
            class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center overflow-hidden flex-shrink-0">
              <img v-if="u.avatar" :src="u.avatar" class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
              <span v-else class="text-white font-bold">{{ (u.name || '?')[0] }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-800 text-sm truncate">{{ u.name }}</p>
              <p class="text-xs text-gray-400">@{{ u.username }}</p>
            </div>
            <button @click="addFriend(u.id)" :disabled="friendLoading"
              class="bg-blue-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition">
              {{ $t('friends.add') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Friends List -->
      <div v-if="activeTab === 'friends'" class="space-y-2">
        <div v-if="!friends.length" class="text-center py-12 text-gray-400">
          <svg class="w-16 h-16 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
          <p>{{ $t('friends.no_friends') }}</p>
        </div>
        <div v-for="f in friends" :key="f.id"
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex items-center gap-3">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center overflow-hidden flex-shrink-0">
            <img v-if="f.avatar" :src="f.avatar" class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
            <span v-else class="text-white font-bold text-lg">{{ (f.name || '?')[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-800 text-sm truncate">{{ f.name }}</p>
            <p class="text-xs text-gray-400">@{{ f.username }}</p>
          </div>
          <div class="flex gap-1.5 flex-shrink-0">
            <router-link :to="`/chat?user=${f.username}`" class="bg-blue-100 text-blue-600 text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-blue-200 transition">
              {{ $t('chat.chat') }}
            </router-link>
            <button @click="removeFriend(f.id)" class="bg-red-50 text-red-500 text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-red-100 transition">
              {{ $t('friends.remove') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Received Requests -->
      <div v-if="activeTab === 'received'" class="space-y-2">
        <div v-if="!pendingRequests.length" class="text-center py-12 text-gray-400">{{ $t('friends.no_requests') }}</div>
        <div v-for="r in pendingRequests" :key="r.id"
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex items-center gap-3">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center overflow-hidden flex-shrink-0">
            <img v-if="r.avatar" :src="r.avatar" class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
            <span v-else class="text-white font-bold text-lg">{{ (r.name || '?')[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-800 text-sm truncate">{{ r.name }}</p>
            <p class="text-xs text-gray-400">@{{ r.username }}</p>
          </div>
          <div class="flex gap-1.5 flex-shrink-0">
            <button @click="acceptRequest(r.id)" :disabled="friendLoading"
              class="bg-blue-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition">
              {{ $t('friends.accept') }}
            </button>
            <button @click="rejectRequest(r.id)" :disabled="friendLoading"
              class="bg-gray-100 text-gray-500 text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition">
              {{ $t('friends.reject') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Sent Requests -->
      <div v-if="activeTab === 'sent'" class="space-y-2">
        <div v-if="!sentRequests.length" class="text-center py-12 text-gray-400">{{ $t('friends.no_sent') }}</div>
        <div v-for="r in sentRequests" :key="r.id"
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex items-center gap-3">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center overflow-hidden flex-shrink-0">
            <img v-if="r.avatar" :src="r.avatar" class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
            <span v-else class="text-white font-bold text-lg">{{ (r.name || '?')[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-800 text-sm truncate">{{ r.name }}</p>
            <p class="text-xs text-gray-400">{{ $t('friends.waiting') }}</p>
          </div>
        </div>
      </div>

      <!-- Blocked -->
      <div v-if="activeTab === 'blocked'" class="space-y-2">
        <div v-if="!blockedUsers.length" class="text-center py-12 text-gray-400">{{ $t('friends.no_blocked') }}</div>
        <div v-for="b in blockedUsers" :key="b.id"
          class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 flex items-center gap-3">
          <div class="w-12 h-12 rounded-full bg-gray-300 flex items-center justify-center overflow-hidden flex-shrink-0">
            <span class="text-white font-bold text-lg">{{ (b.name || '?')[0] }}</span>
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-800 text-sm truncate">{{ b.name }}</p>
          </div>
          <button @click="unblockUser(b.id)" class="bg-gray-100 text-gray-600 text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-gray-200 transition">
            {{ $t('friends.unblock') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const { $t } = useLangStore()

const activeTab = ref('friends')
const friends = ref([])
const pendingRequests = ref([])
const sentRequests = ref([])
const blockedUsers = ref([])
const searchQuery = ref('')
const searchResults = ref([])
const friendLoading = ref(false)

const tabs = computed(() => [
  { key: 'friends', label: $t('friends.friend_tab'), count: friends.value.length },
  { key: 'received', label: $t('friends.received_tab'), count: pendingRequests.value.length },
  { key: 'sent', label: $t('friends.sent_tab'), count: sentRequests.value.length },
  { key: 'blocked', label: $t('friends.blocked_tab'), count: blockedUsers.value.length },
])

async function loadFriends() {
  try {
    const { data } = await axios.get('/api/friends')
    friends.value = data.friends || data.data || []
    pendingRequests.value = data.pending || []
    sentRequests.value = data.sent || []
    blockedUsers.value = data.blocked || []
  } catch { /* ignore */ }
}

async function searchUsers() {
  if (!searchQuery.value.trim()) return
  try {
    const { data } = await axios.get('/api/friends/search', { params: { q: searchQuery.value } })
    searchResults.value = data.data || data || []
  } catch { searchResults.value = [] }
}

async function addFriend(userId) {
  friendLoading.value = true
  try {
    await axios.post(`/api/friends/request/${userId}`)
    searchResults.value = searchResults.value.filter(u => u.id !== userId)
    await loadFriends()
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.request_failed'))
  } finally { friendLoading.value = false }
}

async function acceptRequest(userId) {
  friendLoading.value = true
  try {
    await axios.post(`/api/friends/accept/${userId}`)
    await loadFriends()
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.accept_failed'))
  } finally { friendLoading.value = false }
}

async function rejectRequest(userId) {
  friendLoading.value = true
  try {
    await axios.post(`/api/friends/reject/${userId}`)
    await loadFriends()
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.reject_failed'))
  } finally { friendLoading.value = false }
}

async function removeFriend(userId) {
  if (!confirm($t('friends.confirm_remove'))) return
  try {
    await axios.delete(`/api/friends/${userId}`)
    await loadFriends()
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.remove_failed'))
  }
}

async function unblockUser(userId) {
  try {
    await axios.post(`/api/friends/unblock/${userId}`)
    await loadFriends()
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.unblock_failed'))
  }
}

onMounted(loadFriends)
</script>
