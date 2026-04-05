<template>
  <WriteTemplate
    :title="isEdit ? (locale === 'ko' ? '공고 수정' : 'Edit Job') : (locale === 'ko' ? '공고 등록' : 'Post a Job')"
    :mode="isEdit ? 'edit' : 'create'"
    :loading="submitting"
    :submitLabel="isEdit ? (locale === 'ko' ? '공고 수정' : 'Update') : (locale === 'ko' ? '공고 등록' : 'Submit')"
    :titlePlaceholder="locale === 'ko' ? '예: 한식당 홀서빙 직원 구합니다' : 'e.g., Korean restaurant server needed'"
    :contentPlaceholder="locale === 'ko' ? '업무 내용, 자격 요건, 복리후생 등을 자세히 입력해주세요' : 'Job description, requirements, benefits...'"
    v-model="form"
    :hasImages="true"
    :hasLocation="true"
    @submit="onSubmit"
  >
    <template #fields>
      <!-- Company / Job Type -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ locale === 'ko' ? '회사명' : 'Company' }}</label>
          <input v-model="form.company_name" type="text" :placeholder="locale === 'ko' ? '비공개 가능' : 'Optional'"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ locale === 'ko' ? '직종' : 'Job Type' }}</label>
          <select v-model="form.job_type"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">{{ locale === 'ko' ? '선택' : 'Select' }}</option>
            <option value="full_time">{{ locale === 'ko' ? '풀타임' : 'Full-time' }}</option>
            <option value="part_time">{{ locale === 'ko' ? '파트타임' : 'Part-time' }}</option>
            <option value="contract">{{ locale === 'ko' ? '계약직' : 'Contract' }}</option>
            <option value="freelance">{{ locale === 'ko' ? '프리랜서' : 'Freelance' }}</option>
          </select>
        </div>
      </div>

      <!-- Region / Salary -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ locale === 'ko' ? '지역' : 'Region' }}</label>
          <input v-model="form.region" type="text" :placeholder="locale === 'ko' ? '예: Atlanta, GA' : 'e.g., Atlanta, GA'"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ locale === 'ko' ? '급여' : 'Salary' }}</label>
          <input v-model="form.salary_range" type="text" :placeholder="locale === 'ko' ? '예: $15/hr, $3,000/월' : 'e.g., $15/hr'"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
      </div>

      <!-- Contact Info -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ locale === 'ko' ? '연락처 정보' : 'Contact Info' }}</label>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">{{ locale === 'ko' ? '이메일' : 'Email' }}</label>
            <input v-model="form.contact_email" type="email" placeholder="example@email.com"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 dark:text-gray-400 mb-1">{{ locale === 'ko' ? '전화번호' : 'Phone' }}</label>
            <input v-model="form.contact_phone" type="tel" placeholder="000-000-0000"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="text-red-600 text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">{{ error }}</div>
    </template>
  </WriteTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLangStore } from '../../stores/lang'
import WriteTemplate from '../../components/templates/WriteTemplate.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const submitting = ref(false)
const error = ref('')
const isEdit = ref(false)
const editId = ref(null)

const form = ref({
  title: '',
  content: '',
  company_name: '',
  job_type: '',
  region: '',
  salary_range: '',
  contact_email: '',
  contact_phone: '',
})

async function onSubmit({ files }) {
  if (!form.value.title?.trim()) { error.value = locale.value === 'ko' ? '제목을 입력하세요' : 'Enter a title'; return }
  if (!form.value.content?.trim()) { error.value = locale.value === 'ko' ? '내용을 입력하세요' : 'Enter content'; return }

  submitting.value = true
  error.value = ''
  try {
    const fd = new FormData()
    Object.entries(form.value).forEach(([key, val]) => {
      if (val !== null && val !== '' && key !== 'address') fd.append(key, val)
    })
    if (form.value.address) fd.append('address', form.value.address)
    if (files?.length) files.forEach(f => fd.append('photos[]', f))

    if (isEdit.value) {
      fd.append('_method', 'PUT')
      await axios.post(`/api/jobs/${editId.value}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      router.push(`/jobs/${editId.value}`)
    } else {
      const { data } = await axios.post('/api/jobs', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      router.push(`/jobs/${data.job?.id || data.id}`)
    }
  } catch (e) {
    error.value = e.response?.data?.message || (locale.value === 'ko' ? '오류가 발생했습니다' : 'An error occurred')
  } finally { submitting.value = false }
}

onMounted(async () => {
  const id = route.query.edit
  if (id) {
    isEdit.value = true
    editId.value = id
    try {
      const { data } = await axios.get(`/api/jobs/${id}`)
      form.value.title = data.title || ''
      form.value.content = data.content || ''
      form.value.company_name = data.company_name || ''
      form.value.job_type = data.job_type || ''
      form.value.region = data.region || ''
      form.value.salary_range = data.salary_range || ''
      form.value.contact_email = data.contact_email || ''
      form.value.contact_phone = data.contact_phone || ''
    } catch { error.value = locale.value === 'ko' ? '기존 공고를 불러올 수 없습니다' : 'Could not load job post' }
  }
})
</script>
