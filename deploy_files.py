import paramiko, base64, sys

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunk_size = 50000
    chunks = [enc[i:i+chunk_size] for i in range(0, len(enc), chunk_size)]
    for i, chunk in enumerate(chunks):
        ssh(f"printf '%s' '{chunk}' > /tmp/wf_chunk{i}.b64")
    cat_cmd = "cat " + " ".join([f"/tmp/wf_chunk{i}.b64" for i in range(len(chunks))]) + f" | base64 -d > {path}"
    ssh(cat_cmd)
    ssh("rm -f /tmp/wf_chunk*.b64")
    return f"Written: {path}"

# ============================================================
# TASK 1: QaList.vue
# ============================================================
QA_LIST_VUE = """<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">

    <!-- 헤더: 지식인 스타일 -->
    <div class="bg-gradient-to-r from-blue-600 to-blue-500 rounded-2xl p-6 mb-6 shadow-lg">
      <h1 class="text-white text-2xl font-bold mb-1">❓ 지식인</h1>
      <p class="text-blue-100 text-sm mb-4">궁금한 건 뭐든 물어보세요! 미국 한인 생활 Q&A</p>
      <div class="flex gap-2">
        <div class="relative flex-1">
          <input v-model="search" type="text" placeholder="질문을 검색해보세요"
            class="w-full pl-10 pr-4 py-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
            @keyup.enter="doSearch" />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <button @click="doSearch" class="bg-white text-blue-600 px-5 py-3 rounded-xl text-sm font-semibold hover:bg-blue-50 transition">검색</button>
        <button @click="$router.push('/qa/write')" class="bg-yellow-400 text-gray-900 px-5 py-3 rounded-xl text-sm font-semibold hover:bg-yellow-300 transition flex items-center gap-1">
          ✏ 질문하기
        </button>
      </div>
    </div>

    <!-- 많이 본 Q&A (인기글) -->
    <section v-if="popularPosts.length" class="mb-6">
      <h2 class="text-base font-bold text-gray-800 mb-3">🔥 많이 본 Q&A</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
        <div v-for="(item, idx) in popularPosts.slice(0,6)" :key="item.id"
          class="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md transition cursor-pointer flex gap-3"
          @click="$router.push('/qa/' + item.id)">
          <span class="text-2xl font-extrabold text-blue-500 leading-none min-w-[28px]">{{ idx + 1 }}</span>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-bold text-gray-800 truncate">{{ item.title }}</p>
            <div class="flex items-center gap-3 mt-1 text-xs text-gray-400">
              <span>👁 {{ item.view_count || 0 }}</span>
              <span>💬 {{ item.answer_count || 0 }}</span>
              <span v-if="item.category" class="text-blue-500">{{ item.category.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 3단 레이아웃 -->
    <div class="flex gap-5">

      <!-- 왼쪽: 카테고리 사이드바 (데스크톱) -->
      <aside class="hidden lg:block w-44 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 overflow-hidden sticky top-20">
          <h3 class="text-xs font-bold text-gray-500 px-4 py-3 border-b border-gray-100 uppercase tracking-wide">카테고리</h3>
          <ul>
            <li>
              <button @click="selectCat(''); page=1; loadPosts()"
                class="w-full text-left px-4 py-2.5 text-sm transition"
                :class="activeCategory==='' ? 'bg-blue-50 text-blue-600 font-bold border-l-2 border-blue-500' : 'text-gray-600 hover:bg-gray-50'">
                📋 전체
              </button>
            </li>
            <li v-for="cat in categories" :key="cat.id">
              <button @click="selectCat(cat.key)"
                class="w-full text-left px-4 py-2.5 text-sm transition"
                :class="activeCategory===cat.key ? 'bg-blue-50 text-blue-600 font-bold border-l-2 border-blue-500' : 'text-gray-600 hover:bg-gray-50'">
                {{ cat.icon || '•' }} {{ cat.name }}
              </button>
            </li>
          </ul>
        </div>
      </aside>

      <!-- 모바일 카테고리 탭 -->
      <div class="lg:hidden w-full">
        <div class="flex overflow-x-auto gap-2 pb-2 mb-3" style="scrollbar-width:none">
          <button @click="selectCat(''); page=1; loadPosts()"
            class="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-medium transition flex-shrink-0"
            :class="activeCategory==='' ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
            전체
          </button>
          <button v-for="cat in categories" :key="'m'+cat.id" @click="selectCat(cat.key)"
            class="whitespace-nowrap px-3 py-1.5 rounded-full text-xs font-medium transition flex-shrink-0"
            :class="activeCategory===cat.key ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'">
            {{ cat.icon || '' }} {{ cat.name }}
          </button>
        </div>
      </div>

      <!-- 중앙: 질문 목록 -->
      <main class="flex-1 min-w-0">
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-gray-500">총 <strong class="text-gray-800">{{ totalCount.toLocaleString() }}</strong>개</span>
          <div class="flex items-center gap-2">
            <select v-model="sortOrder" @change="loadPosts()" class="text-xs border border-gray-200 rounded-lg px-2 py-1.5 text-gray-600 focus:outline-none">
              <option value="latest">최신순</option>
              <option value="views">조회순</option>
              <option value="answers">답변순</option>
            </select>
          </div>
        </div>

        <!-- 로딩 -->
        <div v-if="loading" class="space-y-3">
          <div v-for="i in 5" :key="i" class="bg-white rounded-xl border border-gray-100 p-4 animate-pulse">
            <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div class="h-3 bg-gray-100 rounded w-full mb-3"></div>
            <div class="h-3 bg-gray-100 rounded w-1/3"></div>
          </div>
        </div>

        <!-- 질문 카드 -->
        <div v-else class="space-y-2">
          <div v-for="post in posts" :key="post.id"
            class="bg-white rounded-xl border border-gray-100 p-4 hover:shadow-md transition cursor-pointer"
            @click="$router.push('/qa/' + post.id)">
            <div class="flex items-start gap-3">
              <!-- 답변 카운트 박스 -->
              <div class="flex-shrink-0 text-center min-w-[48px]">
                <div :class="post.answer_count > 0 ? 'bg-green-50 text-green-700 border-green-200' : 'bg-gray-50 text-gray-400 border-gray-200'"
                  class="border rounded-lg px-2 py-1">
                  <div class="text-lg font-bold leading-none">{{ post.answer_count || 0 }}</div>
                  <div class="text-[10px] mt-0.5">답변</div>
                </div>
              </div>
              <!-- 내용 -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1 flex-wrap">
                  <span v-if="post.category" class="text-[11px] px-2 py-0.5 rounded-full bg-blue-50 text-blue-600 font-medium">
                    {{ post.category.icon || '' }} {{ post.category.name }}
                  </span>
                  <span v-if="post.status==='solved'" class="text-[11px] px-2 py-0.5 rounded-full bg-green-100 text-green-700 font-medium">✓ 해결</span>
                  <span v-if="post.is_pinned" class="text-[11px] text-orange-500">📌</span>
                </div>
                <h3 class="text-sm font-semibold text-gray-800 line-clamp-1 mb-1">{{ post.title }}</h3>
                <div class="flex items-center gap-3 text-xs text-gray-400">
                  <div class="flex items-center gap-1">
                    <div class="w-4 h-4 rounded-full bg-blue-100 flex items-center justify-center text-[9px] font-bold text-blue-600">
                      {{ (displayName(post.user)).charAt(0) }}
                    </div>
                    <span>{{ displayName(post.user) }}</span>
                  </div>
                  <span>{{ timeAgo(post.created_at) }}</span>
                  <span>👁 {{ post.view_count || 0 }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="!loading && posts.length===0" class="text-center py-16">
            <div class="text-5xl mb-3">🤔</div>
            <p class="text-gray-400 text-sm">등록된 질문이 없습니다.</p>
            <button @click="$router.push('/qa/write')" class="text-blue-500 text-sm mt-2 hover:underline">첫 번째 질문 작성하기 →</button>
          </div>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="totalPages > 1" class="flex justify-center gap-1 mt-5 flex-wrap">
          <button @click="goPage(page-1)" :disabled="page<=1" class="w-8 h-8 rounded-lg text-xs font-medium bg-white text-gray-500 border border-gray-200 hover:bg-gray-50 disabled:opacity-30">‹</button>
          <button v-for="p in pageRange" :key="p" @click="goPage(p)"
            class="w-8 h-8 rounded-lg text-xs font-medium transition"
            :class="page===p ? 'bg-blue-500 text-white' : 'bg-white text-gray-500 border border-gray-200 hover:bg-gray-50'">
            {{ p }}
          </button>
          <button @click="goPage(page+1)" :disabled="page>=totalPages" class="w-8 h-8 rounded-lg text-xs font-medium bg-white text-gray-500 border border-gray-200 hover:bg-gray-50 disabled:opacity-30">›</button>
        </div>
      </main>

      <!-- 오른쪽: 랭킹 사이드바 (데스크톱) -->
      <aside class="hidden xl:block w-52 flex-shrink-0">
        <div class="bg-white rounded-xl border border-gray-100 sticky top-20 mb-4">
          <h3 class="text-xs font-bold text-gray-500 px-4 py-3 border-b border-gray-100 uppercase tracking-wide">🏆 지식인 랭킹</h3>
          <ul class="py-1">
            <li v-for="(u, idx) in topUsers" :key="u.name"
              class="flex items-center gap-2.5 px-4 py-2.5 hover:bg-gray-50 transition">
              <span class="text-sm font-bold w-5 text-center leading-none">
                <template v-if="idx===0">🥇</template>
                <template v-else-if="idx===1">🥈</template>
                <template v-else-if="idx===2">🥉</template>
                <template v-else>{{ idx+1 }}</template>
              </span>
              <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
                :style="{background: u.color}">{{ u.name.charAt(0) }}</div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-semibold text-gray-800 truncate">{{ u.name }}</p>
                <p class="text-[10px] text-gray-400">채택 {{ u.adopted }}회</p>
              </div>
            </li>
          </ul>
        </div>

        <!-- 빠른 카테고리 링크 -->
        <div class="bg-white rounded-xl border border-gray-100">
          <h3 class="text-xs font-bold text-gray-500 px-4 py-3 border-b border-gray-100">📂 인기 카테고리</h3>
          <div class="p-3 flex flex-wrap gap-1.5">
            <button v-for="cat in categories.slice(0,8)" :key="'s'+cat.id"
              @click="selectCat(cat.key)"
              class="text-[11px] px-2.5 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-blue-50 hover:text-blue-600 transition font-medium">
              {{ cat.name }}
            </button>
          </div>
        </div>
      </aside>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const categories = ref([])
const posts = ref([])
const popularPosts = ref([])
const loading = ref(false)
const activeCategory = ref('')
const search = ref('')
const sortOrder = ref('latest')
const page = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

const topUsers = ref([
  { name: '미국한인생활', color: '#3B82F6', adopted: 142 },
  { name: '비빔밥마스터', color: '#8B5CF6', adopted: 98 },
  { name: '핫도그킹', color: '#EC4899', adopted: 76 },
  { name: '조지아주한인', color: '#F59E0B', adopted: 51 },
  { name: '텍사스한국인', color: '#10B981', adopted: 43 },
  { name: '뉴욕한인', color: '#EF4444', adopted: 38 },
  { name: '캘리포니아꿈', color: '#6366F1', adopted: 31 },
])

function displayName(user) {
  if (!user) return '익명'
  return user.nickname || user.username || '익명'
}

function selectCat(key) {
  activeCategory.value = key
  page.value = 1
  loadPosts()
}

function doSearch() {
  page.value = 1
  loadPosts()
}

function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt)) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return Math.floor(diff/60) + '분 전'
  if (diff < 86400) return Math.floor(diff/3600) + '시간 전'
  if (diff < 604800) return Math.floor(diff/86400) + '일 전'
  const d = new Date(dt)
  return `${d.getMonth()+1}/${d.getDate()}`
}

const pageRange = computed(() => {
  const start = Math.max(1, page.value - 4)
  const end = Math.min(totalPages.value, page.value + 4)
  return Array.from({length: end-start+1}, (_,i) => start+i)
})

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  loadPosts()
  window.scrollTo({top: 0, behavior: 'smooth'})
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/qa/categories')
    categories.value = data
  } catch {}
}

async function loadPopular() {
  try {
    const { data } = await axios.get('/api/qa', { params: { sort: 'views', per_page: 6 } })
    popularPosts.value = (data.data || data).slice(0, 6)
  } catch {}
}

async function loadPosts() {
  loading.value = true
  try {
    const params = { page: page.value, sort: sortOrder.value }
    if (activeCategory.value) params.category = activeCategory.value
    if (search.value.trim()) params.search = search.value.trim()
    const { data } = await axios.get('/api/qa', { params })
    posts.value = data.data || data
    totalPages.value = data.last_page || 1
    totalCount.value = data.total || posts.value.length
    page.value = data.current_page || page.value
  } catch { posts.value = [] }
  finally { loading.value = false }
}

onMounted(async () => {
  await loadCategories()
  await Promise.all([loadPopular(), loadPosts()])
})
</script>

<style scoped>
.line-clamp-1 { display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden; }
</style>
"""

