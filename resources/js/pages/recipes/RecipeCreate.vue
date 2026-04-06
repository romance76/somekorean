<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">🍳 레시피 등록</h1>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">제목 (한글)</label><input v-model="form.title" type="text" placeholder="예: 김치찌개 만들기" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">Title (English)</label><input v-model="form.title_ko" type="text" placeholder="Kimchi Jjigae" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">카테고리</label>
          <select v-model="form.category_id" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none">
            <option value="">선택</option><option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select></div>
        <div><label class="text-sm font-semibold text-gray-700">난이도</label>
          <select v-model="form.difficulty" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none">
            <option value="easy">쉬움</option><option value="medium">보통</option><option value="hard">어려움</option>
          </select></div>
      </div>
      <div class="grid grid-cols-3 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">인분</label><input v-model.number="form.servings" type="number" min="1" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">준비 시간(분)</label><input v-model.number="form.prep_time" type="number" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">조리 시간(분)</label><input v-model.number="form.cook_time" type="number" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div><label class="text-sm font-semibold text-gray-700">설명</label><textarea v-model="form.content" rows="4" placeholder="레시피에 대한 간단한 소개" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none resize-none"></textarea></div>
      <div><label class="text-sm font-semibold text-gray-700">재료 (한 줄에 하나씩)</label><textarea v-model="ingredientsText" rows="5" placeholder="돼지고기 300g&#10;김치 2컵&#10;두부 1모&#10;고추장 1큰술" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none resize-none font-mono"></textarea></div>
      <div><label class="text-sm font-semibold text-gray-700">조리 순서 (한 줄에 하나씩)</label><textarea v-model="stepsText" rows="5" placeholder="1. 재료를 준비합니다&#10;2. 김치를 볶습니다&#10;3. 물을 넣고 끓입니다&#10;4. 두부를 넣고 5분 더 끓입니다" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none resize-none font-mono"></textarea></div>
      <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
      <div class="flex gap-3 pt-2">
        <button @click="submit" :disabled="submitting" class="bg-amber-400 text-amber-900 font-bold px-6 py-2.5 rounded-lg hover:bg-amber-500 disabled:opacity-50">{{ submitting ? '등록 중...' : '레시피 등록' }}</button>
        <button @click="$router.back()" class="text-gray-500 px-6 py-2.5">취소</button>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const form = reactive({ title:'',title_ko:'',content:'',category_id:'',difficulty:'medium',servings:2,prep_time:10,cook_time:20 })
const ingredientsText = ref('')
const stepsText = ref('')
const categories = ref([])
const error = ref('')
const submitting = ref(false)
async function submit() {
  if (!form.title || !form.content) { error.value = '제목과 설명을 입력해주세요'; return }
  submitting.value = true; error.value = ''
  try {
    const payload = { ...form, ingredients: ingredientsText.value.split('\n').filter(Boolean), steps: stepsText.value.split('\n').filter(Boolean) }
    const { data } = await axios.post('/api/recipes', payload)
    router.push(`/recipes/${data.data.id}`)
  } catch (e) { error.value = e.response?.data?.message || '등록 실패' }
  submitting.value = false
}
onMounted(async () => { try { const { data } = await axios.get('/api/recipes/categories'); categories.value = data.data || [] } catch {} })
</script>
