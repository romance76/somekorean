<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <div class="flex items-center justify-between mb-4">
      <h1 class="text-xl font-black text-gray-800">❓ Q&A</h1>
      <RouterLink v-if="auth.isLoggedIn" to="/qa/write" class="bg-amber-400 text-amber-900 font-bold px-4 py-2 rounded-lg text-sm hover:bg-amber-500">✏️ 질문하기</RouterLink>
    </div>

    <div class="grid grid-cols-12 gap-4">
      <!-- 왼쪽: 카테고리 -->
      <div class="col-span-12 lg:col-span-2 hidden lg:block">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden sticky top-20">
          <div class="px-3 py-2.5 border-b font-bold text-xs text-amber-900">📋 카테고리</div>
          <button @click="activeCat=null; loadQa()" class="w-full text-left px-3 py-2 text-xs transition"
            :class="!activeCat ? 'bg-amber-50 text-amber-700 font-bold' : 'text-gray-600 hover:bg-amber-50/50'">전체</button>
          <button v-for="cat in categories" :key="cat.id" @click="activeCat=cat; loadQa()"
            class="w-full text-left px-3 py-2 text-xs transition"
            :class="activeCat?.id===cat.id ? 'bg-amber-50 text-amber-700 font-bold' : 'text-gray-600 hover:bg-amber-50/50'">{{ cat.name }}</button>
        </div>

        <!-- 상태 필터 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden mt-3">
          <div class="px-3 py-2.5 border-b font-bold text-xs text-amber-900">🔍 상태</div>
          <button v-for="s in statusFilters" :key="s.value" @click="statusFilter=s.value; loadQa()"
            class="w-full text-left px-3 py-2 text-xs transition"
            :class="statusFilter===s.value ? 'bg-amber-50 text-amber-700 font-bold' : 'text-gray-600 hover:bg-amber-50/50'">{{ s.label }}</button>
        </div>
      </div>

      <!-- 메인 -->
      <div class="col-span-12 lg:col-span-7">
        <!-- 모바일 필터 -->
        <div class="lg:hidden flex gap-2 mb-3">
          <select @change="e => { activeCat = categories.find(c=>c.id==e.target.value)||null; loadQa() }" class="flex-1 border rounded-lg px-2 py-2 text-sm">
            <option :value="null">전체 카테고리</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <select v-model="statusFilter" @change="loadQa()" class="border rounded-lg px-2 py-2 text-sm">
            <option v-for="s in statusFilters" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
        </div>

        <div v-if="activeCat" class="mb-2 text-sm font-bold text-amber-700">{{ activeCat.name }}</div>

        <div v-if="loading" class="text-center py-12 text-gray-400">로딩중...</div>
        <div v-else-if="!items.length" class="text-center py-12">
          <div class="text-4xl mb-3">❓</div>
          <div class="text-gray-500 font-semibold">질문이 없습니다</div>
          <RouterLink v-if="auth.isLoggedIn" to="/qa/write" class="inline-block mt-3 bg-amber-400 text-amber-900 font-bold px-5 py-2 rounded-lg text-sm">첫 질문 올리기</RouterLink>
        </div>
        <div v-else class="space-y-2">
          <RouterLink v-for="item in items" :key="item.id" :to="`/qa/${item.id}`"
            class="block bg-white rounded-xl shadow-sm border border-gray-100 px-4 py-3 hover:shadow-md transition">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full font-semibold">{{ item.category?.name || 'Q&A' }}</span>
              <span v-if="item.bounty_points > 0" class="text-[10px] bg-yellow-400 text-yellow-900 px-1.5 py-0.5 rounded-full font-bold">🏆 {{ item.bounty_points }}P</span>
              <span v-if="item.is_resolved" class="text-[10px] bg-green-100 text-green-700 px-1.5 py-0.5 rounded-full font-bold">✅ 해결</span>
              <span v-else class="text-[10px] bg-red-100 text-red-600 px-1.5 py-0.5 rounded-full">미해결</span>
            </div>
            <div class="text-sm font-medium text-gray-800">{{ item.title }}</div>
            <div class="flex items-center gap-3 mt-1.5 text-xs text-gray-400">
              <span>{{ item.user?.name }}</span>
              <span>💬 답변 {{ item.answer_count }}개</span>
              <span>👁 {{ item.view_count }}</span>
              <span>{{ formatDate(item.created_at) }}</span>
            </div>
          </RouterLink>
        </div>

        <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
          <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="loadQa(pg)"
            class="px-3 py-1 rounded text-sm" :class="pg===page?'bg-amber-400 text-amber-900 font-bold':'bg-white border text-gray-600'">{{ pg }}</button>
        </div>
      </div>

      <!-- 오른쪽: 위젯 -->
      <div class="col-span-12 lg:col-span-3 hidden lg:block">
        <SidebarWidgets api-url="/api/qa" detail-path="/qa/" :current-id="0"
          label="질문" recommend-label="인기 질문" quick-label="최신 질문"
          :links="[{to:'/qa',icon:'📋',label:'전체 Q&A'},{to:'/qa/write',icon:'✏️',label:'질문하기'}]" />
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import SidebarWidgets from '../../components/SidebarWidgets.vue'
import axios from 'axios'

const auth = useAuthStore()
const items = ref([])
const categories = ref([])
const activeCat = ref(null)
const statusFilter = ref('')
const loading = ref(true)
const page = ref(1)
const lastPage = ref(1)

const statusFilters = [
  { value: '', label: '전체' },
  { value: 'false', label: '❌ 미해결' },
  { value: 'true', label: '✅ 해결됨' },
]

function formatDate(dt) {
  if (!dt) return ''
  const h = Math.floor((Date.now() - new Date(dt).getTime()) / 3600000)
  if (h < 1) return '방금'
  if (h < 24) return h + '시간 전'
  return Math.floor(h / 24) + '일 전'
}

async function loadQa(p = 1) {
  loading.value = true; page.value = p
  const params = { page: p, per_page: 20 }
  if (activeCat.value) params.category_id = activeCat.value.id
  if (statusFilter.value) params.resolved = statusFilter.value
  try {
    const { data } = await axios.get('/api/qa', { params })
    items.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
  } catch {}
  loading.value = false
}

onMounted(async () => {
  const [qRes, cRes] = await Promise.allSettled([
    axios.get('/api/qa?per_page=20'),
    axios.get('/api/qa/categories'),
  ])
  if (qRes.status === 'fulfilled') { items.value = qRes.value.data?.data?.data || []; lastPage.value = qRes.value.data?.data?.last_page || 1 }
  if (cRes.status === 'fulfilled') categories.value = cRes.value.data?.data || []
  loading.value = false
})
</script>
