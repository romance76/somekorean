<template>
  <div v-if="ads.length" class="space-y-2">
    <div v-for="ad in ads" :key="ad.id"
      class="relative rounded-xl overflow-hidden border border-gray-200 shadow-sm cursor-pointer group hover:shadow-md transition"
      @click="handleClick(ad)">
      <img :src="ad.image_url" :alt="ad.title" class="w-full object-cover"
        :class="position === 'top' ? 'h-[90px]' : position === 'center' ? 'h-[60px]' : 'h-auto max-h-[200px]'"
        @error="e => e.target.src = '/images/ad-placeholder.png'" />
      <div class="absolute top-1 right-1 bg-black/50 text-white text-[8px] px-1.5 py-0.5 rounded font-bold">AD</div>
      <div v-if="ad.title && position !== 'top'" class="px-2 py-1.5 bg-white">
        <div class="text-[11px] text-gray-700 truncate">{{ ad.title }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const props = defineProps({
  page: { type: String, required: true },
  position: { type: String, required: true },
  maxSlots: { type: Number, default: 3 }
})

const ads = ref([])

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
