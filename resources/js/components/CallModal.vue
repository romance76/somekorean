<template>
  <teleport to="body">
    <div
      v-if="callState !== 'idle'"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black"
      :class="callType === 'video' && callState === 'connected' ? 'bg-opacity-95' : 'bg-opacity-80'"
    >
      <!-- Video call: remote video (fullscreen) -->
      <video
        v-if="callType === 'video' && callState === 'connected' && remoteStream"
        ref="remoteVideoEl"
        autoplay
        playsinline
        class="absolute inset-0 w-full h-full object-cover"
      ></video>

      <!-- Video call: local video (PIP, bottom-right) -->
      <div
        v-if="callType === 'video' && callState === 'connected' && localStream"
        class="absolute bottom-28 right-4 w-32 h-44 sm:w-40 sm:h-56 rounded-2xl overflow-hidden border-2 border-white shadow-lg z-10"
      >
        <video
          ref="localVideoEl"
          autoplay
          playsinline
          muted
          class="w-full h-full object-cover"
          :class="{ 'opacity-30': isVideoOff }"
        ></video>
        <div v-if="isVideoOff" class="absolute inset-0 flex items-center justify-center bg-gray-800 bg-opacity-60">
          <span class="text-white text-sm">카메라 꺼짐</span>
        </div>
      </div>

      <!-- Main content overlay -->
      <div class="relative z-10 flex flex-col items-center justify-center w-full max-w-md mx-auto px-6 text-center">

        <!-- Calling state -->
        <template v-if="callState === 'calling'">
          <div class="mb-6">
            <div class="w-28 h-28 mx-auto rounded-full bg-gray-700 flex items-center justify-center mb-4 animate-pulse">
              <span class="text-5xl">{{ callType === 'video' ? '📹' : '📞' }}</span>
            </div>
            <p class="text-white text-2xl font-bold mb-2">{{ remoteUser?.name || '상대방' }}</p>
            <p class="text-gray-300 text-xl animate-pulse">전화 거는 중...</p>
          </div>

          <!-- Hang up button -->
          <div class="mt-8">
            <button
              @click="$emit('endCall')"
              class="w-20 h-20 rounded-full bg-red-600 hover:bg-red-700 active:scale-95 transition flex items-center justify-center shadow-xl"
            >
              <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08a.956.956 0 010-1.36C3.53 8.46 7.56 6.5 12 6.5s8.47 1.96 11.71 5.22c.19.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28a11.27 11.27 0 00-2.67-1.85.996.996 0 01-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
              </svg>
            </button>
            <p class="text-gray-400 text-base mt-2">취소</p>
          </div>
        </template>

        <!-- Ringing state (incoming call) -->
        <template v-if="callState === 'ringing'">
          <div class="mb-6">
            <div class="w-28 h-28 mx-auto rounded-full bg-green-600 flex items-center justify-center mb-4 ring-animation">
              <span class="text-5xl">{{ callType === 'video' ? '📹' : '📞' }}</span>
            </div>
            <p class="text-white text-2xl font-bold mb-2">{{ remoteUser?.name || '알 수 없음' }}</p>
            <p class="text-gray-300 text-xl">
              {{ callType === 'video' ? '영상 전화가 왔습니다' : '전화가 왔습니다' }}
            </p>
          </div>

          <!-- Accept / Reject buttons -->
          <div class="flex items-center justify-center gap-16 mt-8">
            <div class="text-center">
              <button
                @click="$emit('rejectCall')"
                class="w-20 h-20 rounded-full bg-red-600 hover:bg-red-700 active:scale-95 transition flex items-center justify-center shadow-xl"
              >
                <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08a.956.956 0 010-1.36C3.53 8.46 7.56 6.5 12 6.5s8.47 1.96 11.71 5.22c.19.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28a11.27 11.27 0 00-2.67-1.85.996.996 0 01-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
                </svg>
              </button>
              <p class="text-red-400 text-lg font-bold mt-2">거절</p>
            </div>
            <div class="text-center">
              <button
                @click="$emit('answerCall')"
                class="w-20 h-20 rounded-full bg-green-500 hover:bg-green-600 active:scale-95 transition flex items-center justify-center shadow-xl ring-animation"
              >
                <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56a.977.977 0 00-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 .99-.63.99-1.18v-3.45c0-.54-.45-.99-.99-.99z"/>
                </svg>
              </button>
              <p class="text-green-400 text-lg font-bold mt-2">받기</p>
            </div>
          </div>
        </template>

        <!-- Connected state (audio call - no video overlay) -->
        <template v-if="callState === 'connected' && callType === 'audio'">
          <div class="mb-6">
            <div class="w-28 h-28 mx-auto rounded-full bg-green-600 flex items-center justify-center mb-4">
              <span class="text-5xl">📞</span>
            </div>
            <p class="text-white text-2xl font-bold mb-2">{{ remoteUser?.name || '상대방' }}</p>
            <p class="text-green-400 text-3xl font-mono">{{ formatDuration(callDuration) }}</p>
          </div>
        </template>

        <!-- Connected state (video call - duration overlay) -->
        <template v-if="callState === 'connected' && callType === 'video'">
          <div class="absolute top-8 left-0 right-0 text-center">
            <p class="text-white text-lg font-bold drop-shadow-lg">{{ remoteUser?.name || '상대방' }}</p>
            <p class="text-green-400 text-2xl font-mono drop-shadow-lg">{{ formatDuration(callDuration) }}</p>
          </div>
        </template>

        <!-- Controls for connected state -->
        <div v-if="callState === 'connected'" class="fixed bottom-8 left-0 right-0 flex items-center justify-center gap-6 z-20">
          <!-- Mute toggle -->
          <div class="text-center">
            <button
              @click="$emit('toggleMute')"
              class="w-16 h-16 rounded-full transition flex items-center justify-center shadow-lg"
              :class="isMuted ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-600 hover:bg-gray-700'"
            >
              <svg v-if="!isMuted" class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1-9c0-.55.45-1 1-1s1 .45 1 1v6c0 .55-.45 1-1 1s-1-.45-1-1V5zm6 6c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
              <svg v-else class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.54-.9L19.73 21 21 19.73 4.27 3z"/>
              </svg>
            </button>
            <p class="text-gray-300 text-xs mt-1">{{ isMuted ? '음소거' : '마이크' }}</p>
          </div>

          <!-- Video toggle (only for video calls) -->
          <div v-if="callType === 'video'" class="text-center">
            <button
              @click="$emit('toggleVideo')"
              class="w-16 h-16 rounded-full transition flex items-center justify-center shadow-lg"
              :class="isVideoOff ? 'bg-red-500 hover:bg-red-600' : 'bg-gray-600 hover:bg-gray-700'"
            >
              <svg v-if="!isVideoOff" class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
              </svg>
              <svg v-else class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M21 6.5l-4 4V7c0-.55-.45-1-1-1H9.82L21 17.18V6.5zM3.27 2L2 3.27 4.73 6H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.21 0 .39-.08.54-.18L19.73 21 21 19.73 3.27 2z"/>
              </svg>
            </button>
            <p class="text-gray-300 text-xs mt-1">{{ isVideoOff ? '카메라 꺼짐' : '카메라' }}</p>
          </div>

          <!-- End call -->
          <div class="text-center">
            <button
              @click="$emit('endCall')"
              class="w-20 h-20 rounded-full bg-red-600 hover:bg-red-700 active:scale-95 transition flex items-center justify-center shadow-xl"
            >
              <svg class="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 9c-1.6 0-3.15.25-4.6.72v3.1c0 .39-.23.74-.56.9-.98.49-1.87 1.12-2.66 1.85-.18.18-.43.28-.7.28-.28 0-.53-.11-.71-.29L.29 13.08a.956.956 0 010-1.36C3.53 8.46 7.56 6.5 12 6.5s8.47 1.96 11.71 5.22c.19.18.29.43.29.71 0 .28-.11.53-.29.71l-2.48 2.48c-.18.18-.43.29-.71.29-.27 0-.52-.1-.7-.28a11.27 11.27 0 00-2.67-1.85.996.996 0 01-.56-.9v-3.1C15.15 9.25 13.6 9 12 9z"/>
              </svg>
            </button>
            <p class="text-red-400 text-xs mt-1">종료</p>
          </div>
        </div>

        <!-- Ended state -->
        <template v-if="callState === 'ended'">
          <div class="mb-6">
            <div class="w-28 h-28 mx-auto rounded-full bg-gray-700 flex items-center justify-center mb-4">
              <span class="text-5xl">📵</span>
            </div>
            <p class="text-white text-2xl font-bold mb-2">통화 종료</p>
            <p class="text-gray-400 text-lg" v-if="callDuration > 0">
              통화 시간: {{ formatDuration(callDuration) }}
            </p>
          </div>
        </template>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  callState: { type: String, default: 'idle' },
  callType: { type: String, default: 'audio' },
  callDuration: { type: Number, default: 0 },
  localStream: { type: Object, default: null },
  remoteStream: { type: Object, default: null },
  remoteUser: { type: Object, default: null },
  isMuted: { type: Boolean, default: false },
  isVideoOff: { type: Boolean, default: false },
  formatDuration: { type: Function, default: (s) => {
    const m = Math.floor(s/60).toString().padStart(2,'0')
    const sec = (s%60).toString().padStart(2,'0')
    return `${m}:${sec}`
  }},
})

defineEmits(['answerCall', 'rejectCall', 'endCall', 'toggleMute', 'toggleVideo'])

const localVideoEl = ref(null)
const remoteVideoEl = ref(null)

// Attach streams to video elements
watch(() => props.localStream, async (stream) => {
  await nextTick()
  if (localVideoEl.value && stream) {
    localVideoEl.value.srcObject = stream
  }
}, { immediate: true })

watch(() => props.remoteStream, async (stream) => {
  await nextTick()
  if (remoteVideoEl.value && stream) {
    remoteVideoEl.value.srcObject = stream
  }
}, { immediate: true })

// Re-attach when video elements appear
watch(() => localVideoEl.value, (el) => {
  if (el && props.localStream) el.srcObject = props.localStream
})
watch(() => remoteVideoEl.value, (el) => {
  if (el && props.remoteStream) el.srcObject = props.remoteStream
})
</script>

<style scoped>
@keyframes ring-pulse {
  0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
  70% { box-shadow: 0 0 0 20px rgba(34, 197, 94, 0); }
  100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}
.ring-animation {
  animation: ring-pulse 1.5s infinite;
}
</style>
