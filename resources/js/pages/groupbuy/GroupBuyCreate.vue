<template>
<div class="min-h-screen bg-gray-50">
  <div class="max-w-3xl mx-auto px-4 py-5">
    <router-link to="/groupbuy" class="text-xl font-black text-gray-800 mb-4 inline-block hover:text-amber-600 transition">
      🤝 공동구매 등록
    </router-link>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-5">

      <!-- 1. 제목 -->
      <div>
        <label class="text-sm font-semibold text-gray-700">제목 <span class="text-red-400">*</span></label>
        <input v-model="form.title" type="text" placeholder="예: 코스트코 한우 공동구매"
          class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
      </div>

      <!-- 2. 카테고리 -->
      <div>
        <label class="text-sm font-semibold text-gray-700">카테고리</label>
        <select v-model="form.category" class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none">
          <option v-for="c in categories" :key="c.value" :value="c.value">{{ c.label }}</option>
        </select>
      </div>

      <!-- 3. 상세 설명 -->
      <div>
        <label class="text-sm font-semibold text-gray-700">상세 설명 <span class="text-red-400">*</span></label>
        <textarea v-model="form.content" rows="6" placeholder="공동구매 상품 설명, 배송 방법, 픽업 장소 등을 자세히 작성해주세요"
          class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none resize-none"></textarea>
      </div>

      <!-- 4. 가격 -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-sm font-semibold text-gray-700">원래 가격 ($)</label>
          <input v-model.number="form.original_price" type="number" min="0" placeholder="0"
            class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">공동구매 최저가 ($)</label>
          <input v-model.number="form.group_price" type="number" min="0" placeholder="0"
            class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
      </div>

      <!-- 5. 상품 링크 -->
      <div>
        <label class="text-sm font-semibold text-gray-700">상품 링크</label>
        <input v-model="form.product_url" type="url" placeholder="https://..."
          class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
      </div>

      <!-- 6. 상품 이미지 -->
      <div>
        <label class="text-sm font-semibold text-gray-700 flex items-center gap-2">
          상품 이미지
          <span class="text-xs text-gray-400 font-normal">최대 5장</span>
        </label>
        <div class="flex flex-wrap gap-2 mt-2">
          <div v-for="(photo, idx) in photoList" :key="idx"
            class="relative w-24 h-24 rounded-lg overflow-hidden border-2 border-gray-200 group">
            <img :src="photo.preview" class="w-full h-full object-cover" />
            <button @click="removePhoto(idx)"
              class="absolute bottom-1 right-1 bg-black/60 text-white w-5 h-5 rounded-full text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
              ✕
            </button>
          </div>
          <label v-if="photoList.length < 5"
            class="w-24 h-24 rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-amber-400 hover:bg-amber-50/50 transition">
            <span class="text-2xl text-gray-400">+</span>
            <span class="text-[10px] text-gray-400">사진 추가</span>
            <input type="file" multiple accept="image/*" @change="onSelectPhotos" class="hidden" />
          </label>
        </div>
      </div>

      <!-- 7. 참여 인원 -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-sm font-semibold text-gray-700">최소 인원</label>
          <input v-model.number="form.min_participants" type="number" min="2" placeholder="2"
            class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">최대 인원</label>
          <input v-model.number="form.max_participants" type="number" min="2" placeholder="50"
            class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
      </div>

      <!-- 8. 마감일 -->
      <div>
        <label class="text-sm font-semibold text-gray-700">마감일</label>
        <input v-model="form.deadline" type="date"
          class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
      </div>

      <!-- 9. 종료 방식 -->
      <div>
        <label class="text-sm font-semibold text-gray-700 mb-2 block">종료 방식</label>
        <div class="space-y-2">
          <label class="flex items-start gap-2 p-3 rounded-lg border cursor-pointer transition"
            :class="form.end_type === 'target_met' ? 'border-amber-400 bg-amber-50' : 'border-gray-200 hover:bg-gray-50'">
            <input v-model="form.end_type" type="radio" value="target_met" class="mt-0.5 accent-amber-500" />
            <div>
              <div class="text-sm font-semibold text-gray-800">목표 인원 달성 시 자동 종료</div>
              <div class="text-xs text-gray-400">최대 인원에 도달하면 자동으로 모집이 마감됩니다</div>
            </div>
          </label>
          <label class="flex items-start gap-2 p-3 rounded-lg border cursor-pointer transition"
            :class="form.end_type === 'time_limit' ? 'border-amber-400 bg-amber-50' : 'border-gray-200 hover:bg-gray-50'">
            <input v-model="form.end_type" type="radio" value="time_limit" class="mt-0.5 accent-amber-500" />
            <div>
              <div class="text-sm font-semibold text-gray-800">기한 종료 시 현재 인원 기준 진행</div>
              <div class="text-xs text-gray-400">마감일이 지나면 참여 인원 수에 관계없이 진행됩니다</div>
            </div>
          </label>
          <label class="flex items-start gap-2 p-3 rounded-lg border cursor-pointer transition"
            :class="form.end_type === 'flexible' ? 'border-amber-400 bg-amber-50' : 'border-gray-200 hover:bg-gray-50'">
            <input v-model="form.end_type" type="radio" value="flexible" class="mt-0.5 accent-amber-500" />
            <div>
              <div class="text-sm font-semibold text-gray-800">최소 인원 미달 시 자동 취소</div>
              <div class="text-xs text-gray-400">마감일까지 최소 인원에 도달하지 못하면 자동 취소됩니다</div>
            </div>
          </label>
        </div>
      </div>

      <!-- 10. 할인 티어 -->
      <div>
        <label class="text-sm font-semibold text-gray-700 mb-2 block">할인 티어 (선택)</label>
        <div class="space-y-2">
          <div v-for="(tier, idx) in form.discount_tiers" :key="idx"
            class="flex items-center gap-2 bg-gray-50 rounded-lg p-3">
            <div class="flex-1 flex items-center gap-2">
              <label class="text-xs text-gray-500 flex-shrink-0">최소</label>
              <input v-model.number="tier.min_people" type="number" min="2" placeholder="10"
                class="border rounded-lg px-2 py-1.5 text-sm w-20 focus:ring-2 focus:ring-amber-400 outline-none" />
              <label class="text-xs text-gray-500 flex-shrink-0">명 이상</label>
            </div>
            <div class="flex-1 flex items-center gap-2">
              <label class="text-xs text-gray-500 flex-shrink-0">할인</label>
              <input v-model.number="tier.discount_pct" type="number" min="1" max="100" placeholder="10"
                class="border rounded-lg px-2 py-1.5 text-sm w-20 focus:ring-2 focus:ring-amber-400 outline-none" />
              <label class="text-xs text-gray-500 flex-shrink-0">%</label>
            </div>
            <button @click="removeTier(idx)"
              class="text-red-400 hover:text-red-600 text-lg leading-none flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-full hover:bg-red-50 transition">
              ✕
            </button>
          </div>
        </div>
        <button @click="addTier"
          class="mt-2 text-xs font-semibold text-amber-700 hover:text-amber-900 border border-amber-300 rounded-lg px-3 py-1.5 hover:bg-amber-50 transition">
          + 할인 티어 추가
        </button>
      </div>

      <!-- 11. 지역 -->
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="text-sm font-semibold text-gray-700">City</label>
          <input v-model="form.city" type="text" placeholder="Los Angeles"
            class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
        <div>
          <label class="text-sm font-semibold text-gray-700">State</label>
          <input v-model="form.state" type="text" placeholder="CA"
            class="w-full border rounded-lg px-3 py-2 mt-1 text-sm focus:ring-2 focus:ring-amber-400 outline-none" />
        </div>
      </div>

      <!-- 12. 사업자 등록증 -->
      <div>
        <label class="text-sm font-semibold text-gray-700">사업자 등록증 <span class="text-red-400">*</span></label>
        <div class="mt-1">
          <label class="flex items-center gap-2 border-2 border-dashed border-gray-300 rounded-lg px-4 py-3 cursor-pointer hover:border-amber-400 hover:bg-amber-50/50 transition">
            <span class="text-gray-400 text-lg">📎</span>
            <span class="text-sm text-gray-500">{{ businessDocName || '파일을 선택하세요 (PDF, JPG, PNG)' }}</span>
            <input type="file" accept=".pdf,.jpg,.jpeg,.png" @change="onBusinessDoc" class="hidden" />
          </label>
        </div>
        <div class="text-[10px] text-gray-400 mt-1">관리자 승인 시 사업자 등록증을 확인합니다</div>
      </div>

      <!-- 안내문 -->
      <div class="bg-amber-50 border border-amber-200 rounded-lg p-3">
        <div class="flex items-start gap-2">
          <span class="text-amber-500 flex-shrink-0">⚠️</span>
          <div class="text-xs text-amber-800 leading-relaxed">
            <b>등록 후 관리자 승인이 필요합니다.</b> 사업자 등록증 확인 후 승인됩니다.
          </div>
        </div>
      </div>

      <!-- 에러 -->
      <div v-if="error" class="text-red-500 text-sm">{{ error }}</div>

      <!-- 버튼 -->
      <div class="flex gap-3 pt-2">
        <button @click="submit" :disabled="submitting"
          class="bg-amber-400 text-amber-900 font-bold px-6 py-2.5 rounded-lg hover:bg-amber-500 disabled:opacity-50 transition">
          {{ submitting ? '등록 중...' : '등록하기' }}
        </button>
        <button @click="$router.back()" class="text-gray-500 px-6 py-2.5">취소</button>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const router = useRouter()
