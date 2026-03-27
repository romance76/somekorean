<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-8">
    <div class="bg-white rounded-2xl shadow-md p-8 w-full max-w-sm">
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-red-600">SomeKorean</h1>
        <p class="text-gray-500 text-sm mt-1">무료 회원가입</p>
      </div>
      <form @submit.prevent="handleRegister" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">이름</label>
          <input v-model="form.name" type="text" required placeholder="실명 또는 닉네임"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">아이디 (영문/숫자)</label>
          <input v-model="form.username" type="text" required placeholder="사용할 아이디"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">이메일</label>
          <input v-model="form.email" type="email" required placeholder="이메일 주소"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호</label>
          <input v-model="form.password" type="password" required placeholder="8자 이상"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">비밀번호 확인</label>
          <input v-model="form.password_confirmation" type="password" required placeholder="비밀번호 재입력"
            class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
        </div>
        <div v-if="errors.length" class="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-lg">
          <p v-for="err in errors" :key="err">{{ err }}</p>
        </div>
        <button type="submit" :disabled="loading"
          class="w-full bg-red-600 text-white py-2.5 rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50">
          {{ loading ? '가입 중...' : '회원가입' }}
        </button>
      </form>
      <p class="text-center text-sm text-gray-500 mt-4">
        이미 계정이 있으신가요?
        <router-link to="/auth/login" class="text-red-600 font-medium hover:underline">로그인</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';

const authStore = useAuthStore();
const router = useRouter();
const form = ref({ name: '', username: '', email: '', password: '', password_confirmation: '' });
const loading = ref(false);
const errors = ref([]);

async function handleRegister() {
    loading.value = true;
    errors.value = [];
    try {
        await authStore.register(form.value);
        router.push('/');
    } catch(e) {
        if (e.response?.data?.errors) {
            errors.value = Object.values(e.response.data.errors).flat();
        } else {
            errors.value = [e.response?.data?.message || '가입에 실패했습니다.'];
        }
    } finally {
        loading.value = false;
    }
}
</script>
