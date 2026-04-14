<template>
<div class="min-h-screen bg-gray-100">
  <div class="max-w-3xl mx-auto px-4 py-6 space-y-5">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="w-9 h-9 flex items-center justify-center rounded-full bg-white shadow-sm border border-gray-200 text-gray-500 hover:bg-gray-50">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-xl font-black text-gray-800">{{ isEdit ? '동호회 수정' : '동호회 만들기' }}</h1>
    </div>

    <!-- Section 1: 기본 정보 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 bg-amber-50">
        <h2 class="text-sm font-bold text-amber-800">기본 정보</h2>
      </div>
      <div class="p-5 space-y-4">
        <!-- 이름 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-1">
            동호회 이름 <span class="text-red-400">*</span>
          </label>
          <input v-model="form.name" type="text" placeholder="예: LA 한인 등산 모임"
            class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm transition outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400" />
        </div>

        <!-- 카테고리 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-1">
            카테고리 <span class="text-red-400">*</span>
          </label>
          <select v-model="form.category"
            class="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm transition outline-none appearance-none bg-white focus:ring-2 focus:ring-amber-400 focus:border-amber-400">
            <option value="" disabled>카테고리를 선택하세요</option>
            <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>

        <!-- 활동 유형 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-2">활동 유형</label>
          <div class="flex gap-3">
            <button type="button" @click="form.type = 'online'"
              class="flex-1 py-3 rounded-xl font-bold text-sm transition-all border-2 flex items-center justify-center gap-2"
              :class="form.type === 'online'
                ? 'bg-blue-500 border-blue-500 text-white shadow-md shadow-blue-200'
                : 'bg-white border-gray-200 text-gray-400 hover:border-blue-300'">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9"/></svg>
              온라인
            </button>
            <button type="button" @click="form.type = 'local'"
              class="flex-1 py-3 rounded-xl font-bold text-sm transition-all border-2 flex items-center justify-center gap-2"
              :class="form.type === 'local'
                ? 'bg-green-500 border-green-500 text-white shadow-md shadow-green-200'
                : 'bg-white border-gray-200 text-gray-400 hover:border-green-300'">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              지역 모임
            </button>
          </div>
        </div>

        <!-- 공개 여부 -->
        <div class="flex items-center gap-3 pt-1">
          <label class="relative inline-flex items-center cursor-pointer">
            <input v-model="form.is_public" type="checkbox" class="sr-only peer" />
            <div class="w-10 h-5 bg-gray-200 peer-focus:ring-2 peer-focus:ring-amber-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-amber-400"></div>
          </label>
          <span class="text-sm font-semibold text-gray-700">공개 동호회</span>
          <span class="text-xs text-gray-400">{{ form.is_public ? '누구나 자유롭게 가입할 수 있습니다' : '가입 승인이 필요합니다' }}</span>
        </div>

        <!-- 최대 인원 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-1">최대 인원</label>
          <div class="flex items-center gap-3">
            <input v-model.number="form.max_members" type="number" min="0" placeholder="0"
              class="w-32 border border-gray-300 rounded-lg px-4 py-2.5 text-sm transition outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400" />
            <span class="text-xs text-gray-400">0 = 무제한</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 2: 위치 (local only) -->
    <section v-if="form.type === 'local'" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 bg-green-50">
        <h2 class="text-sm font-bold text-green-800">활동 위치</h2>
      </div>
      <div class="p-5">
        <div class="grid grid-cols-3 gap-3">
          <div>
            <label class="text-xs text-gray-500 block mb-1">City</label>
            <input v-model="form.city" type="text" placeholder="예: Los Angeles"
              class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm transition outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400" />
          </div>
          <div>
            <label class="text-xs text-gray-500 block mb-1">State</label>
            <input v-model="form.state" type="text" placeholder="예: CA"
              class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm transition outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400" />
          </div>
          <div>
            <label class="text-xs text-gray-500 block mb-1">Zip Code</label>
            <input v-model="form.zipcode" type="text" placeholder="예: 90001"
              class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm transition outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400" />
          </div>
        </div>
      </div>
    </section>

    <!-- Section 3: 소개 & 규칙 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 bg-amber-50">
        <h2 class="text-sm font-bold text-amber-800">소개 & 규칙</h2>
      </div>
      <div class="p-5 space-y-4">
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-1">동호회 소개</label>
          <textarea v-model="form.description" rows="4"
            placeholder="동호회의 활동 내용, 모임 주기, 목표 등을 자유롭게 작성해주세요"
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm transition outline-none resize-none leading-relaxed focus:ring-2 focus:ring-amber-400 focus:border-amber-400"></textarea>
          <p class="text-xs text-gray-400 mt-1 text-right">{{ (form.description || '').length }}자</p>
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-1">동호회 규칙 (선택)</label>
          <textarea v-model="form.rules" rows="4"
            placeholder="예:&#10;1. 서로 존중하기&#10;2. 개인정보 보호&#10;3. 정기 모임 참석 필수"
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm transition outline-none resize-none leading-relaxed focus:ring-2 focus:ring-amber-400 focus:border-amber-400"></textarea>
        </div>
      </div>
    </section>

    <!-- Section 4: 이미지 -->
    <section class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-5 py-3 border-b border-gray-100 bg-amber-50">
        <h2 class="text-sm font-bold text-amber-800">이미지</h2>
      </div>
      <div class="p-5 space-y-4">
        <!-- 대표 이미지 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-2">대표 이미지 (프로필)</label>
          <div class="flex items-center gap-4">
            <div class="w-24 h-24 rounded-xl border-2 border-dashed border-gray-300 overflow-hidden flex items-center justify-center bg-gray-50"
              :class="{ 'border-amber-400': imagePreview }">
              <img v-if="imagePreview" :src="imagePreview" class="w-full h-full object-cover" />
              <span v-else class="text-3xl text-gray-300">+</span>
            </div>
            <div class="flex-1">
              <label class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold cursor-pointer bg-amber-50 text-amber-700 hover:bg-amber-100 transition border border-amber-200">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                사진 선택
                <input type="file" accept="image/*" @change="onImageSelect" class="hidden" />
              </label>
              <p class="text-xs text-gray-400 mt-1">권장: 정사각형 비율 (200x200px 이상)</p>
            </div>
          </div>
        </div>

        <!-- 커버 이미지 -->
        <div>
          <label class="text-sm font-semibold text-gray-700 block mb-2">커버 이미지 (배너)</label>
          <div class="relative w-full h-32 rounded-xl border-2 border-dashed border-gray-300 overflow-hidden flex items-center justify-center bg-gray-50 cursor-pointer hover:border-amber-400 transition"
            :class="{ 'border-amber-400': coverPreview }"
            @click="$refs.coverInput.click()">
            <img v-if="coverPreview" :src="coverPreview" class="w-full h-full object-cover" />
            <div v-else class="text-center">
              <span class="text-3xl text-gray-300 block">+</span>
              <span class="text-xs text-gray-400">클릭하여 커버 이미지 업로드</span>
            </div>
          </div>
          <input ref="coverInput" type="file" accept="image/*" @change="onCoverSelect" class="hidden" />
          <p class="text-xs text-gray-400 mt-1">권장: 가로 비율 (1200x300px 이상)</p>
        </div>
      </div>
    </section>

    <!-- Error -->
    <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 rounded-xl px-5 py-3 text-sm font-medium">
      {{ error }}
    </div>

    <!-- Actions -->
    <div class="flex gap-3 pb-10">
      <button @click="submit" :disabled="submitting"
        class="flex-1 sm:flex-none font-bold px-8 py-3 rounded-xl shadow-md transition disabled:opacity-50 text-sm bg-amber-400 text-amber-900 hover:bg-amber-500 shadow-amber-200">
        {{ submitting ? '저장 중...' : (isEdit ? '수정하기' : '만들기') }}
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const form = reactive({
  name: '',
  description: '',
  rules: '',
  category: '',
  type: 'local',
  city: '',
  state: '',
  zipcode: '',
  max_members: 0,
  is_public: true,
})

