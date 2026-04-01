<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 배너 -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
      <div class="max-w-7xl mx-auto px-4 py-8">
        <h1 class="text-2xl font-bold">&#10067; 질문 작성하기</h1>
        <p class="text-blue-100 mt-1 text-sm">궁금한 것을 자세히 적어주시면 더 좋은 답변을 받을 수 있어요</p>
      </div>
    </div>

    <div class="max-w-3xl mx-auto px-4 py-6">
      <div class="bg-white rounded-2xl shadow-sm p-6">
        <!-- 카테고리 선택 -->
        <div class="mb-5">
          <label class="block text-sm font-bold text-gray-700 mb-2">카테고리</label>
          <div class="grid grid-cols-2 sm:grid-cols-5 gap-2">
            <button v-for="cat in categories" :key="cat.id"
              @click="form.category_id = cat.id"
              class="px-3 py-2 rounded-lg text-sm font-medium transition border"
              :class="form.category_id === cat.id ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'">
              {{ cat.name }}
            </button>
          </div>
        </div>

        <!-- 제목 -->
        <div class="mb-5">
          <label class="block text-sm font-bold text-gray-700 mb-2">제목</label>
          <input v-model="form.title" type="text"
            class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="질문 제목을 입력하세요" />
        </div>

        <!-- 내용 -->
        <div class="mb-5">
          <label class="block text-sm font-bold text-gray-700 mb-2">내용</label>
          <textarea v-model="form.content" rows="10"
            class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            placeholder="질문 내용을 자세히 작성해주세요..."></textarea>
        </div>

        <!-- 포인트 걸기 -->
        <div class="mb-6 bg-yellow-50 rounded-xl p-4">
          <label class="block text-sm font-bold text-gray-700 mb-2">&#127942; 포인트 걸기</label>
          <p class="text-xs text-gray-500 mb-3">걸어놓은 포인트는 채택 시 답변자에게 전달됩니다</p>
          <div class="flex items-center gap-4">
            <input v-model.number="form.point_reward" type="range" min="0" :max="myPoints"
              class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-yellow-500" />
            <div class="flex items-center gap-2">
              <input v-model.number="form.point_reward" type="number" min="0" :max="myPoints"
                class="w-20 border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-center" />
              <span class="text-sm text-gray-500">P</span>
            </div>
          </div>
          <p class="text-xs text-gray-400 mt-2">현재 보유: {{ myPoints.toLocaleString() }}P</p>
        </div>

        <!-- 등록 버튼 -->
        <div class="flex justify-end gap-3">
          <button @click="$router.back()"
            class="px-5 py-2.5 border border-gray-200 rounded-xl text-sm text-gray-600 hover:bg-gray-50 transition">
            취소
          </button>
          <button @click="submitQuestion" :disabled="submitting"
            class="px-6 py-2.5 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 transition disabled:opacity-50">
            {{ submitting ? '등록 중...' : '질문 등록' }}
          </button>
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
const categories = ref([])
const myPoints = ref(0)
const submitting = ref(false)

const form = reactive({
  category_id: null,
  title: '',
  content: '',
  point_reward: 0,
})

const token = localStorage.getItem('sk_token')
if (!token) {
  router.push('/auth/login')
}
const headers = { Authorization: 'Bearer ' + token }

onMounted(async () => {
  try {
    const results = await Promise.all([
      axios.get('/api/qa-v2/categories', { headers: headers }),
      axios.get('/api/user/me', { headers: headers })
    ])
    categories.value = results[0].data.data || results[0].data
    const user = results[1].data.data || results[1].data
    myPoints.value = user.points || user.point_balance || 0
  } catch (e) { console.error(e) }
})

async function submitQuestion() {
  if (!form.category_id) return alert('카테고리를 선택해주세요.')
  if (!form.title.trim()) return alert('제목을 입력해주세요.')
  if (!form.content.trim()) return alert('내용을 입력해주세요.')
  if (form.point_reward > myPoints.value) return alert('보유 포인트보다 많은 포인트를 걸 수 없습니다.')

  submitting.value = true
  try {
    const resp = await axios.post('/api/qa-v2/questions', {
      category_id: form.category_id,
      title: form.title,
      content: form.content,
      point_reward: form.point_reward,
    }, { headers: headers })
    const newQ = resp.data.data || resp.data
    const slug = newQ.category?.slug || 'general'
    router.push('/qa/' + slug + '/' + newQ.id)
  } catch (e) {
    console.error(e)
    alert(e.response?.data?.message || '질문 등록에 실패했습니다.')
  }
  submitting.value = false
}
</script>
