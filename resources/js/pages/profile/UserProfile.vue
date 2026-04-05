<template>
  <div class="max-w-[1200px] mx-auto px-4 py-6">
    <div v-if="loading" class="text-center py-20 text-gray-400">불러오는 중...</div>
    <template v-else-if="profile">
      <!-- 프로필 헤더 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-4">
        <div class="flex items-center space-x-4">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
            <img v-if="profile.avatar" :src="profile.avatar" :alt="profile.name" class="w-full h-full object-cover rounded-full" />
            <span v-else class="text-2xl font-bold text-red-600">{{ profile.name?.[0] }}</span>
          </div>
          <div class="flex-1">
            <div class="flex items-center space-x-2 mb-1">
              <h1 class="text-lg font-bold text-gray-900">{{ profile.name }}</h1>
              <span class="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded font-medium">{{ profile.level }}</span>
              <!-- 친구 뱃지 -->
              <span v-if="!isMyProfile && friendStatus === 'friends'" class="text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded font-medium">친구</span>
            </div>
            <p class="text-sm text-gray-500">@{{ profile.username }}</p>
            <p v-if="profile.region" class="text-xs text-gray-400 mt-1">📍 {{ profile.region }}</p>
          </div>
          <!-- 본인 프로필: 수정 버튼 -->
          <div v-if="isMyProfile" class="flex-shrink-0">
            <button @click="showEdit = !showEdit" class="text-sm text-red-600 border border-red-200 px-3 py-1.5 rounded-lg hover:bg-red-50">
              프로필 수정
            </button>
          </div>
        </div>

        <!-- 친구 관련 액션 (타인 프로필) -->
        <div v-if="!isMyProfile && friendStatus !== null" class="mt-4 pt-4 border-t border-gray-100">
          <!-- 친구가 아닌 경우 -->
          <div v-if="friendStatus === 'none'" class="flex gap-2">
            <button @click="sendFriendRequest" :disabled="friendLoading"
              class="bg-blue-600 text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition">
              {{ friendLoading ? '요청 중...' : '👋 친구 추가' }}
            </button>
          </div>
          <!-- 이미 친구인 경우 -->
          <div v-else-if="friendStatus === 'friends'" class="flex items-center gap-3">
            <span class="text-sm text-green-600 font-semibold">친구입니다</span>
            <button @click="removeFriend"
              class="text-xs text-red-400 border border-red-200 px-3 py-1.5 rounded-lg hover:bg-red-50 transition">
              친구 삭제
            </button>
          </div>
          <!-- 요청 보낸 상태 -->
          <div v-else-if="friendStatus === 'request_sent'" class="flex items-center gap-2">
            <span class="text-sm text-yellow-600 font-semibold bg-yellow-50 px-3 py-1.5 rounded-lg">요청 대기중</span>
          </div>
          <!-- 요청 받은 상태 -->
          <div v-else-if="friendStatus === 'request_received'" class="flex items-center gap-2">
            <span class="text-sm text-gray-600 mr-2">친구 요청을 받았습니다</span>
            <button @click="acceptFriendRequest" :disabled="friendLoading"
              class="bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition">
              수락
            </button>
            <button @click="rejectFriendRequest" :disabled="friendLoading"
              class="bg-gray-100 text-gray-500 text-sm font-bold px-4 py-2 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition">
              거절
            </button>
          </div>
        </div>

        <p v-if="profile.bio" class="text-sm text-gray-600 mt-3 leading-relaxed">{{ profile.bio }}</p>
        <div class="flex space-x-6 mt-4 pt-4 border-t border-gray-100 text-center">
          <div><p class="font-bold text-gray-800">{{ profile.post_count }}</p><p class="text-xs text-gray-400">게시글</p></div>
          <div><p class="font-bold text-gray-800">{{ profile.comment_count }}</p><p class="text-xs text-gray-400">댓글</p></div>
          <div><p class="font-bold text-gray-800">{{ profile.points?.toLocaleString() }}</p><p class="text-xs text-gray-400">포인트</p></div>
        </div>
      </div>

      <!-- 프로필 수정 폼 (본인만) -->
      <div v-if="showEdit && isMyProfile" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-4">
        <h2 class="font-semibold text-gray-800 mb-4">프로필 수정</h2>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">이름</label>
            <input v-model="editForm.name" type="text" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">자기소개</label>
            <textarea v-model="editForm.bio" rows="3" maxlength="300"
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500 resize-none"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">지역</label>
            <select v-model="editForm.region" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-500">
              <option value="">선택</option>
              <option>Atlanta</option><option>New York</option><option>Los Angeles</option>
              <option>Dallas</option><option>Chicago</option>
            </select>
          </div>
          <div v-if="editError" class="text-red-600 text-sm">{{ editError }}</div>
          <div class="flex justify-end space-x-2">
            <button @click="showEdit = false" class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm hover:bg-gray-50">취소</button>
            <button @click="saveProfile" :disabled="saving" class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50">
              {{ saving ? '저장 중...' : '저장' }}
            </button>
          </div>
        </div>
      </div>

      <!-- 최근 게시글 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-3 border-b border-gray-100">
          <h2 class="font-semibold text-gray-800">최근 게시글</h2>
        </div>
        <div v-if="posts.length === 0" class="text-center py-8 text-gray-400 text-sm">게시글이 없습니다.</div>
        <ul v-else>
          <li v-for="post in posts" :key="post.id" class="px-5 py-3 border-b border-gray-50 last:border-0">
            <router-link :to="`/community/${post.board?.slug || 'general'}/${post.id}`" class="flex items-center justify-between hover:text-red-600">
              <span class="text-sm text-gray-800 truncate flex-1">{{ post.title }}</span>
              <span class="text-xs text-gray-400 ml-3 flex-shrink-0">{{ formatDate(post.created_at) }}</span>
            </router-link>
          </li>
        </ul>
      </div>
    </template>
    <div v-else class="text-center py-20 text-gray-400">사용자를 찾을 수 없습니다.</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import axios from 'axios';

