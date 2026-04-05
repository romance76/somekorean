<template>
  <WriteTemplate
    :title="editId ? (locale === 'ko' ? '게시글 수정' : 'Edit Post') : (locale === 'ko' ? '글쓰기' : 'Write')"
    :mode="editId ? 'edit' : 'create'"
    :loading="submitting"
    :submitLabel="editId ? (locale === 'ko' ? '수정 완료' : 'Update') : (locale === 'ko' ? '등록' : 'Submit')"
    :cancelLabel="locale === 'ko' ? '취소' : 'Cancel'"
    :titlePlaceholder="locale === 'ko' ? '제목을 입력하세요' : 'Enter title'"
    :contentPlaceholder="locale === 'ko' ? '내용을 입력하세요' : 'Enter content'"
    v-model="form"
    :categories="boardCategories"
    :hasImages="true"
    :hasLocation="false"
    @submit="onSubmit"
  >
    <template #fields>
      <!-- Board Selector -->
      <div v-if="!$route.query.board">
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          {{ locale === 'ko' ? '게시판 선택' : 'Select Board' }} *
        </label>
        <select v-model="form.board_id"
          class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
          <option value="">{{ locale === 'ko' ? '게시판을 선택하세요' : 'Select a board' }}</option>
          <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.icon || '📋' }} {{ b.name }}</option>
        </select>
      </div>

      <!-- Anonymous Toggle -->
      <div class="flex items-center gap-4">
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="form.is_anonymous" type="checkbox" class="rounded text-blue-600 w-4 h-4" />
          <span class="text-sm text-gray-600 dark:text-gray-400">{{ locale === 'ko' ? '익명으로 작성' : 'Post anonymously' }}</span>
        </label>
      </div>

      <!-- Error -->
      <div v-if="error" class="text-red-600 text-sm bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">{{ error }}</div>
    </template>
  </WriteTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import WriteTemplate from '../../components/templates/WriteTemplate.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const langStore = useLangStore()
const locale = computed(() => langStore.locale)

const editId = ref(route.query.edit || null)
const boards = ref([])
const submitting = ref(false)
const error = ref('')

const form = ref({
  board_id: route.query.board_id || '',
  title: '',
  content: '',
  category: '',
  is_anonymous: false,
})

const boardCategories = computed(() => {
  // If board has categories, return them
  const board = boards.value.find(b => b.id == form.value.board_id)
  if (board?.categories?.length) {
    return board.categories.map(c => ({ value: c.slug || c.id, label: c.name }))
  }
  return null
})

async function onSubmit({ files }) {
  if (!form.value.board_id && !route.query.board) {
    error.value = locale.value === 'ko' ? '게시판을 선택하세요' : 'Please select a board'
    return
  }
  if (!form.value.title?.trim()) {
    error.value = locale.value === 'ko' ? '제목을 입력하세요' : 'Please enter a title'
    return
  }
  if (!form.value.content?.trim()) {
    error.value = locale.value === 'ko' ? '내용을 입력하세요' : 'Please enter content'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('board_id', form.value.board_id)
    fd.append('title', form.value.title)
    fd.append('content', form.value.content)
    if (form.value.category) fd.append('category', form.value.category)
    fd.append('is_anonymous', form.value.is_anonymous ? '1' : '0')

    if (files?.length) {
      files.forEach(f => fd.append('photos[]', f))
    }

    if (editId.value) {
      fd.append('_method', 'PUT')
      await axios.post(`/api/posts/${editId.value}`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      auth.refreshPoints()
      router.push(`/community/post/${editId.value}`)
    } else {
      const { data } = await axios.post('/api/posts', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      auth.refreshPoints()
      router.push(`/community/post/${data.post?.id || data.id}`)
    }
  } catch (e) {
    error.value = e.response?.data?.message || Object.values(e.response?.data?.errors || {})[0]?.[0] || (locale.value === 'ko' ? '오류가 발생했습니다' : 'An error occurred')
  } finally { submitting.value = false }
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/boards')
    boards.value = Array.isArray(data) ? data : data.data || []
  } catch { /* empty */ }

  // Set board from route query
  if (route.query.board) {
    const board = boards.value.find(b => b.slug === route.query.board)
    if (board) form.value.board_id = board.id
  }

  // Load existing post for editing
  if (editId.value) {
    try {
      const { data } = await axios.get(`/api/posts/${editId.value}`)
      if (data.user_id !== auth.user?.id && !auth.user?.is_admin) {
        router.push(`/community/post/${editId.value}`)
        return
      }
      form.value.board_id = data.board_id
      form.value.title = data.title
      form.value.content = data.content
    } catch {
      error.value = locale.value === 'ko' ? '게시글을 불러올 수 없습니다' : 'Could not load post'
    }
  }
})
</script>
