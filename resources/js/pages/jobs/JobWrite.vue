<template>
<div class="min-h-screen bg-gray-100">
  <div class="max-w-3xl mx-auto px-4 py-6 space-y-5">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="w-9 h-9 flex items-center justify-center rounded-full bg-white shadow-sm border border-gray-200 text-gray-500 hover:bg-gray-50">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-xl font-black text-gray-800">{{ isEdit ? '공고 수정' : '공고 등록' }}</h1>
    </div>

    <!-- Section 1: 글 유형 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100" :class="isHiring ? 'bg-amber-50' : 'bg-blue-50'">
        <h2 class="text-sm font-bold" :class="isHiring ? 'text-amber-800' : 'text-blue-800'">공고 유형</h2>
      </div>
      <div class="p-5">
        <div class="flex gap-3">
          <button type="button" @click="form.post_type='hiring'"
            class="flex-1 py-3 rounded-xl font-bold text-sm transition-all border-2 flex items-center justify-center gap-2"
            :class="isHiring ? 'bg-amber-400 border-amber-400 text-amber-900 shadow-md shadow-amber-200' : 'bg-white border-gray-200 text-gray-400 hover:border-amber-300'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            구인 (채용합니다)
          </button>
          <button type="button" @click="form.post_type='seeking'"
            class="flex-1 py-3 rounded-xl font-bold text-sm transition-all border-2 flex items-center justify-center gap-2"
            :class="!isHiring ? 'bg-blue-500 border-blue-500 text-white shadow-md shadow-blue-200' : 'bg-white border-gray-200 text-gray-400 hover:border-blue-300'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            구직 (일자리 찾습니다)
          </button>
        </div>
      </div>
    </section>

    <!-- Section 2: 기본 정보 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100" :class="isHiring ? 'bg-amber-50' : 'bg-blue-50'">
        <h2 class="text-sm font-bold" :class="isHiring ? 'text-amber-800' : 'text-blue-800'">기본 정보</h2>
      </div>
      <div class="p-5 space-y-4">
        <!-- 제목 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-1">
            제목 <span class="text-red-400">*</span>
          </label>
          <input v-model="form.title" type="text"
            :placeholder="isHiring ? '예: 한식당 주방보조 구합니다' : '예: 경력 3년 웹개발자 구직합니다'"
            class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm transition outline-none"
            :class="focusRing" />
        </div>

        <!-- 회사명/이름 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-1">
            {{ isHiring ? '회사명' : '이름 / 경력 (선택)' }}
            <span v-if="isHiring" class="text-red-400">*</span>
          </label>
          <input v-model="form.company" type="text"
            :placeholder="isHiring ? '예: OO 레스토랑' : '예: 홍길동 / 요식업 3년'"
            class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm transition outline-none"
            :class="focusRing" />
        </div>

        <!-- 카테고리 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-1">
            카테고리 <span class="text-red-400">*</span>
          </label>
          <select v-model="form.category"
            class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm transition outline-none appearance-none bg-white"
            :class="focusRing">
            <option value="" disabled>카테고리를 선택하세요</option>
            <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>

        <!-- 고용형태 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-2">고용형태</label>
          <div class="flex gap-2">
            <button v-for="t in typeOptions" :key="t.value" type="button"
              @click="form.type = t.value"
              class="flex-1 py-2.5 rounded-lg text-sm font-semibold transition border-2"
              :class="form.type === t.value
                ? (isHiring ? 'border-amber-400 bg-amber-50 text-amber-800' : 'border-blue-400 bg-blue-50 text-blue-800')
                : 'border-gray-200 bg-white text-gray-500 hover:border-gray-300'">
              {{ t.label }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 3: 급여 & 위치 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100" :class="isHiring ? 'bg-amber-50' : 'bg-blue-50'">
        <h2 class="text-sm font-bold" :class="isHiring ? 'text-amber-800' : 'text-blue-800'">급여 & 위치</h2>
      </div>
      <div class="p-5 space-y-4">
        <!-- 급여 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-2">급여</label>
          <!-- 급여 단위 버튼 -->
          <div class="flex gap-2 mb-3">
            <button v-for="s in salaryTypes" :key="s.value" type="button"
              @click="form.salary_type = s.value"
              class="px-4 py-2 rounded-lg text-xs font-semibold transition border-2"
              :class="form.salary_type === s.value
                ? (isHiring ? 'border-amber-400 bg-amber-50 text-amber-800' : 'border-blue-400 bg-blue-50 text-blue-800')
                : 'border-gray-200 bg-white text-gray-500 hover:border-gray-300'">
              {{ s.label }}
            </button>
          </div>
          <!-- 급여 범위 -->
          <div class="flex items-center gap-3">
            <div class="flex-1 relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
              <input v-model.number="form.salary_min" type="number" placeholder="최소"
                class="w-full border border-gray-300 rounded-lg pl-7 pr-3 py-2.5 text-sm transition outline-none"
                :class="focusRing" />
            </div>
            <span class="text-gray-400 font-bold">~</span>
            <div class="flex-1 relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">$</span>
              <input v-model.number="form.salary_max" type="number" placeholder="최대"
                class="w-full border border-gray-300 rounded-lg pl-7 pr-3 py-2.5 text-sm transition outline-none"
                :class="focusRing" />
            </div>
          </div>
        </div>

        <!-- 위치 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-2">근무 위치</label>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="text-xs text-gray-500 block mb-1">City</label>
              <input v-model="form.city" type="text" placeholder="예: Los Angeles"
                class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm transition outline-none"
                :class="focusRing" />
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-1">State</label>
              <input v-model="form.state" type="text" placeholder="예: CA"
                class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm transition outline-none"
                :class="focusRing" />
            </div>
            <div>
              <label class="text-xs text-gray-500 block mb-1">Zip Code</label>
              <input v-model="form.zipcode" type="text" placeholder="예: 90001"
                class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm transition outline-none"
                :class="focusRing" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 4: 복리후생 (Benefits) - only for hiring -->
    <section v-if="isHiring" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 bg-amber-50">
        <h2 class="text-sm font-bold text-amber-800">복리후생 (Benefits)</h2>
      </div>
      <div class="p-5 space-y-3">
        <p class="text-xs text-gray-500">해당하는 복리후생을 클릭하세요. 상세 설명에 자동으로 추가됩니다.</p>
        <div class="flex flex-wrap gap-2">
          <button v-for="b in benefitChips" :key="b"
            type="button" @click="toggleBenefit(b)"
            class="px-3 py-1.5 rounded-full text-xs font-medium transition border"
            :class="selectedBenefits.has(b)
              ? 'bg-amber-100 border-amber-400 text-amber-800'
              : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-amber-300 hover:bg-amber-50'">
            <span v-if="selectedBenefits.has(b)" class="mr-1">&#10003;</span>{{ b }}
          </button>
        </div>
        <!-- Custom benefit input -->
        <div class="flex gap-2 mt-2">
          <input v-model="customBenefit" type="text" placeholder="직접 입력 (예: Free meals)"
            @keyup.enter="addCustomBenefit"
            class="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-amber-400" />
          <button type="button" @click="addCustomBenefit"
            class="px-4 py-2 rounded-lg text-xs font-bold bg-amber-100 text-amber-700 hover:bg-amber-200 transition">
            + 추가
          </button>
        </div>
      </div>
    </section>

    <!-- Section 5: 상세 설명 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100" :class="isHiring ? 'bg-amber-50' : 'bg-blue-50'">
        <h2 class="text-sm font-bold" :class="isHiring ? 'text-amber-800' : 'text-blue-800'">상세 설명</h2>
      </div>
      <div class="p-5">
        <label class="text-xs text-gray-500 block mb-2">
          {{ isHiring ? '근무 조건, 자격 요건, 우대사항 등을 자세히 작성해주세요' : '본인 소개, 경력, 희망 근무조건 등을 작성해주세요' }}
        </label>
        <textarea v-model="form.content" rows="10"
          :placeholder="isHiring
            ? '예:\n- 근무시간: 월~금 9am~6pm\n- 자격요건: 영어 가능자\n- 우대사항: 한식 조리 경험자\n- 지원방법: 이메일 또는 전화'
            : '예:\n- 경력: 요식업 3년\n- 가능업무: 주방보조, 서빙, 카운터\n- 희망지역: LA 한인타운\n- 영어: 일상회화 가능'"
          class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm transition outline-none resize-none leading-relaxed"
          :class="focusRing"></textarea>
        <p class="text-xs text-gray-400 mt-1 text-right">{{ form.content.length }} 자</p>
      </div>
    </section>

    <!-- Section 6: 연락처 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100" :class="isHiring ? 'bg-amber-50' : 'bg-blue-50'">
        <h2 class="text-sm font-bold" :class="isHiring ? 'text-amber-800' : 'text-blue-800'">연락처</h2>
      </div>
      <div class="p-5">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="text-sm font-semibold text-gray-700 block mb-1">전화번호</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
              <input v-model="form.contact_phone" type="text" placeholder="213-000-0000"
                class="w-full border border-gray-300 rounded-lg pl-9 pr-3 py-2.5 text-sm transition outline-none"
                :class="focusRing" />
            </div>
          </div>
          <div>
            <label class="text-sm font-semibold text-gray-700 block mb-1">이메일</label>
            <div class="relative">
              <svg class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
              <input v-model="form.contact_email" type="email" placeholder="email@example.com"
                class="w-full border border-gray-300 rounded-lg pl-9 pr-3 py-2.5 text-sm transition outline-none"
                :class="focusRing" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 7: 만료일 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100" :class="isHiring ? 'bg-amber-50' : 'bg-blue-50'">
        <h2 class="text-sm font-bold" :class="isHiring ? 'text-amber-800' : 'text-blue-800'">만료일 (선택)</h2>
      </div>
      <div class="p-5">
        <label class="text-xs text-gray-500 block mb-2">설정하지 않으면 무기한 게시됩니다</label>
        <input v-model="form.expires_at" type="date"
          class="w-full sm:w-auto border border-gray-300 rounded-lg px-4 py-2.5 text-sm transition outline-none"
          :class="focusRing" />
      </div>
    </section>

    <!-- Error -->
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 rounded-xl px-5 py-3 text-sm font-medium">
      {{ error }}
    </div>

    <!-- Actions -->
    <div class="flex gap-3 pb-10">
      <button @click="submit" :disabled="submitting"
        class="flex-1 sm:flex-none font-bold px-8 py-3 rounded-xl shadow-md transition disabled:opacity-50 text-sm"
        :class="isHiring
          ? 'bg-amber-400 text-amber-900 hover:bg-amber-500 shadow-amber-200'
          : 'bg-blue-500 text-white hover:bg-blue-600 shadow-blue-200'">
        {{ submitting ? '저장 중...' : (isEdit ? '수정하기' : '등록하기') }}
      </button>
      <button @click="$router.back()"
        class="px-6 py-3 rounded-xl text-gray-500 bg-white border border-gray-200 hover:bg-gray-50 text-sm font-medium transition">
        취소
      </button>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const form = reactive({
  post_type: 'hiring',
  title: '',
  company: '',
  category: '',
  type: 'full',
  salary_min: null,
  salary_max: null,
  salary_type: 'hourly',
  city: '',
  state: '',
  zipcode: '',
  content: '',
  contact_phone: '',
  contact_email: '',
  expires_at: '',
})

const categories = [
  { value: 'restaurant', label: '요식업 (Restaurant)' },
  { value: 'it', label: 'IT / 기술 (Tech)' },
  { value: 'beauty', label: '미용 (Beauty)' },
  { value: 'driving', label: '운전 (Driving)' },
  { value: 'retail', label: '판매 (Retail)' },
  { value: 'office', label: '사무직 (Office)' },
  { value: 'construction', label: '건설 (Construction)' },
  { value: 'medical', label: '의료 (Medical)' },
  { value: 'education', label: '교육 (Education)' },
  { value: 'etc', label: '기타 (Other)' },
]

const typeOptions = [
  { value: 'full', label: '풀타임 (Full-time)' },
  { value: 'part', label: '파트타임 (Part-time)' },
  { value: 'contract', label: '계약직 (Contract)' },
]

const salaryTypes = [
  { value: 'hourly', label: '시급 (Hourly)' },
  { value: 'monthly', label: '월급 (Monthly)' },
  { value: 'yearly', label: '연봉 (Yearly)' },
]

const benefitChips = [
  'Health insurance',
  'Dental insurance',
  'Vision insurance',
  '401(k)',
  'Paid time off',
  'Paid sick leave',
  'On-the-job training',
  'Employee discount',
  'Flexible schedule',
  'Free meals',
  'Commuter assistance',
  'Tuition reimbursement',
  'Referral program',
  'Life insurance',
  'Retirement plan',
]

const selectedBenefits = reactive(new Set())
const customBenefit = ref('')
const error = ref('')
const submitting = ref(false)
const isEdit = ref(false)
const editId = ref(null)

const isHiring = computed(() => form.post_type === 'hiring')
const focusRing = computed(() =>
  isHiring.value ? 'focus:ring-2 focus:ring-amber-400 focus:border-amber-400' : 'focus:ring-2 focus:ring-blue-400 focus:border-blue-400'
)

function toggleBenefit(b) {
  if (selectedBenefits.has(b)) {
    selectedBenefits.delete(b)
  } else {
    selectedBenefits.add(b)
  }
}

function addCustomBenefit() {
  const val = customBenefit.value.trim()
  if (val && !selectedBenefits.has(val)) {
    selectedBenefits.add(val)
    customBenefit.value = ''
  }
}

function buildContentWithBenefits() {
  let content = form.content.trim()
  if (selectedBenefits.size > 0) {
    const benefitsList = Array.from(selectedBenefits).join(', ')
    // Remove any existing benefits block so we don't duplicate
    content = content.replace(/\n?\n?---BENEFITS---\n[\s\S]*?---END BENEFITS---/g, '').trim()
    content += `\n\n---BENEFITS---\n${benefitsList}\n---END BENEFITS---`
  }
  return content
}

function parseBenefitsFromContent(content) {
  if (!content) return
  const match = content.match(/---BENEFITS---\n([\s\S]*?)\n---END BENEFITS---/)
  if (match) {
    const benefits = match[1].split(',').map(b => b.trim()).filter(Boolean)
    benefits.forEach(b => selectedBenefits.add(b))
    // Remove the benefits block from content for display
    form.content = content.replace(/\n?\n?---BENEFITS---\n[\s\S]*?---END BENEFITS---/, '').trim()
  }
}

async function submit() {
  if (!form.title) { error.value = '제목을 입력해주세요'; return }
  if (!form.company && isHiring.value) { error.value = '회사명을 입력해주세요'; return }
  if (!form.category) { error.value = '카테고리를 선택해주세요'; return }
  if (!form.content.trim()) { error.value = '상세 설명을 입력해주세요'; return }

  submitting.value = true
  error.value = ''

  const payload = { ...form, content: buildContentWithBenefits() }
  // Clean empty values
  if (!payload.expires_at) delete payload.expires_at
  if (!payload.salary_min) delete payload.salary_min
  if (!payload.salary_max) delete payload.salary_max

  try {
    if (isEdit.value) {
      await axios.put(`/api/jobs/${editId.value}`, payload)
      router.push(`/jobs/${editId.value}`)
    } else {
      const { data } = await axios.post('/api/jobs', payload)
      router.push(`/jobs/${data.data.id}`)
    }
  } catch (e) {
    error.value = e.response?.data?.message || '등록에 실패했습니다. 다시 시도해주세요.'
  }
  submitting.value = false
}

onMounted(async () => {
  if (route.query.edit) {
    editId.value = route.query.edit
    isEdit.value = true
    try {
      const { data } = await axios.get(`/api/jobs/${editId.value}`)
      const j = data.data
      Object.keys(form).forEach(k => {
        if (j[k] !== undefined && j[k] !== null) form[k] = j[k]
      })
      // Parse benefits from content
      parseBenefitsFromContent(form.content)
    } catch {}
  }
})
</script>
