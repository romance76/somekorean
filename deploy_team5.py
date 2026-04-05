import paramiko, base64

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=60):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace').strip()

def write_file(path, content):
    chunk_size = 3000
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [encoded[i:i+chunk_size] for i in range(0, len(encoded), chunk_size)]
    ssh(f'> {path}')
    ssh(f'> /tmp/_chunk.b64')
    for chunk in chunks:
        ssh(f"echo -n '{chunk}' >> /tmp/_chunk.b64")
    ssh(f"base64 -d /tmp/_chunk.b64 > {path} && rm /tmp/_chunk.b64")
    return f"Written: {path}"

# FILE 1: ClaimBusiness.vue
claim_business = r"""<template>
  <div class="min-h-screen bg-gray-50 py-10">
    <div class="max-w-2xl mx-auto px-4">
      <!-- Step indicator -->
      <div class="flex items-center justify-center mb-8 gap-2">
        <div v-for="s in 4" :key="s" class="flex items-center">
          <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
            step >= s ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500']">{{s}}</div>
          <div v-if="s < 4" :class="['w-12 h-1', step > s ? 'bg-blue-600' : 'bg-gray-200']"></div>
        </div>
      </div>

      <!-- Step 1: Login check / Business info -->
      <div v-if="step === 1" class="bg-white rounded-2xl shadow p-8">
        <h2 class="text-2xl font-bold mb-2">업소 소유권 신청</h2>
        <p class="text-gray-500 mb-6">내 업소를 등록하고 직접 관리하세요</p>
        <div v-if="!isLoggedIn" class="text-center py-8">
          <div class="text-5xl mb-4">🔐</div>
          <p class="text-gray-600 mb-4">소유권 신청을 위해 로그인이 필요합니다</p>
          <router-link to="/login" class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700">로그인하기</router-link>
        </div>
        <div v-else>
          <div class="border rounded-xl p-4 mb-6 bg-gray-50">
            <h3 class="font-bold text-lg">{{ business.name }}</h3>
            <p class="text-gray-500 text-sm">{{ business.address }}</p>
            <p class="text-gray-500 text-sm">{{ business.phone }}</p>
            <span v-if="business.is_claimed" class="inline-block mt-2 bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">✓ 이미 등록된 업소</span>
          </div>
          <div v-if="business.is_claimed" class="text-center text-gray-500 py-4">이미 소유자가 등록된 업소입니다.</div>
          <button v-else @click="step=2" class="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700">이 업소 소유권 신청하기 →</button>
        </div>
      </div>

      <!-- Step 2: Verification method -->
      <div v-if="step === 2" class="bg-white rounded-2xl shadow p-8">
        <h2 class="text-2xl font-bold mb-2">본인 인증</h2>
        <p class="text-gray-500 mb-6">업소 소유자임을 확인합니다</p>
        <div class="space-y-4">
          <button @click="chooseMethod('email')" :class="['w-full border-2 rounded-xl p-4 text-left transition',
            method==='email' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300']">
            <div class="font-semibold">📧 이메일 인증</div>
            <div class="text-sm text-gray-500">업소 관련 이메일로 인증 링크 발송</div>
          </button>
          <button @click="chooseMethod('document')" :class="['w-full border-2 rounded-xl p-4 text-left transition',
            method==='document' ? 'border-blue-600 bg-blue-50' : 'border-gray-200 hover:border-blue-300']">
            <div class="font-semibold">📄 서류 인증</div>
            <div class="text-sm text-gray-500">사업자 등록증, 영업 허가증 등 업로드</div>
          </button>
        </div>
        <div v-if="method === 'email'" class="mt-4">
          <input v-model="verifyEmail" type="email" placeholder="업소 이메일 주소" class="w-full border rounded-xl px-4 py-3 mb-3"/>
          <button @click="sendEmailVerif" :disabled="sending" class="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50">
            {{ sending ? '발송 중...' : '인증 이메일 발송' }}
          </button>
        </div>
        <div v-if="method === 'document'" class="mt-4">
          <div class="border-2 border-dashed rounded-xl p-6 text-center cursor-pointer" @click="$refs.docInput.click()">
            <div class="text-3xl mb-2">📁</div>
            <p class="text-gray-500 text-sm">클릭하여 파일 선택 (PDF, JPG, PNG)</p>
            <p v-if="docs.length" class="text-blue-600 font-semibold mt-2">{{ docs.length }}개 파일 선택됨</p>
          </div>
          <input ref="docInput" type="file" multiple accept=".pdf,.jpg,.jpeg,.png" class="hidden" @change="onDocChange"/>
          <button v-if="docs.length" @click="uploadDocs" :disabled="uploading" class="mt-3 w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50">
            {{ uploading ? '업로드 중...' : '서류 제출' }}
          </button>
        </div>
        <button @click="step=1" class="mt-4 text-gray-400 text-sm hover:text-gray-600">← 이전으로</button>
      </div>

      <!-- Step 3: Waiting -->
      <div v-if="step === 3" class="bg-white rounded-2xl shadow p-8 text-center">
        <div class="text-6xl mb-4">⏳</div>
        <h2 class="text-2xl font-bold mb-2">검토 중</h2>
        <p class="text-gray-500 mb-6">신청이 접수되었습니다. 1-3 영업일 내 검토 후 이메일로 결과를 안내드립니다.</p>
        <div class="bg-gray-50 rounded-xl p-4 text-left text-sm space-y-2">
          <div>📋 신청 업소: <span class="font-semibold">{{ business.name }}</span></div>
          <div>📧 인증 방법: <span class="font-semibold">{{ method === 'email' ? '이메일 인증' : '서류 제출' }}</span></div>
          <div>📅 신청일: <span class="font-semibold">{{ today }}</span></div>
        </div>
        <router-link to="/" class="mt-6 inline-block bg-gray-100 text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-200">홈으로 돌아가기</router-link>
      </div>

      <!-- Step 4: Approved -->
      <div v-if="step === 4" class="bg-white rounded-2xl shadow p-8 text-center">
        <div class="text-6xl mb-4">🎉</div>
        <h2 class="text-2xl font-bold mb-2">소유권 승인 완료!</h2>
        <p class="text-gray-500 mb-6">이제 내 업소를 직접 관리할 수 있습니다</p>
        <router-link to="/my-business" class="bg-blue-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-blue-700">내 업소 관리하기 →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const step = ref(1)
const business = ref({})
const method = ref('')
const verifyEmail = ref('')
const docs = ref([])
const sending = ref(false)
const uploading = ref(false)
const claimId = ref(null)
const today = new Date().toLocaleDateString('ko-KR')

const isLoggedIn = computed(() => !!localStorage.getItem('sk_token'))

onMounted(async () => {
  const id = route.params.id || route.query.id
  if (id) {
    try {
      const r = await axios.get(`/api/businesses/${id}`)
      business.value = r.data.data || r.data
    } catch(e) {}
  }
})

async function chooseMethod(m) {
  method.value = m
  if (!claimId.value) {
    try {
      const r = await axios.post(`/api/businesses/${business.value.id}/claim`)
      claimId.value = r.data.claim_id || r.data.id
    } catch(e) { console.error(e) }
  }
}

async function sendEmailVerif() {
  if (!verifyEmail.value) return
  sending.value = true
  try {
    await axios.post(`/api/claims/${claimId.value}/email`, { email: verifyEmail.value })
    step.value = 3
  } catch(e) {
    alert('이메일 발송 실패. 다시 시도해주세요.')
  } finally { sending.value = false }
}

function onDocChange(e) { docs.value = Array.from(e.target.files) }

async function uploadDocs() {
  if (!docs.value.length) return
  uploading.value = true
  const fd = new FormData()
  docs.value.forEach(f => fd.append('documents[]', f))
  try {
    await axios.post(`/api/claims/${claimId.value}/documents`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    step.value = 3
  } catch(e) {
    alert('서류 업로드 실패. 다시 시도해주세요.')
  } finally { uploading.value = false }
}
</script>
"""