const route = useRoute();
const authStore = useAuthStore();
const profile = ref(null);
const posts = ref([]);
const loading = ref(true);
const showEdit = ref(false);
const saving = ref(false);
const editError = ref('');
const editForm = ref({ name: '', bio: '', region: '' });

// Friend state
const friendStatus = ref(null);
const friendLoading = ref(false);

const isMyProfile = computed(() =>
  authStore.user && (authStore.user.username === route.params.username)
);

// Check friendship status
async function checkFriendship() {
  if (isMyProfile.value || !profile.value?.id || !authStore.user) {
    friendStatus.value = null;
    return;
  }
  try {
    const { data } = await axios.get(`/api/friends/check/${profile.value.id}`);
    friendStatus.value = data.status;
  } catch (e) {
    friendStatus.value = 'none';
  }
}

// Send friend request
async function sendFriendRequest() {
  if (!profile.value?.id) return;
  friendLoading.value = true;
  try {
    await axios.post(`/api/friends/request/${profile.value.id}`);
    friendStatus.value = 'request_sent';
  } catch (e) {
    alert(e?.response?.data?.message || '친구 요청 실패');
  } finally {
    friendLoading.value = false;
  }
}

// Accept friend request
async function acceptFriendRequest() {
  if (!profile.value?.id) return;
  friendLoading.value = true;
  try {
    await axios.post(`/api/friends/accept/${profile.value.id}`);
    friendStatus.value = 'friends';
  } catch (e) {
    alert(e?.response?.data?.message || '수락 실패');
  } finally {
    friendLoading.value = false;
  }
}

// Reject friend request
async function rejectFriendRequest() {
  if (!profile.value?.id) return;
  friendLoading.value = true;
  try {
    await axios.post(`/api/friends/reject/${profile.value.id}`);
    friendStatus.value = 'none';
  } catch (e) {
    alert(e?.response?.data?.message || '거절 실패');
  } finally {
    friendLoading.value = false;
  }
}

// Remove friend
async function removeFriend() {
  if (!profile.value?.id) return;
  if (!confirm('친구를 삭제할까요?')) return;
  friendLoading.value = true;
  try {
    await axios.delete(`/api/friends/${profile.value.id}`);
    friendStatus.value = 'none';
  } catch (e) {
    alert(e?.response?.data?.message || '삭제 실패');
  } finally {
    friendLoading.value = false;
  }
}

async function saveProfile() {
  saving.value = true; editError.value = '';
  try {
    const { data } = await axios.put('/api/profile', editForm.value);
    profile.value.name = data.user.name;
    profile.value.bio = data.user.bio;
    profile.value.region = data.user.region;
    showEdit.value = false;
    await authStore.fetchMe();
  } catch(e) {
    editError.value = e.response?.data?.message || '오류가 발생했습니다.';
  } finally { saving.value = false; }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('ko-KR');
}

async function loadProfile() {
  loading.value = true;
  try {
    const [profileRes, postsRes] = await Promise.all([
      axios.get(`/api/profile/${route.params.username}`),
      isMyProfile.value ? axios.get('/api/profile/me/posts') : Promise.resolve({ data: { data: [] } }),
    ]);
    profile.value = profileRes.data;
    posts.value = postsRes.data.data || [];
    editForm.value = { name: profile.value.name, bio: profile.value.bio || '', region: profile.value.region || '' };
    // Check friendship after loading profile
    await checkFriendship();
  } catch { profile.value = null; }
  loading.value = false;
}

onMounted(loadProfile);

// Re-load when route changes (navigating to different profile)
watch(() => route.params.username, (newVal, oldVal) => {
  if (newVal && newVal !== oldVal) {
    loadProfile();
  }
});
</script>
