<template>
  <DetailTemplate
    :item="recipe"
    :loading="loading"
    :images="recipe?.image_url ? [recipe.image_url] : []"
    :showAuthor="true"
    :showActions="true"
    :showComments="false"
    commentType="recipe"
    :breadcrumb="[{ label: '레시피', to: '/recipes' }, { label: recipe?.title_ko || recipe?.title || '' }]"
    @like="toggleLike"
    @bookmark="toggleBookmark"
  >
    <!-- Header: Recipe meta info -->
    <template #header>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <div class="flex items-center gap-2 mb-3 flex-wrap">
          <span v-if="recipe.category" class="text-xs bg-orange-100 text-orange-700 px-2.5 py-1 rounded-full font-medium">
            {{ typeof recipe.category === 'object' ? `${recipe.category.icon || ''} ${recipe.category.name}` : recipe.category }}
          </span>
          <span v-if="recipe.difficulty" :class="difficultyClass(recipe.difficulty)" class="text-xs px-2.5 py-1 rounded-full font-medium">
            {{ recipe.difficulty }}
          </span>
        </div>
        <h1 class="text-xl font-black text-gray-800 dark:text-white mb-2">{{ recipe.display_title || recipe.title_ko || recipe.title }}</h1>
        <p v-if="recipe.display_intro || recipe.intro_ko || recipe.intro"
          class="text-gray-600 dark:text-gray-300 text-sm leading-relaxed mb-4">
          {{ recipe.display_intro || recipe.intro_ko || recipe.intro }}
        </p>

        <!-- Meta tags -->
        <div class="flex flex-wrap gap-3 text-sm">
          <div v-if="recipe.cook_time" class="flex items-center gap-1.5 bg-gray-50 dark:bg-gray-700 rounded-xl px-3 py-2">
            <span>⏱</span><span class="font-medium text-gray-700 dark:text-gray-300">{{ recipe.cook_time }}</span>
          </div>
          <div v-if="recipe.servings" class="flex items-center gap-1.5 bg-gray-50 dark:bg-gray-700 rounded-xl px-3 py-2">
            <span>👥</span><span class="font-medium text-gray-700 dark:text-gray-300">{{ recipe.servings }}인분</span>
          </div>
          <div v-if="recipe.calories" class="flex items-center gap-1.5 bg-gray-50 dark:bg-gray-700 rounded-xl px-3 py-2">
            <span>🔥</span><span class="font-medium text-gray-700 dark:text-gray-300">{{ recipe.calories }}kcal</span>
          </div>
        </div>

        <!-- Language toggle -->
        <div class="flex gap-2 mt-4">
          <button @click="lang = 'ko'" class="px-3 py-1.5 rounded-lg text-xs font-medium transition"
            :class="lang === 'ko' ? 'bg-orange-500 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'">한글</button>
          <button @click="lang = 'en'" class="px-3 py-1.5 rounded-lg text-xs font-medium transition"
            :class="lang === 'en' ? 'bg-orange-500 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'">English</button>
        </div>
      </div>
    </template>

    <!-- Body: Ingredients + Steps -->
    <template #body>
      <!-- Ingredients -->
      <div class="mb-6">
        <h2 class="font-bold text-gray-800 dark:text-white mb-3 flex items-center gap-2">
          <span class="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs">🛒</span>
          재료 ({{ recipe.servings }}인분)
        </h2>
        <ul class="space-y-2">
          <li v-for="(ing, i) in currentIngredients" :key="i"
            class="flex items-center gap-2 text-sm py-2 border-b border-gray-50 dark:border-gray-700 last:border-0">
            <span class="w-2 h-2 rounded-full bg-orange-300 flex-shrink-0"></span>
            <span class="flex-1 text-gray-700 dark:text-gray-300">{{ typeof ing === 'object' ? ing.name : ing }}</span>
            <span v-if="ing.amount" class="text-gray-400 text-xs">{{ ing.amount }}</span>
          </li>
        </ul>
      </div>

      <!-- Steps -->
      <div>
        <h2 class="font-bold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
          <span class="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs">👨‍🍳</span>
          조리 순서
        </h2>
        <ol class="space-y-4">
          <li v-for="(step, i) in currentSteps" :key="i" class="flex gap-4">
            <div class="w-7 h-7 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
              {{ i + 1 }}
            </div>
            <p class="text-gray-700 dark:text-gray-300 text-sm leading-relaxed pt-0.5">
              {{ typeof step === 'object' ? (step.description || step.text) : step }}
            </p>
          </li>
        </ol>
      </div>
    </template>

    <!-- After body: Tips + Comments -->
    <template #after-body>
      <!-- Tips -->
      <div v-if="displayTips?.length" class="bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800 rounded-xl p-5">
        <h2 class="font-bold text-amber-800 dark:text-amber-300 mb-3">💡 요리 팁</h2>
        <ul class="space-y-2">
          <li v-for="(tip, i) in displayTips" :key="i" class="text-sm text-amber-700 dark:text-amber-400 flex gap-2">
            <span class="text-amber-400 flex-shrink-0">&#x2022;</span>
            <span>{{ tip }}</span>
          </li>
        </ul>
      </div>

      <!-- Comments -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
        <h3 class="font-bold text-gray-700 dark:text-white mb-4">댓글 {{ recipe.comments?.length || 0 }}</h3>
        <div v-for="c in recipe.comments" :key="c.id" class="border-b border-gray-50 dark:border-gray-700 py-3 last:border-0">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-7 h-7 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 font-bold text-xs">
              {{ (c.user?.name || '?').charAt(0) }}
            </div>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ c.user?.name }}</span>
            <span v-if="c.rating" class="text-yellow-400 text-sm">{{ '⭐'.repeat(c.rating) }}</span>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400 ml-9">{{ c.content }}</p>
        </div>

        <!-- Write comment -->
        <div class="mt-4 border-t border-gray-100 dark:border-gray-700 pt-4">
          <div class="flex gap-2 mb-2">
            <span class="text-sm text-gray-500">별점:</span>
            <span v-for="n in 5" :key="n" @click="commentRating = n" class="cursor-pointer text-lg"
              :class="n <= commentRating ? 'text-yellow-400' : 'text-gray-300'">★</span>
          </div>
          <textarea v-model="commentText" rows="3" placeholder="이 레시피 어떠셨나요?"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400 resize-none mb-2" />
          <div class="flex justify-end">
            <button @click="submitComment" :disabled="!commentText.trim()"
              class="bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white px-4 py-2 rounded-xl text-sm font-semibold transition">
              댓글 등록
            </button>
          </div>
        </div>
      </div>
    </template>

    <!-- Sidebar: Related recipes -->
    <template #sidebar>
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4">
        <h3 class="font-bold text-gray-800 dark:text-white text-sm mb-3">같은 카테고리 레시피</h3>
        <div v-if="sidebarRecipes.length === 0" class="text-center py-4 text-gray-400 text-sm">레시피가 없습니다</div>
        <div v-else class="space-y-3">
          <RouterLink v-for="item in sidebarRecipes" :key="item.id" :to="`/recipes/${item.id}`"
            class="block p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition border border-gray-100 dark:border-gray-600">
            <div class="flex items-start gap-3">
              <div class="w-14 h-14 rounded-lg bg-gray-100 dark:bg-gray-700 flex-shrink-0 overflow-hidden flex items-center justify-center">
                <img v-if="item.image_url" :src="item.image_url" class="w-full h-full object-cover"
                  @error="e => e.target.parentElement.innerHTML = '<span class=\'text-2xl\'>🍽️</span>'" />
                <span v-else class="text-2xl">🍽️</span>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-bold text-gray-800 dark:text-white truncate">{{ item.title_ko || item.title }}</p>
                <p class="text-xs text-gray-400">{{ item.cook_time }} · {{ item.servings }}인분</p>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>
    </template>
  </DetailTemplate>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DetailTemplate from '@/components/templates/DetailTemplate.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const recipe = ref(null)
