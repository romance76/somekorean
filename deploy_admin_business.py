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
    chunk_size = 3000
    chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]
    ssh('> /tmp/_wf.b64')
    for chunk in chunks:
        ssh(f"echo -n '{chunk}' >> /tmp/_wf.b64")
    result = ssh(f'base64 -d /tmp/_wf.b64 > {path} && rm /tmp/_wf.b64 && echo OK')
    print(f"  {path}: {result}")

admin_business_vue = '''<template>
  <div class="p-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">🏪 업소 관리</h1>
      <button @click="refreshAll" class="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg text-sm font-medium">🔄 새로고침</button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-blue-50 rounded-xl p-4"><div class="text-2xl font-bold text-blue-700">{{ statCards.total }}</div><div class="text-xs text-gray-500 mt-1">전체 업소</div></div>
      <div class="bg-green-50 rounded-xl p-4"><div class="text-2xl font-bold text-green-700">{{ statCards.claimed }}</div><div class="text-xs text-gray-500 mt-1">소유권 등록</div></div>
      <div class="bg-yellow-50 rounded-xl p-4"><div class="text-2xl font-bold text-yellow-700">{{ statCards.premium }}</div><div class="text-xs text-gray-500 mt-1">프리미엄</div></div>
      <div class="bg-red-50 rounded-xl p-4"><div class="text-2xl font-bold text-red-600">{{ statCards.pending }}</div><div class="text-xs text-gray-500 mt-1">신청 대기</div></div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6 overflow-x-auto">
      <button v-for="t in tabs" :key="t.id" @click="activeTab=t.id"
        :class="[\'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition\',
          activeTab===t.id ? \'bg-white shadow text-blue-600\' : \'text-gray-600 hover:text-gray-800\']">
        {{ t.icon }} {{ t.label }}
        <span v-if="t.id===\'claims\' && statCards.pending" class="ml-1 bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">{{ statCards.pending }}</span>
      </button>
    </div>

    <!-- Tab: 업소목록 -->
    <div v-if="activeTab===\'list\'">
      <div class="bg-white rounded-xl shadow p-4 mb-4 flex flex-wrap gap-3">
        <input v-model="bizSearch" placeholder="업소명, 주소 검색..." class="flex-1 min-w-40 border rounded-lg px-3 py-2 text-sm" @keyup.enter="loadBusinesses"/>
        <select v-model="bizStatus" class="border rounded-lg px-3 py-2 text-sm">
          <option value="">전체</option>
          <option value="claimed">소유권 등록</option>
          <option value="unclaimed">미등록</option>
          <option value="premium">프리미엄</option>
        </select>
        <button @click="loadBusinesses" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700">검색</button>
      </div>
      <div class="bg-white rounded-xl shadow overflow-hidden">
        <div v-if="bizLoading" class="flex justify-center py-12"><div class="animate-spin w-6 h-6 border-4 border-blue-600 border-t-transparent rounded-full"></div></div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-600 text-xs uppercase">
            <tr>
              <th class="px-4 py-3 text-left">업소명</th>
              <th class="px-4 py-3 text-left hidden md:table-cell">주소/도시</th>
              <th class="px-4 py-3 text-center">상태</th>
              <th class="px-4 py-3 text-center">관리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="biz in businesses" :key="biz.id" class="border-t hover:bg-gray-50">
              <td class="px-4 py-3">
                <div class="font-medium">{{ biz.name }}</div>
                <div class="text-xs text-gray-400">ID: {{ biz.id }} · {{ biz.category_name || biz.category?.name }}</div>
              </td>
              <td class="px-4 py-3 hidden md:table-cell text-xs text-gray-500">{{ biz.address }}</td>
              <td class="px-4 py-3 text-center">
                <span v-if="biz.is_premium" class="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded-full">⭐ 프리미엄</span>
                <span v-else-if="biz.is_claimed" class="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded-full">✓ 등록됨</span>
                <span v-else class="bg-gray-100 text-gray-500 text-xs px-2 py-0.5 rounded-full">미등록</span>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-1 justify-center">
                  <a :href="\'/businesses/\'+biz.id" target="_blank" class="text-blue-600 hover:bg-blue-50 px-2 py-1 rounded text-xs">보기</a>
                  <button @click="togglePremium(biz)" class="text-yellow-600 hover:bg-yellow-50 px-2 py-1 rounded text-xs">{{ biz.is_premium ? \'⭐해제\' : \'⭐설정\' }}</button>
                  <button @click="deleteBiz(biz)" class="text-red-500 hover:bg-red-50 px-2 py-1 rounded text-xs">삭제</button>
                </div>
              </td>
            </tr>
            <tr v-if="!bizLoading && businesses.length===0"><td colspan="4" class="text-center py-10 text-gray-400">업소가 없습니다</td></tr>
          </tbody>
        </table>
        <div v-if="bizTotal > 0" class="flex justify-between items-center px-4 py-3 border-t text-xs text-gray-500">
          <span>총 {{ bizTotal }}개</span>
          <div class="flex gap-2">
            <button @click="bizPage--; loadBusinesses()" :disabled="bizPage<=1" class="px-3 py-1 rounded border disabled:opacity-40 hover:bg-gray-50">이전</button>
            <span class="px-2 py-1">{{ bizPage }}</span>
            <button @click="bizPage++; loadBusinesses()" :disabled="bizPage*20>=bizTotal" class="px-3 py-1 rounded border disabled:opacity-40 hover:bg-gray-50">다음</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab: 소유권 신청 -->
    <div v-if="activeTab===\'claims\'">
      <div class="bg-white rounded-xl shadow overflow-hidden">
        <div class="p-4 border-b flex flex-wrap gap-2">
          <button v-for="s in claimStatuses" :key="s.id" @click="claimFilter=s.id; loadClaims()"
            :class="[\'px-3 py-1.5 rounded-lg text-xs font-medium\', claimFilter===s.id ? \'bg-blue-600 text-white\' : \'bg-gray-100 text-gray-600 hover:bg-gray-200\']">{{ s.label }}</button>
        </div>
        <div v-if="claimsLoading" class="flex justify-center py-12"><div class="animate-spin w-6 h-6 border-4 border-blue-600 border-t-transparent rounded-full"></div></div>
        <table v-else class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-600 text-xs uppercase">
            <tr>
              <th class="px-4 py-3 text-left">신청자</th>
              <th class="px-4 py-3 text-left">업소</th>
              <th class="px-4 py-3 text-center">방법</th>
              <th class="px-4 py-3 text-center">상태</th>
              <th class="px-4 py-3 text-center">신청일</th>
              <th class="px-4 py-3 text-center">처리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cl in claims" :key="cl.id" class="border-t hover:bg-gray-50">
              <td class="px-4 py-3"><div class="font-medium text-sm">{{ cl.user?.name }}</div><div class="text-xs text-gray-400">{{ cl.user?.email }}</div></td>
              <td class="px-4 py-3 text-sm">{{ cl.business?.name }}</td>
              <td class="px-4 py-3 text-center text-xs">
                <span v-if="cl.document_urls?.length" class="text-purple-600">📄 서류</span>
                <span v-else class="text-blue-600">📧 이메일</span>
              </td>
              <td class="px-4 py-3 text-center"><span :class="[\'text-xs px-2 py-0.5 rounded-full font-medium\', claimStatusStyle(cl.status)]">{{ claimStatusLabel(cl.status) }}</span></td>
              <td class="px-4 py-3 text-center text-xs text-gray-500">{{ fmtDate(cl.created_at) }}</td>
              <td class="px-4 py-3">
                <div class="flex gap-1 justify-center">
                  <button v-if="cl.document_urls?.length" @click="docsModal=cl" class="text-blue-600 text-xs px-2 py-1 rounded hover:bg-blue-50">서류</button>
                  <template v-if="[\'docs_submitted\',\'email_verified\'].includes(cl.status)">
                    <button @click="approveClaim(cl.id)" class="bg-green-100 text-green-700 text-xs px-2 py-1 rounded hover:bg-green-200">승인</button>
                    <button @click="rejectClaim(cl.id)" class="bg-red-100 text-red-600 text-xs px-2 py-1 rounded hover:bg-red-200">거절</button>
                  </template>
                </div>
              </td>
            </tr>
            <tr v-if="!claimsLoading && claims.length===0"><td colspan="6" class="text-center py-10 text-gray-400">신청 내역이 없습니다</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab: 리뷰관리 -->
    <div v-if="activeTab===\'reviews\'">
      <div class="bg-white rounded-xl shadow overflow-hidden">
        <div class="p-4 border-b flex gap-2">
          <button @click="reviewFilter=\'all\'; loadReviews()" :class="[\'px-3 py-1.5 rounded-lg text-xs font-medium\', reviewFilter===\'all\' ? \'bg-blue-600 text-white\' : \'bg-gray-100 text-gray-600\']">전체</button>
          <button @click="reviewFilter=\'reported\'; loadReviews()" :class="[\'px-3 py-1.5 rounded-lg text-xs font-medium\', reviewFilter===\'reported\' ? \'bg-red-600 text-white\' : \'bg-gray-100 text-gray-600\']">🚨 신고됨</button>
          <button @click="reviewFilter=\'hidden\'; loadReviews()" :class="[\'px-3 py-1.5 rounded-lg text-xs font-medium\', reviewFilter===\'hidden\' ? \'bg-gray-600 text-white\' : \'bg-gray-100 text-gray-600\']">숨김</button>
        </div>
        <div v-if="reviewsLoading" class="flex justify-center py-12"><div class="animate-spin w-6 h-6 border-4 border-blue-600 border-t-transparent rounded-full"></div></div>
        <div v-else class="divide-y">
          <div v-for="rv in adminReviews" :key="rv.id" class="p-4 flex gap-4">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1 flex-wrap">
                <span class="font-semibold text-sm">{{ rv.user?.name }}</span>
                <div class="flex">
                  <span v-for="s in 5" :key="s" :class="s<=rv.rating?\'text-yellow-400\':\'text-gray-200\'" class="text-xs">★</span>
                </div>
                <span class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">{{ rv.business?.name }}</span>
                <span v-if="rv.report_count>0" class="bg-red-100 text-red-600 text-xs px-1.5 py-0.5 rounded-full">신고 {{ rv.report_count }}건</span>
                <span v-if="!rv.is_visible" class="bg-gray-200 text-gray-500 text-xs px-1.5 py-0.5 rounded-full">숨김</span>
              </div>
              <p class="text-gray-700 text-sm">{{ rv.content }}</p>
            </div>
            <div class="flex flex-col gap-1 flex-shrink-0">
              <button v-if="rv.is_visible" @click="hideReview(rv)" class="text-gray-500 hover:text-red-600 text-xs px-2 py-1 rounded border hover:border-red-300">숨기기</button>
              <button v-else @click="restoreReview(rv)" class="text-green-600 text-xs px-2 py-1 rounded border hover:bg-green-50">복원</button>
              <button @click="deleteReview(rv)" class="text-red-500 text-xs px-2 py-1 rounded border hover:bg-red-50">삭제</button>
            </div>
          </div>
          <div v-if="adminReviews.length===0" class="text-center py-10 text-gray-400">리뷰가 없습니다</div>
        </div>
      </div>
    </div>

    <!-- Tab: 크롤링 -->
    <div v-if="activeTab===\'crawl\'">
      <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl shadow p-6">
          <h3 class="font-bold text-lg mb-4">🕷️ 크롤러 실행</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">도시</label>
              <select v-model="crawlCity" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="all">전체 (38개 도시)</option>
                <option v-for="city in crawlCities" :key="city">{{ city }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">카테고리</label>
              <select v-model="crawlCat" class="w-full border rounded-lg px-3 py-2 text-sm">
                <option value="all">전체 카테고리</option>
                <option v-for="cat in crawlCats" :key="cat">{{ cat }}</option>
              </select>
            </div>
            <div class="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800">
              ⚠️ 크롤링은 백그라운드에서 실행됩니다. 완료까지 수 분 소요됩니다.
            </div>
            <button @click="startCrawl" :disabled="crawling" class="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50 transition">
              {{ crawling ? \'⏳ 처리 중...\' : \'🕷️ 크롤링 시작\' }}
            </button>
          </div>
        </div>
        <div class="bg-white rounded-xl shadow p-6">
          <h3 class="font-bold text-lg mb-4">📊 업소 현황</h3>
          <div class="space-y-3 mb-4">
            <div class="flex justify-between text-sm border-b pb-2"><span class="text-gray-500">전체 업소</span><span class="font-bold">{{ statCards.total }}</span></div>
            <div class="flex justify-between text-sm border-b pb-2"><span class="text-gray-500">소유권 등록</span><span class="font-bold text-green-600">{{ statCards.claimed }}</span></div>
            <div class="flex justify-between text-sm border-b pb-2"><span class="text-gray-500">프리미엄 업소</span><span class="font-bold text-yellow-600">{{ statCards.premium }}</span></div>
            <div class="flex justify-between text-sm"><span class="text-gray-500">신청 대기</span><span class="font-bold text-red-600">{{ statCards.pending }}</span></div>
          </div>
          <div v-if="crawlLog" class="bg-gray-900 text-green-400 rounded-xl p-3 text-xs font-mono max-h-40 overflow-y-auto whitespace-pre-wrap">{{ crawlLog }}</div>
        </div>
      </div>
    </div>

    <!-- Docs Modal -->
    <div v-if="docsModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" @click.self="docsModal=null">
      <div class="bg-white rounded-2xl p-6 max-w-lg w-full">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-lg">📄 제출 서류 — {{ docsModal.business?.name }}</h3>
          <button @click="docsModal=null" class="text-gray-400 hover:text-gray-700 text-xl">✕</button>
        </div>
        <div class="grid grid-cols-2 gap-3 mb-4 max-h-60 overflow-y-auto">
          <a v-for="(doc,i) in docsModal.document_urls" :key="i" :href="\'/storage/\'+doc" target="_blank">
            <img :src="\'/storage/\'+doc" class="w-full rounded-lg object-cover h-32 hover:opacity-80"/>
          </a>
        </div>
        <div v-if="![\'approved\',\'rejected\'].includes(docsModal.status)" class="flex gap-3">
          <button @click="approveClaim(docsModal.id); docsModal=null" class="flex-1 bg-green-600 text-white py-2.5 rounded-xl font-semibold hover:bg-green-700">✓ 승인</button>
          <button @click="rejectClaim(docsModal.id); docsModal=null" class="flex-1 bg-red-600 text-white py-2.5 rounded-xl font-semibold hover:bg-red-700">✕ 거절</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from \'vue\'
import axios from \'axios\'

const activeTab = ref(\'list\')
const businesses = ref([])
const claims = ref([])
const adminReviews = ref([])
const bizLoading = ref(false)
const claimsLoading = ref(false)
const reviewsLoading = ref(false)
const bizSearch = ref(\'\')
const bizStatus = ref(\'\')
const bizPage = ref(1)
const bizTotal = ref(0)
const claimFilter = ref(\'all\')
const reviewFilter = ref(\'all\')
const crawlCity = ref(\'all\')
const crawlCat = ref(\'all\')
const crawling = ref(false)
const crawlLog = ref(\'\')
const docsModal = ref(null)
const statCards = ref({ total:0, claimed:0, premium:0, pending:0 })

const tabs = [
  { id:\'list\', icon:\'📋\', label:\'업소목록\' },
  { id:\'claims\', icon:\'🔐\', label:\'소유권 신청\' },
  { id:\'reviews\', icon:\'⭐\', label:\'리뷰관리\' },
  { id:\'crawl\', icon:\'🕷️\', label:\'크롤링\' },
]

const claimStatuses = [
  { id:\'all\', label:\'전체\' },
  { id:\'pending\', label:\'접수\' },
  { id:\'email_verified\', label:\'이메일 인증\' },
  { id:\'docs_submitted\', label:\'서류 제출\' },
  { id:\'approved\', label:\'승인됨\' },
  { id:\'rejected\', label:\'거절됨\' },
]

const crawlCities = [\'Los Angeles\',\'New York\',\'Chicago\',\'Houston\',\'Seattle\',\'Atlanta\',\'Dallas\',\'San Francisco\',\'Washington DC\',\'Las Vegas\',\'Boston\',\'Philadelphia\',\'Miami\']
const crawlCats = [\'Korean Restaurant\',\'Korean Grocery\',\'Korean BBQ\',\'Spa & Nail\',\'Hair Salon\',\'Real Estate\',\'Legal Services\',\'Medical Clinic\',\'Insurance\',\'Travel Agency\']

function claimStatusStyle(s) {
  return { pending:\'bg-gray-100 text-gray-600\', email_sent:\'bg-blue-100 text-blue-600\', email_verified:\'bg-cyan-100 text-cyan-700\', docs_submitted:\'bg-yellow-100 text-yellow-700\', approved:\'bg-green-100 text-green-700\', rejected:\'bg-red-100 text-red-600\' }[s] || \'bg-gray-100 text-gray-500\'
}
function claimStatusLabel(s) {
  return { pending:\'접수\', email_sent:\'이메일 발송\', email_verified:\'이메일 인증\', docs_submitted:\'서류 제출\', approved:\'승인됨\', rejected:\'거절됨\' }[s] || s
}
function fmtDate(d) { return d ? new Date(d).toLocaleDateString(\'ko-KR\') : \'\' }

async function loadBusinesses() {
  bizLoading.value = true
  try {
    const r = await axios.get(\'/api/admin/businesses-list\', { params:{ search:bizSearch.value, status:bizStatus.value || undefined, page:bizPage.value } })
    businesses.value = r.data.data || r.data
    bizTotal.value = r.data.total || businesses.value.length
    statCards.value.total = bizTotal.value
  } catch(e) { console.error(e) }
  finally { bizLoading.value = false }
}

async function loadClaims() {
  claimsLoading.value = true
  try {
    const p = claimFilter.value !== \'all\' ? { status: claimFilter.value } : {}
    const r = await axios.get(\'/api/admin/business-claims-list\', { params:p })
    claims.value = r.data.data || r.data
    statCards.value.pending = claims.value.filter(c => [\'docs_submitted\',\'email_verified\'].includes(c.status)).length
  } catch(e) {}
  finally { claimsLoading.value = false }
}

async function loadReviews() {
  reviewsLoading.value = true
  try {
    const p = reviewFilter.value !== \'all\' ? { filter: reviewFilter.value } : {}
    const r = await axios.get(\'/api/admin/business-reviews-list\', { params:p })
    adminReviews.value = r.data.data || r.data
  } catch(e) {}
  finally { reviewsLoading.value = false }
}

async function loadStats() {
  try {
    const r = await axios.get(\'/api/admin/businesses-list\', { params:{ per_page:1 } })
    statCards.value.total = r.data.total || 0
    if (r.data.stats) {
      statCards.value.claimed = r.data.stats.claimed || 0
      statCards.value.premium = r.data.stats.premium || 0
    }
  } catch(e) {}
}

async function togglePremium(biz) {
  try {
    await axios.put(\`/api/admin/businesses-list/${biz.id}\`, { is_premium: !biz.is_premium })
    biz.is_premium = !biz.is_premium
  } catch(e) {}
}

async function deleteBiz(biz) {
  if (!confirm(\`"${biz.name}" 을 삭제하시겠습니까?\`)) return
  try {
    await axios.delete(\`/api/admin/businesses-list/${biz.id}\`)
    businesses.value = businesses.value.filter(b => b.id !== biz.id)
    bizTotal.value--
  } catch(e) {}
}

async function approveClaim(id) {
  try { await axios.post(\`/api/admin/business-claims-list/${id}/approve\`); loadClaims() } catch(e) {}
}

async function rejectClaim(id) {
  const note = prompt(\'거절 사유 (선택사항):\') || \'\'
  try { await axios.post(\`/api/admin/business-claims-list/${id}/reject\`, { note }); loadClaims() } catch(e) {}
}

async function hideReview(rv) {
  try { await axios.post(\`/api/admin/business-reviews-list/${rv.id}/hide\`); rv.is_visible = false } catch(e) {}
}
async function restoreReview(rv) {
  try { await axios.post(\`/api/admin/business-reviews-list/${rv.id}/restore\`); rv.is_visible = true } catch(e) {}
}
async function deleteReview(rv) {
  if (!confirm(\'이 리뷰를 삭제하시겠습니까?\')) return
  try { await axios.delete(\`/api/admin/business-reviews-list/${rv.id}\`); adminReviews.value = adminReviews.value.filter(r => r.id !== rv.id) } catch(e) {}
}

async function startCrawl() {
  crawling.value = true
  crawlLog.value = \'크롤링 요청 전송 중...\\n\'
  try {
    const r = await axios.post(\'/api/admin/businesses/import\', { city: crawlCity.value, category: crawlCat.value, trigger: \'manual\' })
    crawlLog.value += r.data.message || \'크롤링이 시작되었습니다.\'
  } catch(e) {
    crawlLog.value += \'요청 실패: \' + (e.response?.data?.message || e.message)
  } finally { crawling.value = false }
}

function refreshAll() { loadBusinesses(); loadClaims(); loadReviews(); loadStats() }

onMounted(() => refreshAll())
</script>
'''

print("Writing admin Business.vue...")
write_file('/var/www/somekorean/resources/js/pages/admin/Business.vue', admin_business_vue)

# Check admin navigation
print("\nChecking admin layout/sidebar for business link...")
result = ssh("grep -r 'business\\|업소' /var/www/somekorean/resources/js/layouts/ 2>/dev/null | grep -i 'link\\|route\\|to=' | head -5")
print(result)

result2 = ssh("grep -rn 'Business\\|업소' /var/www/somekorean/resources/js/pages/admin/AdminLayout.vue 2>/dev/null | head -10")
print(result2)

result3 = ssh("ls /var/www/somekorean/resources/js/layouts/ 2>/dev/null")
print("Layouts:", result3)

result4 = ssh("ls /var/www/somekorean/resources/js/pages/admin/ 2>/dev/null")
print("Admin pages:", result4)

print("\n=== TEAM 7 ADMIN ETA COMPLETE ===")
c.close()
