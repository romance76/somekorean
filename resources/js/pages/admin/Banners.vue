<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">📢 광고 관리</h1>

  <!-- ═══ 전체 요약 ═══ -->
  <div class="grid grid-cols-5 gap-2 mb-4">
    <div class="bg-white rounded-xl border p-3 text-center">
      <div class="text-[10px] text-gray-500">전체 입찰</div>
      <div class="text-lg font-black text-gray-800">{{ items.length }}</div>
    </div>
    <div class="bg-white rounded-xl border p-3 text-center">
      <div class="text-[10px] text-gray-500">대기</div>
      <div class="text-lg font-black text-amber-600">{{ items.filter(i=>i.status==='pending').length }}</div>
    </div>
    <div class="bg-white rounded-xl border p-3 text-center">
      <div class="text-[10px] text-gray-500">게시중</div>
      <div class="text-lg font-black text-green-600">{{ items.filter(i=>i.status==='active').length }}</div>
    </div>
    <div class="bg-white rounded-xl border p-3 text-center">
      <div class="text-[10px] text-gray-500">총 수입</div>
      <div class="text-lg font-black text-blue-600">{{ items.reduce((s,i)=>s+(i.bid_amount||i.total_cost||0),0).toLocaleString() }}P</div>
    </div>
    <div class="bg-white rounded-xl border p-3 text-center">
      <div class="text-[10px] text-gray-500">총 클릭</div>
      <div class="text-lg font-black text-purple-600">{{ items.reduce((s,i)=>s+(i.clicks||0),0).toLocaleString() }}</div>
    </div>
  </div>

  <!-- 페이지별 슬롯 현황 요약 -->
  <div class="bg-white rounded-xl border p-4 mb-4">
    <h2 class="text-sm font-bold text-gray-700 mb-3">📊 페이지별 슬롯 현황</h2>
    <div class="flex flex-wrap gap-2">
      <button @click="activePage='all'"
        class="px-3 py-1.5 rounded-lg text-xs font-bold border transition"
        :class="activePage==='all' ? 'bg-amber-400 text-amber-900 border-amber-500' : 'bg-white text-gray-600 border-gray-200 hover:border-amber-300'">
        전체 ({{ items.length }})
      </button>
      <button v-for="pg in pageList" :key="pg.key" @click="activePage=pg.key"
        class="px-3 py-1.5 rounded-lg text-xs font-bold border transition"
        :class="activePage===pg.key ? 'bg-amber-400 text-amber-900 border-amber-500' : 'bg-white text-gray-600 border-gray-200 hover:border-amber-300'">
        {{ pg.icon }} {{ pg.label }}
        <span class="ml-1 text-[10px]" :class="pageAdCount(pg.key) > 0 ? 'text-green-600' : 'text-gray-400'">
          ({{ pageAdCount(pg.key) }})
        </span>
      </button>
    </div>
  </div>

  <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>

  <!-- ═══ 슬롯별 상세 뷰 (카테고리 선택 시) ═══ -->
  <div v-else-if="activePage !== 'all'" class="space-y-4">
    <h2 class="text-sm font-bold text-gray-800">{{ pageIcon(activePage) }} {{ pageLabel(activePage) }} — 슬롯별 입찰 현황</h2>

    <!-- 좌측 슬롯 -->
    <div class="bg-white rounded-xl border overflow-hidden">
      <div class="px-4 py-2 bg-blue-50 border-b font-bold text-xs text-blue-800">📌 좌측 사이드바</div>
      <div v-for="slot in leftSlots" :key="slot.key" class="border-b last:border-0">
        <div class="px-4 py-2 bg-gray-50 flex items-center gap-2">
          <span class="text-sm">{{ slot.icon }}</span>
          <span class="text-xs font-bold text-gray-700">{{ slot.label }}</span>
          <span class="text-[10px] text-gray-400">· 최대 {{ slot.max }}개 · slot_number={{ slot.num }}</span>
          <span class="ml-auto text-[10px] font-bold" :class="slotAds(activePage,'left',slot.num).length ? 'text-green-600' : 'text-gray-400'">
            {{ slotAds(activePage,'left',slot.num).length }}/{{ slot.max }}
          </span>
        </div>
        <div v-if="slotAds(activePage,'left',slot.num).length" class="px-4 py-2 space-y-1.5">
          <div v-for="(ad, idx) in slotAds(activePage,'left',slot.num)" :key="ad.id"
            class="flex items-center gap-3 p-2 rounded-lg" :class="idx===0 ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'">
            <span class="text-xs font-black w-6 text-center" :class="idx===0?'text-yellow-600':idx===1?'text-gray-500':'text-gray-400'">{{ idx+1 }}위</span>
            <div class="w-12 h-8 rounded overflow-hidden bg-gray-200 flex-shrink-0">
              <img :src="ad.image_url" class="w-full h-full object-cover" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs font-bold text-gray-800 truncate">{{ ad.title }}</div>
              <div class="text-[10px] text-gray-400">{{ ad.user?.name }} · {{ ad.geo_scope==='all'?'전국':ad.geo_value }} · {{ ad.auction_month||'-' }}</div>
            </div>
            <div class="text-sm font-black text-amber-700">{{ (ad.bid_amount||0).toLocaleString() }}P</div>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-bold" :class="stCls[ad.status]">{{ stLbl[ad.status] }}</span>
            <div class="flex gap-1">
              <button v-if="ad.status==='pending'" @click="approve(ad)" class="text-[10px] bg-green-500 text-white px-2 py-1 rounded font-bold">승인</button>
              <button v-if="ad.status==='pending'" @click="reject(ad)" class="text-[10px] bg-red-500 text-white px-2 py-1 rounded font-bold">거절</button>
              <button v-if="ad.status==='active'" @click="pause(ad)" class="text-[10px] bg-gray-200 text-gray-600 px-2 py-1 rounded font-bold">중지</button>
              <button @click="remove(ad)" class="text-[10px] text-red-400 hover:text-red-600 px-1">삭제</button>
            </div>
          </div>
        </div>
        <div v-else class="px-4 py-3 text-[10px] text-gray-400">입찰 없음</div>
      </div>
    </div>

    <!-- 우측 슬롯 -->
    <div class="bg-white rounded-xl border overflow-hidden">
      <div class="px-4 py-2 bg-orange-50 border-b font-bold text-xs text-orange-800">📌 우측 사이드바</div>
      <div v-for="slot in rightSlots" :key="slot.key" class="border-b last:border-0">
        <div class="px-4 py-2 bg-gray-50 flex items-center gap-2">
          <span class="text-sm">{{ slot.icon }}</span>
          <span class="text-xs font-bold text-gray-700">{{ slot.label }}</span>
          <span class="text-[10px] text-gray-400">· 최대 {{ slot.max }}개 · slot_number={{ slot.num }}</span>
          <span class="ml-auto text-[10px] font-bold" :class="slotAds(activePage,'right',slot.num).length ? 'text-green-600' : 'text-gray-400'">
            {{ slotAds(activePage,'right',slot.num).length }}/{{ slot.max }}
          </span>
        </div>
        <div v-if="slotAds(activePage,'right',slot.num).length" class="px-4 py-2 space-y-1.5">
          <div v-for="(ad, idx) in slotAds(activePage,'right',slot.num)" :key="ad.id"
            class="flex items-center gap-3 p-2 rounded-lg" :class="idx===0 ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'">
            <span class="text-xs font-black w-6 text-center" :class="idx===0?'text-yellow-600':'text-gray-400'">{{ idx+1 }}위</span>
            <div class="w-12 h-8 rounded overflow-hidden bg-gray-200 flex-shrink-0">
              <img :src="ad.image_url" class="w-full h-full object-cover" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs font-bold text-gray-800 truncate">{{ ad.title }}</div>
              <div class="text-[10px] text-gray-400">{{ ad.user?.name }} · {{ ad.geo_scope==='all'?'전국':ad.geo_value }} · {{ ad.auction_month||'-' }}</div>
            </div>
            <div class="text-sm font-black text-amber-700">{{ (ad.bid_amount||0).toLocaleString() }}P</div>
            <span class="text-[10px] px-2 py-0.5 rounded-full font-bold" :class="stCls[ad.status]">{{ stLbl[ad.status] }}</span>
            <div class="flex gap-1">
              <button v-if="ad.status==='pending'" @click="approve(ad)" class="text-[10px] bg-green-500 text-white px-2 py-1 rounded font-bold">승인</button>
              <button v-if="ad.status==='pending'" @click="reject(ad)" class="text-[10px] bg-red-500 text-white px-2 py-1 rounded font-bold">거절</button>
              <button v-if="ad.status==='active'" @click="pause(ad)" class="text-[10px] bg-gray-200 text-gray-600 px-2 py-1 rounded font-bold">중지</button>
              <button @click="remove(ad)" class="text-[10px] text-red-400 hover:text-red-600 px-1">삭제</button>
            </div>
          </div>
        </div>
        <div v-else class="px-4 py-3 text-[10px] text-gray-400">입찰 없음</div>
      </div>
    </div>
  </div>

  <!-- ═══ 전체 목록 뷰 ═══ -->
  <div v-else-if="!items.length" class="text-center py-8 text-gray-400">광고 신청 없음</div>
  <div v-else class="space-y-2">
    <div v-for="item in items" :key="item.id" class="bg-white rounded-xl border p-3">
      <div class="flex gap-3 items-center">
        <div class="w-20 h-14 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
          <img :src="item.image_url" class="w-full h-full object-cover" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-1.5 flex-wrap">
            <span class="text-[10px] px-2 py-0.5 rounded-full font-bold" :class="stCls[item.status]">{{ stLbl[item.status] }}</span>
            <span class="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full">{{ pageLabel(item.page) }}</span>
            <span class="text-[10px] bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded-full">{{ {left:'좌',right:'우'}[item.position] }}{{ item.slot_number }}</span>
            <span class="text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-bold">{{ (item.bid_amount||item.total_cost||0).toLocaleString() }}P</span>
            <span v-if="item.geo_scope!=='all'" class="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full">{{ item.geo_value }}</span>
          </div>
          <div class="text-xs font-bold text-gray-800 truncate mt-0.5">{{ item.title }}</div>
          <div class="text-[10px] text-gray-400">{{ item.user?.name }} · {{ (item.target_pages||[]).join(', ') || item.page }} · 노출{{ item.impressions||0 }} · 클릭{{ item.clicks||0 }}</div>
        </div>
        <div class="flex gap-1 flex-shrink-0">
          <button v-if="item.status==='pending'" @click="approve(item)" class="text-[10px] bg-green-500 text-white px-2 py-1 rounded font-bold">승인</button>
          <button v-if="item.status==='pending'" @click="reject(item)" class="text-[10px] bg-red-500 text-white px-2 py-1 rounded font-bold">거절</button>
          <button v-if="item.status==='active'" @click="pause(item)" class="text-[10px] bg-gray-200 text-gray-600 px-2 py-1 rounded font-bold">중지</button>
          <button @click="remove(item)" class="text-[10px] text-red-400 hover:text-red-600">삭제</button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const items = ref([])