# ============================================================
# TASK 2: QaDetail.vue - updated with displayName
# ============================================================
QA_DETAIL_VUE = """<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[800px] mx-auto px-4 pt-4">

      <!-- 로딩 -->
      <div v-if="loading" class="text-center py-16 text-gray-400">불러오는 중...</div>

      <template v-else-if="post">
        <!-- 뒤로가기 -->
        <button @click="$router.back()" class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition">
          ← 목록으로
        </button>

        <!-- 질문 카드 -->
        <div class="bg-white rounded-2xl shadow-sm p-5 mb-4">
          <div class="flex items-center gap-2 mb-3">
            <span v-if="post.category" class="text-xs px-2.5 py-1 rounded-full bg-violet-50 text-violet-700 font-semibold">
              {{ post.category.icon }} {{ post.category.name }}
            </span>
            <span :class="statusBadgeClass(post.status)" class="text-xs px-2.5 py-1 rounded-full font-semibold">
              {{ statusLabel(post.status) }}
            </span>
          </div>
          <h1 class="text-lg font-bold text-gray-900 mb-3 leading-snug">{{ post.title }}</h1>
          <p class="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap mb-4">{{ post.content }}</p>
          <div class="flex items-center gap-3 text-xs text-gray-400 pt-3 border-t border-gray-100">
            <div class="w-7 h-7 rounded-full bg-violet-100 flex items-center justify-center text-violet-600 font-bold text-sm">
              {{ displayName(post.user).charAt(0) }}
            </div>
            <span class="font-medium text-gray-600">{{ displayName(post.user) }}</span>
            <span v-if="post.region" class="text-blue-500">📍 {{ post.region }}</span>
            <span>{{ timeAgo(post.created_at) }}</span>
            <span>조회 {{ post.view_count }}</span>
          </div>
        </div>

        <!-- 베스트 답변 -->
        <div v-if="post.best_answer" class="bg-yellow-50 border border-yellow-200 rounded-2xl p-5 mb-4">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-yellow-500 text-lg">⭐</span>
            <span class="text-sm font-bold text-yellow-700">베스트 답변</span>
          </div>
          <p class="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap mb-3">{{ post.best_answer.content }}</p>
          <div class="flex items-center gap-2 text-xs text-gray-500">
            <div class="w-6 h-6 rounded-full bg-yellow-200 flex items-center justify-center text-yellow-700 font-bold text-xs">
              {{ displayName(post.best_answer.user).charAt(0) }}
            </div>
            <span>{{ displayName(post.best_answer.user) }}</span>
            <span>{{ timeAgo(post.best_answer.created_at) }}</span>
          </div>
        </div>

        <!-- 답변 목록 -->
        <div class="mb-4">
          <h2 class="text-sm font-bold text-gray-600 mb-3">답변 {{ post.answers?.length || 0 }}개</h2>
          <div v-for="ans in nonBestAnswers" :key="ans.id"
            class="bg-white rounded-2xl shadow-sm p-4 mb-3">
            <p class="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap mb-3">{{ ans.content }}</p>
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2 text-xs text-gray-400">
                <div class="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">
                  {{ displayName(ans.user).charAt(0) }}
                </div>
                <span>{{ displayName(ans.user) }}</span>
                <span>{{ timeAgo(ans.created_at) }}</span>
              </div>
              <div class="flex items-center gap-2">
                <button @click="likeAnswer(ans)" class="flex items-center gap-1 text-xs text-gray-400 hover:text-blue-500 transition">
                  👍 {{ ans.like_count || 0 }}
                </button>
                <button v-if="isPostOwner && !post.best_answer_id" @click="setBest(ans.id)"
                  class="text-xs px-2 py-1 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition">
                  베스트 선택
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 답변 작성 -->
        <div class="bg-white rounded-2xl shadow-sm p-5">
          <h3 class="text-sm font-bold text-gray-700 mb-3">답변 작성</h3>
          <textarea v-model="newAnswer" rows="4" placeholder="실용적인 답변을 작성해주세요..."
            class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-violet-400 resize-none mb-3" />
          <div class="flex justify-end">
            <button @click="submitAnswer" :disabled="!newAnswer.trim() || submitting"
              class="bg-violet-500 hover:bg-violet-600 disabled:opacity-50 text-white px-5 py-2 rounded-xl text-sm font-semibold transition">
              {{ submitting ? '등록 중...' : '답변 등록' }}
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const post = ref(null)
const loading = ref(true)
const newAnswer = ref('')
const submitting = ref(false)

const isPostOwner = computed(() => auth.user && post.value && auth.user.id === post.value.user_id)
const nonBestAnswers = computed(() => (post.value?.answers || []).filter(a => !a.is_best))

function displayName(user) {
  if (!user) return '익명'
  return user.nickname || user.username || '익명'
}

function statusLabel(s) { return { open: '미답변', solved: '해결됨', closed: '마감' }[s] || s }
function statusBadgeClass(s) {
  if (s === 'solved') return 'bg-green-100 text-green-700'
  return 'bg-blue-100 text-blue-700'
}
function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt)) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return Math.floor(diff/60) + '분 전'
  if (diff < 86400) return Math.floor(diff/3600) + '시간 전'
  return Math.floor(diff/86400) + '일 전'
}

async function load() {
  try {
    const { data } = await axios.get('/api/qa/' + route.params.id)
    post.value = data
  } catch { post.value = null }
  finally { loading.value = false }
}

async function submitAnswer() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  if (!newAnswer.value.trim()) return
  submitting.value = true
  try {
    const { data } = await axios.post('/api/qa/' + post.value.id + '/answers', { content: newAnswer.value })
    if (!post.value.answers) post.value.answers = []
    post.value.answers.push(data.answer)
    post.value.answer_count++
    newAnswer.value = ''
  } catch (e) {
    alert(e.response?.data?.message || '등록 실패')
  } finally { submitting.value = false }
}

async function likeAnswer(ans) {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post('/api/qa/answers/' + ans.id + '/like')
    ans.like_count = data.like_count
  } catch {}
}

async function setBest(answerId) {
  try {
    await axios.post('/api/qa/' + post.value.id + '/best-answer', { answer_id: answerId })
    await load()
  } catch {}
}

onMounted(load)
</script>
"""

