<template>
  <div class="space-y-5">

    <!-- 헤더 -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-bold text-gray-800">친구 관리</h2>
        <p class="text-xs text-gray-400 mt-0.5">회원 간 친구 관계 및 차단 현황을 관리합니다</p>
      </div>
    </div>

    <!-- 통계 카드 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-xl">🤝</div>
          <div>
            <p class="text-xs text-gray-400 font-medium">전체 친구 연결</p>
            <p class="text-2xl font-bold text-gray-800">{{ stats.total }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center text-xl">✨</div>
          <div>
            <p class="text-xs text-gray-400 font-medium">오늘 신규</p>
            <p class="text-2xl font-bold text-green-600">{{ stats.today }}</p>
          </div>
        </div>
      </div>
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center text-xl">🚫</div>
          <div>
            <p class="text-xs text-gray-400 font-medium">차단된 관계</p>
            <p class="text-2xl font-bold text-red-500">{{ stats.blocked }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 필터 -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex flex-wrap gap-3 items-center">
      <input
        v-model="search"
        type="text"
        placeholder="회원 이름 검색..."
        class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition w-48"
      />
      <select
        v-model="filterStatus"
        class="border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition"
      >
        <option value="">전체 상태</option>
        <option value="friends">친구</option>
        <option value="blocked">차단</option>
      </select>
      <button
        @click="search = ''; filterStatus = ''"
        class="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
      >
        초기화
      </button>
      <span class="ml-auto text-xs text-gray-400">총 {{ filteredFriends.length }}건</span>
    </div>

    <!-- 테이블 -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-100">
          <tr>
            <th class="text-left px-4 py-3 font-semibold text-gray-600 text-xs">사용자 1</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-600 text-xs">사용자 2</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-600 text-xs">연결일</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-600 text-xs">관계 상태</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-600 text-xs">관리</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-if="filteredFriends.length === 0">
            <td colspan="5" class="text-center py-12 text-gray-400 text-sm">친구 관계가 없습니다</td>
          </tr>
          <tr
            v-for="rel in filteredFriends"
            :key="rel.id"
            class="hover:bg-gray-50 transition-colors"
          >
            <!-- 사용자 1 -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-600">
                  {{ rel.user1.name[0] }}
                </div>
                <div>
                  <p class="font-medium text-gray-800 text-xs">{{ rel.user1.name }}</p>
                  <p class="text-gray-400 text-xs">@{{ rel.user1.username }}</p>
                </div>
              </div>
            </td>
            <!-- 사용자 2 -->
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-7 h-7 rounded-full bg-green-100 flex items-center justify-center text-xs font-bold text-green-600">
                  {{ rel.user2.name[0] }}
                </div>
                <div>
                  <p class="font-medium text-gray-800 text-xs">{{ rel.user2.name }}</p>
                  <p class="text-gray-400 text-xs">@{{ rel.user2.username }}</p>
                </div>
              </div>
            </td>
            <!-- 연결일 -->
            <td class="px-4 py-3 text-gray-500 text-xs whitespace-nowrap">{{ rel.created_at }}</td>
            <!-- 관계 상태 -->
            <td class="px-4 py-3">
              <span
                class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold"
                :class="rel.status === 'friends'
                  ? 'bg-green-50 text-green-700'
                  : 'bg-red-50 text-red-600'"
              >
                <span>{{ rel.status === 'friends' ? '🤝' : '🚫' }}</span>
                {{ rel.status === 'friends' ? '친구' : '차단' }}
              </span>
            </td>
            <!-- 관리 -->
            <td class="px-4 py-3">
              <button
                @click="deleteRelation(rel.id)"
                class="px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg border border-red-200 transition"
              >
                삭제
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 삭제 확인 모달 -->
    <div v-if="deleteModal.show" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 shadow-xl w-80">
        <h3 class="font-bold text-gray-800 mb-2">친구 관계 삭제</h3>
        <p class="text-sm text-gray-500 mb-5">이 친구 관계를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.</p>
        <div class="flex gap-2">
          <button
            @click="deleteModal.show = false"
            class="flex-1 px-4 py-2 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
          >
            취소
          </button>
          <button
            @click="confirmDelete"
            class="flex-1 px-4 py-2 text-sm font-semibold text-white bg-red-500 hover:bg-red-600 rounded-lg transition"
          >
            삭제
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

// ─── Stats ───────────────────────────────────────────────────────────────────
const stats = reactive({ total: 0, today: 0, blocked: 0 })

// ─── Dummy Data ──────────────────────────────────────────────────────────────
const friends = ref([])

// ─── Filter ──────────────────────────────────────────────────────────────────
const search = ref('')
const filterStatus = ref('')

const filteredFriends = computed(() => {
  return friends.value.filter(rel => {
    const matchSearch = !search.value ||
      rel.user1.name.includes(search.value) ||
      rel.user2.name.includes(search.value) ||
      rel.user1.username.includes(search.value) ||
      rel.user2.username.includes(search.value)
    const matchStatus = !filterStatus.value || rel.status === filterStatus.value
    return matchSearch && matchStatus
  })
})

// ─── Delete ──────────────────────────────────────────────────────────────────
const deleteModal = reactive({ show: false, id: null })

function deleteRelation(id) {
  deleteModal.id = id
  deleteModal.show = true
}

function confirmDelete() {
  friends.value = friends.value.filter(r => r.id !== deleteModal.id)
  stats.total = friends.value.filter(r => r.status === 'friends').length + friends.value.filter(r => r.status === 'blocked').length
  stats.blocked = friends.value.filter(r => r.status === 'blocked').length
  deleteModal.show = false
  deleteModal.id = null
}

async function loadFriendsData() {
  try {
    const { data } = await axios.get('/api/admin/friends/stats')
    Object.assign(stats, data)
  } catch(e) {}
}

onMounted(loadFriendsData)

</script>
