<template>
<div>
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-xl font-black text-gray-800">💭 채팅 관리</h1>
  </div>

  <div class="flex gap-4">
    <!-- 왼쪽: 방 리스트 -->
    <div :class="activeRoom ? 'w-2/5' : 'w-full'" class="transition-all">
      <div class="bg-white rounded-xl shadow-sm border p-3 mb-3 flex gap-2">
        <input v-model="search" @keyup.enter="loadRooms(1)" placeholder="방 이름 검색..."
          class="flex-1 border rounded px-3 py-1.5 text-sm" />
        <button @click="loadRooms(1)" class="bg-amber-400 text-amber-900 font-bold px-3 py-1.5 rounded text-sm">검색</button>
        <button @click="createRoom" class="bg-green-500 text-white font-bold px-3 py-1.5 rounded text-sm">+ 새 방</button>
      </div>

      <div v-if="roomsLoading" class="text-center py-8 text-gray-400">로딩중...</div>
      <div v-else-if="!rooms.length" class="text-center py-8 text-gray-400">방 없음</div>
      <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
        <div v-for="r in rooms" :key="r.id"
          @click="openRoom(r)"
          class="border-b last:border-0 px-3 py-3 cursor-pointer hover:bg-amber-50/30 transition"
          :class="activeRoom?.id === r.id ? 'bg-amber-50 border-l-2 border-l-amber-500' : ''">
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <div class="font-semibold text-gray-800 text-sm truncate">{{ r.name || '(이름 없음)' }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">
                <span class="inline-block px-1.5 py-0.5 rounded bg-gray-100 mr-1">{{ r.type }}</span>
                <span>ID: {{ r.id }}</span>
                <span class="ml-2">👥 {{ r.users_count || 0 }}</span>
              </div>
              <div v-if="r.messages?.[0]" class="text-[11px] text-gray-500 mt-1 truncate">
                {{ r.messages[0].user?.nickname || r.messages[0].user?.name || '?' }}: {{ r.messages[0].content }}
              </div>
            </div>
            <button @click.stop="deleteRoom(r)" class="text-red-400 hover:text-red-600 text-xs flex-shrink-0">🗑</button>
          </div>
        </div>
      </div>

      <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
        <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="loadRooms(pg)"
          class="px-3 py-1 rounded text-sm"
          :class="pg === page ? 'bg-amber-400 text-amber-900 font-bold' : 'bg-white border text-gray-600'">{{ pg }}</button>
      </div>
    </div>

    <!-- 오른쪽: 방 상세 -->
    <div v-if="activeRoom" class="w-3/5">
      <div class="bg-white rounded-xl shadow-sm border sticky top-4">
        <!-- 헤더 -->
        <div class="px-4 py-3 border-b bg-amber-50 flex items-center justify-between">
          <div>
            <div class="font-black text-amber-800">💬 {{ activeRoom.name || '(이름 없음)' }}</div>
            <div class="text-[10px] text-amber-700">ID: {{ activeRoom.id }} · 멤버: {{ roomDetail?.members?.length || 0 }} · 차단: {{ roomDetail?.bans?.length || 0 }}</div>
          </div>
          <button @click="activeRoom = null" class="text-amber-700 text-lg">✕</button>
        </div>

        <!-- 탭 -->
        <div class="flex border-b">
          <button v-for="t in subTabs" :key="t.key" @click="subTab = t.key"
            class="flex-1 px-3 py-2.5 text-xs font-bold border-b-2 transition"
            :class="subTab === t.key ? 'border-amber-500 text-amber-700' : 'border-transparent text-gray-400'">
            {{ t.icon }} {{ t.label }}
          </button>
        </div>

        <!-- 💬 메시지 탭 -->
        <div v-if="subTab === 'messages'" class="p-3 max-h-[600px] overflow-y-auto">
          <div v-if="detailLoading" class="text-center py-8 text-gray-400">로딩중...</div>
          <div v-else-if="!roomDetail?.messages?.length" class="text-center py-8 text-gray-400">메시지 없음</div>
          <div v-else class="space-y-2">
            <div v-for="m in [...roomDetail.messages].reverse()" :key="m.id"
              class="flex items-start gap-2 p-2 rounded hover:bg-gray-50"
              :class="m.type === 'system' ? 'bg-amber-50' : ''">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-bold text-gray-700">{{ m.user?.nickname || m.user?.name || '?' }}</span>
                  <span class="text-[9px] text-gray-400">{{ fmt(m.created_at) }}</span>
                  <span v-if="m.type === 'system'" class="text-[9px] px-1 py-0.5 bg-amber-200 text-amber-800 rounded">SYSTEM</span>
                </div>
                <div class="text-xs text-gray-800 mt-0.5 break-words">{{ m.content }}</div>
              </div>
              <button @click="deleteMessage(m)" class="text-red-300 hover:text-red-500 text-xs flex-shrink-0">🗑</button>
            </div>
          </div>
        </div>

        <!-- 👥 멤버 탭 -->
        <div v-else-if="subTab === 'members'" class="p-3">
          <div v-if="detailLoading" class="text-center py-8 text-gray-400">로딩중...</div>
          <div v-else>
            <div class="text-xs font-bold text-gray-600 mb-2">📋 참가자 ({{ roomDetail?.members?.length || 0 }})</div>
            <div v-if="!roomDetail?.members?.length" class="text-center py-4 text-gray-400 text-sm">멤버 없음</div>
            <div v-else class="space-y-2 mb-4">
              <div v-for="u in roomDetail.members" :key="u.id"
                class="flex items-center justify-between gap-2 p-2 border rounded">
                <div class="flex-1 min-w-0">
                  <div class="text-xs font-semibold truncate">{{ u.nickname || u.name }}</div>
                  <div class="text-[10px] text-gray-400 truncate">{{ u.email }}</div>
                  <div class="text-[9px] text-gray-400">가입: {{ fmt(u.joined_at) }}</div>
                </div>
                <div class="flex gap-1 flex-shrink-0">
                  <button @click="kickMember(u)" class="text-[10px] bg-yellow-100 text-yellow-700 px-2 py-1 rounded font-bold hover:bg-yellow-200">👋 강퇴</button>
                  <button @click="banMember(u)" class="text-[10px] bg-red-100 text-red-700 px-2 py-1 rounded font-bold hover:bg-red-200">🚫 차단</button>
                </div>
              </div>
            </div>

            <!-- 차단 목록 -->
            <div v-if="roomDetail?.bans?.length">
              <div class="text-xs font-bold text-gray-600 mb-2 border-t pt-3">🚫 차단된 유저 ({{ roomDetail.bans.length }})</div>
              <div class="space-y-2">
                <div v-for="u in roomDetail.bans" :key="'b-'+u.id"
                  class="flex items-center justify-between gap-2 p-2 border border-red-200 bg-red-50 rounded">
                  <div class="flex-1 min-w-0">
                    <div class="text-xs font-semibold truncate">{{ u.nickname || u.name }}</div>
                    <div class="text-[10px] text-gray-400 truncate">{{ u.email }}</div>
                    <div v-if="u.reason" class="text-[10px] text-red-600">사유: {{ u.reason }}</div>
                  </div>
                  <button @click="unbanMember(u)" class="text-[10px] bg-green-100 text-green-700 px-2 py-1 rounded font-bold hover:bg-green-200">🔓 해제</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 📢 공지 작성 탭 -->
        <div v-else-if="subTab === 'announce'" class="p-4">
          <div class="text-xs font-bold text-gray-700 mb-2">📢 공지 내용</div>
          <textarea v-model="announceText" rows="5" placeholder="공지 내용을 입력하세요..."
            class="w-full border rounded px-3 py-2 text-sm resize-none"></textarea>
          <div class="flex justify-end mt-3">
            <button @click="sendAnnounce" :disabled="!announceText.trim() || announcing"
              class="bg-amber-400 text-amber-900 font-bold px-5 py-2 rounded text-sm disabled:opacity-50">
              {{ announcing ? '전송중...' : '📢 공지 발송' }}
            </button>
          </div>
          <div class="text-[10px] text-gray-400 mt-2">* 공지는 시스템 메시지로 채팅방에 표시됩니다.</div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const rooms = ref([])
const roomsLoading = ref(true)
const page = ref(1)
const lastPage = ref(1)
const search = ref('')

const activeRoom = ref(null)
const roomDetail = ref(null)
const detailLoading = ref(false)

const subTabs = [
  { key: 'messages', icon: '💬', label: '메시지' },
  { key: 'members', icon: '👥', label: '멤버' },
  { key: 'announce', icon: '📢', label: '공지' },
]
const subTab = ref('messages')

const announceText = ref('')
const announcing = ref(false)

function fmt(v) {
  if (!v) return '-'
  try { return new Date(v).toLocaleString('ko-KR', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) }
  catch { return v }
}

async function loadRooms(p = 1) {
  roomsLoading.value = true
  page.value = p
  try {
    const { data } = await axios.get('/api/admin/chat/rooms', { params: { page: p, search: search.value } })
    rooms.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
  } catch (e) {}
  roomsLoading.value = false
}

async function createRoom() {
  const name = prompt('새 채팅방 이름을 입력하세요:')
  if (!name) return
  try {
    await axios.post('/api/admin/chat/rooms', { name, type: 'group' })
    loadRooms(1)
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function deleteRoom(r) {
  if (!confirm(`"${r.name || '방 #' + r.id}"을(를) 삭제하시겠습니까?\n모든 메시지와 멤버 정보가 사라집니다.`)) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${r.id}`)
    rooms.value = rooms.value.filter(x => x.id !== r.id)
    if (activeRoom.value?.id === r.id) { activeRoom.value = null; roomDetail.value = null }
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function openRoom(r) {
  activeRoom.value = r
  subTab.value = 'messages'
  await loadRoomDetail()
}

async function loadRoomDetail() {
  if (!activeRoom.value) return
  detailLoading.value = true
  try {
    const { data } = await axios.get(`/api/admin/chat/rooms/${activeRoom.value.id}`)
    roomDetail.value = data.data || null
  } catch (e) {}
  detailLoading.value = false
}

async function deleteMessage(m) {
  if (!confirm('이 메시지를 삭제할까요?')) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${activeRoom.value.id}/messages/${m.id}`)
    roomDetail.value.messages = roomDetail.value.messages.filter(x => x.id !== m.id)
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function kickMember(u) {
  if (!confirm(`${u.nickname || u.name} 님을 방에서 강퇴할까요?\n(재입장 가능)`)) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${activeRoom.value.id}/members/${u.id}`)
    await loadRoomDetail()
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function banMember(u) {
  const reason = prompt(`${u.nickname || u.name} 님을 차단합니다.\n사유를 입력하세요(선택):`) ?? null
  if (reason === null) return
  try {
    await axios.post(`/api/admin/chat/rooms/${activeRoom.value.id}/ban/${u.id}`, { reason })
    await loadRoomDetail()
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function unbanMember(u) {
  if (!confirm(`${u.nickname || u.name} 님의 차단을 해제할까요?`)) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${activeRoom.value.id}/ban/${u.id}`)
    await loadRoomDetail()
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function sendAnnounce() {
  if (!announceText.value.trim()) return
  announcing.value = true
  try {
    await axios.post(`/api/admin/chat/rooms/${activeRoom.value.id}/announce`, { content: announceText.value })
    announceText.value = ''
    subTab.value = 'messages'
    await loadRoomDetail()
  } catch (e) { alert(e.response?.data?.message || '실패') }
  announcing.value = false
}

onMounted(() => loadRooms(1))
</script>
