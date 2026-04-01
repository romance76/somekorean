<template>
  <div class="max-w-[800px] mx-auto px-4 py-6">

    <!-- 헤더 -->
    <div class="bg-gradient-to-r from-red-500 to-pink-500 rounded-2xl px-6 py-5 mb-6 shadow-lg">
      <h1 class="text-white text-xl font-black">{{ isEdit ? '✏️ 글 수정' : '✏️ 새 글쓰기' }}</h1>
      <p class="text-red-100 text-sm mt-1">커뮤니티에 글을 {{ isEdit ? '수정' : '작성' }}합니다</p>
    </div>

    <div class="bg-white rounded-xl border border-gray-100 p-6">
      <!-- 카테고리 선택 -->
      <div class="mb-4">
        <label class="block text-sm font-bold text-gray-700 mb-1.5">카테고리</label>
        <select
          v-model="form.category_slug"
          class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-300"
        >
          <option value="">카테고리를 선택하세요</option>
          <option v-for="cat in categories" :key="cat.slug" :value="cat.slug">
            {{ cat.icon }} {{ cat.name }}
          </option>
        </select>
      </div>

      <!-- 제목 -->
      <div class="mb-4">
        <label class="block text-sm font-bold text-gray-700 mb-1.5">제목</label>
        <input
          v-model="form.title"
          type="text"
          placeholder="제목을 입력하세요"
          class="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-300"
          maxlength="200"
        />
      </div>

      <!-- 내용 -->
      <div class="mb-4">
        <label class="block text-sm font-bold text-gray-700 mb-1.5">내용</label>
        <textarea
          v-model="form.content"
          rows="12"
          placeholder="내용을 입력하세요..."
          class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-300 resize-none"
        ></textarea>
      </div>

      <!-- 익명 체크박스 -->
      <div class="mb-6">
        <label class="flex items-center gap-2 cursor-pointer">
          <input
            v-model="form.is_anonymous"
            type="checkbox"
            class="w-4 h-4 rounded border-gray-300 text-red-500 focus:ring-red-300"
          />
          <span class="text-sm text-gray-600">🎭 익명으로 작성</span>
        </label>
        <p v-if="form.category_slug === 'anonymous'" class="text-xs text-gray-400 mt-1 ml-6">
          이 카테고리는 자동으로 익명 처리됩니다.
        </p>
      </div>

      <!-- 버튼 -->
      <div class="flex justify-end gap-3">
        <button
          @click="cancel"
          class="px-6 py-2.5 rounded-xl text-sm font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 transition"
        >
          취소
        </button>
        <button
          @click="submitPost"
          :disabled="submitting || !form.category_slug || !form.title.trim() || !form.content.trim()"
          class="px-6 py-2.5 rounded-xl text-sm font-bold text-white bg-red-500 hover:bg-red-600 transition disabled:opacity-50"
        >
          {{ submitting ? '처리 중...' : (isEdit ? '수정' : '등록') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()
const categories = ref([])
const submitting = ref(false)

const form = ref({
  category_slug: '',
  title: '',
  content: '',
  is_anonymous: false
})

const isEdit = computed(() => route.name === 'community-edit')
const editSlug = computed(() => route.params.slug)
const editId = computed(() => route.params.id)

function getAuthHeaders() {
  const token = localStorage.getItem('sk_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function fetchCategories() {
  try {
    const { data } = await axios.get('/api/community-v2/categories', { headers: getAuthHeaders() })
    categories.value = data.data || data || []
  } catch (e) {
    console.error('카테고리 로딩 실패', e)
  }
}

async function fetchPostForEdit() {
  if (!isEdit.value) return
  try {
    const { data } = await axios.get(`/api/community-v2/${editSlug.value}/posts/${editId.value}`, { headers: getAuthHeaders() })
    const p = data.data || data
    form.value.category_slug = p.category_slug || editSlug.value
    form.value.title = p.title
    form.value.content = p.content_raw || p.content || ''
    form.value.is_anonymous = !!p.is_anonymous
  } catch (e) {
    console.error('글 로딩 실패', e)
    alert('글을 불러올 수 없습니다.')
    router.push('/community')
  }
}

async function submitPost() {
  if (!form.value.category_slug || !form.value.title.trim() || !form.value.content.trim()) {
    alert('카테고리, 제목, 내용을 모두 입력해주세요.')
    return
  }
  submitting.value = true
  try {
    if (isEdit.value) {
      await axios.put(`/api/community-v2/${editSlug.value}/posts/${editId.value}`, {
        title: form.value.title,
        content: form.value.content,
        is_anonymous: form.value.is_anonymous
      }, { headers: getAuthHeaders() })
      router.push(`/community/${editSlug.value}/${editId.value}`)
    } else {
      const { data } = await axios.post(`/api/community-v2/${form.value.category_slug}/posts`, {
        title: form.value.title,
        content: form.value.content,
        category_slug: form.value.category_slug,
        is_anonymous: form.value.is_anonymous
      }, { headers: getAuthHeaders() })
      const newPost = data.data || data
      router.push(`/community/${form.value.category_slug}/${newPost.id}`)
    }
  } catch (e) {
    console.error('글 저장 실패', e)
    alert('저장에 실패했습니다. 로그인 상태를 확인해주세요.')
  } finally {
    submitting.value = false
  }
}

function cancel() {
  if (isEdit.value) {
    router.push(`/community/${editSlug.value}/${editId.value}`)
  } else {
    router.push('/community')
  }
}

// 익명 카테고리 자동 체크
watch(() => form.value.category_slug, (val) => {
  if (val === 'anonymous') {
    form.value.is_anonymous = true
  }
})

// URL 쿼리에서 카테고리 자동 선택
onMounted(() => {
  fetchCategories()
  if (route.query.category) {
    form.value.category_slug = route.query.category
  }
  if (isEdit.value) {
    fetchPostForEdit()
  }
})
</script>
