<template>
  <div class="space-y-5">

    <!-- 헤더 -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-bold text-gray-800">게시판별 설정</h2>
        <p class="text-xs text-gray-400 mt-0.5">각 게시판의 이름, 권한, 카테고리, 기능 등을 설정합니다</p>
      </div>
      <span v-if="toast.show" class="text-sm font-medium px-3 py-1.5 rounded-lg"
        :class="toast.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'">
        {{ toast.type === 'success' ? '✓' : '✗' }} {{ toast.message }}
      </span>
    </div>

    <!-- 카테고리 탭 네비게이션 -->
    <div class="flex gap-1 bg-gray-100 rounded-xl p-1 overflow-x-auto">
      <button
        v-for="cat in categories"
        :key="cat.key"
        @click="switchCategory(cat.key)"
        class="flex-shrink-0 px-4 py-2 rounded-lg text-sm font-medium transition whitespace-nowrap"
        :class="activeCategory === cat.key
          ? 'bg-white text-blue-600 shadow-sm font-semibold'
          : 'text-gray-500 hover:text-gray-700 hover:bg-white/60'"
      >
        {{ cat.icon }} {{ cat.label }}
      </button>
    </div>

    <!-- 로딩 -->
    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else>
      <!-- 게시판 선택 서브탭: 활성 카테고리의 boards만 표시 -->
      <div class="flex gap-1 mb-4 border-b border-gray-200 overflow-x-auto">
        <button
          v-for="bk in (activeCat?.boards || [])"
          :key="bk"
          @click="activeBoard = bk"
          class="px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors whitespace-nowrap flex-shrink-0"
          :class="activeBoard === bk
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          {{ boards[bk]?.icon }} {{ boards[bk]?.name }}
          <span v-if="boards[bk] && !boards[bk].enabled" class="ml-1 text-xs text-red-400">(비활성)</span>
        </button>
      </div>

      <!-- 선택된 게시판 설정 폼 (v-for 없이 activeBoard 하나만 렌더링) -->
      <div v-if="boards[activeBoard]" class="space-y-4">

            <!-- 기본 정보 카드 -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 class="font-bold text-gray-700 text-sm mb-4 flex items-center gap-2">
                <span class="w-1 h-4 bg-blue-500 rounded-full inline-block"></span>
                기본 정보
              </h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1.5">게시판 이름</label>
                  <input
                    v-model="boards[activeBoard].name"
                    type="text"
                    placeholder="게시판 이름 입력..."
                    class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition"
                  />
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1.5">아이콘/이모지</label>
                  <input
                    v-model="boards[activeBoard].icon"
                    type="text"
                    placeholder="이모지 입력..."
                    class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition"
                  />
                </div>
                <div class="sm:col-span-2">
                  <label class="block text-xs font-semibold text-gray-600 mb-1.5">설명</label>
                  <input
                    v-model="boards[activeBoard].description"
                    type="text"
                    placeholder="게시판 설명..."
                    class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition"
                  />
                </div>
              </div>

              <!-- 활성화 토글 -->
              <div class="flex items-center justify-between mt-5 pt-4 border-t border-gray-100">
                <div>
                  <p class="text-sm font-medium text-gray-700">게시판 활성화</p>
                  <p class="text-xs text-gray-400">비활성화 시 사이트에서 보이지 않습니다</p>
                </div>
                <button
                  @click="boards[activeBoard].enabled = !boards[activeBoard].enabled"
                  :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0',
                    boards[activeBoard].enabled ? 'bg-blue-500' : 'bg-gray-200']"
                >
                  <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                    boards[activeBoard].enabled ? 'translate-x-6' : 'translate-x-1']"></span>
                </button>
              </div>
            </div>

            <!-- 카테고리/태그 관리 카드 -->
            <div v-if="boards[activeBoard].categories" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 class="font-bold text-gray-700 text-sm mb-4 flex items-center gap-2">
                <span class="w-1 h-4 bg-purple-500 rounded-full inline-block"></span>
                카테고리/태그 관리
              </h3>
              <div class="flex flex-wrap gap-2 mb-3">
                <span
                  v-for="(cat, ci) in boards[activeBoard].categories"
                  :key="ci"
                  class="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs font-medium px-3 py-1.5 rounded-full"
                >
                  {{ cat }}
                  <button @click="removeCategory(activeBoard, ci)" class="text-blue-400 hover:text-red-500 ml-0.5 text-sm leading-none">&times;</button>
                </span>
                <span v-if="boards[activeBoard].categories.length === 0" class="text-xs text-gray-400">등록된 카테고리가 없습니다</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  v-model="newCategoryInput[activeBoard]"
                  type="text"
                  placeholder="새 카테고리 입력..."
                  class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition"
                  @keyup.enter="addCategory(activeBoard)"
                />
                <button
                  @click="addCategory(activeBoard)"
                  class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg transition-colors"
                >
                  추가
                </button>
              </div>
            </div>

            <!-- 권한 설정 카드 -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 class="font-bold text-gray-700 text-sm mb-4 flex items-center gap-2">
                <span class="w-1 h-4 bg-amber-500 rounded-full inline-block"></span>
                권한 설정
              </h3>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1.5">글쓰기 권한</label>
                  <select v-model="boards[activeBoard].write_permission" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition bg-white">
                    <option value="all">전체 공개</option>
                    <option value="login">로그인 필수</option>
                    <option value="level">레벨 제한</option>
                    <option value="admin">관리자만</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1.5">댓글 권한</label>
                  <select v-model="boards[activeBoard].comment_permission" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition bg-white">
                    <option value="all">전체 공개</option>
                    <option value="login">로그인 필수</option>
                    <option value="admin">관리자만</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1.5">열람 권한</label>
                  <select v-model="boards[activeBoard].view_permission" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition bg-white">
                    <option value="all">전체 공개</option>
                    <option value="login">로그인 필수</option>
                    <option value="admin">관리자만</option>
                  </select>
                </div>
              </div>
              <!-- 레벨 제한 입력 (글쓰기 권한이 level일 때) -->
              <div v-if="boards[activeBoard].write_permission === 'level'" class="mt-3">
                <label class="block text-xs font-semibold text-gray-600 mb-1.5">최소 레벨</label>
                <input
                  v-model.number="boards[activeBoard].min_write_level"
                  type="number"
                  min="1"
                  max="99"
                  class="w-32 border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition"
                />
              </div>
            </div>

            <!-- 기능 설정 카드 -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 class="font-bold text-gray-700 text-sm mb-4 flex items-center gap-2">
                <span class="w-1 h-4 bg-green-500 rounded-full inline-block"></span>
                기능 설정
              </h3>
              <div class="space-y-4">
                <!-- 파일 업로드 -->
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-700">파일 업로드 허용</p>
                    <p class="text-xs text-gray-400">이미지 및 첨부파일 업로드</p>
                  </div>
                  <button
                    @click="boards[activeBoard].file_upload = !boards[activeBoard].file_upload"
                    :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0',
                      boards[activeBoard].file_upload ? 'bg-blue-500' : 'bg-gray-200']"
                  >
                    <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                      boards[activeBoard].file_upload ? 'translate-x-6' : 'translate-x-1']"></span>
                  </button>
                </div>

                <!-- 파일 업로드 세부 설정 -->
                <div v-if="boards[activeBoard].file_upload" class="ml-4 pl-4 border-l-2 border-gray-100 space-y-3">
                  <div class="flex items-center gap-3">
                    <label class="text-xs font-semibold text-gray-600 w-32">최대 파일 크기</label>
                    <input
                      v-model.number="boards[activeBoard].max_file_size"
                      type="number"
                      min="1"
                      max="200"
                      class="w-24 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition"
                    />
                    <span class="text-xs text-gray-400">MB</span>
                  </div>
                  <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1.5">허용 파일 형식</label>
                    <input
                      v-model="boards[activeBoard].file_types"
                      type="text"
                      placeholder="jpg,png,gif,pdf"
                      class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition"
                    />
                    <p class="text-xs text-gray-400 mt-1">쉼표로 구분하여 입력</p>
                  </div>
                </div>

                <!-- 댓글 기능 -->
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-700">댓글 기능</p>
                    <p class="text-xs text-gray-400">댓글 작성 기능 활성화</p>
                  </div>
                  <button
                    @click="boards[activeBoard].comments_enabled = !boards[activeBoard].comments_enabled"
                    :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0',
                      boards[activeBoard].comments_enabled ? 'bg-blue-500' : 'bg-gray-200']"
                  >
                    <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                      boards[activeBoard].comments_enabled ? 'translate-x-6' : 'translate-x-1']"></span>
                  </button>
                </div>

                <!-- 좋아요 기능 -->
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-700">좋아요 기능</p>
                    <p class="text-xs text-gray-400">게시글 좋아요/추천 기능</p>
                  </div>
                  <button
                    @click="boards[activeBoard].likes_enabled = !boards[activeBoard].likes_enabled"
                    :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0',
                      boards[activeBoard].likes_enabled ? 'bg-blue-500' : 'bg-gray-200']"
                  >
                    <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                      boards[activeBoard].likes_enabled ? 'translate-x-6' : 'translate-x-1']"></span>
                  </button>
                </div>

                <!-- 신고 기능 -->
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-700">신고 기능</p>
                    <p class="text-xs text-gray-400">부적절한 게시글 신고 기능</p>
                  </div>
                  <button
                    @click="boards[activeBoard].reports_enabled = !boards[activeBoard].reports_enabled"
                    :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0',
                      boards[activeBoard].reports_enabled ? 'bg-blue-500' : 'bg-gray-200']"
                  >
                    <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                      boards[activeBoard].reports_enabled ? 'translate-x-6' : 'translate-x-1']"></span>
                  </button>
                </div>

                <!-- 글 승인제 -->
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-700">글 승인제</p>
                    <p class="text-xs text-gray-400">관리자 승인 후 게시글 공개</p>
                  </div>
                  <button
                    @click="boards[activeBoard].approval_required = !boards[activeBoard].approval_required"
                    :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0',
                      boards[activeBoard].approval_required ? 'bg-blue-500' : 'bg-gray-200']"
                  >
                    <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                      boards[activeBoard].approval_required ? 'translate-x-6' : 'translate-x-1']"></span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 표시 설정 카드 -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 class="font-bold text-gray-700 text-sm mb-4 flex items-center gap-2">
                <span class="w-1 h-4 bg-indigo-500 rounded-full inline-block"></span>
                표시 설정
              </h3>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1.5">페이지당 글 수</label>
                  <select v-model.number="boards[activeBoard].per_page" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition bg-white">
                    <option :value="10">10개</option>
                    <option :value="15">15개</option>
                    <option :value="20">20개</option>
                    <option :value="30">30개</option>
                    <option :value="50">50개</option>
                  </select>
                </div>
                <div>
                  <label class="block text-xs font-semibold text-gray-600 mb-1.5">목록 표시 형태</label>
                  <select v-model="boards[activeBoard].display_mode" class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 transition bg-white">
                    <option value="list">리스트</option>
                    <option value="card">카드</option>
                    <option value="gallery">갤러리</option>
                  </select>
                </div>
                <div class="flex items-center">
                  <div class="flex items-center justify-between w-full">
                    <div>
                      <p class="text-xs font-semibold text-gray-600">공지사항 표시</p>
                    </div>
                    <button
                      @click="boards[activeBoard].show_notices = !boards[activeBoard].show_notices"
                      :class="['relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0',
                        boards[activeBoard].show_notices ? 'bg-blue-500' : 'bg-gray-200']"
                    >
                      <span :class="['inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform',
                        boards[activeBoard].show_notices ? 'translate-x-6' : 'translate-x-1']"></span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- 표시 모드 미리보기 -->
              <div class="mt-4 p-3 bg-gray-50 rounded-lg">
                <p class="text-xs text-gray-500 mb-2">미리보기</p>
                <div v-if="boards[activeBoard].display_mode === 'list'" class="space-y-1">
                  <div v-for="i in 3" :key="i" class="flex items-center gap-3 py-1.5">
                    <span class="w-8 h-3 bg-gray-200 rounded"></span>
                    <span class="flex-1 h-3 bg-gray-200 rounded"></span>
                    <span class="w-16 h-3 bg-gray-200 rounded"></span>
                  </div>
                </div>
                <div v-else-if="boards[activeBoard].display_mode === 'card'" class="grid grid-cols-3 gap-2">
                  <div v-for="i in 3" :key="i" class="bg-white border border-gray-200 rounded-lg p-2">
                    <div class="w-full h-8 bg-gray-200 rounded mb-1.5"></div>
                    <div class="h-2 bg-gray-200 rounded w-3/4"></div>
                  </div>
                </div>
                <div v-else class="grid grid-cols-4 gap-1.5">
                  <div v-for="i in 4" :key="i" class="bg-gray-200 rounded aspect-square"></div>
                </div>
              </div>
            </div>

            <!-- 저장 영역 -->
            <div class="flex items-center justify-between bg-white rounded-xl shadow-sm border border-gray-100 p-4">
              <span class="text-xs text-gray-400">
                마지막 저장: {{ boardLastSaved[activeBoard] || '저장 기록 없음' }}
              </span>
              <button
                @click="saveBoard(activeBoard)"
                :disabled="saving"
                class="inline-flex items-center px-5 py-2.5 bg-blue-500 hover:bg-blue-600 text-white text-sm font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="saving" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
                설정 저장
              </button>
            </div>

        </div>
        <div v-else class="text-center py-10 text-gray-400">게시판을 선택하세요</div>
      </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'

