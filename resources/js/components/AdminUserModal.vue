<template>
<div v-if="show" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
  <div class="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
    <div class="px-5 py-4 border-b flex items-center justify-between bg-amber-50 sticky top-0 z-10">
      <span class="font-bold text-amber-900">👤 회원 상세 정보</span>
      <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 text-xl">✕</button>
    </div>
    <div v-if="loading" class="py-12 text-center text-gray-400">로딩중...</div>
    <div v-else-if="data" class="p-5">
      <div class="flex gap-1 mb-4 border-b">
        <button v-for="t in tabs" :key="t.key" @click="tab=t.key"
          class="px-4 py-2 text-sm font-medium border-b-2 -mb-px transition"
          :class="tab===t.key?'border-amber-500 text-amber-700':'border-transparent text-gray-500'">{{ t.label }}</button>
      </div>

      <div v-show="tab==='info'">
        <div class="grid grid-cols-2 gap-3">
          <div><label class="text-xs text-gray-500">이름</label><input v-model="data.user.name" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
          <div><label class="text-xs text-gray-500">닉네임</label><input v-model="data.user.nickname" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
          <div><label class="text-xs text-gray-500">이메일</label><input v-model="data.user.email" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
          <div><label class="text-xs text-gray-500">전화</label><input v-model="data.user.phone" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
          <div><label class="text-xs text-gray-500">도시</label><input v-model="data.user.city" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
          <div><label class="text-xs text-gray-500">역할</label>
            <select v-model="data.user.role" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5"><option value="user">일반</option><option value="admin">관리자</option><option value="super_admin">슈퍼</option></select>
          </div>
          <div><label class="text-xs text-gray-500">포인트</label><input v-model.number="data.user.points" type="number" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
          <div><label class="text-xs text-gray-500">상태</label>
            <select v-model="data.user.is_banned" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5"><option :value="false">정상</option><option :value="true">정지</option></select>
          </div>
        </div>
        <div class="mt-3 text-xs text-gray-400">가입: {{ data.user.created_at?.slice(0,10) }} · 로그인 {{ data.user.login_count||0 }}회</div>
        <button @click="saveUser" class="mt-3 bg-amber-400 text-amber-900 font-bold px-5 py-2 rounded-lg text-sm hover:bg-amber-500">저장</button>
      </div>

      <div v-show="tab==='payments'">
        <div v-if="!data.payments?.length" class="py-6 text-center text-gray-400 text-sm">결제 내역 없음</div>
        <div v-for="p in data.payments" :key="p.id" class="py-2 border-b flex justify-between text-xs">
          <span>{{ p.created_at?.slice(0,10) }}</span><span>${{ p.amount }}</span><span class="text-amber-600 font-bold">+{{ p.points }}P</span><span>{{ p.status }}</span>
        </div>
      </div>

      <div v-show="tab==='points'">
        <div v-if="!data.points?.length" class="py-6 text-center text-gray-400 text-sm">포인트 내역 없음</div>
        <div v-for="pt in data.points" :key="pt.id" class="py-2 border-b flex justify-between text-xs">
          <span>{{ pt.created_at?.slice(0,10) }}</span><span>{{ pt.reason }}</span><span :class="pt.amount>0?'text-green-600':'text-red-600'" class="font-bold">{{ pt.amount>0?'+':'' }}{{ pt.amount }}P</span>
        </div>
      </div>

      <div v-show="tab==='posts'">
        <div v-if="!data.posts?.length" class="py-6 text-center text-gray-400 text-sm">게시글 없음</div>
        <div v-for="post in data.posts" :key="post.id" class="py-2 border-b">
          <div class="text-sm font-medium text-gray-800">{{ post.title }}</div>
          <div class="text-[10px] text-gray-400">{{ post.created_at?.slice(0,10) }} · 조회 {{ post.view_count }}</div>
        </div>
      </div>

      <div v-show="tab==='comments'">
        <div v-if="!data.comments?.length" class="py-6 text-center text-gray-400 text-sm">댓글 없음</div>
        <div v-for="c in data.comments" :key="c.id" class="py-2 border-b">
          <div class="text-sm text-gray-700">{{ c.content }}</div>
          <div class="text-[10px] text-gray-400">{{ c.created_at?.slice(0,10) }}</div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps({ show: Boolean, userId: [Number, String] })
const emit = defineEmits(['close'])

const data = ref(null); const loading = ref(false); const tab = ref('info')
const tabs = [{ key:'info',label:'기본정보' },{ key:'payments',label:'결제' },{ key:'points',label:'포인트' },{ key:'posts',label:'게시글' },{ key:'comments',label:'댓글' }]

watch(() => props.userId, async (id) => {
  if (!id) return
  loading.value = true; data.value = null; tab.value = 'info'
  try { const { data: res } = await axios.get(`/api/admin/users/${id}/detail`); data.value = res.data } catch {}
  loading.value = false
}, { immediate: true })

async function saveUser() {
  if (!data.value?.user) return
  try { await axios.put(`/api/admin/users/${data.value.user.id}`, data.value.user); alert('저장!') } catch (e) { alert(e.response?.data?.message || '실패') }
}
</script>
