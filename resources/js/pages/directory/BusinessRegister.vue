<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">🏪 업소 등록</h1>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-4">
      <div><label class="text-sm font-semibold text-gray-700">업소명</label><input v-model="form.name" type="text" placeholder="예: 서울가든 Korean BBQ" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">카테고리</label>
          <select v-model="form.category" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none">
            <option v-for="c in ['restaurant','grocery','beauty','medical','professional','auto','realestate','education','etc']" :key="c" :value="c">{{ {restaurant:'음식점',grocery:'마트/식료품',beauty:'미용/뷰티',medical:'의료/건강',professional:'전문서비스',auto:'자동차',realestate:'부동산',education:'교육',etc:'기타'}[c] }}</option>
          </select></div>
        <div><label class="text-sm font-semibold text-gray-700">세부 카테고리</label><input v-model="form.subcategory" type="text" placeholder="예: 한식, 네일, 치과 등" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">전화번호</label><input v-model="form.phone" type="text" placeholder="(213) 555-1234" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">이메일</label><input v-model="form.email" type="email" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div><label class="text-sm font-semibold text-gray-700">웹사이트</label><input v-model="form.website" type="url" placeholder="https://" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      <div><label class="text-sm font-semibold text-gray-700">주소</label><input v-model="form.address" type="text" placeholder="123 Main St" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      <div class="grid grid-cols-3 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">도시</label><input v-model="form.city" type="text" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">주</label><input v-model="form.state" type="text" maxlength="2" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">우편번호</label><input v-model="form.zipcode" type="text" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div><label class="text-sm font-semibold text-gray-700">업소 소개</label><textarea v-model="form.description" rows="4" placeholder="업소를 소개해주세요" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none resize-none"></textarea></div>
      <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
      <div class="flex gap-3 pt-2">
        <button @click="submit" :disabled="submitting" class="bg-amber-400 text-amber-900 font-bold px-6 py-2.5 rounded-lg hover:bg-amber-500 disabled:opacity-50">{{ submitting ? '등록 중...' : '업소 등록' }}</button>
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
const form = reactive({ name:'',category:'restaurant',subcategory:'',phone:'',email:'',website:'',address:'',city:'',state:'',zipcode:'',description:'' })
const error = ref('')
const submitting = ref(false)
async function submit() {
  if (!form.name || !form.category) { error.value = '업소명과 카테고리를 입력해주세요'; return }
  submitting.value = true; error.value = ''
  try { const { data } = await axios.post('/api/businesses', form); router.push(`/directory/${data.data.id}`) }
  catch (e) { error.value = e.response?.data?.message || '등록 실패' }
  submitting.value = false
}
</script>
