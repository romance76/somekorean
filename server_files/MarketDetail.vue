<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[1200px] mx-auto px-4 pt-4">
      <div v-if="loading" class="text-center py-20 text-gray-400">불러오는 중...</div>
      <template v-else-if="item">
        <!-- 상단 컬러 헤더 -->
        <div class="bg-gradient-to-r from-orange-500 to-amber-500 text-white px-6 py-4 rounded-2xl mb-4">
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center gap-2">
              <button @click="router.push('/market')" class="text-orange-200 text-sm hover:text-white transition">&larr; 중고장터</button>
              <span v-if="item.category" class="bg-white/20 text-xs px-3 py-1 rounded-full">{{ item.category }}</span>
              <span v-if="item.status === 'sold'" class="bg-gray-900/50 text-xs px-3 py-1 rounded-full font-medium">판매완료</span>
              <span v-else-if="item.status === 'reserved'" class="bg-red-500/60 text-xs px-3 py-1 rounded-full font-medium">예약중</span>
              <span v-else class="bg-white/20 text-xs px-3 py-1 rounded-full font-medium">판매중</span>
            </div>
            <div class="flex items-center gap-2">
              <button @click="shareItem" class="flex items-center gap-1 text-xs text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/></svg>
                공유
              </button>
              <button @click="toggleBookmark" :class="item.is_bookmarked ? 'bg-yellow-400/30' : 'bg-white/10 hover:bg-white/20'" class="flex items-center gap-1 text-xs text-white/80 hover:text-white px-3 py-1.5 rounded-lg transition">
                <svg class="w-3.5 h-3.5" :fill="item.is_bookmarked ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"/></svg>
                북마크
              </button>
            </div>
          </div>
          <h1 class="text-lg sm:text-xl font-black leading-tight">{{ item.title }}</h1>
          <div class="flex items-center gap-2 mt-2 text-sm text-orange-100">
            <span class="font-medium">
              <template v-if="Number(item.price) === 0">무료 나눔</template>
              <template v-else>${{ Number(item.price).toLocaleString() }}</template>
            </span>
            <span v-if="item.region">·</span>
            <span v-if="item.region">{{ item.region }}</span>
            <span>·</span>
            <span>{{ formatDate(item.created_at) }}</span>
          </div>
        </div>

        <!-- 2컬럼 레이아웃: 본문(좌) + 사이드바(우) -->
        <div class="flex gap-5 items-start">

          <!-- 본문 컬럼 (좌) -->
          <div class="flex-1 min-w-0">

            <!-- 이미지 갤러리 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-4 relative">
              <!-- SOLD 배지 -->
              <div v-if="item.status === 'sold'" class="absolute top-4 left-4 z-10 bg-gray-900/80 text-white px-4 py-2 rounded-lg font-bold text-lg">
                판매완료
              </div>
              <!-- 메인 이미지 -->
              <div class="aspect-video bg-gray-100 flex items-center justify-center cursor-pointer" @click="item.images?.length > 0 && openGallery(selectedImageIndex)">
                <img v-if="item.images?.[selectedImageIndex]" :src="item.images[selectedImageIndex]" :alt="item.title" class="w-full h-full object-contain" />
                <span v-else class="text-6xl">📦</span>
              </div>
              <!-- 썸네일 -->
              <div v-if="item.images?.length > 1" class="flex gap-2 p-3 overflow-x-auto">
                <div v-for="(img, idx) in item.images" :key="idx"
                  @click="selectedImageIndex = idx"
                  :class="['w-16 h-16 rounded-lg overflow-hidden flex-shrink-0 cursor-pointer border-2 transition',
   idx === selectedImageIndex ? 'border-orange-500' : 'border-transparent hover:border-gray-300']">
                  <img :src="img" class="w-full h-full object-cover" />
                </div>
              </div>
            </div>

            <!-- 상품 정보 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-4">
              <div class="flex items-start justify-between mb-3">
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">{{ item.category }}</span>
                  <span v-if="item.condition" class="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded">{{ item.condition }}</span>
                  <span v-if="item.status === 'sold'" class="text-xs text-white bg-gray-600 px-2 py-1 rounded font-medium">판매완료</span>
                  <span v-else-if="item.status === 'reserved'" class="text-xs text-orange-600 bg-orange-50 px-2 py-1 rounded font-medium">예약중</span>
                </div>
                <div v-if="canEdit" class="flex space-x-2">
                  <router-link :to="`/market/write?edit=${item.id}`" class="text-xs text-gray-400 hover:text-gray-600">수정</router-link>
                  <button @click="deleteItem" class="text-xs text-red-400 hover:text-red-600">삭제</button>
                </div>
              </div>
              <p class="text-2xl font-bold text-orange-600 mb-4">
                <template v-if="Number(item.price) === 0">무료 나눔</template>
                <template v-else>${{ Number(item.price).toLocaleString() }}</template>
                <span v-if="item.price_negotiable" class="text-sm text-gray-400 font-normal ml-2">가격 협의 가능</span>
              </p>
              <div class="flex items-center gap-4 text-xs text-gray-500 mb-4">
                <span>조회 {{ item.view_count || 0 }}</span>
                <span>관심 {{ item.like_count || 0 }}</span>
                <span>{{ formatDate(item.created_at) }}</span>
              </div>
              <div class="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed">{{ item.description }}</div>
            </div>

            <!-- 판매자 정보 카드 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">판매자 정보</h3>
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 bg-orange-100 rounded-full flex items-center justify-center text-orange-600 font-bold text-xl flex-shrink-0">
                  {{ item.user?.name?.[0] || '?' }}
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900">{{ item.user?.name }}</p>
                  <div class="flex items-center gap-3 mt-1 text-xs text-gray-500">
                    <span>📍 {{ item.region || '지역 미상' }}</span>
                    <span v-if="item.user?.rating" class="flex items-center gap-0.5">
                      <span class="text-yellow-500">★</span> {{ item.user.rating }}
                    </span>
                    <span v-if="item.user?.market_count != null">판매 {{ item.user.market_count }}건</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 지도 -->
            <div v-if="item.latitude && item.longitude" class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-4">
              <div class="px-5 py-3 border-b border-gray-100">
                <h3 class="font-semibold text-gray-800 text-sm">📍 거래 희망 위치</h3>
              </div>
              <iframe
                :src="`https://maps.google.com/maps?q=${item.latitude},${item.longitude}&output=embed`"
                class="w-full h-[300px] border-0"
                allowfullscreen
                loading="lazy"
              ></iframe>
              <div v-if="item.address" class="px-5 py-3 text-sm text-gray-600">{{ item.address }}</div>
            </div>

            <!-- 찜/예약 섹션 -->
            <div v-if="item.reservation_points > 0 || item.reservation" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 mb-4">
              <h3 class="text-sm font-semibold text-gray-700 mb-3">찜/예약 정보</h3>

              <!-- 찜 가능 상태 (찜이 없고, 내 물건이 아닐 때) -->
              <div v-if="!item.reservation && !canEdit && item.status !== 'sold'" class="space-y-3">
                <div class="flex items-center gap-3">
                  <span class="inline-flex items-center gap-1 bg-green-50 text-green-700 text-sm font-medium px-3 py-1.5 rounded-full border border-green-200">
                    <span class="w-2 h-2 bg-green-500 rounded-full"></span> 찜 가능
                  </span>
                  <span v-if="item.reservation_points > 0" class="text-sm text-gray-600">보증금: <strong class="text-orange-600">{{ item.reservation_points }}P</strong></span>
                  <span class="text-sm text-gray-500">유효시간: {{ item.reservation_hours || 24 }}시간</span>
                </div>
                <button v-if="authStore.isLoggedIn" @click="showReserveModal = true"
                  class="w-full py-2.5 bg-green-600 text-white rounded-lg font-medium text-sm hover:bg-green-700 transition">
                  찜하기
                </button>
                <p v-else class="text-xs text-gray-400 text-center">
                  <router-link to="/auth/login" class="text-orange-600 hover:underline">로그인</router-link> 후 찜할 수 있습니다.
                </p>
              </div>

              <!-- 찜된 상태 - 내가 찜한 경우 -->
              <div v-else-if="item.reservation && item.my_reservation" class="space-y-3">
                <div class="flex items-center gap-3">
                  <span class="inline-flex items-center gap-1 bg-yellow-50 text-yellow-700 text-sm font-medium px-3 py-1.5 rounded-full border border-yellow-200">
                    <span class="w-2 h-2 bg-yellow-500 rounded-full"></span> 내가 찜함
                  </span>
                  <span v-if="item.reservation.points_held > 0" class="text-sm text-gray-600">보증금: <strong class="text-orange-600">{{ item.reservation.points_held }}P</strong></span>
                </div>
                <div class="text-xs text-gray-500">
                  만료: {{ formatDateTime(item.reservation.expires_at) }}
                  <span v-if="reservationTimeLeft" class="ml-1 text-orange-600 font-medium">({{ reservationTimeLeft }})</span>
                </div>
                <div class="flex gap-2">
                  <button @click="completeReservation"
                    class="flex-1 py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 transition">
                    거래완료
                  </button>
                  <button @click="cancelReservation"
                    class="flex-1 py-2.5 bg-gray-200 text-gray-700 rounded-lg font-medium text-sm hover:bg-gray-300 transition">
                    찜 취소
                  </button>
                </div>
                <p v-if="item.reservation.points_held > 0" class="text-xs text-red-500">* 취소 시 보증금의 50%가 판매자에게 지급됩니다.</p>
              </div>

              <!-- 찜된 상태 - 내 물건인 경우 (판매자 뷰) -->
              <div v-else-if="item.reservation && canEdit" class="space-y-3">
                <div class="flex items-center gap-3">
                  <span class="inline-flex items-center gap-1 bg-yellow-50 text-yellow-700 text-sm font-medium px-3 py-1.5 rounded-full border border-yellow-200">
                    <span class="w-2 h-2 bg-yellow-500 rounded-full"></span> 찜됨
                  </span>
                  <span class="text-sm text-gray-700">구매자: <strong>{{ item.reservation.buyer?.name }}</strong></span>
                </div>
                <div class="text-xs text-gray-500">
                  만료: {{ formatDateTime(item.reservation.expires_at) }}
                  <span v-if="reservationTimeLeft" class="ml-1 text-orange-600 font-medium">({{ reservationTimeLeft }})</span>
                </div>
                <button @click="completeReservation"
                  class="w-full py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 transition">
                  거래완료 처리
                </button>
              </div>

              <!-- 다른 사람이 찜한 경우 -->
              <div v-else-if="item.reservation && !item.my_reservation && !canEdit" class="space-y-2">
                <div class="flex items-center gap-3">
                  <span class="inline-flex items-center gap-1 bg-red-50 text-red-700 text-sm font-medium px-3 py-1.5 rounded-full border border-red-200">
                    <span class="w-2 h-2 bg-red-500 rounded-full"></span> 예약중
                  </span>
                  <span class="text-sm text-gray-500">다른 사용자가 찜한 물품입니다.</span>
                </div>
              </div>

              <!-- 내 물건인데 찜이 없는 경우 -->
              <div v-else-if="!item.reservation && canEdit && item.reservation_points > 0" class="space-y-2">
                <div class="flex items-center gap-3 text-sm text-gray-600">
                  <span>보증금: <strong class="text-orange-600">{{ item.reservation_points }}P</strong></span>
                  <span>유효시간: {{ item.reservation_hours || 24 }}시간</span>
                </div>
                <p class="text-xs text-gray-400">아직 찜한 사용자가 없습니다.</p>
              </div>
            </div>

            <!-- 좋아요 / 연락하기 버튼 -->
            <div class="bg-white rounded-2xl shadow-sm p-4 mb-4 flex items-center justify-center gap-3">
              <button @click="toggleLike"
                :class="['flex items-center justify-center space-x-2 px-6 py-2.5 rounded-full border-2 transition font-medium text-sm',
   item.is_liked ? 'border-red-500 bg-red-50 text-red-600' : 'border-gray-200 text-gray-500 hover:border-red-300']">
                <span>{{ item.is_liked ? '❤️' : '🤍' }}</span>
                <span>관심 {{ item.like_count || 0 }}</span>
              </button>
              <button v-if="authStore.isLoggedIn && !canEdit && item.status !== 'sold'"
                @click="sendMessage"
                class="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-full bg-orange-500 text-white font-medium text-sm hover:bg-orange-600 transition">
                <span>💬</span>
                <span>연락하기</span>
              </button>
            </div>

            <!-- 찜 확인 모달 -->
            <div v-if="showReserveModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" @click.self="showReserveModal = false">
              <div class="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl">
                <h3 class="text-lg font-bold text-gray-800 mb-4">찜하기</h3>
                <div class="space-y-3 text-sm text-gray-700">
                  <p><strong>{{ item.title }}</strong></p>
                  <div v-if="item.reservation_points > 0" class="bg-orange-50 border border-orange-200 rounded-lg p-3">
                    <p class="font-medium text-orange-800">보증금: {{ item.reservation_points }}P</p>
                    <p class="text-xs text-orange-600 mt-1">찜 취소 시 보증금의 50%가 판매자에게 지급됩니다.</p>
                    <p class="text-xs text-orange-600">시간 초과 시 보증금 전액이 판매자에게 이전됩니다.</p>
                  </div>
                  <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p class="text-blue-800">유효시간: <strong>{{ item.reservation_hours || 24 }}시간</strong></p>
                    <p class="text-xs text-blue-600 mt-1">유효시간 내에 연락하여 거래를 진행해주세요.</p>
                  </div>
                </div>
                <div class="flex gap-2 mt-5">
                  <button @click="showReserveModal = false"
                    class="flex-1 py-2.5 bg-gray-100 text-gray-700 rounded-lg font-medium text-sm hover:bg-gray-200 transition">취소</button>
                  <button @click="doReserve" :disabled="reserving"
                    class="flex-1 py-2.5 bg-green-600 text-white rounded-lg font-medium text-sm hover:bg-green-700 disabled:opacity-50 transition">
                    {{ reserving ? '처리중...' : '찜하기' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 댓글/문의 섹션 -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-4">
              <div class="px-5 py-3 border-b border-gray-100">
                <h3 class="font-semibold text-gray-800 text-sm">💬 댓글/문의 {{ item.comments?.length || 0 }}개</h3>
              </div>
              <ul v-if="item.comments?.length">
                <li v-for="comment in item.comments" :key="comment.id" class="px-5 py-3.5 border-b border-gray-50 last:border-0">
                  <div class="flex items-start justify-between">
                    <div class="flex items-start space-x-2 flex-1">
                      <div class="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center text-gray-500 text-xs font-bold flex-shrink-0 mt-0.5">
                        {{ (comment.user?.name || comment.user_name || '익명')[0] }}
                      </div>
                      <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-1">
                          <span class="text-sm font-medium text-gray-800">{{ comment.user?.name || comment.user_name || '익명' }}</span>
                          <span v-if="comment.user_id === item.user_id" class="text-xs bg-orange-50 text-orange-500 px-1.5 py-0.5 rounded">판매자</span>
                          <span class="text-xs text-gray-400">{{ formatDate(comment.created_at) }}</span>
                        </div>
                        <p class="text-sm text-gray-700">{{ comment.content }}</p>
                      </div>
                    </div>
                    <button v-if="authStore.user?.id === comment.user?.id || authStore.user?.is_admin"
                      @click="deleteComment(comment.id)" class="text-xs text-gray-300 hover:text-red-400 ml-2">삭제</button>
                  </div>
                </li>
              </ul>
              <div v-else class="px-5 py-8 text-center text-sm text-gray-400">아직 문의가 없습니다.</div>

              <!-- 댓글 입력 -->
              <div v-if="authStore.isLoggedIn" class="px-5 py-3 bg-gray-50 border-t border-gray-100">
                <div class="flex space-x-2">
                  <input v-model="commentText" @keyup.enter.ctrl="submitComment" type="text" placeholder="댓글을 입력하세요 (Ctrl+Enter)"
                    class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500" />
                  <button @click="submitComment" :disabled="!commentText.trim()"
                    class="bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-600 disabled:opacity-40">등록</button>
                </div>
              </div>
              <div v-else class="px-5 py-3 bg-gray-50 border-t border-gray-100 text-center">
                <router-link to="/auth/login" class="text-orange-600 text-sm hover:underline">로그인 후 댓글을 작성할 수 있습니다</router-link>
              </div>
            </div>

            <!-- 하단 목록 링크 -->
            <router-link to="/market" class="text-sm text-gray-500 hover:text-orange-600">← 목록으로</router-link>
          </div><!-- /본문 컬럼 -->

          <!-- 사이드바 (우) — 같은 카테고리 매물 -->
          <div class="hidden lg:block flex-shrink-0 sticky top-4" style="width:320px">
            <div class="bg-white rounded-2xl shadow-sm flex flex-col overflow-hidden">
              <h3 class="flex-shrink-0 font-bold text-gray-800 text-sm px-4 py-3 border-b border-gray-100">
                {{ item.category || '관련' }} 매물
              </h3>
              <div>
                <div v-if="sidebarItems.length">
                  <router-link v-for="(si, idx) in sidebarItems" :key="si.id" :to="`/market/${si.id}`"
                    class="flex gap-3 py-3 px-3 cursor-pointer hover:bg-orange-50/40 transition border-b border-gray-50 last:border-0"
                    :class="si.id == item.id ? 'bg-orange-50' : ''">
                    <!-- 썸네일 -->
                    <div class="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-gray-100">
                      <img v-if="si.images?.[0]" :src="si.images[0]" class="w-full h-full object-cover" />
                      <div v-else class="w-full h-full flex items-center justify-center text-2xl">📦</div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium text-gray-800 line-clamp-2 leading-snug">{{ si.title }}</p>
                      <p class="text-[12px] text-orange-600 font-bold mt-1">
                        <template v-if="Number(si.price) === 0">무료 나눔</template>
                        <template v-else>${{ Number(si.price).toLocaleString() }}</template>
                      </p>
                    </div>
                  </router-link>
                </div>
                <div v-else class="text-center py-10 text-gray-400 text-sm">관련 매물이 없습니다.</div>
              </div>
            </div>
          </div><!-- /사이드바 -->

        </div><!-- /2컬럼 -->
      </template>
      <div v-else class="text-center py-20 text-gray-400">물품을 찾을 수 없습니다.</div>

      <!-- 이미지 갤러리 모달 -->
      <div v-if="galleryOpen" class="fixed inset-0 bg-black/80 z-50 flex items-center justify-center" @click.self="galleryOpen = false">
        <button @click="galleryOpen = false" class="absolute top-4 right-4 text-white text-2xl hover:text-gray-300">&times;</button>
        <button v-if="galleryIndex > 0" @click="galleryIndex--" class="absolute left-4 text-white text-3xl hover:text-gray-300">&lsaquo;</button>
        <img :src="item.images[galleryIndex]" class="max-w-[90vw] max-h-[85vh] object-contain rounded-lg" />
        <button v-if="galleryIndex < item.images.length - 1" @click="galleryIndex++" class="absolute right-4 text-white text-3xl hover:text-gray-300">&rsaquo;</button>
        <div class="absolute bottom-4 text-white text-sm">{{ galleryIndex + 1 }} / {{ item.images.length }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const item = ref(null);
const loading = ref(true);
const commentText = ref('');
const selectedImageIndex = ref(0);
const galleryOpen = ref(false);
const galleryIndex = ref(0);
const sidebarItems = ref([]);
const showReserveModal = ref(false);
const reserving = ref(false);

const canEdit = computed(() =>
  authStore.user && (authStore.user.id === item.value?.user_id || authStore.user.is_admin)
);

function openGallery(idx) {
  galleryIndex.value = idx;
  galleryOpen.value = true;
}

async function toggleLike() {
  if (!authStore.isLoggedIn) { router.push('/auth/login'); return; }
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/like`);
    item.value.is_liked = data.liked;
    item.value.like_count = data.like_count;
  } catch {}
}

async function toggleBookmark() {
  if (!authStore.isLoggedIn) { router.push('/auth/login'); return; }
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/bookmark`);
    item.value.is_bookmarked = data.bookmarked;
  } catch {}
}

function shareItem() {
  const url = window.location.href;
  if (navigator.share) {
    navigator.share({ title: item.value.title, url });
  } else if (navigator.clipboard) {
    navigator.clipboard.writeText(url);
    alert('링크가 복사되었습니다.');
  }
}

async function sendMessage() {
  router.push(`/messages?to=${item.value.user_id}&item=${item.value.id}`);
}

async function submitComment() {
  if (!commentText.value.trim()) return;
  try {
    const { data } = await axios.post(`/api/market/${item.value.id}/comments`, { content: commentText.value });
    if (!item.value.comments) item.value.comments = [];
    item.value.comments.push(data.comment);
    commentText.value = '';
  } catch (e) {
    alert(e.response?.data?.message || '댓글 등록 실패');
  }
}

async function deleteComment(id) {
  if (!confirm('댓글을 삭제하시겠습니까?')) return;
  try {
    await axios.delete(`/api/comments/${id}`);
    item.value.comments = item.value.comments.filter(c => c.id !== id);
  } catch {}
}

async function deleteItem() {
  if (!confirm('삭제하시겠습니까?')) return;
  await axios.delete(`/api/market/${item.value.id}`);
  router.push('/market');
}

async function loadSidebarItems() {
  try {
    const { data } = await axios.get('/api/market', {
      params: { category: item.value.category, limit: 5, per_page: 5 }
    });
    sidebarItems.value = (data.data || data).filter(i => i.id !== item.value.id).slice(0, 5);
  } catch {}
}

function formatDate(d) {
  const date = new Date(d);
  const now = new Date();
  const diff = (now - date) / 1000;
  if (diff < 60) return '방금 전';
  if (diff < 3600) return `${Math.floor(diff/60)}분 전`;
  if (diff < 86400) return `${Math.floor(diff/3600)}시간 전`;
  return date.toLocaleDateString('ko-KR');
}

function formatDateTime(d) {
  if (!d) return '';
  return new Date(d).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

const reservationTimeLeft = computed(() => {
  if (!item.value?.reservation?.expires_at) return '';
  const expires = new Date(item.value.reservation.expires_at);
  const now = new Date();
  const diff = (expires - now) / 1000;
  if (diff <= 0) return '만료됨';
  const h = Math.floor(diff / 3600);
  const m = Math.floor((diff % 3600) / 60);
  if (h > 0) return `${h}시간 ${m}분 남음`;
  return `${m}분 남음`;
});

async function doReserve() {
  reserving.value = true;
  try {
    await axios.post(`/api/market/${item.value.id}/reserve`);
    showReserveModal.value = false;
    // 새로고침
    const { data } = await axios.get(`/api/market/${route.params.id}`);
    item.value = data;
    alert('찜이 완료되었습니다!');
  } catch (e) {
    alert(e.response?.data?.message || '찜하기 실패');
  } finally { reserving.value = false; }
}

async function completeReservation() {
  if (!item.value?.reservation?.id) return;
  if (!confirm('거래를 완료하시겠습니까?')) return;
  try {
    await axios.post(`/api/market/reservations/${item.value.reservation.id}/complete`);
    const { data } = await axios.get(`/api/market/${route.params.id}`);
    item.value = data;
    alert('거래가 완료되었습니다!');
  } catch (e) {
    alert(e.response?.data?.message || '거래 완료 처리 실패');
  }
}

async function cancelReservation() {
  if (!item.value?.reservation?.id) return;
  const msg = item.value.reservation.points_held > 0
    ? `찜을 취소하시겠습니까?\n보증금 ${item.value.reservation.points_held}P 중 50%만 반환됩니다.`
    : '찜을 취소하시겠습니까?';
  if (!confirm(msg)) return;
  try {
    await axios.post(`/api/market/reservations/${item.value.reservation.id}/cancel`);
    const { data } = await axios.get(`/api/market/${route.params.id}`);
    item.value = data;
    alert('찜이 취소되었습니다.');
  } catch (e) {
    alert(e.response?.data?.message || '찜 취소 실패');
  }
}

onMounted(async () => {
  try {
    const { data } = await axios.get(`/api/market/${route.params.id}`);
    item.value = data;
    loadSidebarItems();
  } catch { item.value = null; }
  loading.value = false;
});
</script>
