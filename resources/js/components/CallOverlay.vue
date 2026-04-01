<template>
  <!-- 수신 알림 (ringing) -->
  <Teleport to="body">
    <Transition name="slide-up">
      <div v-if="callState === 'ringing'" class="fixed bottom-6 left-1/2 -translate-x-1/2 z-[200] w-[340px]">
        <div class="bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">
          <div class="bg-gradient-to-r from-blue-600 to-blue-500 px-5 py-4 flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center text-xl font-bold text-white flex-shrink-0">
              {{ (remoteUser?.name ?? '?')[0] }}
            </div>
            <div>
              <p class="text-white font-black text-base">{{ remoteUser?.name }}</p>
              <p class="text-blue-200 text-sm flex items-center gap-1">
                <span class="animate-pulse">●</span>
                {{ callType === 'video' ? '영상통화 수신 중...' : '음성통화 수신 중...' }}
              </p>
            </div>
          </div>
          <div class="flex gap-3 p-4">
            <button @click="emit('reject')"
              class="flex-1 bg-red-500 hover:bg-red-600 text-white rounded-xl py-3 font-bold flex items-center justify-center gap-2 transition">
              📵 거절
            </button>
            <button @click="emit('accept')"
              class="flex-1 bg-green-500 hover:bg-green-600 text-white rounded-xl py-3 font-bold flex items-center justify-center gap-2 transition">
              {{ callType === 'video' ? '📹 수락' : '📞 수락' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 통화 중 화면 (connected / calling) -->
    <Transition name="fade">
      <div v-if="callState === 'connected' || callState === 'calling'"
        class="fixed inset-0 bg-gray-950 z-[200] flex flex-col">

        <!-- 원격 비디오 (배경 전체) -->
        <div class="relative flex-1 overflow-hidden">
          <video v-if="remoteStream && callType === 'video'"
            :srcObject="remoteStream" autoplay playsinline
            class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex flex-col items-center justify-center gap-4">
            <div class="w-24 h-24 rounded-full bg-gray-700 flex items-center justify-center text-4xl font-black text-white">
              {{ (remoteUser?.name ?? '?')[0] }}
            </div>
            <p class="text-white font-bold text-xl">{{ remoteUser?.name }}</p>
            <p class="text-gray-400 text-sm">{{ callState === 'calling' ? '연결 중...' : '통화 중' }}</p>
          </div>

          <!-- 내 카메라 (PIP) -->
          <div v-if="localStream && callType === 'video'" class="absolute top-4 right-4 w-28 h-40 rounded-2xl overflow-hidden border-2 border-white/30 shadow-lg">
            <video :srcObject="localStream" autoplay playsinline muted class="w-full h-full object-cover" />
            <div v-if="isVideoOff" class="absolute inset-0 bg-gray-800 flex items-center justify-center">
              <span class="text-2xl">📷</span>
            </div>
          </div>

          <!-- 통화 시간 -->
          <div class="absolute top-4 left-1/2 -translate-x-1/2 bg-black/50 text-white text-sm px-3 py-1.5 rounded-full backdrop-blur-sm">
            {{ callState === 'calling' ? '연결 중...' : callDuration }}
          </div>
        </div>

        <!-- 컨트롤 바 -->
        <div class="bg-gray-900/95 backdrop-blur-sm px-6 py-6 pb-[max(1.5rem,env(safe-area-inset-bottom))]">
          <div class="flex items-center justify-center gap-5">
            <!-- 마이크 -->
            <button @click="emit('toggleMute')"
              class="w-14 h-14 rounded-full flex items-center justify-center transition"
              :class="isMuted ? 'bg-red-500/30 ring-2 ring-red-500' : 'bg-gray-700 hover:bg-gray-600'">
              <span class="text-2xl">{{ isMuted ? '🔇' : '🎤' }}</span>
            </button>

            <!-- 카메라 (영상통화만) -->
            <button v-if="callType === 'video'" @click="emit('toggleVideo')"
              class="w-14 h-14 rounded-full flex items-center justify-center transition"
              :class="isVideoOff ? 'bg-red-500/30 ring-2 ring-red-500' : 'bg-gray-700 hover:bg-gray-600'">
              <span class="text-2xl">{{ isVideoOff ? '📷' : '📹' }}</span>
            </button>

            <!-- 종료 -->
            <button @click="emit('hangup')"
              class="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 flex items-center justify-center shadow-lg shadow-red-500/40 transition">
              <span class="text-2xl">📵</span>
            </button>

            <!-- 스피커 -->
            <button class="w-14 h-14 rounded-full bg-gray-700 hover:bg-gray-600 flex items-center justify-center transition">
              <span class="text-2xl">🔊</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  callState:    String,
  remoteUser:   Object,
  remoteStream: Object,
  localStream:  Object,
  isMuted:      Boolean,
  isVideoOff:   Boolean,
  callType:     String,
})
const emit = defineEmits(['accept', 'reject', 'hangup', 'toggleMute', 'toggleVideo'])

// 통화 시간 카운터
const callDuration = ref('00:00')
let timer = null

watch(() => props.callState, (state) => {
  if (state === 'connected') {
    let secs = 0
    timer = setInterval(() => {
      secs++
      const m = String(Math.floor(secs / 60)).padStart(2, '0')
      const s = String(secs % 60).padStart(2, '0')
      callDuration.value = `${m}:${s}`
    }, 1000)
  } else {
    clearInterval(timer)
    callDuration.value = '00:00'
  }
})

onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.slide-up-enter-from, .slide-up-leave-to { transform: translate(-50%, 100px); opacity: 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
