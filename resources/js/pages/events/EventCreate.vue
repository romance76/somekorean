<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">🎉 {{ isEdit ? '이벤트 수정' : '이벤트 등록' }}</h1>
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 space-y-4">
      <div>
        <label class="text-sm font-semibold text-gray-700">제목 *</label>
        <input v-model="form.title" type="text" placeholder="예: 한인 문화 축제" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-sm font-semibold text-gray-700">카테고리</label>
          <select v-model="form.category" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none">
            <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">주최</label>
          <input v-model="form.organizer" type="text" placeholder="주최 단체/개인" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-sm font-semibold text-gray-700">시작일시 *</label>
          <input v-model="form.start_date" type="datetime-local" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">종료일시</label>
          <input v-model="form.end_date" type="datetime-local" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-sm font-semibold text-gray-700">장소명</label>
          <input v-model="form.venue" type="text" placeholder="장소명" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">주소</label>
          <input v-model="form.address" type="text" placeholder="상세 주소" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
      </div>

      <div class="grid grid-cols-3 gap-3">
        <div>
          <label class="text-sm font-semibold text-gray-700">도시</label>
          <input v-model="form.city" type="text" placeholder="Atlanta" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">주</label>
          <input v-model="form.state" type="text" placeholder="GA" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">가격 ($)</label>
          <input v-model.number="form.price" type="number" min="0" placeholder="0 = 무료" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-sm font-semibold text-gray-700">최대 참가자 (0=무제한)</label>
          <input v-model.number="form.max_attendees" type="number" min="0" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">관련 URL</label>
          <input v-model="form.url" type="url" placeholder="https://..." class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
      </div>

      <!-- 이미지 -->
      <div>
        <label class="text-sm font-semibold text-gray-700">이벤트 이미지</label>
        <div class="mt-1 flex items-center gap-3">
          <img v-if="previewImg" :src="previewImg" class="w-24 h-24 rounded-lg object-cover border" />
          <label class="cursor-pointer bg-gray-100 hover:bg-gray-200 text-gray-600 text-xs font-bold px-4 py-2 rounded-lg">
            📷 {{ previewImg ? '변경' : '업로드' }}
            <input type="file" accept="image/*" @change="onImage" class="hidden" />
          </label>
        </div>
      </div>

      <div>
        <label class="text-sm font-semibold text-gray-700">상세 내용</label>
        <textarea v-model="form.content" rows="8" placeholder="이벤트 상세 내용을 작성해주세요" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none resize-none"></textarea>
      </div>

      <div v-if="error" class="text-red-500 text-sm bg-red-50 rounded-lg px-3 py-2">{{ error }}</div>

      <div class="flex gap-3 pt-2">
        <button @click="submit" :disabled="submitting"
          class="bg-amber-400 text-amber-900 font-bold px-6 py-2.5 rounded-lg hover:bg-amber-500 disabled:opacity-50">
          {{ submitting ? '저장 중...' : (isEdit ? '수정 완료' : '이벤트 등록') }}
        </button>
        <button @click="$router.back()" class="text-gray-500 px-6 py-2.5">취소</button>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const editId = computed(() => route.params.id)
const isEdit = computed(() => !!editId.value)

const categories = [
  { value: 'culture', label: '🎭 문화' },
  { value: 'networking', label: '🤝 네트워킹' },
  { value: 'education', label: '📚 교육/세미나' },
  { value: 'community', label: '🏘️ 커뮤니티' },
  { value: 'sports', label: '⚽ 스포츠' },
  { value: 'food', label: '🍽️ 음식/맛집' },
  { value: 'music', label: '🎵 음악/공연' },
  { value: 'religion', label: '⛪ 종교' },
  { value: 'business', label: '💼 비즈니스' },
  { value: 'other', label: '📋 기타' },
]

const form = reactive({
  title: '', category: 'culture', organizer: '', start_date: '', end_date: '',
  venue: '', address: '', city: '', state: '', price: 0, content: '',
  max_attendees: 0, url: '',
})
const imageFile = ref(null)
const previewImg = ref(null)
const error = ref('')
const submitting = ref(false)

function onImage(e) {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value = file
  previewImg.value = URL.createObjectURL(file)
}

async function submit() {
  if (!form.title || !form.start_date) { error.value = '제목과 시작일을 입력해주세요'; return }
  submitting.value = true; error.value = ''

  const fd = new FormData()
  Object.entries(form).forEach(([k, v]) => { if (v !== '' && v !== null) fd.append(k, v) })
  if (form.price == 0) fd.set('is_free', '1')
  if (imageFile.value) fd.append('image', imageFile.value)

  try {
    if (isEdit.value) {
      fd.append('_method', 'PUT')
      const { data } = await axios.post(`/api/events/${editId.value}`, fd)
      router.push(`/events/${editId.value}`)
    } else {
      const { data } = await axios.post('/api/events', fd)
      router.push(`/events/${data.data.id}`)
    }
  } catch (e) {
    error.value = e.response?.data?.message || '저장 실패'
  }
  submitting.value = false
}

onMounted(async () => {
  if (isEdit.value) {
    try {
      const { data } = await axios.get(`/api/events/${editId.value}`)
      const e = data.data
      Object.assign(form, {
        title: e.title || '', category: e.category || 'culture', organizer: e.organizer || '',
        start_date: e.start_date ? e.start_date.slice(0, 16) : '',
        end_date: e.end_date ? e.end_date.slice(0, 16) : '',
        venue: e.venue || '', address: e.address || '', city: e.city || '', state: e.state || '',
        price: e.price || 0, content: e.content || '', max_attendees: e.max_attendees || 0, url: e.url || '',
      })
      if (e.image_url) previewImg.value = e.image_url
    } catch {}
  }
})
</script>