const loading = ref(true)
const activePage = ref('all')

const pageList = [
  { key: 'home', icon: '🏠', label: '홈' },
  { key: 'community', icon: '💬', label: '커뮤니티' }, { key: 'qa', icon: '❓', label: 'Q&A' },
  { key: 'jobs', icon: '💼', label: '구인구직' }, { key: 'market', icon: '🛒', label: '장터' },
  { key: 'realestate', icon: '🏠', label: '부동산' }, { key: 'directory', icon: '🏪', label: '업소록' },
  { key: 'clubs', icon: '👥', label: '동호회' }, { key: 'news', icon: '📰', label: '뉴스' },
  { key: 'recipes', icon: '🍳', label: '레시피' }, { key: 'groupbuy', icon: '🤝', label: '공동구매' },
  { key: 'events', icon: '🎉', label: '이벤트' },
]

const leftSlots = [
  { key: 'l1', num: 1, icon: '🥇', label: '프리미엄 (고정 1개)', max: 1 },
  { key: 'l2', num: 2, icon: '🥈', label: '스탠다드 (2개 랜덤)', max: 2 },
  { key: 'l3', num: 3, icon: '🥉', label: '이코노미 (5개 랜덤)', max: 5 },
]
const rightSlots = [
  { key: 'r1', num: 1, icon: '🥇', label: '프리미엄 (고정 1개)', max: 1 },
  { key: 'r2', num: 2, icon: '🥉', label: '이코노미 (3개 랜덤)', max: 3 },
]

