<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-2xl mx-auto px-4 pt-4">

      <!-- 헤더 -->
      <div class="flex items-center gap-3 mb-5">
        <button @click="$router.back()" class="p-2 rounded-xl bg-white border text-gray-500 hover:bg-gray-50">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <div>
          <h1 class="text-xl font-black text-gray-800">레시피 올리기</h1>
          <p class="text-xs text-gray-400">나만의 요리 레시피를 공유해보세요</p>
        </div>
      </div>

      <!-- Step bar -->
      <div class="flex gap-1.5 mb-2">
        <div v-for="s in 4" :key="s" @click="s < step ? step=s : null"
          :class="['flex-1 h-1.5 rounded-full transition', s <= step ? 'bg-orange-500' : 'bg-gray-200']"></div>
      </div>
      <p class="text-xs text-center text-gray-400 mb-5">
        {{ ['기본 정보', '재료', '조리 순서', '마무리'][step-1] }} {{ step }}/4
      </p>

      <!-- ── STEP 1: 기본 정보 ── -->
      <div v-if="step === 1" class="space-y-4">

        <!-- 대표 사진 -->
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <p class="text-sm font-semibold text-gray-700 mb-3">대표 사진</p>
          <div v-if="!form.image_url"
            class="w-full h-48 border-2 border-dashed border-gray-200 rounded-xl flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-orange-400 transition relative"
            @click="$refs.imgInput.click()">
            <div v-if="uploadingImg" class="absolute inset-0 bg-white/80 rounded-xl flex items-center justify-center">
              <div class="animate-spin w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full"></div>
            </div>
            <div class="text-4xl">📸</div>
            <p class="text-sm text-gray-400">클릭하여 사진 업로드</p>
            <p class="text-xs text-gray-300">JPG, PNG, WEBP (최대 5MB)</p>
          </div>
          <div v-else class="relative">
            <img :src="form.image_url" class="w-full h-48 object-cover rounded-xl"/>
            <button @click="form.image_url=''" class="absolute top-2 right-2 bg-black/50 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm hover:bg-black/70">✕</button>
          </div>
          <input ref="imgInput" type="file" accept="image/*" class="hidden" @change="uploadImage"/>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-4 space-y-4">
          <!-- 제목 -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">
              요리 이름 <span class="text-red-500">*</span>
            </label>
            <input v-model="form.title" type="text" placeholder="예: 김치찌개, 불고기 덮밥..." maxlength="100"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-orange-400"/>
          </div>

          <!-- 카테고리 -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              카테고리 <span class="text-red-500">*</span>
            </label>
            <div class="flex flex-wrap gap-2">
              <button v-for="cat in categories" :key="cat.id"
                @click="form.category_id = cat.id"
                :class="['px-3 py-1.5 rounded-full text-sm border transition', form.category_id === cat.id
                  ? 'bg-orange-500 text-white border-orange-500'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-orange-300']">
                {{ cat.icon }} {{ cat.name }}
              </button>
            </div>
          </div>

          <!-- 소개 -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">간단 소개</label>
            <textarea v-model="form.intro" rows="3" maxlength="300"
              placeholder="이 요리에 대해 간단히 소개해주세요..."
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-orange-400 resize-none"></textarea>
          </div>
        </div>

        <!-- 기본 정보 -->
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <p class="text-sm font-semibold text-gray-700 mb-3">기본 정보</p>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">난이도</label>
              <select v-model="form.difficulty" class="w-full border border-gray-200 rounded-xl px-2 py-2.5 text-sm focus:outline-none focus:border-orange-400">
                <option value="">선택</option>
                <option value="쉬움">😊 쉬움</option>
                <option value="보통">😐 보통</option>
                <option value="어려움">😤 어려움</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">조리 시간</label>
              <select v-model="form.cook_time" class="w-full border border-gray-200 rounded-xl px-2 py-2.5 text-sm focus:outline-none focus:border-orange-400">
                <option value="">선택</option>
                <option value="10분 이내">10분 이내</option>
                <option value="15분">15분</option>
                <option value="30분">30분</option>
                <option value="45분">45분</option>
                <option value="1시간">1시간</option>
                <option value="1시간 이상">1시간+</option>
              </select>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">인분</label>
              <select v-model="form.servings" class="w-full border border-gray-200 rounded-xl px-2 py-2.5 text-sm focus:outline-none focus:border-orange-400">
                <option :value="1">1인분</option>
                <option :value="2">2인분</option>
                <option :value="3">3인분</option>
                <option :value="4">4인분</option>
                <option :value="6">6인분</option>
                <option :value="8">8인분+</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- ── STEP 2: 재료 ── -->
      <div v-if="step === 2" class="space-y-4">
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700">재료 목록</p>
            <span class="text-xs text-gray-400">{{ form.ingredients.length }}개</span>
          </div>
          <div class="space-y-2 mb-3">
            <div v-for="(ing, i) in form.ingredients" :key="i" class="flex gap-2 items-center">
              <input v-model="ing.name" type="text" placeholder="재료명" maxlength="50"
                class="flex-1 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-orange-400"/>
              <input v-model="ing.amount" type="text" placeholder="양 (예: 1컵)" maxlength="30"
                class="w-28 border border-gray-200 rounded-xl px-3 py-2.5 text-sm focus:outline-none focus:border-orange-400"/>
              <button @click="form.ingredients.splice(i,1)" class="text-gray-300 hover:text-red-400 text-xl leading-none flex-shrink-0 pb-0.5">×</button>
            </div>
          </div>
          <button @click="form.ingredients.push({name:'',amount:''})"
            class="w-full border-2 border-dashed border-gray-200 rounded-xl py-2.5 text-sm text-gray-400 hover:border-orange-400 hover:text-orange-500 transition">
            + 재료 추가
          </button>
        </div>

        <!-- 빠른 추가 -->
        <div class="bg-orange-50 rounded-2xl p-4 border border-orange-100">
          <p class="text-xs font-semibold text-orange-600 mb-2">자주 쓰는 재료 빠른 추가</p>
          <div class="flex flex-wrap gap-2">
            <button v-for="item in quickIngredients" :key="item"
              @click="form.ingredients.push({name:item, amount:''})"
              class="px-2.5 py-1 bg-white border border-orange-200 rounded-full text-xs text-orange-700 hover:bg-orange-100 transition">
              + {{ item }}
            </button>
          </div>
        </div>
      </div>

      <!-- ── STEP 3: 조리 순서 ── -->
      <div v-if="step === 3" class="space-y-4">
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <div class="flex items-center justify-between mb-3">
            <p class="text-sm font-semibold text-gray-700">조리 순서</p>
            <span class="text-xs text-gray-400">{{ form.steps.length }}단계</span>
          </div>
          <div class="space-y-3 mb-3">
            <div v-for="(st, i) in form.steps" :key="i" class="flex gap-3">
              <div class="flex-shrink-0 w-7 h-7 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs font-bold mt-2.5">{{ i+1 }}</div>
              <div class="flex-1">
                <textarea v-model="st.text" rows="2" :placeholder="(i+1) + '번째 순서를 입력하세요'" maxlength="400"
                  class="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400 resize-none"></textarea>
              </div>
              <button @click="form.steps.splice(i,1)" class="text-gray-300 hover:text-red-400 text-xl leading-none flex-shrink-0 mt-2.5">×</button>
            </div>
          </div>
          <button @click="form.steps.push({text:''})"
            class="w-full border-2 border-dashed border-gray-200 rounded-xl py-2.5 text-sm text-gray-400 hover:border-orange-400 hover:text-orange-500 transition">
            + 단계 추가
          </button>
        </div>
      </div>

      <!-- ── STEP 4: 마무리 ── -->
      <div v-if="step === 4" class="space-y-4">
        <!-- 태그 -->
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <p class="text-sm font-semibold text-gray-700 mb-2">태그</p>
          <div class="flex gap-2 mb-2 flex-wrap">
            <span v-for="(tag, i) in form.tags" :key="i"
              class="flex items-center gap-1 bg-orange-100 text-orange-700 rounded-full px-3 py-1 text-sm">
              #{{ tag }}
              <button @click="form.tags.splice(i,1)" class="hover:text-red-500 ml-0.5">×</button>
            </span>
          </div>
          <div class="flex gap-2">
            <input v-model="tagInput" type="text" placeholder="태그 입력 후 엔터 (예: 한식, 간단요리)"
              @keyup.enter="addTag" maxlength="20"
              class="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400"/>
            <button @click="addTag" class="bg-orange-100 text-orange-600 px-4 py-2 rounded-xl text-sm font-medium hover:bg-orange-200 transition">추가</button>
          </div>
        </div>

        <!-- 팁 -->
        <div class="bg-white rounded-2xl shadow-sm p-4">
          <p class="text-sm font-semibold text-gray-700 mb-2">요리 팁 (선택)</p>
          <div class="space-y-2 mb-2">
            <div v-for="(tip, i) in form.tips" :key="i" class="flex gap-2">
              <input v-model="form.tips[i]" type="text" placeholder="예: 고추장은 청양고추장을 쓰면 더 맛있어요" maxlength="200"
                class="flex-1 border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-orange-400"/>
              <button @click="form.tips.splice(i,1)" class="text-gray-300 hover:text-red-400 text-xl">×</button>
            </div>
          </div>
          <button @click="form.tips.push('')"
            class="w-full border-2 border-dashed border-gray-200 rounded-xl py-2.5 text-sm text-gray-400 hover:border-orange-400 hover:text-orange-500 transition">
            + 팁 추가
          </button>
        </div>

        <!-- 미리보기 -->
        <div class="bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl p-4 border border-orange-100">
          <p class="text-sm font-bold text-gray-700 mb-3">게시물 미리보기</p>
          <div class="flex gap-3 bg-white rounded-xl p-3">
            <div class="w-20 h-20 bg-gray-100 rounded-xl overflow-hidden flex-shrink-0">
              <img v-if="form.image_url" :src="form.image_url" class="w-full h-full object-cover"/>
              <div v-else class="w-full h-full flex items-center justify-center text-3xl">🍳</div>
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-bold text-gray-800 truncate">{{ form.title || '제목 없음' }}</p>
              <p class="text-xs text-gray-400 mt-0.5">{{ categoryName }}</p>
              <div class="flex gap-1.5 mt-2 flex-wrap">
                <span v-if="form.difficulty" class="text-xs bg-gray-100 rounded-full px-2 py-0.5">{{ form.difficulty }}</span>
                <span v-if="form.cook_time" class="text-xs bg-gray-100 rounded-full px-2 py-0.5">{{ form.cook_time }}</span>
                <span v-if="form.servings" class="text-xs bg-gray-100 rounded-full px-2 py-0.5">{{ form.servings }}인분</span>
              </div>
              <p class="text-xs text-gray-400 mt-1">재료 {{ form.ingredients.filter(i=>i.name).length }}가지 · {{ form.steps.filter(s=>s.text).length }}단계</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 에러 -->
      <div v-if="error" class="mt-4 bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-600">
        {{ error }}
      </div>

      <!-- 버튼 -->
      <div class="mt-6 flex gap-3">
        <button v-if="step > 1" @click="step--"
          class="flex-1 border border-gray-200 bg-white text-gray-600 py-3.5 rounded-2xl font-semibold text-sm hover:bg-gray-50 transition">
          이전
        </button>
        <button v-if="step < 4" @click="nextStep"
          class="flex-1 bg-orange-500 text-white py-3.5 rounded-2xl font-semibold text-sm hover:bg-orange-600 transition shadow-sm">
          다음
        </button>
        <button v-if="step === 4" @click="submit" :disabled="submitting"
          :class="['flex-1 py-3.5 rounded-2xl font-bold text-sm transition shadow-sm flex items-center justify-center gap-2',
            submitting ? 'bg-orange-300 text-white cursor-not-allowed' : 'bg-orange-500 text-white hover:bg-orange-600']">
          <div v-if="submitting" class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
          {{ submitting ? '등록 중...' : '레시피 올리기' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const step = ref(1)
const submitting = ref(false)
const uploadingImg = ref(false)
const error = ref('')
const tagInput = ref('')
const categories = ref([])

const form = ref({
  title: '',
  intro: '',
  category_id: null,
  difficulty: '',
  cook_time: '',
  servings: 2,
  image_url: '',
  ingredients: [{ name: '', amount: '' }],
  steps: [{ text: '' }],
  tips: [],
  tags: [],
})

const quickIngredients = [
  '소금','설탕','간장','고추장','된장','참기름','마늘','생강','대파','양파',
  '계란','두부','돼지고기','소고기','닭고기','김치','쌀','당면','깻잎','들기름',
  '식용유','후추','다진마늘','고춧가루','참깨','굴소스','미림','청주'
]

const categoryName = computed(() => {
  const cat = categories.value.find(c => c.id === form.value.category_id)
  return cat ? cat.icon + ' ' + cat.name : ''
})

async function loadCategories() {
  try {
    const { data } = await axios.get('/api/recipes/categories')
    categories.value = data
  } catch {}
}

async function uploadImage(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { error.value = '이미지는 5MB 이하만 가능합니다.'; return }
  uploadingImg.value = true
  error.value = ''
  try {
    const fd = new FormData()
    fd.append('image', file)
    const { data } = await axios.post('/api/recipes/image', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    form.value.image_url = data.url
  } catch {
    error.value = '이미지 업로드에 실패했습니다. 다시 시도해주세요.'
  } finally {
    uploadingImg.value = false
  }
}

function addTag() {
  const t = tagInput.value.trim().replace(/^#/, '')
  if (t && !form.value.tags.includes(t) && form.value.tags.length < 10) {
    form.value.tags.push(t)
  }
  tagInput.value = ''
}

function nextStep() {
  error.value = ''
  if (step.value === 1) {
    if (!form.value.title.trim()) { error.value = '요리 이름을 입력해주세요.'; return }
    if (!form.value.category_id) { error.value = '카테고리를 선택해주세요.'; return }
  }
  step.value++
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function submit() {
  error.value = ''
  if (!form.value.title.trim()) { error.value = '요리 이름을 입력해주세요.'; step.value = 1; return }
  if (!form.value.category_id) { error.value = '카테고리를 선택해주세요.'; step.value = 1; return }

  submitting.value = true
  try {
    const payload = {
      ...form.value,
      ingredients: form.value.ingredients.filter(i => i.name.trim()),
      steps: form.value.steps.filter(s => s.text.trim()),
      tips: form.value.tips.filter(t => t.trim()),
    }
    const { data } = await axios.post('/api/recipes', payload)
    router.push({ name: 'recipe-detail', params: { id: data.id } })
  } catch (e) {
    error.value = e.response?.data?.message || '등록에 실패했습니다. 다시 시도해주세요.'
  } finally {
    submitting.value = false
  }
}

onMounted(loadCategories)
</script>
