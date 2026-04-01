<template>
  <div class="space-y-5">

    <!-- 필터 / 검색 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
      <div class="flex flex-col sm:flex-row gap-3">
        <input v-model="search" @keyup.enter="load" type="text" placeholder="이름, 이메일, 아이디 검색..."
          class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
        <select v-model="filterStatus" @change="load"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 상태</option>
          <option value="active">활성</option>
          <option value="banned">정지</option>
        </select>
        <select v-model="filterRole" @change="load"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 권한</option>
          <option value="admin">관리자</option>
          <option value="user">일반회원</option>
        </select>
        <button @click="load"
          class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition">
          검색
        </button>
      </div>
      <div class="mt-2 text-xs text-gray-400">총 {{ total }}명</div>
    </div>

    <!-- 테이블 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="text-center py-10 text-gray-400 text-sm">불러오는 중...</div>
      <div v-else-if="users.length === 0" class="text-center py-10 text-gray-400 text-sm">회원이 없습니다.</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">회원</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden md:table-cell">이메일</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500 hidden sm:table-cell">가입일</th>
              <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">상태</th>
              <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 transition">
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {{ (user.name || '?')[0] }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-800 text-xs">
                      {{ user.name }}
                      <span v-if="user.is_admin" class="ml-1 text-[10px] bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded-full font-bold">관리자</span>
                    </div>
                    <div class="text-[10px] text-gray-400">@{{ user.username }}</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500 hidden md:table-cell">{{ user.email }}</td>
              <td class="px-4 py-3 text-xs text-gray-400 hidden sm:table-cell">{{ formatDate(user.created_at) }}</td>
              <td class="px-4 py-3">
                <span :class="['text-[10px] px-2 py-0.5 rounded-full font-semibold',
                  user.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600']">
                  {{ user.status === 'active' ? '활성' : '정지' }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-end gap-1.5">
                  <button @click="openDetail(user)"
                    class="text-[10px] bg-blue-50 hover:bg-blue-100 text-blue-600 px-2 py-1 rounded-lg transition">
                    상세
                  </button>
                  <button v-if="user.status === 'active' && !user.is_admin" @click="banUser(user)"
                    class="text-[10px] bg-orange-50 hover:bg-orange-100 text-orange-600 px-2 py-1 rounded-lg transition">
                    정지
                  </button>
                  <button v-if="user.status === 'banned'" @click="unbanUser(user)"
                    class="text-[10px] bg-green-50 hover:bg-green-100 text-green-600 px-2 py-1 rounded-lg transition">
                    해제
                  </button>
                  <button v-if="!user.is_admin" @click="confirmDelete(user)"
                    class="text-[10px] bg-red-50 hover:bg-red-100 text-red-500 px-2 py-1 rounded-lg transition">
                    삭제
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="lastPage > 1" class="flex items-center justify-center gap-2 px-4 py-3 border-t border-gray-100">
        <button @click="changePage(page - 1)" :disabled="page <= 1"
          class="px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition">
          ‹ 이전
        </button>
        <span class="text-xs text-gray-500">{{ page }} / {{ lastPage }}</span>
        <button @click="changePage(page + 1)" :disabled="page >= lastPage"
          class="px-3 py-1.5 text-xs rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition">
          다음 ›
        </button>
      </div>
    </div>

    <!-- 상세 모달 -->
    <div v-if="detailUser" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="detailUser = null">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-bold text-gray-800">회원 상세</h3>
          <button @click="detailUser = null" class="text-gray-400 hover:text-gray-600 text-xl">×</button>
        </div>
        <div class="flex items-center gap-4 mb-4">
          <div class="w-14 h-14 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-2xl font-black">
            {{ (detailUser.name || '?')[0] }}
          </div>
          <div>
            <div class="font-bold text-gray-800">{{ detailUser.name }}
              <span v-if="detailUser.is_admin" class="ml-1 text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full">관리자</span>
            </div>
            <div class="text-xs text-gray-400">@{{ detailUser.username }}</div>
            <div class="text-xs text-gray-400">{{ detailUser.email }}</div>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-3 mb-4">
          <div class="bg-gray-50 rounded-xl p-3 text-center">
            <div class="text-xl font-black text-gray-800">{{ detail.posts ?? 0 }}</div>
            <div class="text-[10px] text-gray-400">게시글</div>
          </div>
          <div class="bg-gray-50 rounded-xl p-3 text-center">
            <div class="text-xl font-black text-gray-800">{{ detail.jobs ?? 0 }}</div>
            <div class="text-[10px] text-gray-400">구인구직</div>
          </div>
          <div class="bg-gray-50 rounded-xl p-3 text-center">
            <div class="text-xl font-black text-gray-800">{{ detail.market ?? 0 }}</div>
            <div class="text-[10px] text-gray-400">중고장터</div>
          </div>
        </div>
        <div class="space-y-2 text-xs text-gray-600 mb-4">
          <div class="flex justify-between"><span class="text-gray-400">가입일</span><span>{{ formatDate(detailUser.created_at) }}</span></div>
          <div class="flex justify-between"><span class="text-gray-400">상태</span>
            <span :class="detailUser.status === 'active' ? 'text-green-600' : 'text-red-500'">
              {{ detailUser.status === 'active' ? '활성' : '정지' }}
            </span>
          </div>
          <div class="flex justify-between"><span class="text-gray-400">포인트</span><span>{{ (detailUser.points ?? 0).toLocaleString() }}P</span></div>
        </div>
        <div class="flex gap-2">
          <button v-if="detailUser.status === 'active' && !detailUser.is_admin" @click="banUser(detailUser); detailUser = null"
            class="flex-1 bg-orange-500 hover:bg-orange-600 text-white py-2 rounded-xl text-sm font-semibold transition">
            계정 정지
          </button>
          <button v-if="detailUser.status === 'banned'" @click="unbanUser(detailUser); detailUser = null"
            class="flex-1 bg-green-500 hover:bg-green-600 text-white py-2 rounded-xl text-sm font-semibold transition">
            정지 해제
          </button>
          <button @click="detailUser = null"
            class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 py-2 rounded-xl text-sm font-semibold transition">
            닫기
          </button>
        </div>
      </div>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" @click.self="deleteTarget = null">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 text-center">
        <div class="text-4xl mb-3">⚠️</div>
        <h3 class="font-bold text-gray-800 mb-2">회원 삭제</h3>
        <p class="text-sm text-gray-500 mb-5">
          <strong>{{ deleteTarget.name }}</strong> 회원을 삭제하면 모든 데이터가 사라집니다. 계속하시겠습니까?
        </p>
        <div class="flex gap-3">
          <button @click="deleteUser" class="flex-1 bg-red-500 hover:bg-red-600 text-white py-2.5 rounded-xl text-sm font-bold transition">삭제</button>
          <button @click="deleteTarget = null" class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 py-2.5 rounded-xl text-sm font-semibold transition">취소</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const users        = ref([])
const total        = ref(0)
const page         = ref(1)
const lastPage     = ref(1)
const loading      = ref(false)
const search       = ref('')
const filterStatus = ref('')
const filterRole   = ref('')
const detailUser   = ref(null)
const detail       = ref({})
const deleteTarget = ref(null)

async function load() {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/users', {
      params: { page: page.value, search: search.value, status: filterStatus.value, role: filterRole.value }
    })
    users.value    = res.data.data
    total.value    = res.data.total
    lastPage.value = res.data.last_page
  } finally {
    loading.value = false
  }
}

function changePage(p) {
  if (p < 1 || p > lastPage.value) return
  page.value = p
  load()
}

async function openDetail(user) {
  detailUser.value = user
  detail.value = {}
  try {
    const res = await axios.get(`/api/admin/users/${user.id}`)
    detail.value = res.data
    detailUser.value = res.data.user ?? user
  } catch {}
}

async function banUser(user) {
  await axios.post(`/api/admin/users/${user.id}/ban`)
  user.status = 'banned'
}

async function unbanUser(user) {
  await axios.post(`/api/admin/users/${user.id}/unban`)
  user.status = 'active'
}

function confirmDelete(user) {
  deleteTarget.value = user
}

async function deleteUser() {
  if (!deleteTarget.value) return
  await axios.delete(`/api/admin/users/${deleteTarget.value.id}`)
  users.value = users.value.filter(u => u.id !== deleteTarget.value.id)
  total.value--
  deleteTarget.value = null
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('ko-KR', { year: '2-digit', month: 'numeric', day: 'numeric' })
}

onMounted(load)
</script>
