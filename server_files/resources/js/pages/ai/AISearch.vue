<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">
    <!-- 헤더 -->
    <div class="bg-gradient-to-r from-violet-600 to-blue-600 text-white rounded-2xl px-6 py-6 mb-6 text-center">
      <div class="text-4xl mb-3">🤖</div>
      <h1 class="text-2xl font-black mb-2">AI 통합검색</h1>
      <p class="text-white/75 text-sm">자연어로 검색하세요 — AI가 게시글·업소·구인 전체에서 찾아드립니다</p>

      <div class="mt-6 flex gap-3 max-w-2xl mx-auto">
        <input
          v-model="query"
          @keyup.enter="search"
          type="text"
          placeholder="예: LA 한식당 추천해줘, 주말 행사 있어?, 그래픽 디자이너 구인..."
          class="flex-1 bg-white/15 border border-white/30 text-white placeholder-white/50 rounded-xl px-5 py-3 text-sm focus:outline-none focus:bg-white/25"
        />
        <button @click="search" :disabled="loading || !query.trim()"
          class="bg-white text-violet-700 font-black px-6 py-3 rounded-xl text-sm disabled:opacity-50 hover:bg-violet-50 transition flex items-center gap-2">
          <span v-if="loading" class="animate-spin">⏳</span>
          <span v-else>🔍</span>
          검색
        </button>
      </div>

      <!-- 예시 질문 -->
      <div class="mt-4 flex flex-wrap justify-center gap-2">
        <button v-for="ex in examples" :key="ex" @click="query=ex; search()"
          class="bg-white/15 hover:bg-white/25 text-white text-xs px-3 py-1.5 rounded-full transition">
          {{ ex }}
        </button>
      </div>
    </div>

    <!-- AI 분석 노트 -->
    <div v-if="aiNote" class="bg-violet-50 border border-violet-200 text-violet-700 rounded-xl px-4 py-3 mb-4 text-sm flex items-center gap-2">
      <span>✨</span>
      <span>{{ aiNote }} — 키워드: <strong>{{ keywords.join(', ') }}</strong></span>
    </div>

    <!-- 번역 툴 -->
    <div class="bg-white rounded-2xl shadow-sm p-5 mb-6">
      <h2 class="font-black text-gray-700 mb-4 flex items-center gap-2">🌍 AI 번역기</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <textarea v-model="translateInput" rows="4" placeholder="번역할 텍스트를 입력하세요..."
            class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:border-violet-400"></textarea>
          <div class="flex gap-2 mt-2">
            <button v-for="lang in [{k:'ko',l:'한국어'},{k:'en',l:'영어'},{k:'es',l:'스페인어'}]" :key="lang.k"
              @click="targetLang=lang.k; doTranslate()"
              :class="targetLang===lang.k ? 'bg-violet-600 text-white' : 'bg-gray-100 text-gray-600'"
              class="px-3 py-1.5 rounded-lg text-xs font-semibold transition">
              → {{ lang.l }}
            </button>
          </div>
        </div>
        <div class="bg-gray-50 rounded-xl px-4 py-3 text-sm text-gray-700 min-h-[100px] relative">
          <div v-if="translating" class="absolute inset-0 flex items-center justify-center">
            <div class="animate-spin w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full"></div>
          </div>
          <p v-else-if="translated" class="whitespace-pre-wrap leading-relaxed">{{ translated }}</p>
          <p v-else class="text-gray-300 italic">번역 결과가 여기에 표시됩니다</p>
          <button v-if="translated" @click="copyTranslated"
            class="absolute top-2 right-2 text-xs text-gray-400 hover:text-violet-500">📋 복사</button>
        </div>
      </div>
    </div>

    <!-- 검색 결과 -->
    <div v-if="searched">
      <!-- 게시글 결과 -->
      <section v-if="results.posts?.length" class="mb-6">
        <h2 class="font-black text-gray-700 mb-3 flex items-center gap-2">
          📋 게시글
          <span class="text-xs font-normal text-gray-400">{{ results.posts.length }}건</span>
        </h2>
        <div class="space-y-2">
          <RouterLink v-for="p in results.posts" :key="p.id" :to="`/community/${p.board_slug || 'free'}/${p.id}`"
            class="bg-white rounded-xl px-4 py-3 flex justify-between items-start hover:shadow-md transition cursor-pointer block">
            <div>
              <p class="font-semibold text-gray-800 text-sm mb-1">{{ p.title }}</p>
              <p class="text-xs text-gray-400 line-clamp-1">{{ p.content }}</p>
            </div>
            <span class="text-xs text-gray-300 whitespace-nowrap ml-4">{{ formatDate(p.created_at) }}</span>
          </RouterLink>
        </div>
      </section>

      <!-- 업소 결과 -->
      <section v-if="results.businesses?.length" class="mb-6">
        <h2 class="font-black text-gray-700 mb-3 flex items-center gap-2">
          🏢 업소
          <span class="text-xs font-normal text-gray-400">{{ results.businesses.length }}건</span>
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          <RouterLink v-for="b in results.businesses" :key="b.id" :to="`/directory/${b.id}`"
            class="bg-white rounded-xl p-4 hover:shadow-md transition cursor-pointer block">
            <p class="font-bold text-gray-800 text-sm">{{ b.name }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ b.category }} · {{ b.city }}</p>
          </RouterLink>
        </div>
      </section>

      <!-- 구인구직 결과 -->
      <section v-if="results.jobs?.length" class="mb-6">
        <h2 class="font-black text-gray-700 mb-3 flex items-center gap-2">
          💼 구인구직
          <span class="text-xs font-normal text-gray-400">{{ results.jobs.length }}건</span>
        </h2>
        <div class="space-y-2">
          <RouterLink v-for="j in results.jobs" :key="j.id" :to="`/jobs/${j.id}`"
            class="bg-white rounded-xl px-4 py-3 flex justify-between items-center hover:shadow-md transition cursor-pointer block">
            <div>
              <p class="font-semibold text-gray-800 text-sm">{{ j.title }}</p>
              <p class="text-xs text-gray-400">{{ j.location }}</p>
            </div>
            <span v-if="j.salary" class="text-sm font-bold text-violet-600 ml-4">{{ j.salary }}</span>
          </RouterLink>
        </div>
      </section>

      <!-- 중고장터 결과 -->
      <section v-if="results.market?.length" class="mb-6">
        <h2 class="font-black text-gray-700 mb-3 flex items-center gap-2">
          🛍️ 중고장터
          <span class="text-xs font-normal text-gray-400">{{ results.market.length }}건</span>
        </h2>
        <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <RouterLink v-for="m in results.market" :key="m.id" :to="`/market/${m.id}`"
            class="bg-white rounded-xl p-4 hover:shadow-md transition cursor-pointer block">
            <p class="font-bold text-gray-800 text-sm">{{ m.title }}</p>
            <p v-if="m.price" class="text-violet-600 font-black text-sm mt-1">${{ m.price }}</p>
          </RouterLink>
        </div>
      </section>

      <!-- 결과 없음 -->
      <div v-if="!results.posts?.length && !results.businesses?.length && !results.jobs?.length && !results.market?.length"
        class="text-center py-16 text-gray-400">
        <p class="text-4xl mb-3">🔍</p>
        <p class="font-semibold">검색 결과가 없습니다</p>
        <p class="text-sm mt-1">다른 키워드로 검색해보세요</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const query          = ref('')
