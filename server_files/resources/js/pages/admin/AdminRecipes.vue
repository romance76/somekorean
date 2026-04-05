<template>
  <div class="space-y-5">
    <!-- 통계 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">전체 레시피</div>
        <div class="text-2xl font-bold text-gray-800">{{ stats.total_recipes || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">AI 생성</div>
        <div class="text-2xl font-bold text-purple-600">{{ stats.ai_recipes || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">이미지 연동</div>
        <div class="text-2xl font-bold text-green-600">{{ stats.with_images || 0 }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">댓글</div>
        <div class="text-2xl font-bold text-blue-600">{{ stats.total_comments || 0 }}</div>
      </div>
    </div>

    <!-- 탭 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="flex border-b border-gray-100">
        <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
          :class="['px-5 py-3 text-sm font-medium transition border-b-2 -mb-px',
            activeTab === tab.key ? 'border-orange-500 text-orange-600' : 'border-transparent text-gray-500 hover:text-gray-700']">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- TAB: 레시피 목록 -->
    <template v-if="activeTab === 'recipes'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex flex-wrap gap-3 items-center">
          <input v-model="search" @keyup.enter="loadRecipes" type="text" placeholder="레시피 검색..."
            class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-orange-400 w-48" />
          <select v-model="filterCategory" @change="loadRecipes"
            class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none">
            <option value="">전체 카테고리</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
          <select v-model="filterDifficulty" @change="loadRecipes"
            class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none">
            <option value="">난이도 전체</option>
            <option value="쉬움">쉬움</option>
            <option value="보통">보통</option>
            <option value="어려움">어려움</option>
          </select>
          <button @click="loadRecipes" class="bg-orange-500 text-white px-4 py-1.5 rounded-lg text-sm transition hover:bg-orange-600">검색</button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 text-gray-500 text-xs">
              <tr>
                <th class="px-4 py-3 text-left w-12">이미지</th>
                <th class="px-4 py-3 text-left">제목</th>
                <th class="px-4 py-3 text-left">카테고리</th>
                <th class="px-4 py-3 text-left">난이도</th>
                <th class="px-4 py-3 text-left">조리시간</th>
                <th class="px-4 py-3 text-left">좋아요</th>
                <th class="px-4 py-3 text-left">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-if="loading"><td colspan="7" class="py-8 text-center text-gray-400">불러오는 중...</td></tr>
              <tr v-for="recipe in recipes" :key="recipe.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="w-10 h-10 rounded-lg overflow-hidden bg-gray-100">
                    <img v-if="recipe.image_url" :src="recipe.image_url" class="w-full h-full object-cover" @error="recipe.image_url=null" />
                    <div v-else class="w-full h-full flex items-center justify-center text-lg">🍽️</div>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="font-medium text-gray-800 truncate max-w-xs">{{ recipe.title }}</div>
                  <div class="text-xs text-gray-400">{{ recipe.user?.name }}</div>
                </td>
                <td class="px-4 py-3">
                  <span class="text-xs bg-orange-50 text-orange-700 px-2 py-0.5 rounded-full">{{ recipe.category?.name }}</span>
                </td>
                <td class="px-4 py-3">
                  <span :class="diffClass(recipe.difficulty)" class="text-xs px-2 py-0.5 rounded-full font-medium">{{ recipe.difficulty }}</span>
                </td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ recipe.cook_time }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">❤️ {{ recipe.like_count || 0 }}</td>
                <td class="px-4 py-3">
                  <div class="flex gap-1">
                    <button @click="openEdit(recipe)" class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition">수정</button>
                    <button @click="toggleHide(recipe)" :class="recipe.is_hidden ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                      class="text-xs px-2 py-1 rounded-lg transition hover:opacity-80">
                      {{ recipe.is_hidden ? '복구' : '숨김' }}
                    </button>
                    <button @click="deleteRecipe(recipe.id)" class="text-xs px-2 py-1 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition">삭제</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="px-5 py-3 flex justify-between items-center border-t border-gray-100">
          <span class="text-xs text-gray-400">총 {{ totalRecipes }}개</span>
          <div class="flex gap-1">
            <button v-for="p in Math.min(totalPages, 10)" :key="p" @click="page = p; loadRecipes()"
              :class="['px-2.5 py-1 rounded text-xs font-medium', page === p ? 'bg-orange-500 text-white' : 'bg-gray-100 text-gray-600']">
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
          <h3 class="font-bold text-gray-800">레시피 카테고리</h3>
          <button @click="showCatForm = !showCatForm" class="bg-orange-500 text-white px-4 py-1.5 rounded-lg text-sm transition hover:bg-orange-600">
            + 카테고리 추가
          </button>
        </div>
        <div v-if="showCatForm" class="bg-gray-50 rounded-xl p-4 mb-4">
          <div class="grid grid-cols-3 gap-3 mb-3">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">이름</label>
              <input v-model="newCat.name" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-orange-400" />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">키 (영문)</label>
              <input v-model="newCat.key" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-orange-400" />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">아이콘</label>
              <input v-model="newCat.icon" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none" />
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="createCategory" class="bg-orange-500 text-white px-4 py-2 rounded-lg text-sm">추가</button>
            <button @click="showCatForm = false" class="bg-gray-100 text-gray-600 px-4 py-2 rounded-lg text-sm">취소</button>
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
                  class="text-xs px-2 py-0.5 rounded-full font-medium">
                  {{ cat.is_active ? '활성' : '비활성' }}
                </button>
              </td>
              <td class="px-4 py-3">
                <button @click="deleteCategory(cat.id)" class="text-xs px-2 py-1 bg-red-100 text-red-600 rounded-lg">삭제</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- 수정 모달 -->
    <div v-if="editRecipe" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
        <div class="flex justify-between items-center mb-5">
          <h3 class="font-bold text-gray-800">레시피 수정</h3>
          <button @click="editRecipe = null" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="text-xs text-gray-500 mb-1 block">제목</label>
            <input v-model="editRecipe.title" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-orange-400" />
          </div>
          <div>
            <label class="text-xs text-gray-500 mb-1 block">소개</label>
            <textarea v-model="editRecipe.intro" rows="2" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none resize-none"></textarea>
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">난이도</label>
              <select v-model="editRecipe.difficulty" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none">
                <option>쉬움</option><option>보통</option><option>어려움</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">조리시간</label>
              <input v-model="editRecipe.cook_time" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none" />
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">칼로리</label>
              <input v-model="editRecipe.calories" type="number" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="text-xs text-gray-500 mb-1 block">이미지 URL</label>
            <input v-model="editRecipe.image_url" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none" />
          </div>
          <div v-if="editRecipe.image_url" class="rounded-xl overflow-hidden h-32 bg-gray-100">
            <img :src="editRecipe.image_url" class="w-full h-full object-cover" @error="editRecipe.image_url=''" />
          </div>
        </div>
        <div class="flex gap-3 mt-5">
          <button @click="saveEdit" class="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-2.5 rounded-xl text-sm font-semibold transition">저장</button>
          <button @click="editRecipe = null" class="flex-1 bg-gray-100 text-gray-600 py-2.5 rounded-xl text-sm">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const tabs = [
  { key: 'recipes', label: '레시피 목록' },
  { key: 'categories', label: '카테고리 관리' },
]
const activeTab = ref('recipes')
const stats = ref({})
const recipes = ref([])
const categories = ref([])
const loading = ref(false)
const search = ref('')
const filterCategory = ref('')
const filterDifficulty = ref('')
const page = ref(1)
const totalPages = ref(1)
const totalRecipes = ref(0)
const editRecipe = ref(null)
const showCatForm = ref(false)
const newCat = ref({ name: '', key: '', icon: '' })

function diffClass(d) {
  if (d === '쉬움') return 'bg-green-100 text-green-700'
  if (d === '어려움') return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

async function loadStats() {
  try { const { data } = await axios.get('/api/admin/recipes/stats'); stats.value = data } catch {}
}
async function loadCategories() {
  try { const { data } = await axios.get('/api/admin/recipes/categories'); categories.value = data } catch {}
}
async function loadRecipes() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (search.value) params.search = search.value
    if (filterCategory.value) params.category = filterCategory.value
    if (filterDifficulty.value) params.difficulty = filterDifficulty.value
    const { data } = await axios.get('/api/admin/recipes/list', { params })
    recipes.value = data.data || []
    totalPages.value = Math.min(data.last_page || 1, 10)
    totalRecipes.value = data.total || 0
  } catch { recipes.value = [] }
  finally { loading.value = false }
}
function openEdit(recipe) {
  editRecipe.value = { ...recipe }
}
async function saveEdit() {
  try {
    await axios.put(`/api/admin/recipes/${editRecipe.value.id}`, editRecipe.value)
    await loadRecipes()
    editRecipe.value = null
  } catch (e) { alert('저장 실패') }
}
async function toggleHide(recipe) {
  try {
    await axios.put(`/api/admin/recipes/${recipe.id}`, { is_hidden: !recipe.is_hidden })
    recipe.is_hidden = !recipe.is_hidden
  } catch {}
}
async function deleteRecipe(id) {
  if (!confirm('삭제하시겠습니까?')) return
  try { await axios.delete(`/api/admin/recipes/${id}`); await loadRecipes() } catch {}
}
async function createCategory() {
  if (!newCat.value.name || !newCat.value.key) return alert('이름과 키를 입력하세요')
  try {
    await axios.post('/api/admin/recipes/categories', newCat.value)
    newCat.value = { name: '', key: '', icon: '' }
    showCatForm.value = false
    await loadCategories()
  } catch (e) { alert(e.response?.data?.message || '추가 실패') }
}
async function toggleCatActive(cat) {
  try { await axios.put(`/api/admin/recipes/categories/${cat.id}`, { is_active: !cat.is_active }); cat.is_active = !cat.is_active } catch {}
}
async function deleteCategory(id) {
  if (!confirm('삭제하시겠습니까?')) return
  try { await axios.delete(`/api/admin/recipes/categories/${id}`); await loadCategories() } catch {}
}

onMounted(() => Promise.all([loadStats(), loadCategories(), loadRecipes()]))
</script>