# ============================================================
# TASK 3: RecipeDetail.vue - with related recipes sidebar
# ============================================================
RECIPE_DETAIL_VUE = """<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <div v-if="loading" class="text-center py-16 text-gray-400">불러오는 중...</div>

      <template v-else-if="recipe">
        <button @click="$router.back()" class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition">
          ← 목록으로
        </button>

        <!-- 뉴스 스타일 2단 레이아웃 -->
        <div class="flex gap-6 items-start">

          <!-- 메인 컨텐츠 -->
          <div class="flex-1 min-w-0">
            <div class="bg-white rounded-2xl shadow-sm overflow-hidden mb-4">
              <!-- 대표 이미지 -->
              <div v-if="recipe.image_url" class="relative">
                <img :src="recipe.image_url" :alt="recipe.title" class="w-full object-cover" style="max-height:420px" />
                <div v-if="recipe.image_credit" class="absolute bottom-2 right-3 text-xs text-white bg-black/40 px-2 py-0.5 rounded">
                  {{ recipe.image_credit }}
                </div>
              </div>
              <div v-else class="bg-gradient-to-br from-orange-100 to-amber-50 flex items-center justify-center" style="height:200px">
                <span class="text-7xl">🍽️</span>
              </div>

              <div class="p-5">
                <!-- 카테고리 + 제목 -->
                <div class="flex items-center gap-2 mb-2">
                  <span v-if="recipe.category" class="text-xs px-2.5 py-1 bg-orange-50 text-orange-700 rounded-full font-medium">
                    {{ recipe.category.icon }} {{ recipe.category.name }}
                  </span>
                  <span :class="difficultyClass(recipe.difficulty)" class="text-xs px-2.5 py-1 rounded-full font-medium">{{ recipe.difficulty }}</span>
                </div>
                <h1 class="text-xl font-black text-gray-900 mb-1">{{ recipe.title }}</h1>

                <!-- 평점 -->
                <div v-if="recipe.avg_rating" class="flex items-center gap-1 mb-2">
                  <span v-for="n in 5" :key="n" class="text-lg" :class="n <= Math.round(recipe.avg_rating) ? 'text-yellow-400' : 'text-gray-200'">★</span>
                  <span class="text-sm font-bold text-gray-700 ml-1">{{ recipe.avg_rating }}</span>
                  <span class="text-xs text-gray-400">({{ recipe.comment_count || 0 }}개 후기)</span>
                </div>

                <p v-if="recipe.intro" class="text-gray-600 text-sm leading-relaxed mb-4">{{ recipe.intro }}</p>

                <!-- 작성자 -->
                <div class="flex items-center gap-2 mb-4 text-xs text-gray-400">
                  <div class="w-6 h-6 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 font-bold text-xs">
                    {{ displayName(recipe.user).charAt(0) }}
                  </div>
                  <span class="font-medium text-gray-600">{{ displayName(recipe.user) }}</span>
                  <span>·</span>
                  <span>조회 {{ recipe.view_count || 0 }}</span>
                  <span>❤️ {{ recipe.like_count || 0 }}</span>
                </div>

                <!-- 정보 태그 -->
                <div class="flex flex-wrap gap-3 mb-4 text-sm">
                  <div class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                    <span>⏱</span><span class="font-medium">{{ recipe.cook_time }}</span>
                  </div>
                  <div v-if="recipe.calories" class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                    <span>🔥</span><span class="font-medium">{{ recipe.calories }}kcal</span>
                  </div>
                  <div class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                    <span>👥</span><span class="font-medium">{{ recipe.servings }}인분</span>
                  </div>
                </div>

                <!-- 좋아요/북마크 -->
                <div class="flex gap-3 mb-4">
                  <button @click="toggleLike" :class="recipe.is_liked ? 'bg-red-50 text-red-500 border-red-200' : 'bg-gray-50 text-gray-500 border-gray-200'"
                    class="flex items-center gap-2 border px-4 py-2 rounded-xl text-sm font-medium transition hover:scale-105">
                    ❤️ {{ recipe.like_count || 0 }}
                  </button>
                  <button @click="toggleBookmark" :class="recipe.is_bookmarked ? 'bg-amber-50 text-amber-600 border-amber-200' : 'bg-gray-50 text-gray-500 border-gray-200'"
                    class="flex items-center gap-2 border px-4 py-2 rounded-xl text-sm font-medium transition hover:scale-105">
                    🔖 저장
                  </button>
                </div>

                <!-- 태그 -->
                <div v-if="recipe.tags?.length" class="flex flex-wrap gap-1.5">
                  <span v-for="tag in recipe.tags" :key="tag" class="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full">#{{ tag }}</span>
                </div>
              </div>
            </div>

            <!-- 재료 -->
            <div class="bg-white rounded-2xl shadow-sm p-5 mb-4">
              <h2 class="font-bold text-gray-800 mb-3 flex items-center gap-2">
                <span class="w-7 h-7 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm">🛒</span>
                재료 ({{ recipe.servings }}인분)
              </h2>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div v-for="(ing, i) in recipe.ingredients" :key="i"
                  class="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg text-sm">
                  <span class="text-gray-700">{{ typeof ing === 'object' ? ing.name : ing }}</span>
                  <span v-if="ing.amount" class="text-gray-400 text-xs font-medium">{{ ing.amount }}</span>
                </div>
              </div>
            </div>

            <!-- 조리 순서 -->
            <div class="bg-white rounded-2xl shadow-sm p-5 mb-4">
              <h2 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="w-7 h-7 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm">👨‍🍳</span>
                조리 순서
              </h2>
              <ol class="space-y-4">
                <li v-for="(step, i) in recipe.steps" :key="i" class="flex gap-4">
                  <div class="w-7 h-7 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                    {{ i + 1 }}
                  </div>
                  <p class="text-gray-700 text-sm leading-relaxed pt-1">{{ typeof step === 'object' ? step.description : step }}</p>
                </li>
              </ol>
            </div>

            <!-- 팁 -->
            <div v-if="recipe.tips?.length" class="bg-amber-50 border border-amber-100 rounded-2xl p-5 mb-4">
              <h2 class="font-bold text-amber-800 mb-3">💡 요리 팁</h2>
              <ul class="space-y-2">
                <li v-for="(tip, i) in recipe.tips" :key="i" class="text-sm text-amber-700 flex gap-2">
                  <span class="text-amber-400 flex-shrink-0">•</span>
                  <span>{{ tip }}</span>
                </li>
              </ul>
            </div>

            <!-- 후기/댓글 -->
            <div class="bg-white rounded-2xl shadow-sm p-5">
              <h3 class="font-bold text-gray-700 mb-4 flex items-center gap-2">
                💬 후기 <span class="text-sm font-normal text-gray-400">({{ recipe.comments?.length || 0 }}개)</span>
              </h3>
              <div class="space-y-4 mb-6">
                <div v-for="cm in recipe.comments" :key="cm.id" class="border-b border-gray-50 pb-4 last:border-0 last:pb-0">
                  <div class="flex items-center gap-2 mb-1.5">
                    <div class="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 font-bold text-sm">
                      {{ displayName(cm.user).charAt(0) }}
                    </div>
                    <div>
                      <span class="text-sm font-semibold text-gray-700">{{ displayName(cm.user) }}</span>
                      <div class="flex items-center gap-0.5 mt-0.5">
                        <span v-for="n in 5" :key="n" class="text-sm" :class="cm.rating && n<=cm.rating ? 'text-yellow-400' : 'text-gray-200'">★</span>
                      </div>
                    </div>
                    <span class="ml-auto text-xs text-gray-400">{{ timeAgo(cm.created_at) }}</span>
                  </div>
                  <p class="text-sm text-gray-600 ml-10">{{ cm.content }}</p>
                </div>
                <div v-if="!recipe.comments?.length" class="text-center py-6 text-gray-400 text-sm">
                  아직 후기가 없어요. 첫 번째 후기를 남겨보세요!
                </div>
              </div>
              <!-- 댓글 작성 -->
              <div class="border-t border-gray-100 pt-4">
                <div class="flex gap-1 mb-3">
                  <span class="text-sm text-gray-500 mr-1">별점:</span>
                  <span v-for="n in 5" :key="n" @click="commentRating = n" class="cursor-pointer text-2xl transition-transform hover:scale-110"
                    :class="n <= commentRating ? 'text-yellow-400' : 'text-gray-200'">★</span>
                </div>
                <textarea v-model="commentText" rows="3" placeholder="이 레시피 어떠셨나요? 솔직한 후기를 남겨주세요."
                  class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-orange-400 resize-none mb-2" />
                <div class="flex justify-end">
                  <button @click="submitComment" :disabled="!commentText.trim()"
                    class="bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white px-5 py-2 rounded-xl text-sm font-semibold transition">
                    후기 등록
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 오른쪽 사이드바: 같은 카테고리 레시피 -->
          <aside class="hidden lg:block w-72 flex-shrink-0">
            <div class="bg-white rounded-2xl shadow-sm overflow-hidden sticky top-20">
              <div class="px-4 py-3 border-b border-gray-100">
                <h3 class="text-sm font-bold text-gray-700">
                  {{ recipe.category ? recipe.category.name + ' 레시피' : '관련 레시피' }}
                </h3>
              </div>
              <div class="divide-y divide-gray-50">
                <div v-for="rel in (recipe.related || [])" :key="rel.id"
                  class="flex gap-3 p-3 hover:bg-gray-50 cursor-pointer transition"
                  @click="goRecipe(rel.id)">
                  <!-- 썸네일 -->
                  <div class="w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 bg-orange-50">
                    <img v-if="rel.image_url" :src="rel.image_url" :alt="rel.title" class="w-full h-full object-cover"/>
                    <div v-else class="w-full h-full flex items-center justify-center text-2xl">🍽️</div>
                  </div>
                  <!-- 정보 -->
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-gray-800 line-clamp-2 mb-1">{{ rel.title }}</p>
                    <div class="flex items-center gap-2 text-xs text-gray-400">
                      <span>⏱ {{ rel.cook_time }}</span>
                      <span>❤️ {{ rel.like_count || 0 }}</span>
                    </div>
                  </div>
                </div>
                <div v-if="!recipe.related?.length" class="p-4 text-center text-sm text-gray-400">
                  관련 레시피가 없습니다
                </div>
              </div>
              <div class="p-3 border-t border-gray-100">
                <button @click="$router.push('/recipes?category=' + (recipe.category?.key || ''))"
                  class="w-full text-xs text-orange-600 hover:text-orange-700 font-semibold text-center">
                  {{ recipe.category?.name || '전체' }} 레시피 더보기 →
                </button>
              </div>
            </div>
          </aside>

        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const recipe = ref(null)
const loading = ref(true)
const commentText = ref('')
const commentRating = ref(0)

function displayName(user) {
  if (!user) return '익명'
  return user.nickname || user.username || '익명'
}

function difficultyClass(d) {
  if (d === '쉬움') return 'bg-green-100 text-green-700'
  if (d === '어려움') return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

function timeAgo(dt) {
  if (!dt) return ''
  const diff = (Date.now() - new Date(dt)) / 1000
  if (diff < 60) return '방금 전'
  if (diff < 3600) return Math.floor(diff/60) + '분 전'
  if (diff < 86400) return Math.floor(diff/3600) + '시간 전'
  return Math.floor(diff/86400) + '일 전'
}

function goRecipe(id) {
  router.push('/recipes/' + id)
  window.scrollTo({top: 0, behavior: 'smooth'})
}

async function load() {
  loading.value = true
  try {
    const { data } = await axios.get('/api/recipes/' + route.params.id)
    recipe.value = data
  } catch { recipe.value = null }
  finally { loading.value = false }
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post('/api/recipes/' + recipe.value.id + '/like')
    recipe.value.is_liked = data.liked
    recipe.value.like_count = data.like_count
  } catch {}
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post('/api/recipes/' + recipe.value.id + '/bookmark')
    recipe.value.is_bookmarked = data.bookmarked
  } catch {}
}

async function submitComment() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post('/api/recipes/' + recipe.value.id + '/comments', {
      content: commentText.value, rating: commentRating.value || null
    })
    if (!recipe.value.comments) recipe.value.comments = []
    recipe.value.comments.unshift(data.comment)
    commentText.value = ''
    commentRating.value = 0
  } catch {}
}

onMounted(load)
</script>

<style scoped>
.line-clamp-2 { display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }
</style>
"""

