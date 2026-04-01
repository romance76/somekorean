<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <div v-if="loading" class="text-center py-16 text-gray-400">불러오는 중...</div>

      <template v-else-if="recipe">

        <!-- Color Header -->
        <div class="bg-gradient-to-r from-rose-500 to-pink-500 text-white px-6 py-4 rounded-2xl mb-4">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <button @click="router.push('/recipes')" class="text-rose-200 text-sm hover:text-white transition">&larr; 레시피 목록</button>
              <span v-if="recipe.category" class="bg-white/20 text-xs px-3 py-1 rounded-full">{{ recipe.category.icon }} {{ recipe.category.name }}</span>
              <span v-if="recipe.difficulty" :class="difficultyBadgeClass(recipe.difficulty)" class="text-xs px-3 py-1 rounded-full">{{ recipe.difficulty }}</span>
            </div>
            <div class="flex items-center gap-2">
              <button @click="shareRecipe" class="flex items-center gap-1 text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
                공유
              </button>
              <button @click="toggleBookmark" :class="recipe.is_bookmarked ? 'bg-yellow-400/30' : 'bg-white/10 hover:bg-white/20'" class="flex items-center gap-1 text-xs text-white/80 hover:text-white px-3 py-1.5 rounded-lg transition">
                <svg class="w-3.5 h-3.5" :fill="recipe.is_bookmarked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/></svg>
                북마크
              </button>
            </div>
          </div>
          <h1 class="text-lg sm:text-xl font-black leading-tight">{{ recipe.title }}</h1>
          <div class="flex items-center gap-2 mt-2 text-sm text-rose-100">
            <span v-if="recipe.cook_time">&#x23F1; {{ recipe.cook_time }}</span>
            <span v-if="recipe.cook_time && recipe.servings">·</span>
            <span v-if="recipe.servings">{{ recipe.servings }}인분</span>
            <span v-if="recipe.user">·</span>
            <span v-if="recipe.user" class="font-medium">{{ recipe.user.name }}</span>
          </div>
        </div>

        <!-- 2-Column Layout -->
        <div class="flex gap-5 items-start">

          <!-- Left: Main Content -->
          <div class="flex-1 min-w-0">

            <!-- Hero Image + Content Card -->
            <div class="bg-white rounded-2xl shadow-sm overflow-hidden mb-4">
              <!-- 대표 이미지 -->
              <div v-if="recipe.image_url" class="relative">
                <img :src="recipe.image_url" :alt="recipe.title" class="w-full object-cover" style="max-height:420px" />
                <div v-if="recipe.image_credit" class="absolute bottom-2 right-3 text-xs text-white bg-black/40 px-2 py-0.5 rounded">
                  {{ recipe.image_credit }}
                </div>
              </div>
              <div v-else class="bg-gradient-to-br from-orange-100 to-amber-50 flex items-center justify-center" style="height:220px">
                <span class="text-7xl">&#x1F37D;&#xFE0F;</span>
              </div>

              <div class="p-5">
                <p v-if="recipe.intro" class="text-gray-600 text-sm leading-relaxed mb-4">{{ recipe.intro }}</p>

                <!-- 정보 태그 -->
                <div class="flex flex-wrap gap-3 mb-4 text-sm">
                  <div class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                    <span>&#x23F1;</span><span class="font-medium">{{ recipe.cook_time }}</span>
                  </div>
                  <div v-if="recipe.calories" class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                    <span>&#x1F525;</span><span class="font-medium">{{ recipe.calories }}kcal</span>
                  </div>
                  <div class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                    <span>&#x1F465;</span><span class="font-medium">{{ recipe.servings }}인분</span>
                  </div>
                </div>

                <!-- 좋아요/북마크 -->
                <div class="flex flex-wrap gap-3 mb-4">
                  <button @click="toggleLike" :class="recipe.is_liked ? 'bg-red-50 text-red-500 border-red-200' : 'bg-gray-50 text-gray-500 border-gray-200'"
                    class="flex items-center gap-2 border px-4 py-2 rounded-xl text-sm font-medium transition hover:scale-105">
                    &#x2764;&#xFE0F; {{ recipe.like_count || 0 }}
                  </button>
                </div>

                <!-- 태그 -->
                <div v-if="recipe.tags?.length" class="flex flex-wrap gap-1.5 mb-2">
                  <span v-for="tag in recipe.tags" :key="tag" class="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full">#{{ tag }}</span>
                </div>
              </div>
            </div>

            <!-- 재료 -->
            <div class="bg-white rounded-2xl shadow-sm p-5 mb-4">
              <h2 class="font-bold text-gray-800 mb-3 flex items-center gap-2">
                <span class="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs">&#x1F6D2;</span>
                재료 ({{ recipe.servings }}인분)
              </h2>
              <ul class="space-y-2">
                <li v-for="(ing, i) in recipe.ingredients" :key="i"
                  class="flex items-center gap-2 text-sm py-2 border-b border-gray-50 last:border-0">
                  <span class="w-2 h-2 rounded-full bg-orange-300 flex-shrink-0"></span>
                  <span class="flex-1 text-gray-700">{{ typeof ing === 'object' ? ing.name : ing }}</span>
                  <span v-if="ing.amount" class="text-gray-400 text-xs">{{ ing.amount }}</span>
                </li>
              </ul>
            </div>

            <!-- 조리 순서 -->
            <div class="bg-white rounded-2xl shadow-sm p-5 mb-4">
              <h2 class="font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span class="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs">&#x1F468;&#x200D;&#x1F373;</span>
                조리 순서
              </h2>
              <ol class="space-y-4">
                <li v-for="(step, i) in recipe.steps" :key="i" class="flex gap-4">
                  <div class="w-7 h-7 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                    {{ i + 1 }}
                  </div>
                  <p class="text-gray-700 text-sm leading-relaxed pt-0.5">{{ typeof step === 'object' ? step.description : step }}</p>
                </li>
              </ol>
            </div>

            <!-- 팁 -->
            <div v-if="recipe.tips?.length" class="bg-amber-50 border border-amber-100 rounded-2xl p-5 mb-4">
              <h2 class="font-bold text-amber-800 mb-3">&#x1F4A1; 요리 팁</h2>
              <ul class="space-y-2">
                <li v-for="(tip, i) in recipe.tips" :key="i" class="text-sm text-amber-700 flex gap-2">
                  <span class="text-amber-400 flex-shrink-0">&#x2022;</span>
                  <span>{{ tip }}</span>
                </li>
              </ul>
            </div>

            <!-- 댓글 -->
            <div class="bg-white rounded-2xl shadow-sm p-5">
              <h3 class="font-bold text-gray-700 mb-4">댓글 {{ recipe.comments?.length || 0 }}</h3>
              <div v-for="c in recipe.comments" :key="c.id" class="border-b border-gray-50 py-3 last:border-0">
                <div class="flex items-center gap-2 mb-1">
                  <div class="w-7 h-7 rounded-full bg-orange-100 flex items-center justify-center text-orange-600 font-bold text-xs">
                    {{ (c.user?.name || '?').charAt(0) }}
                  </div>
                  <span class="text-sm font-medium text-gray-700">{{ c.user?.name }}</span>
                  <span v-if="c.rating" class="text-yellow-400 text-sm">{{ '&#x2B50;'.repeat(c.rating) }}</span>
                </div>
                <p class="text-sm text-gray-600 ml-9">{{ c.content }}</p>
              </div>
              <!-- 댓글 작성 -->
              <div class="mt-4">
                <div class="flex gap-2 mb-2">
                  <span class="text-sm text-gray-500">별점:</span>
                  <span v-for="n in 5" :key="n" @click="commentRating = n" class="cursor-pointer text-lg"
                    :class="n <= commentRating ? 'text-yellow-400' : 'text-gray-300'">&#x2605;</span>
                </div>
                <textarea v-model="commentText" rows="3" placeholder="이 레시피 어떠셨나요?"
                  class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-orange-400 resize-none mb-2" />
                <div class="flex justify-end">
                  <button @click="submitComment" :disabled="!commentText.trim()"
                    class="bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white px-4 py-2 rounded-xl text-sm font-semibold transition">
                    댓글 등록
                  </button>
                </div>
              </div>
            </div>

          </div>

          <!-- Right: Sidebar (desktop only) -->
          <div class="hidden lg:block flex-shrink-0 sticky top-4" style="width:320px">
            <div class="bg-white rounded-2xl shadow-sm p-4">
              <h3 class="font-bold text-gray-800 text-sm mb-3">같은 카테고리 레시피</h3>
              <div v-if="sidebarRecipes.length === 0" class="text-center py-4 text-gray-400 text-sm">레시피가 없습니다</div>
              <div v-else class="space-y-3">
                <router-link v-for="item in sidebarRecipes" :key="item.id" :to="`/recipes/${item.id}`"
                  class="block p-3 rounded-xl hover:bg-gray-50 transition border border-gray-100">
                  <div class="flex items-start gap-3">
                    <div class="w-16 h-16 rounded-lg bg-gray-100 flex-shrink-0 overflow-hidden flex items-center justify-center">
                      <img v-if="item.image_url" :src="item.image_url" class="w-full h-full object-cover" />
                      <span v-else class="text-2xl text-gray-300">&#x1F37D;&#xFE0F;</span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-bold text-gray-800 truncate">{{ item.title }}</p>
                      <p class="text-xs text-rose-500 font-medium">{{ item.difficulty }}</p>
                      <p class="text-xs text-gray-400">{{ item.cook_time }} · {{ item.servings }}인분</p>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>

        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const recipe = ref(null)
