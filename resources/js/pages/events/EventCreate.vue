<template>
  <WriteTemplate
    :title="editId ? '이벤트 수정' : '이벤트 등록'"
    :loading="submitting"
    :submitLabel="editId ? '이벤트 수정' : '이벤트 등록'"
    :modelValue="form"
    :hasImages="true"
    :hasLocation="false"
    titlePlaceholder="이벤트 제목을 입력하세요"
    contentPlaceholder="이벤트에 대해 자세히 설명해주세요"
    @update:modelValue="form = $event"
    @submit="submit"
  >
    <template #fields>
      <!-- Category -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">카테고리</label>
        <select v-model="form.category"
          class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
          <option value="general">일반</option>
          <option value="meetup">모임</option>
          <option value="food">음식/맛집</option>
          <option value="culture">문화/예술</option>
          <option value="sports">스포츠</option>
          <option value="education">교육</option>
          <option value="business">비즈니스</option>
        </select>
      </div>

      <!-- Date/time -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">시작 날짜/시간 <span class="text-red-400">*</span></label>
          <input v-model="form.event_date" type="datetime-local"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">종료 날짜/시간</label>
          <input v-model="form.end_date" type="datetime-local"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
      </div>

      <!-- Online toggle -->
      <label class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-xl cursor-pointer">
        <input v-model="form.is_online" type="checkbox" class="w-5 h-5 rounded border-gray-300 text-blue-600" />
        <div>
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300">온라인 이벤트</p>
          <p class="text-xs text-gray-400">온라인으로 진행되는 이벤트입니다</p>
        </div>
      </label>

      <!-- Location -->
      <div v-if="!form.is_online">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">장소</label>
        <input v-model="form.location" type="text" placeholder="주소 또는 장소명"
          class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
      </div>

      <!-- Price & Max attendees -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">참가비 ($)</label>
          <input v-model="form.price" type="number" min="0" step="0.01" placeholder="0 = 무료"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          <p class="text-xs text-gray-400 mt-1">0 또는 비워두면 무료</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">최대 참가자</label>
          <input v-model="form.max_attendees" type="number" min="1" placeholder="무제한"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>
      </div>

      <!-- URL -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">관련 링크 (선택)</label>
        <input v-model="form.url" type="url" placeholder="https://..."
          class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
      </div>

      <!-- Error -->
      <div v-if="error" class="text-red-600 text-sm bg-red-50 dark:bg-red-900/30 p-3 rounded-xl">{{ error }}</div>
    </template>
  </WriteTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import WriteTemplate from '@/components/templates/WriteTemplate.vue'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const submitting = ref(false)
const editId = ref(null)
const error = ref('')

const form = ref({
  title: '', content: '', category: 'general',
  event_date: '', end_date: '', is_online: false,
  location: '', price: 0, max_attendees: '', url: '',
})

async function submit({ files }) {
  if (!form.value.title?.trim()) { error.value = '제목을 입력하세요.'; return }
  if (!form.value.event_date) { error.value = '날짜를 선택하세요.'; return }

  submitting.value = true
  error.value = ''
  try {
    const payload = {
      title: form.value.title,
      description: form.value.content,
      category: form.value.category,
      event_date: form.value.event_date,
      end_date: form.value.end_date || null,
      is_online: form.value.is_online,
      location: form.value.location,
      price: form.value.price || 0,
      max_attendees: form.value.max_attendees || null,
      url: form.value.url || null,
    }

    if (editId.value) {
      await axios.put(`/api/events/${editId.value}`, payload)
      router.push(`/events/${editId.value}`)
    } else {
      const { data } = await axios.post('/api/events', payload)
      router.push(`/events/${data.id}`)
    }
  } catch (e) {
    const errs = e?.response?.data?.errors
    error.value = errs ? Object.values(errs).flat().join('\n') : (e.response?.data?.message || '오류가 발생했습니다.')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const id = route.query.edit
  if (id) {
    editId.value = id
    try {
      const { data } = await axios.get(`/api/events/${id}`)
      form.value.title = data.title || ''
      form.value.content = data.description || ''
      form.value.category = data.category || 'general'
      form.value.event_date = data.event_date ? data.event_date.slice(0, 16) : ''
      form.value.end_date = data.end_date ? data.end_date.slice(0, 16) : ''
      form.value.is_online = !!data.is_online
      form.value.location = data.location || ''
      form.value.price = data.price || 0
      form.value.max_attendees = data.max_attendees || ''
      form.value.url = data.url || ''
    } catch {}
  }
})
</script>
