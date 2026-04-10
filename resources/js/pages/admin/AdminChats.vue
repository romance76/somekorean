<template>
<div>
  <h2 class="text-lg font-bold text-gray-800 mb-4">💬 채팅 관리</h2>

  <!-- 상단 툴바 -->
  <div v-if="!activeRoom" class="flex gap-2 mb-3">
    <input v-model="search" @keyup.enter="loadRooms()" placeholder="방 이름 검색..." class="flex-1 border rounded-lg px-3 py-1.5 text-sm" />
    <button @click="loadRooms()" class="bg-gray-100 text-gray-700 px-3 py-1.5 rounded-lg text-xs">검색</button>
    <button @click="showCreate=true" class="bg-amber-400 text-amber-900 font-bold px-3 py-1.5 rounded-lg text-xs">+ 방 개설</button>
  </div>

  <!-- 방 목록 -->
  <div v-if="!activeRoom">
    <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
    <div v-else-if="!rooms.length" class="text-center py-8 text-gray-400">채팅방이 없습니다</div>
    <div v-else class="bg-white rounded-lg border overflow-hidden">
      <div v-for="r in rooms" :key="r.id" class="border-b px-4 py-3 hover:bg-amber-50/30 cursor-pointer flex items-center justify-between" @click="openRoom(r)">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-sm font-bold text-gray-800">{{ r.name }}</span>
            <span class="text-[10px] bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full">{{ r.type }}</span>
            <span class="text-[10px] text-amber-600">👥 {{ r.users_count }}</span>
          </div>
          <div v-if="r.messages?.[0]" class="text-xs text-gray-500 mt-0.5 truncate">
            {{ r.messages[0].user?.name }}: {{ r.messages[0].content }}
          </div>
        </div>
        <div class="flex items-center gap-2 ml-3">
          <span class="text-[10px] text-gray-400">{{ formatDate(r.updated_at) }}</span>
          <button @click.stop="deleteRoom(r)" class="text-red-400 hover:text-red-600 text-xs">🗑️</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 방 상세 -->
  <div v-else>
    <button @click="activeRoom=null; roomDetail=null" class="text-xs text-gray-500 hover:text-gray-700 mb-3">← 방 목록</button>
    <div v-if="roomDetail" class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- 왼쪽: 메시지 -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg border p-3 mb-3">
          <h3 class="font-bold text-sm text-gray-800">🏠 {{ roomDetail.room.name }}</h3>
          <div class="text-xs text-gray-500">{{ roomDetail.room.type }} · 멤버 {{ roomDetail.room.users_count }}명</div>
        </div>

        <!-- 공지 입력 -->
        <div class="bg-amber-50 rounded-lg border border-amber-200 p-3 mb-3">
          <div class="text-xs font-bold text-amber-700 mb-2">📢 공지 발송</div>
          <textarea v-model="announceText" rows="2" placeholder="모두에게 공지를 발송합니다..." class="w-full border rounded-lg px-3 py-2 text-sm resize-none"></textarea>
          <button @click="sendAnnounce" :disabled="!announceText.trim()" class="mt-2 bg-amber-400 text-amber-900 font-bold px-4 py-1.5 rounded-lg text-xs disabled:opacity-50">공지 발송</button>
        </div>

        <!-- 메시지 목록 -->
        <div class="bg-white rounded-lg border">
          <div class="px-3 py-2 border-b font-bold text-xs text-gray-700">최근 메시지</div>
          <div v-if="!roomDetail.messages.length" class="px-3 py-6 text-center text-xs text-gray-400">메시지가 없습니다</div>
          <div v-else class="max-h-96 overflow-y-auto">
            <div v-for="m in roomDetail.messages" :key="m.id" class="px-3 py-2 border-b last:border-0 group hover:bg-gray-50">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2 min-w-0 flex-1">
                  <span class="text-xs font-bold text-gray-700">{{ m.user?.name }}</span>
                  <span class="text-[10px] text-gray-400">{{ formatDateTime(m.created_at) }}</span>
                  <span v-if="m.type==='system'" class="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full">시스템</span>
                </div>
                <button @click="deleteMessage(m)" class="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 text-[10px]">🗑️</button>
              </div>
              <div class="text-xs text-gray-600 mt-0.5">{{ m.content }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 오른쪽: 멤버 + 차단 -->
      <div>
        <div class="bg-white rounded-lg border mb-3">
          <div class="px-3 py-2 border-b font-bold text-xs text-gray-700">👥 멤버 ({{ roomDetail.members.length }})</div>
          <div class="max-h-60 overflow-y-auto">
            <div v-for="u in roomDetail.members" :key="u.id" class="px-3 py-2 border-b last:border-0 flex items-center justify-between">
              <div>
                <div class="text-xs font-bold">{{ u.nickname || u.name }}</div>
                <div class="text-[10px] text-gray-400">{{ u.email }}</div>
              </div>
              <div class="flex gap-1">
                <button @click="kickMember(u)" class="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full hover:bg-amber-200">강퇴</button>
                <button @click="banMember(u)" class="text-[10px] bg-red-100 text-red-700 px-2 py-0.5 rounded-full hover:bg-red-200">차단</button>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg border">
          <div class="px-3 py-2 border-b font-bold text-xs text-red-700">🚫 차단 목록 ({{ roomDetail.bans.length }})</div>
          <div v-if="!roomDetail.bans.length" class="px-3 py-4 text-center text-[10px] text-gray-400">차단된 사용자 없음</div>
          <div v-else>
            <div v-for="u in roomDetail.bans" :key="u.id" class="px-3 py-2 border-b last:border-0 flex items-center justify-between">
              <div>
                <div class="text-xs font-bold">{{ u.nickname || u.name }}</div>
                <div class="text-[10px] text-red-500">{{ u.reason }}</div>
              </div>
              <button @click="unbanMember(u)" class="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full hover:bg-gray-200">해제</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 방 개설 모달 -->
  <div v-if="showCreate" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showCreate=false">
    <div class="bg-white rounded-xl p-5 w-full max-w-md">
      <h3 class="font-bold text-gray-800 mb-3">💬 새 채팅방 개설</h3>
      <input v-model="newRoomName" placeholder="방 이름" class="w-full border rounded-lg px-3 py-2 text-sm mb-3" />
      <select v-model="newRoomType" class="w-full border rounded-lg px-3 py-2 text-sm mb-3">
        <option value="group">그룹 채팅</option>
        <option value="public">공개 채팅</option>
      </select>
      <div class="flex gap-2">
        <button @click="createRoom" :disabled="!newRoomName.trim()" class="flex-1 bg-amber-400 text-amber-900 font-bold py-2 rounded-lg text-sm disabled:opacity-50">개설</button>
        <button @click="showCreate=false" class="px-4 py-2 text-gray-500 text-sm">취소</button>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const rooms = ref([])
const loading = ref(true)
const search = ref('')
const activeRoom = ref(null)
const roomDetail = ref(null)
const showCreate = ref(false)
const newRoomName = ref('')
const newRoomType = ref('group')
const announceText = ref('')

function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString('ko-KR') : '' }
function formatDateTime(dt) { return dt ? new Date(dt).toLocaleString('ko-KR') : '' }

