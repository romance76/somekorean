<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="bg-white rounded-2xl shadow p-8 max-w-md w-full text-center">
      <div v-if="loading" class="py-8">
        <div class="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p class="text-gray-500">이메일 인증 처리 중...</p>
      </div>
      <div v-else-if="success">
        <div class="text-6xl mb-4">✅</div>
        <h2 class="text-2xl font-bold mb-2">이메일 인증 완료!</h2>
        <p class="text-gray-500 mb-6">소유권 신청이 접수되었습니다. 관리자 검토 후 1-3 영업일 내 안내드립니다.</p>
        <router-link to="/" class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700">홈으로</router-link>
      </div>
      <div v-else>
        <div class="text-6xl mb-4">❌</div>
        <h2 class="text-2xl font-bold mb-2">인증 실패</h2>
        <p class="text-gray-500 mb-6">{{ errorMsg }}</p>
        <router-link to="/businesses" class="bg-gray-100 text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-200">업소 목록으로</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const loading = ref(true)
const success = ref(false)
const errorMsg = ref('인증 링크가 유효하지 않거나 만료되었습니다.')

onMounted(async () => {
  const token = route.params.token
  if (!token) { loading.value = false; return }
  try {
    await axios.get(`/api/claims/email/verify/${token}`)
    success.value = true
  } catch(e) {
    errorMsg.value = e.response?.data?.message || '인증 처리 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
})
</script>
