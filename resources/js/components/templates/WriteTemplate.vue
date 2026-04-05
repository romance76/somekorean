<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="max-w-[800px] mx-auto px-4 py-6">

      <!-- Header -->
      <div class="flex items-center justify-between mb-5">
        <div class="flex items-center gap-3">
          <button @click="$router.back()" class="text-gray-400 hover:text-gray-600 transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          <h1 class="text-xl font-bold text-gray-800 dark:text-white">{{ title }}</h1>
        </div>
        <div class="flex items-center gap-2">
          <button @click="$router.back()"
            class="px-4 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition">
            {{ cancelLabel }}
          </button>
          <button @click="onSubmit" :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition">
            {{ loading ? '\uCC98\uB9AC\uC911...' : submitLabel }}
          </button>
        </div>
      </div>

      <!-- Form Card -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5 space-y-5">

        <!-- Title input -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\uC81C\uBAA9</label>
          <input :value="modelValue?.title" @input="updateField('title', $event.target.value)"
            type="text" :placeholder="titlePlaceholder"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
        </div>

        <!-- Category selector -->
        <div v-if="categories && categories.length">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\uCE74\uD14C\uACE0\uB9AC</label>
          <select :value="modelValue?.category" @change="updateField('category', $event.target.value)"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option value="">\uC120\uD0DD\uD574\uC8FC\uC138\uC694</option>
            <option v-for="cat in categories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
          </select>
        </div>

        <!-- Content (textarea with markdown) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\uB0B4\uC6A9</label>
          <textarea :value="modelValue?.content" @input="updateField('content', $event.target.value)"
            :placeholder="contentPlaceholder"
            rows="12"
            class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-y" />
          <p class="text-xs text-gray-400 mt-1">Markdown \uBB38\uBC95\uC744 \uC0AC\uC6A9\uD560 \uC218 \uC788\uC2B5\uB2C8\uB2E4</p>
        </div>

        <!-- Image upload -->
        <div v-if="hasImages">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\uC774\uBBF8\uC9C0</label>
          <div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition"
            @click="$refs.fileInput?.click()"
            @dragover.prevent
            @drop.prevent="onDrop">
            <svg class="w-8 h-8 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <p class="text-sm text-gray-500">\uD074\uB9AD \uB610\uB294 \uB4DC\uB798\uADF8\uD558\uC5EC \uC774\uBBF8\uC9C0 \uC5C5\uB85C\uB4DC</p>
            <p class="text-xs text-gray-400 mt-1">JPG, PNG, GIF (10MB \uC774\uD558)</p>
          </div>
          <input ref="fileInput" type="file" accept="image/*" multiple class="hidden" @change="onFileSelect" />

          <!-- Image previews -->
          <div v-if="imagePreviews.length" class="flex gap-2 mt-3 flex-wrap">
            <div v-for="(preview, idx) in imagePreviews" :key="idx" class="relative group">
              <img :src="preview" class="w-20 h-20 object-cover rounded-lg border border-gray-200" />
              <button @click="removeImage(idx)"
                class="absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Location input -->
        <div v-if="hasLocation">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">\uC704\uCE58</label>
          <AddressInput :modelValue="modelValue?.address" @update:modelValue="updateField('address', $event)" />
        </div>

        <!-- Custom fields slot -->
        <slot name="fields" />
      </div>

      <!-- Bottom submit (mobile-friendly) -->
      <div class="mt-5 flex justify-end gap-3">
        <button @click="$router.back()"
          class="w-full sm:w-auto px-5 py-2.5 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition">
          {{ cancelLabel }}
        </button>
        <button @click="onSubmit" :disabled="loading"
          class="w-full sm:w-auto px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition">
          {{ loading ? '\uCC98\uB9AC\uC911...' : submitLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AddressInput from '../AddressInput.vue'

const props = defineProps({
  title: { type: String, default: '\uAE00\uC4F0\uAE30' },
  mode: { type: String, default: 'create' }, // 'create' | 'edit'
  loading: { type: Boolean, default: false },
  submitLabel: { type: String, default: '\uC791\uC131\uD558\uAE30' },
  cancelLabel: { type: String, default: '\uCDE8\uC18C' },
  titlePlaceholder: { type: String, default: '\uC81C\uBAA9\uC744 \uC785\uB825\uD558\uC138\uC694' },
  contentPlaceholder: { type: String, default: '\uB0B4\uC6A9\uC744 \uC785\uB825\uD558\uC138\uC694' },
  modelValue: { type: Object, default: () => ({}) },
  categories: { type: Array, default: null },
  hasImages: { type: Boolean, default: true },
  hasLocation: { type: Boolean, default: false },
})

const emit = defineEmits(['submit', 'update:modelValue'])
const fileInput = ref(null)
const imagePreviews = ref([])
const imageFiles = ref([])

function updateField(field, value) {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}

function onSubmit() {
  if (props.loading) return
  emit('submit', { files: imageFiles.value })
}

function onFileSelect(e) {
  const files = Array.from(e.target.files)
  addFiles(files)
}

function onDrop(e) {
  const files = Array.from(e.dataTransfer.files).filter(f => f.type.startsWith('image/'))
  addFiles(files)
}

function addFiles(files) {
  for (const file of files) {
    if (file.size > 10 * 1024 * 1024) continue // Skip files > 10MB
    imageFiles.value.push(file)
    const reader = new FileReader()
    reader.onload = (e) => imagePreviews.value.push(e.target.result)
    reader.readAsDataURL(file)
  }
}

function removeImage(idx) {
  imagePreviews.value.splice(idx, 1)
  imageFiles.value.splice(idx, 1)
}
</script>
