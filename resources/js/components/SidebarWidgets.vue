<template>
<div class="space-y-3">
  <!-- 많이 본 글 (조회수 순) -->
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="flex border-b">
      <button @click="popTab='views'" class="flex-1 py-2.5 text-xs font-bold transition"
        :class="popTab==='views' ? 'text-amber-700 border-b-2 border-amber-500 bg-amber-50' : 'text-gray-400'">많이 본 {{ label }}</button>
      <button @click="popTab='latest'" class="flex-1 py-2.5 text-xs font-bold transition"
        :class="popTab==='latest' ? 'text-amber-700 border-b-2 border-amber-500 bg-amber-50' : 'text-gray-400'">최신 {{ label }}</button>
    </div>
    <div class="py-1">
      <component v-for="(item, i) in (popTab==='views' ? popularItems : latestItems)" :key="item.id"
        :is="inline ? 'button' : 'RouterLink'" :to="inline ? undefined : detailPath + item.id"
        @click="inline && emit('select', item)"
        class="flex items-start gap-2 px-3 py-2 hover:bg-amber-50/50 transition w-full text-left">
        <span class="text-xs font-bold flex-shrink-0 w-5 text-center" :class="i < 3 ? 'text-amber-600' : 'text-gray-400'">{{ i + 1 }}</span>
        <span class="text-xs text-gray-700 leading-snug line-clamp-2">{{ item.title || item.name }}</span>
      </component>
      <div v-if="!popularItems.length && !latestItems.length" class="py-4 text-center text-xs text-gray-400">데이터 로딩중...</div>
    </div>
  </div>

  <!-- 좋아할 기사/추천 글 -->
  <div v-if="recommendItems.length" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="px-3 py-2.5 border-b font-bold text-xs text-gray-800">👍 {{ recommendLabel }}</div>
    <div class="py-1">
      <component v-for="item in recommendItems" :key="item.id"
        :is="inline ? 'button' : 'RouterLink'" :to="inline ? undefined : detailPath + item.id"
        @click="inline && emit('select', item)"
        class="block px-3 py-2 hover:bg-amber-50/50 transition w-full text-left">
        <div class="text-xs text-gray-700 line-clamp-2 leading-snug">{{ item.title || item.name }}</div>
        <div class="text-[10px] text-gray-400 mt-0.5">{{ item.user?.name || item.company || item.source || '' }}</div>
      </component>
    </div>
  </div>

  <!-- 실시간/바로가기 -->
  <div v-if="quickLabel" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="px-3 py-2.5 border-b font-bold text-xs text-gray-800">⚡ {{ quickLabel }}</div>
    <div class="py-1">
      <component v-for="item in quickItems" :key="item.id"
        :is="inline ? 'button' : 'RouterLink'" :to="inline ? undefined : detailPath + item.id"
        @click="inline && emit('select', item)"
        class="flex items-center gap-2 px-3 py-1.5 hover:bg-amber-50/50 transition w-full text-left">
        <span class="text-[10px] text-amber-500">●</span>
        <span class="text-xs text-gray-600 truncate">{{ item.title || item.name }}</span>
      </component>
      <div v-if="!quickItems.length" class="py-3 text-center text-xs text-gray-400">준비 중</div>
    </div>
  </div>

  <!-- 빠른 링크 -->
  <div v-if="links.length" class="bg-white rounded-xl shadow-sm border border-gray-100 p-3">
    <div class="font-bold text-xs text-gray-800 mb-2">📋 바로가기</div>
    <RouterLink v-for="link in links" :key="link.to" :to="link.to"
      class="block text-xs text-gray-600 hover:text-amber-700 py-1 transition">
      {{ link.icon }} {{ link.label }}
    </RouterLink>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const props = defineProps({
  apiUrl: { type: String, required: true },
  detailPath: { type: String, required: true },
  currentId: { type: [Number, String], default: 0 },
  label: { type: String, default: '글' },
  recommendLabel: { type: String, default: '추천 글' },
  quickLabel: { type: String, default: '' },
  links: { type: Array, default: () => [] },
  filterParams: { type: Object, default: () => ({}) },
  inline: { type: Boolean, default: false }, // true면 클릭 시 emit
})

const emit = defineEmits(['select'])

const popTab = ref('views')
const popularItems = ref([])
const latestItems = ref([])
const recommendItems = ref([])
const quickItems = ref([])

onMounted(async () => {
  try {
    const [popRes, latRes, recRes] = await Promise.allSettled([
      axios.get(props.apiUrl, { params: { sort: 'popular', per_page: 10, ...props.filterParams } }),
      axios.get(props.apiUrl, { params: { sort: 'latest', per_page: 10, ...props.filterParams } }),
      axios.get(props.apiUrl, { params: { per_page: 5 } }),
    ])

    const cid = Number(props.currentId)
    if (popRes.status === 'fulfilled')
      popularItems.value = (popRes.value.data?.data?.data || []).filter(i => i.id !== cid).slice(0, 10)
    if (latRes.status === 'fulfilled')
      latestItems.value = (latRes.value.data?.data?.data || []).filter(i => i.id !== cid).slice(0, 10)
    if (recRes.status === 'fulfilled')
      recommendItems.value = (recRes.value.data?.data?.data || []).filter(i => i.id !== cid).slice(0, 5)

    // 실시간 = 최근 24시간 내 최신
    quickItems.value = latestItems.value.slice(0, 6)
  } catch {}
})
</script>
