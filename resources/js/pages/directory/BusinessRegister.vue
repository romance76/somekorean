<template>
  <WriteTemplate
    title="업소 등록"
    :loading="submitting"
    submitLabel="업소 등록"
    :modelValue="form"
    :hasImages="false"
    :hasLocation="true"
    titlePlaceholder="업소명을 입력하세요"
    contentPlaceholder="업소 소개, 특징, 주요 서비스 등을 입력하세요"
    @update:modelValue="form = $event"
    @submit="submit"
  >
    <template #fields>
      <!-- Category & Region -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">카테고리 <span class="text-red-400">*</span></label>
          <select v-model="form.category"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">선택</option>
            <option>식당</option><option>미용</option><option>의료</option><option>법률</option>
            <option>부동산</option><option>쇼핑</option><option>교육</option><option>기타</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">지역</label>
          <select v-model="form.region"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">선택</option>
            <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
      </div>

      <!-- Photos -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">업소 사진</label>
        <p class="text-xs text-gray-500 mb-3">첫 번째 사진은 로고/대표 이미지로 사용됩니다.</p>
        <div class="grid grid-cols-4 sm:grid-cols-6 gap-2">
          <div v-for="i in 6" :key="i" class="relative">
            <div v-if="photos[i - 1]" class="h-20 rounded-xl overflow-hidden relative group">
              <img :src="photos[i - 1].preview" class="w-full h-full object-cover" />
              <button @click="removePhoto(i - 1)"
                class="absolute top-1 right-1 w-5 h-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
              <span v-if="i === 1" class="absolute bottom-1 left-1 bg-blue-600 text-white text-[9px] px-1.5 py-0.5 rounded-full font-medium">로고</span>
            </div>
            <label v-else class="h-20 rounded-xl border-2 border-dashed flex flex-col items-center justify-center cursor-pointer transition-colors"
              :class="i === 1 ? 'border-blue-300 hover:border-blue-400 hover:bg-blue-50' : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 hover:bg-blue-50'">
              <span class="text-xl" :class="i === 1 ? 'text-blue-400' : 'text-gray-400'">+</span>
              <span class="text-[9px] mt-0.5" :class="i === 1 ? 'text-blue-500 font-medium' : 'text-gray-400'">
                {{ i === 1 ? '로고' : '사진' }}
              </span>
              <input type="file" accept="image/*" class="hidden" @change="addPhoto($event, i - 1)" />
            </label>
          </div>
        </div>
      </div>

      <!-- Contact info -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">연락처 정보</label>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label class="block text-xs text-gray-500 mb-1">전화번호</label>
            <input v-model="form.phone" type="tel" placeholder="000-000-0000"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">이메일</label>
            <input v-model="form.email" type="email" placeholder="example@email.com"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">웹사이트</label>
            <input v-model="form.website" type="url" placeholder="https://"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
        </div>
      </div>

      <!-- Operating hours -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">영업시간</label>
        <div class="space-y-2 bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 border border-gray-100 dark:border-gray-600">
          <div v-for="day in days" :key="day.key" class="flex items-center gap-2">
            <span class="w-8 text-sm font-bold text-gray-700 dark:text-gray-300">{{ day.label }}</span>
            <input type="time" v-model="hours[day.key].open" :disabled="hours[day.key].closed"
              class="border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-40" />
            <span class="text-gray-400 text-sm">~</span>
            <input type="time" v-model="hours[day.key].close" :disabled="hours[day.key].closed"
              class="border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-40" />
            <label class="flex items-center gap-1 text-sm text-gray-500 ml-2 cursor-pointer">
              <input type="checkbox" v-model="hours[day.key].closed" class="rounded text-blue-600" />
              휴무
            </label>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="text-red-600 text-sm bg-red-50 dark:bg-red-900/30 p-3 rounded-xl">{{ error }}</div>
    </template>
  </WriteTemplate>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import WriteTemplate from '@/components/templates/WriteTemplate.vue'
import axios from 'axios'

const router = useRouter()
const submitting = ref(false)
const error = ref('')

const regions = ['Atlanta', 'New York', 'Los Angeles', 'Dallas', 'Chicago', 'Houston', 'Seattle', 'San Francisco', 'Washington DC', 'Las Vegas', 'Boston', 'Miami']

const form = ref({
  title: '', content: '', category: '', region: '',
  phone: '', email: '', website: '', address: '',
})

const days = [
  { key: 'mon', label: '월' }, { key: 'tue', label: '화' }, { key: 'wed', label: '수' },
  { key: 'thu', label: '목' }, { key: 'fri', label: '금' }, { key: 'sat', label: '토' },
  { key: 'sun', label: '일' },
]

const hours = reactive({
  mon: { open: '09:00', close: '18:00', closed: false },
  tue: { open: '09:00', close: '18:00', closed: false },
  wed: { open: '09:00', close: '18:00', closed: false },
  thu: { open: '09:00', close: '18:00', closed: false },
  fri: { open: '09:00', close: '18:00', closed: false },
  sat: { open: '10:00', close: '15:00', closed: false },
  sun: { open: '', close: '', closed: true },
})

const photos = reactive([])

function addPhoto(event, index) {
  const file = event.target.files[0]
  if (!file) return
  photos[index] = { file, preview: URL.createObjectURL(file) }
}

function removePhoto(index) {
  if (photos[index]?.preview) URL.revokeObjectURL(photos[index].preview)
  photos[index] = null
}

async function submit() {
  if (!form.value.title?.trim()) { error.value = '업소명을 입력하세요.'; return }
  if (!form.value.category) { error.value = '카테고리를 선택하세요.'; return }

  submitting.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('name', form.value.title)
    fd.append('description', form.value.content || '')
    fd.append('category', form.value.category)
    fd.append('region', form.value.region || '')
    fd.append('address', form.value.address || '')
    fd.append('phone', form.value.phone || '')
    fd.append('email', form.value.email || '')
    fd.append('website', form.value.website || '')
    fd.append('operating_hours', JSON.stringify(hours))

    photos.forEach(photo => {
      if (photo?.file) fd.append('photos[]', photo.file)
    })

    const { data } = await axios.post('/api/businesses', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    router.push(`/directory/${data.business?.id || data.id}`)
  } catch (e) {
    error.value = e.response?.data?.message || '오류가 발생했습니다.'
  } finally {
    submitting.value = false
  }
}
</script>
