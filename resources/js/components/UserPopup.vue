<template>
<!-- 미니 프로필 팝업 -->
<div v-if="show && user" class="fixed inset-0 z-50 flex items-center justify-center" @click.self="$emit('close')">
  <div class="absolute inset-0 bg-black/30"></div>
  <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-xs overflow-hidden animate-in">
    <!-- 헤더 배경 -->
    <div class="bg-gradient-to-r from-amber-400 to-orange-400 h-16 relative">
      <button @click="$emit('close')" class="absolute top-2 right-2 text-white/80 hover:text-white text-lg">✕</button>
    </div>

    <!-- 아바타 + 이름 -->
    <div class="px-5 pb-4 -mt-8 text-center">
      <div class="w-16 h-16 rounded-full bg-amber-500 text-white flex items-center justify-center text-2xl font-black border-4 border-white shadow mx-auto overflow-hidden">
        <img v-if="user.avatar" :src="user.avatar" class="w-full h-full object-cover" @error="e=>e.target.style.display='none'" />
        <span v-else>{{ (user.name || '?')[0] }}</span>
      </div>
      <h3 class="text-lg font-bold text-gray-900 mt-2">{{ user.name }}</h3>
      <div v-if="user.nickname" class="text-xs text-gray-400">@{{ user.nickname }}</div>
      <div v-if="user.city" class="text-xs text-gray-500 mt-1">📍 {{ user.city }}, {{ user.state }}</div>
      <div v-if="user.bio" class="text-xs text-gray-500 mt-1 line-clamp-2">{{ user.bio }}</div>

      <!-- 온라인 상태 -->
      <div class="flex items-center justify-center gap-1 mt-2">
        <span class="w-2 h-2 rounded-full" :class="onlineClass"></span>
        <span class="text-[10px]" :class="onlineTextClass">{{ onlineText }}</span>
      </div>
    </div>

    <!-- 액션 버튼 -->
    <div class="px-5 pb-5 space-y-2">
      <!-- 본인이면 프로필 수정 -->
      <template v-if="isMe">
        <RouterLink to="/profile/edit" @click="$emit('close')" class="block w-full text-center bg-amber-400 text-amber-900 font-bold py-2.5 rounded-xl text-sm hover:bg-amber-500">✏️ 프로필 수정</RouterLink>
      </template>
      <template v-else>
        <!-- 쪽지 (항상 가능) -->
        <button @click="sendMessage" class="w-full bg-blue-500 text-white font-bold py-2.5 rounded-xl text-sm hover:bg-blue-600">✉️ 쪽지 보내기</button>
        <!-- 친구 추가 (allow_friend_request && 아직 친구 아님) -->
        <button v-if="user.allow_friend_request && !isFriend && !isPending" @click="addFriend" :disabled="adding" class="w-full bg-amber-400 text-amber-900 font-bold py-2.5 rounded-xl text-sm hover:bg-amber-500 disabled:opacity-50">{{ adding ? '요청중...' : '👫 친구 추가' }}</button>
        <div v-else-if="isPending" class="text-center text-xs text-gray-400 py-2">⏳ 친구 요청 대기중</div>
        <div v-else-if="isFriend" class="text-center text-xs text-green-600 py-2">✅ 이미 친구입니다</div>
        <div v-else-if="!user.allow_friend_request" class="text-center text-xs text-gray-400 py-2">🔒 친구 요청을 받지 않는 사용자입니다</div>
        <!-- 프로필 보기 -->
        <RouterLink :to="`/profile/${user.id}`" @click="$emit('close')" class="block w-full text-center border border-gray-200 text-gray-600 font-semibold py-2 rounded-xl text-sm hover:bg-gray-50">👤 프로필 보기</RouterLink>
      </template>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const props = defineProps({ show: Boolean, userId: [Number, String] })
const emit = defineEmits(['close'])
const auth = useAuthStore()
const router = useRouter()

const user = ref(null)
const isFriend = ref(false)
const isPending = ref(false)
const adding = ref(false)

const isMe = computed(() => auth.user?.id == props.userId)

const onlineClass = computed(() => {
  if (!user.value?.last_active_at) return 'bg-gray-300'
  const mins = Math.floor((Date.now() - new Date(user.value.last_active_at).getTime()) / 60000)
  if (mins <= 5) return 'bg-green-500'
  if (mins <= 30) return 'bg-yellow-400'
  return 'bg-gray-300'
})

const onlineTextClass = computed(() => {
  if (!user.value?.last_active_at) return 'text-gray-400'
  const mins = Math.floor((Date.now() - new Date(user.value.last_active_at).getTime()) / 60000)
  if (mins <= 5) return 'text-green-600'
  if (mins <= 30) return 'text-yellow-600'
  return 'text-gray-400'
})

const onlineText = computed(() => {
  if (!user.value?.last_active_at) return '오프라인'
  const mins = Math.floor((Date.now() - new Date(user.value.last_active_at).getTime()) / 60000)
  if (mins <= 5) return '온라인'
  if (mins <= 30) return '자리비움'
  if (mins <= 1440) return `${Math.floor(mins / 60)}시간 전`
  return '오프라인'
})

watch(() => props.userId, async (id) => {
  if (!id || !props.show) return
  user.value = null; isFriend.value = false; isPending.value = false
  try {
    const { data } = await axios.get(`/api/users/${id}`)
    user.value = data.data
  } catch {}
  // 친구 상태 확인
  if (auth.isLoggedIn && !isMe.value) {
    try {
      const { data } = await axios.get('/api/friends')
      const list = data.data || []
      isFriend.value = list.some(f => f.friend?.id == id && f.status === 'accepted')
      isPending.value = list.some(f => f.friend?.id == id && f.status === 'pending')
    } catch {}
  }
}, { immediate: true })

async function addFriend() {
  adding.value = true
  try {
    await axios.post(`/api/friends/request/${user.value.id}`, { source: 'community' })
    isPending.value = true
  } catch (e) { alert(e.response?.data?.message || '요청 실패') }
  adding.value = false
}

function sendMessage() {
  emit('close')
  router.push('/messages')
}
</script>

<style scoped>
.animate-in { animation: popIn 0.2s ease-out; }
@keyframes popIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
</style>
