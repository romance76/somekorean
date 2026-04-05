<template>
  <div class="space-y-5">

    <!-- 탭 네비게이션 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="flex border-b border-gray-100">
        <button v-for="tab in mainTabs" :key="tab.key"
          @click="activeMainTab = tab.key"
          :class="['px-5 py-3 text-sm font-medium transition border-b-2 -mb-px',
            activeMainTab === tab.key
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700']">
          {{ tab.label }}
          <span v-if="tab.key === 'reports' && pendingReports > 0" class="ml-1 bg-red-100 text-red-600 text-xs px-1.5 py-0.5 rounded-full">
            {{ pendingReports }}
          </span>
        </button>
      </div>
    </div>

    <!-- TAB 1: 채팅방 목록 -->
    <template v-if="activeMainTab === 'rooms'">
      <!-- 통계 카드 -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div class="text-xs text-gray-400 mb-1">전체 채팅방</div>
          <div class="text-2xl font-bold text-gray-800">
            <span v-if="loadingStats" class="text-gray-300">...</span>
            <span v-else>{{ stats.totalRooms }}</span>
          </div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div class="text-xs text-gray-400 mb-1">활성 채팅방</div>
          <div class="text-2xl font-bold text-green-600">
            <span v-if="loadingStats" class="text-gray-300">...</span>
            <span v-else>{{ stats.activeRooms }}</span>
          </div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div class="text-xs text-gray-400 mb-1">총 메시지</div>
          <div class="text-2xl font-bold text-blue-600">
            <span v-if="loadingStats" class="text-gray-300">...</span>
            <span v-else>{{ stats.totalMessages.toLocaleString() }}</span>
          </div>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <div class="text-xs text-gray-400 mb-1">오늘 메시지</div>
          <div class="text-2xl font-bold text-purple-600">
            <span v-if="loadingStats" class="text-gray-300">...</span>
            <span v-else>{{ stats.todayMessages }}</span>
          </div>
        </div>
      </div>

      <!-- 메인 레이아웃 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <!-- 왼쪽: 채팅방 목록 -->
        <div class="lg:col-span-1 space-y-3">
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-3 space-y-2">
            <div class="flex gap-2">
              <input v-model="search" type="text" placeholder="채팅방 검색..."
                class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
              <button @click="applyFilter"
                class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-2 rounded-lg text-sm transition">검색</button>
            </div>
            <div class="flex gap-2">
              <select v-model="filterType" @change="applyFilter"
                class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
                <option value="">전체</option>
                <option value="public">공개</option>
                <option value="private">비공개</option>
                <option value="announcement">공지</option>
                <option value="regional">지역</option>
                <option value="theme">주제별</option>
              </select>
              <button @click="showCreateModal = true"
                class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap">
                + 새 채팅방
              </button>
            </div>
          </div>

          <!-- 로딩 / 에러 / 목록 -->
          <div v-if="loadingRooms" class="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center">
            <div class="flex justify-center mb-2">
              <svg class="animate-spin h-6 w-6 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
            </div>
            <div class="text-sm text-gray-400">채팅방 목록 불러오는 중...</div>
          </div>
          <div v-else-if="roomsError" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 text-center">
            <div class="text-sm text-red-500 mb-3">불러오기 실패</div>
            <button @click="loadRooms" class="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition">
              다시 시도
            </button>
          </div>
          <div v-else class="space-y-2 max-h-[600px] overflow-y-auto">
            <div v-for="room in filteredRooms" :key="room.id"
              @click="selectRoom(room)"
              :class="['bg-white rounded-xl shadow-sm border cursor-pointer p-3 transition hover:shadow-md',
                selectedRoom?.id === room.id ? 'border-blue-400 ring-1 ring-blue-200' : 'border-gray-100']">
              <div class="flex items-center justify-between mb-1">
                <div class="flex items-center gap-2 min-w-0">
                  <span v-if="room.icon" class="text-lg flex-shrink-0">{{ room.icon }}</span>
                  <div class="font-semibold text-sm text-gray-800 truncate">{{ room.name }}</div>
                </div>
                <span :class="['text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 ml-1', roomTypeBadge(room.type).class]">
                  {{ roomTypeBadge(room.type).label }}
                </span>
              </div>
              <div class="text-xs text-gray-400 flex gap-3 mb-1">
                <span :class="room.is_open ? 'text-green-500' : 'text-red-400'">
                  {{ room.is_open ? '활성' : '비활성' }}
                </span>
              </div>
              <div class="text-xs text-gray-500 truncate">{{ room.last_message_preview || room.description }}</div>
            </div>
            <div v-if="filteredRooms.length === 0" class="text-center text-gray-400 text-sm py-8">
              채팅방이 없습니다
            </div>
          </div>
        </div>

        <!-- 오른쪽: 채팅방 상세 -->
        <div class="lg:col-span-2">
          <div v-if="!selectedRoom" class="bg-white rounded-xl shadow-sm border border-gray-100 p-8 text-center text-gray-400">
            <div class="text-4xl mb-3">💬</div>
            <div class="text-sm">채팅방을 선택하면 메시지가 표시됩니다</div>
          </div>

          <div v-else class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <!-- 채팅방 헤더 -->
            <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h3 class="font-bold text-gray-800 flex items-center gap-2">
                  <span v-if="selectedRoom.icon">{{ selectedRoom.icon }}</span>
                  {{ selectedRoom.name }}
                </h3>
                <p class="text-xs text-gray-400">{{ selectedRoom.description }}</p>
              </div>
              <div class="flex gap-2 flex-shrink-0">
                <span :class="['text-xs px-2 py-1 rounded-full font-medium', roomTypeBadge(selectedRoom.type).class]">
                  {{ roomTypeBadge(selectedRoom.type).label }}
                </span>
                <button @click="toggleRoomStatus(selectedRoom)"
                  :class="['text-xs px-3 py-1 rounded-lg font-medium transition',
                    selectedRoom.is_open
                      ? 'bg-red-100 text-red-600 hover:bg-red-200'
                      : 'bg-green-100 text-green-600 hover:bg-green-200']">
                  {{ selectedRoom.is_open ? '비활성화' : '활성화' }}
                </button>
                <button @click="deleteRoom(selectedRoom)"
                  class="text-xs px-3 py-1 rounded-lg font-medium bg-gray-100 text-gray-600 hover:bg-red-100 hover:text-red-600 transition">
                  삭제
                </button>
              </div>
            </div>

            <!-- 메시지 패널 -->
            <div class="flex flex-col" style="height:480px;">
              <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 bg-gray-50 space-y-3">
                <!-- 로딩 -->
                <div v-if="loadingMessages" class="flex flex-col items-center justify-center h-full text-gray-400">
                  <svg class="animate-spin h-6 w-6 text-blue-400 mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                  <span class="text-sm">메시지를 불러오는 중...</span>
                </div>

                <!-- 에러 -->
                <div v-else-if="messagesError" class="flex flex-col items-center justify-center h-full text-gray-400">
                  <div class="text-sm text-red-400 mb-3">메시지 불러오기 실패</div>
                  <button @click="loadMessages(selectedRoom)" class="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition">
                    다시 시도
                  </button>
                </div>

                <!-- 빈 상태 -->
                <div v-else-if="roomMessages.length === 0" class="flex items-center justify-center h-full text-gray-400 text-sm">
                  메시지가 없습니다
                </div>

                <!-- 메시지 버블 -->
                <template v-else>
                  <div v-for="msg in roomMessages" :key="msg.id"
                    class="flex items-end gap-2 flex-row group">
                    <!-- 아바타 -->
                    <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                      :style="{ backgroundColor: getUserColor(msg.user_id) }">
                      {{ (msg.user?.name || msg.user?.username || '?').charAt(0) }}
                    </div>
                    <div class="max-w-[65%]">
                      <!-- 이름 + 시간 -->
                      <div class="text-xs text-gray-400 mb-1 px-1 text-left">
                        <span class="font-medium text-gray-600">{{ msg.user?.name || msg.user?.username || '알 수 없음' }}</span>
                        <span class="ml-1">{{ formatTime(msg.created_at) }}</span>
                      </div>
                      <!-- 말풍선 -->
                      <div class="relative">
                        <div :class="['px-3 py-2 rounded-2xl text-sm break-words shadow-sm bg-white text-gray-800 rounded-bl-sm border border-gray-100',
                          msg.is_pinned ? 'ring-2 ring-yellow-300' : '']">
                          <span v-if="msg.is_pinned" class="text-yellow-400 mr-1">📌</span>
                          {{ msg.message || msg.content || '' }}
                        </div>
                        <!-- 액션 버튼 (hover) -->
                        <div class="absolute top-0 left-full ml-2 opacity-0 group-hover:opacity-100 transition flex gap-1">
                          <button @click="deleteMessage(msg)"
                            class="text-xs px-2 py-1 rounded bg-red-100 text-red-600 hover:bg-red-200 whitespace-nowrap transition">
                            삭제
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- TAB 2: 신고 관리 -->
    <template v-if="activeMainTab === 'reports'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 class="font-bold text-gray-800">신고 목록</h3>
          <div class="flex gap-2">
            <select v-model="reportFilter" @change="loadReports"
              class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400">
              <option value="">전체</option>
              <option value="pending">처리 대기</option>
              <option value="resolved">처리 완료</option>
            </select>
            <button v-if="selectedReports.length > 0"
              @click="bulkResolve"
              class="bg-gray-800 text-white px-3 py-1.5 rounded-lg text-sm font-medium transition hover:bg-gray-700">
              선택 일괄처리 ({{ selectedReports.length }})
            </button>
          </div>
        </div>

        <!-- 신고 로딩 -->
        <div v-if="loadingReports" class="px-5 py-8 text-center">
          <svg class="animate-spin h-6 w-6 text-blue-400 mx-auto mb-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
          </svg>
          <div class="text-sm text-gray-400">신고 목록 불러오는 중...</div>
        </div>
        <div v-else-if="reportsError" class="px-5 py-8 text-center">
          <div class="text-sm text-red-400 mb-3">불러오기 실패</div>
          <button @click="loadReports" class="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition">
            다시 시도
          </button>
        </div>
        <div v-else class="divide-y divide-gray-50">
          <div v-for="report in reports" :key="report.id">
            <!-- 신고 요약 행 -->
            <div @click="toggleReport(report.id)"
              class="px-5 py-3 hover:bg-gray-50 cursor-pointer flex items-center gap-3 transition">
              <input type="checkbox" :value="report.id" v-model="selectedReports"
                @click.stop class="rounded" />
              <div class="flex-1 grid grid-cols-5 gap-3 text-sm">
                <div>
                  <div class="text-xs text-gray-400 mb-0.5">신고자</div>
                  <div class="font-medium text-gray-700">{{ report.reporter }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-0.5">신고대상</div>
                  <div class="font-semibold text-red-600">{{ report.reported_user }}</div>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-0.5">사유</div>
                  <span class="bg-orange-100 text-orange-700 text-xs px-2 py-0.5 rounded-full">{{ report.reason }}</span>
                </div>
                <div>
                  <div class="text-xs text-gray-400 mb-0.5">채팅방</div>
                  <div class="text-gray-600 text-xs">{{ report.room_name }}</div>
                </div>
                <div class="text-right">
                  <span :class="['text-xs px-2 py-1 rounded-full font-medium',
                    report.status === 'pending' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700']">
                    {{ report.status === 'pending' ? '처리 대기' : '처리 완료' }}
                  </span>
                  <div class="text-xs text-gray-400 mt-0.5">{{ formatDate(report.created_at) }}</div>
                </div>
              </div>
              <div class="text-gray-400 text-sm">{{ expandedReports.includes(report.id) ? '▲' : '▼' }}</div>
            </div>

            <!-- 신고 상세 (펼치기) -->
            <div v-if="expandedReports.includes(report.id)"
              class="px-5 pb-5 bg-red-50 border-t border-red-100">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-4">
                <!-- 신고된 회원 정보 -->
                <div class="bg-white rounded-xl border border-red-100 p-4">
                  <h4 class="font-semibold text-gray-800 mb-3 text-sm">신고된 회원 정보</h4>
                  <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                      <span class="text-gray-400">이름</span>
                      <span class="font-medium text-gray-800">{{ report.reported_user }}</span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">이전 신고 건수</span>
                      <span class="font-medium" :class="(report.prior_reports || 0) > 2 ? 'text-red-600' : 'text-gray-800'">
                        {{ report.prior_reports || 0 }}건
                      </span>
                    </div>
                    <div class="flex justify-between">
                      <span class="text-gray-400">계정 상태</span>
                      <span class="text-green-600 font-medium">활성</span>
                    </div>
                  </div>
                </div>

                <!-- 신고된 메시지 + 컨텍스트 -->
                <div class="bg-white rounded-xl border border-red-100 p-4">
                  <h4 class="font-semibold text-gray-800 mb-3 text-sm">메시지 컨텍스트</h4>
                  <div class="space-y-2">
                    <div v-if="report.context_before" class="text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2">
                      이전: {{ report.context_before }}
                    </div>
                    <div class="bg-red-100 border border-red-200 rounded-lg px-3 py-2">
                      <div class="text-xs text-red-500 mb-1 font-medium">신고된 메시지</div>
                      <div class="text-sm text-red-800 font-medium">{{ report.message_content }}</div>
                    </div>
                    <div v-if="report.context_after" class="text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2">
                      이후: {{ report.context_after }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- 처리 버튼 -->
              <div v-if="report.status === 'pending'" class="mt-4 flex flex-wrap gap-2">
                <button @click="resolveReport(report, '메시지 삭제')"
                  class="bg-orange-100 hover:bg-orange-200 text-orange-700 px-4 py-2 rounded-lg text-sm font-medium transition">
                  메시지 삭제
                </button>
                <button @click="resolveReport(report, '채팅 강퇴')"
                  class="bg-red-100 hover:bg-red-200 text-red-600 px-4 py-2 rounded-lg text-sm font-medium transition">
                  채팅 강퇴
                </button>
                <button @click="resolveReport(report, '계정 정지 1일')"
                  class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                  계정 정지 1일
                </button>
                <button @click="resolveReport(report, '계정 정지 7일')"
                  class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                  계정 정지 7일
                </button>
                <button @click="resolveReport(report, '영구 정지')"
                  class="bg-gray-900 hover:bg-black text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                  영구 정지
                </button>
                <button @click="resolveReport(report, '무혐의')"
                  class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-medium transition ml-auto">
                  무혐의
                </button>
              </div>
              <div v-else class="mt-4 flex items-center gap-2">
                <span class="bg-green-100 text-green-700 text-sm px-3 py-1.5 rounded-lg font-medium">
                  처리 완료: {{ report.resolved_action }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="reports.length === 0 && !loadingReports && !reportsError" class="px-5 py-8 text-center text-gray-400 text-sm">
            신고 내역이 없습니다
          </div>
        </div>
      </div>
    </template>

    <!-- TAB 3: 채팅방 생성/설정 -->
    <template v-if="activeMainTab === 'create'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="font-bold text-gray-800 text-lg mb-5">새 채팅방 생성</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">방 이름 <span class="text-red-500">*</span></label>
            <input v-model="newRoom.name" type="text" placeholder="예: LA 한인 맛집 정보"
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">채팅방 유형 <span class="text-red-500">*</span></label>
            <select v-model="newRoom.type"
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400">
              <option value="public">공개 (누구나 참여 가능)</option>
              <option value="regional">지역기반 (지역 인증 필요)</option>
              <option value="theme">주제별 (카테고리 선택)</option>
              <option value="announcement">공지 (읽기 전용)</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">방 설명</label>
            <textarea v-model="newRoom.description" rows="3" placeholder="채팅방 소개글을 입력하세요"
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400"></textarea>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">아이콘 (이모지)</label>
            <input v-model="newRoom.icon" type="text" placeholder="💬"
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">슬러그 (URL용)</label>
            <input v-model="newRoom.slug" type="text" placeholder="la-korean-food"
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>
        </div>

        <!-- 고급 설정 -->
        <div class="mt-6 border-t border-gray-100 pt-5">
          <h4 class="font-semibold text-gray-700 mb-4 text-sm">고급 설정</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-700 mb-1.5 block">공개 여부</label>
              <select v-model="newRoom.is_open"
                class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400">
                <option :value="true">활성 (공개)</option>
                <option :value="false">비활성</option>
              </select>
            </div>
            <div class="space-y-3 pt-1">
              <label class="flex items-center gap-3 cursor-pointer">
                <div class="relative">
                  <input type="checkbox" v-model="newRoom.profanity_filter" class="sr-only" />
                  <div :class="['w-10 h-5 rounded-full transition', newRoom.profanity_filter ? 'bg-blue-500' : 'bg-gray-300']"></div>
                  <div :class="['absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform',
                    newRoom.profanity_filter ? 'translate-x-5' : 'translate-x-0.5']"></div>
                </div>
                <span class="text-sm text-gray-700">욕설 필터 ON</span>
              </label>
            </div>
          </div>
        </div>

        <div class="mt-6 flex gap-3">
          <button @click="createRoom" :disabled="creatingRoom"
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
            <svg v-if="creatingRoom" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
            {{ creatingRoom ? '생성 중...' : '채팅방 생성' }}
          </button>
          <button @click="resetNewRoom"
            class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-6 py-2.5 rounded-lg text-sm font-semibold transition">
            초기화
          </button>
        </div>
      </div>
    </template>

    <!-- 채팅방 생성 모달 -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 mx-4">
        <div class="flex justify-between items-center mb-5">
          <h3 class="font-bold text-gray-800 text-lg">새 채팅방</h3>
          <button @click="showCreateModal = false" class="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
        </div>
        <div class="space-y-4">
          <div>
            <label class="text-xs text-gray-500 mb-1 block">방 이름</label>
            <input v-model="newRoom.name" type="text" placeholder="채팅방 이름"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          </div>
          <div>
            <label class="text-xs text-gray-500 mb-1 block">설명</label>
            <textarea v-model="newRoom.description" rows="2"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-xs text-gray-500 mb-1 block">유형</label>
              <select v-model="newRoom.type"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
                <option value="public">공개</option>
                <option value="regional">지역</option>
                <option value="theme">주제별</option>
                <option value="announcement">공지</option>
              </select>
            </div>
            <div>
              <label class="text-xs text-gray-500 mb-1 block">아이콘</label>
              <input v-model="newRoom.icon" type="text" placeholder="💬"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
            </div>
          </div>
          <div>
            <label class="text-xs text-gray-500 mb-1 block">슬러그</label>
            <input v-model="newRoom.slug" type="text" placeholder="my-room"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          </div>
        </div>
        <div class="flex gap-3 mt-5">
          <button @click="createRoom" :disabled="creatingRoom"
            class="flex-1 bg-blue-500 hover:bg-blue-600 text-white py-2.5 rounded-lg text-sm font-semibold transition disabled:opacity-50">
            {{ creatingRoom ? '생성 중...' : '생성' }}
          </button>
          <button @click="showCreateModal = false"
            class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 py-2.5 rounded-lg text-sm font-semibold transition">취소</button>
        </div>
      </div>
    </div>

    <!-- 토스트 알림 -->
    <div v-if="toast.show" :class="['fixed bottom-5 right-5 z-50 px-5 py-3 rounded-xl shadow-lg text-white text-sm font-medium transition-all',
      toast.type === 'success' ? 'bg-green-500' : 'bg-red-500']">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import axios from 'axios'

// ─── 탭 ───────────────────────────────────────────
const mainTabs = [
  { key: 'rooms', label: '채팅방 목록' },
  { key: 'reports', label: '신고 관리' },
  { key: 'create', label: '채팅방 생성/설정' },
]
const activeMainTab = ref('rooms')

// ─── 채팅방 목록 상태 ─────────────────────────────
const rooms = ref([])
const loadingRooms = ref(false)
const roomsError = ref(false)
const search = ref('')
const filterType = ref('')
const selectedRoom = ref(null)

// ─── 메시지 상태 ──────────────────────────────────
const loadingMessages = ref(false)
const messagesError = ref(false)
const roomMessages = ref([])
const chatContainer = ref(null)

// ─── 통계 상태 ────────────────────────────────────
const loadingStats = ref(false)
const stats = ref({ totalRooms: 0, activeRooms: 0, totalMessages: 0, todayMessages: 0 })

// ─── 신고 상태 ────────────────────────────────────
const reports = ref([])
const loadingReports = ref(false)
const reportsError = ref(false)
const reportFilter = ref('')
const expandedReports = ref([])
const selectedReports = ref([])

// ─── 채팅방 생성 상태 ─────────────────────────────
const showCreateModal = ref(false)
const creatingRoom = ref(false)
const newRoom = ref({
  name: '', description: '', type: 'public', icon: '', slug: '',
  is_open: true, profanity_filter: true,
})

// ─── 기타 ─────────────────────────────────────────
const toast = ref({ show: false, message: '', type: 'success' })

// ─── Computed ─────────────────────────────────────
const filteredRooms = computed(() => {
  let list = rooms.value
  if (search.value) list = list.filter(r => r.name.includes(search.value) || (r.description || '').includes(search.value))
  if (filterType.value) list = list.filter(r => r.type === filterType.value)
  return list
})

const pendingReports = computed(() => reports.value.filter(r => r.status === 'pending').length)

// ─── API: 채팅방 목록 로드 ────────────────────────
async function loadRooms() {
  loadingRooms.value = true
  roomsError.value = false
  try {
    const { data } = await axios.get('/api/chat/rooms')
    rooms.value = data
    // 통계를 실시간 데이터로 업데이트 (stats API 병행)
    stats.value.totalRooms = data.length
    stats.value.activeRooms = data.filter(r => r.is_open).length
  } catch (e) {
    console.error('채팅방 목록 로드 실패:', e)
    roomsError.value = true
  } finally {
    loadingRooms.value = false
  }
}

// ─── API: 통계 로드 ───────────────────────────────
async function loadStats() {
  loadingStats.value = true
  try {
    const { data } = await axios.get('/api/admin/chat/stats')
    stats.value = {
      totalRooms: data.total_rooms ?? data.totalRooms ?? 0,
      activeRooms: data.active_rooms ?? data.activeRooms ?? 0,
      totalMessages: data.total_messages ?? data.totalMessages ?? 0,
      todayMessages: data.today_messages ?? data.todayMessages ?? 0,
    }
  } catch (e) {
    // 통계 API 실패 시 rooms에서 계산된 값 유지 (조용히 실패)
    console.warn('통계 로드 실패, rooms 데이터에서 계산:', e)
  } finally {
    loadingStats.value = false
  }
}

// ─── API: 메시지 로드 ─────────────────────────────
async function loadMessages(room) {
  selectedRoom.value = room
  loadingMessages.value = true
  messagesError.value = false
  roomMessages.value = []
  try {
    const { data } = await axios.get(`/api/admin/chat/rooms/${room.id}/messages`)
    roomMessages.value = data.messages || data
  } catch (e) {
    console.error('메시지 로드 실패:', e)
    messagesError.value = true
  } finally {
    loadingMessages.value = false
    await nextTick()
    if (chatContainer.value) chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// ─── API: 신고 목록 로드 ──────────────────────────
async function loadReports() {
  loadingReports.value = true
  reportsError.value = false
  try {
    const params = { type: 'chat' }
    if (reportFilter.value) params.status = reportFilter.value
    const { data } = await axios.get('/api/admin/reports', { params })
    reports.value = data.data || data
  } catch (e) {
    console.error('신고 목록 로드 실패:', e)
    reportsError.value = true
  } finally {
    loadingReports.value = false
  }
}

// ─── selectRoom: 클릭 시 메시지 패널 열기 ─────────
function selectRoom(room) {
  loadMessages(room)
}

function applyFilter() {
  // filteredRooms computed가 자동 반응
}

// ─── 채팅방 상태 토글 (활성/비활성) ──────────────
async function toggleRoomStatus(room) {
  const action = room.is_open ? '비활성화' : '활성화'
  if (!confirm(`"${room.name}" 채팅방을 ${action}하시겠습니까?`)) return
  try {
    await axios.patch(`/api/admin/chat/rooms/${room.id}`, { is_open: !room.is_open })
    room.is_open = !room.is_open
    stats.value.activeRooms = rooms.value.filter(r => r.is_open).length
    showToast(`채팅방을 ${action}했습니다`, 'success')
  } catch (e) {
    showToast(`${action} 실패`, 'error')
  }
}

// ─── 채팅방 삭제 ──────────────────────────────────
async function deleteRoom(room) {
  if (!confirm(`"${room.name}" 채팅방을 삭제하시겠습니까? 모든 메시지가 삭제됩니다.`)) return
  try {
    await axios.delete(`/api/admin/chat/rooms/${room.id}`)
    rooms.value = rooms.value.filter(r => r.id !== room.id)
    if (selectedRoom.value?.id === room.id) selectedRoom.value = null
    stats.value.totalRooms = rooms.value.length
    stats.value.activeRooms = rooms.value.filter(r => r.is_open).length
    showToast('채팅방이 삭제되었습니다', 'success')
  } catch (e) {
    showToast('삭제 실패', 'error')
  }
}

// ─── 메시지 삭제 ──────────────────────────────────
async function deleteMessage(msg) {
  if (!confirm(`"${msg.content.slice(0, 20)}..." 메시지를 삭제하시겠습니까?`)) return
  try {
    await axios.delete(`/api/admin/chat/messages/${msg.id}`)
    roomMessages.value = roomMessages.value.filter(m => m.id !== msg.id)
    showToast('메시지가 삭제되었습니다', 'success')
  } catch (e) {
    showToast('삭제 실패', 'error')
  }
}

// ─── 신고 처리 ────────────────────────────────────
async function resolveReport(report, action) {
  try {
    await axios.patch(`/api/admin/reports/${report.id}`, { action, status: 'resolved' })
    report.status = 'resolved'
    report.resolved_action = action
    showToast(`처리 완료: ${action}`, 'success')
  } catch (e) {
    showToast('처리 실패', 'error')
  }
}

async function bulkResolve() {
  const ids = selectedReports.value
  if (ids.length === 0) return
  try {
    await axios.post('/api/admin/reports/bulk-resolve', { ids, action: '일괄 처리' })
    ids.forEach(id => {
      const r = reports.value.find(rp => rp.id === id)
      if (r && r.status === 'pending') { r.status = 'resolved'; r.resolved_action = '일괄 처리' }
    })
    showToast(`${ids.length}건 일괄 처리 완료`, 'success')
    selectedReports.value = []
  } catch (e) {
    showToast('일괄 처리 실패', 'error')
  }
}

// ─── 채팅방 생성 ──────────────────────────────────
async function createRoom() {
  if (!newRoom.value.name.trim()) { showToast('방 이름을 입력하세요', 'error'); return }
  creatingRoom.value = true
  try {
    const { data } = await axios.post('/api/admin/chat/rooms', newRoom.value)
    rooms.value.unshift(data)
    stats.value.totalRooms = rooms.value.length
    if (data.is_open) stats.value.activeRooms++
    showCreateModal.value = false
    resetNewRoom()
    showToast('채팅방이 생성되었습니다', 'success')
  } catch (e) {
    const msg = e.response?.data?.message || '생성 실패'
    showToast(msg, 'error')
  } finally {
    creatingRoom.value = false
  }
}

function resetNewRoom() {
  newRoom.value = { name: '', description: '', type: 'public', icon: '', slug: '', is_open: true, profanity_filter: true }
}

// ─── 신고 토글 ────────────────────────────────────
function toggleReport(id) {
  const idx = expandedReports.value.indexOf(id)
  if (idx === -1) expandedReports.value.push(id)
  else expandedReports.value.splice(idx, 1)
}

// ─── 유틸 ─────────────────────────────────────────
function roomTypeBadge(type) {
  const map = {
    public: { label: '공개', class: 'bg-blue-100 text-blue-700' },
    private: { label: '비공개', class: 'bg-gray-100 text-gray-600' },
    announcement: { label: '공지', class: 'bg-yellow-100 text-yellow-700' },
    regional: { label: '지역', class: 'bg-green-100 text-green-700' },
    theme: { label: '주제별', class: 'bg-purple-100 text-purple-700' },
  }
  return map[type] || { label: type, class: 'bg-gray-100 text-gray-600' }
}

function getUserColor(id) {
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#EC4899', '#84CC16']
  return colors[(id || 0) % colors.length]
}

function formatTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}

function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 2500)
}

// ─── 탭 전환 시 데이터 로드 ──────────────────────
watch(activeMainTab, (tab) => {
  if (tab === 'reports') loadReports()
})

// ─── 초기 로드 ────────────────────────────────────
onMounted(() => {
  loadRooms()
  loadStats()
})
</script>
