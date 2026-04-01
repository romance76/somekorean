import paramiko, sys, base64
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=120):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    return o + (('\nERR:'+e) if e else '')

def write_file(path, content):
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [encoded[i:i+3000] for i in range(0, len(encoded), 3000)]
    ssh('> /tmp/_wf.b64')
    for chunk in chunks:
        ssh("echo -n '{}' >> /tmp/_wf.b64".format(chunk))
    return ssh('base64 -d /tmp/_wf.b64 > {} && rm /tmp/_wf.b64 && echo OK'.format(path))

# ── 1. Add blindShort to AdminController ─────────────────────────────────────
print("=== 1. Adding blindShort to AdminController ===")
raw = ssh('base64 /var/www/somekorean/app/Http/Controllers/API/AdminController.php')
ctrl = base64.b64decode(raw).decode('utf-8')

old_get_shorts = '''    public function getShorts(Request $req)'''
new_blind = '''    public function blindShort($id) {
        $short = DB::table('shorts')->where('id', $id)->first();
        if (!$short) return response()->json(['error' => 'Not found'], 404);
        $newActive = $short->is_active ? 0 : 1;
        DB::table('shorts')->where('id', $id)->update(['is_active' => $newActive, 'updated_at' => now()]);
        return response()->json(['is_active' => $newActive, 'message' => $newActive ? '활성화됨' : '숨김 처리됨']);
    }

    public function getShorts(Request $req)'''

if old_get_shorts in ctrl:
    ctrl = ctrl.replace(old_get_shorts, new_blind)
    print("blindShort added")
    print(write_file('/var/www/somekorean/app/Http/Controllers/API/AdminController.php', ctrl))
else:
    print("WARN: getShorts pattern not found")

# ── 2. Add blind route to api.php ─────────────────────────────────────────────
print("\n=== 2. Adding blind route ===")
raw = ssh('base64 /var/www/somekorean/routes/api.php')
api = base64.b64decode(raw).decode('utf-8')

old_shorts_route = "Route::delete('shorts/{id}',           [AdminController::class, 'deleteShort']);"
new_shorts_routes = """Route::patch('shorts/{id}/blind',      [AdminController::class, 'blindShort']);
        Route::delete('shorts/{id}',           [AdminController::class, 'deleteShort']);"""

if old_shorts_route in api:
    api = api.replace(old_shorts_route, new_shorts_routes)
    print("Blind route added")
    print(write_file('/var/www/somekorean/routes/api.php', api))
else:
    print("WARN: pattern not found, current shorts routes:")
    idx = api.find("'shorts/")
    print(api[max(0,idx-100):idx+200])