const loading        = ref(false)
const searched       = ref(false)
const results        = ref({})
const aiNote         = ref('')
const keywords       = ref([])
const translateInput = ref('')
const targetLang     = ref('en')
const translated     = ref('')
const translating    = ref(false)

const examples = [
  'LA 한식당 추천',
  '웹개발자 구인',
  '그래픽카드 중고',
  '이민 비자 정보',
  '주말 한인 행사',
]

function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt), t = new Date()
  const diff = (t - d) / 1000
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`
  return `${Math.floor(diff / 86400)}일 전`
}

async function search() {
  if (!query.value.trim() || loading.value) return
  loading.value = true; searched.value = false
  try {
    const { data } = await axios.get('/api/ai/search', { params: { q: query.value } })
    results.value  = data.results ?? {}
    aiNote.value   = data.ai_note ?? ''
    keywords.value = data.keywords ?? []
    searched.value = true
  } catch {}
  finally { loading.value = false }
}

let translateTimer = null
async function doTranslate() {
  if (!translateInput.value.trim()) return
  clearTimeout(translateTimer)
  translateTimer = setTimeout(async () => {
    translating.value = true
    try {
      const { data } = await axios.post('/api/ai/translate', {
        text: translateInput.value,
        target: targetLang.value,
      })
      translated.value = data.translated
    } catch { translated.value = '번역 실패. API 키를 확인해주세요.' }
    finally { translating.value = false }
  }, 500)
}

function copyTranslated() {
  navigator.clipboard.writeText(translated.value).then(() => alert('복사됐습니다!'))
}
</script>
