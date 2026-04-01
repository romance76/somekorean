<template>
  <div class="space-y-5">
    <!-- 헤더 통계 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">전체 Q&A</div>
        <div class="text-2xl font-bold text-gray-800">{{ stats.total_posts || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">해결됨</div>
        <div class="text-2xl font-bold text-green-600">{{ stats.solved_posts || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">전체 답변</div>
        <div class="text-2xl font-bold text-blue-600">{{ stats.total_answers || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">AI 생성</div>
        <div class="text-2xl font-bold text-purple-600">{{ stats.ai_posts || 0 }}</div>
      </div>
    </div>

    <!-- 탭 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="flex border-b border-gray-100">
        <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
          :class="['px-5 py-3 text-sm font-medium transition border-b-2 -mb-px',
            activeTab === tab.key ? 'border-violet-500 text-violet-600' : 'border-transparent text-gray-500 hover:text-gray-700']">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- TAB: 게시글 목록 -->
    <template v-if="activeTab === 'posts'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex flex-wrap gap-3 items-center">
          <input v-model="search" @keyup.enter="loadPosts" type="text" placeholder="제목 검색..."
            class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-violet-400 w-48" />
          <select v-model="filterCategory" @change="loadPosts"
            class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none">
            <option value="">전체 카테고리</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <select v-model="filterStatus" @change="loadPosts"
            class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none">
            <option value="">전체 상태</option>
            <option value="open">미답변</option>
            <option value="solved">해결</option>
            <option value="closed">마감</option>
          </select>
          <button @click="loadPosts" class="bg-violet-500 text-white px-4 py-1.5 rounded-lg text-sm transition hover:bg-violet-600">검색</button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs">
              <tr>
                <th class="px-4 py-3 text-left">제목</th>
                <th class="px-4 py-3 text-left">카테고리</th>
                <th class="px-4 py-3 text-left">작성자</th>
                <th class="px-4 py-3 text-left">상태</th>
                <th class="px-4 py-3 text-left">답변</th>
                <th class="px-4 py-3 text-left">작성일</th>
                <th class="px-4 py-3 text-left">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-if="loading" class="text-center"><td colspan="7" class="py-8 text-gray-400">불러오는 중...</td></tr>
              <tr v-for="post in posts" :key="post.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 max-w-xs">
                  <div class="font-medium text-gray-800 truncate">{{ post.title }}</div>
                  <div v-if="post.is_hidden" class="text-xs text-red-400">숨김</div>
                </td>
                <td class="px-4 py-3">
                  <span class="text-xs bg-violet-50 text-violet-700 px-2 py-0.5 rounded-full">{{ post.category?.name }}</span>
                </td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ post.user?.name }}</td>
                <td class="px-4 py-3">
                  <span :class="statusClass(post.status)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ statusLabel(post.status) }}</span>
                </td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ post.answer_count }}</td>
                <td class="px-4 py-3 text-gray-400 text-xs">{{ formatDate(post.created_at) }}</td>
                <td class="px-4 py-3">
                  <div class="flex gap-1">
                    <button @click="toggleHide(post)" :class="post.is_hidden ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                      class="text-xs px-2 py-1 rounded-lg transition hover:opacity-80">
                      {{ post.is_hidden ? '복구' : '숨김' }}
                    </button>
                    <button @click="deletePost(post.id)" class="text-xs px-2 py-1 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition">삭제</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 페이지네이션 -->
        <div class="px-5 py-3 flex justify-between items-center border-t border-gray-100">
          <span class="text-xs text-gray-400">총 {{ totalPosts }}개</span>
          <div class="flex gap-1">
            <button v-for="p in totalPages" :key="p" @click="page = p; loadPosts()"
              :class="['px-2.5 py-1 rounded text-xs font-medium', page === p ? 'bg-violet-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
              {{ p }}
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- TAB: 카테고리 관리 -->
    <template v-if="activeTab === 'categories'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-gray-800">카테고리 관리</h3>
          <button @click="showCatForm = !showCatForm" class="bg-violet-500 text-white px-4 py-1.5 rounded-lg text-sm transition hover:bg-violet-600">
            + 카테고리 추가
          </button>
        </div>

        <!-- 추가 폼 -->
        <div v-if="showCatForm" class="bg-gray-50 rounded-xl p-4 mb-4">
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">이름</label>
              <input v-model="newCat.name" type="text" placeholder="카테고리명"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400" />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">키 (영문)</label>
              <input v-model="newCat.key" type="text" placeholder="category-key"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-violet-400" />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">아이콘</label>
              <input v-model="newCat.icon" type="text" placeholder="🏠"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">색상</label>
              <input v-model="newCat.color" type="text" placeholder="blue"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none" />
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="createCategory" class="bg-violet-500 text-white px-4 py-2 rounded-lg text-sm transition hover:bg-violet-600">추가</button>
            <button @click="showCatForm = false" class="bg-gray-100 text-gray-600 px-4 py-2 rounded-lg text-sm transition hover:bg-gray-200">취소</button>
          </div>
        </div>

        <table class="w-full text-sm">
          <thead class="bg-gray-50 text-gray-500 text-xs">
            <tr>
              <th class="px-4 py-3 text-left">아이콘</th>
              <th class="px-4 py-3 text-left">이름</th>
              <th class="px-4 py-3 text-left">키</th>
              <th class="px-4 py-3 text-left">상태</th>
              <th class="px-4 py-3 text-left">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="cat in categories" :key="cat.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-xl">{{ cat.icon }}</td>
              <td class="px-4 py-3 font-medium text-gray-800">{{ cat.name }}</td>
              <td class="px-4 py-3 text-gray-400 text-xs font-mono">{{ cat.key }}</td>
              <td class="px-4 py-3">
                <button @click="toggleCatActive(cat)" :class="cat.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                  class="text-xs px-2 py-0.5 rounded-full font-medium transition hover:opacity-80">
                  {{ cat.is_active ? '활성' : '비활성' }}
                </button>
              </td>
              <td class="px-4 py-3">
                <button @click="deleteCategory(cat.id)" class="text-xs px-2 py-1 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition">삭제</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tabs = [
  { key: 'posts', label: 'Q&A 목록' },
  { key: 'categories', label: '카테고리 관리' },
]
const activeTab = ref('posts')
const stats = ref({})
const posts = ref([])
const categories = ref([])
const loading = ref(false)
const search = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const page = ref(1)
const totalPages = ref(1)
const totalPosts = ref(0)
const showCatForm = ref(false)
const newCat = ref({ name: '', key: '', icon: '', color: 'blue' })

function statusLabel(s) { return { open: '미답변', solved: '해결', closed: '마감' }[s] || s }
function statusClass(s) {
  if (s === 'solved') return 'bg-green-100 text-green-700'
  if (s === 'closed') return 'bg-gray-100 text-gray-500'
  return 'bg-blue-100 text-blue-600'
}
function formatDate(d) { return d ? new Date(d).toLocaleDateString('ko-KR') : '' }

async function loadStats() {
  try { const { data } = await axios.get('/api/admin/qa/stats'); stats.value = data } catch {}
}
async function loadCategories() {
  try { const { data } = await axios.get('/api/admin/qa/categories'); categories.value = data } catch {}
}
async function loadPosts() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (search.value) params.search = search.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterStatus.value) params.status = filterStatus.value
    const { data } = await axios.get('/api/admin/qa/posts', { params })
    posts.value = data.data || []
    totalPages.value = Math.min(data.last_page || 1, 10)
    totalPosts.value = data.total || 0
  } catch { posts.value = [] }
  finally { loading.value = false }
}
async function toggleHide(post) {
  try {
    await axios.put(`/api/admin/qa/posts/${post.id}`, { is_hidden: !post.is_hidden })
    post.is_hidden = !post.is_hidden
  } catch {}
}
async function deletePost(id) {
  if (!confirm('삭제하시겠습니까?')) return
  try { await axios.delete(`/api/admin/qa/posts/${id}`); await loadPosts() } catch {}
}
async function createCategory() {
  if (!newCat.value.name || !newCat.value.key) return alert('이름과 키를 입력하세요')
  try {
    await axios.post('/api/admin/qa/categories', newCat.value)
    newCat.value = { name: '', key: '', icon: '', color: 'blue' }
    showCatForm.value = false
    await loadCategories()
  } catch (e) { alert(e.response?.data?.message || '추가 실패') }
}
async function toggleCatActive(cat) {
  try { await axios.put(`/api/admin/qa/categories/${cat.id}`, { is_active: !cat.is_active }); cat.is_active = !cat.is_active } catch {}
}
async function deleteCategory(id) {
  if (!confirm('카테고리를 삭제하시겠습니까?')) return
  try { await axios.delete(`/api/admin/qa/categories/${id}`); await loadCategories() } catch {}
}

onMounted(async () => {
  await Promise.all([loadStats(), loadCategories(), loadPosts()])
})
</script>
