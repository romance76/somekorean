<template>
  <WriteTemplate
    :title="isEdit ? (locale === 'ko' ? '물품 수정' : 'Edit Item') : (locale === 'ko' ? '물품 등록' : 'Sell Item')"
    :mode="isEdit ? 'edit' : 'create'"
    :loading="submitting"
    :submitLabel="isEdit ? (locale === 'ko' ? '물품 수정' : 'Update') : (locale === 'ko' ? '물품 등록' : 'Submit')"
    :titlePlaceholder="locale === 'ko' ? '물품명을 입력하세요' : 'Item name'"
    :contentPlaceholder="locale === 'ko' ? '물품 상태, 구매 시기, 하자 유무 등을 자세히 입력해주세요' : 'Item details, condition, purchase date...'"
    v-model="form"
    :hasImages="true"
    :hasLocation="true"
    @submit="onSubmit"
  >
    <template #fields>
      <!-- Price -->
      <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-700 rounded-xl p-4">
        <div class="flex flex-col sm:flex-row sm:items-center gap-3">
          <div class="flex-1">
            <label class="block text-sm font-bold text-blue-700 dark:text-blue-300 mb-1">{{ locale === 'ko' ? '가격 ($)' : 'Price ($)' }} *</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-blue-600 font-bold text-lg">$</span>
              <input v-model="form.price" type="number" min="0" placeholder="0"
                class="w-full border border-blue-200 dark:border-blue-600 rounded-lg pl-8 pr-3 py-3 text-lg font-bold text-blue-700 dark:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700" />
            </div>
          </div>
          <label class="flex items-center gap-2 cursor-pointer sm:pt-6">
            <input v-model="form.price_negotiable" type="checkbox" class="rounded text-blue-600 w-4 h-4" />
            <span class="text-sm text-blue-600 dark:text-blue-400 font-medium">{{ locale === 'ko' ? '가격 협의 가능' : 'Negotiable' }}</span>
          </label>
        </div>
      </div>

      <!-- Category / Condition -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ locale === 'ko' ? '카테고리' : 'Category' }}</label>
          <select v-model="form.category"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">{{ locale === 'ko' ? '선택' : 'Select' }}</option>
            <option v-for="cat in ['전자제품','의류/잡화','가구/인테리어','식품','도서','유아동','기타']" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{{ locale === 'ko' ? '상품 상태' : 'Condition' }}</label>
          <select v-model="form.condition"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">{{ locale === 'ko' ? '선택' : 'Select' }}</option>
            <option value="새것">{{ locale === 'ko' ? '새것' : 'New' }}</option>
            <option value="거의 새것">{{ locale === 'ko' ? '거의 새것' : 'Like New' }}</option>
            <option value="사용감 있음">{{ locale === 'ko' ? '사용감 있음' : 'Used - Good' }}</option>
            <option value="많이 사용">{{ locale === 'ko' ? '많이 사용' : 'Used - Fair' }}</option>
          </select>
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
  price: '',
  price_negotiable: false,
  category: '',
  condition: '',
})

async function onSubmit({ files }) {
  if (!form.value.title?.trim()) { error.value = locale.value === 'ko' ? '제목을 입력하세요' : 'Enter title'; return }
  if (form.value.price === '' && form.value.price !== 0) { error.value = locale.value === 'ko' ? '가격을 입력하세요' : 'Enter price'; return }

  submitting.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('title', form.value.title)
    fd.append('description', form.value.content || '')
    fd.append('price', form.value.price || 0)
    fd.append('price_negotiable', form.value.price_negotiable ? '1' : '0')
    if (form.value.category) fd.append('category', form.value.category)
    if (form.value.condition) fd.append('condition', form.value.condition)
    if (form.value.address) fd.append('address', form.value.address)
    if (files?.length) files.forEach(f => fd.append('photos[]', f))

    if (isEdit.value) {
      fd.append('_method', 'PUT')
      await axios.post(`/api/market/${editId.value}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      router.push(`/market/${editId.value}`)
    } else {
      const { data } = await axios.post('/api/market', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      router.push(`/market/${data.item?.id || data.id}`)
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
      const { data } = await axios.get(`/api/market/${id}`)
      form.value.title = data.title || ''
      form.value.content = data.description || ''
      form.value.price = data.price ?? ''
      form.value.price_negotiable = !!data.price_negotiable
      form.value.category = data.category || ''
      form.value.condition = data.condition || ''
    } catch { error.value = locale.value === 'ko' ? '기존 물품을 불러올 수 없습니다' : 'Could not load item' }
  }
})
</script>
