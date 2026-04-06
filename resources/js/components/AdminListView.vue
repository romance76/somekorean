<template>
<div>
  <!-- 타이틀 -->
  <h1 v-if="title" class="text-xl font-black text-gray-800 mb-4">{{ icon }} {{ title }}</h1>

  <!-- 검색 + 필터 -->
  <div class="bg-white rounded-xl shadow-sm border p-3 mb-4">
    <div class="flex flex-wrap gap-2">
      <slot name="filters"></slot>
      <form @submit.prevent="load()" class="flex-1 flex gap-1 min-w-[150px]">
        <input v-model="search" type="text" placeholder="제목/작성자 검색..." class="flex-1 border rounded-lg px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-amber-400" />
        <button type="submit" class="bg-amber-400 text-amber-900 font-bold px-3 py-1.5 rounded-lg text-xs">검색</button>
      </form>
    </div>
    <div class="text-[10px] text-gray-400 mt-1">전체 {{ total }}건</div>
  </div>

  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
  <div v-else class="flex gap-4">
    <!-- 왼쪽: 목록 -->
    <div :class="activeItem ? 'w-1/2' : 'w-full'">
      <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b"><tr>
            <th class="px-3 py-2 text-left text-xs text-gray-500 w-8">#</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">{{ titleCol }}</th>
            <th v-for="col in extraCols" :key="col.key" v-show="!activeItem" class="px-3 py-2 text-left text-xs text-gray-500">{{ col.label }}</th>
            <th class="px-3 py-2 text-left text-xs text-gray-500">작성자</th>
            <th class="px-3 py-2 text-xs text-gray-500">👁</th>
            <th class="px-3 py-2 text-xs text-gray-500">날짜</th>
            <th class="px-3 py-2 text-xs text-gray-500">관리</th>
          </tr></thead>
          <tbody>
            <tr v-for="item in items" :key="item.id"
              class="border-b last:border-0 hover:bg-amber-50/30 cursor-pointer transition"
              :class="activeItem?.id===item.id ? 'bg-amber-50 border-l-2 border-l-amber-500' : ''"
              @click="openItem(item)">
              <td class="px-3 py-2 text-xs text-gray-400">{{ item.id }}</td>
              <td class="px-3 py-2.5 max-w-[250px]">
                <div class="truncate text-sm font-medium text-gray-800">{{ item.title || item.name }}</div>
                <div class="text-[10px] text-gray-400 truncate mt-0.5">{{ (item.content || item.description || '').slice(0, 60) }}{{ (item.content || item.description || '').length > 60 ? '...' : '' }}</div>
              </td>
              <td v-for="col in extraCols" :key="col.key" v-show="!activeItem" class="px-3 py-2.5">
                <span class="text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-semibold">{{ getNestedVal(item, col.key) }}</span>
              </td>
              <td class="px-3 py-2.5">
                <button @click.stop="$emit('openUser', item.user || {id: item.user_id})" class="text-xs text-blue-600 hover:underline">{{ item.user?.name || '-' }}</button>
              </td>
              <td class="px-3 py-2.5 text-center text-xs text-gray-400">{{ item.view_count || 0 }}</td>
              <td class="px-3 py-2.5 text-[10px] text-gray-400">{{ (item.created_at || item.published_at || '')?.slice(0,10) }}</td>
              <td class="px-3 py-2.5 text-center" @click.stop>
                <button @click="deleteItem(item)" class="text-xs text-red-400 hover:text-red-600">🗑</button>
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

    <!-- 오른쪽: 인라인 상세 뷰 -->
    <div v-if="activeItem" class="w-1/2">
      <div class="bg-white rounded-xl shadow-sm border overflow-hidden sticky top-4">
        <div class="px-4 py-3 border-b flex items-center justify-between bg-amber-50">
          <span class="font-bold text-sm text-amber-900">상세 보기</span>
          <button @click="activeItem=null" class="text-gray-400 hover:text-gray-600 text-lg">✕</button>
        </div>
        <div class="px-4 py-3">
          <h2 class="text-lg font-bold text-gray-900">{{ activeItem.title || activeItem.name }}</h2>
          <div class="flex flex-wrap items-center gap-3 mt-2 text-xs text-gray-400">
            <button @click="$emit('openUser', activeItem.user || {id: activeItem.user_id})" class="text-blue-600 hover:underline font-semibold">{{ activeItem.user?.name || '-' }}</button>
            <span v-if="activeItem.company">🏢 {{ activeItem.company }}</span>
            <span v-if="activeItem.city">📍 {{ activeItem.city }}, {{ activeItem.state }}</span>
            <span v-if="activeItem.source">📰 {{ activeItem.source }}</span>
            <span v-if="activeItem.category">📋 {{ typeof activeItem.category === 'object' ? activeItem.category.name : activeItem.category }}</span>
            <span v-if="activeItem.price !== undefined && activeItem.price !== null">${{ Number(activeItem.price).toLocaleString() }}</span>
            <span v-if="activeItem.salary_min">💰 ${{ activeItem.salary_min }}~${{ activeItem.salary_max }}/{{ activeItem.salary_type }}</span>
            <span>👁 {{ activeItem.view_count || 0 }}</span>
            <span>{{ (activeItem.created_at || activeItem.published_at || '')?.slice(0,10) }}</span>
          </div>
        </div>
        <!-- 이미지 -->
        <div v-if="activeItem.image_url" class="px-4 pb-2">
          <img :src="activeItem.image_url" class="w-full max-h-48 object-cover rounded-lg" @error="e=>e.target.style.display='none'" />
        </div>
        <!-- 본문 -->
        <div class="px-4 py-4 border-t text-sm text-gray-700 leading-relaxed whitespace-pre-wrap max-h-[500px] overflow-y-auto">{{ activeItem.content || activeItem.description || '(내용 없음)' }}</div>
        <!-- 연락처 -->
        <div v-if="activeItem.contact_phone || activeItem.contact_email || activeItem.phone" class="px-4 py-3 border-t bg-amber-50 text-sm">
          <div v-if="activeItem.contact_phone || activeItem.phone">📱 {{ activeItem.contact_phone || activeItem.phone }}</div>
          <div v-if="activeItem.contact_email || activeItem.email">📧 {{ activeItem.contact_email || activeItem.email }}</div>
          <div v-if="activeItem.website">🌐 {{ activeItem.website }}</div>
        </div>
        <!-- 관리 버튼 -->
        <div class="px-4 py-3 border-t flex gap-2">
          <button @click="deleteItem(activeItem); activeItem=null" class="text-xs bg-red-100 text-red-700 px-3 py-1.5 rounded-lg hover:bg-red-200">🗑 삭제</button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  icon: { type: String, default: '📋' },
  title: { type: String, required: true },
  apiUrl: { type: String, required: true },
  titleCol: { type: String, default: '제목' },
  extraCols: { type: Array, default: () => [] },
})

const emit = defineEmits(['openUser'])

const items = ref([]); const loading = ref(true)
const page = ref(1); const lastPage = ref(1); const total = ref(0)
const search = ref(''); const activeItem = ref(null)

function getNestedVal(obj, key) {
  return key.split('.').reduce((o, k) => o?.[k], obj) || '-'
}

async function openItem(item) {
  try { const { data } = await axios.get(`${props.apiUrl}/${item.id}`); activeItem.value = data.data }
  catch { activeItem.value = item }
}

async function load(p=1) {
  loading.value = true; page.value = p
  const params = { page: p, per_page: 20 }
  if (search.value) params.search = search.value
  try {
    const { data } = await axios.get(props.apiUrl, { params })
    items.value = data.data?.data || data.data || []
    lastPage.value = data.data?.last_page || 1
    total.value = data.data?.total || items.value.length
  } catch {}
  loading.value = false
}

async function deleteItem(item) {
  if (!confirm('정말 삭제하시겠습니까?')) return
  try { await axios.delete(`${props.apiUrl}/${item.id}`); items.value = items.value.filter(x => x.id !== item.id); total.value-- } catch {}
}

onMounted(() => load())
</script>