async function loadRooms() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/admin/chat/rooms', { params: { search: search.value } })
    rooms.value = data.data?.data || []
  } catch {}
  loading.value = false
}

async function openRoom(r) {
  activeRoom.value = r
  try {
    const { data } = await axios.get(`/api/admin/chat/rooms/${r.id}`)
    roomDetail.value = data.data
  } catch {}
}

async function createRoom() {
  try {
    await axios.post('/api/admin/chat/rooms', { name: newRoomName.value, type: newRoomType.value })
    showCreate.value = false
    newRoomName.value = ''
    loadRooms()
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function deleteRoom(r) {
  if (!confirm(`"${r.name}" 방을 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${r.id}`)
    loadRooms()
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function sendAnnounce() {
  try {
    await axios.post(`/api/admin/chat/rooms/${activeRoom.value.id}/announce`, { content: announceText.value })
    announceText.value = ''
    openRoom(activeRoom.value)
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function kickMember(u) {
  if (!confirm(`${u.name} 님을 강퇴하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${activeRoom.value.id}/members/${u.id}`)
    openRoom(activeRoom.value)
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function banMember(u) {
  const reason = prompt(`${u.name} 님을 차단합니다. 사유를 입력하세요:`)
  if (reason === null) return
  try {
    await axios.post(`/api/admin/chat/rooms/${activeRoom.value.id}/ban/${u.id}`, { reason })
    openRoom(activeRoom.value)
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function unbanMember(u) {
  if (!confirm(`${u.name} 님의 차단을 해제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${activeRoom.value.id}/ban/${u.id}`)
    openRoom(activeRoom.value)
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

async function deleteMessage(m) {
  if (!confirm('이 메시지를 삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${activeRoom.value.id}/messages/${m.id}`)
    openRoom(activeRoom.value)
  } catch (e) { alert(e.response?.data?.message || '실패') }
}

onMounted(loadRooms)
</script>