print(write_file('/var/www/somekorean/resources/js/pages/ClaimBusiness.vue', claim_business))

# FILE 2: OwnerDashboard.vue
owner_dashboard = r"""<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white border-b px-4 py-4">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <h1 class="text-xl font-bold">🏪 내 업소 관리</h1>
        <div class="flex gap-2">
          <span v-if="business.is_premium" class="bg-yellow-100 text-yellow-700 text-xs px-2 py-1 rounded-full font-semibold">⭐ 프리미엄</span>
          <span v-else class="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">기본 플랜</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
    </div>

    <div v-else-if="!business.id" class="max-w-2xl mx-auto px-4 py-20 text-center">
      <div class="text-5xl mb-4">🏪</div>
      <h2 class="text-2xl font-bold mb-2">등록된 업소가 없습니다</h2>
      <p class="text-gray-500 mb-6">소유권 신청을 통해 내 업소를 등록하세요</p>
      <router-link to="/businesses" class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700">업소 찾기</router-link>
    </div>

    <div v-else class="max-w-6xl mx-auto px-4 py-6">
      <!-- Business header card -->
      <div class="bg-white rounded-2xl shadow p-6 mb-6 flex items-start gap-4">
        <div class="w-16 h-16 rounded-xl bg-gray-100 flex items-center justify-center text-3xl flex-shrink-0">🏪</div>
        <div class="flex-1">
          <h2 class="text-xl font-bold">{{ business.name }}</h2>
          <p class="text-gray-500 text-sm">{{ business.address }}</p>
          <p class="text-blue-600 text-sm">{{ business.phone }}</p>
        </div>
        <router-link :to="`/businesses/${business.id}`" class="text-blue-600 text-sm hover:underline">업소 보기 →</router-link>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6 overflow-x-auto">
        <button v-for="t in tabs" :key="t.id" @click="activeTab=t.id"
          :class="['px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition',
            activeTab===t.id ? 'bg-white shadow text-blue-600' : 'text-gray-600 hover:text-gray-800']">
          {{ t.icon }} {{ t.label }}
        </button>
      </div>

      <!-- Tab: 기본정보 -->
      <div v-if="activeTab==='info'" class="bg-white rounded-2xl shadow p-6">
        <h3 class="font-bold text-lg mb-4">기본 정보 수정</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">업소명 (한국어)</label>
            <input v-model="form.name_ko" class="w-full border rounded-xl px-4 py-2.5" placeholder="한국어 업소명"/>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">업소명 (영어)</label>
            <input v-model="form.name_en" class="w-full border rounded-xl px-4 py-2.5" placeholder="English name"/>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">전화번호</label>
            <input v-model="form.phone" class="w-full border rounded-xl px-4 py-2.5" placeholder="(000) 000-0000"/>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">웹사이트</label>
            <input v-model="form.website" class="w-full border rounded-xl px-4 py-2.5" placeholder="https://"/>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-gray-600 mb-1">소개 (한국어)</label>
            <textarea v-model="form.owner_description_ko" rows="3" class="w-full border rounded-xl px-4 py-2.5" placeholder="업소 소개를 입력하세요"></textarea>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-gray-600 mb-1">임시 휴업</label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.temp_closed" class="w-4 h-4"/>
              <span class="text-sm text-gray-700">현재 임시 휴업 중</span>
            </label>
          </div>
        </div>
        <button @click="saveInfo" :disabled="saving" class="mt-4 bg-blue-600 text-white px-6 py-2.5 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50">
          {{ saving ? '저장 중...' : '저장하기' }}
        </button>
        <span v-if="saved" class="ml-3 text-green-600 text-sm">✓ 저장되었습니다</span>
      </div>

      <!-- Tab: 사진 -->
      <div v-if="activeTab==='photos'" class="bg-white rounded-2xl shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-lg">사진 관리</h3>
          <span class="text-sm text-gray-500">{{ photos.length }}/{{ business.is_premium ? 20 : 5 }}장</span>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div v-for="(ph, i) in photos" :key="i" class="relative group">
            <img :src="ph" class="w-full h-28 object-cover rounded-xl"/>
            <button @click="deletePhoto(i)" class="absolute top-1 right-1 bg-red-500 text-white w-6 h-6 rounded-full text-xs opacity-0 group-hover:opacity-100 transition">✕</button>
          </div>
          <div v-if="photos.length < (business.is_premium ? 20 : 5)"
            class="border-2 border-dashed rounded-xl h-28 flex items-center justify-center cursor-pointer text-gray-400 hover:border-blue-400 hover:text-blue-400 transition"
            @click="$refs.photoInput.click()">
            <div class="text-center"><div class="text-2xl">+</div><div class="text-xs">추가</div></div>
          </div>
        </div>
        <input ref="photoInput" type="file" multiple accept="image/*" class="hidden" @change="uploadPhotos"/>
        <div v-if="!business.is_premium" class="bg-yellow-50 rounded-xl p-4 text-sm">
          💡 프리미엄 업그레이드 시 최대 20장의 사진을 등록할 수 있습니다.
          <router-link to="/premium" class="text-blue-600 ml-1 hover:underline">업그레이드 →</router-link>
        </div>
      </div>

      <!-- Tab: 리뷰 -->
      <div v-if="activeTab==='reviews'" class="bg-white rounded-2xl shadow p-6">
        <h3 class="font-bold text-lg mb-4">리뷰 관리</h3>
        <div v-if="reviews.length === 0" class="text-center py-8 text-gray-400">아직 리뷰가 없습니다</div>
        <div v-for="rv in reviews" :key="rv.id" class="border-b last:border-b-0 py-4">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="font-semibold text-sm">{{ rv.user?.name || '익명' }}</span>
                <div class="flex">
                  <span v-for="s in 5" :key="s" :class="s <= rv.rating ? 'text-yellow-400' : 'text-gray-200'" class="text-xs">★</span>
                </div>
              </div>
              <p class="text-gray-700 text-sm">{{ rv.content }}</p>
              <p v-if="rv.owner_reply" class="mt-2 bg-blue-50 rounded-lg p-2 text-sm text-blue-800">
                <span class="font-semibold">사장님 답변: </span>{{ rv.owner_reply }}
              </p>
            </div>
          </div>
          <div v-if="!rv.owner_reply" class="mt-3">
            <div class="flex gap-2">
              <input v-model="rv._reply" placeholder="답변을 입력하세요..." class="flex-1 border rounded-lg px-3 py-1.5 text-sm"/>
              <button @click="replyReview(rv)" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-blue-700">답변</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: 이벤트 -->
      <div v-if="activeTab==='events'" class="bg-white rounded-2xl shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-lg">이벤트 관리</h3>
          <button v-if="business.is_premium" @click="showEventForm=!showEventForm" class="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-blue-700">+ 이벤트 추가</button>
        </div>
        <div v-if="!business.is_premium" class="bg-yellow-50 rounded-xl p-4 text-sm mb-4">
          ⭐ 이벤트 기능은 프리미엄 플랜에서 이용 가능합니다.
          <router-link to="/premium" class="text-blue-600 ml-1 hover:underline">업그레이드 →</router-link>
        </div>
        <div v-if="showEventForm && business.is_premium" class="border rounded-xl p-4 mb-4 bg-gray-50">
          <div class="grid grid-cols-2 gap-3 mb-3">
            <input v-model="eventForm.title" placeholder="이벤트 제목" class="col-span-2 border rounded-lg px-3 py-2 text-sm"/>
            <input v-model="eventForm.event_date" type="date" class="border rounded-lg px-3 py-2 text-sm"/>
            <input v-model="eventForm.event_time" type="time" class="border rounded-lg px-3 py-2 text-sm"/>
            <textarea v-model="eventForm.description" placeholder="이벤트 설명" rows="2" class="col-span-2 border rounded-lg px-3 py-2 text-sm"></textarea>
          </div>
          <button @click="createEvent" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700">이벤트 등록</button>
        </div>
        <div v-for="ev in events" :key="ev.id" class="flex items-center justify-between border-b last:border-b-0 py-3">
          <div>
            <p class="font-semibold text-sm">{{ ev.title }}</p>
            <p class="text-gray-500 text-xs">{{ ev.event_date }} {{ ev.event_time }}</p>
          </div>
          <button @click="deleteEvent(ev.id)" class="text-red-500 hover:text-red-700 text-sm">삭제</button>
        </div>
        <div v-if="events.length === 0 && business.is_premium" class="text-center py-8 text-gray-400">등록된 이벤트가 없습니다</div>
      </div>

      <!-- Tab: 통계 -->
      <div v-if="activeTab==='stats'" class="bg-white rounded-2xl shadow p-6">
        <h3 class="font-bold text-lg mb-4">통계</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div v-for="s in statCards" :key="s.label" class="bg-gray-50 rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-blue-600">{{ s.value }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ s.label }}</div>
          </div>
        </div>
        <div v-if="!business.is_premium" class="bg-yellow-50 rounded-xl p-4 text-sm">
          ⭐ 상세 통계는 프리미엄 플랜에서 이용 가능합니다.
          <router-link to="/premium" class="text-blue-600 ml-1 hover:underline">업그레이드 →</router-link>
        </div>
      </div>

      <!-- Tab: 프리미엄 -->
      <div v-if="activeTab==='premium'" class="bg-white rounded-2xl shadow p-6">
        <h3 class="font-bold text-lg mb-6">프리미엄 플랜</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="plan in plans" :key="plan.id"
            :class="['border-2 rounded-2xl p-6', plan.recommended ? 'border-blue-600' : 'border-gray-200']">
            <div v-if="plan.recommended" class="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full inline-block mb-2">추천</div>
            <h4 class="font-bold text-lg">{{ plan.name }}</h4>
            <div class="text-2xl font-bold text-blue-600 my-2">${{ plan.price }}<span class="text-sm text-gray-500">/월</span></div>
            <ul class="space-y-2 text-sm text-gray-600 mb-4">
              <li v-for="f in plan.features" :key="f">✓ {{ f }}</li>
            </ul>
            <button class="w-full bg-blue-600 text-white py-2 rounded-xl font-semibold hover:bg-blue-700" @click="alert('준비 중입니다')">선택하기</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const loading = ref(true)
const business = ref({})
const form = ref({})
const photos = ref([])
const reviews = ref([])
const events = ref([])
const stats = ref({})
const activeTab = ref('info')
const saving = ref(false)
const saved = ref(false)
const showEventForm = ref(false)
const eventForm = ref({ title: '', event_date: '', event_time: '', description: '' })

const tabs = [
  { id: 'info', icon: '📝', label: '기본정보' },
  { id: 'photos', icon: '📷', label: '사진' },
  { id: 'reviews', icon: '⭐', label: '리뷰' },
  { id: 'events', icon: '🎉', label: '이벤트' },
  { id: 'stats', icon: '📊', label: '통계' },
  { id: 'premium', icon: '👑', label: '프리미엄' },
]

const plans = [
  { id: 'basic', name: 'Basic', price: 29, features: ['사진 10장', '소개글 작성', '영업시간 관리', '기본 통계'] },
  { id: 'standard', name: 'Standard', price: 59, recommended: true, features: ['사진 20장', '이벤트 등록', '상세 통계', '리뷰 답변', '검색 상단 노출'] },
  { id: 'premium', name: 'Premium', price: 99, features: ['모든 Standard 기능', '광고 배너', '메뉴 관리', '우선 지원', '맞춤 마케팅'] },
]

const statCards = computed(() => [
  { label: '이번달 조회수', value: stats.value.views || 0 },
  { label: '전화 클릭', value: stats.value.phone_clicks || 0 },
  { label: '길찾기 클릭', value: stats.value.direction_clicks || 0 },
  { label: '웹사이트 클릭', value: stats.value.website_clicks || 0 },
])

onMounted(async () => {
  try {
    const r = await axios.get('/api/owner/business')
    business.value = r.data.business || r.data
    form.value = { ...business.value }
    photos.value = business.value.owner_photos || []
    const [rv, ev, st] = await Promise.all([
      axios.get('/api/owner/reviews').catch(() => ({ data: { data: [] } })),
      axios.get('/api/owner/events').catch(() => ({ data: { data: [] } })),
      axios.get('/api/owner/stats').catch(() => ({ data: {} })),
    ])
    reviews.value = rv.data.data || []
    events.value = ev.data.data || []
    stats.value = st.data || {}
  } catch(e) {
    console.error(e)
  } finally { loading.value = false }
})

async function saveInfo() {
  saving.value = true
  try {
    await axios.put('/api/owner/business', form.value)
    saved.value = true
    setTimeout(() => saved.value = false, 3000)
  } catch(e) { alert('저장 실패') }
  finally { saving.value = false }
}

async function uploadPhotos(e) {
  const files = Array.from(e.target.files)
  const fd = new FormData()
  files.forEach(f => fd.append('photos[]', f))
  try {
    const r = await axios.post('/api/owner/business/photos', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    photos.value = r.data.photos || photos.value
  } catch(e) { alert('업로드 실패') }
}

async function deletePhoto(i) {
  try {
    await axios.delete(`/api/owner/business/photos/${i}`)
    photos.value.splice(i, 1)
  } catch(e) {}
}

async function replyReview(rv) {
  if (!rv._reply) return
  try {
    await axios.post(`/api/owner/reviews/${rv.id}/reply`, { reply: rv._reply })
    rv.owner_reply = rv._reply
  } catch(e) {}
}

async function createEvent() {
  try {
    const r = await axios.post('/api/owner/events', eventForm.value)
    events.value.unshift(r.data)
    eventForm.value = { title: '', event_date: '', event_time: '', description: '' }
    showEventForm.value = false
  } catch(e) { alert('이벤트 등록 실패') }
}

async function deleteEvent(id) {
  if (!confirm('삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/owner/events/${id}`)
    events.value = events.value.filter(e => e.id !== id)
  } catch(e) {}
}
</script>
"""

