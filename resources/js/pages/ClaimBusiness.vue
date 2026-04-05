<template>
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
          <router-link to="/auth/login" class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700">로그인하기</router-link>
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
        <router-link to="/dashboard" class="bg-blue-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-blue-700">내 업소 관리하기 →</router-link>
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