const categories = [
  { value: 'hiking', label: '등산' },
  { value: 'golf', label: '골프' },
  { value: 'tennis', label: '테니스' },
  { value: 'bowling', label: '볼링' },
  { value: 'books', label: '독서' },
  { value: 'cooking', label: '요리' },
  { value: 'photo', label: '사진' },
  { value: 'music', label: '음악' },
  { value: 'fitness', label: '운동' },
  { value: 'movie', label: '영화' },
  { value: 'gaming', label: '게임' },
  { value: 'travel', label: '여행' },
  { value: 'fishing', label: '낚시' },
  { value: 'etc', label: '기타' },
]

const imageFile = ref(null)
const imagePreview = ref(null)
const coverFile = ref(null)
const coverPreview = ref(null)

const error = ref('')
const submitting = ref(false)
const isEdit = ref(false)
const editId = ref(null)

function onImageSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value = file
  const reader = new FileReader()
  reader.onload = ev => { imagePreview.value = ev.target.result }
  reader.readAsDataURL(file)
}

function onCoverSelect(e) {
  const file = e.target.files[0]
  if (!file) return
  coverFile.value = file
  const reader = new FileReader()
  reader.onload = ev => { coverPreview.value = ev.target.result }
  reader.readAsDataURL(file)
}

async function submit() {
  if (!form.name.trim()) { error.value = '동호회 이름을 입력해주세요'; return }
  if (!form.category) { error.value = '카테고리를 선택해주세요'; return }

  submitting.value = true
  error.value = ''

  try {
    const fd = new FormData()
    fd.append('name', form.name)
    fd.append('description', form.description || '')
    fd.append('rules', form.rules || '')
    fd.append('category', form.category)
    fd.append('type', form.type)
    fd.append('city', form.city || '')
    fd.append('state', form.state || '')
    fd.append('zipcode', form.zipcode || '')
    fd.append('max_members', form.max_members || 0)
    fd.append('is_public', form.is_public ? '1' : '0')

    if (imageFile.value) fd.append('image', imageFile.value)
    if (coverFile.value) fd.append('cover_image', coverFile.value)

    if (isEdit.value) {
      fd.append('_method', 'PUT')
      const { data } = await axios.post(`/api/clubs/${editId.value}`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      router.push(`/clubs/${editId.value}`)
    } else {
      const { data } = await axios.post('/api/clubs', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      const newId = data.data?.id || data.id
      router.push(`/clubs/${newId}`)
    }
  } catch (e) {
    const msg = e.response?.data?.message || ''
    const errs = e.response?.data?.errors ? Object.values(e.response.data.errors).flat().join(', ') : ''
    error.value = msg || errs || '저장에 실패했습니다. 다시 시도해주세요.'
  }
  submitting.value = false
}

onMounted(async () => {
  // Edit mode: /clubs/:id/edit
  if (route.params.id) {
    editId.value = route.params.id
    isEdit.value = true
    try {
      const { data } = await axios.get(`/api/clubs/${editId.value}`)
      const c = data.data
      Object.keys(form).forEach(k => {
        if (c[k] !== undefined && c[k] !== null) form[k] = c[k]
      })
      // Boolean cast
      form.is_public = !!c.is_public
      // Existing images
      if (c.image) imagePreview.value = c.image.startsWith('http') ? c.image : `/storage/${c.image}`
      if (c.cover_image) coverPreview.value = c.cover_image.startsWith('http') ? c.cover_image : `/storage/${c.cover_image}`
    } catch {}
  } else {
    // Auto-fill location from user profile
    if (auth.user) {
      if (auth.user.city) form.city = auth.user.city
      if (auth.user.state) form.state = auth.user.state
      if (auth.user.zipcode) form.zipcode = auth.user.zipcode
    }
  }
})
</script>
