<template>
  <div class="flex gap-2">
    <button @click="startCall('video')"
      class="flex items-center gap-1.5 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-bold transition shadow-sm">
      📹 영상통화
    </button>
    <button @click="startCall('audio')"
      class="flex items-center gap-1.5 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-xl text-sm font-bold transition shadow-sm">
      📞 전화
    </button>
  </div>
</template>

<script setup>
import { inject } from 'vue'

const props = defineProps({
  targetUser: { type: Object, required: true },
})

// App.vue에서 provide한 전역 webrtc composable 사용
const webrtc = inject('webrtc')

function startCall(type) {
  if (!webrtc) { alert('통화 기능을 사용할 수 없습니다.'); return }
  webrtc.call(props.targetUser, type)
}
</script>