const loading = ref(true)
const lang = ref('ko')
const commentText = ref('')
const commentRating = ref(0)
const sidebarRecipes = ref([])

const displayTips = computed(() => {
  if (!recipe.value) return []
  return recipe.value.display_tips || recipe.value.tips_ko || recipe.value.tips || []
})

const currentIngredients = computed(() => {
  if (!recipe.value) return []
  if (lang.value === 'ko') return recipe.value.display_ingredients || recipe.value.ingredients_ko || recipe.value.ingredients || []
  return recipe.value.ingredients || recipe.value.ingredients_ko || []
})

const currentSteps = computed(() => {
  if (!recipe.value) return []
  if (lang.value === 'ko') return recipe.value.display_steps || recipe.value.steps_ko || recipe.value.steps || []
  return recipe.value.steps || recipe.value.steps_ko || []
})

function difficultyClass(d) {
  if (d === '쉬움') return 'bg-green-100 text-green-700'
  if (d === '어려움') return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/recipes/${recipe.value.id}/like`)
    recipe.value.is_liked = data.liked
    recipe.value.like_count = data.like_count
  } catch {}
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/recipes/${recipe.value.id}/bookmark`)
    recipe.value.is_bookmarked = data.bookmarked
  } catch {}
}

async function submitComment() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post(`/api/recipes/${recipe.value.id}/comments`, {
      content: commentText.value,
      rating: commentRating.value || null,
    })
    if (!recipe.value.comments) recipe.value.comments = []
    recipe.value.comments.unshift(data.comment || data)
    commentText.value = ''
    commentRating.value = 0
  } catch {}
}

onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/recipes/${route.params.id}`)
    recipe.value = data
  } catch {
    recipe.value = null
  }

  if (recipe.value?.category) {
    const catName = typeof recipe.value.category === 'object' ? recipe.value.category.name : recipe.value.category
    try {
      const { data } = await axios.get('/api/recipes', { params: { category: catName, limit: 5 } })
      const items = data.data || data || []
      sidebarRecipes.value = items.filter(i => i.id !== recipe.value.id).slice(0, 5)
    } catch {}
  }

  loading.value = false
})
</script>