// ─── Categories / Tabs ─────────────────────────────────────────────────────
const categories = [
  { key: 'community', label: '커뮤니티', icon: '💬', boards: ['community', 'qna'] },
  { key: 'trade',     label: '거래',     icon: '💼', boards: ['jobs', 'market', 'realestate'] },
  { key: 'biz',       label: '업소/서비스', icon: '🏪', boards: ['directory', 'groupbuy', 'shopping'] },
  { key: 'social',    label: '소셜',     icon: '🤝', boards: ['clubs', 'events', 'match', 'mentor'] },
  { key: 'media',     label: '미디어',   icon: '📰', boards: ['news', 'shorts', 'ai'] },
  { key: 'etc',       label: '기타',     icon: '🎮', boards: ['elder', 'ride', 'games'] },
]

// activeCategory must match exact key in categories array
const activeCategory = ref('community')
// activeBoard tracks which board sub-tab is selected
const activeBoard = ref('community')

// Computed: always returns the currently active category object
const activeCat = computed(() => categories.find(c => c.key === activeCategory.value))

// When category changes, auto-select the first board in that category
function switchCategory(catKey) {
  activeCategory.value = catKey
  const cat = categories.find(c => c.key === catKey)
  if (cat && cat.boards.length > 0) {
    activeBoard.value = cat.boards[0]
  }
}