# ── 3. AdminShorts.vue – Real API integration ─────────────────────────────────
print("\n=== 3. Writing AdminShorts.vue ===")
admin_shorts = '''<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-400 mb-1">전체 숏츠</p>
        <p class="text-2xl font-black text-gray-800">{{ stats.total }}</p>
        <p class="text-xs text-gray-400 mt-1">등록된 모든 숏츠</p>
      </div>
      <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-400 mb-1">YouTube</p>
        <p class="text-2xl font-black text-red-500">{{ stats.youtube }}</p>
        <p class="text-xs text-gray-400 mt-1">자동 수집</p>
      </div>
      <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-400 mb-1">회원 업로드</p>
        <p class="text-2xl font-black text-blue-500">{{ stats.member }}</p>
        <p class="text-xs text-gray-400 mt-1">회원이 직접 등록</p>
      </div>
      <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
        <p class="text-xs text-gray-400 mb-1">숨김 처리</p>
        <p class="text-2xl font-black text-orange-500">{{ stats.hidden }}</p>
        <p class="text-xs text-gray-400 mt-1">비활성 숏츠</p>
      </div>
    </div>

    <!-- 필터 / 검색 -->
    <div class="bg-white rounded-2xl shadow-sm p-4 border border-gray-100">
      <div class="flex flex-wrap gap-3 items-center">
        <!-- 플랫폼 탭 -->
        <div class="flex gap-1 bg-gray-100 rounded-xl p-1">
          <button v-for="pt in platformTabs" :key="pt.key"
            @click="filterPlatform = pt.key; loadShorts()"
            :class="['px-3 py-1.5 rounded-lg text-xs font-semibold transition', filterPlatform === pt.key ? 'bg-white shadow-sm text-gray-800' : 'text-gray-500 hover:text-gray-700']">
            {{ pt.label }}
          </button>
        </div>
        <!-- 상태 필터 -->
        <select v-model="filterStatus" @change="loadShorts"
          class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 상태</option>
          <option value="1">활성</option>
          <option value="0">숨김</option>
        </select>
        <!-- 검색 -->
        <div class="flex gap-2 flex-1 min-w-48">
          <input v-model="search" @keyup.enter="loadShorts" type="text" placeholder="제목 검색..."
            class="flex-1 border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-blue-400"/>
          <button @click="loadShorts" class="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 transition">검색</button>
        </div>
      </div>
    </div>

    <!-- 숏츠 목록 테이블 -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
        <h3 class="font-bold text-gray-800 text-sm">숏츠 목록</h3>
        <span class="text-xs text-gray-400">총 {{ totalCount }}개</span>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="flex items-center justify-center py-16">
        <div class="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full"></div>
      </div>

      <!-- 데이터 없음 -->
      <div v-else-if="!shorts.length" class="text-center py-16 text-gray-400">
        <p class="text-4xl mb-3">📱</p>
        <p class="text-sm">등록된 숏츠가 없습니다</p>
      </div>

      <!-- 테이블 -->
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 w-64">숏츠</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">플랫폼</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">업로더</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500">조회</th>
              <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500">좋아요</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500">상태</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">등록일</th>
              <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="s in shorts" :key="s.id" class="hover:bg-gray-50 transition-colors">
              <!-- 썸네일 + 제목 -->
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="relative flex-shrink-0 cursor-pointer" @click="preview(s)">
                    <div class="w-16 h-10 bg-gray-200 rounded-lg overflow-hidden">
                      <img v-if="s.thumbnail" :src="s.thumbnail" class="w-full h-full object-cover"/>
                      <div v-else class="w-full h-full flex items-center justify-center text-gray-400 text-xs">No Img</div>
                    </div>
                    <!-- 재생 버튼 오버레이 -->
                    <div class="absolute inset-0 flex items-center justify-center bg-black/20 rounded-lg hover:bg-black/40 transition">
                      <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z"/>
                      </svg>
                    </div>
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-800 truncate max-w-36">
                      {{ s.title || s.url }}
                    </p>
                    <p class="text-xs text-gray-400 truncate max-w-36">{{ s.url }}</p>
                  </div>
                </div>
              </td>
              <!-- 플랫폼 -->
              <td class="px-4 py-3">
                <span :class="platformBadgeClass(s.platform)"
                  class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold">
                  {{ platformLabel(s.platform) }}
                </span>
              </td>
              <!-- 업로더 -->
              <td class="px-4 py-3">
                <span class="text-sm text-gray-600">
                  {{ s.user_name || (s.user_id ? '회원 #'+s.user_id : '자동수집') }}
                </span>
              </td>
              <!-- 조회수 -->
              <td class="px-4 py-3 text-right">
                <span class="text-sm text-gray-600">{{ (s.view_count||0).toLocaleString() }}</span>
              </td>
              <!-- 좋아요 -->
              <td class="px-4 py-3 text-right">
                <span class="text-sm text-gray-600">{{ (s.like_count||0).toLocaleString() }}</span>
              </td>
              <!-- 상태 -->
              <td class="px-4 py-3 text-center">
                <span :class="s.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                  class="px-2 py-1 rounded-full text-xs font-semibold">
                  {{ s.is_active ? '활성' : '숨김' }}
                </span>
              </td>
              <!-- 등록일 -->
              <td class="px-4 py-3 text-xs text-gray-400">{{ formatDate(s.created_at) }}</td>
              <!-- 관리 -->
              <td class="px-4 py-3">
                <div class="flex items-center justify-center gap-1">
                  <button @click="preview(s)"
                    class="p-1.5 text-blue-500 hover:bg-blue-50 rounded-lg transition text-xs" title="미리보기">▶</button>
                  <button @click="toggleBlind(s)"
                    :class="s.is_active ? 'text-orange-500 hover:bg-orange-50' : 'text-green-500 hover:bg-green-50'"
                    class="p-1.5 rounded-lg transition text-xs" :title="s.is_active ? '숨김' : '활성화'">
                    {{ s.is_active ? '🙈' : '👁' }}
                  </button>
                  <button @click="deleteShort(s)"
                    class="p-1.5 text-red-400 hover:bg-red-50 rounded-lg transition text-xs" title="삭제">🗑</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="totalPages > 1" class="px-5 py-3 border-t border-gray-100 flex items-center justify-between">
        <span class="text-xs text-gray-400">{{ currentPage }} / {{ totalPages }} 페이지</span>
        <div class="flex gap-1">
          <button @click="changePage(currentPage-1)" :disabled="currentPage===1"
            class="px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition">이전</button>
          <button v-for="p in pageList" :key="p"
            @click="typeof p === 'number' && changePage(p)"
            :class="['px-3 py-1.5 text-xs rounded-lg border transition',
              p === currentPage ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-200 hover:bg-gray-50',
              typeof p !== 'number' ? 'cursor-default text-gray-400' : '']">
            {{ p }}
          </button>
          <button @click="changePage(currentPage+1)" :disabled="currentPage===totalPages"
            class="px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition">다음</button>
        </div>
      </div>
    </div>

    <!-- 미리보기 모달 -->
    <Transition name="fade">
      <div v-if="previewShort" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
        @click.self="previewShort = null">
        <div class="bg-black rounded-2xl overflow-hidden w-full max-w-sm shadow-2xl">
          <!-- 모달 헤더 -->
          <div class="flex items-center justify-between px-4 py-3 bg-gray-900">
            <div class="flex-1 min-w-0">
              <p class="text-white text-sm font-semibold truncate">{{ previewShort.title || '숏츠 미리보기' }}</p>
              <p class="text-gray-400 text-xs mt-0.5">{{ platformLabel(previewShort.platform) }}</p>
            </div>
            <button @click="previewShort = null" class="text-gray-400 hover:text-white ml-3 text-xl leading-none">✕</button>
          </div>
          <!-- 9:16 비율 iframe -->
          <div class="relative w-full" style="padding-top: 177.77%">
            <iframe class="absolute inset-0 w-full h-full border-0"
              :src="previewEmbedUrl"
              allow="autoplay; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen>
            </iframe>
          </div>
          <!-- 정보 -->
          <div class="px-4 py-3 bg-gray-900 flex items-center justify-between">
            <div class="flex gap-4 text-xs text-gray-400">
              <span>👁 {{ (previewShort.view_count||0).toLocaleString() }}</span>
              <span>❤️ {{ (previewShort.like_count||0).toLocaleString() }}</span>
            </div>
            <a :href="previewShort.url" target="_blank" rel="noopener"
              class="text-xs text-blue-400 hover:text-blue-300">원본 보기 →</a>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const shorts       = ref([])
const loading      = ref(false)
const search       = ref('')
const filterPlatform = ref('')
const filterStatus = ref('')
const currentPage  = ref(1)
const totalPages   = ref(1)
const totalCount   = ref(0)
const previewShort = ref(null)

const stats = ref({ total: 0, youtube: 0, member: 0, hidden: 0 })

const platformTabs = [
  { key: '', label: '전체' },
  { key: 'youtube', label: 'YouTube' },
  { key: 'tiktok', label: 'TikTok' },
  { key: 'instagram', label: 'Instagram' },
  { key: 'member', label: '회원업로드' },
]

const pageList = computed(() => {
  const pages = []
  const delta = 2
  const left = Math.max(2, currentPage.value - delta)
  const right = Math.min(totalPages.value - 1, currentPage.value + delta)
  pages.push(1)
  if (left > 2) pages.push('...')
  for (let i = left; i <= right; i++) pages.push(i)
  if (right < totalPages.value - 1) pages.push('...')
  if (totalPages.value > 1) pages.push(totalPages.value)
  return pages
})

const previewEmbedUrl = computed(() => {
  if (!previewShort.value) return ''
  const s = previewShort.value
  if (s.platform !== 'youtube') return s.embed_url || s.url
  const match = (s.url || s.embed_url || '').match(/(?:shorts\\/|embed\\/|v=|youtu\\.be\\/)([A-Za-z0-9_-]{11})/)
  if (!match) return s.embed_url || ''
  const vid = match[1]
  return `https://www.youtube.com/embed/${vid}?autoplay=1&mute=0&controls=1&rel=0&playsinline=1`
})

async function loadShorts() {
  loading.value = true
  try {
    const params = { page: currentPage.value }
    if (search.value) params.search = search.value
    if (filterPlatform.value && filterPlatform.value !== 'member') params.platform = filterPlatform.value
    if (filterStatus.value !== '') params.is_active = filterStatus.value
    const { data } = await axios.get('/api/admin/shorts', { params })
    const items = data.data || data
    shorts.value = filterPlatform.value === 'member'
      ? items.filter(s => s.user_id && s.platform !== 'youtube')
      : items
    totalPages.value = data.last_page || 1
    totalCount.value = data.total || shorts.value.length
    computeStats(data.all || items)
  } catch(e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  try {
    // Load all for stats
    const { data } = await axios.get('/api/admin/shorts', { params: { per_page: 999 } })
    const all = data.data || data
    stats.value = {
      total:   all.length,
      youtube: all.filter(s => s.platform === 'youtube').length,
      member:  all.filter(s => s.user_id && s.platform !== 'youtube').length,
      hidden:  all.filter(s => !s.is_active).length,
    }
  } catch {}
}

function computeStats(items) {
  if (!items.length) return
  stats.value = {
    total:   totalCount.value || items.length,
    youtube: items.filter(s => s.platform === 'youtube').length,
    member:  items.filter(s => s.user_id && s.platform !== 'youtube').length,
    hidden:  items.filter(s => !s.is_active).length,
  }
}

function changePage(p) {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  loadShorts()
}

function preview(s) {
  previewShort.value = s
}

async function toggleBlind(s) {
  try {
    const { data } = await axios.patch(`/api/admin/shorts/${s.id}/blind`)
    s.is_active = data.is_active
    // Update stats
    stats.value.hidden = shorts.value.filter(x => !x.is_active).length
  } catch(e) {
    alert('처리 실패: ' + (e.response?.data?.message || e.message))
  }
}

async function deleteShort(s) {
  if (!confirm(`"${s.title || s.url}" 숏츠를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/shorts/${s.id}`)
    shorts.value = shorts.value.filter(x => x.id !== s.id)
    totalCount.value--
    stats.value.total--
  } catch(e) {
    alert('삭제 실패: ' + (e.response?.data?.message || e.message))
  }
}

function platformLabel(p) {
  return { youtube: '▶ YouTube', tiktok: '🎵 TikTok', instagram: '📸 Instagram', other: '🔗 기타' }[p] || p
}

function platformBadgeClass(p) {
  return {
    youtube:   'bg-red-100 text-red-700',
    tiktok:    'bg-gray-900 text-white',
    instagram: 'bg-pink-100 text-pink-700',
    other:     'bg-gray-100 text-gray-600',
  }[p] || 'bg-gray-100 text-gray-600'
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR', { year: '2-digit', month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  loadShorts()
  loadStats()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s }
.fade-enter-from, .fade-leave-to { opacity: 0 }
</style>
'''
print(write_file('/var/www/somekorean/resources/js/pages/admin/AdminShorts.vue', admin_shorts))

