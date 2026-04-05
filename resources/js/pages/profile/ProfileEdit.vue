<template>
  <div class="min-h-screen bg-gray-50 pb-24">
    <div class="max-w-3xl mx-auto px-4 py-6">
      <h1 class="text-2xl font-black text-gray-900 mb-6">{{ $t('profile.settings') }}</h1>

      <!-- Avatar -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
        <h2 class="text-sm font-bold text-gray-800 mb-4">{{ $t('profile.avatar') }}</h2>
        <div class="flex items-center gap-4">
          <div class="w-20 h-20 rounded-full bg-gradient-to-br from-red-400 to-red-600 flex items-center justify-center text-3xl text-white font-black overflow-hidden shadow-md">
            <img v-if="avatarPreview || form.avatar" :src="avatarPreview || form.avatar" class="w-full h-full object-cover"
              @error="e => e.target.style.display='none'" />
            <span v-else>{{ (form.name || '?')[0] }}</span>
          </div>
          <div>
            <input type="file" ref="avatarInput" accept="image/*" class="hidden" @change="onAvatarChange" />
            <button @click="$refs.avatarInput.click()"
              class="bg-red-600 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-red-700 transition">
              {{ $t('profile.change_photo') }}
            </button>
            <p class="text-xs text-gray-400 mt-1">JPG, PNG ({{ $t('profile.max_size') }} 2MB)</p>
          </div>
        </div>
      </div>

      <!-- Basic Info -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
        <h2 class="text-sm font-bold text-gray-800 mb-4">{{ $t('profile.basic_info') }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('auth.name') }} <span class="text-red-500">*</span></label>
            <input v-model="form.name" type="text" maxlength="50"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('auth.nickname') }}</label>
            <input v-model="form.nickname" type="text" maxlength="50" :placeholder="$t('profile.nickname_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>
          <div class="sm:col-span-2">
            <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('profile.bio') }}</label>
            <textarea v-model="form.bio" rows="3" maxlength="500" :placeholder="$t('profile.bio_placeholder')"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition resize-none" />
            <p class="text-xs text-gray-400 text-right mt-1">{{ (form.bio || '').length }}/500</p>
          </div>
        </div>
      </div>

      <!-- Contact -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
        <h2 class="text-sm font-bold text-gray-800 mb-4">{{ $t('profile.contact') }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('auth.phone') }}</label>
            <input v-model="form.phone" type="tel" placeholder="010-1234-5678"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('auth.email') }}</label>
            <input v-model="form.email" type="email" readonly
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm bg-gray-50 text-gray-500 cursor-not-allowed" />
            <p class="text-xs text-gray-400 mt-1">{{ $t('profile.email_readonly') }}</p>
          </div>
        </div>
      </div>

      <!-- Address -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
        <h2 class="text-sm font-bold text-gray-800 mb-4">{{ $t('profile.address') }}</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Address Line 1</label>
            <input v-model="form.address" type="text" placeholder="123 Main St"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Address Line 2</label>
            <input v-model="form.address2" type="text" placeholder="Apt 4B"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>
          <div class="grid grid-cols-3 gap-3">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">City</label>
              <input v-model="form.city" type="text"
                class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">State</label>
              <select v-model="form.state"
                class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition">
                <option value="">{{ $t('common.select') }}</option>
                <option v-for="s in usStates" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1">ZIP Code</label>
              <input v-model="form.zip_code" type="text" maxlength="10"
                class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
            </div>
          </div>
        </div>
      </div>

      <!-- Language Preference -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
        <h2 class="text-sm font-bold text-gray-800 mb-4">{{ $t('profile.preferences') }}</h2>
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('profile.language') }}</label>
          <select v-model="form.lang"
            class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition">
            <option value="ko">한국어</option>
            <option value="en">English</option>
          </select>
        </div>
      </div>

      <!-- Password Change -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-4">
        <h2 class="text-sm font-bold text-gray-800 mb-4">{{ $t('profile.change_password') }}</h2>
        <div class="space-y-3 max-w-md">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('profile.current_password') }}</label>
            <input v-model="pwForm.current_password" type="password"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('profile.new_password') }}</label>
            <input v-model="pwForm.password" type="password"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">{{ $t('profile.new_password_confirm') }}</label>
            <input v-model="pwForm.password_confirmation" type="password"
              class="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition" />
          </div>
          <button @click="changePassword" :disabled="!pwForm.current_password || !pwForm.password"
            class="bg-gray-800 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-gray-900 disabled:opacity-40 transition">
            {{ $t('profile.change_password') }}
          </button>
        </div>
      </div>

      <!-- Fixed Save Bar -->
      <div class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 z-40">
        <div class="max-w-3xl mx-auto flex gap-3">
          <router-link to="/dashboard"
            class="flex-1 bg-gray-100 text-gray-700 py-3 rounded-xl text-sm font-semibold text-center hover:bg-gray-200 transition">
            {{ $t('common.cancel') }}
          </router-link>
          <button @click="saveProfile" :disabled="saving"
            class="flex-1 bg-red-600 text-white py-3 rounded-xl text-sm font-bold hover:bg-red-700 disabled:opacity-50 transition">
            {{ saving ? $t('common.saving') : $t('common.save') }}
          </button>
        </div>
      </div>

      <!-- Toast -->
      <transition name="fade">
        <div v-if="showToast"
          class="fixed top-20 right-4 bg-green-500 text-white px-5 py-3 rounded-xl shadow-lg text-sm font-semibold z-50">
          {{ $t('profile.saved') }}
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useLangStore } from '../../stores/lang'
import axios from 'axios'

