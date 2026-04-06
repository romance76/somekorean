<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">✏️ 프로필 수정</h1>
    <div v-if="auth.user" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">이름</label><input v-model="form.name" type="text" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">닉네임</label><input v-model="form.nickname" type="text" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div><label class="text-sm font-semibold text-gray-700">소개</label><textarea v-model="form.bio" rows="3" placeholder="자기소개를 적어주세요" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none resize-none"></textarea></div>
      <div><label class="text-sm font-semibold text-gray-700">전화번호</label><input v-model="form.phone" type="text" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      <div class="grid grid-cols-3 gap-3">
        <div><label class="text-sm font-semibold text-gray-700">도시</label><input v-model="form.city" type="text" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">주</label><input v-model="form.state" type="text" maxlength="2" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
        <div><label class="text-sm font-semibold text-gray-700">우편번호</label><input v-model="form.zipcode" type="text" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" /></div>
      </div>
      <div>
        <label class="text-sm font-semibold text-gray-700">언어</label>
        <select v-model="form.language" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none">
          <option value="ko">한국어</option><option value="en">English</option>
        </select>
      </div>
      <div v-if="msg" class="text-sm" :class="msgType==='success'?'text-green-600':'text-red-500'">{{ msg }}</div>
      <button @click="save" :disabled="saving" class="bg-amber-400 text-amber-900 font-bold px-6 py-2.5 rounded-lg hover:bg-amber-500 disabled:opacity-50">{{ saving ? '저장 중...' : '저장하기' }}</button>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'
const auth = useAuthStore()
const form = reactive({ name:'',nickname:'',bio:'',phone:'',city:'',state:'',zipcode:'',language:'ko' })
const msg = ref('')
const msgType = ref('')
const saving = ref(false)
async function save() {
  saving.value = true; msg.value = ''
  try {
    await axios.put('/api/user/profile', form)
    await auth.fetchUser()
    msg.value = '저장되었습니다!'; msgType.value = 'success'
  } catch (e) { msg.value = e.response?.data?.message || '저장 실패'; msgType.value = 'error' }
  saving.value = false
}
onMounted(() => {
  if (auth.user) {
    Object.keys(form).forEach(k => { if (auth.user[k]) form[k] = auth.user[k] })
  }
})
</script>
