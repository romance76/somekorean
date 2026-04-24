<template>
<div class="leaderboard-card">
  <div class="lb-header">
    <span class="lb-title">🏆 Lv.{{ level }} 기록 TOP 10</span>
    <button @click="load" class="lb-refresh" title="새로고침">🔄</button>
  </div>

  <div v-if="loading" class="lb-empty">불러오는 중...</div>
  <div v-else-if="!records.length" class="lb-empty">아직 기록이 없어요. 첫 번째 기록을 세워보세요!</div>
  <div v-else class="lb-list">
    <div v-for="r in records" :key="r.rank" class="lb-row" :class="{ mine: r.user_id === myUserId }">
      <span class="lb-rank" :class="rankClass(r.rank)">{{ rankIcon(r.rank) }}</span>
      <img v-if="r.avatar" :src="r.avatar" class="lb-avatar" @error="e=>e.target.style.display='none'" />
      <div v-else class="lb-avatar-fb">{{ (r.name || '?')[0] }}</div>
      <span class="lb-name">{{ r.name }}</span>
      <span class="lb-time">{{ formatTime(r.time_ms) }}</span>
    </div>
  </div>

  <!-- 내 기록 (10위 밖일 때만 별도 표시) -->
  <div v-if="my && my.rank > 10" class="lb-my-row">
    <span class="lb-rank mine">{{ my.rank }}</span>
    <span class="lb-name mine">나의 기록</span>
    <span class="lb-time">{{ formatTime(my.time_ms) }}</span>
  </div>
</div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  slug: { type: String, required: true },   // ex: 'flag'
  level: { type: Number, default: 1 },
})

const auth = useAuthStore()
const myUserId = auth.user?.id
const records = ref([])
const my = ref(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await axios.get(`/api/games/${props.slug}/leaderboard`, { params: { level: props.level } })
    records.value = data.data || []
    my.value = data.my || null
  } catch { records.value = []; my.value = null }
  loading.value = false
}

function formatTime(ms) {
  if (!ms) return '-'
  const total = Math.round(ms / 10) / 100 // 소수점 2자리 초
  return total.toFixed(2) + '초'
}
function rankIcon(r) {
  if (r === 1) return '🥇'
  if (r === 2) return '🥈'
  if (r === 3) return '🥉'
  return r
}
function rankClass(r) { return r === 1 ? 'gold' : r === 2 ? 'silver' : r === 3 ? 'bronze' : '' }

onMounted(load)
watch(() => [props.slug, props.level], load)

defineExpose({ reload: load })
</script>

<style scoped>
.leaderboard-card { background: rgba(255,255,255,0.95); border-radius: 16px; padding: 14px 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin: 16px auto; max-width: 420px; width: 100%; }
.lb-header { display:flex; align-items:center; justify-content:space-between; margin-bottom: 10px; border-bottom: 1px solid #f3f4f6; padding-bottom: 8px; }
.lb-title { font-weight: 800; font-size: 14px; color: #1f2937; }
.lb-refresh { background: transparent; border: none; cursor: pointer; font-size: 14px; color: #6b7280; }
.lb-empty { text-align: center; color: #9ca3af; font-size: 13px; padding: 24px 0; }
.lb-list { display: flex; flex-direction: column; gap: 4px; }
.lb-row { display: flex; align-items: center; gap: 8px; padding: 6px 8px; border-radius: 8px; font-size: 13px; transition: background 0.2s; }
.lb-row:hover { background: #fef3c7; }
.lb-row.mine { background: #fef3c7; border: 1px solid #f59e0b; }
.lb-rank { width: 28px; text-align: center; font-weight: 800; font-size: 13px; color: #6b7280; flex-shrink: 0; }
.lb-rank.gold { font-size: 18px; }
.lb-rank.silver { font-size: 17px; }
.lb-rank.bronze { font-size: 16px; }
.lb-rank.mine { color: #f59e0b; }
.lb-avatar { width: 24px; height: 24px; border-radius: 50%; object-fit: cover; flex-shrink: 0; }
.lb-avatar-fb { width: 24px; height: 24px; border-radius: 50%; background: #fde68a; color: #92400e; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 11px; flex-shrink: 0; }
.lb-name { flex: 1; font-weight: 600; color: #374151; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.lb-name.mine { color: #b45309; font-weight: 800; }
.lb-time { font-weight: 700; color: #1d4ed8; font-variant-numeric: tabular-nums; flex-shrink: 0; }
.lb-my-row { display: flex; align-items: center; gap: 8px; padding: 8px; margin-top: 8px; border-top: 1px dashed #e5e7eb; background: #fffbeb; border-radius: 8px; font-size: 13px; }
</style>