// Also watch activeCategory as a safety net
watch(activeCategory, (newCat) => {
  const cat = categories.find(c => c.key === newCat)
  if (cat && cat.boards.length > 0) {
    // Only reset if current activeBoard doesn't belong to the new category
    if (!cat.boards.includes(activeBoard.value)) {
      activeBoard.value = cat.boards[0]
    }
  }
})

// ─── State ──────────────────────────────────────────────────────────────────
const loading = ref(true)
const saving = ref(false)
const toast = reactive({ show: false, message: '', type: 'success' })
let toastTimer = null

function showToast(msg, type = 'success') {
  clearTimeout(toastTimer)
  toast.message = msg
  toast.type = type
  toast.show = true
  toastTimer = setTimeout(() => { toast.show = false }, 3000)
}

// ─── Default Boards Config ──────────────────────────────────────────────────
const defaultBoardConfig = {
  write_permission: 'login',
  comment_permission: 'login',
  view_permission: 'all',
  file_upload: true,
  max_file_size: 10,
  file_types: 'jpg,png,gif,pdf',
  comments_enabled: true,
  likes_enabled: true,
  reports_enabled: true,
  approval_required: false,
  per_page: 20,
  display_mode: 'list',
  show_notices: true,
  min_write_level: 2,
}

// All 18 board types fully defined
const defaultBoards = {
  // ── 커뮤니티 ──
  community: {
    name: '커뮤니티', description: '자유로운 한인 커뮤니티', icon: '💬', enabled: true,
    categories: ['자유', '질문', '정보', '유머', '뉴스'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'list', show_notices: true, min_write_level: 2,
  },
  qna: {
    name: 'QnA', description: '질문과 답변', icon: '❓', enabled: true,
    categories: ['일반', '이민', '법률', '세금', '건강'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 5, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'list', show_notices: true, min_write_level: 2,
  },
  // ── 거래 ──
  jobs: {
    name: '구인구직', description: '일자리 정보', icon: '💼', enabled: true,
    categories: ['정규직', '파트타임', '프리랜서', '인턴'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 15, display_mode: 'list', show_notices: true, min_write_level: 2,
  },
  market: {
    name: '중고장터', description: '중고 물품 거래', icon: '🛒', enabled: true,
    categories: ['전자기기', '가구', '의류', '자동차', '기타'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'card', show_notices: true, min_write_level: 2,
  },
  realestate: {
    name: '부동산', description: '부동산 매물 정보', icon: '🏠', enabled: true,
    categories: ['매매', '전세', '월세', '상가', '토지'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 15, display_mode: 'list', show_notices: true, min_write_level: 2,
  },
  // ── 업소/서비스 ──
  directory: {
    name: '업소록', description: '한인 업소 디렉토리', icon: '🏪', enabled: true,
    categories: ['음식점', '뷰티', '자동차', '부동산', '법률', '의료', '교육', '쇼핑', '서비스', '기타'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: true, per_page: 20, display_mode: 'card', show_notices: true, min_write_level: 2,
  },
  groupbuy: {
    name: '공동구매', description: '공동구매 모집', icon: '🤲', enabled: true,
    categories: ['식품', '생활용품', '건강', '뷰티', '기타'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: true, per_page: 20, display_mode: 'card', show_notices: true, min_write_level: 2,
  },
  shopping: {
    name: '쇼핑정보', description: '쇼핑 및 딜 정보', icon: '🛍️', enabled: true,
    categories: ['핫딜', '쿠폰', '세일', '리뷰'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'card', show_notices: true, min_write_level: 2,
  },
  // ── 소셜 ──
  clubs: {
    name: '동호회', description: '취미 모임', icon: '🤝', enabled: true,
    categories: ['운동', '음악', '요리', '독서', '여행', '사진'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'card', show_notices: true, min_write_level: 2,
  },
  events: {
    name: '이벤트', description: '지역 행사 및 이벤트', icon: '🎉', enabled: true,
    categories: ['문화', '교육', '봉사', '파티', '세미나'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'card', show_notices: true, min_write_level: 2,
  },
  match: {
    name: '매칭', description: '한인 매칭 서비스', icon: '💕', enabled: true,
    categories: [],
    write_permission: 'login', comment_permission: 'login', view_permission: 'login',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'card', show_notices: false, min_write_level: 2,
  },
  mentor: {
    name: '멘토링', description: '멘토-멘티 매칭', icon: '🎓', enabled: true,
    categories: ['커리어', '유학', '이민', '사업', '기술'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'list', show_notices: true, min_write_level: 2,
  },
  // ── 미디어 ──
  news: {
    name: '뉴스', description: '한인 뉴스', icon: '📰', enabled: true,
    categories: ['미국', '한국', '지역', '경제', '문화'],
    write_permission: 'admin', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 10, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'list', show_notices: true, min_write_level: 2,
  },
  shorts: {
    name: '숏츠', description: '짧은 영상', icon: '📱', enabled: true,
    categories: ['일상', '요리', '여행', '유머', '정보'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 100, file_types: 'mp4,mov,jpg,png',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'gallery', show_notices: false, min_write_level: 2,
  },
  ai: {
    name: 'AI검색', description: 'AI 기반 검색', icon: '🤖', enabled: true,
    categories: [],
    write_permission: 'admin', comment_permission: 'login', view_permission: 'all',
    file_upload: false, max_file_size: 5, file_types: '',
    comments_enabled: false, likes_enabled: false, reports_enabled: false,
    approval_required: false, per_page: 20, display_mode: 'list', show_notices: false, min_write_level: 2,
  },
  // ── 기타 ──
  elder: {
    name: '노인안심', description: '노인 안심 서비스', icon: '💙', enabled: true,
    categories: [],
    write_permission: 'login', comment_permission: 'login', view_permission: 'login',
    file_upload: true, max_file_size: 5, file_types: 'jpg,png,gif,pdf',
    comments_enabled: true, likes_enabled: true, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'list', show_notices: true, min_write_level: 2,
  },
  ride: {
    name: '알바라이드', description: '커뮤니티 라이드 서비스', icon: '🚗', enabled: true,
    categories: ['출퇴근', '공항', '장거리', '기타'],
    write_permission: 'login', comment_permission: 'login', view_permission: 'all',
    file_upload: false, max_file_size: 5, file_types: 'jpg,png',
    comments_enabled: true, likes_enabled: false, reports_enabled: true,
    approval_required: false, per_page: 20, display_mode: 'list', show_notices: true, min_write_level: 2,
  },
  games: {
    name: '게임/퀴즈', description: '게임과 퀴즈', icon: '🎮', enabled: true,
    categories: ['퀴즈', '미니게임', '이벤트'],
    write_permission: 'admin', comment_permission: 'login', view_permission: 'all',
    file_upload: true, max_file_size: 20, file_types: 'jpg,png,gif',
    comments_enabled: true, likes_enabled: true, reports_enabled: false,
    approval_required: false, per_page: 20, display_mode: 'card', show_notices: true, min_write_level: 2,
  },
}

// ─── Reactive Boards Data ───────────────────────────────────────────────────
const boards = reactive({})
const boardLastSaved = reactive({})
const newCategoryInput = reactive({})

// Initialize boards from defaults (all 18 types)
function initBoards() {
  for (const [key, config] of Object.entries(defaultBoards)) {
    boards[key] = { ...defaultBoardConfig, ...JSON.parse(JSON.stringify(config)) }
    boardLastSaved[key] = ''
    newCategoryInput[key] = ''
  }
}

// ─── Category helpers ───────────────────────────────────────────────────────
function addCategory(boardKey) {
  const val = (newCategoryInput[boardKey] || '').trim()
  if (!val) return
  if (!boards[boardKey].categories) {
    boards[boardKey].categories = []
  }
  if (boards[boardKey].categories.includes(val)) {
    showToast('이미 존재하는 카테고리입니다.', 'error')
    return
  }
  boards[boardKey].categories.push(val)
  newCategoryInput[boardKey] = ''
}

function removeCategory(boardKey, index) {
  boards[boardKey].categories.splice(index, 1)
}

// ─── Load Settings ──────────────────────────────────────────────────────────
async function loadSettings() {
  loading.value = true
  initBoards()
  try {
    const { data } = await axios.get('/api/admin/settings/all')
    if (data) {
      for (const key of Object.keys(defaultBoards)) {
        const serverKey = `board_${key}`
        if (data[serverKey]) {
          Object.assign(boards[key], data[serverKey])
        }
      }
    }
  } catch {
    // Use defaults already initialized
  } finally {
    loading.value = false
  }
}

// ─── Save Board ─────────────────────────────────────────────────────────────
async function saveBoard(boardKey) {
  saving.value = true
  try {
    await axios.post(`/api/admin/settings/boards/${boardKey}`, { ...boards[boardKey] })
    boardLastSaved[boardKey] = new Date().toLocaleString('ko-KR')
    showToast(`${boards[boardKey].name} 설정이 저장되었습니다.`)
  } catch {
    showToast('저장에 실패했습니다.', 'error')
  } finally {
    saving.value = false
  }
}

// ─── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(loadSettings)
</script>

<style scoped>
/* Scrollbar styling for tab overflow */
::-webkit-scrollbar {
  height: 4px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}
</style>
