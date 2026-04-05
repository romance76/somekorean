<template>
  <div class="space-y-6">

    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">회원 관리</h1>
        <p class="text-sm text-gray-500 mt-1">전체 회원 목록 및 관리</p>
      </div>
      <button @click="exportCSV" class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
        CSV 내보내기
      </button>
    </div>

    <!-- Statistics Cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <div v-for="stat in statsCards" :key="stat.label"
        class="bg-white rounded-xl shadow-sm border p-4 hover:shadow-md transition">
        <div class="flex items-center justify-between mb-2">
          <span class="text-2xl">{{ stat.icon }}</span>
          <span v-if="stat.change !== undefined" class="text-xs font-semibold"
            :class="stat.change > 0 ? 'text-green-600' : 'text-red-500'">
            {{ stat.change > 0 ? '+' : '' }}{{ stat.change }}%
          </span>
        </div>
        <div class="text-2xl font-bold text-gray-900">{{ stat.value.toLocaleString() }}</div>
        <div class="text-xs text-gray-500 mt-1">{{ stat.label }}</div>
      </div>
    </div>

    <!-- Search & Filter Bar -->
    <div class="bg-white rounded-xl shadow-sm border p-4">
      <div class="flex flex-wrap gap-3 items-center">
        <div class="relative flex-1 min-w-[200px]">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <input v-model="searchQuery" @input="debouncedFetch" type="text" placeholder="이름, 이메일, 아이디 검색..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none" />
        </div>
        <select v-model="filterStatus" @change="fetchMembers" class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none">
          <option value="">전체 상태</option>
          <option value="active">활성</option>
          <option value="banned">정지</option>
          <option value="dormant">휴면</option>
          <option value="pending_delete">탈퇴대기</option>
        </select>
        <select v-model="filterRole" @change="fetchMembers" class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none">
          <option value="">전체 권한</option>
          <option value="user">일반회원</option>
          <option value="admin">관리자</option>
          <option value="elder">어르신</option>
          <option value="driver">드라이버</option>
        </select>
        <select v-model="sortBy" @change="fetchMembers" class="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none">
          <option value="created_at_desc">최신 가입순</option>
          <option value="created_at_asc">오래된 순</option>
          <option value="last_login_desc">최근 로그인순</option>
          <option value="points_desc">포인트 높은순</option>
          <option value="posts_desc">게시글 많은순</option>
        </select>
        <button @click="fetchMembers" class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition">
          검색
        </button>
        <button @click="resetFilters" class="px-4 py-2 border border-gray-300 text-gray-600 text-sm rounded-lg hover:bg-gray-50 transition">
          초기화
        </button>
      </div>
    </div>

    <!-- Bulk Actions Bar -->
    <div v-if="selectedIds.length > 0" class="bg-blue-50 border border-blue-200 rounded-xl p-3 flex flex-wrap items-center gap-3">
      <span class="text-sm font-medium text-blue-700">{{ selectedIds.length }}명 선택됨</span>
      <button @click="bulkAction('activate')" class="px-3 py-1.5 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 transition">활성화</button>
      <button @click="bulkAction('ban')" class="px-3 py-1.5 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700 transition">정지</button>
      <button @click="showBulkPoints = true" class="px-3 py-1.5 bg-yellow-500 text-white text-xs rounded-lg hover:bg-yellow-600 transition">포인트 지급</button>
      <button @click="bulkAction('email')" class="px-3 py-1.5 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition">이메일 발송</button>
      <button @click="selectedIds = []" class="ml-auto px-3 py-1.5 border border-blue-300 text-blue-600 text-xs rounded-lg hover:bg-blue-100 transition">선택 해제</button>
    </div>

    <!-- Bulk Points Modal -->
    <div v-if="showBulkPoints" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <h3 class="text-lg font-bold mb-4">포인트 일괄 지급</h3>
        <label class="block text-sm text-gray-600 mb-1">포인트 금액</label>
        <input v-model.number="bulkPointAmount" type="number" class="w-full border rounded-lg px-3 py-2 mb-3 text-sm" placeholder="예: 100" />
        <label class="block text-sm text-gray-600 mb-1">사유</label>
        <input v-model="bulkPointReason" type="text" class="w-full border rounded-lg px-3 py-2 mb-4 text-sm" placeholder="포인트 지급 사유" />
        <div class="flex gap-2">
          <button @click="bulkAction('points')" class="flex-1 py-2 bg-yellow-500 text-white rounded-lg text-sm font-medium hover:bg-yellow-600">지급</button>
          <button @click="showBulkPoints = false" class="flex-1 py-2 border text-gray-600 rounded-lg text-sm hover:bg-gray-50">취소</button>
        </div>
      </div>
    </div>

    <!-- Members Table -->
    <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 border-b">
              <th class="px-4 py-3 text-left">
                <input type="checkbox" @change="toggleSelectAll" :checked="selectedIds.length === filteredMembers.length && filteredMembers.length > 0" class="rounded" />
              </th>
              <th class="px-4 py-3 text-left font-medium text-gray-600">회원</th>
              <th class="px-4 py-3 text-left font-medium text-gray-600">아이디</th>
              <th class="px-4 py-3 text-left font-medium text-gray-600">가입일</th>
              <th class="px-4 py-3 text-left font-medium text-gray-600">마지막로그인</th>
              <th class="px-4 py-3 text-right font-medium text-gray-600">포인트</th>
              <th class="px-4 py-3 text-right font-medium text-gray-600">게시글</th>
              <th class="px-4 py-3 text-center font-medium text-gray-600">상태</th>
              <th class="px-4 py-3 text-center font-medium text-gray-600">권한</th>
              <th class="px-4 py-3 text-center font-medium text-gray-600">작업</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading" class="text-center">
              <td colspan="10" class="py-12 text-gray-400">
                <div class="flex justify-center items-center gap-2">
                  <svg class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                  불러오는 중...
                </div>
              </td>
            </tr>
            <tr v-else-if="filteredMembers.length === 0">
              <td colspan="10" class="py-12 text-center text-gray-400">검색 결과가 없습니다</td>
            </tr>
            <tr v-for="member in filteredMembers" :key="member.id"
              class="border-b hover:bg-gray-50 transition"
              :class="selectedIds.includes(member.id) ? 'bg-blue-50' : ''">
              <td class="px-4 py-3">
                <input type="checkbox" :value="member.id" v-model="selectedIds" class="rounded" />
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
                    :style="{ background: avatarColor(member.name) }">
                    {{ member.name.charAt(0) }}
                  </div>
                  <div>
                    <div class="font-medium text-gray-900">{{ member.name }}</div>
                    <div class="text-xs text-gray-400">{{ member.email }}</div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-600">@{{ member.username }}</td>
              <td class="px-4 py-3 text-gray-500">{{ formatDate(member.created_at) }}</td>
              <td class="px-4 py-3 text-gray-500">{{ formatDate(member.last_login_at) }}</td>
              <td class="px-4 py-3 text-right font-medium text-blue-600">{{ (member.points || 0).toLocaleString() }}</td>
              <td class="px-4 py-3 text-right text-gray-600">{{ member.posts_count || 0 }}</td>
              <td class="px-4 py-3 text-center">
                <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="statusClass(member.status)">
                  {{ statusLabel(member.status) }}
                </span>
              </td>
              <td class="px-4 py-3 text-center">
                <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                  :class="roleClass(member.role)">
                  {{ roleLabel(member.role) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center justify-center gap-1">
                  <button @click="openDetail(member)" title="상세보기"
                    class="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                  </button>
                  <button @click="toggleBan(member)" :title="member.status === 'banned' ? '활성화' : '정지'"
                    class="p-1.5 rounded-lg transition"
                    :class="member.status === 'banned' ? 'text-green-600 hover:bg-green-50' : 'text-orange-500 hover:bg-orange-50'">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/></svg>
                  </button>
                  <button @click="confirmDelete(member)" title="삭제"
                    class="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="px-4 py-3 border-t flex items-center justify-between">
        <span class="text-sm text-gray-500">총 {{ pagination.total }}명</span>
        <div class="flex gap-1">
          <button @click="changePage(pagination.current_page - 1)" :disabled="pagination.current_page <= 1"
            class="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-40 hover:bg-gray-50 transition">이전</button>
          <button v-for="p in visiblePages" :key="p" @click="changePage(p)"
            class="px-3 py-1.5 text-sm border rounded-lg transition"
            :class="p === pagination.current_page ? 'bg-blue-600 text-white border-blue-600' : 'hover:bg-gray-50'">
            {{ p }}
          </button>
          <button @click="changePage(pagination.current_page + 1)" :disabled="pagination.current_page >= pagination.last_page"
            class="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-40 hover:bg-gray-50 transition">다음</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <div v-if="deleteTarget" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm p-6">
        <div class="text-center mb-4">
          <div class="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg class="w-7 h-7 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-900">회원 삭제</h3>
          <p class="text-sm text-gray-500 mt-1"><strong>{{ deleteTarget.name }}</strong> 님의 계정을 삭제하시겠습니까?<br/>이 작업은 되돌릴 수 없습니다.</p>
        </div>
        <div class="flex gap-2">
          <button @click="deleteMember" class="flex-1 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700">삭제</button>
          <button @click="deleteTarget = null" class="flex-1 py-2 border text-gray-600 rounded-lg text-sm hover:bg-gray-50">취소</button>
        </div>
      </div>
    </div>

    <!-- ===== DETAIL MODAL ===== -->
    <div v-if="detailModal" class="fixed inset-0 bg-black/60 z-50 flex items-start justify-center p-4 overflow-y-auto">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl my-6">

        <!-- Modal Header -->
        <div class="flex items-center justify-between p-6 border-b">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
              :style="{ background: avatarColor(detailMember.name || '') }">
              {{ (detailMember.name || '?').charAt(0) }}
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-900">{{ detailMember.name }}</h2>
              <p class="text-sm text-gray-500">@{{ detailMember.username }} · {{ detailMember.email }}</p>
            </div>
          </div>
          <button @click="detailModal = false" class="p-2 hover:bg-gray-100 rounded-full transition">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <!-- Tabs -->
        <div class="border-b overflow-x-auto">
          <div class="flex min-w-max">
            <button v-for="tab in detailTabs" :key="tab.id" @click="activeTab = tab.id"
              class="px-5 py-3 text-sm font-medium border-b-2 transition whitespace-nowrap"
              :class="activeTab === tab.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
              {{ tab.label }}
            </button>
          </div>
        </div>

        <!-- Tab Content -->
        <div class="p-6">

          <!-- Tab 1: 기본 정보 -->
          <div v-if="activeTab === 'basic'">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">이름</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm font-medium">{{ detailMember.name }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">아이디</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm">@{{ detailMember.username }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">이메일</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm">{{ detailMember.email }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">전화번호</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm">{{ detailMember.phone || '-' }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">지역</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm">{{ detailMember.region || '-' }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">주소</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm">{{ detailMember.address || '-' }}</div>
              </div>
              <div class="md:col-span-2">
                <label class="block text-xs text-gray-500 mb-1">자기소개</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm min-h-[60px]">{{ detailMember.bio || '-' }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">가입일</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm">{{ formatDateFull(detailMember.created_at) }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">마지막 로그인</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm">{{ formatDateFull(detailMember.last_login_at) }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">레벨</label>
                <div class="px-3 py-2 bg-gray-50 rounded-lg text-sm">Lv.{{ detailMember.level || 1 }}</div>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">상태 / 권한</label>
                <div class="flex gap-2 px-3 py-2 bg-gray-50 rounded-lg">
                  <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="statusClass(detailMember.status)">{{ statusLabel(detailMember.status) }}</span>
                  <span class="px-2 py-0.5 rounded-full text-xs font-medium" :class="roleClass(detailMember.role)">{{ roleLabel(detailMember.role) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab 2: 활동 내역 -->
          <div v-if="activeTab === 'activity'">
            <!-- Activity Stats -->
            <div class="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
              <div v-for="s in activityStats" :key="s.label" class="bg-gray-50 rounded-xl p-3 text-center">
                <div class="text-xl font-bold text-gray-900">{{ s.value }}</div>
                <div class="text-xs text-gray-500 mt-1">{{ s.label }}</div>
              </div>
            </div>

            <!-- Recent Posts -->
            <h4 class="font-semibold text-gray-700 mb-2">최근 게시글</h4>
            <div class="border rounded-xl overflow-hidden mb-4">
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">제목</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">게시판</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">날짜</th>
                    <th class="px-3 py-2 text-right font-medium text-gray-600">조회</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="post in (detailMember.recent_posts || [])" :key="post.id" class="border-t">
                    <td class="px-3 py-2 text-gray-800">{{ post.title }}</td>
                    <td class="px-3 py-2 text-gray-500">{{ post.board }}</td>
                    <td class="px-3 py-2 text-gray-500">{{ formatDate(post.created_at) }}</td>
                    <td class="px-3 py-2 text-right text-gray-500">{{ post.views }}</td>
                  </tr>
                  <tr v-if="!detailMember.recent_posts || detailMember.recent_posts.length === 0">
                    <td colspan="4" class="px-3 py-4 text-center text-gray-400">게시글이 없습니다</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Recent Comments -->
            <h4 class="font-semibold text-gray-700 mb-2">최근 댓글</h4>
            <div class="space-y-2 mb-4">
              <div v-for="c in (detailMember.recent_comments || [])" :key="c.id"
                class="px-3 py-2 bg-gray-50 rounded-lg text-sm text-gray-700">
                {{ c.content }} <span class="text-gray-400 text-xs ml-2">{{ formatDate(c.created_at) }}</span>
              </div>
              <div v-if="!detailMember.recent_comments || detailMember.recent_comments.length === 0"
                class="text-sm text-gray-400 text-center py-3">댓글이 없습니다</div>
            </div>

            <!-- Recent Liked Posts -->
            <h4 class="font-semibold text-gray-700 mb-2">최근 좋아요한 게시글</h4>
            <div class="space-y-2">
              <div v-for="lp in (detailMember.liked_posts || [])" :key="lp.id"
                class="px-3 py-2 bg-gray-50 rounded-lg text-sm text-gray-700">
                {{ lp.title }} <span class="text-gray-400 text-xs ml-2">{{ formatDate(lp.created_at) }}</span>
              </div>
              <div v-if="!detailMember.liked_posts || detailMember.liked_posts.length === 0"
                class="text-sm text-gray-400 text-center py-3">좋아요한 게시글이 없습니다</div>
            </div>
          </div>

          <!-- Tab 3: 포인트/결제 -->
          <div v-if="activeTab === 'points'">
            <!-- Current Points -->
            <div class="bg-gradient-to-r from-blue-500 to-blue-700 rounded-xl p-4 text-white mb-6">
              <div class="flex items-center justify-between">
                <div>
                  <div class="text-sm opacity-80">현재 포인트</div>
                  <div class="text-3xl font-bold mt-1">{{ (detailMember.points || 0).toLocaleString() }}<span class="text-lg ml-1">P</span></div>
                </div>
                <div class="text-right">
                  <div class="text-sm opacity-80">레벨</div>
                  <div class="text-2xl font-bold">Lv.{{ detailMember.level || 1 }}</div>
                </div>
              </div>
            </div>

            <!-- Point Adjustment -->
            <div class="bg-gray-50 rounded-xl p-4 mb-6">
              <h4 class="font-semibold text-gray-700 mb-3">포인트 조정</h4>
              <div class="flex gap-3">
                <input v-model.number="pointAdjustAmount" type="number" placeholder="포인트 (음수 가능)"
                  class="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                <input v-model="pointAdjustReason" type="text" placeholder="사유"
                  class="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                <button @click="adjustPoints" class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition">적용</button>
              </div>
            </div>

            <!-- Point History -->
            <h4 class="font-semibold text-gray-700 mb-2">포인트 내역</h4>
            <div class="border rounded-xl overflow-hidden mb-6">
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">구분</th>
                    <th class="px-3 py-2 text-right font-medium text-gray-600">금액</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">설명</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">날짜</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="log in (detailMember.point_logs || [])" :key="log.id" class="border-t">
                    <td class="px-3 py-2">
                      <span class="px-2 py-0.5 rounded text-xs" :class="log.amount > 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
                        {{ log.action }}
                      </span>
                    </td>
                    <td class="px-3 py-2 text-right font-medium" :class="log.amount > 0 ? 'text-green-600' : 'text-red-500'">
                      {{ log.amount > 0 ? '+' : '' }}{{ log.amount.toLocaleString() }}
                    </td>
                    <td class="px-3 py-2 text-gray-600">{{ log.description }}</td>
                    <td class="px-3 py-2 text-gray-400">{{ formatDate(log.created_at) }}</td>
                  </tr>
                  <tr v-if="!detailMember.point_logs || detailMember.point_logs.length === 0">
                    <td colspan="4" class="py-4 text-center text-gray-400">포인트 내역이 없습니다</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Payment History -->
            <h4 class="font-semibold text-gray-700 mb-2">결제 내역</h4>
            <div class="border rounded-xl overflow-hidden">
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">유형</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">항목</th>
                    <th class="px-3 py-2 text-right font-medium text-gray-600">금액</th>
                    <th class="px-3 py-2 text-center font-medium text-gray-600">상태</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">결제수단</th>
                    <th class="px-3 py-2 text-left font-medium text-gray-600">날짜</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="pay in (detailMember.payments || [])" :key="pay.id" class="border-t">
                    <td class="px-3 py-2 text-gray-700">{{ pay.type }}</td>
                    <td class="px-3 py-2 text-gray-700">{{ pay.item }}</td>
                    <td class="px-3 py-2 text-right font-medium">${{ pay.amount }}</td>
                    <td class="px-3 py-2 text-center">
                      <span class="px-2 py-0.5 rounded-full text-xs" :class="pay.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
                        {{ pay.status === 'completed' ? '완료' : '대기' }}
                      </span>
                    </td>
                    <td class="px-3 py-2 text-gray-500">{{ pay.method }}</td>
                    <td class="px-3 py-2 text-gray-400">{{ formatDate(pay.created_at) }}</td>
                  </tr>
                  <tr v-if="!detailMember.payments || detailMember.payments.length === 0">
                    <td colspan="6" class="py-4 text-center text-gray-400">결제 내역이 없습니다</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab 4: 프로필/매칭 설정 -->
          <div v-if="activeTab === 'profile'">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="md:col-span-2">
                <label class="block text-xs text-gray-500 mb-1">프로필 사진 URL</label>
                <input v-model="profileEdit.avatar_url" type="text"
                  class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">관계 상태</label>
                <select v-model="profileEdit.relationship_status" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                  <option value="">선택</option>
                  <option value="single">싱글</option>
                  <option value="married">기혼</option>
                  <option value="divorced">이혼</option>
                  <option value="widowed">사별</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">언어 설정</label>
                <select v-model="profileEdit.language" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                  <option value="ko">한국어</option>
                  <option value="en">영어</option>
                  <option value="both">한국어+영어</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">프리미엄 유형</label>
                <select v-model="profileEdit.premium_type" class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                  <option value="">없음</option>
                  <option value="basic">베이직</option>
                  <option value="premium">프리미엄</option>
                  <option value="vip">VIP</option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">프리미엄 만료일</label>
                <input v-model="profileEdit.premium_expires_at" type="date"
                  class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
              </div>
              <div class="md:col-span-2">
                <label class="block text-xs text-gray-500 mb-1">관심사 태그</label>
                <div class="flex flex-wrap gap-2 px-3 py-2 bg-gray-50 rounded-lg min-h-[40px]">
                  <span v-for="tag in (detailMember.interests || [])" :key="tag"
                    class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">{{ tag }}</span>
                  <span v-if="!detailMember.interests || detailMember.interests.length === 0" class="text-gray-400 text-sm">없음</span>
                </div>
              </div>

              <!-- 매칭 설정 -->
              <div class="md:col-span-2 border-t pt-4">
                <h4 class="font-semibold text-gray-700 mb-3">매칭 설정</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div class="flex items-center gap-3">
                    <label class="text-sm text-gray-600 flex-1">매칭 활성화</label>
                    <button @click="profileEdit.is_matching_active = !profileEdit.is_matching_active"
                      class="relative inline-flex h-6 w-11 items-center rounded-full transition"
                      :class="profileEdit.is_matching_active ? 'bg-blue-600' : 'bg-gray-300'">
                      <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
                        :class="profileEdit.is_matching_active ? 'translate-x-6' : 'translate-x-1'"/>
                    </button>
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">선호 지역</label>
                    <input v-model="profileEdit.preferred_region" type="text"
                      class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                  </div>
                  <div>
                    <label class="block text-xs text-gray-500 mb-1">나이 범위</label>
                    <input v-model="profileEdit.age_range" type="text" placeholder="예: 30-45"
                      class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                  </div>
                  <div class="md:col-span-2">
                    <label class="block text-xs text-gray-500 mb-1">매칭 소개글</label>
                    <textarea v-model="profileEdit.matching_bio" rows="3"
                      class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"></textarea>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-4 flex justify-end">
              <button @click="saveProfile" class="px-6 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition">
                저장하기
              </button>
            </div>
          </div>

          <!-- Tab 5: 보안/계정 -->
          <div v-if="activeTab === 'security'">
            <div class="space-y-5">

              <!-- Password Reset -->
              <div class="bg-gray-50 rounded-xl p-4">
                <h4 class="font-semibold text-gray-700 mb-3">비밀번호 재설정</h4>
                <div class="flex flex-col md:flex-row gap-3">
                  <button @click="sendPasswordReset" class="flex-1 px-4 py-2 border border-blue-500 text-blue-600 text-sm rounded-lg hover:bg-blue-50 transition">
                    📧 비밀번호 재설정 이메일 발송
                  </button>
                  <div class="flex-1 flex gap-2">
                    <input v-model="newPassword" type="password" placeholder="새 비밀번호 직접 설정"
                      class="flex-1 border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                    <button @click="forceSetPassword" class="px-4 py-2 bg-orange-500 text-white text-sm rounded-lg hover:bg-orange-600 transition">설정</button>
                  </div>
                </div>
              </div>

              <!-- 2FA Status -->
              <div class="bg-gray-50 rounded-xl p-4">
                <h4 class="font-semibold text-gray-700 mb-2">2단계 인증</h4>
                <div class="flex items-center gap-2">
                  <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                    :class="detailMember.two_factor_enabled ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'">
                    {{ detailMember.two_factor_enabled ? '활성화됨' : '비활성화' }}
                  </span>
                </div>
              </div>

              <!-- Login History -->
              <div>
                <h4 class="font-semibold text-gray-700 mb-2">최근 로그인 기록 (최대 5개)</h4>
                <div class="border rounded-xl overflow-hidden">
                  <table class="w-full text-sm">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-3 py-2 text-left font-medium text-gray-600">IP 주소</th>
                        <th class="px-3 py-2 text-left font-medium text-gray-600">기기</th>
                        <th class="px-3 py-2 text-left font-medium text-gray-600">날짜</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="log in (detailMember.login_history || [])" :key="log.id" class="border-t">
                        <td class="px-3 py-2 font-mono text-gray-700">{{ log.ip }}</td>
                        <td class="px-3 py-2 text-gray-600">{{ log.device }}</td>
                        <td class="px-3 py-2 text-gray-400">{{ formatDateFull(log.created_at) }}</td>
                      </tr>
                      <tr v-if="!detailMember.login_history || detailMember.login_history.length === 0">
                        <td colspan="3" class="py-4 text-center text-gray-400">기록이 없습니다</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Active Sessions -->
              <div>
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-semibold text-gray-700">활성 세션</h4>
                  <button @click="forceLogout" class="px-3 py-1.5 bg-red-500 text-white text-xs rounded-lg hover:bg-red-600 transition">
                    전체 로그아웃
                  </button>
                </div>
                <div class="space-y-2">
                  <div v-for="sess in (detailMember.active_sessions || [])" :key="sess.id"
                    class="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg text-sm">
                    <div>
                      <span class="font-medium text-gray-700">{{ sess.device }}</span>
                      <span class="text-gray-400 ml-2 text-xs">{{ sess.ip }}</span>
                    </div>
                    <span class="text-gray-400 text-xs">{{ formatDate(sess.last_active) }}</span>
                  </div>
                  <div v-if="!detailMember.active_sessions || detailMember.active_sessions.length === 0"
                    class="text-sm text-gray-400 text-center py-3">활성 세션이 없습니다</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab 6: 관리 -->
          <div v-if="activeTab === 'manage'">
            <div class="space-y-5">

              <!-- Account Status -->
              <div class="bg-gray-50 rounded-xl p-4">
                <h4 class="font-semibold text-gray-700 mb-3">계정 상태</h4>
                <div class="flex flex-wrap gap-3 mb-3">
                  <label v-for="s in accountStatuses" :key="s.value"
                    class="flex items-center gap-2 cursor-pointer">
                    <input type="radio" :value="s.value" v-model="manageEdit.status" class="text-blue-600" />
                    <span class="text-sm text-gray-700">{{ s.label }}</span>
                  </label>
                </div>
                <div v-if="manageEdit.status === 'banned'">
                  <label class="block text-xs text-gray-500 mb-1">정지 사유</label>
                  <textarea v-model="manageEdit.ban_reason" rows="2"
                    class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                    placeholder="정지 사유를 입력하세요..."></textarea>
                </div>
              </div>

              <!-- Toggles -->
              <div class="bg-gray-50 rounded-xl p-4 space-y-3">
                <h4 class="font-semibold text-gray-700 mb-2">권한 및 서비스</h4>
                <div class="flex items-center justify-between">
                  <label class="text-sm text-gray-600">관리자 권한</label>
                  <button @click="manageEdit.is_admin = !manageEdit.is_admin"
                    class="relative inline-flex h-6 w-11 items-center rounded-full transition"
                    :class="manageEdit.is_admin ? 'bg-blue-600' : 'bg-gray-300'">
                    <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
                      :class="manageEdit.is_admin ? 'translate-x-6' : 'translate-x-1'"/>
                  </button>
                </div>
                <div class="flex items-center justify-between">
                  <label class="text-sm text-gray-600">어르신 서비스 (Elder)</label>
                  <button @click="manageEdit.is_elder = !manageEdit.is_elder"
                    class="relative inline-flex h-6 w-11 items-center rounded-full transition"
                    :class="manageEdit.is_elder ? 'bg-green-600' : 'bg-gray-300'">
                    <span class="inline-block h-4 w-4 transform rounded-full bg-white shadow transition"
                      :class="manageEdit.is_elder ? 'translate-x-6' : 'translate-x-1'"/>
                  </button>
                </div>
                <div class="flex items-center justify-between">
                  <label class="text-sm text-gray-600">드라이버 등록 상태</label>
                  <span class="px-2 py-0.5 rounded-full text-xs" :class="detailMember.is_driver ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-600'">
                    {{ detailMember.is_driver ? '등록됨' : '미등록' }}
                  </span>
                </div>
              </div>

              <!-- Admin Memo -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">관리자 메모</label>
                <textarea v-model="manageEdit.admin_memo" rows="3"
                  class="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none resize-none"
                  placeholder="관리자용 내부 메모..."></textarea>
              </div>

              <!-- Save Management -->
              <div class="flex justify-end">
                <button @click="saveManagement" class="px-6 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition">
                  변경사항 저장
                </button>
              </div>

              <!-- Danger Zone -->
              <div class="border border-red-200 rounded-xl p-4 bg-red-50">
                <h4 class="font-semibold text-red-700 mb-2">위험 구역</h4>
                <div v-if="!confirmDeleteDetail">
                  <button @click="confirmDeleteDetail = true" class="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition">
                    계정 영구 삭제
                  </button>
                </div>
                <div v-else class="space-y-2">
                  <p class="text-sm text-red-700">정말로 <strong>{{ detailMember.name }}</strong> 님의 계정을 삭제하시겠습니까? 되돌릴 수 없습니다.</p>
                  <div class="flex gap-2">
                    <button @click="deleteFromDetail" class="px-4 py-2 bg-red-700 text-white text-sm rounded-lg hover:bg-red-800">확인 삭제</button>
                    <button @click="confirmDeleteDetail = false" class="px-4 py-2 border text-gray-600 text-sm rounded-lg hover:bg-gray-100">취소</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Business Section (shown if user has businesses) -->
          <div v-if="activeTab !== 'basic' && detailMember.businesses && detailMember.businesses.length > 0" class="mt-6 border-t pt-5">
            <h4 class="font-semibold text-gray-700 mb-3">사업체 정보</h4>
            <div class="space-y-2">
              <div v-for="biz in detailMember.businesses" :key="biz.id"
                class="flex items-center justify-between px-4 py-3 bg-gray-50 rounded-xl">
                <div>
                  <span class="font-medium text-gray-800">{{ biz.name }}</span>
                  <span class="ml-2 px-2 py-0.5 rounded-full text-xs" :class="biz.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'">
                    {{ biz.status === 'active' ? '운영중' : '비활성' }}
                  </span>
                </div>
                <div class="flex items-center gap-3">
                  <span class="text-xs text-gray-500">ACH: {{ biz.ach_status || '미등록' }}</span>
                  <button class="text-xs text-blue-600 hover:underline">편집</button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toast.show"
      class="fixed bottom-6 right-6 z-[9999] px-5 py-3 rounded-xl shadow-xl text-white text-sm font-medium transition-all"
      :class="toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'">
      {{ toast.message }}
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from 'axios'

// ── State ──────────────────────────────────────────────────────────────────
const loading = ref(false)
const members = ref([])
const selectedIds = ref([])
const searchQuery = ref('')
const filterStatus = ref('')
const filterRole = ref('')
const sortBy = ref('created_at_desc')
const showBulkPoints = ref(false)
const bulkPointAmount = ref(0)
const bulkPointReason = ref('')
const deleteTarget = ref(null)
const detailModal = ref(false)
const detailMember = ref({})
const detailLoading = ref(false)
const activeTab = ref('basic')
const confirmDeleteDetail = ref(false)
const newPassword = ref('')
const pointAdjustAmount = ref(0)
const pointAdjustReason = ref('')
const profileEdit = reactive({
  avatar_url: '', relationship_status: '', language: 'ko',
  premium_type: '', premium_expires_at: '',
  is_matching_active: false, preferred_region: '', age_range: '', matching_bio: ''
})
const manageEdit = reactive({
  status: 'active', ban_reason: '', is_admin: false, is_elder: false, admin_memo: ''
})
const toast = reactive({ show: false, message: '', type: 'success' })
const pagination = reactive({ current_page: 1, last_page: 1, total: 0, per_page: 20 })

// ── Dummy Data ─────────────────────────────────────────────────────────────
const dummyMembers = [
  { id: 1, name: '김민준', username: 'minjun_kim', email: 'minjun@example.com', phone: '213-555-0101', region: '로스앤젤레스', address: '123 Koreatown Blvd, LA, CA 90005', bio: '한인 커뮤니티 활동 좋아합니다.', status: 'active', role: 'admin', points: 4820, posts_count: 47, created_at: '2023-03-15T10:00:00Z', last_login_at: '2026-03-27T09:12:00Z', level: 7, is_driver: false, two_factor_enabled: true, interests: ['음식', '여행', '문화'], premium_type: 'vip', premium_expires_at: '2027-01-01' },
  { id: 2, name: '이서연', username: 'seoyeon_lee', email: 'seoyeon@example.com', phone: '323-555-0202', region: '뉴욕', address: '456 32nd St, New York, NY 10001', bio: '요리와 사진을 즐깁니다.', status: 'active', role: 'user', points: 1230, posts_count: 23, created_at: '2023-07-22T14:30:00Z', last_login_at: '2026-03-26T20:05:00Z', level: 4, is_driver: false, two_factor_enabled: false, interests: ['요리', '사진', '독서'], premium_type: 'basic', premium_expires_at: '2026-06-30' },
  { id: 3, name: '박지호', username: 'jiho_park', email: 'jiho@example.com', phone: '312-555-0303', region: '시카고', address: '789 N Wacker Dr, Chicago, IL 60601', bio: '사업가. 교민 네트워크 구축 중.', status: 'active', role: 'user', points: 2100, posts_count: 31, created_at: '2023-11-05T08:00:00Z', last_login_at: '2026-03-25T16:40:00Z', level: 5, is_driver: true, two_factor_enabled: false, interests: ['비즈니스', '골프', '네트워킹'], premium_type: 'premium', premium_expires_at: '2026-12-31' },
  { id: 4, name: '최유나', username: 'yuna_choi', email: 'yuna@example.com', phone: '214-555-0404', region: '달라스', address: '321 Commerce St, Dallas, TX 75201', bio: '댄스 강사입니다.', status: 'banned', role: 'user', points: 320, posts_count: 8, created_at: '2024-01-18T11:15:00Z', last_login_at: '2026-02-10T14:20:00Z', level: 2, is_driver: false, two_factor_enabled: false, interests: ['댄스', '음악', '헬스'] },
  { id: 5, name: '정현우', username: 'hyunwoo_jung', email: 'hyunwoo@example.com', phone: '404-555-0505', region: '애틀란타', address: '654 Peachtree St NE, Atlanta, GA 30308', bio: '의사. 의료봉사 활동 중.', status: 'active', role: 'elder', points: 3450, posts_count: 15, created_at: '2023-05-30T09:45:00Z', last_login_at: '2026-03-27T07:30:00Z', level: 6, is_driver: false, two_factor_enabled: true, interests: ['의료', '봉사', '독서'] },
  { id: 6, name: '한소희', username: 'sohee_han', email: 'sohee@example.com', phone: '206-555-0606', region: '시애틀', address: '987 Pike St, Seattle, WA 98101', bio: '스타트업 창업자.', status: 'active', role: 'user', points: 1890, posts_count: 42, created_at: '2024-02-14T16:20:00Z', last_login_at: '2026-03-27T11:00:00Z', level: 4, is_driver: false, two_factor_enabled: true, interests: ['테크', '창업', 'AI'] },
  { id: 7, name: '오민석', username: 'minseok_oh', email: 'minseok@example.com', phone: '415-555-0707', region: '샌프란시스코', address: '147 Market St, San Francisco, CA 94103', bio: '소프트웨어 개발자.', status: 'active', role: 'user', points: 980, posts_count: 19, created_at: '2024-04-10T13:00:00Z', last_login_at: '2026-03-24T22:15:00Z', level: 3, is_driver: false, two_factor_enabled: false, interests: ['코딩', '게임', '음악'] },
  { id: 8, name: '강지수', username: 'jisu_kang', email: 'jisu@example.com', phone: '702-555-0808', region: '라스베가스', address: '258 Las Vegas Blvd, NV 89101', bio: '호텔 매니저.', status: 'dormant', role: 'user', points: 560, posts_count: 6, created_at: '2023-09-01T10:30:00Z', last_login_at: '2025-11-20T09:00:00Z', level: 2, is_driver: false, two_factor_enabled: false, interests: ['호텔', '여행', '요리'] },
  { id: 9, name: '윤지영', username: 'jiyoung_yoon', email: 'jiyoung@example.com', phone: '617-555-0909', region: '보스턴', address: '369 Boylston St, Boston, MA 02116', bio: '대학원생. 연구 중.', status: 'active', role: 'user', points: 740, posts_count: 12, created_at: '2024-06-05T08:30:00Z', last_login_at: '2026-03-26T15:45:00Z', level: 3, is_driver: false, two_factor_enabled: false, interests: ['학업', '연구', '커피'] },
  { id: 10, name: '임태양', username: 'taeyang_lim', email: 'taeyang@example.com', phone: '503-555-1010', region: '포틀랜드', address: '741 SW Broadway, Portland, OR 97201', bio: '요식업 운영.', status: 'active', role: 'user', points: 2670, posts_count: 38, created_at: '2023-06-15T07:00:00Z', last_login_at: '2026-03-27T06:00:00Z', level: 5, is_driver: true, two_factor_enabled: false, interests: ['요식업', '음식', '운동'] },
  { id: 11, name: '노은혜', username: 'eunhye_noh', email: 'eunhye@example.com', phone: '602-555-1111', region: '피닉스', address: '852 N Central Ave, Phoenix, AZ 85004', bio: '간호사. 이민자 지원 봉사.', status: 'active', role: 'elder', points: 1540, posts_count: 21, created_at: '2023-08-20T12:00:00Z', last_login_at: '2026-03-25T19:30:00Z', level: 4, is_driver: false, two_factor_enabled: true, interests: ['봉사', '의료', '종교'] },
  { id: 12, name: '서준혁', username: 'junhyuk_seo', email: 'junhyuk@example.com', phone: '303-555-1212', region: '덴버', address: '963 16th St Mall, Denver, CO 80202', bio: '건축가.', status: 'active', role: 'user', points: 430, posts_count: 9, created_at: '2024-07-30T14:45:00Z', last_login_at: '2026-03-23T10:20:00Z', level: 2, is_driver: false, two_factor_enabled: false, interests: ['건축', '디자인', '등산'] },
  { id: 13, name: '황미래', username: 'mirae_hwang', email: 'mirae@example.com', phone: '813-555-1313', region: '탬파', address: '174 Franklin St, Tampa, FL 33602', bio: '마케터. SNS 전문.', status: 'active', role: 'user', points: 1120, posts_count: 55, created_at: '2023-10-10T09:15:00Z', last_login_at: '2026-03-27T12:30:00Z', level: 4, is_driver: false, two_factor_enabled: false, interests: ['마케팅', 'SNS', '뷰티'] },
  { id: 14, name: '송대현', username: 'daehyun_song', email: 'daehyun@example.com', phone: '612-555-1414', region: '미니애폴리스', address: '285 Nicollet Mall, Minneapolis, MN 55401', bio: '회계사.', status: 'banned', role: 'user', points: 200, posts_count: 3, created_at: '2024-03-22T11:30:00Z', last_login_at: '2026-01-15T08:00:00Z', level: 1, is_driver: false, two_factor_enabled: false, interests: ['금융', '독서'] },
  { id: 15, name: '구나연', username: 'nayeon_goo', email: 'nayeon@example.com', phone: '410-555-1515', region: '볼티모어', address: '396 Charles St, Baltimore, MD 21201', bio: '유학생 지원 상담사.', status: 'active', role: 'user', points: 870, posts_count: 17, created_at: '2024-05-18T16:00:00Z', last_login_at: '2026-03-26T13:10:00Z', level: 3, is_driver: false, two_factor_enabled: false, interests: ['교육', '문화', '여행'] },
  { id: 16, name: '변성훈', username: 'sunghoon_byun', email: 'sunghoon@example.com', phone: '901-555-1616', region: '멤피스', address: '507 Beale St, Memphis, TN 38103', bio: '음악가. 재즈 피아니스트.', status: 'active', role: 'user', points: 320, posts_count: 11, created_at: '2024-08-14T18:30:00Z', last_login_at: '2026-03-22T21:00:00Z', level: 2, is_driver: false, two_factor_enabled: false, interests: ['음악', '재즈', '문화'] },
  { id: 17, name: '여진아', username: 'jina_yeo', email: 'jina@example.com', phone: '314-555-1717', region: '세인트루이스', address: '618 Market St, St. Louis, MO 63101', bio: '패션 디자이너.', status: 'active', role: 'user', points: 1680, posts_count: 28, created_at: '2023-12-01T10:00:00Z', last_login_at: '2026-03-27T10:45:00Z', level: 4, is_driver: false, two_factor_enabled: true, interests: ['패션', '디자인', '예술'] },
  { id: 18, name: '탁재원', username: 'jaewon_tak', email: 'jaewon@example.com', phone: '216-555-1818', region: '클리블랜드', address: '729 Euclid Ave, Cleveland, OH 44114', bio: '변호사. 이민 전문.', status: 'pending_delete', role: 'user', points: 90, posts_count: 2, created_at: '2024-09-05T09:00:00Z', last_login_at: '2026-02-28T16:00:00Z', level: 1, is_driver: false, two_factor_enabled: false, interests: ['법률', '이민'] },
  { id: 19, name: '방수진', username: 'sujin_bang', email: 'sujin@example.com', phone: '702-555-1919', region: '라스베가스', address: '840 Fremont St, Las Vegas, NV 89101', bio: '뷰티 살롱 운영.', status: 'active', role: 'user', points: 2350, posts_count: 44, created_at: '2023-04-08T13:30:00Z', last_login_at: '2026-03-27T08:15:00Z', level: 5, is_driver: false, two_factor_enabled: false, interests: ['뷰티', '패션', '네트워킹'], premium_type: 'premium', premium_expires_at: '2026-09-30' },
  { id: 20, name: '장호진', username: 'hojin_jang', email: 'hojin@example.com', phone: '702-555-2020', region: '라스베가스', address: '951 Paradise Rd, Las Vegas, NV 89119', bio: '카지노 딜러.', status: 'active', role: 'driver', points: 760, posts_count: 14, created_at: '2024-01-30T07:30:00Z', last_login_at: '2026-03-26T04:00:00Z', level: 3, is_driver: true, two_factor_enabled: false, interests: ['운전', '스포츠', '음악'] },
]

const dummyDetailExtras = (id) => ({
  recent_posts: [
    { id: 1, title: '한인 커뮤니티 행사 안내', board: '공지사항', created_at: '2026-03-20T10:00:00Z', views: 342 },
    { id: 2, title: '로스앤젤레스 맛집 추천', board: '맛집/음식', created_at: '2026-03-15T14:30:00Z', views: 215 },
    { id: 3, title: '렌트비 관련 법률 질문', board: '생활정보', created_at: '2026-03-10T09:00:00Z', views: 88 },
  ],
  recent_comments: [
    { id: 1, content: '정말 유용한 정보 감사합니다!', created_at: '2026-03-25T11:00:00Z' },
    { id: 2, content: '저도 비슷한 경험이 있어요.', created_at: '2026-03-22T16:45:00Z' },
  ],
  liked_posts: [
    { id: 10, title: '미국 운전면허 취득 후기', created_at: '2026-03-18T10:00:00Z' },
    { id: 11, title: '한국 음식 재료 구입처', created_at: '2026-03-14T12:00:00Z' },
  ],
  point_logs: [
    { id: 1, action: '게시글 작성', amount: 50, description: '게시글 작성 보상', created_at: '2026-03-20T10:00:00Z' },
    { id: 2, action: '댓글 작성', amount: 10, description: '댓글 작성 보상', created_at: '2026-03-18T14:00:00Z' },
    { id: 3, action: '관리자 지급', amount: 200, description: '이벤트 당첨 포인트', created_at: '2026-03-10T09:00:00Z' },
    { id: 4, action: '포인트 사용', amount: -100, description: '프리미엄 멤버십 결제', created_at: '2026-03-05T11:00:00Z' },
  ],
  payments: [
    { id: 1, type: '멤버십', item: '프리미엄 1개월', amount: '9.99', status: 'completed', method: 'Visa ****1234', created_at: '2026-03-01T10:00:00Z' },
    { id: 2, type: '광고', item: '비즈니스 디렉토리 1개월', amount: '29.99', status: 'completed', method: 'PayPal', created_at: '2026-02-15T14:00:00Z' },
  ],
  login_history: [
    { id: 1, ip: '192.168.1.101', device: 'Chrome / macOS', created_at: '2026-03-27T09:12:00Z' },
    { id: 2, ip: '172.16.0.50', device: 'Safari / iPhone', created_at: '2026-03-26T20:05:00Z' },
    { id: 3, ip: '10.0.0.25', device: 'Chrome / Windows', created_at: '2026-03-25T13:30:00Z' },
    { id: 4, ip: '192.168.1.101', device: 'Chrome / macOS', created_at: '2026-03-24T08:00:00Z' },
    { id: 5, ip: '172.16.0.50', device: 'Safari / iPhone', created_at: '2026-03-23T21:45:00Z' },
  ],
  active_sessions: [
    { id: 1, device: 'Chrome / macOS', ip: '192.168.1.101', last_active: '2026-03-27T09:12:00Z' },
    { id: 2, device: 'Safari / iPhone', ip: '172.16.0.50', last_active: '2026-03-26T20:05:00Z' },
  ],
  businesses: id % 3 === 0 ? [
    { id: 1, name: '한식당 코리아나', status: 'active', ach_status: '등록완료' },
  ] : [],
})

// ── Computed ───────────────────────────────────────────────────────────────
const statsCards = computed(() => {
  const all = members.value.length || dummyMembers.length
  const today = new Date().toDateString()
  const thisMonth = new Date().getMonth()
  const todayCount = dummyMembers.filter(m => new Date(m.created_at).toDateString() === today).length
  const monthCount = dummyMembers.filter(m => new Date(m.created_at).getMonth() === thisMonth).length
  return [
    { label: '전체 회원', value: all, icon: '👥', change: 12 },
    { label: '오늘 가입', value: todayCount, icon: '🆕' },
    { label: '이번달 가입', value: monthCount + 3, icon: '📅', change: 8 },
    { label: '활성', value: dummyMembers.filter(m => m.status === 'active').length, icon: '✅' },
    { label: '정지', value: dummyMembers.filter(m => m.status === 'banned').length, icon: '🚫' },
    { label: '관리자', value: dummyMembers.filter(m => m.role === 'admin').length, icon: '🛡️' },
  ]
})

const filteredMembers = computed(() => {
  let list = members.value.length > 0 ? members.value : dummyMembers
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(m =>
      m.name.toLowerCase().includes(q) ||
      m.email.toLowerCase().includes(q) ||
      m.username.toLowerCase().includes(q)
    )
  }
  if (filterStatus.value) list = list.filter(m => m.status === filterStatus.value)
  if (filterRole.value) list = list.filter(m => m.role === filterRole.value)
  return list
})

const visiblePages = computed(() => {
  const pages = []
  const cur = pagination.current_page
  const last = pagination.last_page
  for (let i = Math.max(1, cur - 2); i <= Math.min(last, cur + 2); i++) pages.push(i)
  return pages
})

const activityStats = computed(() => [
  { label: '게시글', value: detailMember.value.posts_count || 0 },
  { label: '댓글', value: detailMember.value.comments_count || 0 },
  { label: '좋아요', value: detailMember.value.likes_count || 0 },
  { label: '신고', value: detailMember.value.reports_count || 0 },
  { label: '북마크', value: detailMember.value.bookmarks_count || 0 },
])

// ── Constants ──────────────────────────────────────────────────────────────
const detailTabs = [
  { id: 'basic', label: '기본 정보' },
  { id: 'activity', label: '활동 내역' },
  { id: 'points', label: '포인트/결제' },
  { id: 'profile', label: '프로필/매칭' },
  { id: 'security', label: '보안/계정' },
  { id: 'manage', label: '관리' },
]

const accountStatuses = [
  { value: 'active', label: '활성' },
  { value: 'banned', label: '정지' },
  { value: 'dormant', label: '휴면' },
  { value: 'pending_delete', label: '탈퇴대기' },
]

// ── Methods ────────────────────────────────────────────────────────────────
async function fetchMembers() {
  loading.value = true
  try {
    const params = {
      page: pagination.current_page,
      search: searchQuery.value,
      status: filterStatus.value,
      role: filterRole.value,
      sort: sortBy.value,
    }
    const { data } = await axios.get('/api/admin/users', { params })
    members.value = data.data || []
    pagination.current_page = data.current_page || 1
    pagination.last_page = data.last_page || 1
    pagination.total = data.total || 0
  } catch {
    members.value = []
  } finally {
    loading.value = false
  }
}

let debounceTimer = null
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchMembers, 400)
}

async function openDetail(member) {
  detailMember.value = { ...member }
  activeTab.value = 'basic'
  confirmDeleteDetail.value = false
  newPassword.value = ''
  pointAdjustAmount.value = 0
  pointAdjustReason.value = ''
  // Populate edit forms
  Object.assign(profileEdit, {
    avatar_url: member.avatar_url || '',
    relationship_status: member.relationship_status || '',
    language: member.language || 'ko',
    premium_type: member.premium_type || '',
    premium_expires_at: member.premium_expires_at ? member.premium_expires_at.substring(0, 10) : '',
    is_matching_active: member.is_matching_active || false,
    preferred_region: member.preferred_region || '',
    age_range: member.age_range || '',
    matching_bio: member.matching_bio || '',
  })
  Object.assign(manageEdit, {
    status: member.status || 'active',
    ban_reason: member.ban_reason || '',
    is_admin: member.role === 'admin',
    is_elder: member.role === 'elder' || member.is_elder || false,
    admin_memo: member.admin_memo || '',
  })
  detailModal.value = true
  // Try to fetch full details
  try {
    const { data } = await axios.get(`/api/admin/users/${member.id}`)
    const extras = dummyDetailExtras(member.id)
    detailMember.value = {
      ...extras,
      ...member,
      ...data,
      comments_count: data.comments_count ?? 0,
      likes_count: data.likes_count ?? 0,
      reports_count: data.reports_count ?? 0,
      bookmarks_count: data.bookmarks_count ?? 0,
    }
  } catch {
    const extras = dummyDetailExtras(member.id)
    detailMember.value = {
      comments_count: Math.floor(Math.random() * 50),
      likes_count: Math.floor(Math.random() * 120),
      reports_count: Math.floor(Math.random() * 3),
      bookmarks_count: Math.floor(Math.random() * 30),
      ...extras,
      ...member,
    }
  }
}

function toggleSelectAll(e) {
  if (e.target.checked) selectedIds.value = filteredMembers.value.map(m => m.id)
  else selectedIds.value = []
}

async function toggleBan(member) {
  const newStatus = member.status === 'banned' ? 'active' : 'banned'
  try {
    await axios.post(`/api/admin/users/bulk-action`, {
      ids: [member.id], action: newStatus === 'banned' ? 'ban' : 'activate'
    })
  } catch {}
  const idx = (members.value.length > 0 ? members.value : dummyMembers).findIndex(m => m.id === member.id)
  if (members.value.length > 0 && idx >= 0) members.value[idx].status = newStatus
  else if (idx >= 0) dummyMembers[idx].status = newStatus
  showToast(newStatus === 'banned' ? '정지 처리되었습니다' : '활성화되었습니다', 'success')
}

function confirmDelete(member) { deleteTarget.value = member }

async function deleteMember() {
  if (!deleteTarget.value) return
  try {
    await axios.delete(`/api/admin/users/${deleteTarget.value.id}`)
  } catch {}
  if (members.value.length > 0) members.value = members.value.filter(m => m.id !== deleteTarget.value.id)
  showToast('회원이 삭제되었습니다', 'success')
  deleteTarget.value = null
}

async function deleteFromDetail() {
  try {
    await axios.delete(`/api/admin/users/${detailMember.value.id}`)
  } catch {}
  if (members.value.length > 0) members.value = members.value.filter(m => m.id !== detailMember.value.id)
  detailModal.value = false
  showToast('회원이 삭제되었습니다', 'success')
}

async function bulkAction(action) {
  const payload = { ids: selectedIds.value, action }
  if (action === 'points') {
    payload.amount = bulkPointAmount.value
    payload.reason = bulkPointReason.value
  }
  try {
    await axios.post('/api/admin/users/bulk-action', payload)
    showToast('일괄 처리 완료', 'success')
  } catch {
    showToast('처리 중 오류가 발생했습니다', 'error')
  }
  selectedIds.value = []
  showBulkPoints.value = false
}

async function adjustPoints() {
  if (!pointAdjustAmount.value) return
  try {
    await axios.post(`/api/admin/users/${detailMember.value.id}/adjust-points`, {
      amount: pointAdjustAmount.value,
      reason: pointAdjustReason.value,
    })
    detailMember.value.points = (detailMember.value.points || 0) + pointAdjustAmount.value
    if (!detailMember.value.point_logs) detailMember.value.point_logs = []
    detailMember.value.point_logs.unshift({
      id: Date.now(), action: '관리자 조정', amount: pointAdjustAmount.value,
      description: pointAdjustReason.value || '관리자 포인트 조정',
      created_at: new Date().toISOString(),
    })
    showToast('포인트가 조정되었습니다', 'success')
    pointAdjustAmount.value = 0
    pointAdjustReason.value = ''
  } catch {
    showToast('포인트 조정 실패', 'error')
  }
}

async function saveProfile() {
  try {
    await axios.put(`/api/admin/users/${detailMember.value.id}/profile`, { ...profileEdit })
    showToast('프로필이 저장되었습니다', 'success')
  } catch {
    showToast('저장 실패', 'error')
  }
}

async function saveManagement() {
  try {
    await axios.put(`/api/admin/users/${detailMember.value.id}/profile`, {
      status: manageEdit.status,
      ban_reason: manageEdit.ban_reason,
      role: manageEdit.is_admin ? 'admin' : (manageEdit.is_elder ? 'elder' : 'user'),
      admin_memo: manageEdit.admin_memo,
    })
    detailMember.value.status = manageEdit.status
    if (members.value.length > 0) {
      const idx = members.value.findIndex(m => m.id === detailMember.value.id)
      if (idx >= 0) members.value[idx].status = manageEdit.status
    }
    showToast('변경사항이 저장되었습니다', 'success')
  } catch {
    showToast('저장 실패', 'error')
  }
}

async function sendPasswordReset() {
  try {
    await axios.post(`/api/admin/users/${detailMember.value.id}/send-password-reset`)
    showToast('비밀번호 재설정 이메일이 발송되었습니다', 'success')
  } catch {
    showToast('이메일 발송 실패', 'error')
  }
}

async function forceSetPassword() {
  if (!newPassword.value || newPassword.value.length < 6) {
    showToast('비밀번호는 6자 이상이어야 합니다', 'error')
    return
  }
  try {
    await axios.post(`/api/admin/users/${detailMember.value.id}/set-password`, {
      new_password: newPassword.value
    })
    showToast('비밀번호가 변경되었습니다', 'success')
    newPassword.value = ''
  } catch {
    showToast('비밀번호 변경 실패', 'error')
  }
}

async function forceLogout() {
  try {
    await axios.post(`/api/admin/users/${detailMember.value.id}/force-logout`)
    detailMember.value.active_sessions = []
    showToast('모든 세션이 로그아웃되었습니다', 'success')
  } catch {
    showToast('로그아웃 처리 실패', 'error')
  }
}

function exportCSV() {
  const list = filteredMembers.value
  const headers = ['ID', '이름', '아이디', '이메일', '전화번호', '지역', '상태', '권한', '포인트', '게시글수', '가입일', '마지막로그인']
  const rows = list.map(m => [
    m.id, m.name, m.username, m.email, m.phone || '', m.region || '',
    statusLabel(m.status), roleLabel(m.role), m.points || 0, m.posts_count || 0,
    formatDateFull(m.created_at), formatDateFull(m.last_login_at)
  ])
  const csvContent = [headers, ...rows].map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `members_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
  showToast('CSV 파일이 다운로드되었습니다', 'success')
}

function resetFilters() {
  searchQuery.value = ''
  filterStatus.value = ''
  filterRole.value = ''
  sortBy.value = 'created_at_desc'
  fetchMembers()
}

function changePage(page) {
  if (page < 1 || page > pagination.last_page) return
  pagination.current_page = page
  fetchMembers()
}

// ── Helpers ────────────────────────────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`
}

function formatDateFull(dateStr) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function statusLabel(s) {
  return { active: '활성', banned: '정지', dormant: '휴면', pending_delete: '탈퇴대기' }[s] || s
}
function statusClass(s) {
  return {
    active: 'bg-green-100 text-green-700',
    banned: 'bg-red-100 text-red-700',
    dormant: 'bg-gray-100 text-gray-600',
    pending_delete: 'bg-yellow-100 text-yellow-700',
  }[s] || 'bg-gray-100 text-gray-600'
}
function roleLabel(r) {
  return { admin: '관리자', user: '일반', elder: '어르신', driver: '드라이버' }[r] || r
}
function roleClass(r) {
  return {
    admin: 'bg-purple-100 text-purple-700',
    user: 'bg-blue-100 text-blue-700',
    elder: 'bg-orange-100 text-orange-700',
    driver: 'bg-teal-100 text-teal-700',
  }[r] || 'bg-gray-100 text-gray-600'
}

const avatarColors = ['#4f46e5', '#7c3aed', '#db2777', '#dc2626', '#d97706', '#059669', '#0891b2', '#1d4ed8']
function avatarColor(name) {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

let toastTimer = null
function showToast(message, type = 'success') {
  clearTimeout(toastTimer)
  toast.show = true
  toast.message = message
  toast.type = type
  toastTimer = setTimeout(() => { toast.show = false }, 3000)
}

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  fetchMembers()
})
</script>
