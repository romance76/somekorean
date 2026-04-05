<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-20 text-gray-400">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-3"></div>
        <p class="text-sm">불러오는 중...</p>
      </div>

      <template v-else-if="club">
        <!-- Back button -->
        <button @click="$router.push('/clubs')" class="flex items-center gap-1 text-sm text-gray-500 hover:text-blue-600 transition mb-3">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
          동호회 목록
        </button>

        <!-- Club header banner -->
        <div class="rounded-2xl overflow-hidden mb-4 shadow-sm">
          <div class="h-40 sm:h-48 relative"
            :style="{ background: `linear-gradient(135deg, ${club.gradient_from || '#6366F1'}, ${club.gradient_to || '#8B5CF6'})` }">
            <div class="absolute inset-0 bg-black/10"></div>
            <div class="absolute bottom-0 left-0 right-0 p-5 bg-gradient-to-t from-black/40 to-transparent">
              <div class="flex items-end gap-4">
                <div class="w-14 h-14 rounded-full border-4 border-white flex items-center justify-center text-2xl font-bold text-white shadow-lg flex-shrink-0"
                  :style="{ background: `linear-gradient(135deg, ${club.gradient_from || '#6366F1'}, ${club.gradient_to || '#8B5CF6'})` }">
                  {{ club.name?.[0] || '👥' }}
                </div>
                <div class="text-white pb-1 flex-1 min-w-0">
                  <h1 class="text-xl font-black truncate">{{ club.name }}</h1>
                  <div class="flex items-center gap-2 text-sm text-white/80 mt-0.5 flex-wrap">
                    <span class="bg-white/20 px-2 py-0.5 rounded-full text-xs">{{ club.category }}</span>
                    <span>👤 {{ club.member_count || members.length }}명</span>
                    <span v-if="club.is_online" class="bg-blue-400/80 px-2 py-0.5 rounded-full text-xs">🌐 온라인</span>
                    <span v-else-if="club.region || club.zip_code" class="bg-green-400/80 px-2 py-0.5 rounded-full text-xs">📍 {{ club.region || club.zip_code }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Description + Join button -->
          <div class="bg-white dark:bg-gray-800 p-5">
            <div class="flex items-start justify-between gap-4">
              <p class="text-sm text-gray-600 dark:text-gray-300 leading-relaxed flex-1">{{ club.description }}</p>
              <div class="flex-shrink-0">
                <button v-if="!isMember" @click="joinClub"
                  class="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-bold hover:bg-blue-700 transition">
                  {{ club.is_approval ? '가입 신청' : '가입하기' }}
                </button>
                <button v-else-if="!isOwner" @click="leaveClub"
                  class="bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-5 py-2 rounded-lg text-sm font-semibold hover:bg-gray-200 transition">
                  탈퇴하기
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 mb-4 bg-white dark:bg-gray-800 rounded-xl p-1 shadow-sm border border-gray-100 dark:border-gray-700">
          <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
            class="flex-1 py-2 text-sm font-medium rounded-lg transition"
            :class="activeTab === tab.key ? 'bg-blue-600 text-white' : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'">
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab content: Posts -->
        <div v-if="activeTab === 'posts'" class="space-y-4">
          <!-- Write post button -->
          <div v-if="isMember" class="flex justify-end">
            <button @click="showWriteForm = !showWriteForm"
              class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition">
              ✏️ 글쓰기
            </button>
          </div>

          <!-- Write form -->
          <div v-if="showWriteForm && isMember" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-5">
            <h3 class="font-semibold text-gray-800 dark:text-white mb-3">새 글 작성</h3>
            <input v-model="postForm.title" type="text" placeholder="제목을 입력하세요"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2 text-sm mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
            <textarea v-model="postForm.content" rows="4" placeholder="내용을 입력하세요"
              class="w-full border border-gray-200 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2 text-sm mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"></textarea>
            <div class="flex justify-end gap-2">
              <button @click="showWriteForm = false"
                class="px-4 py-2 rounded-lg text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition">취소</button>
              <button @click="submitPost" :disabled="!postForm.title.trim()"
                class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-40 transition">등록</button>
            </div>
          </div>

          <!-- Notices -->
          <div v-if="notices.length" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
            <div class="px-5 py-3 border-b border-gray-100 dark:border-gray-700 bg-yellow-50/50 dark:bg-yellow-900/20">
              <h3 class="font-semibold text-gray-800 dark:text-white text-sm">📌 공지사항</h3>
            </div>
            <div v-for="post in notices" :key="post.id"
              class="px-5 py-3 border-b border-gray-50 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer"
              @click="selectedPost = post">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <span class="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-medium flex-shrink-0">공지</span>
                  <span class="text-sm text-gray-800 dark:text-gray-200 font-medium truncate">{{ post.title }}</span>
                </div>
                <span class="text-xs text-gray-400 flex-shrink-0 ml-2">{{ formatDate(post.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Post list -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
            <div class="px-5 py-3 border-b border-gray-100 dark:border-gray-700">
              <h3 class="font-semibold text-gray-800 dark:text-white text-sm">📝 게시판</h3>
            </div>
            <div v-if="posts.length">
              <div v-for="post in posts" :key="post.id"
                class="px-5 py-4 border-b border-gray-50 dark:border-gray-700 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition"
                @click="selectedPost = post">
                <h4 class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate mb-1">{{ post.title }}</h4>
                <p class="text-xs text-gray-500 line-clamp-2">{{ post.content }}</p>
                <div class="flex items-center gap-3 mt-2 text-xs text-gray-400">
                  <span>{{ post.user?.name || '익명' }}</span>
                  <span>💬 {{ post.comment_count || 0 }}</span>
                  <span>{{ formatDate(post.created_at) }}</span>
                </div>
              </div>
            </div>
            <div v-else class="px-5 py-10 text-center text-gray-400 text-sm">아직 게시글이 없습니다.</div>
          </div>
        </div>

        <!-- Tab content: Members -->
        <div v-if="activeTab === 'members'" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div class="px-5 py-3 border-b border-gray-100 dark:border-gray-700">
            <h3 class="font-semibold text-gray-800 dark:text-white text-sm">👥 회원 ({{ members.length }}명)</h3>
          </div>
          <div class="max-h-[500px] overflow-y-auto">
            <div v-for="member in members" :key="member.id"
              class="px-5 py-3 border-b border-gray-50 dark:border-gray-700 last:border-0 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white">
                  {{ (member.user?.name || member.name || '?')[0] }}
                </div>
                <span class="text-sm text-gray-700 dark:text-gray-300">{{ member.user?.name || member.name }}</span>
              </div>
              <span :class="roleBadgeClass(member.role)">{{ roleName(member.role) }}</span>
            </div>
          </div>
        </div>

        <!-- Post detail modal -->
        <Teleport to="body">
          <div v-if="selectedPost" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click="selectedPost = null">
            <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-y-auto" @click.stop>
              <div class="p-5 border-b border-gray-100 dark:border-gray-700">
                <div class="flex items-start justify-between">
                  <div>
                    <span v-if="selectedPost.is_notice" class="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded font-medium mr-2">공지</span>
                    <h2 class="text-lg font-bold text-gray-900 dark:text-white inline">{{ selectedPost.title }}</h2>
                  </div>
                  <button @click="selectedPost = null" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
                </div>
                <div class="flex items-center gap-2 mt-2 text-xs text-gray-400">
                  <span>{{ selectedPost.user?.name }}</span>
                  <span>{{ formatDate(selectedPost.created_at) }}</span>
                </div>
              </div>
              <div class="p-5">
                <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">{{ selectedPost.content }}</p>
              </div>
            </div>
          </div>
        </Teleport>
      </template>

      <!-- Not found -->
      <div v-else-if="!loading" class="text-center py-20">
        <p class="text-4xl mb-3">😢</p>
        <p class="text-gray-400">동호회를 찾을 수 없습니다.</p>
        <RouterLink to="/clubs" class="mt-3 inline-block text-blue-600 text-sm hover:underline">목록으로 돌아가기</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const club = ref(null)
const members = ref([])
const posts = ref([])
const notices = ref([])
const activeTab = ref('posts')
const showWriteForm = ref(false)
const selectedPost = ref(null)
const postForm = ref({ title: '', content: '' })

const tabs = [
  { key: 'posts', label: '📝 게시판' },
  { key: 'members', label: '👥 멤버' },
]

const isMember = computed(() => {
  if (!auth.user) return false
  return members.value.some(m => (m.user_id || m.user?.id) === auth.user.id)
})

const isOwner = computed(() => {
  if (!auth.user || !club.value) return false
  return club.value.user_id === auth.user.id
})

function roleName(role) {
  return { owner: '방장', admin: '운영자', member: '회원' }[role] || '회원'
}

function roleBadgeClass(role) {
  const base = 'text-[10px] px-2 py-0.5 rounded-full font-medium'
  if (role === 'owner') return `${base} bg-blue-100 text-blue-700`
  if (role === 'admin') return `${base} bg-purple-100 text-purple-700`
  return `${base} bg-gray-100 text-gray-500`
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
}

async function joinClub() {
  if (!auth.isLoggedIn) { router.push('/auth/login'); return }
  try {
    await axios.post(`/api/clubs/${club.value.id}/join`)
    await fetchAll()
    alert(club.value.is_approval ? '가입 신청이 완료되었습니다.' : '가입되었습니다!')
  } catch (e) {
    alert(e.response?.data?.message || '오류가 발생했습니다.')
  }
}

async function leaveClub() {
  if (!confirm('정말로 동호회를 탈퇴하시겠습니까?')) return
  try {
    await axios.post(`/api/clubs/${club.value.id}/leave`)
    await fetchAll()
  } catch (e) {
    alert(e.response?.data?.message || '오류가 발생했습니다.')
  }
}

async function submitPost() {
  try {
    await axios.post(`/api/clubs/${club.value.id}/posts`, postForm.value)
    postForm.value = { title: '', content: '' }
    showWriteForm.value = false
    await fetchPosts()
  } catch (e) {
    alert(e.response?.data?.message || '오류가 발생했습니다.')
  }
}

async function fetchAll() {
  try {
    const { data } = await axios.get(`/api/clubs/${route.params.id}`)
    const c = data.club || data
    club.value = c
    if (c.members?.length) members.value = c.members
  } catch { club.value = null }

  await Promise.all([fetchMembers(), fetchPosts()])
  loading.value = false
}

async function fetchMembers() {
  try {
    const { data } = await axios.get(`/api/clubs/${route.params.id}/members`)
    members.value = data
  } catch {}
}

async function fetchPosts() {
  try {
    const { data } = await axios.get(`/api/clubs/${route.params.id}/posts`)
    const list = data.data || data || []
    notices.value = list.filter(p => p.is_notice)
    posts.value = list.filter(p => !p.is_notice)
  } catch {}
}

onMounted(fetchAll)
</script>