# ── 4. AdminRecipes.vue – Fix detail modal ────────────────────────────────────
print("\n=== 4. Writing AdminRecipes.vue ===")
admin_recipes = '''<template>
  <div class="space-y-5">

    <!-- 탭 -->
    <div class="flex gap-1 bg-white rounded-2xl p-1 shadow-sm border border-gray-100 w-fit">
      <button v-for="t in tabs" :key="t.key" @click="activeTab = t.key"
        :class="['px-5 py-2 rounded-xl text-sm font-semibold transition', activeTab === t.key ? 'bg-orange-500 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50']">
        {{ t.label }}
      </button>
    </div>

    <!-- ── TAB 1: 레시피 목록 ── -->
    <div v-if="activeTab === 'list'" class="space-y-4">

      <!-- 통계 카드 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
          <p class="text-xs text-gray-400 mb-1">전체 레시피</p>
          <p class="text-2xl font-black text-gray-800">{{ recipeStats.total }}</p>
        </div>
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
          <p class="text-xs text-gray-400 mb-1">이번 주 등록</p>
          <p class="text-2xl font-black text-green-500">{{ recipeStats.thisWeek }}</p>
        </div>
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
          <p class="text-xs text-gray-400 mb-1">사진 있음</p>
          <p class="text-2xl font-black text-blue-500">{{ recipeStats.withImage }}</p>
        </div>
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-gray-100">
          <p class="text-xs text-gray-400 mb-1">숨김 처리</p>
          <p class="text-2xl font-black text-orange-500">{{ recipeStats.hidden }}</p>
        </div>
      </div>

      <!-- 필터 -->
      <div class="bg-white rounded-2xl shadow-sm p-4 border border-gray-100">
        <div class="flex flex-wrap gap-3 items-center">
          <input v-model="recipeSearch" @keyup.enter="loadRecipes" type="text" placeholder="레시피 제목 검색..."
            class="border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-orange-400 flex-1 min-w-40"/>
          <select v-model="recipeCategory" @change="loadRecipes"
            class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400">
            <option value="">전체 카테고리</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.icon }} {{ cat.name }}</option>
          </select>
          <select v-model="recipeDifficulty" @change="loadRecipes"
            class="border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400">
            <option value="">전체 난이도</option>
            <option value="쉬움">쉬움</option>
            <option value="보통">보통</option>
            <option value="어려움">어려움</option>
          </select>
          <button @click="loadRecipes" class="bg-orange-500 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-orange-600 transition">검색</button>
        </div>
      </div>

      <!-- 테이블 -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between">
          <h3 class="font-bold text-gray-800 text-sm">레시피 목록</h3>
          <span class="text-xs text-gray-400">총 {{ recipeTotalCount }}개</span>
        </div>

        <div v-if="recipeLoading" class="flex items-center justify-center py-16">
          <div class="animate-spin w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full"></div>
        </div>
        <div v-else-if="!recipes.length" class="text-center py-16 text-gray-400">
          <p class="text-4xl mb-3">🍳</p>
          <p class="text-sm">등록된 레시피가 없습니다</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 w-64">레시피</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">카테고리</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">작성자</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500">난이도</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500">좋아요</th>
                <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500">조회</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500">상태</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">등록일</th>
                <th class="px-4 py-3 text-center text-xs font-semibold text-gray-500">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="r in recipes" :key="r.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3">
                  <div class="flex items-center gap-3">
                    <div class="w-14 h-14 bg-orange-50 rounded-xl overflow-hidden flex-shrink-0">
                      <img v-if="r.image_url" :src="r.image_url" class="w-full h-full object-cover"
                        @error="$event.target.style.display='none'"/>
                      <div v-else class="w-full h-full flex items-center justify-center text-2xl">🍳</div>
                    </div>
                    <div class="min-w-0">
                      <p class="font-semibold text-gray-800 truncate max-w-40">{{ r.title }}</p>
                      <p class="text-xs text-gray-400 truncate max-w-40 mt-0.5">{{ r.intro || '소개 없음' }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span class="bg-orange-100 text-orange-700 px-2 py-1 rounded-full text-xs font-semibold">
                    {{ r.category?.icon }} {{ r.category?.name || '-' }}
                  </span>
                </td>
                <td class="px-4 py-3 text-xs text-gray-500">{{ r.user?.name || r.user?.username || '-' }}</td>
                <td class="px-4 py-3 text-center">
                  <span :class="diffClass(r.difficulty)" class="px-2 py-0.5 rounded-full text-xs font-semibold">
                    {{ r.difficulty || '-' }}
                  </span>
                </td>
                <td class="px-4 py-3 text-right text-xs text-gray-500">{{ r.like_count || 0 }}</td>
                <td class="px-4 py-3 text-right text-xs text-gray-500">{{ r.view_count || 0 }}</td>
                <td class="px-4 py-3 text-center">
                  <span :class="r.is_hidden ? 'bg-gray-100 text-gray-500' : 'bg-green-100 text-green-700'"
                    class="px-2 py-1 rounded-full text-xs font-semibold">
                    {{ r.is_hidden ? '숨김' : '공개' }}
                  </span>
                </td>
                <td class="px-4 py-3 text-xs text-gray-400">{{ formatDate(r.created_at) }}</td>
                <td class="px-4 py-3">
                  <div class="flex items-center justify-center gap-1">
                    <button @click="viewRecipe(r)" title="상세보기"
                      class="p-1.5 text-blue-500 hover:bg-blue-50 rounded-lg transition text-xs">👁</button>
                    <button @click="editRecipe(r)" title="수정"
                      class="p-1.5 text-gray-500 hover:bg-gray-100 rounded-lg transition text-xs">✏️</button>
                    <button @click="toggleHide(r)" :title="r.is_hidden ? '공개' : '숨김'"
                      :class="r.is_hidden ? 'text-green-500 hover:bg-green-50' : 'text-orange-500 hover:bg-orange-50'"
                      class="p-1.5 rounded-lg transition text-xs">{{ r.is_hidden ? '👁' : '🙈' }}</button>
                    <button @click="deleteRecipe(r)" title="삭제"
                      class="p-1.5 text-red-400 hover:bg-red-50 rounded-lg transition text-xs">🗑</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 페이지네이션 -->
        <div v-if="recipeTotalPages > 1" class="px-5 py-3 border-t border-gray-100 flex items-center justify-between">
          <span class="text-xs text-gray-400">{{ recipePage }} / {{ recipeTotalPages }} 페이지</span>
          <div class="flex gap-1">
            <button @click="changeRecipePage(recipePage-1)" :disabled="recipePage===1"
              class="px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50">이전</button>
            <button v-for="p in recipePageList" :key="p"
              @click="typeof p === 'number' && changeRecipePage(p)"
              :class="['px-3 py-1.5 text-xs rounded-lg border',
                p === recipePage ? 'bg-orange-500 text-white border-orange-500' : 'border-gray-200 hover:bg-gray-50']">
              {{ p }}
            </button>
            <button @click="changeRecipePage(recipePage+1)" :disabled="recipePage===recipeTotalPages"
              class="px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50">다음</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ── TAB 2: 카테고리 관리 ── -->
    <div v-if="activeTab === 'categories'" class="space-y-4">
      <div class="bg-white rounded-2xl shadow-sm p-5 border border-gray-100">
        <h3 class="font-bold text-gray-800 mb-4">카테고리 추가</h3>
        <div class="flex gap-3 flex-wrap">
          <input v-model="newCat.name" type="text" placeholder="카테고리 이름" class="border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-orange-400 flex-1 min-w-32"/>
          <input v-model="newCat.key" type="text" placeholder="키 (영문)" class="border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-orange-400 w-32"/>
          <input v-model="newCat.icon" type="text" placeholder="이모지" class="border border-gray-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-orange-400 w-20"/>
          <button @click="addCategory" class="bg-orange-500 text-white px-5 py-2 rounded-xl text-sm font-medium hover:bg-orange-600 transition">추가</button>
        </div>
      </div>
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500">아이콘</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500">이름</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500">키</th>
              <th class="px-5 py-3 text-center text-xs font-semibold text-gray-500">상태</th>
              <th class="px-5 py-3 text-center text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="cat in categories" :key="cat.id" class="hover:bg-gray-50">
              <td class="px-5 py-3 text-xl">{{ cat.icon }}</td>
              <td class="px-5 py-3 font-medium text-gray-800">{{ cat.name }}</td>
              <td class="px-5 py-3 font-mono text-xs text-gray-500">{{ cat.key }}</td>
              <td class="px-5 py-3 text-center">
                <button @click="toggleCatStatus(cat)"
                  :class="cat.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                  class="px-3 py-1 rounded-full text-xs font-semibold hover:opacity-80 transition">
                  {{ cat.is_active ? '활성' : '비활성' }}
                </button>
              </td>
              <td class="px-5 py-3 text-center">
                <button @click="deleteCategory(cat)" class="p-1.5 text-red-400 hover:bg-red-50 rounded-lg transition text-xs">🗑</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── 상세 보기 모달 ── -->
    <Transition name="fade">
      <div v-if="viewModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="viewModal = null">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <!-- 헤더 -->
          <div class="sticky top-0 bg-white px-6 py-4 border-b flex items-center justify-between z-10">
            <h2 class="font-black text-gray-800 text-lg">레시피 상세</h2>
            <button @click="viewModal = null" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">✕</button>
          </div>
          <!-- 내용 -->
          <div class="p-6 space-y-5">
            <!-- 대표 이미지 -->
            <div v-if="viewModal.image_url" class="rounded-2xl overflow-hidden h-56 bg-gray-100">
              <img :src="viewModal.image_url" class="w-full h-full object-cover"
                @error="$event.target.parentElement.style.display='none'"/>
            </div>
            <!-- 제목 + 기본 정보 -->
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span v-if="viewModal.category" class="bg-orange-100 text-orange-700 px-2 py-1 rounded-full text-xs font-semibold">
                  {{ viewModal.category?.icon }} {{ viewModal.category?.name }}
                </span>
                <span v-if="viewModal.difficulty" :class="diffClass(viewModal.difficulty)" class="px-2 py-1 rounded-full text-xs font-semibold">
                  {{ viewModal.difficulty }}
                </span>
              </div>
              <h3 class="text-xl font-black text-gray-800 mb-2">{{ viewModal.title }}</h3>
              <p v-if="viewModal.intro" class="text-gray-600 text-sm leading-relaxed">{{ viewModal.intro }}</p>
            </div>
            <!-- 기본 정보 칩 -->
            <div class="flex flex-wrap gap-2">
              <span v-if="viewModal.cook_time" class="bg-gray-100 text-gray-600 px-3 py-1.5 rounded-full text-xs">⏱ {{ viewModal.cook_time }}</span>
              <span v-if="viewModal.servings" class="bg-gray-100 text-gray-600 px-3 py-1.5 rounded-full text-xs">👥 {{ viewModal.servings }}인분</span>
              <span v-if="viewModal.calories" class="bg-gray-100 text-gray-600 px-3 py-1.5 rounded-full text-xs">🔥 {{ viewModal.calories }}kcal</span>
            </div>
            <!-- 재료 -->
            <div v-if="viewModal.ingredients && viewModal.ingredients.length">
              <h4 class="font-bold text-gray-700 mb-3 text-sm">재료</h4>
              <div class="grid grid-cols-2 gap-2">
                <div v-for="(ing, i) in viewModal.ingredients" :key="i"
                  class="flex items-center justify-between bg-orange-50 rounded-xl px-3 py-2">
                  <span class="text-sm text-gray-700">{{ ing.name || ing }}</span>
                  <span class="text-xs text-orange-600 font-medium">{{ ing.amount || '' }}</span>
                </div>
              </div>
            </div>
            <!-- 조리 순서 -->
            <div v-if="viewModal.steps && viewModal.steps.length">
              <h4 class="font-bold text-gray-700 mb-3 text-sm">조리 순서</h4>
              <div class="space-y-3">
                <div v-for="(step, i) in viewModal.steps" :key="i" class="flex gap-3">
                  <div class="flex-shrink-0 w-7 h-7 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs font-bold">{{ i+1 }}</div>
                  <p class="text-sm text-gray-700 leading-relaxed pt-0.5">{{ step.text || step }}</p>
                </div>
              </div>
            </div>
            <!-- 팁 -->
            <div v-if="viewModal.tips && viewModal.tips.length">
              <h4 class="font-bold text-gray-700 mb-2 text-sm">요리 팁</h4>
              <ul class="space-y-1.5">
                <li v-for="(tip, i) in viewModal.tips" :key="i" class="flex items-start gap-2 text-sm text-gray-600">
                  <span class="text-orange-400 flex-shrink-0">💡</span> {{ tip }}
                </li>
              </ul>
            </div>
            <!-- 태그 -->
            <div v-if="viewModal.tags && viewModal.tags.length">
              <div class="flex flex-wrap gap-2">
                <span v-for="tag in viewModal.tags" :key="tag"
                  class="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-xs">#{{ tag }}</span>
              </div>
            </div>
            <!-- 작성자 -->
            <div class="pt-2 border-t border-gray-100 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-gray-200 overflow-hidden">
                  <img v-if="viewModal.user?.avatar" :src="viewModal.user.avatar" class="w-full h-full object-cover"/>
                </div>
                <span class="text-sm text-gray-600">{{ viewModal.user?.name || viewModal.user?.username || '작성자 정보 없음' }}</span>
              </div>
              <span class="text-xs text-gray-400">{{ formatDate(viewModal.created_at) }}</span>
            </div>
          </div>
          <!-- 하단 버튼 -->
          <div class="sticky bottom-0 bg-gray-50 px-6 py-4 border-t flex gap-3">
            <button @click="editFromView" class="flex-1 bg-orange-500 text-white py-2.5 rounded-xl text-sm font-bold hover:bg-orange-600 transition">수정하기</button>
            <button @click="viewModal = null" class="flex-1 border border-gray-200 text-gray-600 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-100 transition">닫기</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- ── 수정 모달 ── -->
    <Transition name="fade">
      <div v-if="editModal" class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="editModal = null">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg">
          <div class="px-6 py-4 border-b flex items-center justify-between">
            <h2 class="font-black text-gray-800">레시피 수정</h2>
            <button @click="editModal = null" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">✕</button>
          </div>
          <div class="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
            <!-- 이미지 미리보기 -->
            <div v-if="editModal.image_url" class="rounded-xl overflow-hidden h-40 bg-gray-100">
              <img :src="editModal.image_url" class="w-full h-full object-cover" @error="$event.target.parentElement.style.display='none'"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">이미지 URL</label>
              <input v-model="editModal.image_url" type="text" placeholder="이미지 URL"
                class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-orange-400"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">제목 <span class="text-red-500">*</span></label>
              <input v-model="editModal.title" type="text"
                class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-orange-400"/>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">카테고리</label>
              <select v-model="editModal.category_id" class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-orange-400">
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.icon }} {{ cat.name }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">소개</label>
              <textarea v-model="editModal.intro" rows="3"
                class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-orange-400 resize-none"></textarea>
            </div>
            <div class="grid grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1">난이도</label>
                <select v-model="editModal.difficulty" class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-orange-400">
                  <option value="">선택</option>
                  <option value="쉬움">쉬움</option>
                  <option value="보통">보통</option>
                  <option value="어려움">어려움</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1">조리 시간</label>
                <input v-model="editModal.cook_time" type="text" placeholder="예: 30분"
                  class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-orange-400"/>
              </div>
              <div>
                <label class="block text-xs font-semibold text-gray-500 mb-1">인분</label>
                <input v-model="editModal.servings" type="number" min="1"
                  class="w-full border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-orange-400"/>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 border-t flex gap-3">
            <button @click="saveEdit" :disabled="saving"
              class="flex-1 bg-orange-500 text-white py-2.5 rounded-xl text-sm font-bold hover:bg-orange-600 transition disabled:opacity-60">
              {{ saving ? '저장 중...' : '저장' }}
            </button>
            <button @click="editModal = null" class="flex-1 border border-gray-200 text-gray-600 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-100 transition">취소</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const activeTab = ref('list')
const tabs = [
  { key: 'list', label: '레시피 목록' },
  { key: 'categories', label: '카테고리 관리' },
]

// Recipe list state
const recipes      = ref([])
const categories   = ref([])
const recipeLoading = ref(false)
const recipeSearch  = ref('')
const recipeCategory = ref('')
const recipeDifficulty = ref('')
const recipePage    = ref(1)
const recipeTotalPages = ref(1)
const recipeTotalCount = ref(0)
const recipeStats = ref({ total: 0, thisWeek: 0, withImage: 0, hidden: 0 })

// Modals
const viewModal = ref(null)
const editModal = ref(null)
const saving    = ref(false)

// Category form
const newCat = ref({ name: '', key: '', icon: '' })

const recipePageList = computed(() => {
  const pages = []
  const delta = 2
  const left = Math.max(2, recipePage.value - delta)
  const right = Math.min(recipeTotalPages.value - 1, recipePage.value + delta)
  pages.push(1)
  if (left > 2) pages.push('...')
  for (let i = left; i <= right; i++) pages.push(i)
  if (right < recipeTotalPages.value - 1) pages.push('...')
  if (recipeTotalPages.value > 1) pages.push(recipeTotalPages.value)
  return pages
})

async function loadRecipes() {
  recipeLoading.value = true
  try {
    const params = { page: recipePage.value }
    if (recipeSearch.value) params.search = recipeSearch.value
    if (recipeCategory.value) params.category = recipeCategory.value
    if (recipeDifficulty.value) params.difficulty = recipeDifficulty.value
    const { data } = await axios.get('/api/admin/recipes/list', { params })
    recipes.value = data.data || data
    recipeTotalPages.value = data.last_page || 1
    recipeTotalCount.value = data.total || recipes.value.length
  } catch(e) { console.error(e) }
  finally { recipeLoading.value = false }
}

async function loadStats() {
  try {
    const { data } = await axios.get('/api/admin/recipes/stats')
    recipeStats.value = {
      total:     data.total || 0,
      thisWeek:  data.this_week || data.thisWeek || 0,
      withImage: data.with_image || data.withImage || 0,
      hidden:    data.hidden || 0,
    }
  } catch {}
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/admin/recipes/categories')
    categories.value = data
  } catch {}
}

function changeRecipePage(p) {
  if (p < 1 || p > recipeTotalPages.value) return
  recipePage.value = p
  loadRecipes()
}

async function viewRecipe(r) {
  try {
    const { data } = await axios.get(`/api/admin/recipes/${r.id}`)
    viewModal.value = data
  } catch {
    viewModal.value = { ...r }
  }
}

function editRecipe(r) {
  editModal.value = { ...r, category_id: r.category_id || r.category?.id }
  viewModal.value = null
}

function editFromView() {
  if (viewModal.value) {
    editModal.value = { ...viewModal.value, category_id: viewModal.value.category_id || viewModal.value.category?.id }
    viewModal.value = null
  }
}

async function saveEdit() {
  if (!editModal.value) return
  saving.value = true
  try {
    const payload = {
      title: editModal.value.title,
      intro: editModal.value.intro,
      category_id: editModal.value.category_id,
      difficulty: editModal.value.difficulty,
      cook_time: editModal.value.cook_time,
      servings: editModal.value.servings,
      image_url: editModal.value.image_url,
    }
    await axios.put(`/api/admin/recipes/${editModal.value.id}`, payload)
    // Update in list
    const idx = recipes.value.findIndex(r => r.id === editModal.value.id)
    if (idx >= 0) Object.assign(recipes.value[idx], payload)
    editModal.value = null
  } catch(e) {
    alert('저장 실패: ' + (e.response?.data?.message || e.message))
  } finally {
    saving.value = false
  }
}

async function toggleHide(r) {
  try {
    await axios.put(`/api/admin/recipes/${r.id}`, { is_hidden: !r.is_hidden })
    r.is_hidden = !r.is_hidden
  } catch(e) {
    alert('처리 실패')
  }
}

async function deleteRecipe(r) {
  if (!confirm(`"${r.title}" 레시피를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/recipes/${r.id}`)
    recipes.value = recipes.value.filter(x => x.id !== r.id)
    recipeTotalCount.value--
    recipeStats.value.total--
  } catch(e) {
    alert('삭제 실패')
  }
}

async function addCategory() {
  if (!newCat.value.name || !newCat.value.key) { alert('이름과 키를 입력해주세요'); return }
  try {
    const { data } = await axios.post('/api/admin/recipes/categories', newCat.value)
    categories.value.push(data)
    newCat.value = { name: '', key: '', icon: '' }
  } catch(e) {
    alert('추가 실패: ' + (e.response?.data?.message || e.message))
  }
}

async function toggleCatStatus(cat) {
  try {
    const { data } = await axios.put(`/api/admin/recipes/categories/${cat.id}`, { is_active: !cat.is_active })
    cat.is_active = data.is_active ?? !cat.is_active
  } catch {}
}

async function deleteCategory(cat) {
  if (!confirm(`"${cat.name}" 카테고리를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/recipes/categories/${cat.id}`)
    categories.value = categories.value.filter(c => c.id !== cat.id)
  } catch(e) {
    alert('삭제 실패')
  }
}

function diffClass(d) {
  if (d === '쉬움') return 'bg-green-100 text-green-700'
  if (d === '어려움') return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleDateString('ko-KR', { year: '2-digit', month: '2-digit', day: '2-digit' })
}

onMounted(() => {
  loadRecipes()
  loadCategories()
  loadStats()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s }
.fade-enter-from, .fade-leave-to { opacity: 0 }
</style>
'''
print(write_file('/var/www/somekorean/resources/js/pages/admin/AdminRecipes.vue', admin_recipes))