const authStore = useAuthStore()
const { $t } = useLangStore()
const saving = ref(false)
const showToast = ref(false)
const avatarInput = ref(null)
const avatarPreview = ref('')

const form = ref({
  name: '', nickname: '', bio: '', phone: '', email: '',
  address: '', address2: '', city: '', state: '', zip_code: '',
  lang: 'ko', avatar: '',
})

const pwForm = ref({ current_password: '', password: '', password_confirmation: '' })

const usStates = [
  'AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA',
  'KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
  'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT',
  'VA','WA','WV','WI','WY','DC',
]

async function loadProfile() {
  try {
    const { data } = await axios.get('/api/auth/me')
    const u = data.user || data
    form.value = {
      name: u.name || '', nickname: u.nickname || '', bio: u.bio || '',
      phone: u.phone || '', email: u.email || '',
      address: u.address || '', address2: u.address2 || '',
      city: u.city || '', state: u.state || '', zip_code: u.zip_code || '',
      lang: u.lang || 'ko', avatar: u.avatar || '',
    }
  } catch (e) {
    console.error('Profile load failed', e)
  }
}

async function saveProfile() {
  saving.value = true
  try {
    await axios.put('/api/profile', form.value)
    showToast.value = true
    setTimeout(() => (showToast.value = false), 3000)
    authStore.fetchUser()
  } catch (e) {
    alert(e.response?.data?.message || $t('common.save_failed'))
  } finally {
    saving.value = false
  }
}

async function changePassword() {
  try {
    await axios.post('/api/profile/password', pwForm.value)
    alert($t('profile.password_changed'))
    pwForm.value = { current_password: '', password: '', password_confirmation: '' }
  } catch (e) {
    alert(e.response?.data?.message || $t('profile.password_change_failed'))
  }
}

async function onAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    alert($t('profile.file_too_large'))
    return
  }
  // Preview
  avatarPreview.value = URL.createObjectURL(file)
  const fd = new FormData()
  fd.append('avatar', file)
  try {
    const { data } = await axios.post('/api/profile/avatar', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.value.avatar = data.avatar_url || data.avatar || ''
    authStore.fetchUser()
  } catch {
    alert($t('profile.upload_failed'))
    avatarPreview.value = ''
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