const stLbl = { pending:'대기', active:'게시중', rejected:'거절', expired:'만료', paused:'중지' }
const stCls = { pending:'bg-amber-100 text-amber-700', active:'bg-green-100 text-green-700', rejected:'bg-red-100 text-red-700', expired:'bg-gray-200 text-gray-500', paused:'bg-gray-200 text-gray-500' }

function pageLabel(key) { return pageList.find(p => p.key === key)?.label || key }
function pageIcon(key) { return pageList.find(p => p.key === key)?.icon || '📄' }

function pageAdCount(pageKey) {
  return items.value.filter(i => i.page === pageKey || (i.target_pages && i.target_pages.includes(pageKey))).length
}

function slotAds(pageKey, position, slotNum) {
  return items.value
    .filter(i => {
      const matchPage = i.page === pageKey || (i.target_pages && i.target_pages.includes(pageKey)) || i.page === 'all'
      return matchPage && i.position === position && (i.slot_number || 1) === slotNum
    })
    .sort((a, b) => (b.bid_amount || 0) - (a.bid_amount || 0))
}

async function load() {
  try {
    const { data } = await axios.get('/api/admin/banners')
    items.value = (data.data || []).map(i => ({
      ...i,
      target_pages: typeof i.target_pages === 'string' ? JSON.parse(i.target_pages) : (i.target_pages || [])
    }))
  } catch {}
  loading.value = false
}

async function approve(item) { try { await axios.post(`/api/admin/banners/${item.id}/approve`); item.status = 'active' } catch (e) { alert(e.response?.data?.message || '실패') } }
async function reject(item) { const r = prompt('거절 사유:'); if (!r) return; try { await axios.post(`/api/admin/banners/${item.id}/reject`, { reason: r }); item.status = 'rejected' } catch {} }
async function pause(item) { try { await axios.post(`/api/admin/banners/${item.id}/pause`); item.status = 'paused' } catch {} }
async function remove(item) { if (!confirm('삭제하시겠습니까?')) return; try { await axios.delete(`/api/admin/banners/${item.id}`); items.value = items.value.filter(i => i.id !== item.id) } catch {} }

onMounted(load)
</script>
