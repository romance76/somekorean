<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="w-full max-w-sm">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-red-600 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-lg">
          <span class="text-white text-2xl font-black">SK</span>
        </div>
        <h1 class="text-2xl font-black text-gray-900">{{ $t('auth.login_title') }}</h1>
        <p class="text-gray-500 text-sm mt-1">{{ $t('auth.login_subtitle') }}</p>
      </div>

      <!-- Form -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.email') }}</label>
            <input
              v-model="form.email"
              type="email"
              required
              :placeholder="$t('auth.email_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition"
            />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.password') }}</label>
            <div class="relative">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                :placeholder="$t('auth.password_placeholder')"
                class="w-full border border-gray-200 rounded-xl px-4 py-3 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition"
              />
              <button type="button" @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.542-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Remember Me -->
          <label class="flex items-center gap-2 cursor-pointer">
            <input v-model="form.remember" type="checkbox"
              class="w-4 h-4 rounded border-gray-300 text-red-600 focus:ring-red-500" />
            <span class="text-sm text-gray-600">{{ $t('auth.remember_me') }}</span>
          </label>

          <!-- Error -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-xl flex items-center gap-2">
            <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            <span>{{ error }}</span>
          </div>

          <button type="submit" :disabled="loading"
            class="w-full bg-red-600 text-white py-3 rounded-xl font-bold text-sm hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed">
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ $t('auth.logging_in') }}
            </span>
            <span v-else>{{ $t('auth.login') }}</span>
          </button>
        </form>
      </div>

      <!-- Register Link -->
      <p class="text-center text-sm text-gray-500 mt-6">
        {{ $t('auth.no_account') }}
        <router-link to="/auth/register" class="text-red-600 font-semibold hover:underline">{{ $t('auth.register') }}</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'

const authStore = useAuthStore()
const { $t } = useLangStore()
const router = useRouter()
const route = useRoute()

const form = ref({ email: '', password: '', remember: false })
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await authStore.login(form.value.email, form.value.password)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    error.value = e.response?.data?.message || $t('auth.login_failed')
  } finally {
    loading.value = false
  }
}
</script>
