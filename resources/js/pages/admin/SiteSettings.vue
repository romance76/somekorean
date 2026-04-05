<template>
  <div class="space-y-5">
    <h2 class="text-lg font-bold text-gray-800">사이트 설정</h2>

    <!-- Logo -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">로고</h3>
      <div class="flex items-center gap-4">
        <div class="w-16 h-16 bg-gray-100 rounded-xl flex items-center justify-center overflow-hidden">
          <img v-if="settings.logo_url" :src="settings.logo_url" class="w-full h-full object-contain" @error="e => e.target.style.display='none'" />
          <span v-else class="text-gray-400 text-sm">No logo</span>
        </div>
        <div>
          <input type="file" ref="logoInput" accept="image/*" class="hidden" @change="uploadLogo" />
          <button @click="$refs.logoInput.click()" class="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-red-700 transition">로고 변경</button>
        </div>
      </div>
    </div>

    <!-- Basic Settings -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <h3 class="font-bold text-gray-800 text-sm mb-4">기본 설정</h3>
      <div class="space-y-3 max-w-lg">
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">사이트 이름</label>
          <input v-model="settings.site_name" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">사이트 설명</label>
          <textarea v-model="settings.site_description" rows="3" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 resize-none" />
        </div>
      </div>
    </div>

    <!-- Key-Value Settings -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold text-gray-800 text-sm">커스텀 설정</h3>
        <button @click="addSetting" class="text-xs bg-gray-100 text-gray-600 px-3 py-1.5 rounded-lg hover:bg-gray-200 transition">+ 추가</button>
      </div>
      <div class="space-y-2">
        <div v-for="(s, idx) in customSettings" :key="idx" class="flex gap-2 items-center">
          <input v-model="s.key" type="text" placeholder="키" class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-red-500" />
          <input v-model="s.value" type="text" placeholder="값" class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-red-500" />
          <button @click="customSettings.splice(idx, 1)" class="text-red-400 hover:text-red-600">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Save -->
    <button @click="saveSettings" :disabled="saving" class="bg-red-600 text-white px-6 py-3 rounded-xl text-sm font-bold hover:bg-red-700 disabled:opacity-50 transition">
      {{ saving ? '저장 중...' : '설정 저장' }}
    </button>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const settings = ref({ site_name: '', site_description: '', logo_url: '' })
const customSettings = ref([])
const saving = ref(false), logoInput = ref(null)
async function loadSettings() { try { const { data } = await axios.get('/api/admin/settings'); settings.value = { ...settings.value, ...data }; customSettings.value = data.custom || [] } catch {} }
function addSetting() { customSettings.value.push({ key: '', value: '' }) }
async function saveSettings() {
  saving.value = true
  try { await axios.put('/api/admin/settings', { ...settings.value, custom: customSettings.value }); alert('저장되었습니다') } catch (e) { alert(e.response?.data?.message || '저장 실패') }
  saving.value = false
}
async function uploadLogo(e) {
  const file = e.target.files[0]; if (!file) return
  const fd = new FormData(); fd.append('logo', file)
  try { const { data } = await axios.post('/api/admin/settings/logo', fd, { headers: { 'Content-Type': 'multipart/form-data' } }); settings.value.logo_url = data.url || data.logo_url } catch { alert('업로드 실패') }
}
onMounted(loadSettings)
</script>