const auth = useAuthStore()

const categories = [
  { value: 'food', label: '🍱 식품' },
  { value: 'beauty', label: '💄 뷰티' },
  { value: 'electronics', label: '📱 전자제품' },
  { value: 'living', label: '🏠 생활용품' },
  { value: 'fashion', label: '👗 패션' },
  { value: 'health', label: '💊 건강' },
  { value: 'education', label: '📚 교육' },
  { value: 'etc', label: '📋 기타' },
]

const form = reactive({
  title: '',
  content: '',
  category: 'food',
  original_price: null,
  group_price: null,
  product_url: '',
  min_participants: 2,
  max_participants: 50,
  deadline: '',
  end_type: 'target_met',
  discount_tiers: [],
  city: '',
  state: '',
})

// 사진 관리
const photoList = ref([])

function onSelectPhotos(e) {
  const newFiles = Array.from(e.target.files)
  const total = photoList.value.length + newFiles.length
  if (total > 5) {
    alert('사진은 최대 5장까지 등록 가능합니다')
    return
  }
  for (const f of newFiles) {
    const reader = new FileReader()
    reader.onload = ev => {
      photoList.value.push({ file: f, preview: ev.target.result })
    }
    reader.readAsDataURL(f)
  }
  e.target.value = ''
}

function removePhoto(idx) {
  photoList.value.splice(idx, 1)
}