print(write_file('/var/www/somekorean/resources/js/pages/OwnerDashboard.vue', owner_dashboard))

# FILE 3: PremiumUpgrade.vue
premium_upgrade = r"""<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 py-16 px-4">
    <div class="max-w-5xl mx-auto text-center mb-12">
      <div class="text-5xl mb-4">👑</div>
      <h1 class="text-4xl font-bold mb-3">프리미엄 업그레이드</h1>
      <p class="text-gray-500 text-lg">내 업소를 더 많은 한인들에게 알리세요</p>
    </div>
    <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="plan in plans" :key="plan.id"
        :class="['bg-white rounded-3xl shadow-lg p-8 relative transition hover:shadow-xl',
          plan.recommended ? 'ring-2 ring-blue-600 scale-105' : '']">
        <div v-if="plan.recommended" class="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-600 text-white text-sm px-4 py-1 rounded-full font-semibold">가장 인기</div>
        <div class="text-4xl mb-3">{{ plan.icon }}</div>
        <h3 class="text-xl font-bold mb-1">{{ plan.name }}</h3>
        <div class="text-3xl font-bold text-blue-600 mb-1">${{ plan.price }}<span class="text-base text-gray-400 font-normal">/월</span></div>
        <p class="text-gray-400 text-sm mb-6">약 ₩{{ Math.round(plan.price * 1350).toLocaleString() }}/월</p>
        <ul class="space-y-3 mb-8">
          <li v-for="f in plan.features" :key="f" class="flex items-start gap-2 text-sm">
            <span class="text-green-500 font-bold mt-0.5">✓</span>
            <span>{{ f }}</span>
          </li>
        </ul>
        <button @click="selectPlan(plan)" :class="['w-full py-3 rounded-xl font-bold transition',
          plan.recommended ? 'bg-blue-600 text-white hover:bg-blue-700' : 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50']">
          {{ plan.id === currentPlan ? '현재 플랜' : '선택하기' }}
        </button>
      </div>
    </div>
    <div class="max-w-2xl mx-auto mt-12 bg-white rounded-2xl shadow p-8">
      <h3 class="font-bold text-lg mb-4">자주 묻는 질문</h3>
      <div v-for="faq in faqs" :key="faq.q" class="mb-4">
        <button @click="faq.open = !faq.open" class="w-full text-left font-semibold text-gray-800 flex justify-between">
          {{ faq.q }} <span>{{ faq.open ? '▲' : '▼' }}</span>
        </button>
        <p v-if="faq.open" class="text-gray-500 text-sm mt-2">{{ faq.a }}</p>
      </div>
    </div>
    <!-- Modal -->
    <div v-if="selectedPlan" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl p-8 max-w-md w-full">
        <h3 class="text-xl font-bold mb-2">{{ selectedPlan.name }} 플랜 신청</h3>
        <p class="text-gray-500 text-sm mb-4">카드 결제 연동은 준비 중입니다. 하단 계좌로 선결제 후 이메일로 문의해주세요.</p>
        <div class="bg-gray-50 rounded-xl p-4 text-sm mb-4">
          <p>💳 <strong>결제 금액:</strong> ${{ selectedPlan.price }}/월</p>
          <p class="mt-1">📧 <strong>문의:</strong> admin@somekorean.com</p>
        </div>
        <button @click="selectedPlan=null" class="w-full border-2 border-gray-200 py-2.5 rounded-xl font-semibold hover:bg-gray-50">닫기</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const currentPlan = ref('free')
const selectedPlan = ref(null)

const plans = [
  {
    id: 'basic', name: 'Basic', price: 29, icon: '🌟',
    features: ['사진 10장 등록', '소개글 작성', '영업시간 상세 관리', '기본 통계 (조회수)', '리뷰 답변']
  },
  {
    id: 'standard', name: 'Standard', price: 59, icon: '⭐', recommended: true,
    features: ['사진 20장 등록', '이벤트 등록 (월 4개)', '상세 통계 (클릭/방문)', '검색 결과 상단 노출', '메뉴/서비스 목록', '우선 고객 지원']
  },
  {
    id: 'premium', name: 'Premium', price: 99, icon: '👑',
    features: ['모든 Standard 기능', '무제한 이벤트 등록', '광고 배너 노출', '홈 추천 업소 등재', '맞춤형 마케팅 지원', '전담 매니저 배정']
  }
]

const faqs = ref([
  { q: '언제부터 프리미엄 혜택을 받을 수 있나요?', a: '결제 확인 후 24시간 이내 활성화됩니다.', open: false },
  { q: '해지하면 어떻게 되나요?', a: '해지 시 다음 결제일부터 기본 플랜으로 전환됩니다. 이미 결제된 금액은 환불되지 않습니다.', open: false },
  { q: '업소가 여러 개인 경우 어떻게 하나요?', a: '업소당 별도 구독이 필요합니다.', open: false },
])

function selectPlan(plan) {
  selectedPlan.value = plan
}
</script>
"""

