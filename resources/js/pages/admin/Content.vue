<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">📝 콘텐츠 관리</h1>
  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
  <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 border-b"><tr>
        <th class="px-3 py-2 text-left text-xs text-gray-500">제목</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">게시판</th>
        <th class="px-3 py-2 text-left text-xs text-gray-500">작성자</th>
        <th class="px-3 py-2 text-xs text-gray-500">조회</th>
        <th class="px-3 py-2 text-xs text-gray-500">관리</th>
      </tr></thead>
      <tbody>
        <tr v-for="p in posts" :key="p.id" class="border-b last:border-0 hover:bg-amber-50/30" :class="p.is_hidden ? 'opacity-50' : ''">
          <td class="px-3 py-2.5 truncate max-w-[200px]">
            <span v-if="p.is_pinned" class="text-amber-500 mr-1">📌</span>{{ p.title }}
          </td>
          <td class="px-3 py-2.5 text-xs text-gray-500">{{ p.board?.name }}</td>
          <td class="px-3 py-2.5 text-xs text-gray-500">{{ p.user?.name }}</td>
          <td class="px-3 py-2.5 text-center text-xs text-gray-400">{{ p.view_count }}</td>
          <td class="px-3 py-2.5 text-center space-x-1">
            <button @click="pinPost(p)" class="text-xs" :class="p.is_pinned?'text-amber-500':'text-gray-400 hover:text-amber-500'">📌</button>
            <button @click="hidePost(p)" class="text-xs" :class="p.is_hidden?'text-green-500':'text-gray-400 hover:text-red-500'">{{ p.is_hidden ? '👁' : '🚫' }}</button>
            <button @click="deletePost(p)" class="text-xs text-red-400 hover:text-red-600">🗑</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
    <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="load(pg)"
      class="px-3 py-1 rounded text-sm" :class="pg===page?'bg-amber-400 text-amber-900 font-bold':'bg-white border text-gray-600'">{{ pg }}</button>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const posts = ref([]); const loading = ref(true); const page = ref(1); const lastPage = ref(1)
async function load(p=1) { loading.value=true; page.value=p; try { const{data}=await axios.get('/api/admin/posts',{params:{page:p}}); posts.value=data.data?.data||[]; lastPage.value=data.data?.last_page||1 }catch{}; loading.value=false }
async function pinPost(p) { try { await axios.post(`/api/admin/posts/${p.id}/pin`); p.is_pinned=!p.is_pinned } catch {} }
async function hidePost(p) { try { await axios.post(`/api/admin/posts/${p.id}/hide`); p.is_hidden=!p.is_hidden } catch {} }
async function deletePost(p) { if(!confirm('삭제?'))return; try { await axios.delete(`/api/admin/posts/${p.id}`); posts.value=posts.value.filter(x=>x.id!==p.id) } catch {} }
onMounted(()=>load())
</script>
