<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4 py-8">
    <div class="w-full max-w-sm">
      <!-- Logo -->
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-red-600 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-lg">
          <span class="text-white text-2xl font-black">SK</span>
        </div>
        <h1 class="text-2xl font-black text-gray-900">{{ $t('auth.register_title') }}</h1>
        <p class="text-gray-500 text-sm mt-1">{{ $t('auth.register_subtitle') }}</p>
      </div>

      <!-- Form -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.name') }} <span class="text-red-500">*</span></label>
            <input v-model="form.name" type="text" required :placeholder="$t('auth.name_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.nickname') }}</label>
            <input v-model="form.nickname" type="text" :placeholder="$t('auth.nickname_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.email') }} <span class="text-red-500">*</span></label>
            <input v-model="form.email" type="email" required :placeholder="$t('auth.email_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.password') }} <span class="text-red-500">*</span></label>
            <input v-model="form.password" type="password" required placeholder="8자 이상"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>

          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.password_confirm') }} <span class="text-red-500">*</span></label>
            <input v-model="form.password_confirmation" type="password" required :placeholder="$t('auth.password_confirm_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>

          <!-- Optional fields -->
          <div class="border-t border-gray-100 pt-4 space-y-4">
            <p class="text-xs text-gray-400 font-medium">{{ $t('auth.optional_fields') }}</p>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.phone') }}</label>
              <input v-model="form.phone" type="tel" placeholder="010-1234-5678"
                class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1.5">{{ $t('auth.zipcode') }}</label>
              <input v-model="form.zip_code" type="text" placeholder="30301" maxlength="10"
                class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
            </div>
          </div>

          <!-- Errors -->
          <div v-if="errors.length" class="bg-red-50 border border-red-200 text-red-600 text-sm p-3 rounded-xl space-y-1">
            <div v-for="err in errors" :key="err" class="flex items-start gap-2">
              <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
              </svg>
              <span>{{ err }}</span>
            </div>
          </div>

          <button type="submit" :disabled="loading"
            class="w-full bg-red-600 text-white py-3 rounded-xl font-bold text-sm hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed">
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ $t('auth.registering') }}
            </span>
            <span v-else>{{ $t('auth.register') }}</span>
          </button>
        </form>
      </div>

      <!-- Login Link -->
      <p class="text-center text-sm text-gray-500 mt-6">
        {{ $t('auth.has_account') }}
        <router-link to="/auth/login" class="text-red-600 font-semibold hover:underline">{{ $t('auth.login') }}</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'

const authStore = useAuthStore()
const { $t } = useLangStore()
const router = useRouter()

const form = ref({
  name: '', nickname: '', email: '',
  password: '', password_confirmation: '',
  phone: '', zip_code: ''
})
const loading = ref(false)
const errors = ref([])

async function handleRegister() {
  loading.value = true
  errors.value = []
  try {
    await authStore.register(form.value)
    router.push('/')
  } catch (e) {
    if (e.response?.data?.errors) {
      errors.value = Object.values(e.response.data.errors).flat()
    } else {
      errors.value = [e.response?.data?.message || $t('auth.register_failed')]
    }
  } finally {
    loading.value = false
  }
}
</script>
