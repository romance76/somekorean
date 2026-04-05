<template>
  <ListTemplate
    title="레시피"
    emoji="🍳"
    subtitle="미국 한인들의 요리 레시피 모음"
    :loading="loading"
    :items="recipes"
    :categories="categoryTabs"
    :activeCategory="activeCategory"
    :hasSearch="true"
    :searchQuery="search"
    searchPlaceholder="재료나 음식명 검색..."
    :sortOptions="difficultyOptions"
    :activeSort="difficulty"
    :hasViewToggle="false"
    :hasWrite="true"
    writeTo="/recipes/create"
    :pagination="pagination"
    :totalCount="pagination?.total || null"
    @category-change="onCategoryChange"
    @search="onSearch"
    @sort-change="onDifficultyChange"
    @page-change="loadRecipes"
  >
    <template #item-card="{ item }">
      <div @click="$router.push('/recipes/' + item.id)"
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden cursor-pointer hover:shadow-md transition group">
        <div class="flex sm:flex-col">
          <!-- Image -->
          <div class="w-28 sm:w-full sm:aspect-[4/3] bg-gray-100 dark:bg-gray-700 relative overflow-hidden flex-shrink-0">
            <img v-if="item.image_url" :src="item.image_url" :alt="item.title_ko || item.title"
              class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
              @error="e => { e.target.style.display='none' }" />
            <div v-if="!item.image_url" class="w-full h-full flex items-center justify-center bg-gradient-to-br from-orange-100 to-amber-50 text-4xl sm:text-5xl">🍽️</div>
            <span v-if="item.difficulty" :class="difficultyClass(item.difficulty)"
              class="absolute top-2 right-2 text-[10px] px-2 py-0.5 rounded-full font-medium">
              {{ item.difficulty }}
            </span>
          </div>
          <!-- Info -->
          <div class="p-3 flex-1 min-w-0">
            <h3 class="font-semibold text-gray-800 dark:text-white text-sm leading-snug line-clamp-2 mb-1.5">
              {{ item.title_ko || item.title }}
            </h3>
            <div v-if="item.category" class="text-xs text-gray-400 mb-1">
              {{ typeof item.category === 'object' ? item.category.name : item.category }}
            </div>
            <div class="flex items-center justify-between text-xs text-gray-400">
              <span v-if="item.cook_time">⏱ {{ item.cook_time }}</span>
              <span>❤️ {{ item.like_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #grid-card="{ item }">
      <div @click="$router.push('/recipes/' + item.id)"
        class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden cursor-pointer hover:shadow-md transition group">
        <div class="relative bg-gray-100 dark:bg-gray-700 overflow-hidden" style="aspect-ratio:4/3">
          <img v-if="item.image_url" :src="item.image_url" :alt="item.title_ko || item.title"
            class="w-full h-full object-cover group-hover:scale-105 transition duration-300"
            @error="e => { e.target.style.display='none' }" />
          <div v-if="!item.image_url" class="w-full h-full flex items-center justify-center bg-gradient-to-br from-orange-100 to-amber-50 text-5xl">🍽️</div>
          <span v-if="item.difficulty" :class="difficultyClass(item.difficulty)"
            class="absolute top-2 right-2 text-xs px-2 py-0.5 rounded-full font-medium">
            {{ item.difficulty }}
          </span>
        </div>
        <div class="p-3">
          <h3 class="font-semibold text-gray-800 dark:text-white text-sm leading-snug line-clamp-2 mb-2">{{ item.title_ko || item.title }}</h3>
          <div class="flex items-center justify-between text-xs text-gray-400">
            <span v-if="item.cook_time">⏱ {{ item.cook_time }}</span>
            <span>❤️ {{ item.like_count || 0 }}</span>
          </div>
        </div>
      </div>
    </template>

    <template #empty>
      <div class="text-center py-16 bg-white dark:bg-gray-800 rounded-xl">
        <p class="text-4xl mb-3">🍽️</p>
        <p class="text-gray-400 text-sm">레시피가 없습니다</p>
      </div>
    </template>
  </ListTemplate>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ListTemplate from '@/components/templates/ListTemplate.vue'
import axios from 'axios'

const loading = ref(true)
const recipes = ref([])
const categories = ref([])
const activeCategory = ref('')
const search = ref('')
const difficulty = ref('')
const pagination = ref(null)

const categoryTabs = ref([{ value: '', label: '전체' }])

const difficultyOptions = [
  { value: '', label: '난이도 전체' },
  { value: '쉬움', label: '쉬움' },
  { value: '보통', label: '보통' },
  { value: '어려움', label: '어려움' },
]

function difficultyClass(d) {
  if (d === '쉬움') return 'bg-green-100 text-green-700'
  if (d === '어려움') return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

function onCategoryChange(val) { activeCategory.value = val; loadRecipes(1) }
function onSearch(val) { search.value = val; loadRecipes(1) }
function onDifficultyChange(val) { difficulty.value = val; loadRecipes(1) }

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/recipes/categories')
    categories.value = data
    categoryTabs.value = [
      { value: '', label: '전체' },
      ...data.map(c => ({ value: c.key || c.id, label: `${c.icon || ''} ${c.name}`.trim() }))
    ]
  } catch {}
}

async function loadRecipes(page = 1) {
  loading.value = true
  try {
    const params = { page }
    if (activeCategory.value) params.category = activeCategory.value
    if (search.value) params.search = search.value
    if (difficulty.value) params.difficulty = difficulty.value
    const { data } = await axios.get('/api/recipes', { params })
    recipes.value = data.data || data || []
    pagination.value = data.data ? {
      current_page: data.current_page,
      last_page: data.last_page,
      total: data.total,
    } : null
  } catch {
    recipes.value = []
  }
  loading.value = false
}

onMounted(async () => {
  await loadCategories()
  await loadRecipes()
})
</script>
