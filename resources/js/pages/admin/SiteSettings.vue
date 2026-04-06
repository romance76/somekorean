<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">⚙️ 사이트 설정</h1>
  <div class="bg-white rounded-xl shadow-sm border p-5 space-y-4">
    <div v-for="(val, key) in settings" :key="key" class="flex items-center gap-3">
      <label class="text-sm font-semibold text-gray-700 w-32">{{ key }}</label>
      <input v-model="settings[key]" class="flex-1 border rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-amber-400" />
    </div>
    <button @click="save" class="bg-amber-400 text-amber-900 font-bold px-6 py-2 rounded-lg text-sm hover:bg-amber-500">저장</button>
    <div v-if="msg" class="text-green-600 text-sm">{{ msg }}</div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const settings = ref({}); const msg = ref('')
onMounted(async () => { try { const{data}=await axios.get('/api/admin/settings'); settings.value=data.data||{} }catch{} })
async function save() { try { await axios.put('/api/admin/settings',settings.value); msg.value='저장되었습니다!' }catch{}; setTimeout(()=>msg.value='',3000) }
</script>