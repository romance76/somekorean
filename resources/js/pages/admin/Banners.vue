<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold text-gray-800">배너/광고 관리</h2>
      <button @click="openCreate" class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-700 transition">+ 배너 추가</button>
    </div>

    <!-- Banner List -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="!banners.length" class="text-center py-12 text-gray-400 text-sm">배너가 없습니다</div>
      <div v-else>
        <div v-for="(banner, idx) in banners" :key="banner.id" class="px-5 py-4 border-b border-gray-50 last:border-0 flex items-center gap-4">
          <!-- Reorder -->
          <div class="flex flex-col gap-0.5 flex-shrink-0">
            <button @click="moveUp(idx)" :disabled="idx === 0" class="text-gray-400 hover:text-gray-600 disabled:opacity-30">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7"/></svg>
            </button>
            <button @click="moveDown(idx)" :disabled="idx === banners.length - 1" class="text-gray-400 hover:text-gray-600 disabled:opacity-30">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>
          </div>
          <!-- Preview -->
          <div class="w-20 h-12 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
            <img v-if="banner.image_url" :src="banner.image_url" class="w-full h-full object-cover" @error="e => e.target.style.display='none'" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-800 text-sm truncate">{{ banner.title }}</p>
            <p class="text-xs text-gray-400">{{ banner.position }} · {{ banner.start_date }} ~ {{ banner.end_date }}</p>
          </div>
          <span class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="banner.is_active ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-500'">{{ banner.is_active ? '활성' : '비활성' }}</span>
          <div class="flex gap-1 flex-shrink-0">
            <button @click="openEdit(banner)" class="text-xs px-2 py-1 rounded bg-blue-50 text-blue-600 hover:bg-blue-100">수정</button>
            <button @click="toggleActive(banner)" class="text-xs px-2 py-1 rounded bg-yellow-50 text-yellow-600 hover:bg-yellow-100">{{ banner.is_active ? '비활성' : '활성' }}</button>
            <button @click="del(banner)" class="text-xs px-2 py-1 rounded bg-red-50 text-red-600 hover:bg-red-100">삭제</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4" @click.self="showModal = false">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
        <h3 class="font-bold text-gray-800 text-lg mb-4">{{ editing ? '배너 수정' : '배너 추가' }}</h3>
        <div class="space-y-3">
          <div><label class="block text-sm font-medium text-gray-700 mb-1">제목</label><input v-model="form.title" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" /></div>
          <div><label class="block text-sm font-medium text-gray-700 mb-1">이미지</label><input type="file" ref="imgInput" accept="image/*" @change="onImageChange" class="w-full text-sm text-gray-500" /></div>
          <div><label class="block text-sm font-medium text-gray-700 mb-1">링크 URL</label><input v-model="form.link_url" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" /></div>
          <div class="grid grid-cols-2 gap-3">
            <div><label class="block text-sm font-medium text-gray-700 mb-1">위치</label><select v-model="form.position" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm bg-white"><option value="top">상단</option><option value="sidebar">사이드바</option><option value="middle">중간</option></select></div>
            <div><label class="block text-sm font-medium text-gray-700 mb-1">시작일</label><input v-model="form.start_date" type="date" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm" /></div>
          </div>
          <div><label class="block text-sm font-medium text-gray-700 mb-1">종료일</label><input v-model="form.end_date" type="date" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm" /></div>
          <div class="flex justify-end gap-2 pt-2">
            <button @click="showModal = false" class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm hover:bg-gray-50">취소</button>
            <button @click="saveBanner" :disabled="!form.title" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-bold hover:bg-red-700 disabled:opacity-50">저장</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const banners = ref([]), showModal = ref(false), editing = ref(null), imageFile = ref(null)
const form = ref({ title: '', link_url: '', position: 'top', start_date: '', end_date: '' })
function openCreate() { editing.value = null; form.value = { title: '', link_url: '', position: 'top', start_date: '', end_date: '' }; showModal.value = true }
function openEdit(b) { editing.value = b; form.value = { title: b.title, link_url: b.link_url, position: b.position, start_date: b.start_date, end_date: b.end_date }; showModal.value = true }
function onImageChange(e) { imageFile.value = e.target.files[0] }
async function loadBanners() { try { const { data } = await axios.get('/api/admin/banners'); banners.value = data.data || data || [] } catch {} }
async function saveBanner() {
  const fd = new FormData(); Object.entries(form.value).forEach(([k, v]) => { if (v) fd.append(k, v) }); if (imageFile.value) fd.append('image', imageFile.value)
  try { if (editing.value) { await axios.post(`/api/admin/banners/${editing.value.id}`, fd) } else { await axios.post('/api/admin/banners', fd) }; showModal.value = false; imageFile.value = null; await loadBanners() } catch (e) { alert(e.response?.data?.message || '저장 실패') }
}
async function toggleActive(b) { try { await axios.post(`/api/admin/banners/${b.id}/toggle`); b.is_active = !b.is_active } catch {} }
async function del(b) { if (!confirm('삭제?')) return; try { await axios.delete(`/api/admin/banners/${b.id}`); banners.value = banners.value.filter(x => x.id !== b.id) } catch {} }
async function moveUp(idx) { if (idx === 0) return; const arr = [...banners.value]; [arr[idx-1], arr[idx]] = [arr[idx], arr[idx-1]]; banners.value = arr; try { await axios.post('/api/admin/banners/reorder', { ids: banners.value.map(b => b.id) }) } catch {} }
async function moveDown(idx) { if (idx >= banners.value.length - 1) return; const arr = [...banners.value]; [arr[idx], arr[idx+1]] = [arr[idx+1], arr[idx]]; banners.value = arr; try { await axios.post('/api/admin/banners/reorder', { ids: banners.value.map(b => b.id) }) } catch {} }
onMounted(loadBanners)
</script>
