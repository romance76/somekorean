<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white border-b px-4 py-4">
      <div class="max-w-6xl mx-auto flex items-center justify-between">
        <h1 class="text-xl font-bold">🏪 내 업소 관리</h1>
        <div class="flex gap-2">
          <span v-if="business.is_premium" class="bg-yellow-100 text-yellow-700 text-xs px-2 py-1 rounded-full font-semibold">⭐ 프리미엄</span>
          <span v-else class="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">기본 플랜</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
    </div>

    <div v-else-if="!business.id" class="max-w-2xl mx-auto px-4 py-20 text-center">
      <div class="text-5xl mb-4">🏪</div>
      <h2 class="text-2xl font-bold mb-2">등록된 업소가 없습니다</h2>
      <p class="text-gray-500 mb-6">소유권 신청을 통해 내 업소를 등록하세요</p>
      <router-link to="/directory" class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700">업소 찾기</router-link>
    </div>

    <div v-else class="max-w-6xl mx-auto px-4 py-6">
      <!-- Business header card -->
      <div class="bg-white rounded-2xl shadow p-6 mb-6 flex items-start gap-4">
        <div class="w-16 h-16 rounded-xl bg-gray-100 flex items-center justify-center text-3xl flex-shrink-0">🏪</div>
        <div class="flex-1">
          <h2 class="text-xl font-bold">{{ business.name }}</h2>
          <p class="text-gray-500 text-sm">{{ business.address }}</p>
          <p class="text-blue-600 text-sm">{{ business.phone }}</p>
        </div>
        <router-link :to="`/directory/${business.id}`" class="text-blue-600 text-sm hover:underline">업소 보기 →</router-link>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 bg-gray-100 rounded-xl p-1 mb-6 overflow-x-auto">
        <button v-for="t in tabs" :key="t.id" @click="activeTab=t.id"
          :class="['px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition',
            activeTab===t.id ? 'bg-white shadow text-blue-600' : 'text-gray-600 hover:text-gray-800']">
          {{ t.icon }} {{ t.label }}
        </button>
      </div>

      <!-- Tab: 기본정보 -->
      <div v-if="activeTab==='info'" class="bg-white rounded-2xl shadow p-6">
        <h3 class="font-bold text-lg mb-4">기본 정보 수정</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">업소명 (한국어)</label>
            <input v-model="form.name_ko" class="w-full border rounded-xl px-4 py-2.5" placeholder="한국어 업소명"/>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">업소명 (영어)</label>
            <input v-model="form.name_en" class="w-full border rounded-xl px-4 py-2.5" placeholder="English name"/>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">전화번호</label>
            <input v-model="form.phone" class="w-full border rounded-xl px-4 py-2.5" placeholder="(000) 000-0000"/>
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">웹사이트</label>
            <input v-model="form.website" class="w-full border rounded-xl px-4 py-2.5" placeholder="https://"/>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-gray-600 mb-1">소개 (한국어)</label>
            <textarea v-model="form.owner_description_ko" rows="3" class="w-full border rounded-xl px-4 py-2.5" placeholder="업소 소개를 입력하세요"></textarea>
          </div>
          <div class="md:col-span-2">
            <label class="block text-sm text-gray-600 mb-1">임시 휴업</label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.temp_closed" class="w-4 h-4"/>
              <span class="text-sm text-gray-700">현재 임시 휴업 중</span>
            </label>
          </div>
        </div>
        <button @click="saveInfo" :disabled="saving" class="mt-4 bg-blue-600 text-white px-6 py-2.5 rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-50">
          {{ saving ? '저장 중...' : '저장하기' }}
        </button>
        <span v-if="saved" class="ml-3 text-green-600 text-sm">✓ 저장되었습니다</span>
      </div>

      <!-- Tab: 사진 -->
      <div v-if="activeTab==='photos'" class="bg-white rounded-2xl shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-lg">사진 관리</h3>
          <span class="text-sm text-gray-500">{{ photos.length }}/{{ business.is_premium ? 20 : 5 }}장</span>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          <div v-for="(ph, i) in photos" :key="i" class="relative group">
            <img :src="ph" class="w-full h-28 object-cover rounded-xl"/>
            <button @click="deletePhoto(i)" class="absolute top-1 right-1 bg-red-500 text-white w-6 h-6 rounded-full text-xs opacity-0 group-hover:opacity-100 transition">✕</button>
          </div>
          <div v-if="photos.length < (business.is_premium ? 20 : 5)"
            class="border-2 border-dashed rounded-xl h-28 flex items-center justify-center cursor-pointer text-gray-400 hover:border-blue-400 hover:text-blue-400 transition"
            @click="$refs.photoInput.click()">
            <div class="text-center"><div class="text-2xl">+</div><div class="text-xs">추가</div></div>
          </div>
        </div>
        <input ref="photoInput" type="file" multiple accept="image/*" class="hidden" @change="uploadPhotos"/>
        <div v-if="!business.is_premium" class="bg-yellow-50 rounded-xl p-4 text-sm">
          💡 프리미엄 업그레이드 시 최대 20장의 사진을 등록할 수 있습니다.
          <router-link to="/premium-upgrade" class="text-blue-600 ml-1 hover:underline">업그레이드 →</router-link>
        </div>
      </div>

      <!-- Tab: 리뷰 -->
      <div v-if="activeTab==='reviews'" class="bg-white rounded-2xl shadow p-6">
        <h3 class="font-bold text-lg mb-4">리뷰 관리</h3>
        <div v-if="reviews.length === 0" class="text-center py-8 text-gray-400">아직 리뷰가 없습니다</div>
        <div v-for="rv in reviews" :key="rv.id" class="border-b last:border-b-0 py-4">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="font-semibold text-sm">{{ rv.user?.name || '익명' }}</span>
                <div class="flex">
                  <span v-for="s in 5" :key="s" :class="s <= rv.rating ? 'text-yellow-400' : 'text-gray-200'" class="text-xs">★</span>
                </div>
              </div>
              <p class="text-gray-700 text-sm">{{ rv.content }}</p>
              <p v-if="rv.owner_reply" class="mt-2 bg-blue-50 rounded-lg p-2 text-sm text-blue-800">
                <span class="font-semibold">사장님 답변: </span>{{ rv.owner_reply }}
              </p>
            </div>
          </div>
          <div v-if="!rv.owner_reply" class="mt-3">
            <div class="flex gap-2">
              <input v-model="rv._reply" placeholder="답변을 입력하세요..." class="flex-1 border rounded-lg px-3 py-1.5 text-sm"/>
              <button @click="replyReview(rv)" class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-blue-700">답변</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: 이벤트 -->
      <div v-if="activeTab==='events'" class="bg-white rounded-2xl shadow p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-lg">이벤트 관리</h3>
          <button v-if="business.is_premium" @click="showEventForm=!showEventForm" class="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-semibold hover:bg-blue-700">+ 이벤트 추가</button>
        </div>
        <div v-if="!business.is_premium" class="bg-yellow-50 rounded-xl p-4 text-sm mb-4">
          ⭐ 이벤트 기능은 프리미엄 플랜에서 이용 가능합니다.
          <router-link to="/premium-upgrade" class="text-blue-600 ml-1 hover:underline">업그레이드 →</router-link>
        </div>
        <div v-if="showEventForm && business.is_premium" class="border rounded-xl p-4 mb-4 bg-gray-50">
          <div class="grid grid-cols-2 gap-3 mb-3">
            <input v-model="eventForm.title" placeholder="이벤트 제목" class="col-span-2 border rounded-lg px-3 py-2 text-sm"/>
            <input v-model="eventForm.event_date" type="date" class="border rounded-lg px-3 py-2 text-sm"/>
            <input v-model="eventForm.event_time" type="time" class="border rounded-lg px-3 py-2 text-sm"/>
            <textarea v-model="eventForm.description" placeholder="이벤트 설명" rows="2" class="col-span-2 border rounded-lg px-3 py-2 text-sm"></textarea>
          </div>
          <button @click="createEvent" class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700">이벤트 등록</button>
        </div>
        <div v-for="ev in events" :key="ev.id" class="flex items-center justify-between border-b last:border-b-0 py-3">
          <div>
            <p class="font-semibold text-sm">{{ ev.title }}</p>
            <p class="text-gray-500 text-xs">{{ ev.event_date }} {{ ev.event_time }}</p>
          </div>
          <button @click="deleteEvent(ev.id)" class="text-red-500 hover:text-red-700 text-sm">삭제</button>
        </div>
        <div v-if="events.length === 0 && business.is_premium" class="text-center py-8 text-gray-400">등록된 이벤트가 없습니다</div>
      </div>

      <!-- Tab: 통계 -->
      <div v-if="activeTab==='stats'" class="bg-white rounded-2xl shadow p-6">
        <h3 class="font-bold text-lg mb-4">통계</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div v-for="s in statCards" :key="s.label" class="bg-gray-50 rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-blue-600">{{ s.value }}</div>
            <div class="text-xs text-gray-500 mt-1">{{ s.label }}</div>
          </div>
        </div>
        <div v-if="!business.is_premium" class="bg-yellow-50 rounded-xl p-4 text-sm">
          ⭐ 상세 통계는 프리미엄 플랜에서 이용 가능합니다.
          <router-link to="/premium-upgrade" class="text-blue-600 ml-1 hover:underline">업그레이드 →</router-link>
        </div>
      </div>

      <!-- Tab: 프리미엄 -->
      <div v-if="activeTab==='premium'" class="bg-white rounded-2xl shadow p-6">
        <h3 class="font-bold text-lg mb-6">프리미엄 플랜</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="plan in plans" :key="plan.id"
            :class="['border-2 rounded-2xl p-6', plan.recommended ? 'border-blue-600' : 'border-gray-200']">
            <div v-if="plan.recommended" class="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-full inline-block mb-2">추천</div>
            <h4 class="font-bold text-lg">{{ plan.name }}</h4>
            <div class="text-2xl font-bold text-blue-600 my-2">${{ plan.price }}<span class="text-sm text-gray-500">/월</span></div>
            <ul class="space-y-2 text-sm text-gray-600 mb-4">
              <li v-for="f in plan.features" :key="f">✓ {{ f }}</li>
            </ul>
            <button class="w-full bg-blue-600 text-white py-2 rounded-xl font-semibold hover:bg-blue-700" @click="alert('준비 중입니다')">선택하기</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const loading = ref(true)
