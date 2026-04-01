<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">공동구매 관리</h1>
      <p class="text-gray-500 text-sm mt-1">기업 공동구매 목록, 기업 회원, 정산을 관리합니다. 기업 회원만 공동구매를 등록할 수 있습니다.</p>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 mb-6 bg-white rounded-t-lg shadow-sm overflow-x-auto">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'px-6 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
          activeTab === tab.key
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700'
        ]"
      >
        {{ tab.label }}
        <span v-if="tab.badge" class="ml-2 px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-600">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- ===== TAB 1: 공동구매 목록 ===== -->
    <div v-if="activeTab === 'groupbuys'">
      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm p-4 mb-4 flex flex-wrap gap-4 items-end">
        <div>
          <label class="text-xs text-gray-500 block mb-1">상태</label>
          <select v-model="gbFilter.status" class="border border-gray-300 rounded px-3 py-1.5 text-sm">
            <option value="">전체</option>
            <option value="pending">승인대기</option>
            <option value="active">모집중</option>
            <option value="closed">마감</option>
            <option value="completed">완료</option>
            <option value="rejected">거절</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-gray-500 block mb-1">카테고리</label>
          <select v-model="gbFilter.category" class="border border-gray-300 rounded px-3 py-1.5 text-sm">
            <option value="">전체</option>
            <option value="식품">식품</option>
            <option value="농산물">농산물</option>
            <option value="해산물">해산물</option>
            <option value="가공식품">가공식품</option>
            <option value="생활용품">생활용품</option>
          </select>
        </div>
        <button @click="gbFilter = { status: '', category: '' }" class="text-sm text-gray-400 hover:text-gray-600 underline">초기화</button>
      </div>

      <!-- 승인대기 알림 배너 -->
      <div v-if="pendingGroupbuys.length > 0" class="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4 flex items-center gap-3">
        <span class="text-yellow-600 font-semibold text-sm">승인 대기 중인 공동구매가 {{ pendingGroupbuys.length }}건 있습니다.</span>
        <button @click="gbFilter.status = 'pending'" class="text-xs text-yellow-700 underline hover:no-underline">바로 보기</button>
      </div>

      <!-- GroupBuy Table -->
      <div class="bg-white rounded-lg shadow-sm overflow-x-auto">
        <table class="w-full text-sm min-w-max">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">ID</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">제목</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">기업명</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">카테고리</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">가격</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">참여 / 최대</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">마감일</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">상태</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="gb in filteredGroupbuys"
              :key="gb.id"
              :class="gb.status === 'pending' ? 'bg-yellow-50 hover:bg-yellow-100' : 'hover:bg-gray-50'"
            >
              <td class="px-4 py-3 font-mono text-gray-500 text-xs">#{{ gb.id }}</td>
              <td class="px-4 py-3">
                <div class="font-medium text-gray-800">{{ gb.title }}</div>
                <div class="text-xs text-gray-400 mt-0.5">{{ gb.description.slice(0, 40) }}...</div>
              </td>
              <td class="px-4 py-3">
                <div class="text-gray-700 font-medium">{{ gb.company_name }}</div>
                <div class="text-xs text-gray-400">기업 전용</div>
              </td>
              <td class="px-4 py-3">
                <span class="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{{ gb.category }}</span>
              </td>
              <td class="px-4 py-3 font-semibold text-gray-800">${{ gb.price.toFixed(2) }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <span class="font-semibold text-blue-600">{{ gb.participants }}</span>
                  <span class="text-gray-400">/</span>
                  <span class="text-gray-600">{{ gb.max_participants }}</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-1 mt-1">
                  <div class="bg-blue-500 h-1 rounded-full" :style="{ width: Math.min(100, gb.participants / gb.max_participants * 100) + '%' }"></div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ gb.deadline }}</td>
              <td class="px-4 py-3">
                <span :class="gbStatusBadge(gb.status)">{{ gbStatusLabel(gb.status) }}</span>
              </td>
              <td class="px-4 py-3">
                <div class="flex gap-1 flex-wrap">
                  <button v-if="gb.status === 'pending'" @click="openApproveGb(gb)" class="px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600 font-semibold">승인</button>
                  <button v-if="gb.status === 'pending'" @click="openRejectGb(gb)" class="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 font-semibold">반려</button>
                  <button @click="openGbDetail(gb)" class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200">상세</button>
                  <button v-if="gb.status !== 'completed'" @click="deleteGb(gb)" class="px-2 py-1 text-xs bg-red-50 text-red-500 rounded hover:bg-red-100">삭제</button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredGroupbuys.length === 0">
              <td colspan="9" class="px-4 py-10 text-center text-gray-400">조건에 맞는 공동구매가 없습니다.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ===== TAB 2: 기업 회원 관리 ===== -->
    <div v-if="activeTab === 'companies'">
      <!-- Pending company approvals -->
      <div class="mb-8">
        <h2 class="text-base font-semibold text-gray-700 mb-3">
          기업 등록 신청 대기
          <span class="ml-2 text-xs bg-yellow-200 text-yellow-800 px-2 py-0.5 rounded-full">{{ pendingCompanies.length }}</span>
        </h2>
        <div v-if="pendingCompanies.length === 0" class="bg-white rounded-lg shadow-sm p-6 text-center text-gray-400">
          대기중인 신청이 없습니다.
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="company in pendingCompanies"
            :key="company.id"
            class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex flex-wrap items-start justify-between gap-3"
          >
            <div class="space-y-0.5">
              <div class="font-semibold text-gray-800">{{ company.company_name }}</div>
              <div class="text-sm text-gray-500">사업자등록번호: {{ company.business_no }} · 대표자: {{ company.owner }}</div>
              <div class="text-sm text-gray-500">{{ company.phone }} · {{ company.email }}</div>
              <div class="text-xs text-gray-400">신청일: {{ company.applied_at }}</div>
            </div>
            <div class="flex gap-2 flex-wrap">
              <button @click="approveCompany(company)" class="px-3 py-1.5 text-sm bg-green-500 text-white rounded hover:bg-green-600 font-medium">승인</button>
              <button @click="rejectCompany(company)" class="px-3 py-1.5 text-sm bg-red-500 text-white rounded hover:bg-red-600 font-medium">반려</button>
              <button @click="openCompanyDetail(company)" class="px-3 py-1.5 text-sm bg-white border border-gray-300 text-gray-600 rounded hover:bg-gray-50">상세</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Approved companies -->
      <div>
        <h2 class="text-base font-semibold text-gray-700 mb-3">승인된 기업 회원</h2>
        <div class="bg-white rounded-lg shadow-sm overflow-x-auto">
          <table class="w-full text-sm min-w-max">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">회사명</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">사업자등록번호</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">대표자</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">연락처</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">ACH 상태</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">공동구매</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">승인일</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="company in approvedCompanies" :key="company.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-800">{{ company.company_name }}</td>
                <td class="px-4 py-3 text-gray-500 font-mono text-xs">{{ company.business_no }}</td>
                <td class="px-4 py-3 text-gray-700">{{ company.owner }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ company.phone }}<br/>{{ company.email }}</td>
                <td class="px-4 py-3">
                  <span v-if="company.ach_bank" class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">등록됨</span>
                  <span v-else class="text-xs bg-gray-100 text-gray-400 px-2 py-0.5 rounded-full">미등록</span>
                </td>
                <td class="px-4 py-3 text-gray-700">{{ company.groupbuys_count }}건</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ company.approved_at }}</td>
                <td class="px-4 py-3">
                  <button @click="openCompanyDetail(company)" class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200">상세</button>
                </td>
              </tr>
              <tr v-if="approvedCompanies.length === 0">
                <td colspan="8" class="px-4 py-10 text-center text-gray-400">승인된 기업 회원이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== TAB 3: 정산 관리 ===== -->
    <div v-if="activeTab === 'payouts'">
      <!-- Summary -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow-sm p-5 border-l-4 border-orange-400">
          <div class="text-xs text-gray-500 mb-1">미정산 합계</div>
          <div class="text-2xl font-bold text-gray-800">${{ gbTotalPending.toFixed(2) }}</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-5 border-l-4 border-green-400">
          <div class="text-xs text-gray-500 mb-1">이달 수수료 수익 (15%)</div>
          <div class="text-2xl font-bold text-green-600">${{ gbMonthlyCommission.toFixed(2) }}</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-5 border-l-4 border-blue-400">
          <div class="text-xs text-gray-500 mb-1">완료된 공동구매</div>
          <div class="text-2xl font-bold text-blue-600">{{ completedGroupbuys }}건</div>
        </div>
      </div>

      <!-- Payout pending list -->
      <div class="mb-6">
        <h2 class="text-base font-semibold text-gray-700 mb-3">정산 대기 목록 (마감 완료)</h2>
        <div class="bg-white rounded-lg shadow-sm overflow-x-auto">
          <table class="w-full text-sm min-w-max">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">기업명</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">공동구매명</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">참여자수</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">총 결제액</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">수수료 (15%)</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">정산 금액</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">ACH 계좌</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="gb in closedGroupbuys" :key="'pay-'+gb.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-800">{{ gb.company_name }}</td>
                <td class="px-4 py-3 text-gray-700">{{ gb.title }}</td>
                <td class="px-4 py-3 text-gray-600">{{ gb.participants }}명</td>
                <td class="px-4 py-3 text-gray-700">${{ (gb.participants * gb.price).toFixed(2) }}</td>
                <td class="px-4 py-3 text-red-600">-${{ (gb.participants * gb.price * 0.15).toFixed(2) }}</td>
                <td class="px-4 py-3 font-semibold text-green-700">${{ (gb.participants * gb.price * 0.85).toFixed(2) }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ getCompanyAch(gb.company_name) }}</td>
                <td class="px-4 py-3">
                  <button @click="processGbPayout(gb)" class="px-3 py-1.5 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 font-medium">정산하기</button>
                </td>
              </tr>
              <tr v-if="closedGroupbuys.length === 0">
                <td colspan="8" class="px-4 py-10 text-center text-gray-400">정산 대기 중인 공동구매가 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Payout history -->
      <div>
        <h2 class="text-base font-semibold text-gray-700 mb-3">정산 내역</h2>
        <div class="bg-white rounded-lg shadow-sm overflow-x-auto">
          <table class="w-full text-sm min-w-max">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">날짜</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">기업명</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">공동구매</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">정산 금액</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">방법</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">상태</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="payout in gbPayoutHistory" :key="payout.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-gray-500">{{ payout.date }}</td>
                <td class="px-4 py-3 font-medium text-gray-800">{{ payout.company }}</td>
                <td class="px-4 py-3 text-gray-700">{{ payout.title }}</td>
                <td class="px-4 py-3 font-semibold text-gray-800">${{ payout.amount.toFixed(2) }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ payout.method }}</td>
                <td class="px-4 py-3">
                  <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">완료</span>
                </td>
              </tr>
              <tr v-if="gbPayoutHistory.length === 0">
                <td colspan="6" class="px-4 py-10 text-center text-gray-400">정산 내역이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== MODAL: 공동구매 승인 ===== -->
    <div v-if="showApproveGbModal" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-bold text-gray-800">공동구매 승인</h3>
        </div>
        <div class="p-6 space-y-4">
          <div class="p-4 bg-gray-50 rounded-lg text-sm space-y-1.5">
            <div><span class="text-gray-400 mr-2">제목</span><span class="font-medium">{{ selectedGb?.title }}</span></div>
            <div><span class="text-gray-400 mr-2">기업</span><span>{{ selectedGb?.company_name }}</span></div>
            <div><span class="text-gray-400 mr-2">가격</span><span class="font-semibold text-green-700">${{ selectedGb?.price?.toFixed(2) }}</span></div>
          </div>
          <div>
            <label class="text-sm text-gray-600 mb-1.5 block font-medium">관리자 메모 (선택)</label>
            <textarea v-model="approveGbNote" rows="3" class="w-full border border-gray-300 rounded px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-300" placeholder="메모를 입력하세요..."></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
          <button @click="showApproveGbModal = false" class="px-4 py-2 text-sm border border-gray-300 rounded text-gray-600 hover:bg-gray-50">취소</button>
          <button @click="confirmApproveGb" class="px-4 py-2 text-sm bg-green-500 text-white rounded hover:bg-green-600 font-medium">승인 확정</button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL: 공동구매 반려 ===== -->
    <div v-if="showRejectGbModal" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-bold text-gray-800">공동구매 반려</h3>
        </div>
        <div class="p-6 space-y-4">
          <div class="p-4 bg-gray-50 rounded-lg text-sm">
            <div class="font-medium text-gray-800">{{ selectedGb?.title }}</div>
            <div class="text-gray-500 mt-1">{{ selectedGb?.company_name }}</div>
          </div>
          <div>
            <label class="text-sm text-gray-600 mb-1.5 block font-medium">
              반려 사유 <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="rejectGbReason"
              rows="4"
              class="w-full border border-gray-300 rounded px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-red-300"
              :class="rejectGbError ? 'border-red-400' : ''"
              placeholder="반려 사유를 상세히 입력하세요..."
            ></textarea>
            <p v-if="rejectGbError" class="text-xs text-red-500 mt-1">반려 사유는 필수 입력 항목입니다.</p>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
          <button @click="showRejectGbModal = false" class="px-4 py-2 text-sm border border-gray-300 rounded text-gray-600 hover:bg-gray-50">취소</button>
          <button @click="confirmRejectGb" class="px-4 py-2 text-sm bg-red-500 text-white rounded hover:bg-red-600 font-medium">반려 확정</button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL: 공동구매 상세 ===== -->
    <div v-if="showGbDetailModal" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center px-6 py-4 border-b border-gray-100 sticky top-0 bg-white">
          <h3 class="text-lg font-bold text-gray-800">공동구매 상세 #{{ selectedGb?.id }}</h3>
          <button @click="showGbDetailModal = false" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div v-if="selectedGb" class="p-6 space-y-5 text-sm">
          <!-- Product info -->
          <div class="space-y-2">
            <div class="flex items-center gap-2">
              <h4 class="font-semibold text-gray-700">상품 정보</h4>
              <span :class="gbStatusBadge(selectedGb.status)">{{ gbStatusLabel(selectedGb.status) }}</span>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-xs text-gray-400 mb-1">제목</div>
                <div class="font-medium">{{ selectedGb.title }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-xs text-gray-400 mb-1">카테고리</div>
                <div>{{ selectedGb.category }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-xs text-gray-400 mb-1">가격</div>
                <div class="font-semibold text-green-700">${{ selectedGb.price.toFixed(2) }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-xs text-gray-400 mb-1">마감일</div>
                <div>{{ selectedGb.deadline }}</div>
              </div>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-xs text-gray-400 mb-1">상품 설명</div>
              <div class="text-gray-700">{{ selectedGb.description }}</div>
            </div>
          </div>

          <!-- Participants -->
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">참여자 목록 ({{ selectedGb.participants }}/{{ selectedGb.max_participants }})</h4>
            <div class="border border-gray-200 rounded-lg overflow-hidden">
              <table class="w-full text-xs">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left text-gray-500">이름</th>
                    <th class="px-3 py-2 text-left text-gray-500">연락처</th>
                    <th class="px-3 py-2 text-left text-gray-500">참여일</th>
                    <th class="px-3 py-2 text-left text-gray-500">결제</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="(p, i) in (selectedGb.participant_list || [])" :key="i">
                    <td class="px-3 py-2 font-medium text-gray-800">{{ p.name }}</td>
                    <td class="px-3 py-2 text-gray-500">{{ p.phone }}</td>
                    <td class="px-3 py-2 text-gray-400">{{ p.joined_at }}</td>
                    <td class="px-3 py-2">
                      <span :class="p.paid ? 'text-green-600 bg-green-50' : 'text-yellow-600 bg-yellow-50'" class="px-1.5 py-0.5 rounded">{{ p.paid ? '결제완료' : '미결제' }}</span>
                    </td>
                  </tr>
                  <tr v-if="!(selectedGb.participant_list && selectedGb.participant_list.length)">
                    <td colspan="4" class="px-3 py-4 text-center text-gray-400">참여자가 없습니다.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Company info -->
          <div class="bg-blue-50 border border-blue-100 p-4 rounded-lg">
            <h4 class="text-xs text-blue-500 font-semibold mb-3">기업 정보</h4>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div><span class="text-gray-400">회사명:</span> <span class="font-medium">{{ selectedGb.company_name }}</span></div>
              <div><span class="text-gray-400">사업자번호:</span> {{ selectedGb.business_no }}</div>
              <div><span class="text-gray-400">대표자:</span> {{ selectedGb.owner }}</div>
              <div><span class="text-gray-400">연락처:</span> {{ selectedGb.company_phone }}</div>
            </div>
          </div>

          <!-- ACH info -->
          <div class="bg-gray-50 border border-gray-200 p-4 rounded-lg">
            <h4 class="text-xs text-gray-500 font-semibold mb-3">ACH 정산 계좌</h4>
            <div v-if="selectedGb.ach_bank" class="grid grid-cols-2 gap-2 text-sm">
              <div><span class="text-gray-400">은행명:</span> <span class="font-medium">{{ selectedGb.ach_bank }}</span></div>
              <div><span class="text-gray-400">계좌번호:</span> <span class="font-mono">{{ selectedGb.ach_account }}</span></div>
              <div class="col-span-2"><span class="text-gray-400">라우팅번호:</span> <span class="font-mono">{{ selectedGb.ach_routing }}</span></div>
            </div>
            <div v-else class="text-gray-400 text-sm">ACH 계좌 정보가 없습니다.</div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end">
          <button @click="showGbDetailModal = false" class="px-4 py-2 text-sm bg-gray-100 text-gray-600 rounded hover:bg-gray-200">닫기</button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL: 기업 상세 ===== -->
    <div v-if="showCompanyDetailModal" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-xl max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center px-6 py-4 border-b border-gray-100 sticky top-0 bg-white">
          <h3 class="text-lg font-bold text-gray-800">기업 회원 상세</h3>
          <button @click="showCompanyDetailModal = false" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div v-if="selectedCompany" class="p-6 space-y-5 text-sm">
          <!-- Business info -->
          <div>
            <h4 class="font-semibold text-gray-700 mb-3">사업자 정보</h4>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-xs text-gray-400 mb-1">회사명</div>
                <div class="font-semibold">{{ selectedCompany.company_name }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-xs text-gray-400 mb-1">사업자등록번호</div>
                <div class="font-mono font-medium">{{ selectedCompany.business_no }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-xs text-gray-400 mb-1">대표자</div>
                <div class="font-medium">{{ selectedCompany.owner }}</div>
              </div>
              <div class="bg-gray-50 p-3 rounded-lg">
                <div class="text-xs text-gray-400 mb-1">연락처</div>
                <div>{{ selectedCompany.phone }}</div>
                <div class="text-gray-400">{{ selectedCompany.email }}</div>
              </div>
            </div>
          </div>

          <!-- ACH info -->
          <div v-if="selectedCompany.ach_bank" class="bg-blue-50 border border-blue-100 p-4 rounded-lg">
            <div class="text-xs text-blue-500 font-semibold mb-3">ACH 정산 계좌</div>
            <div class="grid grid-cols-2 gap-2">
              <div><span class="text-gray-400">은행명:</span> <span class="font-medium">{{ selectedCompany.ach_bank }}</span></div>
              <div><span class="text-gray-400">계좌번호:</span> <span class="font-mono">{{ selectedCompany.ach_account }}</span></div>
              <div class="col-span-2"><span class="text-gray-400">라우팅번호:</span> <span class="font-mono">{{ selectedCompany.ach_routing }}</span></div>
            </div>
          </div>
          <div v-else class="bg-gray-50 p-3 rounded-lg text-gray-400 text-center">ACH 계좌 정보가 등록되지 않았습니다.</div>

          <!-- Company's groupbuys -->
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">공동구매 내역 ({{ selectedCompany.groupbuys_count }}건)</h4>
            <div v-if="getCompanyGroupbuys(selectedCompany).length === 0" class="text-gray-400 text-sm">공동구매 내역이 없습니다.</div>
            <div v-else class="space-y-1.5 max-h-48 overflow-y-auto">
              <div
                v-for="gb in getCompanyGroupbuys(selectedCompany)"
                :key="gb.id"
                class="flex justify-between items-center bg-gray-50 px-3 py-2 rounded text-xs"
              >
                <span class="font-medium text-gray-700">{{ gb.title }}</span>
                <span :class="gbStatusBadge(gb.status)">{{ gbStatusLabel(gb.status) }}</span>
                <span class="text-gray-400">{{ gb.deadline }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end">
          <button @click="showCompanyDetailModal = false" class="px-4 py-2 text-sm bg-gray-100 text-gray-600 rounded hover:bg-gray-200">닫기</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <Transition name="fade">
      <div
        v-if="toast.show"
        class="fixed bottom-6 right-6 z-50 px-5 py-3 rounded-lg shadow-lg text-white text-sm font-medium"
        :class="toast.type === 'success' ? 'bg-green-500' : 'bg-red-500'"
      >
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// ─── Tabs ────────────────────────────────────────────────
const activeTab = ref('groupbuys')

const pendingGbCount = computed(() => groupbuys.value.filter(g => g.status === 'pending').length)
const pendingCompanyCount = computed(() => companies.value.filter(c => c.status === 'pending').length)

const tabs = computed(() => [
  { key: 'groupbuys', label: '공동구매 목록', badge: pendingGbCount.value || null },
  { key: 'companies', label: '기업 회원 관리', badge: pendingCompanyCount.value || null },
  { key: 'payouts', label: '정산 관리', badge: null },
])

// ─── Dummy Companies ─────────────────────────────────────
const companies = ref([])

// ─── Dummy Groupbuys ─────────────────────────────────────
const groupbuys = ref([])

// ─── Payout History ──────────────────────────────────────
const gbPayoutHistory = ref([
  { id: 1, date: '2026-02-28', company: 'H마트 LA점', title: '설 선물 세트', amount: 3825.00, method: 'ACH (Wells Fargo ****8901)' },
])

// ─── Computed ────────────────────────────────────────────
const pendingGroupbuys = computed(() => groupbuys.value.filter(g => g.status === 'pending'))
const pendingCompanies = computed(() => companies.value.filter(c => c.status === 'pending'))
const approvedCompanies = computed(() => companies.value.filter(c => c.status === 'approved'))
const closedGroupbuys = computed(() => groupbuys.value.filter(g => g.status === 'closed'))

const gbFilter = ref({ status: '', category: '' })
const filteredGroupbuys = computed(() => {
  return groupbuys.value.filter(g => {
    if (gbFilter.value.status && g.status !== gbFilter.value.status) return false
    if (gbFilter.value.category && g.category !== gbFilter.value.category) return false
    return true
  })
})

const gbTotalPending = computed(() =>
  closedGroupbuys.value.reduce((s, g) => s + g.participants * g.price * 0.85, 0)
)
const gbMonthlyCommission = computed(() =>
  groupbuys.value.filter(g => g.status === 'completed' || g.status === 'closed')
    .reduce((s, g) => s + g.participants * g.price * 0.15, 0)
)
const completedGroupbuys = computed(() =>
  groupbuys.value.filter(g => g.status === 'completed').length
)

const getCompanyGroupbuys = (company) =>
  groupbuys.value.filter(g => g.company_name === company.company_name)

const getCompanyAch = (companyName) => {
  const c = companies.value.find(c => c.company_name === companyName)
  if (!c || !c.ach_bank) return '미등록'
  return `${c.ach_bank} ${c.ach_account}`
}

// ─── Modals / State ──────────────────────────────────────
const showApproveGbModal = ref(false)
const showRejectGbModal = ref(false)
const showGbDetailModal = ref(false)
const showCompanyDetailModal = ref(false)
const selectedGb = ref(null)
const selectedCompany = ref(null)

const approveGbNote = ref('')
const rejectGbReason = ref('')
const rejectGbError = ref(false)

const openApproveGb = (gb) => {
  selectedGb.value = gb
  approveGbNote.value = ''
  showApproveGbModal.value = true
}

const confirmApproveGb = () => {
  if (!selectedGb.value) return
  const idx = groupbuys.value.findIndex(g => g.id === selectedGb.value.id)
  if (idx !== -1) groupbuys.value[idx].status = 'active'
  showApproveGbModal.value = false
  showToast('success', '공동구매가 승인되어 모집이 시작됩니다.')
  // API: POST /api/admin/groupbuys/{id}/approve
}

const openRejectGb = (gb) => {
  selectedGb.value = gb
  rejectGbReason.value = ''
  rejectGbError.value = false
  showRejectGbModal.value = true
}

const confirmRejectGb = () => {
  if (!rejectGbReason.value.trim()) {
    rejectGbError.value = true
    return
  }
  if (!selectedGb.value) return
  const idx = groupbuys.value.findIndex(g => g.id === selectedGb.value.id)
  if (idx !== -1) groupbuys.value[idx].status = 'rejected'
  showRejectGbModal.value = false
  showToast('success', '공동구매가 반려되었습니다.')
  // API: POST /api/admin/groupbuys/{id}/reject
}

const openGbDetail = (gb) => {
  selectedGb.value = gb
  showGbDetailModal.value = true
}

const deleteGb = (gb) => {
  if (!confirm(`"${gb.title}" 공동구매를 삭제하시겠습니까?`)) return
  const idx = groupbuys.value.findIndex(g => g.id === gb.id)
  if (idx !== -1) groupbuys.value.splice(idx, 1)
  showToast('success', '공동구매가 삭제되었습니다.')
}

const openCompanyDetail = (company) => {
  selectedCompany.value = company
  showCompanyDetailModal.value = true
}

const approveCompany = (company) => {
  const idx = companies.value.findIndex(c => c.id === company.id)
  if (idx !== -1) {
    companies.value[idx].status = 'approved'
    companies.value[idx].approved_at = new Date().toISOString().split('T')[0]
  }
  showToast('success', `${company.company_name} 기업 회원이 승인되었습니다.`)
  // API: POST /api/admin/companies/{id}/approve
}

const rejectCompany = (company) => {
  const idx = companies.value.findIndex(c => c.id === company.id)
  if (idx !== -1) companies.value[idx].status = 'rejected'
  showToast('success', `${company.company_name} 기업 회원이 반려되었습니다.`)
}

const processGbPayout = (gb) => {
  const amount = gb.participants * gb.price * 0.85
  const company = companies.value.find(c => c.company_name === gb.company_name)
  gbPayoutHistory.value.unshift({
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    company: gb.company_name,
    title: gb.title,
    amount,
    method: company && company.ach_bank ? `ACH (${company.ach_bank} ${company.ach_account})` : 'ACH',
  })
  const idx = groupbuys.value.findIndex(g => g.id === gb.id)
  if (idx !== -1) groupbuys.value[idx].status = 'completed'
  showToast('success', `$${amount.toFixed(2)} 정산이 완료되었습니다.`)
  // API: POST /api/admin/groupbuys/{id}/payout
}

// ─── Helpers ─────────────────────────────────────────────
const gbStatusBadge = (s) => ({
  pending:   'text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700',
  active:    'text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700',
  closed:    'text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700',
  completed: 'text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700',
  rejected:  'text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700',
}[s] || 'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600')

const gbStatusLabel = (s) => ({
  pending: '승인대기', active: '모집중', closed: '마감', completed: '완료', rejected: '거절',
}[s] || s)

// ─── Toast ────────────────────────────────────────────────
const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (type, message) => {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}

const gbTotal = ref(0)
const gbLoading = ref(false)

async function loadGroupBuys() {
  gbLoading.value = true
  try {
    const { data } = await axios.get('/api/admin/groupbuys')
    groupbuys.value = Array.isArray(data) ? data : (data.data || [])
    gbTotal.value = data.total || groupbuys.value.length
  } catch(e) {} finally { gbLoading.value = false }
}

async function approveGroupBuy(gb) {
  await axios.post(`/api/admin/groupbuys/${gb.id}/approve`)
  gb.status = 'active'
}

async function deleteGroupBuy(gb) {
  if (!confirm('삭제하시겠습니까?')) return
  await axios.delete(`/api/admin/groupbuys/${gb.id}`)
  groupbuys.value = groupbuys.value.filter(g => g.id !== gb.id)
}

onMounted(() => {
  loadGroupBuys()
})

</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
