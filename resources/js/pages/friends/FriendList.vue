<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <!-- Header -->
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <div class="bg-gradient-to-r from-blue-600 to-blue-500 text-white px-6 py-5 rounded-2xl">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-black">친구</h1>
            <p class="text-blue-100 text-sm mt-0.5">{{ friends.length }}명의 친구</p>
          </div>
          <span class="bg-white/20 text-white text-sm font-bold px-3 py-1.5 rounded-xl">
            요청 {{ pendingRequests.length }}개
          </span>
        </div>
      </div>
    </div>

    <div class="max-w-[1200px] mx-auto px-4 py-5 space-y-4">

      <!-- 탭 -->
      <div class="bg-white rounded-2xl shadow-sm p-1 flex gap-1">
        <button v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          class="flex-1 py-2.5 text-sm font-bold rounded-xl transition"
          :class="activeTab === tab.key
            ? 'bg-blue-600 text-white shadow-sm'
            : 'text-gray-500 hover:bg-gray-50'">
          {{ tab.label }}
          <span v-if="tab.count > 0"
            class="ml-1 text-xs px-1.5 py-0.5 rounded-full"
            :class="activeTab === tab.key ? 'bg-white/20' : 'bg-gray-100'">
            {{ tab.count }}
          </span>
        </button>
      </div>

      <!-- 친구 검색 (친구 목록 탭에서만) -->
      <div v-if="activeTab === 'friends'" class="bg-white rounded-2xl shadow-sm p-4">
        <h2 class="font-bold text-gray-800 text-sm mb-3">친구 찾기</h2>
        <div class="flex gap-2">
          <input v-model="searchQuery" type="text" placeholder="이름 또는 @아이디로 검색..."
            class="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400"
            @input="searchUsers" />
          <button @click="searchUsers" class="bg-blue-600 text-white px-4 py-2.5 rounded-xl text-sm font-bold hover:bg-blue-700">
            검색
          </button>
        </div>

        <!-- 검색 결과 -->
        <div v-if="searchResults.length > 0" class="mt-3 space-y-2">
          <div v-for="user in searchResults" :key="user.id"
            class="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 border border-gray-100">
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-600 flex-shrink-0 overflow-hidden">
              <img v-if="user.avatar" :src="user.avatar" class="w-full h-full object-cover" />
              <span v-else>{{ (user.name || '?')[0] }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-800 text-sm">{{ user.name }}</p>
              <p class="text-gray-400 text-xs">@{{ user.username }} · {{ user.region || '지역 미등록' }}</p>
            </div>
            <button @click="sendRequest(user.id)"
              :disabled="user.requestSent || user.isFriend"
              class="text-xs px-3 py-1.5 rounded-lg font-bold flex-shrink-0 transition"
              :class="user.isFriend ? 'bg-gray-100 text-gray-400 cursor-default'
                : user.requestSent ? 'bg-green-100 text-green-600 cursor-default'
                : 'bg-blue-600 text-white hover:bg-blue-700'">
              {{ user.isFriend ? '이미 친구' : user.requestSent ? '요청됨' : '+ 친구 추가' }}
            </button>
          </div>
        </div>
        <div v-else-if="searchQuery && !searching" class="mt-3 text-center text-gray-400 text-sm py-4">
          검색 결과가 없습니다
        </div>
      </div>

      <!-- 친구 목록 탭 -->
      <div v-if="activeTab === 'friends'" class="space-y-3">
        <div v-if="loading" class="text-center py-8 text-gray-400 text-sm">불러오는 중...</div>
        <div v-else-if="friends.length === 0" class="bg-white rounded-2xl shadow-sm text-center py-12">
          <p class="text-4xl mb-3">👋</p>
          <p class="text-gray-600 font-semibold mb-1">아직 친구가 없어요</p>
          <p class="text-gray-400 text-sm">위에서 친구를 검색해서 추가해보세요!</p>
        </div>

        <!-- 친구 카드 그리드 -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div v-for="friend in friends" :key="friend.id"
            class="bg-white rounded-2xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition">
            <!-- 상단: 프로필 -->
            <div class="flex items-center gap-3 mb-3">
              <div class="relative flex-shrink-0">
                <router-link :to="`/profile/${friend.username}`">
                  <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-600 overflow-hidden">
                    <img v-if="friend.avatar" :src="friend.avatar" class="w-full h-full object-cover" />
                    <span v-else>{{ (friend.name || '?')[0] }}</span>
                  </div>
                </router-link>
                <span class="absolute bottom-0 right-0 w-3 h-3 bg-green-400 border-2 border-white rounded-full"></span>
              </div>
              <div class="flex-1 min-w-0">
                <router-link :to="`/profile/${friend.username}`" class="font-semibold text-gray-800 text-sm hover:text-blue-600 block truncate">
                  {{ friend.name }}
                </router-link>
                <p class="text-gray-400 text-xs">@{{ friend.username }}</p>
                <p class="text-xs text-gray-500">{{ friend.region || '지역 미등록' }}</p>
              </div>
              <!-- 삭제 -->
              <button @click="removeFriend(friend.id)"
                class="w-7 h-7 rounded-full bg-gray-50 text-gray-300 flex items-center justify-center hover:bg-red-50 hover:text-red-400 transition text-xs flex-shrink-0"
                title="친구 삭제">
                ✕
              </button>
            </div>

            <!-- 하단: 액션 버튼들 -->
            <div class="flex flex-wrap gap-1.5">
              <button @click="openChat(friend)"
                class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 text-blue-600 hover:bg-blue-100 transition">
                <span>💬</span> 채팅
              </button>
              <button @click="openKakao(friend)"
                class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-yellow-50 text-yellow-700 hover:bg-yellow-100 transition">
                <span>📱</span> 카카오
              </button>
              <button @click="openTelegram(friend)"
                :disabled="!friend.telegram_id"
                class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold transition"
                :class="friend.telegram_id
                  ? 'bg-sky-50 text-sky-600 hover:bg-sky-100'
                  : 'bg-gray-50 text-gray-300 cursor-not-allowed'">
                <span>✈️</span> 텔레그램
              </button>
              <button @click="startCall(friend)"
                class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-green-50 text-green-600 hover:bg-green-100 transition">
                <span>📞</span> 통화
              </button>
              <button @click="downloadVCard(friend)"
                class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-purple-50 text-purple-600 hover:bg-purple-100 transition">
                <span>📋</span> 연락처
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 받은 요청 탭 -->
      <div v-if="activeTab === 'received'" class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div v-if="pendingRequests.length === 0" class="text-center py-12">
          <p class="text-4xl mb-3">📨</p>
          <p class="text-gray-600 font-semibold mb-1">받은 요청이 없습니다</p>
          <p class="text-gray-400 text-sm">새로운 친구 요청이 오면 여기에 표시됩니다</p>
        </div>
        <div v-else class="divide-y divide-gray-50">
          <div v-for="req in pendingRequests" :key="req.id" class="flex items-center gap-3 px-5 py-4">
            <div class="w-11 h-11 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-600 flex-shrink-0 overflow-hidden">
              <img v-if="req.requester?.avatar" :src="req.requester.avatar" class="w-full h-full object-cover" />
              <span v-else>{{ (req.requester?.name || '?')[0] }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-800 text-sm">{{ req.requester?.name }}</p>
              <p class="text-gray-400 text-xs">@{{ req.requester?.username }} · {{ req.requester?.region || '지역 미등록' }}</p>
            </div>
            <div class="flex gap-2 flex-shrink-0">
              <button @click="acceptRequest(req.requester_id)"
                class="bg-blue-600 text-white text-xs px-4 py-2 rounded-lg font-bold hover:bg-blue-700 transition">
                수락
              </button>
              <button @click="rejectRequest(req.requester_id)"
                class="bg-gray-100 text-gray-500 text-xs px-4 py-2 rounded-lg font-bold hover:bg-gray-200 transition">
                거절
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 보낸 요청 탭 -->
      <div v-if="activeTab === 'sent'" class="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div v-if="sentRequests.length === 0" class="text-center py-12">
          <p class="text-4xl mb-3">📤</p>
          <p class="text-gray-600 font-semibold mb-1">보낸 요청이 없습니다</p>
          <p class="text-gray-400 text-sm">친구 요청을 보내면 여기에 표시됩니다</p>
        </div>
        <div v-else class="divide-y divide-gray-50">
          <div v-for="req in sentRequests" :key="req.id" class="flex items-center gap-3 px-5 py-4">
            <div class="w-11 h-11 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-600 flex-shrink-0 overflow-hidden">
              <img v-if="req.recipient?.avatar" :src="req.recipient.avatar" class="w-full h-full object-cover" />
              <span v-else>{{ (req.recipient?.name || '?')[0] }}</span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-gray-800 text-sm">{{ req.recipient?.name }}</p>
              <p class="text-gray-400 text-xs">@{{ req.recipient?.username }} · {{ req.recipient?.region || '지역 미등록' }}</p>
            </div>
            <span class="text-xs bg-yellow-100 text-yellow-700 px-3 py-1.5 rounded-lg font-bold flex-shrink-0">
              대기중
            </span>
          </div>
        </div>
      </div>

    </div>

    <!-- 통화 모달 -->
    <Transition name="fade">
      <div v-if="callModal" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50 px-4">
        <div class="bg-white rounded-3xl p-8 max-w-sm w-full text-center shadow-2xl">
          <div class="w-20 h-20 mx-auto rounded-full bg-blue-100 overflow-hidden flex items-center justify-center text-3xl font-bold text-blue-600 mb-4">
            <img v-if="callModal.friend.avatar" :src="callModal.friend.avatar" class="w-full h-full object-cover" />
            <span v-else>{{ (callModal.friend.name || '?')[0] }}</span>
          </div>
          <h2 class="text-xl font-black text-gray-800 mb-1">{{ callModal.friend.name }}</h2>
          <p class="text-gray-400 text-sm mb-2">📞 음성통화</p>
          <div class="flex gap-2 my-4 justify-center">
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay:0s"></div>
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay:0.15s"></div>
            <div class="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style="animation-delay:0.3s"></div>
          </div>
          <p class="text-gray-500 text-sm mb-6">연결 중... 상대방을 호출하고 있어요</p>
          <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-3 mb-5 text-left">
            <p class="text-yellow-800 text-xs font-bold">서비스 준비 중</p>
            <p class="text-yellow-700 text-xs mt-1">WebRTC 음성/화상통화 기능은 현재 개발 중입니다. 빠른 시일 내 출시 예정!</p>
          </div>
          <button @click="callModal = null" class="w-full bg-red-500 text-white font-bold py-3 rounded-2xl hover:bg-red-600">
            통화 종료
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const friends         = ref([])
const pendingRequests = ref([])
const sentRequests    = ref([])
const searchQuery     = ref('')
const searchResults   = ref([])
const loading         = ref(true)
const searching       = ref(false)
const callModal       = ref(null)
const activeTab       = ref('friends')

const tabs = computed(() => [
  { key: 'friends',  label: '친구 목록',  count: friends.value.length },
  { key: 'received', label: '받은 요청',  count: pendingRequests.value.length },
  { key: 'sent',     label: '보낸 요청',  count: sentRequests.value.length },
])

// Load data
async function loadFriends() {
  loading.value = true
  try {
    const [friendsRes, pendingRes, sentRes] = await Promise.allSettled([
      axios.get('/api/friends'),
      axios.get('/api/friends/pending'),
      axios.get('/api/friends/sent'),
    ])
    if (friendsRes.status === 'fulfilled') {
      friends.value = friendsRes.value.data?.data || friendsRes.value.data || []
    }
    if (pendingRes.status === 'fulfilled') {
      pendingRequests.value = pendingRes.value.data?.data || pendingRes.value.data || []
    }
    if (sentRes.status === 'fulfilled') {
      sentRequests.value = sentRes.value.data?.data || sentRes.value.data || []
    }
  } catch (e) {}
  loading.value = false
}

// Search
let searchTimer = null
function searchUsers() {
  clearTimeout(searchTimer)
  if (!searchQuery.value.trim()) { searchResults.value = []; return }
  searchTimer = setTimeout(async () => {
    searching.value = true
    try {
      const { data } = await axios.get('/api/friends/search', { params: { q: searchQuery.value } })
      const list = data?.data || data || []
      const friendIds = new Set(friends.value.map(f => f.id))
      searchResults.value = list.map(u => ({
        ...u,
        isFriend: friendIds.has(u.id),
        requestSent: false,
      }))
    } catch (e) {} finally {
      searching.value = false
    }
  }, 400)
}

// Friend actions
async function sendRequest(userId) {
  try {
    await axios.post(`/api/friends/request/${userId}`)
    const user = searchResults.value.find(u => u.id === userId)
    if (user) user.requestSent = true
  } catch (e) {
    alert(e?.response?.data?.message || '요청 실패')
  }
}

async function acceptRequest(requesterId) {
  try {
    await axios.post(`/api/friends/accept/${requesterId}`)
    pendingRequests.value = pendingRequests.value.filter(r => r.requester_id !== requesterId)
    await loadFriends()
  } catch (e) {}
}

async function rejectRequest(requesterId) {
  try {
    await axios.post(`/api/friends/reject/${requesterId}`)
    pendingRequests.value = pendingRequests.value.filter(r => r.requester_id !== requesterId)
  } catch (e) {}
}

async function removeFriend(userId) {
  if (!confirm('친구를 삭제할까요?')) return
  try {
    await axios.delete(`/api/friends/${userId}`)
    friends.value = friends.value.filter(f => f.id !== userId)
  } catch (e) {}
}

// 채팅 (1:1 DM)
async function openChat(friend) {
  try {
    const { data } = await axios.post('/api/chat/rooms', {
      name: `DM: ${friend.name}`,
      type: 'friend',
      participant_id: friend.id,
    })
    const slug = data?.slug || data?.room?.slug
    if (slug) {
      router.push(`/chat/${slug}`)
    } else {
      router.push('/chat')
    }
  } catch (e) {
    router.push('/chat')
  }
}

// 카카오톡
function openKakao(friend) {
  if (friend.kakao_id) {
    window.open(`kakaotalk://chat/sendto?user_id=${friend.kakao_id}`, '_blank')
  } else {
    window.open('https://open.kakao.com/', '_blank')
  }
}

// 텔레그램
function openTelegram(friend) {
  if (friend.telegram_id) {
    const tid = friend.telegram_id.replace(/^@/, '')
    window.open(`tg://resolve?domain=${tid}`, '_blank')
  }
}

// 통화
async function startCall(friend) {
  callModal.value = { friend }
  try {
    await axios.post('/api/calls/request', { receiver_id: friend.id })
  } catch (e) {}
}

// vCard 다운로드
function downloadVCard(friend) {
  const vcard = `BEGIN:VCARD
VERSION:3.0
FN:${friend.name || ''}
TEL:${friend.phone || ''}
EMAIL:${friend.email || ''}
END:VCARD`
  const blob = new Blob([vcard], { type: 'text/vcard' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${friend.name || 'contact'}.vcf`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(loadFriends)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
