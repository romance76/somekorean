<template>
  <WriteTemplate
    :title="locale === 'ko' ? '질문 작성하기' : 'Ask a Question'"
    mode="create"
    :loading="submitting"
    :submitLabel="locale === 'ko' ? '질문 등록' : 'Submit Question'"
    :titlePlaceholder="locale === 'ko' ? '질문 제목을 입력하세요' : 'Question title'"
    :contentPlaceholder="locale === 'ko' ? '질문 내용을 자세히 작성해주세요...' : 'Describe your question in detail...'"
    v-model="form"
    :hasImages="false"
    :hasLocation="false"
    @submit="onSubmit"
  >
    <template #fields>
      <!-- Category Selector -->
      <div>
        <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">{{ locale === 'ko' ? '카테고리' : 'Category' }}</label>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <button v-for="cat in categories" :key="cat.id" type="button"
            @click="form.category_id = cat.id"
            class="px-3 py-2 rounded-lg text-sm font-medium transition border"
            :class="form.category_id === cat.id
              ? 'bg-blue-600 text-white border-blue-600'
              : 'bg-white dark:bg-gray-700 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-600 hover:border-blue-300'">
            {{ cat.icon || '' }} {{ cat.name }}
          </button>
        </div>
      </div>

      <!-- Bounty Points -->
      <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-xl p-4">
        <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
          🏆 {{ locale === 'ko' ? '포인트 걸기' : 'Set Bounty' }}
        </label>
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
          {{ locale === 'ko' ? '걸어놓은 포인트는 채택 시 답변자에게 전달됩니다' : 'Bounty goes to the accepted answer' }}
        </p>
        <div class="flex items-center gap-4">
          <input v-model.number="form.point_reward" type="range" min="0" :max="myPoints" step="10"
            class="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-yellow-500" />
          <div class="flex items-center gap-2">
            <input v-model.number="form.point_reward" type="number" min="0" :max="myPoints"
              class="w-20 border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-1.5 text-sm text-center" />
            <span class="text-sm text-gray-500 dark:text-gray-400">P</span>
          </div>
        </div>
        <p class="text-xs text-gray-400 mt-2">
          {{ locale === 'ko' ? '현재 보유' : 'Balance' }}: {{ myPoints.toLocaleString() }}P
        </p>
        <div v-if="form.point_reward > 0" class="mt-2 text-xs text-orange-600 dark:text-orange-400 font-medium">
          ⚠️ {{ locale === 'ko' ? `질문 등록 시 ${form.point_reward}P가 차감됩니다` : `${form.point_reward}P will be deducted on submit` }}
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="text-red-600 text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">{{ error }}</div>
    </template>
  </WriteTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import WriteTemplate from '../../components/templates/WriteTemplate.vue'
import axios from 'axios'

const router = useRouter()
const auth = useAuthStore()
const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const categories = ref([])
const myPoints = ref(0)
const submitting = ref(false)
const error = ref('')

const form = ref({
  title: '',
  content: '',
  category_id: null,
  point_reward: 0,
})

// Redirect if not logged in
if (!auth.isLoggedIn) {
  router.push('/auth/login')
}

async function onSubmit() {
  if (!form.value.category_id) {
    error.value = locale.value === 'ko' ? '카테고리를 선택해주세요' : 'Select a category'
    return
  }
  if (!form.value.title?.trim()) {
    error.value = locale.value === 'ko' ? '제목을 입력해주세요' : 'Enter a title'
    return
  }
  if (!form.value.content?.trim()) {
    error.value = locale.value === 'ko' ? '내용을 입력해주세요' : 'Enter content'
    return
  }
  if (form.value.point_reward > myPoints.value) {
    error.value = locale.value === 'ko' ? '보유 포인트보다 많은 포인트를 걸 수 없습니다' : 'Insufficient points'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    const { data } = await axios.post('/api/qa', {
      category_id: form.value.category_id,
      title: form.value.title,
      content: form.value.content,
      point_reward: form.value.point_reward,
    })
    const newQ = data.data || data
    auth.refreshPoints()
    router.push(`/qa/${newQ.id}`)
  } catch (e) {
    error.value = e.response?.data?.message || (locale.value === 'ko' ? '질문 등록에 실패했습니다' : 'Failed to submit question')
  }
  submitting.value = false
}

onMounted(async () => {
  try {
    const [catRes, userRes] = await Promise.allSettled([
      axios.get('/api/qa/categories'),
      axios.get('/api/auth/me'),
    ])
    if (catRes.status === 'fulfilled') {
      categories.value = catRes.value.data?.data || catRes.value.data || []
    }
    if (userRes.status === 'fulfilled') {
      const user = userRes.value.data?.user || userRes.value.data
      myPoints.value = user?.points || user?.point_balance || 0
    }
  } catch { /* empty */ }
})
</script>