const business = ref({})
const form = ref({})
const photos = ref([])
const reviews = ref([])
const events = ref([])
const stats = ref({})
const activeTab = ref('info')
const saving = ref(false)
const saved = ref(false)
const showEventForm = ref(false)
const eventForm = ref({ title: '', event_date: '', event_time: '', description: '' })

const tabs = [
  { id: 'info', icon: '📝', label: '기본정보' },
  { id: 'photos', icon: '📷', label: '사진' },
  { id: 'reviews', icon: '⭐', label: '리뷰' },
  { id: 'events', icon: '🎉', label: '이벤트' },
  { id: 'stats', icon: '📊', label: '통계' },
  { id: 'premium', icon: '👑', label: '프리미엄' },
]

const plans = [
  { id: 'basic', name: 'Basic', price: 29, features: ['사진 10장', '소개글 작성', '영업시간 관리', '기본 통계'] },
  { id: 'standard', name: 'Standard', price: 59, recommended: true, features: ['사진 20장', '이벤트 등록', '상세 통계', '리뷰 답변', '검색 상단 노출'] },
  { id: 'premium', name: 'Premium', price: 99, features: ['모든 Standard 기능', '광고 배너', '메뉴 관리', '우선 지원', '맞춤 마케팅'] },
]

const statCards = computed(() => [
  { label: '이번달 조회수', value: stats.value.views || 0 },
  { label: '전화 클릭', value: stats.value.phone_clicks || 0 },
  { label: '길찾기 클릭', value: stats.value.direction_clicks || 0 },
  { label: '웹사이트 클릭', value: stats.value.website_clicks || 0 },
])