# ── 5. Fix AdminRecipeController stats ─────────────────────────────────────────
print("\n=== 5. Fixing AdminRecipeController stats ===")
raw = ssh('base64 /var/www/somekorean/app/Http/Controllers/API/AdminRecipeController.php')
actl = base64.b64decode(raw).decode('utf-8')

old_stats = 'public function stats() {'
new_stats = '''public function stats() {
        $now = now();
        $weekStart = $now->copy()->startOfWeek();
        return response()->json([
            'total'      => RecipePost::where('source','user')->count(),
            'this_week'  => RecipePost::where('source','user')->where('created_at', '>=', $weekStart)->count(),
            'with_image' => RecipePost::where('source','user')->whereNotNull('image_url')->where('image_url','!=','')->count(),
            'hidden'     => RecipePost::where('source','user')->where('is_hidden', true)->count(),
        ]);
    }
    public function _stats_old() {'''

if old_stats in actl:
    actl = actl.replace(old_stats, new_stats)
    print("Stats method updated")
    print(write_file('/var/www/somekorean/app/Http/Controllers/API/AdminRecipeController.php', actl))
else:
    print("WARN: stats pattern not found")

# ── 6. Build ──────────────────────────────────────────────────────────────────
print("\n=== 6. Building ===")
result = ssh('cd /var/www/somekorean && npm run build 2>&1', timeout=180)
lines = result.splitlines()
has_error = any('Error' in l for l in lines if 'WARN' not in l)
if has_error:
    for l in lines:
        if 'Error' in l and 'WARN' not in l:
            print(l)
print('\n'.join(lines[-8:]))
c.close()
