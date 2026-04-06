<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">🔒 보안</h1>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
    <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <div class="px-4 py-3 border-b font-bold text-sm text-gray-800">🚫 IP 차단 목록</div>
      <div v-for="ban in ipBans" :key="ban.id" class="px-4 py-2.5 border-b last:border-0 flex justify-between text-sm">
        <div><span class="font-mono text-gray-800">{{ ban.ip_address }}</span> <span class="text-xs text-gray-400 ml-2">{{ ban.reason }}</span></div>
        <button @click="removeBan(ban)" class="text-red-400 text-xs">삭제</button>
      </div>
      <div v-if="!ipBans.length" class="px-4 py-4 text-sm text-gray-400 text-center">차단된 IP 없음</div>
      <div class="px-4 py-3 border-t flex gap-2">
        <input v-model="newIp" placeholder="IP 주소" class="flex-1 border rounded px-2 py-1 text-sm" />
        <button @click="addBan" class="bg-red-500 text-white px-3 py-1 rounded text-xs font-bold">차단</button>
      </div>
    </div>
    <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <div class="px-4 py-3 border-b font-bold text-sm text-gray-800">⚠️ 신고 목록</div>
      <div v-for="r in reports" :key="r.id" class="px-4 py-2.5 border-b last:border-0 text-sm">
        <div class="text-gray-800">{{ r.reason }}</div>
        <div class="text-xs text-gray-400">{{ r.reportable_type }} #{{ r.reportable_id }} · {{ r.status }}</div>
      </div>
      <div v-if="!reports.length" class="px-4 py-4 text-sm text-gray-400 text-center">신고 없음</div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const ipBans = ref([]); const reports = ref([]); const newIp = ref('')
onMounted(async () => {
  try { const{data}=await axios.get('/api/admin/ip-bans'); ipBans.value=data.data||[] }catch{}
  try { const{data}=await axios.get('/api/admin/reports'); reports.value=data.data?.data||data.data||[] }catch{}
})
async function addBan() { if(!newIp.value)return; try { await axios.post('/api/admin/ip-bans',{ip_address:newIp.value,reason:'관리자 차단'}); newIp.value=''; const{data}=await axios.get('/api/admin/ip-bans'); ipBans.value=data.data||[] }catch{} }
async function removeBan(b) { try { await axios.delete('/api/admin/ip-bans/'+b.id); ipBans.value=ipBans.value.filter(x=>x.id!==b.id) }catch{} }
</script>