const loading = ref(true)
const commentText = ref('')
const commentRating = ref(0)
const sidebarRecipes = ref([])

function difficultyClass(d) {
  if (d === '쉬움') return 'bg-green-100 text-green-700'
  if (d === '어려움') return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
}

function difficultyBadgeClass(d) {
  if (d === '쉬움') return 'bg-green-400/30 text-white'
  if (d === '어려움') return 'bg-red-400/30 text-white'
  return 'bg-yellow-400/30 text-white'
}

function shareRecipe() {
  if (navigator.share) {
    navigator.share({ title: recipe.value.title, url: window.location.href })
  } else {
    navigator.clipboard.writeText(window.location.href)
    alert('링크가 복사되었습니다!')
  }
}

async function load() {
  try {
    const { data } = await axios.get('/api/recipes/' + route.params.id)
    recipe.value = data
  } catch { recipe.value = null }
  finally { loading.value = false }
}

async function toggleLike() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post('/api/recipes/' + recipe.value.id + '/like')
    recipe.value.is_liked = data.liked
    recipe.value.like_count = data.like_count
  } catch {}
}

async function toggleBookmark() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post('/api/recipes/' + recipe.value.id + '/bookmark')
    recipe.value.is_bookmarked = data.bookmarked
  } catch {}
}

async function submitComment() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    const { data } = await axios.post('/api/recipes/' + recipe.value.id + '/comments', { content: commentText.value, rating: commentRating.value || null })
    if (!recipe.value.comments) recipe.value.comments = []
    recipe.value.comments.unshift(data.comment)
    commentText.value = ''
    commentRating.value = 0
  } catch {}
}

onMounted(async () => {
  await load()

  // Load sidebar: same category recipes
  if (recipe.value?.category) {
    const catName = typeof recipe.value.category === 'object' ? recipe.value.category.name : recipe.value.category
    try {
      const { data } = await axios.get('/api/recipes', { params: { category: catName, limit: 5 } })
      const items = data.data || data || []
      sidebarRecipes.value = items.filter(i => i.id !== recipe.value.id).slice(0, 5)
    } catch {
      sidebarRecipes.value = []
    }
  }
})
</script>
