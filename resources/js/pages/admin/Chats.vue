<template>
  <div class="space-y-5">
    <h2 class="text-lg font-bold text-gray-800">채팅방 관리</h2>

    <!-- Stats -->
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">전체 채팅방</div>
        <div class="text-2xl font-black text-gray-800">{{ stats.total_rooms || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">오늘 메시지</div>
        <div class="text-2xl font-black text-blue-600">{{ stats.messages_today || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">활성 채팅방</div>
        <div class="text-2xl font-black text-green-600">{{ stats.active_rooms || 0 }}</div>
      </div>
    </div>

    <!-- Room List -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100"><h3 class="font-bold text-gray-800 text-sm">채팅방 목록</h3></div>
      <div class="overflow-x-auto"><table class="w-full text-sm"><thead class="bg-gray-50 border-b border-gray-200"><tr>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">채팅방명</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">유형</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">참여자</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">메시지</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">마지막 활동</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">관리</th>
      </tr></thead><tbody class="divide-y divide-gray-50">
        <tr v-for="room in rooms" :key="room.id" class="hover:bg-gray-50">
          <td class="px-4 py-3 font-medium text-gray-800">{{ room.name || '1:1 채팅' }}</td>
          <td class="px-4 py-3 text-gray-600 text-xs">{{ room.type || 'group' }}</td>
          <td class="px-4 py-3 text-right text-gray-700">{{ room.members_count || 0 }}</td>
          <td class="px-4 py-3 text-right text-gray-700">{{ room.messages_count || 0 }}</td>
          <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(room.last_message_at || room.updated_at) }}</td>
          <td class="px-4 py-3 text-right">
            <button @click="del(room)" class="text-xs px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100">삭제</button>
          </td>
        </tr>
      </tbody></table></div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const rooms = ref([]), stats = ref({})
function formatDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '' }
async function loadData() { try { const { data } = await axios.get('/api/admin/chats'); rooms.value = data.rooms || data.data || []; stats.value = data.stats || {} } catch {} }
async function del(room) { if (!confirm('삭제?')) return; try { await axios.delete(`/api/admin/chats/${room.id}`); rooms.value = rooms.value.filter(r => r.id !== room.id) } catch {} }
onMounted(loadData)
</script>
