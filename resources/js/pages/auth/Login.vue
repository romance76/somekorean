<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="bg-white rounded-2xl shadow-md p-8 w-full max-w-sm">
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-red-600">SomeKorean</h1>
        <p class="text-gray-500 text-sm mt-1">한인 커뮤니티 로그인</p>
      </div>
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">이메일</label>
          <input v-model="form.email" type="email" required placeholder="이메일 입력"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
          <input v-model="form.password" type="password" required placeholder="비밀번호 입력"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent" />
        </div>
        <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-lg">{{ error }}</div>
        <button type="submit" :disabled="loading"
          class="w-full bg-red-600 text-white py-2.5 rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>
      <p class="text-center text-sm text-gray-500 mt-4">
        계정이 없으신가요?
        <router-link to="/auth/register" class="text-red-600 font-medium hover:underline">회원가입</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const form = ref({ email: '', password: '' });
const loading = ref(false);
const error = ref('');

async function handleLogin() {
    loading.value = true;
    error.value = '';
    try {
        await authStore.login(form.value.email, form.value.password);
        const redirect = route.query.redirect || '/';
        router.push(redirect);
    } catch(e) {
        error.value = e.response?.data?.message || '로그인에 실패했습니다.';
    } finally {
        loading.value = false;
    }
}
</script>
