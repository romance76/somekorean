<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[900px] mx-auto px-4 pt-4">
      <div v-if="loading" class="text-center py-16 text-gray-400">불러오는 중...</div>

      <template v-else-if="recipe">
        <button @click="$router.back()" class="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-4 transition">
          ← 목록으로
        </button>

        <div class="bg-white rounded-2xl shadow-sm overflow-hidden mb-4">
          <!-- 대표 이미지 -->
          <div v-if="recipe.image_url" class="relative">
            <img :src="recipe.image_url" :alt="recipe.title" class="w-full object-cover" style="max-height: clamp(200px, 50vw, 420px)" />
            <div v-if="recipe.image_credit" class="absolute bottom-2 right-3 text-xs text-white bg-black/40 px-2 py-0.5 rounded">
              {{ recipe.image_credit }}
            </div>
          </div>
          <div v-else class="bg-gradient-to-br from-orange-100 to-amber-50 flex items-center justify-center" style="height:220px">
            <span class="text-7xl">🍽️</span>
          </div>

          <div class="p-5">
            <!-- 카테고리 + 제목 -->
            <div class="flex items-center gap-2 mb-2">
              <span v-if="recipe.category" class="text-xs px-2.5 py-1 bg-orange-50 text-orange-700 rounded-full font-medium">
                {{ recipe.category.icon }} {{ recipe.category.name }}
              </span>
              <span :class="difficultyClass(recipe.difficulty)" class="text-xs px-2.5 py-1 rounded-full font-medium">{{ recipe.difficulty }}</span>
            </div>
            <h1 class="text-xl font-black text-gray-900 mb-2">{{ recipe.title }}</h1>
            <p v-if="recipe.intro" class="text-gray-600 text-sm leading-relaxed mb-4">{{ recipe.intro }}</p>

            <!-- 정보 태그 -->
            <div class="flex flex-wrap gap-2 sm:gap-3 mb-4 text-sm">
              <div class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                <span>⏱</span><span class="font-medium">{{ recipe.cook_time }}</span>
              </div>
              <div v-if="recipe.calories" class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                <span>🔥</span><span class="font-medium">{{ recipe.calories }}kcal</span>
              </div>
              <div class="flex items-center gap-1.5 bg-gray-50 rounded-xl px-3 py-2">
                <span>👥</span><span class="font-medium">{{ recipe.servings }}인분</span>
              </div>
            </div>

            <!-- 좋아요/북마크 -->
            <div class="flex flex-wrap gap-2 sm:gap-3 mb-4">
              <button @click="toggleLike" :class="recipe.is_liked ? 'bg-red-50 text-red-500 border-red-200' : 'bg-gray-50 text-gray-500 border-gray-200'"
                class="flex items-center gap-2 border px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl text-sm font-medium transition hover:scale-105">
                ❤️ {{ recipe.like_count || 0 }}
              </button>
              <button @click="toggleBookmark" :class="recipe.is_bookmarked ? 'bg-amber-50 text-amber-600 border-amber-200' : 'bg-gray-50 text-gray-500 border-gray-200'"
                class="flex items-center gap-2 border px-3 sm:px-4 py-1.5 sm:py-2 rounded-xl text-sm font-medium transition hover:scale-105">
                🔖 저장
              </button>
            </div>

            <!-- 태그 -->
            <div v-if="recipe.tags?.length" class="flex flex-wrap gap-1.5 mb-5">
              <span v-for="tag in recipe.tags" :key="tag" class="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full">#{{ tag }}</span>
            </div>
          </div>
        </div>

        <!-- 재료 -->
        <div class="bg-white rounded-2xl shadow-sm p-5 mb-4">
          <h2 class="font-bold text-gray-800 mb-3 flex items-center gap-2">
            <span class="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs">🛒</span>
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
            <span class="w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs">👨‍🍳</span>
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
          <h2 class="font-bold text-amber-800 mb-3">💡 요리 팁</h2>
          <ul class="space-y-2">
            <li v-for="(tip, i) in recipe.tips" :key="i" class="text-sm text-amber-700 flex gap-2">
              <span class="text-amber-400 flex-shrink-0">•</span>
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
              <span v-if="c.rating" class="text-yellow-400 text-sm">{{ '⭐'.repeat(c.rating) }}</span>
            </div>
            <p class="text-sm text-gray-600 ml-9">{{ c.content }}</p>
          </div>
          <!-- 댓글 작성 -->
          <div class="mt-4">
            <div class="flex gap-2 mb-2">
              <span class="text-sm text-gray-500">별점:</span>
              <span v-for="n in 5" :key="n" @click="commentRating = n" class="cursor-pointer text-lg"
                :class="n <= commentRating ? 'text-yellow-400' : 'text-gray-300'">★</span>
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

function difficultyClass(d) {
  if (d === '쉬움') return 'bg-green-100 text-green-700'
  if (d === '어려움') return 'bg-red-100 text-red-700'
  return 'bg-yellow-100 text-yellow-700'
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

onMounted(load)
</script>
