<template>
  <div class="min-h-screen bg-gray-50 pb-16">
    <div class="max-w-[1200px] mx-auto px-4 py-6">
      <!-- 헤더: 제목 + 취소/저장 버튼 -->
      <div class="flex items-center justify-between mb-5">
        <h1 class="text-xl font-bold text-gray-800">{{ title }}</h1>
        <div class="flex items-center gap-2">
          <button @click="$router.back()"
            class="px-4 py-2 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition">
            취소
          </button>
          <button @click="onSubmit" :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition">
            {{ loading ? '처리중...' : submitLabel }}
          </button>
        </div>
      </div>

      <!-- 메인 폼 영역 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="space-y-5">
          <!-- 입력 필드 슬롯 -->
          <slot name="fields" />

          <!-- 추가 필드 슬롯 (찜 설정, 부스트 등) -->
          <div v-if="$slots['extra-fields']">
            <slot name="extra-fields" />
          </div>
        </div>
      </div>

      <!-- 하단 제출 버튼 (모바일에서 눈에 잘 띄게) -->
      <div class="mt-5 flex justify-end gap-3">
        <button @click="$router.back()"
          class="w-full sm:w-auto px-5 py-2.5 border border-gray-300 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition">
          취소
        </button>
        <button @click="onSubmit" :disabled="loading"
          class="w-full sm:w-auto px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition">
          {{ loading ? '처리중...' : submitLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: { type: String, default: '글쓰기' },
  loading: { type: Boolean, default: false },
  submitLabel: { type: String, default: '작성하기' }
})

const emit = defineEmits(['submit'])

function onSubmit() {
  if (props.loading) return
  emit('submit')
}
</script>
