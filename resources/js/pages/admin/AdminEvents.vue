<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between"><h2 class="text-lg font-bold text-gray-800">이벤트 관리</h2><span class="text-sm text-gray-400">총 {{ total }}건</span></div>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-wrap gap-3">
      <input v-model="search" type="text" placeholder="검색..." @input="debounceLoad" class="flex-1 min-w-[200px] border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
    </div>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="overflow-x-auto"><table class="w-full text-sm"><thead class="bg-gray-50 border-b border-gray-200"><tr>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">이벤트명</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">장소</th>
        <th class="text-left px-4 py-3 font-semibold text-gray-600">일시</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">참가자</th>
        <th class="text-right px-4 py-3 font-semibold text-gray-600">관리</th>
      </tr></thead><tbody class="divide-y divide-gray-50">
        <tr v-for="item in items" :key="item.id" class="hover:bg-gray-50">
          <td class="px-4 py-3 font-medium text-gray-800 max-w-xs truncate">{{ item.title }}</td>
          <td class="px-4 py-3 text-gray-600 text-xs">{{ item.location || '-' }}</td>
          <td class="px-4 py-3 text-gray-600 text-xs">{{ formatDate(item.event_date || item.start_date) }}</td>
          <td class="px-4 py-3 text-right text-gray-700">{{ item.attendees_count || 0 }}</td>
          <td class="px-4 py-3 text-right"><div class="flex justify-end gap-1">
            <button @click="toggleVis(item)" class="text-xs px-2 py-1 rounded bg-yellow-50 text-yellow-600 hover:bg-yellow-100">{{ item.is_hidden ? '공개' : '숨김' }}</button>
            <button @click="del(item)" class="text-xs px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100">삭제</button>
          </div></td>
        </tr>
      </tbody></table></div>
      <div v-if="totalPages > 1" class="px-4 py-3 border-t border-gray-100 flex justify-center gap-1">
        <button v-for="p in Math.min(totalPages, 10)" :key="p" @click="page = p; loadItems()" class="w-8 h-8 rounded text-xs font-medium" :class="p === page ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">{{ p }}</button>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
const items = ref([]), search = ref(''), page = ref(1), total = ref(0); let dt = null
const totalPages = computed(() => Math.ceil(total.value / 20))
function formatDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '' }
function debounceLoad() { clearTimeout(dt); dt = setTimeout(() => { page.value = 1; loadItems() }, 400) }
async function loadItems() { try { const { data } = await axios.get('/api/admin/events', { params: { search: search.value, page: page.value } }); items.value = data.data || []; total.value = data.total || data.meta?.total || 0 } catch {} }
async function toggleVis(i) { try { await axios.post(`/api/admin/events/${i.id}/toggle`); i.is_hidden = !i.is_hidden } catch {} }
async function del(i) { if (!confirm('삭제?')) return; try { await axios.delete(`/api/admin/events/${i.id}`); items.value = items.value.filter(x => x.id !== i.id) } catch {} }
onMounted(loadItems)
</script>
