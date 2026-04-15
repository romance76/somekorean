<template>
  <div v-if="ads.length" class="space-y-2 mt-3">
    <div v-for="ad in ads" :key="ad.id"
      class="relative rounded-xl overflow-hidden border border-gray-200 shadow-sm cursor-pointer group hover:shadow-md transition"
      @click="handleClick(ad)">
      <img :src="ad.image_url" :alt="ad.title"
        class="w-full object-cover"
        :style="imgStyle"
        @error="e => e.target.src = '/images/ad-placeholder.png'" />
      <div class="absolute top-1 right-1 bg-black/50 text-white text-[8px] px-1.5 py-0.5 rounded font-bold">AD</div>
      <div v-if="ad.title" class="px-2 py-1.5 bg-white">
        <div class="text-[11px] text-gray-700 truncate">{{ ad.title }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  page: { type: String, required: true },
  position: { type: String, required: true },
  maxSlots: { type: Number, default: 3 }
})

const ads = ref([])

// 위치별 고정 사이즈 (어떤 크기 이미지든 이 사이즈로 표시)
const imgStyle = computed(() => {
  if (props.position === 'left') return { width: '100%', height: '150px', objectFit: 'cover' }
  if (props.position === 'right') return { width: '100%', height: '200px', objectFit: 'cover' }
  return { width: '100%', height: '80px', objectFit: 'cover' }
})

async function loadAds() {
  try {
    const { data } = await axios.get('/api/banners/active', {
      params: { page: props.page, position: props.position, limit: props.maxSlots }
    })
    ads.value = data.data || []
  } catch {}
}

function handleClick(ad) {
  axios.post(`/api/banners/${ad.id}/click`).catch(() => {})
  if (ad.link_url) window.open(ad.link_url, '_blank')
}

onMounted(loadAds)
watch(() => props.page, loadAds)
</script>