# Write all files
print(write_file('/var/www/somekorean/resources/js/pages/qa/QaList.vue', QA_LIST_VUE))
print(write_file('/var/www/somekorean/resources/js/pages/qa/QaDetail.vue', QA_DETAIL_VUE))
print(write_file('/var/www/somekorean/resources/js/pages/recipes/RecipeDetail.vue', RECIPE_DETAIL_VUE))

# ============================================================
# TASK 4: Update router - remove /community/qna route
# ============================================================
router_content = ssh("base64 /var/www/somekorean/resources/js/router/index.js")
import base64 as b64_mod
router_decoded = b64_mod.b64decode(router_content).decode('utf-8', errors='replace')
router_updated = router_decoded.replace(
    "    { path: '/community/qna',       component: () => import('../pages/community/QnAHome.vue'),    name: 'qna' },\n",
    ""
)
if router_updated == router_decoded:
    # Try alternate spacing
    router_updated = router_decoded.replace(
        "{ path: '/community/qna', component: () => import('../pages/community/QnAHome.vue'), name: 'qna' },\n",
        ""
    )
print(write_file('/var/www/somekorean/resources/js/router/index.js', router_updated))
print("Router qna line removed:", "qna" not in router_updated or "QnAHome" not in router_updated)

# ============================================================
# TASK 5: RecipeList.vue - check for user.name references
# ============================================================
recipe_list_content = ssh("base64 /var/www/somekorean/resources/js/pages/recipes/RecipeList.vue")
recipe_list_decoded = b64_mod.b64decode(recipe_list_content).decode('utf-8', errors='replace')
# Check if there are user.name references
if 'user.name' in recipe_list_decoded or 'user?.name' in recipe_list_decoded:
    print("RecipeList.vue has user.name references - updating")
    recipe_list_updated = recipe_list_decoded.replace('user.name', "user.nickname || user.username || '작성자'")
    recipe_list_updated = recipe_list_updated.replace("user?.name", "user?.nickname || user?.username || '작성자'")
    print(write_file('/var/www/somekorean/resources/js/pages/recipes/RecipeList.vue', recipe_list_updated))
else:
    print("RecipeList.vue: No user.name references found - no changes needed")
