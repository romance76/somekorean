<template>
<div>
  <h1 class="text-xl font-black text-gray-800 mb-4">📝 콘텐츠 관리</h1>

  <!-- 검색 + 필터 -->
  <div class="bg-white rounded-xl shadow-sm border p-3 mb-4">
    <div class="flex flex-wrap gap-2">
      <select v-model="boardFilter" @change="load()" class="border rounded-lg px-2 py-1.5 text-xs outline-none">
        <option value="">전체 게시판</option>
        <option v-for="b in boards" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <form @submit.prevent="load()" class="flex-1 flex gap-1 min-w-[150px]">
        <input v-model="search" type="text" placeholder="제목/작성자 검색..." class="flex-1 border rounded-lg px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-amber-400" />
        <button type="submit" class="bg-amber-400 text-amber-900 font-bold px-3 py-1.5 rounded-lg text-xs">검색</button>
      </form>
    </div>
    <div class="text-[10px] text-gray-400 mt-1">전체 {{ totalPosts }}건</div>
  </div>

  <div class="flex gap-4">
    <!-- 왼쪽: 목록 -->
    <div :class="activePost ? 'w-1/2' : 'w-full'">
      <div v-if="loading" class="text-center py-8 text-gray-400">로딩중...</div>
      <div v-else class="bg-white rounded-xl shadow-sm border overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b"><tr>
            <th class="px-2 py-2 text-left text-xs text-gray-500 w-8">#</th>
            <th class="px-2 py-2 text-left text-xs text-gray-500">제목</th>
            <th v-if="!activePost" class="px-2 py-2 text-left text-xs text-gray-500">게시판</th>
            <th class="px-2 py-2 text-left text-xs text-gray-500">작성자</th>
            <th class="px-2 py-2 text-xs text-gray-500">💬</th>
            <th class="px-2 py-2 text-xs text-gray-500">👁</th>
            <th class="px-2 py-2 text-xs text-gray-500">날짜</th>
            <th class="px-2 py-2 text-xs text-gray-500">관리</th>
          </tr></thead>
          <tbody>
            <tr v-for="p in posts" :key="p.id"
              class="border-b last:border-0 hover:bg-amber-50/30 cursor-pointer transition"
              :class="[p.is_hidden ? 'opacity-40 bg-red-50/30' : '', activePost?.id===p.id ? 'bg-amber-50 border-l-2 border-l-amber-500' : '']"
              @click="openPost(p)">
              <td class="px-2 py-2 text-xs text-gray-400">{{ p.id }}</td>
              <td class="px-2 py-2 max-w-[200px]">
                <div class="truncate text-sm font-medium text-gray-800">
                  <span v-if="p.is_pinned" class="text-amber-500 mr-1">📌</span>
                  {{ p.title }}
                </div>
              </td>
              <td v-if="!activePost" class="px-2 py-2"><span class="text-[10px] bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded-full">{{ p.board?.name || '-' }}</span></td>
              <td class="px-2 py-2">
                <button @click.stop="openUserModal(p.user)" class="text-xs text-blue-600 hover:underline">{{ p.user?.name }}</button>
              </td>
              <td class="px-2 py-2 text-center text-xs text-gray-500">{{ p.comment_count }}</td>
              <td class="px-2 py-2 text-center text-xs text-gray-400">{{ p.view_count }}</td>
              <td class="px-2 py-2 text-[10px] text-gray-400">{{ p.created_at?.slice(5,10) }}</td>
              <td class="px-2 py-2 text-center space-x-1" @click.stop>
                <button @click="pinPost(p)" class="text-xs" :class="p.is_pinned?'text-amber-500':'text-gray-300 hover:text-amber-500'">📌</button>
                <button @click="hidePost(p)" class="text-xs" :class="p.is_hidden?'text-green-500':'text-gray-300 hover:text-red-500'">{{ p.is_hidden ? '👁' : '🚫' }}</button>
                <button @click="deletePost(p)" class="text-xs text-gray-300 hover:text-red-600">🗑</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="lastPage > 1" class="flex justify-center gap-1.5 mt-4">
        <button v-for="pg in Math.min(lastPage, 10)" :key="pg" @click="load(pg)"
          class="px-3 py-1 rounded text-sm" :class="pg===page?'bg-amber-400 text-amber-900 font-bold':'bg-white border text-gray-600'">{{ pg }}</button>
      </div>
    </div>

    <!-- 오른쪽: 인라인 게시글 뷰 -->
    <div v-if="activePost" class="w-1/2">
      <div class="bg-white rounded-xl shadow-sm border overflow-hidden sticky top-4">
        <div class="px-4 py-3 border-b flex items-center justify-between bg-amber-50">
          <span class="font-bold text-sm text-amber-900">게시글 상세</span>
          <button @click="activePost=null" class="text-gray-400 hover:text-gray-600 text-lg">✕</button>
        </div>
        <div class="px-4 py-3">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-[10px] bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full font-semibold">{{ activePost.board?.name || '게시판' }}</span>
            <span v-if="activePost.is_pinned" class="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">📌 고정</span>
            <span v-if="activePost.is_hidden" class="text-[10px] bg-red-100 text-red-700 px-2 py-0.5 rounded-full">🚫 숨김</span>
          </div>
          <h2 class="text-lg font-bold text-gray-900">{{ activePost.title }}</h2>
          <div class="flex items-center gap-3 mt-2 text-xs text-gray-400">
            <button @click="openUserModal(activePost.user)" class="text-blue-600 hover:underline font-semibold">{{ activePost.user?.name }}</button>
            <span>{{ activePost.user?.email }}</span>
            <span>{{ activePost.created_at?.slice(0,10) }}</span>
            <span>조회 {{ activePost.view_count }}</span>
            <span>❤️ {{ activePost.like_count }}</span>
          </div>
        </div>
        <div class="px-4 py-4 border-t text-sm text-gray-700 leading-relaxed whitespace-pre-wrap max-h-[400px] overflow-y-auto">{{ activePost.content }}</div>

        <!-- 댓글 -->
        <div v-if="activePost.comments?.length" class="px-4 py-3 border-t">
          <div class="font-bold text-xs text-gray-800 mb-2">💬 댓글 {{ activePost.comments.length }}개</div>
          <div v-for="c in activePost.comments" :key="c.id" class="py-2 border-b last:border-0">
            <div class="flex items-center gap-2">
              <button @click="openUserModal(c.user)" class="text-xs text-blue-600 hover:underline font-semibold">{{ c.user?.name }}</button>
              <span class="text-[10px] text-gray-400">{{ c.created_at?.slice(0,10) }}</span>
              <button @click="deleteComment(c.id)" class="text-[10px] text-red-400 hover:text-red-600 ml-auto">삭제</button>
            </div>
            <div class="text-xs text-gray-600 mt-0.5">{{ c.content }}</div>
          </div>
        </div>

        <!-- 관리 버튼 -->
        <div class="px-4 py-3 border-t flex gap-2">
          <button @click="pinPost(activePost)" class="text-xs px-3 py-1.5 rounded-lg" :class="activePost.is_pinned?'bg-amber-100 text-amber-700':'bg-gray-100 text-gray-600'">
            📌 {{ activePost.is_pinned ? '고정 해제' : '고정' }}
          </button>
          <button @click="hidePost(activePost)" class="text-xs px-3 py-1.5 rounded-lg" :class="activePost.is_hidden?'bg-green-100 text-green-700':'bg-red-100 text-red-700'">
            {{ activePost.is_hidden ? '👁 보이기' : '🚫 숨기기' }}
          </button>
          <button @click="deletePost(activePost); activePost=null" class="text-xs bg-red-100 text-red-700 px-3 py-1.5 rounded-lg">🗑 삭제</button>
        </div>
      </div>
    </div>
  </div>

  <!-- ═══ 회원 상세 모달 ═══ -->
  <div v-if="userModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="userModal=null">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto">
      <div class="px-5 py-4 border-b flex items-center justify-between bg-amber-50 sticky top-0">
        <span class="font-bold text-amber-900">👤 회원 상세 정보</span>
        <button @click="userModal=null" class="text-gray-400 hover:text-gray-600 text-xl">✕</button>
      </div>

      <div v-if="userLoading" class="py-12 text-center text-gray-400">로딩중...</div>
      <div v-else-if="userData" class="p-5">
        <!-- 탭 -->
        <div class="flex gap-1 mb-4 border-b">
          <button v-for="t in userTabs" :key="t.key" @click="userTab=t.key"
            class="px-4 py-2 text-sm font-medium border-b-2 -mb-px transition"
            :class="userTab===t.key?'border-amber-500 text-amber-700':'border-transparent text-gray-500 hover:text-gray-700'">{{ t.label }}</button>
        </div>

        <!-- 기본 정보 (수정 가능) -->
        <div v-show="userTab==='info'">
          <div class="grid grid-cols-2 gap-3">
            <div><label class="text-xs text-gray-500">이름</label><input v-model="userData.user.name" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
            <div><label class="text-xs text-gray-500">닉네임</label><input v-model="userData.user.nickname" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
            <div><label class="text-xs text-gray-500">이메일</label><input v-model="userData.user.email" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
            <div><label class="text-xs text-gray-500">전화번호</label><input v-model="userData.user.phone" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
            <div><label class="text-xs text-gray-500">도시</label><input v-model="userData.user.city" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
            <div><label class="text-xs text-gray-500">주</label><input v-model="userData.user.state" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
            <div><label class="text-xs text-gray-500">역할</label>
              <select v-model="userData.user.role" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5">
                <option value="user">일반회원</option><option value="admin">관리자</option><option value="super_admin">슈퍼관리자</option>
              </select>
            </div>
            <div><label class="text-xs text-gray-500">상태</label>
              <select v-model="userData.user.is_banned" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5">
                <option :value="false">정상</option><option :value="true">정지</option>
              </select>
            </div>
            <div><label class="text-xs text-gray-500">포인트</label><input v-model.number="userData.user.points" type="number" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
            <div><label class="text-xs text-gray-500">게임포인트</label><input v-model.number="userData.user.game_points" type="number" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5" /></div>
          </div>
          <div class="mt-2"><label class="text-xs text-gray-500">소개</label><textarea v-model="userData.user.bio" rows="2" class="w-full border rounded px-2 py-1.5 text-sm mt-0.5 resize-none"></textarea></div>
          <div class="mt-3 flex items-center gap-3 text-xs text-gray-400">
            <span>가입일: {{ userData.user.created_at?.slice(0,10) }}</span>
            <span>최근 로그인: {{ userData.user.last_login_at?.slice(0,10) || '없음' }}</span>
            <span>로그인 {{ userData.user.login_count || 0 }}회</span>
          </div>
          <button @click="saveUser" class="mt-4 bg-amber-400 text-amber-900 font-bold px-5 py-2 rounded-lg text-sm hover:bg-amber-500">저장하기</button>
        </div>

        <!-- 결제 내역 -->
        <div v-show="userTab==='payments'">
          <div v-if="!userData.payments?.length" class="py-6 text-center text-gray-400 text-sm">결제 내역 없음</div>
          <table v-else class="w-full text-sm"><thead class="bg-gray-50"><tr>
            <th class="px-2 py-1.5 text-xs text-left text-gray-500">날짜</th><th class="px-2 py-1.5 text-xs text-left text-gray-500">금액</th><th class="px-2 py-1.5 text-xs text-left text-gray-500">포인트</th><th class="px-2 py-1.5 text-xs text-left text-gray-500">상태</th>
          </tr></thead><tbody>
            <tr v-for="pay in userData.payments" :key="pay.id" class="border-b"><td class="px-2 py-1.5 text-xs">{{ pay.created_at?.slice(0,10) }}</td><td class="px-2 py-1.5 text-xs">${{ pay.amount }}</td><td class="px-2 py-1.5 text-xs text-amber-600 font-bold">+{{ pay.points }}P</td><td class="px-2 py-1.5 text-xs">{{ pay.status }}</td></tr>
          </tbody></table>
        </div>

        <!-- 포인트 내역 -->
        <div v-show="userTab==='points'">
          <div v-if="!userData.points?.length" class="py-6 text-center text-gray-400 text-sm">포인트 내역 없음</div>
          <table v-else class="w-full text-sm"><thead class="bg-gray-50"><tr>
            <th class="px-2 py-1.5 text-xs text-left text-gray-500">날짜</th><th class="px-2 py-1.5 text-xs text-left text-gray-500">사유</th><th class="px-2 py-1.5 text-xs text-right text-gray-500">포인트</th>
          </tr></thead><tbody>
            <tr v-for="pt in userData.points" :key="pt.id" class="border-b"><td class="px-2 py-1.5 text-xs">{{ pt.created_at?.slice(0,10) }}</td><td class="px-2 py-1.5 text-xs">{{ pt.reason }}</td><td class="px-2 py-1.5 text-xs text-right font-bold" :class="pt.amount>0?'text-green-600':'text-red-600'">{{ pt.amount>0?'+':'' }}{{ pt.amount }}P</td></tr>
          </tbody></table>
        </div>

        <!-- 게시글 -->
        <div v-show="userTab==='posts'">
          <div v-if="!userData.posts?.length" class="py-6 text-center text-gray-400 text-sm">작성한 글 없음</div>
          <div v-for="post in userData.posts" :key="post.id" class="py-2 border-b flex items-center justify-between">
            <div><div class="text-sm font-medium text-gray-800">{{ post.title }}</div><div class="text-[10px] text-gray-400">{{ post.created_at?.slice(0,10) }} · 조회 {{ post.view_count }}</div></div>
            <button @click="openPost(post); userModal=null" class="text-xs text-amber-600 hover:underline">보기</button>
          </div>
        </div>

        <!-- 댓글 -->
        <div v-show="userTab==='comments'">
          <div v-if="!userData.comments?.length" class="py-6 text-center text-gray-400 text-sm">작성한 댓글 없음</div>
          <div v-for="c in userData.comments" :key="c.id" class="py-2 border-b">
            <div class="text-sm text-gray-700">{{ c.content }}</div>
            <div class="text-[10px] text-gray-400 mt-0.5">{{ c.created_at?.slice(0,10) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const posts = ref([]); const boards = ref([]); const loading = ref(true)
const page = ref(1); const lastPage = ref(1); const totalPosts = ref(0)
const search = ref(''); const boardFilter = ref('')
const activePost = ref(null)

// 회원 모달
const userModal = ref(null)
const userData = ref(null)
const userLoading = ref(false)
const userTab = ref('info')
const userTabs = [
  { key: 'info', label: '기본정보' },
  { key: 'payments', label: '결제내역' },
  { key: 'points', label: '포인트' },
  { key: 'posts', label: '게시글' },
  { key: 'comments', label: '댓글' },
]

async function load(p=1) {
  loading.value=true; page.value=p
  const params = { page: p }
  if (search.value) params.search = search.value
  if (boardFilter.value) params.board_id = boardFilter.value
  try {
    const { data } = await axios.get('/api/admin/posts', { params })
    posts.value = data.data?.data || []
    lastPage.value = data.data?.last_page || 1
    totalPosts.value = data.data?.total || 0
  } catch {}
  loading.value = false
}

async function openPost(p) {
  try {
    const { data } = await axios.get(`/api/admin/posts/${p.id}/detail`)
    activePost.value = data.data
  } catch { activePost.value = p }
}

async function openUserModal(user) {
  if (!user?.id) return
  userModal.value = user; userLoading.value = true; userData.value = null; userTab.value = 'info'
  try {
    const { data } = await axios.get(`/api/admin/users/${user.id}/detail`)
    userData.value = data.data
  } catch {}
  userLoading.value = false
}

async function saveUser() {
  if (!userData.value?.user) return
  try {
    await axios.put(`/api/admin/users/${userData.value.user.id}`, userData.value.user)
    alert('저장되었습니다!')
  } catch (e) { alert(e.response?.data?.message || '저장 실패') }
}

async function deleteComment(id) {
  if (!confirm('댓글 삭제?')) return
  try { await axios.delete(`/api/comments/${id}`); if (activePost.value?.comments) activePost.value.comments = activePost.value.comments.filter(c=>c.id!==id) } catch {}
}

async function pinPost(p) { try { await axios.post(`/api/admin/posts/${p.id}/pin`); p.is_pinned=!p.is_pinned } catch {} }
async function hidePost(p) { try { await axios.post(`/api/admin/posts/${p.id}/hide`); p.is_hidden=!p.is_hidden } catch {} }
async function deletePost(p) { if(!confirm('삭제?'))return; try { await axios.delete(`/api/admin/posts/${p.id}`); posts.value=posts.value.filter(x=>x.id!==p.id) } catch {} }

onMounted(async () => {
  try { const { data } = await axios.get('/api/admin/boards'); boards.value = data.data || [] } catch {}
  load()
})
</script>
