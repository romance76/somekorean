<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <h1 class="text-xl font-black text-gray-800 mb-4">📱 숏츠 업로드</h1>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-4">
      <div>
        <label class="text-sm font-semibold text-gray-700">YouTube URL</label>
        <input v-model="form.video_url" type="url" placeholder="https://youtube.com/shorts/... 또는 https://youtu.be/..."
          @input="parseUrl" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
      </div>
      <div v-if="preview" class="bg-gray-100 rounded-lg p-3">
        <img :src="preview" class="w-32 h-56 object-cover rounded-lg mx-auto" />
        <div class="text-center text-xs text-gray-500 mt-2">미리보기</div>
      </div>
      <div>
        <label class="text-sm font-semibold text-gray-700">제목</label>
        <input v-model="form.title" type="text" placeholder="숏츠 제목" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
      </div>
      <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>
      <div class="flex gap-3 pt-2">
        <button @click="submit" :disabled="submitting || !form.video_url" class="bg-amber-400 text-amber-900 font-bold px-6 py-2.5 rounded-lg hover:bg-amber-500 disabled:opacity-50">{{ submitting ? '업로드 중...' : '업로드' }}</button>
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
const form = reactive({ title: '', video_url: '' })
const preview = ref(null)
const error = ref('')
const submitting = ref(false)
function parseUrl() {
  const m = form.video_url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|shorts\/))([a-zA-Z0-9_-]+)/)
  if (m) { preview.value = `https://img.youtube.com/vi/${m[1]}/hqdefault.jpg`; if (!form.title) form.title = '숏츠 영상' }
  else preview.value = null
}
async function submit() {
  if (!form.video_url || !form.title) { error.value = 'URL과 제목을 입력해주세요'; return }
  submitting.value = true; error.value = ''
  try { await axios.post('/api/shorts', form); router.push('/shorts') }
  catch (e) { error.value = e.response?.data?.message || '업로드 실패' }
  submitting.value = false
}
</script>