onMounted(async () => {
  try {
    const r = await axios.get('/api/owner/business')
    business.value = r.data.business || r.data
    form.value = { ...business.value }
    photos.value = business.value.owner_photos || []
    const [rv, ev, st] = await Promise.all([
      axios.get('/api/owner/reviews').catch(() => ({ data: { data: [] } })),
      axios.get('/api/owner/events').catch(() => ({ data: { data: [] } })),
      axios.get('/api/owner/stats').catch(() => ({ data: {} })),
    ])
    reviews.value = rv.data.data || []
    events.value = ev.data.data || []
    stats.value = st.data || {}
  } catch(e) {
    console.error(e)
  } finally { loading.value = false }
})

async function saveInfo() {
  saving.value = true
  try {
    await axios.put('/api/owner/business', form.value)
    saved.value = true
    setTimeout(() => saved.value = false, 3000)
  } catch(e) { alert('저장 실패') }
  finally { saving.value = false }
}

async function uploadPhotos(e) {
  const files = Array.from(e.target.files)
  const fd = new FormData()
  files.forEach(f => fd.append('photos[]', f))
  try {
    const r = await axios.post('/api/owner/business/photos', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    photos.value = r.data.photos || photos.value
  } catch(e) { alert('업로드 실패') }
}

async function deletePhoto(i) {
  try {
    await axios.delete(`/api/owner/business/photos/${i}`)
    photos.value.splice(i, 1)
  } catch(e) {}
}

async function replyReview(rv) {
  if (!rv._reply) return
  try {
    await axios.post(`/api/owner/reviews/${rv.id}/reply`, { reply: rv._reply })
    rv.owner_reply = rv._reply
  } catch(e) {}
}

async function createEvent() {
  try {
    const r = await axios.post('/api/owner/events', eventForm.value)
    events.value.unshift(r.data)
    eventForm.value = { title: '', event_date: '', event_time: '', description: '' }
    showEventForm.value = false
  } catch(e) { alert('이벤트 등록 실패') }
}

async function deleteEvent(id) {
  if (!confirm('삭제하시겠습니까?')) return
  try {
    await axios.delete(`/api/owner/events/${id}`)
    events.value = events.value.filter(e => e.id !== id)
  } catch(e) {}
}
</script>
