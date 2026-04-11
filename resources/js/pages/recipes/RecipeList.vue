<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 py-5">
    <div class="mb-4">
      <h1 class="text-2xl font-black text-gray-800">🍳 레시피</h1>
      <p class="text-xs text-gray-500 mt-1">한국 전통 음식 레시피 <span class="font-bold text-amber-700">{{ total.toLocaleString() }}</span>개 · 출처: 식품안전나라</p>
    </div>

    <!-- 검색 -->
    <div class="mb-3">
      <input v-model="search" @keyup.enter="loadRecipes(1)" type="text" placeholder="레시피 검색 (예: 김치찌개, 불고기, 비빔밥)"
        class="w-full border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
    </div>

    <!-- 카테고리 탭 -->
    <div class="flex gap-1.5 overflow-x-auto pb-2 mb-4 scrollbar-hide">
      <button @click="selectCategory('')"
        :class="selectedCat === '' ? 'bg-amber-400 text-amber-900' : 'bg-white border text-gray-600 hover:bg-amber-50'"
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold transition">
        전체
      </button>
      <button v-for="c in categories" :key="c.category"
        @click="selectCategory(c.category)"
        :class="selectedCat === c.category ? 'bg-amber-400 text-amber-900' : 'bg-white border text-gray-600 hover:bg-amber-50'"
        class="flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-bold transition">
        {{ c.category }} <span class="text-[9px] opacity-60">({{ c.count }})</span>
      </button>
    </div>

    <!-- 로딩/빈 상태 -->
    <div v-if="loading" class="text-center py-16 text-gray-400">로딩중...</div>
    <div v-else-if="!recipes.length" class="text-center py-16 text-gray-400">레시피가 없습니다</div>

    <!-- 카드 그리드 -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
      <RouterLink v-for="recipe in recipes" :key="recipe.id" :to="'/recipes/' + recipe.id"
        class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md hover:-translate-y-0.5 transition-all">
        <div class="aspect-square bg-amber-50 relative overflow-hidden">
          <img v-if="recipe.thumbnail" :src="recipe.thumbnail" :alt="recipe.title"
            class="w-full h-full object-cover" @error="$event.target.style.display='none'" />
          <div v-else class="w-full h-full flex items-center justify-center text-5xl">🍲</div>
          <span v-if="recipe.category" class="absolute top-2 left-2 bg-white/90 backdrop-blur text-[10px] font-bold text-amber-700 px-2 py-0.5 rounded-full">
            {{ recipe.category }}
          </span>
        </div>
        <div class="p-3">
          <h3 class="text-sm font-bold text-gray-800 line-clamp-2 leading-tight">{{ recipe.title }}</h3>
          <div class="flex items-center gap-2 mt-2 text-[10px] text-gray-400 flex-wrap">
            <span v-if="recipe.calories">🔥 {{ recipe.calories }}kcal</span>
            <span v-if="recipe.cook_method">· {{ recipe.cook_method }}</span>
          </div>
        </div>
      </RouterLink>
    </div>

    <!-- 페이지네이션 -->
    <div v-if="lastPage > 1" class="flex justify-center items-center gap-2 mt-6">
      <button @click="changePage(page - 1)" :disabled="page === 1"
        class="px-3 py-1.5 rounded-lg bg-white border text-sm disabled:opacity-30">← 이전</button>
      <span class="text-sm text-gray-600">{{ page }} / {{ lastPage }}</span>
      <button @click="changePage(page + 1)" :disabled="page === lastPage"
        class="px-3 py-1.5 rounded-lg bg-white border text-sm disabled:opacity-30">다음 →</button>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'

const recipes = ref([])
const categories = ref([])
const selectedCat = ref('')
const search = ref('')
const page = ref(1)
const lastPage = ref(1)
const total = ref(0)
const loading = ref(true)

async function loadRecipes(p = 1) {
  loading.value = true
  page.value = p
  const params = { page: p, per_page: 20 }
  if (search.value) params.search = search.value
  if (selectedCat.value) params.category = selectedCat.value
  try {
    const { data } = await axios.get('/api/recipes', { params })
    recipes.value = data.data || []
    lastPage.value = data.last_page || 1
    total.value = data.total || 0
  } catch {}
  loading.value = false
}

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/recipes/categories')
    categories.value = data || []
  } catch {}
}

function selectCategory(cat) {
  selectedCat.value = cat
  loadRecipes(1)
}

function changePage(p) {
  if (p < 1 || p > lastPage.value) return
  loadRecipes(p)
}

onMounted(() => {
  loadCategories()
  loadRecipes()
})
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar { display: none; }
.scrollbar-hide { scrollbar-width: none; }
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
