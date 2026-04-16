<template>
<Teleport to="body">
  <div v-if="show" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="handleClose">
    <div class="bg-white rounded-2xl w-full max-w-sm shadow-xl overflow-hidden">
      <!-- 헤더 -->
      <div class="px-5 py-3 border-b bg-blue-50 flex items-center justify-between">
        <h3 class="font-bold text-sm text-gray-800">✉️ {{ userName }}님에게 쪽지</h3>
        <button @click="handleClose" class="text-gray-400 hover:text-gray-600">✕</button>
      </div>

      <!-- 작성 뷰 -->
      <template v-if="!msg.sent">
        <div class="p-4 space-y-3">
          <textarea v-model="msg.content" rows="5" maxlength="500" placeholder="쪽지 내용을 입력하세요..."
            class="w-full border border-gray-200 rounded-lg p-3 text-sm resize-none outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400"></textarea>
          <div class="flex items-center justify-between">
            <span class="text-[10px] text-gray-400">{{ msg.content.length }}/500</span>
            <div class="flex gap-2">
              <button @click="handleClose" class="bg-gray-100 text-gray-600 text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-gray-200">취소</button>
              <button @click="doSend" :disabled="msg.sending || !msg.content.trim()"
                class="bg-blue-500 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-blue-600 disabled:opacity-50">
                {{ msg.sending ? '전송중...' : '보내기' }}
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- 전송 완료 뷰 -->
      <template v-else>
        <div class="p-4 space-y-3">
          <p class="text-xs font-bold text-green-600">✅ 쪽지를 보냈습니다</p>
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed max-h-32 overflow-y-auto">{{ msg.sentContent }}</div>
          <div class="flex gap-2">
            <button @click="writeAnother" class="flex-1 bg-blue-500 text-white text-xs font-bold py-2 rounded-lg hover:bg-blue-600">새 쪽지 쓰기</button>
            <button @click="handleClose" class="flex-1 bg-gray-100 text-gray-600 text-xs font-bold py-2 rounded-lg hover:bg-gray-200">닫기</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</Teleport>
</template>

<script setup>
import { useMessage } from '../composables/useSocialActions'

const props = defineProps({
  show: Boolean,
  userId: [Number, String],
  userName: { type: String, default: '' },
})
const emit = defineEmits(['close', 'sent'])

const msg = useMessage()

async function doSend() {
  const ok = await msg.send(props.userId)
  if (ok) emit('sent')
}

function writeAnother() {
  msg.content = ''
  msg.sent = false
  msg.sentContent = ''
}

function handleClose() {
  msg.reset()
  emit('close')
}
</script>
