<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">🎉 이벤트 등록</h1>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-4">
      <div><label class="text-sm font-semibold text-gray-700">제목</label><input v-model="form.title" type="text" placeholder="예: 한인 문화 축제" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">카테고리</label>
          <select v-model="form.category" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none">
            <option v-for="c in ['culture','networking','education','community','sports','food']" :key="c" :value="c">{{ {culture:'문화',networking:'네트워킹',education:'교육',community:'커뮤니티',sports:'스포츠',food:'음식'}[c] }}</option>
          </select></div>
        <div><label class="text-sm font-semibold text-gray-700">주최</label><input v-model="form.organizer" type="text" placeholder="주최 단체/개인" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">시작일시</label><input v-model="form.start_date" type="datetime-local" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">종료일시</label><input v-model="form.end_date" type="datetime-local" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">장소</label><input v-model="form.venue" type="text" placeholder="장소명" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">가격 ($, 0=무료)</label><input v-model.number="form.price" type="number" min="0" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div><label class="text-sm font-semibold text-gray-700">상세 내용</label><textarea v-model="form.content" rows="6" placeholder="이벤트 상세 내용" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none resize-none"></textarea></div>
      <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
      <div class="flex gap-3 pt-2">
        <button @click="submit" :disabled="submitting" class="bg-amber-400 text-amber-900 font-bold px-6 py-2.5 rounded-lg hover:bg-amber-500 disabled:opacity-50">{{ submitting ? '등록 중...' : '이벤트 등록' }}</button>
        <button @click="$router.back()" class="text-gray-500 px-6 py-2.5">취소</button>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const form = reactive({ title:'',category:'culture',organizer:'',start_date:'',end_date:'',venue:'',price:0,content:'' })
const error = ref('')
const submitting = ref(false)
async function submit() {
  if (!form.title || !form.start_date) { error.value = '제목과 시작일을 입력해주세요'; return }
  submitting.value = true; error.value = ''
  try { const { data } = await axios.post('/api/events', form); router.push(`/events/${data.data.id}`) }
  catch (e) { error.value = e.response?.data?.message || '등록 실패' }
  submitting.value = false
}
</script>
