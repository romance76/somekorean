<template>
  <WriteTemplate
    :title="isEdit ? '부동산 매물 수정' : '부동산 매물 등록'"
    :loading="submitting"
    :submitLabel="isEdit ? '매물 수정' : '매물 등록'"
    :modelValue="form"
    :hasImages="true"
    :hasLocation="true"
    titlePlaceholder="예: LA 한인타운 2BR 아파트 렌트"
    contentPlaceholder="매물에 대한 상세 정보를 입력해 주세요"
    @update:modelValue="form = $event"
    @submit="submit"
  >
    <template #fields>
      <!-- Type & Property Type -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">매물 유형 <span class="text-red-400">*</span></label>
          <select v-model="form.type"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">선택</option>
            <option>렌트</option>
            <option>매매</option>
            <option>룸메이트</option>
            <option>상가</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">건물 유형</label>
          <select v-model="form.property_type"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">선택</option>
            <option>아파트</option>
            <option>하우스</option>
            <option>콘도</option>
            <option>스튜디오</option>
            <option>오피스</option>
          </select>
        </div>
      </div>

      <!-- Price & Deposit -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">가격 ($) <span class="text-red-400">*</span></label>
          <input v-model="form.price" type="number" min="0" placeholder="월세 또는 매매가"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
        <div v-if="form.type === '렌트' || form.type === '룸메이트'">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">디파짓 ($)</label>
          <input v-model="form.deposit" type="number" min="0" placeholder="보증금"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
      </div>

      <!-- Bedrooms, Bathrooms, Sqft -->
      <div class="grid grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">방 수</label>
          <input v-model="form.bedrooms" type="number" min="0" max="20" placeholder="0"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">욕실 수</label>
          <input v-model="form.bathrooms" type="number" min="0" max="10" placeholder="0"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">면적 (sqft)</label>
          <input v-model="form.sqft" type="number" min="0" placeholder="0"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
      </div>

      <!-- Move-in date & Pet policy -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">입주 가능일</label>
          <input v-model="form.move_in_date" type="date"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">반려동물</label>
          <div class="flex gap-2">
            <button v-for="p in petOptions" :key="p.value" type="button" @click="form.pet_policy = p.value"
              class="flex-1 py-2 rounded-lg font-semibold text-xs transition"
              :class="form.pet_policy === p.value ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200'">
              {{ p.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Contact info -->
      <div class="border-t border-gray-100 dark:border-gray-700 pt-4">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">연락처</h3>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs text-gray-500 mb-1">전화번호</label>
            <input v-model="form.phone" type="tel" placeholder="000-000-0000"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label class="block text-xs text-gray-500 mb-1">이메일</label>
            <input v-model="form.email" type="email" placeholder="email@example.com"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="text-red-600 text-sm bg-red-50 dark:bg-red-900/30 p-3 rounded-xl">{{ error }}</div>
    </template>
  </WriteTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import WriteTemplate from '@/components/templates/WriteTemplate.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const submitting = ref(false)
const error = ref('')
const isEdit = ref(false)
const editId = ref(null)

const petOptions = [
  { value: '가능', label: '🐶 가능' },
  { value: '불가', label: '🚫 불가' },
  { value: '협의', label: '💬 협의' },
]

const form = ref({
  title: '',
  content: '',
  type: '',
  property_type: '',
  price: '',
  deposit: '',
  bedrooms: '',
  bathrooms: '',
  sqft: '',
  move_in_date: '',
  pet_policy: '협의',
  phone: '',
  email: '',
  address: '',
})

async function submit({ files }) {
  if (!form.value.title?.trim()) { error.value = '제목을 입력하세요.'; return }
  if (!form.value.type) { error.value = '매물 유형을 선택하세요.'; return }

  submitting.value = true
  error.value = ''
  try {
    const fd = new FormData()
    // description from content field
    fd.append('description', form.value.content || '')
    const fields = ['title', 'type', 'property_type', 'price', 'deposit', 'bedrooms', 'bathrooms', 'sqft', 'move_in_date', 'pet_policy', 'phone', 'email', 'address']
    fields.forEach(k => { if (form.value[k] !== '' && form.value[k] != null) fd.append(k, form.value[k]) })

    if (files?.length) {
      files.forEach((file, i) => fd.append(`photos[${i}]`, file))
    }

    if (isEdit.value) {
      fd.append('_method', 'PUT')
      await axios.post(`/api/realestate/${editId.value}`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      router.push(`/realestate/${editId.value}`)
    } else {
      const { data } = await axios.post('/api/realestate', fd, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      router.push(`/realestate/${data.listing?.id || data.id || ''}`)
    }
  } catch (e) {
    error.value = e.response?.data?.message || '등록 실패. 다시 시도해 주세요.'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const id = route.query.edit
  if (id) {
    isEdit.value = true
    editId.value = id
    try {
      const { data } = await axios.get(`/api/realestate/${id}`)
      form.value.title = data.title || ''
      form.value.content = data.description || ''
      form.value.type = data.type || ''
      form.value.property_type = data.property_type || ''
      form.value.price = data.price ?? ''
      form.value.address = data.address || ''
      form.value.bedrooms = data.bedrooms ?? ''
      form.value.bathrooms = data.bathrooms ?? ''
      form.value.sqft = data.sqft ?? ''
      form.value.deposit = data.deposit ?? ''
      form.value.move_in_date = data.move_in_date || ''
      form.value.pet_policy = data.pet_policy || '협의'
      form.value.phone = data.phone || ''
      form.value.email = data.email || ''
    } catch {
      error.value = '기존 매물 정보를 불러올 수 없습니다.'
    }
  }
})
</script>
