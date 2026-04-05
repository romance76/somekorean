<template>
  <div class="max-w-3xl mx-auto px-4 py-6 pb-20">
    <!-- Loading -->
    <div v-if="loading" class="text-center py-20 text-gray-400">
      <svg class="w-8 h-8 animate-spin mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
      {{ $t('common.loading') }}
    </div>

    <template v-else-if="profile">
      <!-- Profile Header -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-4">
        <div class="bg-gradient-to-r from-red-500 to-red-600 h-24"></div>
        <div class="px-5 pb-5 -mt-10">
          <div class="flex items-end gap-4">
            <div class="w-20 h-20 rounded-full border-4 border-white bg-red-100 flex items-center justify-center flex-shrink-0 overflow-hidden shadow-md">
              <img v-if="profile.avatar" :src="profile.avatar" :alt="profile.name"
                class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
              <span v-else class="text-2xl font-black text-red-600">{{ (profile.name || '?')[0] }}</span>
            </div>
            <div class="flex-1 min-w-0 pt-10">
              <div class="flex items-center gap-2 flex-wrap">
                <h1 class="text-lg font-black text-gray-900">{{ profile.name }}</h1>
                <span class="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded-full font-semibold">{{ profile.level || 'Lv.1' }}</span>
                <span v-if="!isMyProfile && friendStatus === 'friends'"
                  class="text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded-full font-semibold">{{ $t('friends.friend') }}</span>
              </div>
              <p class="text-sm text-gray-500">@{{ profile.username }}</p>
            </div>
            <div v-if="isMyProfile" class="flex-shrink-0 pt-10">
              <router-link to="/profile/edit"
                class="text-sm text-red-600 border border-red-200 px-3 py-1.5 rounded-xl hover:bg-red-50 font-semibold transition">
                {{ $t('profile.edit') }}
              </router-link>
            </div>
          </div>

          <!-- Bio -->
          <p v-if="profile.bio" class="text-sm text-gray-600 mt-3 leading-relaxed">{{ profile.bio }}</p>
          <p v-if="profile.region" class="text-xs text-gray-400 mt-2 flex items-center gap-1">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            {{ profile.region }}
          </p>

          <!-- Friend Actions -->
          <div v-if="!isMyProfile && authStore.isLoggedIn" class="mt-4 pt-4 border-t border-gray-100">
            <div v-if="friendStatus === 'none'" class="flex gap-2">
              <button @click="sendFriendRequest" :disabled="friendLoading"
                class="bg-blue-600 text-white text-sm font-bold px-5 py-2.5 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition">
                {{ friendLoading ? $t('common.processing') : $t('friends.add_friend') }}
              </button>
              <router-link :to="`/messages?to=${profile.username}`"
                class="bg-gray-100 text-gray-700 text-sm font-bold px-5 py-2.5 rounded-xl hover:bg-gray-200 transition">
                {{ $t('messages.send') }}
              </router-link>
            </div>
            <div v-else-if="friendStatus === 'friends'" class="flex items-center gap-3">
              <span class="text-sm text-green-600 font-semibold">{{ $t('friends.is_friend') }}</span>
              <button @click="removeFriend"
                class="text-xs text-red-400 border border-red-200 px-3 py-1.5 rounded-xl hover:bg-red-50 transition">
                {{ $t('friends.remove') }}
              </button>
            </div>
            <div v-else-if="friendStatus === 'request_sent'" class="flex items-center gap-2">
              <span class="text-sm text-yellow-600 font-semibold bg-yellow-50 px-3 py-1.5 rounded-xl">{{ $t('friends.request_pending') }}</span>
            </div>
            <div v-else-if="friendStatus === 'request_received'" class="flex items-center gap-2">
              <span class="text-sm text-gray-600 mr-2">{{ $t('friends.request_received') }}</span>
              <button @click="acceptFriendRequest" :disabled="friendLoading"
                class="bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition">
                {{ $t('friends.accept') }}
              </button>
              <button @click="rejectFriendRequest" :disabled="friendLoading"
                class="bg-gray-100 text-gray-500 text-sm font-bold px-4 py-2 rounded-xl hover:bg-gray-200 disabled:opacity-50 transition">
                {{ $t('friends.reject') }}
              </button>
            </div>
          </div>

          <!-- Stats -->
          <div class="flex gap-6 mt-4 pt-4 border-t border-gray-100 text-center">
            <div>
              <p class="text-lg font-black text-gray-800">{{ profile.post_count || 0 }}</p>
              <p class="text-xs text-gray-400">{{ $t('profile.posts') }}</p>
            </div>
            <div>
              <p class="text-lg font-black text-gray-800">{{ profile.comment_count || 0 }}</p>
              <p class="text-xs text-gray-400">{{ $t('profile.comments') }}</p>
            </div>
            <div>
              <p class="text-lg font-black text-gray-800">{{ (profile.points || 0).toLocaleString() }}</p>
              <p class="text-xs text-gray-400">{{ $t('profile.points') }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-4">
        <div class="flex border-b border-gray-100">
          <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
            class="flex-1 py-3 text-sm font-semibold transition text-center"
            :class="activeTab === tab.key ? 'text-red-600 border-b-2 border-red-600' : 'text-gray-400 hover:text-gray-600'">
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Posts Tab -->
      <div v-if="activeTab === 'posts'" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div v-if="!posts.length" class="text-center py-12 text-gray-400 text-sm">{{ $t('profile.no_posts') }}</div>
        <div v-else>
          <div v-for="post in posts" :key="post.id" class="px-5 py-3.5 border-b border-gray-50 last:border-0">
            <router-link :to="`/community/${post.board?.slug || 'general'}/${post.id}`"
              class="flex items-center justify-between hover:text-red-600 transition group">
              <div class="flex-1 min-w-0">
                <span class="text-sm text-gray-800 group-hover:text-red-600 line-clamp-1">{{ post.title }}</span>
                <span v-if="post.board" class="text-xs text-gray-400 ml-2">[{{ post.board.name }}]</span>
              </div>
              <span class="text-xs text-gray-400 ml-3 flex-shrink-0">{{ formatDate(post.created_at) }}</span>
            </router-link>
          </div>
        </div>
      </div>

      <!-- Comments Tab -->
      <div v-if="activeTab === 'comments'" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div v-if="!comments.length" class="text-center py-12 text-gray-400 text-sm">{{ $t('profile.no_comments') }}</div>
        <div v-else>
          <div v-for="c in comments" :key="c.id" class="px-5 py-3.5 border-b border-gray-50 last:border-0">
            <p class="text-sm text-gray-800 line-clamp-2">{{ c.content }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ formatDate(c.created_at) }}</p>
          </div>
        </div>
      </div>

      <!-- Bookmarks Tab -->
      <div v-if="activeTab === 'bookmarks'" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div v-if="!bookmarks.length" class="text-center py-12 text-gray-400 text-sm">{{ $t('profile.no_bookmarks') }}</div>
        <div v-else>
          <div v-for="b in bookmarks" :key="b.id" class="px-5 py-3.5 border-b border-gray-50 last:border-0">
            <router-link :to="b.url || '#'" class="text-sm text-gray-800 hover:text-red-600 line-clamp-1 transition">
              {{ b.title }}
            </router-link>
            <p class="text-xs text-gray-400 mt-1">{{ formatDate(b.created_at) }}</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Not Found -->
    <div v-else class="text-center py-20">
      <div class="text-5xl mb-4">
        <svg class="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
      </div>
      <p class="text-gray-400">{{ $t('profile.not_found') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const route = useRoute()
const authStore = useAuthStore()
const { $t } = useLangStore()

const profile = ref(null)
const posts = ref([])
const comments = ref([])
const bookmarks = ref([])
const loading = ref(true)
const activeTab = ref('posts')

const friendStatus = ref(null)
const friendLoading = ref(false)

const tabs = [
  { key: 'posts', label: $t('profile.posts') },
  { key: 'comments', label: $t('profile.comments') },
  { key: 'bookmarks', label: $t('profile.bookmarks') },
]

const isMyProfile = computed(() =>
  authStore.user && (authStore.user.username === route.params.username)
)

async function checkFriendship() {
  if (isMyProfile.value || !profile.value?.id || !authStore.user) {
    friendStatus.value = null
    return
  }
  try {
    const { data } = await axios.get(`/api/friends/check/${profile.value.id}`)
    friendStatus.value = data.status
  } catch {
    friendStatus.value = 'none'
  }
}

async function sendFriendRequest() {
  if (!profile.value?.id) return
  friendLoading.value = true
  try {
    await axios.post(`/api/friends/request/${profile.value.id}`)
    friendStatus.value = 'request_sent'
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.request_failed'))
  } finally {
    friendLoading.value = false
  }
}

async function acceptFriendRequest() {
  if (!profile.value?.id) return
  friendLoading.value = true
  try {
    await axios.post(`/api/friends/accept/${profile.value.id}`)
    friendStatus.value = 'friends'
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.accept_failed'))
  } finally {
    friendLoading.value = false
  }
}

async function rejectFriendRequest() {
  if (!profile.value?.id) return
  friendLoading.value = true
  try {
    await axios.post(`/api/friends/reject/${profile.value.id}`)
    friendStatus.value = 'none'
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.reject_failed'))
  } finally {
    friendLoading.value = false
  }
}

async function removeFriend() {
  if (!profile.value?.id) return
  if (!confirm($t('friends.confirm_remove'))) return
  friendLoading.value = true
  try {
    await axios.delete(`/api/friends/${profile.value.id}`)
    friendStatus.value = 'none'
  } catch (e) {
    alert(e?.response?.data?.message || $t('friends.remove_failed'))
  } finally {
    friendLoading.value = false
  }
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR')
}

async function loadProfile() {
  loading.value = true
  try {
    const [profileRes, postsRes] = await Promise.all([
      axios.get(`/api/profile/${route.params.username}`),
      isMyProfile.value ? axios.get('/api/profile/me/posts') : Promise.resolve({ data: { data: [] } }),
    ])
    profile.value = profileRes.data
    posts.value = postsRes.data.data || []
    await checkFriendship()
    // Load comments/bookmarks if my profile
    if (isMyProfile.value) {
      try {
        const [commentsRes, bookmarksRes] = await Promise.all([
          axios.get('/api/profile/me/comments'),
          axios.get('/api/profile/me/bookmarks'),
        ])
        comments.value = commentsRes.data.data || []
        bookmarks.value = bookmarksRes.data.data || []
      } catch { /* optional data */ }
    }
  } catch {
    profile.value = null
  }
  loading.value = false
}

onMounted(loadProfile)

watch(() => route.params.username, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) loadProfile()
})
</script>