// 사업자 등록증
const businessDoc = ref(null)
const businessDocName = ref('')

function onBusinessDoc(e) {
  const file = e.target.files[0]
  if (file) {
    businessDoc.value = file
    businessDocName.value = file.name
  }
}

// 할인 티어
function addTier() {
  form.discount_tiers.push({ min_people: null, discount_pct: null })
}

function removeTier(idx) {
  form.discount_tiers.splice(idx, 1)
}

// 제출
const error = ref('')
const submitting = ref(false)

async function submit() {
  if (!form.title.trim()) { error.value = '제목을 입력해주세요'; return }
  if (!form.content.trim()) { error.value = '상세 설명을 입력해주세요'; return }
  if (!businessDoc.value) { error.value = '사업자 등록증을 첨부해주세요'; return }

  submitting.value = true
  error.value = ''

  try {
    const fd = new FormData()
    fd.append('title', form.title)
    fd.append('content', form.content)
    fd.append('category', form.category)
    if (form.original_price) fd.append('original_price', form.original_price)
    if (form.group_price) fd.append('group_price', form.group_price)
    if (form.product_url) fd.append('product_url', form.product_url)
    fd.append('min_participants', form.min_participants)
    fd.append('max_participants', form.max_participants)
    if (form.deadline) fd.append('deadline', form.deadline)
    fd.append('end_type', form.end_type)
    if (form.city) fd.append('city', form.city)
    if (form.state) fd.append('state', form.state)

    // 할인 티어
    const validTiers = form.discount_tiers.filter(t => t.min_people && t.discount_pct)
    if (validTiers.length) {
      fd.append('discount_tiers', JSON.stringify(validTiers))
    }

    // 이미지
    photoList.value.forEach(p => fd.append('images[]', p.file))

    // 사업자 등록증
    fd.append('business_doc', businessDoc.value)

    await axios.post('/api/groupbuys', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    router.push('/groupbuy')
  } catch (e) {
    const msg = e.response?.data?.message || ''
    const errs = e.response?.data?.errors ? Object.values(e.response.data.errors).flat().join(', ') : ''
    error.value = msg || errs || '등록 실패: ' + e.message
  }

  submitting.value = false
}

// 유저 프로필에서 도시/주 자동 채우기
onMounted(() => {
  if (auth.user) {
    if (auth.user.city) form.city = auth.user.city
    if (auth.user.state) form.state = auth.user.state
  }
})
</script>
