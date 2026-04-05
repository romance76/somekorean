<template>
  <div class="space-y-5">
    <!-- 헤더 -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900">매칭 관리</h1>
      <p class="text-sm text-gray-500 mt-1">한인 커뮤니티 매칭 서비스를 관리합니다</p>
    </div>

    <!-- 탭 네비게이션 -->
    <div class="border-b border-gray-200">
      <nav class="flex space-x-0 -mb-px">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 bg-blue-50'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'flex items-center gap-2 px-5 py-3 border-b-2 font-medium text-sm transition-colors duration-150'
          ]"
        >
          <span>{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
          <span v-if="tab.id === 'verification' && pendingVerifications.length > 0"
            class="bg-yellow-100 text-yellow-700 text-xs font-bold px-1.5 py-0.5 rounded-full">
            {{ pendingVerifications.length }}
          </span>
        </button>
      </nav>
    </div>

    <!-- ===================== TAB 1: 본인인증 ===================== -->
    <div v-if="activeTab === 'verification'">
      <!-- 통계 행 -->
      <div class="grid grid-cols-3 gap-4 mb-5">
        <div class="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-center gap-3">
          <div class="w-10 h-10 bg-yellow-200 rounded-full flex items-center justify-center text-yellow-700 font-bold text-lg">
            {{ verificationStats.pending }}
          </div>
          <div>
            <p class="text-xs text-yellow-600 font-medium">대기중</p>
            <p class="text-lg font-bold text-yellow-800">{{ verificationStats.pending }}건</p>
          </div>
        </div>
        <div class="bg-green-50 border border-green-200 rounded-xl p-4 flex items-center gap-3">
          <div class="w-10 h-10 bg-green-200 rounded-full flex items-center justify-center text-green-700 font-bold text-lg">
            {{ verificationStats.approved }}
          </div>
          <div>
            <p class="text-xs text-green-600 font-medium">승인됨</p>
            <p class="text-lg font-bold text-green-800">{{ verificationStats.approved }}건</p>
          </div>
        </div>
        <div class="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
          <div class="w-10 h-10 bg-red-200 rounded-full flex items-center justify-center text-red-700 font-bold text-lg">
            {{ verificationStats.rejected }}
          </div>
          <div>
            <p class="text-xs text-red-600 font-medium">거절됨</p>
            <p class="text-lg font-bold text-red-800">{{ verificationStats.rejected }}건</p>
          </div>
        </div>
      </div>

      <!-- 필터 버튼 -->
      <div class="flex gap-2 mb-5">
        <button
          v-for="f in verificationFilters"
          :key="f.value"
          @click="verificationFilter = f.value"
          :class="[
            verificationFilter === f.value
              ? 'bg-blue-600 text-white shadow-sm'
              : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50',
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-150'
          ]"
        >
          {{ f.label }}
        </button>
      </div>

      <!-- 인증 요청 카드 그리드 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div
          v-for="req in filteredVerifications"
          :key="req.id"
          class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow duration-150 cursor-pointer"
          @click="openVerificationModal(req)"
        >
          <!-- 유저 정보 헤더 -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                {{ req.name.charAt(0) }}
              </div>
              <div>
                <p class="font-semibold text-gray-900 text-sm">{{ req.name }}</p>
                <p class="text-xs text-gray-400">@{{ req.username }}</p>
                <p class="text-xs text-gray-400 mt-0.5">가입일: {{ req.joinDate }}</p>
              </div>
            </div>
            <!-- 상태 배지 -->
            <span :class="statusBadgeClass(req.status)" class="px-2.5 py-1 rounded-full text-xs font-semibold flex-shrink-0">
              {{ statusLabel(req.status) }}
            </span>
          </div>

          <!-- 사진 3개 -->
          <div class="flex gap-3 mb-4">
            <div class="flex-1 flex flex-col items-center gap-1">
              <div class="w-full h-20 bg-blue-100 rounded-lg flex items-center justify-center text-2xl relative group cursor-pointer">
                <span>🪪</span>
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 rounded-lg flex items-center justify-center transition-all duration-150">
                  <span class="text-white text-xs font-medium opacity-0 group-hover:opacity-100">사진 확인</span>
                </div>
              </div>
              <p class="text-xs text-gray-500 font-medium">신분증</p>
            </div>
            <div class="flex-1 flex flex-col items-center gap-1">
              <div class="w-full h-20 bg-green-100 rounded-lg flex items-center justify-center text-2xl relative group cursor-pointer">
                <span>🤳</span>
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 rounded-lg flex items-center justify-center transition-all duration-150">
                  <span class="text-white text-xs font-medium opacity-0 group-hover:opacity-100">사진 확인</span>
                </div>
              </div>
              <p class="text-xs text-gray-500 font-medium">본인 사진</p>
            </div>
            <div class="flex-1 flex flex-col items-center gap-1">
              <div class="w-full h-20 bg-yellow-100 rounded-lg flex items-center justify-center text-2xl relative group cursor-pointer">
                <span>✍️</span>
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 rounded-lg flex items-center justify-center transition-all duration-150">
                  <span class="text-white text-xs font-medium opacity-0 group-hover:opacity-100">사진 확인</span>
                </div>
              </div>
              <p class="text-xs text-gray-500 font-medium">아이디 메모</p>
            </div>
          </div>

          <!-- 액션 버튼 (대기중) or 처리 정보 (승인/거절) -->
          <div v-if="req.status === 'pending'" class="flex gap-2" @click.stop>
            <button
              @click="approveVerification(req.id)"
              class="flex-1 bg-green-500 hover:bg-green-600 text-white text-sm font-semibold py-2 rounded-lg transition-colors duration-150"
            >
              승인
            </button>
            <button
              @click="openRejectModal(req)"
              class="flex-1 bg-red-500 hover:bg-red-600 text-white text-sm font-semibold py-2 rounded-lg transition-colors duration-150"
            >
              거절
            </button>
          </div>
          <div v-else class="text-xs text-gray-400 border-t border-gray-100 pt-3">
            <span class="font-medium">처리자:</span> {{ req.processedBy }} &nbsp;·&nbsp;
            <span class="font-medium">처리일:</span> {{ req.processedAt }}
            <span v-if="req.status === 'rejected' && req.rejectReason" class="block mt-1 text-red-400">
              거절 사유: {{ req.rejectReason }}
            </span>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-if="filteredVerifications.length === 0" class="text-center py-16 text-gray-400">
        <p class="text-4xl mb-3">📭</p>
        <p class="text-sm">해당하는 인증 요청이 없습니다</p>
      </div>
    </div>

    <!-- ===================== TAB 2: 프로필 관리 ===================== -->
    <div v-if="activeTab === 'profiles'">
      <!-- 검색 / 필터 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-5">
        <div class="flex flex-wrap gap-3 items-center">
          <select v-model="profileFilter.gender" class="border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300">
            <option value="">성별 전체</option>
            <option value="남성">남성</option>
            <option value="여성">여성</option>
          </select>
          <select v-model="profileFilter.ageGroup" class="border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300">
            <option value="">나이 전체</option>
            <option value="20">20대</option>
            <option value="30">30대</option>
            <option value="40">40대+</option>
          </select>
          <select v-model="profileFilter.region" class="border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-300">
            <option value="">지역 전체</option>
            <option value="뉴욕">뉴욕</option>
            <option value="LA">LA</option>
            <option value="시카고">시카고</option>
            <option value="시애틀">시애틀</option>
          </select>
          <button @click="resetProfileFilter" class="text-sm text-gray-400 hover:text-gray-600 underline">초기화</button>
        </div>
      </div>

      <!-- 프로필 테이블 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">익명이름</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">나이</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">성별</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">지역</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">사진수</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">완성도</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">상태</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="profile in filteredProfiles" :key="profile.id" class="hover:bg-gray-50 transition-colors">
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-full bg-purple-400 flex items-center justify-center text-white font-bold text-xs flex-shrink-0">
                      {{ profile.nickname.charAt(0) }}
                    </div>
                    <span class="font-medium text-gray-800">{{ profile.nickname }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-gray-600">{{ profile.age }}세</td>
                <td class="px-4 py-3">
                  <span :class="profile.gender === '남성' ? 'text-blue-600 bg-blue-50' : 'text-pink-600 bg-pink-50'"
                    class="px-2 py-0.5 rounded text-xs font-medium">
                    {{ profile.gender }}
                  </span>
                </td>
                <td class="px-4 py-3 text-gray-600">{{ profile.region }}</td>
                <td class="px-4 py-3 text-gray-600">{{ profile.photoCount }}장</td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="flex-1 bg-gray-100 rounded-full h-1.5 w-16">
                      <div class="bg-blue-500 h-1.5 rounded-full" :style="{ width: profile.completion + '%' }"></div>
                    </div>
                    <span class="text-xs text-gray-500">{{ profile.completion }}%</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span :class="profile.active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                    class="px-2 py-0.5 rounded-full text-xs font-semibold">
                    {{ profile.active ? '활성' : '정지됨' }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex gap-2">
                    <button @click="toggleProfileStatus(profile.id)"
                      :class="profile.active ? 'text-orange-500 hover:text-orange-700' : 'text-green-500 hover:text-green-700'"
                      class="text-xs font-medium underline">
                      {{ profile.active ? '정지' : '활성화' }}
                    </button>
                    <button @click="deleteProfile(profile.id)" class="text-xs font-medium text-red-400 hover:text-red-600 underline">삭제</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="filteredProfiles.length === 0" class="text-center py-12 text-gray-400 text-sm">
          조건에 맞는 프로필이 없습니다
        </div>
      </div>
    </div>

    <!-- ===================== TAB 3: 매칭 현황 ===================== -->
    <div v-if="activeTab === 'matching'">
      <!-- 요약 통계 -->
      <div class="grid grid-cols-3 gap-4 mb-5">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">총 매칭 요청</p>
          <p class="text-2xl font-bold text-gray-800">{{ matchRequests.length }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">성사율</p>
          <p class="text-2xl font-bold text-green-600">{{ matchSuccessRate }}%</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">오늘 신규</p>
          <p class="text-2xl font-bold text-blue-600">{{ todayNewMatches }}</p>
        </div>
      </div>

      <!-- 매칭 테이블 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-800">매칭 요청 목록</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">요청자</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">수신자</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">상태</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">요청일</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="match in matchRequests" :key="match.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-full bg-blue-400 flex items-center justify-center text-white text-xs font-bold">
                      {{ match.requester.charAt(0) }}
                    </div>
                    <span class="font-medium text-gray-800">{{ match.requester }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center gap-2">
                    <div class="w-7 h-7 rounded-full bg-pink-400 flex items-center justify-center text-white text-xs font-bold">
                      {{ match.receiver.charAt(0) }}
                    </div>
                    <span class="font-medium text-gray-800">{{ match.receiver }}</span>
                  </div>
                </td>
                <td class="px-4 py-3">
                  <span :class="matchStatusClass(match.status)" class="px-2.5 py-1 rounded-full text-xs font-semibold">
                    {{ matchStatusLabel(match.status) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-gray-500">{{ match.requestDate }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===================== TAB 4: 서비스 설정 ===================== -->
    <div v-if="activeTab === 'settings'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 max-w-xl">
        <h2 class="font-semibold text-gray-800 mb-6 text-base">매칭 서비스 설정</h2>
        <div class="space-y-5">
          <!-- 매칭 기능 ON/OFF -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
            <div>
              <p class="font-medium text-gray-800 text-sm">매칭 기능</p>
              <p class="text-xs text-gray-400 mt-0.5">전체 매칭 서비스를 ON/OFF 합니다</p>
            </div>
            <button
              @click="settings.matchingEnabled = !settings.matchingEnabled"
              :class="settings.matchingEnabled ? 'bg-green-500' : 'bg-gray-300'"
              class="relative inline-flex w-11 h-6 rounded-full transition-colors duration-200 flex-shrink-0"
            >
              <span :class="settings.matchingEnabled ? 'translate-x-5' : 'translate-x-0.5'"
                class="inline-block w-5 h-5 mt-0.5 bg-white rounded-full shadow transform transition-transform duration-200"></span>
            </button>
          </div>

          <!-- 프로필 승인제 -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
            <div>
              <p class="font-medium text-gray-800 text-sm">프로필 승인제</p>
              <p class="text-xs text-gray-400 mt-0.5">신규 프로필 등록 시 관리자 승인 필요</p>
            </div>
            <button
              @click="settings.requireApproval = !settings.requireApproval"
              :class="settings.requireApproval ? 'bg-green-500' : 'bg-gray-300'"
              class="relative inline-flex w-11 h-6 rounded-full transition-colors duration-200 flex-shrink-0"
            >
              <span :class="settings.requireApproval ? 'translate-x-5' : 'translate-x-0.5'"
                class="inline-block w-5 h-5 mt-0.5 bg-white rounded-full shadow transform transition-transform duration-200"></span>
            </button>
          </div>

          <!-- 최소 나이 -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
            <div>
              <p class="font-medium text-gray-800 text-sm">최소 나이</p>
              <p class="text-xs text-gray-400 mt-0.5">매칭 서비스 이용 최소 나이</p>
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model.number="settings.minAge"
                type="number"
                min="18"
                max="99"
                class="w-16 border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-center font-medium focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
              <span class="text-sm text-gray-500">세</span>
            </div>
          </div>

          <!-- 매칭 반경 거리 -->
          <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
            <div>
              <p class="font-medium text-gray-800 text-sm">매칭 반경 거리</p>
              <p class="text-xs text-gray-400 mt-0.5">기본 매칭 반경 설정</p>
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model.number="settings.matchRadius"
                type="number"
                min="1"
                max="500"
                class="w-20 border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-center font-medium focus:outline-none focus:ring-2 focus:ring-blue-300"
              />
              <span class="text-sm text-gray-500">km</span>
            </div>
          </div>

          <!-- 저장 버튼 -->
          <button
            @click="saveSettings"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-xl transition-colors duration-150 text-sm"
          >
            저장
          </button>

          <p v-if="settingsSaved" class="text-center text-sm text-green-600 font-medium">설정이 저장되었습니다 ✓</p>
        </div>
      </div>
    </div>

    <!-- ===================== 상세 모달 ===================== -->
    <div v-if="selectedVerification" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- 배경 오버레이 -->
      <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeModal"></div>

      <!-- 모달 내용 -->
      <div class="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <!-- 모달 헤더 -->
        <div class="flex items-center justify-between p-5 border-b border-gray-100">
          <h3 class="font-bold text-gray-900 text-lg">본인인증 상세 확인</h3>
          <button @click="closeModal" class="w-8 h-8 flex items-center justify-center rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors">
            ✕
          </button>
        </div>

        <div class="p-5 space-y-5">
          <!-- 유저 정보 -->
          <div class="flex items-center gap-4 bg-gray-50 rounded-xl p-4">
            <div class="w-14 h-14 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold text-xl flex-shrink-0">
              {{ selectedVerification.name.charAt(0) }}
            </div>
            <div class="grid grid-cols-2 gap-x-8 gap-y-1 text-sm flex-1">
              <div>
                <span class="text-gray-400 text-xs">이름</span>
                <p class="font-semibold text-gray-800">{{ selectedVerification.name }}</p>
              </div>
              <div>
                <span class="text-gray-400 text-xs">이메일</span>
                <p class="font-semibold text-gray-800">{{ selectedVerification.email }}</p>
              </div>
              <div>
                <span class="text-gray-400 text-xs">나이</span>
                <p class="font-semibold text-gray-800">{{ selectedVerification.age }}세</p>
              </div>
              <div>
                <span class="text-gray-400 text-xs">성별</span>
                <p class="font-semibold text-gray-800">{{ selectedVerification.gender }}</p>
              </div>
              <div>
                <span class="text-gray-400 text-xs">거주 지역</span>
                <p class="font-semibold text-gray-800">{{ selectedVerification.location }}</p>
              </div>
              <div>
                <span class="text-gray-400 text-xs">상태</span>
                <span :class="statusBadgeClass(selectedVerification.status)" class="px-2 py-0.5 rounded-full text-xs font-semibold">
                  {{ statusLabel(selectedVerification.status) }}
                </span>
              </div>
            </div>
          </div>

          <!-- 3개 사진 확대 -->
          <div>
            <p class="text-sm font-semibold text-gray-700 mb-3">제출 사진</p>
            <div class="grid grid-cols-3 gap-3">
              <div class="flex flex-col gap-2">
                <div class="h-48 bg-blue-100 rounded-xl flex items-center justify-center text-5xl">🪪</div>
                <p class="text-center text-xs font-medium text-gray-600 bg-gray-50 py-1 rounded">신분증</p>
              </div>
              <div class="flex flex-col gap-2">
                <div class="h-48 bg-green-100 rounded-xl flex items-center justify-center text-5xl">🤳</div>
                <p class="text-center text-xs font-medium text-gray-600 bg-gray-50 py-1 rounded">본인 사진</p>
              </div>
              <div class="flex flex-col gap-2">
                <div class="h-48 bg-yellow-100 rounded-xl flex items-center justify-center text-5xl">✍️</div>
                <p class="text-center text-xs font-medium text-gray-600 bg-gray-50 py-1 rounded">아이디 메모</p>
              </div>
            </div>
          </div>

          <!-- 거절 사유 입력 (거절 버튼 클릭 시 표시) -->
          <div v-if="showRejectInput" class="space-y-2">
            <label class="text-sm font-semibold text-gray-700">거절 사유</label>
            <textarea
              v-model="rejectReason"
              rows="3"
              placeholder="거절 사유를 입력하세요..."
              class="w-full border border-red-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-red-300 resize-none"
            ></textarea>
          </div>

          <!-- 액션 버튼 -->
          <div v-if="selectedVerification.status === 'pending'" class="flex gap-3">
            <button
              @click="approveVerification(selectedVerification.id); closeModal()"
              class="flex-1 bg-green-500 hover:bg-green-600 text-white font-semibold py-3 rounded-xl transition-colors duration-150"
            >
              승인
            </button>
            <button
              v-if="!showRejectInput"
              @click="showRejectInput = true"
              class="flex-1 bg-red-500 hover:bg-red-600 text-white font-semibold py-3 rounded-xl transition-colors duration-150"
            >
              거절
            </button>
            <button
              v-if="showRejectInput"
              @click="confirmReject(selectedVerification.id)"
              class="flex-1 bg-red-500 hover:bg-red-600 text-white font-semibold py-3 rounded-xl transition-colors duration-150"
            >
              거절 확인
            </button>
          </div>
          <div v-else class="bg-gray-50 rounded-xl p-4 text-sm text-gray-500">
            <span class="font-medium text-gray-700">처리 완료</span> — {{ selectedVerification.processedBy }} · {{ selectedVerification.processedAt }}
            <p v-if="selectedVerification.status === 'rejected' && selectedVerification.rejectReason" class="mt-1 text-red-500">
              거절 사유: {{ selectedVerification.rejectReason }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// ── 탭 ──────────────────────────────────────────────────────────────
const tabs = [
  { id: 'verification', label: '본인인증', icon: '🔐' },
  { id: 'profiles',     label: '프로필 관리', icon: '👤' },
  { id: 'matching',     label: '매칭 현황', icon: '💑' },
  { id: 'settings',     label: '서비스 설정', icon: '⚙️' },
]
const activeTab = ref('verification')

// ── 본인인증 더미 데이터 ──────────────────────────────────────────────
const verifications = ref([
  {
    id: 1,
    name: '김민준',
    username: 'minjun_kim',
    email: 'minjun@example.com',
    age: 28,
    gender: '남성',
    location: '뉴욕, NY',
    joinDate: '2026-03-20',
    status: 'pending',
    processedBy: null,
    processedAt: null,
    rejectReason: null,
  },
  {
    id: 2,
    name: '이서연',
    username: 'seoyeon_lee',
    email: 'seoyeon@example.com',
    age: 25,
    gender: '여성',
    location: 'LA, CA',
    joinDate: '2026-03-22',
    status: 'pending',
    processedBy: null,
    processedAt: null,
    rejectReason: null,
  },
  {
    id: 3,
    name: '박지호',
    username: 'jiho_park',
    email: 'jiho@example.com',
    age: 31,
    gender: '남성',
    location: '시카고, IL',
    joinDate: '2026-03-15',
    status: 'approved',
    processedBy: 'admin@somekorean.com',
    processedAt: '2026-03-18',
    rejectReason: null,
  },
  {
    id: 4,
    name: '최하은',
    username: 'haeun_choi',
    email: 'haeun@example.com',
    age: 27,
    gender: '여성',
    location: '시애틀, WA',
    joinDate: '2026-03-10',
    status: 'approved',
    processedBy: 'admin@somekorean.com',
    processedAt: '2026-03-12',
    rejectReason: null,
  },
  {
    id: 5,
    name: '정도현',
    username: 'dohyun_jung',
    email: 'dohyun@example.com',
    age: 35,
    gender: '남성',
    location: '애틀랜타, GA',
    joinDate: '2026-03-05',
    status: 'rejected',
    processedBy: 'admin@somekorean.com',
    processedAt: '2026-03-07',
    rejectReason: '신분증 사진이 불명확합니다. 다시 제출해주세요.',
  },
])

const verificationFilter = ref('all')
const verificationFilters = [
  { label: '전체', value: 'all' },
  { label: '대기중', value: 'pending' },
  { label: '승인됨', value: 'approved' },
  { label: '거절됨', value: 'rejected' },
]

const filteredVerifications = computed(() => {
  if (verificationFilter.value === 'all') return verifications.value
  return verifications.value.filter(v => v.status === verificationFilter.value)
})

const verificationStats = computed(() => ({
  pending:  verifications.value.filter(v => v.status === 'pending').length,
  approved: verifications.value.filter(v => v.status === 'approved').length,
  rejected: verifications.value.filter(v => v.status === 'rejected').length,
}))

const pendingVerifications = computed(() => verifications.value.filter(v => v.status === 'pending'))

function statusBadgeClass(status) {
  return {
    pending:  'bg-yellow-100 text-yellow-700',
    approved: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
  }[status] || 'bg-gray-100 text-gray-500'
}
function statusLabel(status) {
  return { pending: '대기중', approved: '승인됨', rejected: '거절됨' }[status] || status
}

function approveVerification(id) {
  const item = verifications.value.find(v => v.id === id)
  if (item) {
    item.status = 'approved'
    item.processedBy = 'admin@somekorean.com'
    item.processedAt = new Date().toISOString().slice(0, 10)
  }
}

function rejectVerification(id, reason) {
  const item = verifications.value.find(v => v.id === id)
  if (item) {
    item.status = 'rejected'
    item.rejectReason = reason || '관리자에 의해 거절됨'
    item.processedBy = 'admin@somekorean.com'
    item.processedAt = new Date().toISOString().slice(0, 10)
  }
}

// ── 모달 ──────────────────────────────────────────────────────────────
const selectedVerification = ref(null)
const showRejectInput = ref(false)
const rejectReason = ref('')

function openVerificationModal(req) {
  selectedVerification.value = req
  showRejectInput.value = false
  rejectReason.value = ''
}
function openRejectModal(req) {
  selectedVerification.value = req
  showRejectInput.value = true
  rejectReason.value = ''
}
function closeModal() {
  selectedVerification.value = null
  showRejectInput.value = false
  rejectReason.value = ''
}
function confirmReject(id) {
  rejectVerification(id, rejectReason.value)
  closeModal()
}

// ── 프로필 관리 더미 데이터 ───────────────────────────────────────────
const profiles = ref([
  { id: 1, nickname: '별빛청년',  age: 28, gender: '남성', region: '뉴욕',   photoCount: 4, completion: 90, active: true  },
  { id: 2, nickname: '봄날소녀',  age: 25, gender: '여성', region: 'LA',     photoCount: 5, completion: 95, active: true  },
  { id: 3, nickname: '산하남자',  age: 31, gender: '남성', region: '시카고', photoCount: 2, completion: 65, active: true  },
  { id: 4, nickname: '하늘여인',  age: 27, gender: '여성', region: '시애틀', photoCount: 3, completion: 75, active: false },
  { id: 5, nickname: '달빛청년',  age: 33, gender: '남성', region: '뉴욕',   photoCount: 4, completion: 85, active: true  },
  { id: 6, nickname: '새벽소녀',  age: 29, gender: '여성', region: 'LA',     photoCount: 6, completion: 100, active: true },
])

const profileFilter = ref({ gender: '', ageGroup: '', region: '' })

const filteredProfiles = computed(() => {
  return profiles.value.filter(p => {
    const genderOk = !profileFilter.value.gender || p.gender === profileFilter.value.gender
    const regionOk = !profileFilter.value.region || p.region === profileFilter.value.region
    const ageOk = !profileFilter.value.ageGroup ||
      (profileFilter.value.ageGroup === '20' && p.age >= 20 && p.age < 30) ||
      (profileFilter.value.ageGroup === '30' && p.age >= 30 && p.age < 40) ||
      (profileFilter.value.ageGroup === '40' && p.age >= 40)
    return genderOk && regionOk && ageOk
  })
})

function resetProfileFilter() {
  profileFilter.value = { gender: '', ageGroup: '', region: '' }
}
function toggleProfileStatus(id) {
  const p = profiles.value.find(p => p.id === id)
  if (p) p.active = !p.active
}
function deleteProfile(id) {
  if (confirm('정말 삭제하시겠습니까?')) {
    profiles.value = profiles.value.filter(p => p.id !== id)
  }
}

// ── 매칭 현황 더미 데이터 ─────────────────────────────────────────────
const matchRequests = ref([
  { id: 1, requester: '별빛청년', receiver: '봄날소녀', status: 'accepted',  requestDate: '2026-03-25' },
  { id: 2, requester: '산하남자', receiver: '하늘여인', status: 'pending',   requestDate: '2026-03-26' },
  { id: 3, requester: '달빛청년', receiver: '새벽소녀', status: 'rejected',  requestDate: '2026-03-24' },
  { id: 4, requester: '별빛청년', receiver: '하늘여인', status: 'pending',   requestDate: '2026-03-28' },
])

const matchSuccessRate = computed(() => {
  const total = matchRequests.value.length
  if (!total) return 0
  const accepted = matchRequests.value.filter(m => m.status === 'accepted').length
  return Math.round((accepted / total) * 100)
})
const todayNewMatches = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return matchRequests.value.filter(m => m.requestDate === today).length
})

function matchStatusClass(status) {
  return {
    pending:  'bg-yellow-100 text-yellow-700',
    accepted: 'bg-green-100 text-green-700',
    rejected: 'bg-red-100 text-red-700',
  }[status] || 'bg-gray-100 text-gray-500'
}
function matchStatusLabel(status) {
  return { pending: '대기중', accepted: '수락됨', rejected: '거절됨' }[status] || status
}

// ── 서비스 설정 ──────────────────────────────────────────────────────
const settings = ref({
  matchingEnabled: true,
  requireApproval: true,
  minAge: 18,
  matchRadius: 50,
})
const settingsSaved = ref(false)

function saveSettings() {
  // TODO: API 연동
  settingsSaved.value = true
  setTimeout(() => { settingsSaved.value = false }, 3000)
}
</script>
