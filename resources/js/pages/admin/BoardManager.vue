<template>
<div>
  <div class="flex items-center justify-between mb-4">
    <h1 class="text-xl font-black text-gray-800">📋 게시판 관리</h1>
    <button @click="showCreate=true" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm">+ 추가</button>
  </div>
  <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
    <div v-for="b in boards" :key="b.id" class="px-4 py-3 border-b last:border-0 flex items-center justify-between">
      <div><span class="font-semibold text-gray-800">{{ b.name }}</span> <span class="text-xs text-gray-400 ml-2">/{{ b.slug }}</span></div>
      <div class="flex gap-2">
        <span class="text-xs" :class="b.is_active?'text-green-500':'text-red-500'">{{ b.is_active ? '활성' : '비활성' }}</span>
        <button @click="deleteBoard(b)" class="text-xs text-red-400 hover:text-red-600">삭제</button>
      </div>
    </div>
  </div>
  <div v-if="showCreate" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" @click.self="showCreate=false">
    <div class="bg-white rounded-xl p-5 w-full max-w-sm shadow-xl space-y-3">
      <h3 class="font-bold">게시판 추가</h3>
      <input v-model="newBoard.name" placeholder="이름" class="w-full border rounded-lg px-3 py-2 text-sm" />
      <input v-model="newBoard.slug" placeholder="slug (영문)" class="w-full border rounded-lg px-3 py-2 text-sm" />
      <div class="flex gap-2"><button @click="createBoard" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm flex-1">추가</button><button @click="showCreate=false" class="text-gray-500 px-4">취소</button></div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
const boards = ref([]); const showCreate = ref(false); const newBoard = reactive({name:'',slug:''})
async function load() { try { const{data}=await axios.get('/api/admin/boards'); boards.value=data.data||[] }catch{} }
async function createBoard() { try { await axios.post('/api/admin/boards',newBoard); showCreate.value=false; newBoard.name=''; newBoard.slug=''; load() }catch{} }
async function deleteBoard(b) { if(!confirm('삭제?'))return; try { await axios.delete('/api/admin/boards/'+b.id); load() }catch{} }
onMounted(load)
</script>