print(write_file('/var/www/somekorean/resources/js/pages/PremiumUpgrade.vue', premium_upgrade))

# FILE 4: EmailVerifyBusiness.vue
email_verify = r"""<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="bg-white rounded-2xl shadow p-8 max-w-md w-full text-center">
      <div v-if="loading" class="py-8">
        <div class="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p class="text-gray-500">이메일 인증 처리 중...</p>
      </div>
      <div v-else-if="success">
        <div class="text-6xl mb-4">✅</div>
        <h2 class="text-2xl font-bold mb-2">이메일 인증 완료!</h2>
        <p class="text-gray-500 mb-6">소유권 신청이 접수되었습니다. 관리자 검토 후 1-3 영업일 내 안내드립니다.</p>
        <router-link to="/" class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700">홈으로</router-link>
      </div>
      <div v-else>
        <div class="text-6xl mb-4">❌</div>
        <h2 class="text-2xl font-bold mb-2">인증 실패</h2>
        <p class="text-gray-500 mb-6">{{ errorMsg }}</p>
        <router-link to="/businesses" class="bg-gray-100 text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-200">업소 목록으로</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const loading = ref(true)
const success = ref(false)
const errorMsg = ref('인증 링크가 유효하지 않거나 만료되었습니다.')

onMounted(async () => {
  const token = route.params.token
  if (!token) { loading.value = false; return }
  try {
    await axios.get(`/api/claims/email/verify/${token}`)
    success.value = true
  } catch(e) {
    errorMsg.value = e.response?.data?.message || '인증 처리 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
})
</script>
"""

print(write_file('/var/www/somekorean/resources/js/pages/EmailVerifyBusiness.vue', email_verify))

# Verify all files exist
print("\n--- Verification ---")
for f in ['ClaimBusiness.vue', 'OwnerDashboard.vue', 'PremiumUpgrade.vue', 'EmailVerifyBusiness.vue']:
    result = ssh(f'wc -l /var/www/somekorean/resources/js/pages/{f}')
    print(f'{f}: {result}')

c.close()
print("\n=== TEAM 5 FRONTEND EPSILON COMPLETE ===")
