<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">라이드 관리</h1>
      <p class="text-gray-500 text-sm mt-1">라이드 요청, 드라이버, 정산, 설정을 관리합니다.</p>
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

    <!-- ===== TAB 1: 라이드 요청 관리 ===== -->
    <div v-if="activeTab === 'rides'">
      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm p-4 mb-4 flex flex-wrap gap-4 items-end">
        <div>
          <label class="text-xs text-gray-500 block mb-1">상태</label>
          <select v-model="rideFilter.status" class="border border-gray-300 rounded px-3 py-1.5 text-sm">
            <option value="">전체</option>
            <option value="pending">대기중</option>
            <option value="approved">수락됨</option>
            <option value="in_progress">진행중</option>
            <option value="completed">완료</option>
            <option value="cancelled">취소</option>
          </select>
        </div>
        <div>
          <label class="text-xs text-gray-500 block mb-1">날짜</label>
          <input type="date" v-model="rideFilter.date" class="border border-gray-300 rounded px-3 py-1.5 text-sm" />
        </div>
        <button @click="rideFilter = { status: '', date: '' }" class="text-sm text-gray-400 hover:text-gray-600 underline">초기화</button>
      </div>

      <!-- Rides Table -->
      <div class="bg-white rounded-lg shadow-sm overflow-x-auto">
        <table class="w-full text-sm min-w-max">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">ID</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">출발 → 도착</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">승객</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">드라이버</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">요금</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">결제</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">상태</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">요청일</th>
              <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">관리</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="ride in filteredRides"
              :key="ride.id"
              :class="ride.status === 'pending' ? 'bg-yellow-50 hover:bg-yellow-100' : 'hover:bg-gray-50'"
            >
              <td class="px-4 py-3 font-mono text-gray-500 text-xs">#{{ ride.id }}</td>
              <td class="px-4 py-3">
                <div class="text-xs space-y-0.5">
                  <div class="font-medium text-gray-800">{{ ride.from }}</div>
                  <div class="text-gray-400 text-center">↓</div>
                  <div class="font-medium text-gray-800">{{ ride.to }}</div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-700">{{ ride.passenger }}</td>
              <td class="px-4 py-3">
                <span v-if="ride.driver" class="text-gray-700">{{ ride.driver }}</span>
                <span v-else class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">미배정</span>
              </td>
              <td class="px-4 py-3 font-semibold text-gray-800">${{ ride.fare.toFixed(2) }}</td>
              <td class="px-4 py-3">
                <span :class="paymentBadge(ride.payment_status)">{{ paymentLabel(ride.payment_status) }}</span>
              </td>
              <td class="px-4 py-3">
                <span :class="rideBadge(ride.status)">{{ rideStatusLabel(ride.status) }}</span>
              </td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ ride.created_at }}</td>
              <td class="px-4 py-3">
                <div class="flex gap-1 flex-wrap">
                  <button
                    v-if="ride.status === 'pending'"
                    @click="openApproveRide(ride)"
                    class="px-2 py-1 text-xs bg-green-500 text-white rounded hover:bg-green-600 font-semibold"
                  >승인</button>
                  <button
                    v-if="ride.status === 'pending'"
                    @click="rejectRide(ride)"
                    class="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 font-semibold"
                  >반려</button>
                  <button
                    @click="openRideDetail(ride)"
                    class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
                  >상세</button>
                </div>
              </td>
            </tr>
            <tr v-if="filteredRides.length === 0">
              <td colspan="9" class="px-4 py-10 text-center text-gray-400">조건에 맞는 라이드가 없습니다.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ===== TAB 2: 드라이버 관리 ===== -->
    <div v-if="activeTab === 'drivers'">
      <!-- Pending approvals -->
      <div class="mb-8">
        <h2 class="text-base font-semibold text-gray-700 mb-3">
          신청 대기중
          <span class="ml-2 text-xs bg-yellow-200 text-yellow-800 px-2 py-0.5 rounded-full">{{ pendingDrivers.length }}</span>
        </h2>
        <div v-if="pendingDrivers.length === 0" class="bg-white rounded-lg shadow-sm p-6 text-center text-gray-400">
          대기중인 신청이 없습니다.
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="driver in pendingDrivers"
            :key="driver.id"
            class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex flex-wrap items-center justify-between gap-3"
          >
            <div>
              <div class="font-semibold text-gray-800">{{ driver.name }}</div>
              <div class="text-sm text-gray-500 mt-0.5">{{ driver.phone }} · {{ driver.vehicle }} · {{ driver.license }}</div>
              <div class="text-xs text-gray-400 mt-0.5">신청일: {{ driver.applied_at }}</div>
            </div>
            <div class="flex gap-2 flex-wrap">
              <button @click="approveDriver(driver)" class="px-3 py-1.5 text-sm bg-green-500 text-white rounded hover:bg-green-600 font-medium">승인</button>
              <button @click="holdDriver(driver)" class="px-3 py-1.5 text-sm bg-yellow-400 text-white rounded hover:bg-yellow-500 font-medium">보류</button>
              <button @click="rejectDriver(driver)" class="px-3 py-1.5 text-sm bg-red-500 text-white rounded hover:bg-red-600 font-medium">반려</button>
              <button @click="openDriverDetail(driver)" class="px-3 py-1.5 text-sm bg-white border border-gray-300 text-gray-600 rounded hover:bg-gray-50">상세</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Approved drivers -->
      <div>
        <h2 class="text-base font-semibold text-gray-700 mb-3">승인된 드라이버</h2>
        <div class="bg-white rounded-lg shadow-sm overflow-x-auto">
          <table class="w-full text-sm min-w-max">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">이름</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">연락처</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">차량 / 번호판</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">면허번호</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">완료</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">평점</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">미정산</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">상태</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="driver in approvedDrivers" :key="driver.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-800">{{ driver.name }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ driver.phone }}<br/>{{ driver.email }}</td>
                <td class="px-4 py-3 text-gray-700 text-xs">{{ driver.vehicle }}<br/><span class="text-gray-400">{{ driver.plate }}</span></td>
                <td class="px-4 py-3 text-gray-500 font-mono text-xs">{{ driver.license }}</td>
                <td class="px-4 py-3 text-gray-700">{{ driver.completed }}건</td>
                <td class="px-4 py-3">
                  <span class="text-yellow-500">★</span>
                  <span class="ml-1 text-gray-700">{{ driver.rating || '–' }}</span>
                </td>
                <td class="px-4 py-3 font-semibold text-green-700">${{ driver.payout_pending.toFixed(2) }}</td>
                <td class="px-4 py-3">
                  <span :class="driverStatusBadge(driver.status)">{{ driverStatusLabel(driver.status) }}</span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex gap-1 flex-wrap">
                    <button @click="openDriverDetail(driver)" class="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200">상세</button>
                    <button v-if="driver.status === 'active'" @click="suspendDriver(driver)" class="px-2 py-1 text-xs bg-orange-100 text-orange-600 rounded hover:bg-orange-200">정지</button>
                    <button v-if="driver.status === 'suspended'" @click="activateDriver(driver)" class="px-2 py-1 text-xs bg-green-100 text-green-600 rounded hover:bg-green-200">활성화</button>
                  </div>
                </td>
              </tr>
              <tr v-if="approvedDrivers.length === 0">
                <td colspan="9" class="px-4 py-10 text-center text-gray-400">승인된 드라이버가 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== TAB 3: 정산 관리 ===== -->
    <div v-if="activeTab === 'payouts'">
      <!-- Summary cards -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow-sm p-5 border-l-4 border-orange-400">
          <div class="text-xs text-gray-500 mb-1">미정산 합계</div>
          <div class="text-2xl font-bold text-gray-800">${{ totalPending.toFixed(2) }}</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-5 border-l-4 border-green-400">
          <div class="text-xs text-gray-500 mb-1">이달 수수료 수익 (20%)</div>
          <div class="text-2xl font-bold text-green-600">${{ monthlyCommission.toFixed(2) }}</div>
        </div>
        <div class="bg-white rounded-lg shadow-sm p-5 border-l-4 border-blue-400">
          <div class="text-xs text-gray-500 mb-1">이달 완료 라이드</div>
          <div class="text-2xl font-bold text-blue-600">{{ completedThisMonth }}건</div>
        </div>
      </div>

      <!-- Pending payouts -->
      <div class="mb-6">
        <h2 class="text-base font-semibold text-gray-700 mb-3">미정산 드라이버</h2>
        <div class="bg-white rounded-lg shadow-sm overflow-x-auto">
          <table class="w-full text-sm min-w-max">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">드라이버</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">완료 건수</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">총 수령액</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">수수료 (20%)</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">정산 금액</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">ACH 계좌</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">관리</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="driver in driversWithPending" :key="'payout-'+driver.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 font-medium text-gray-800">{{ driver.name }}</td>
                <td class="px-4 py-3 text-gray-600">{{ driver.completed }}건</td>
                <td class="px-4 py-3 text-gray-700">${{ (driver.payout_pending / 0.8).toFixed(2) }}</td>
                <td class="px-4 py-3 text-red-600">-${{ (driver.payout_pending / 0.8 * 0.2).toFixed(2) }}</td>
                <td class="px-4 py-3 font-semibold text-green-700">${{ driver.payout_pending.toFixed(2) }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ driver.ach_bank || '미등록' }} {{ driver.ach_account || '' }}</td>
                <td class="px-4 py-3">
                  <button
                    @click="processPayout(driver)"
                    class="px-3 py-1.5 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 font-medium"
                  >정산하기</button>
                </td>
              </tr>
              <tr v-if="driversWithPending.length === 0">
                <td colspan="7" class="px-4 py-10 text-center text-gray-400">미정산 내역이 없습니다.</td>
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
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">드라이버</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">금액</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">방법</th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500">상태</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="payout in payoutHistory" :key="payout.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 text-gray-500">{{ payout.date }}</td>
                <td class="px-4 py-3 font-medium text-gray-800">{{ payout.driver }}</td>
                <td class="px-4 py-3 font-semibold text-gray-800">${{ payout.amount.toFixed(2) }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ payout.method }}</td>
                <td class="px-4 py-3">
                  <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">완료</span>
                </td>
              </tr>
              <tr v-if="payoutHistory.length === 0">
                <td colspan="5" class="px-4 py-10 text-center text-gray-400">정산 내역이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== TAB 4: 요금/설정 ===== -->
    <div v-if="activeTab === 'settings'">
      <div class="max-w-2xl space-y-6">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h2 class="text-base font-semibold text-gray-700 mb-5">요금 설정</h2>
          <div class="grid grid-cols-2 gap-5">
            <div>
              <label class="text-sm text-gray-600 mb-1 block">기본요금 ($)</label>
              <input type="number" v-model="rideSettings.base_fare" step="0.5" min="0"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">최소요금 ($)</label>
              <input type="number" v-model="rideSettings.min_fare" step="0.5" min="0"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">km당 요금 ($)</label>
              <input type="number" v-model="rideSettings.per_km" step="0.1" min="0"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">분당 요금 ($)</label>
              <input type="number" v-model="rideSettings.per_min" step="0.05" min="0"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">취소수수료 ($)</label>
              <input type="number" v-model="rideSettings.cancel_fee" step="0.5" min="0"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <h2 class="text-base font-semibold text-gray-700 mb-5">수수료 / 정산 설정</h2>
          <div class="grid grid-cols-2 gap-5">
            <div>
              <label class="text-sm text-gray-600 mb-1 block">수수료율 (%)</label>
              <input type="number" v-model="rideSettings.commission_rate" step="1" min="0" max="100"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300" />
              <p class="text-xs text-gray-400 mt-1">드라이버 정산 시 차감되는 비율</p>
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">정산 주기</label>
              <select v-model="rideSettings.payout_cycle"
                class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300">
                <option value="instant">즉시</option>
                <option value="weekly">주간</option>
                <option value="monthly">월간</option>
              </select>
            </div>
          </div>
        </div>

        <div class="flex justify-end items-center gap-4">
          <span v-if="settingsSaved" class="text-sm text-green-600 font-medium">저장되었습니다.</span>
          <button @click="saveSettings" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium">저장</button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL: 라이드 승인 ===== -->
    <div v-if="showApproveModal" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div class="px-6 py-4 border-b border-gray-100">
          <h3 class="text-lg font-bold text-gray-800">라이드 승인</h3>
        </div>
        <div class="p-6 space-y-4">
          <div class="p-4 bg-gray-50 rounded-lg text-sm space-y-1.5">
            <div><span class="text-gray-400 mr-2">승객</span><span class="font-medium">{{ selectedRide?.passenger }}</span></div>
            <div><span class="text-gray-400 mr-2">구간</span><span>{{ selectedRide?.from }} → {{ selectedRide?.to }}</span></div>
            <div><span class="text-gray-400 mr-2">요금</span><span class="font-semibold text-green-700">${{ selectedRide?.fare?.toFixed(2) }}</span></div>
          </div>
          <div>
            <label class="text-sm text-gray-600 mb-1.5 block font-medium">드라이버 배정 (선택사항)</label>
            <select v-model="approveDriverId" class="w-full border border-gray-300 rounded px-3 py-2 text-sm">
              <option value="">나중에 배정</option>
              <option v-for="d in approvedDrivers.filter(d => d.status === 'active')" :key="d.id" :value="d.id">
                {{ d.name }} – {{ d.vehicle }}
              </option>
            </select>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end gap-3">
          <button @click="showApproveModal = false" class="px-4 py-2 text-sm border border-gray-300 rounded text-gray-600 hover:bg-gray-50">취소</button>
          <button @click="confirmApproveRide" class="px-4 py-2 text-sm bg-green-500 text-white rounded hover:bg-green-600 font-medium">승인 확정</button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL: 라이드 상세 ===== -->
    <div v-if="showRideDetailModal" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center px-6 py-4 border-b border-gray-100 sticky top-0 bg-white">
          <h3 class="text-lg font-bold text-gray-800">라이드 상세 #{{ selectedRide?.id }}</h3>
          <button @click="showRideDetailModal = false" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div v-if="selectedRide" class="p-6 space-y-4 text-sm">
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-xs text-gray-400 mb-1">승객</div>
              <div class="font-semibold">{{ selectedRide.passenger }}</div>
              <div class="text-gray-500">{{ selectedRide.passenger_phone }}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-xs text-gray-400 mb-1">드라이버</div>
              <div class="font-semibold">{{ selectedRide.driver || '미배정' }}</div>
              <div class="text-gray-500">{{ selectedRide.driver_phone || '' }}</div>
            </div>
          </div>
          <div class="bg-gray-50 p-3 rounded-lg">
            <div class="text-xs text-gray-400 mb-2">이동 구간</div>
            <div class="font-medium text-gray-800">{{ selectedRide.from }}</div>
            <div class="text-gray-400 text-center my-1">↓</div>
            <div class="font-medium text-gray-800">{{ selectedRide.to }}</div>
          </div>
          <div class="bg-gray-50 p-3 rounded-lg">
            <div class="text-xs text-gray-400 mb-2">타임라인</div>
            <div v-for="(event, idx) in (selectedRide.timeline || [])" :key="idx" class="flex gap-3 mb-1.5 last:mb-0">
              <span class="text-gray-400 text-xs w-36 shrink-0">{{ event.time }}</span>
              <span class="text-gray-700">{{ event.desc }}</span>
            </div>
          </div>
          <div class="bg-gray-50 p-3 rounded-lg">
            <div class="text-xs text-gray-400 mb-2">결제 정보</div>
            <div class="space-y-1">
              <div class="flex justify-between">
                <span class="text-gray-500">요금</span>
                <span class="font-semibold">${{ selectedRide.fare?.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">결제 방법</span>
                <span>{{ selectedRide.payment_method || '카드결제' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500">결제 상태</span>
                <span :class="paymentBadge(selectedRide.payment_status)">{{ paymentLabel(selectedRide.payment_status) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end">
          <button @click="showRideDetailModal = false" class="px-4 py-2 text-sm bg-gray-100 text-gray-600 rounded hover:bg-gray-200">닫기</button>
        </div>
      </div>
    </div>

    <!-- ===== MODAL: 드라이버 상세 ===== -->
    <div v-if="showDriverDetailModal" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center px-6 py-4 border-b border-gray-100 sticky top-0 bg-white">
          <h3 class="text-lg font-bold text-gray-800">드라이버 상세</h3>
          <button @click="showDriverDetailModal = false" class="text-gray-400 hover:text-gray-600 text-2xl leading-none">&times;</button>
        </div>
        <div v-if="selectedDriver" class="p-6 space-y-4 text-sm">
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-xs text-gray-400 mb-1">이름</div>
              <div class="font-semibold">{{ selectedDriver.name }}</div>
              <span :class="driverStatusBadge(selectedDriver.status)" class="mt-1 inline-block">{{ driverStatusLabel(selectedDriver.status) }}</span>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-xs text-gray-400 mb-1">연락처</div>
              <div class="font-medium">{{ selectedDriver.phone }}</div>
              <div class="text-gray-500">{{ selectedDriver.email }}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-xs text-gray-400 mb-1">차량 정보</div>
              <div class="font-medium">{{ selectedDriver.vehicle }}</div>
              <div class="text-gray-500">번호판: {{ selectedDriver.plate }}</div>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg">
              <div class="text-xs text-gray-400 mb-1">면허번호</div>
              <div class="font-mono font-medium">{{ selectedDriver.license }}</div>
              <div class="text-gray-400 mt-1">완료: {{ selectedDriver.completed }}건 / 평점: {{ selectedDriver.rating || '–' }}</div>
            </div>
          </div>
          <div v-if="selectedDriver.ach_bank" class="bg-blue-50 border border-blue-100 p-4 rounded-lg">
            <div class="text-xs text-blue-500 font-semibold mb-3">ACH 정산 계좌</div>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div><span class="text-gray-400">은행명:</span> <span class="font-medium">{{ selectedDriver.ach_bank }}</span></div>
              <div><span class="text-gray-400">계좌번호:</span> <span class="font-mono">{{ selectedDriver.ach_account }}</span></div>
              <div class="col-span-2"><span class="text-gray-400">라우팅번호:</span> <span class="font-mono">{{ selectedDriver.ach_routing }}</span></div>
            </div>
          </div>
          <div v-else class="bg-gray-50 p-3 rounded-lg text-gray-400 text-center">ACH 계좌 정보가 등록되지 않았습니다.</div>

          <div>
            <div class="text-xs text-gray-500 font-semibold mb-2">완료된 라이드</div>
            <div v-if="getDriverRides(selectedDriver).length === 0" class="text-gray-400 text-sm">완료된 라이드가 없습니다.</div>
            <div v-else class="space-y-1.5 max-h-40 overflow-y-auto">
              <div
                v-for="ride in getDriverRides(selectedDriver)"
                :key="ride.id"
                class="flex justify-between bg-gray-50 px-3 py-2 rounded text-xs"
              >
                <span class="text-gray-600">{{ ride.from }} → {{ ride.to }}</span>
                <span class="font-semibold text-green-700 ml-2">${{ ride.fare.toFixed(2) }}</span>
                <span class="text-gray-400 ml-2">{{ ride.created_at }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-gray-100 flex justify-end">
          <button @click="showDriverDetailModal = false" class="px-4 py-2 text-sm bg-gray-100 text-gray-600 rounded hover:bg-gray-200">닫기</button>
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
import { ref, computed } from 'vue'

// ─── Tabs ────────────────────────────────────────────────
const activeTab = ref('rides')

const pendingRideCount = computed(() => rides.value.filter(r => r.status === 'pending').length)
const pendingDriverCount = computed(() => drivers.value.filter(d => d.status === 'pending_approval').length)

const tabs = computed(() => [
  { key: 'rides', label: '라이드 요청 관리', badge: pendingRideCount.value || null },
  { key: 'drivers', label: '드라이버 관리', badge: pendingDriverCount.value || null },
  { key: 'payouts', label: '정산 관리', badge: null },
  { key: 'settings', label: '요금/설정', badge: null },
])

// ─── Dummy Rides ─────────────────────────────────────────
const rides = ref([
  {
    id: 1001, from: '1234 Olympic Blvd, LA', to: '5678 Wilshire Blvd, LA',
    passenger: '김미래', passenger_phone: '213-555-0011',
    driver: '이철수', driver_phone: '213-555-1001',
    fare: 24.50, payment_status: 'paid', status: 'completed', created_at: '2026-03-20',
    payment_method: '카드결제',
    timeline: [
      { time: '2026-03-20 09:00', desc: '라이드 요청' },
      { time: '2026-03-20 09:05', desc: '관리자 승인' },
      { time: '2026-03-20 09:10', desc: '드라이버 배정 (이철수)' },
      { time: '2026-03-20 09:30', desc: '라이드 완료' },
    ],
  },
  {
    id: 1002, from: '9000 Koreatown Ave, LA', to: '1000 Hollywood Blvd, LA',
    passenger: '박준혁', passenger_phone: '213-555-0022',
    driver: '최강호', driver_phone: '213-555-1002',
    fare: 38.00, payment_status: 'paid', status: 'completed', created_at: '2026-03-21',
    payment_method: '카드결제',
    timeline: [
      { time: '2026-03-21 14:00', desc: '라이드 요청' },
      { time: '2026-03-21 14:08', desc: '관리자 승인' },
      { time: '2026-03-21 15:00', desc: '라이드 완료' },
    ],
  },
  {
    id: 1003, from: '4500 Vermont Ave, LA', to: '2200 Western Ave, LA',
    passenger: '이소연', passenger_phone: '213-555-0033',
    driver: '이철수', driver_phone: '213-555-1001',
    fare: 18.00, payment_status: 'paid', status: 'in_progress', created_at: '2026-03-25',
    payment_method: '카드결제',
    timeline: [
      { time: '2026-03-25 10:00', desc: '라이드 요청' },
      { time: '2026-03-25 10:05', desc: '관리자 승인' },
      { time: '2026-03-25 10:20', desc: '라이드 시작' },
    ],
  },
  {
    id: 1004, from: '3300 Normandie Ave, LA', to: '8800 Sunset Blvd, LA',
    passenger: '한수정', passenger_phone: '213-555-0044',
    driver: null, driver_phone: null,
    fare: 52.00, payment_status: 'pending', status: 'pending', created_at: '2026-03-27',
    payment_method: '카드결제',
    timeline: [{ time: '2026-03-27 08:30', desc: '라이드 요청' }],
  },
  {
    id: 1005, from: '6700 Crenshaw Blvd, LA', to: 'LAX Terminal B',
    passenger: '최영철', passenger_phone: '213-555-0055',
    driver: null, driver_phone: null,
    fare: 65.00, payment_status: 'pending', status: 'pending', created_at: '2026-03-28',
    payment_method: '카드결제',
    timeline: [{ time: '2026-03-28 06:00', desc: '라이드 요청' }],
  },
  {
    id: 1006, from: '1100 S Grand Ave, LA', to: '4400 Figueroa St, LA',
    passenger: '윤지민', passenger_phone: '213-555-0066',
    driver: '최강호', driver_phone: '213-555-1002',
    fare: 21.50, payment_status: 'paid', status: 'approved', created_at: '2026-03-28',
    payment_method: '카드결제',
    timeline: [
      { time: '2026-03-28 11:00', desc: '라이드 요청' },
      { time: '2026-03-28 11:10', desc: '관리자 승인' },
      { time: '2026-03-28 11:15', desc: '드라이버 배정 (최강호)' },
    ],
  },
  {
    id: 1007, from: 'Koreatown Plaza, LA', to: 'Santa Monica Pier',
    passenger: '정대한', passenger_phone: '213-555-0077',
    driver: null, driver_phone: null,
    fare: 47.00, payment_status: 'refunded', status: 'cancelled', created_at: '2026-03-22',
    payment_method: '카드결제',
    timeline: [
      { time: '2026-03-22 13:00', desc: '라이드 요청' },
      { time: '2026-03-22 14:00', desc: '고객 취소' },
    ],
  },
])

// ─── Dummy Drivers ───────────────────────────────────────
const drivers = ref([
  { id: 1, name: '이철수', phone: '213-555-1001', email: 'cheolsu@gmail.com', vehicle: 'Toyota Camry 2023', plate: '8ABC123', license: 'DL98765432', status: 'active', completed: 15, rating: 4.8, ach_bank: 'Wells Fargo', ach_account: '****4567', ach_routing: '121000248', payout_pending: 416.00, approved_at: '2025-06-01' },
  { id: 2, name: '최강호', phone: '213-555-1002', email: 'kangho@gmail.com', vehicle: 'Honda Civic 2024', plate: '9DEF456', license: 'DL87654321', status: 'active', completed: 22, rating: 4.9, ach_bank: 'Bank of America', ach_account: '****7890', ach_routing: '026009593', payout_pending: 624.00, approved_at: '2025-07-15' },
  { id: 3, name: '한드라이브', phone: '213-555-1003', email: 'drive@gmail.com', vehicle: 'Hyundai Sonata 2025', plate: '7GHI789', license: 'DL76543210', status: 'pending_approval', completed: 0, rating: 0, ach_bank: 'Chase', ach_account: '****2345', ach_routing: '021000021', payout_pending: 0, applied_at: '2026-03-27' },
  { id: 4, name: '박라이드', phone: '213-555-1004', email: 'ride@gmail.com', vehicle: 'Kia EV6 2024', plate: '6JKL012', license: 'DL65432109', status: 'pending_approval', completed: 0, rating: 0, payout_pending: 0, applied_at: '2026-03-28' },
])

// ─── Payout History ──────────────────────────────────────
const payoutHistory = ref([
  { id: 1, date: '2026-03-01', driver: '이철수', amount: 320.00, method: 'ACH (Wells Fargo ****4567)' },
  { id: 2, date: '2026-03-10', driver: '최강호', amount: 480.00, method: 'ACH (Bank of America ****7890)' },
])

// ─── Computed ────────────────────────────────────────────
const pendingDrivers = computed(() => drivers.value.filter(d => d.status === 'pending_approval'))
const approvedDrivers = computed(() => drivers.value.filter(d => d.status !== 'pending_approval' && d.status !== 'rejected'))
const driversWithPending = computed(() => approvedDrivers.value.filter(d => d.payout_pending > 0))

const rideFilter = ref({ status: '', date: '' })
const filteredRides = computed(() => {
  return rides.value.filter(r => {
    if (rideFilter.value.status && r.status !== rideFilter.value.status) return false
    if (rideFilter.value.date && !r.created_at.startsWith(rideFilter.value.date)) return false
    return true
  })
})

const totalPending = computed(() => drivers.value.reduce((s, d) => s + (d.payout_pending || 0), 0))
const monthlyCommission = computed(() => rides.value.filter(r => r.status === 'completed').reduce((s, r) => s + r.fare * 0.2, 0))
const completedThisMonth = computed(() => rides.value.filter(r => r.status === 'completed').length)

// ─── Settings ────────────────────────────────────────────
const rideSettings = ref({
  base_fare: 5.00,
  min_fare: 8.00,
  per_km: 1.50,
  per_min: 0.25,
  cancel_fee: 5.00,
  commission_rate: 20,
  payout_cycle: 'weekly',
})
const settingsSaved = ref(false)

const saveSettings = () => {
  // API: POST /api/admin/ride-settings
  settingsSaved.value = true
  showToast('success', '설정이 저장되었습니다.')
  setTimeout(() => { settingsSaved.value = false }, 3000)
}

// ─── Modals / State ──────────────────────────────────────
const showApproveModal = ref(false)
const showRideDetailModal = ref(false)
const showDriverDetailModal = ref(false)
const selectedRide = ref(null)
const selectedDriver = ref(null)
const approveDriverId = ref('')

const openApproveRide = (ride) => {
  selectedRide.value = ride
  approveDriverId.value = ''
  showApproveModal.value = true
}

const confirmApproveRide = () => {
  if (!selectedRide.value) return
  const idx = rides.value.findIndex(r => r.id === selectedRide.value.id)
  if (idx !== -1) {
    rides.value[idx].status = 'approved'
    if (approveDriverId.value) {
      const d = drivers.value.find(d => d.id === parseInt(approveDriverId.value))
      if (d) {
        rides.value[idx].driver = d.name
        rides.value[idx].driver_phone = d.phone
      }
    }
  }
  showApproveModal.value = false
  showToast('success', '라이드가 승인되었습니다.')
  // API: POST /api/admin/rides/{id}/approve
}

const rejectRide = (ride) => {
  const idx = rides.value.findIndex(r => r.id === ride.id)
  if (idx !== -1) rides.value[idx].status = 'cancelled'
  showToast('success', '라이드가 반려되었습니다.')
  // API: POST /api/admin/rides/{id}/reject
}

const openRideDetail = (ride) => {
  selectedRide.value = ride
  showRideDetailModal.value = true
}

const openDriverDetail = (driver) => {
  selectedDriver.value = driver
  showDriverDetailModal.value = true
}

const getDriverRides = (driver) => rides.value.filter(r => r.driver === driver.name && r.status === 'completed')

const approveDriver = (driver) => {
  const idx = drivers.value.findIndex(d => d.id === driver.id)
  if (idx !== -1) drivers.value[idx].status = 'active'
  showToast('success', `${driver.name} 드라이버가 승인되었습니다.`)
  // API: POST /api/admin/drivers/{id}/approve
}

const holdDriver = (driver) => {
  showToast('success', `${driver.name} 드라이버 심사가 보류되었습니다.`)
}

const rejectDriver = (driver) => {
  const idx = drivers.value.findIndex(d => d.id === driver.id)
  if (idx !== -1) drivers.value[idx].status = 'rejected'
  showToast('success', `${driver.name} 드라이버가 반려되었습니다.`)
  // API: POST /api/admin/drivers/{id}/reject
}

const suspendDriver = (driver) => {
  const idx = drivers.value.findIndex(d => d.id === driver.id)
  if (idx !== -1) drivers.value[idx].status = 'suspended'
  showToast('success', `${driver.name} 드라이버가 정지되었습니다.`)
}

const activateDriver = (driver) => {
  const idx = drivers.value.findIndex(d => d.id === driver.id)
  if (idx !== -1) drivers.value[idx].status = 'active'
  showToast('success', `${driver.name} 드라이버가 활성화되었습니다.`)
}

const processPayout = (driver) => {
  const amount = driver.payout_pending
  payoutHistory.value.unshift({
    id: Date.now(),
    date: new Date().toISOString().split('T')[0],
    driver: driver.name,
    amount,
    method: `ACH (${driver.ach_bank || 'N/A'} ${driver.ach_account || ''})`,
  })
  const idx = drivers.value.findIndex(d => d.id === driver.id)
  if (idx !== -1) drivers.value[idx].payout_pending = 0
  showToast('success', `$${amount.toFixed(2)} 정산이 완료되었습니다.`)
  // API: POST /api/admin/drivers/{id}/payout
}

// ─── Helpers ─────────────────────────────────────────────
const rideBadge = (s) => ({
  pending:    'text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700',
  approved:   'text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700',
  in_progress:'text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700',
  completed:  'text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700',
  cancelled:  'text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700',
}[s] || 'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600')

const rideStatusLabel = (s) => ({
  pending: '대기중', approved: '수락됨', in_progress: '진행중', completed: '완료', cancelled: '취소',
}[s] || s)

const paymentBadge = (s) => ({
  paid:     'text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700',
  pending:  'text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700',
  refunded: 'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500',
}[s] || 'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600')

const paymentLabel = (s) => ({ paid: '결제완료', pending: '미결제', refunded: '환불됨' }[s] || s)

const driverStatusBadge = (s) => ({
  active:    'text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-700',
  suspended: 'text-xs px-2 py-0.5 rounded-full bg-red-100 text-red-700',
  vacation:  'text-xs px-2 py-0.5 rounded-full bg-purple-100 text-purple-700',
  rejected:  'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-400',
}[s] || 'text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600')

const driverStatusLabel = (s) => ({
  active: '활성', suspended: '정지', vacation: '휴가중', rejected: '반려',
}[s] || s)

// ─── Toast ────────────────────────────────────────────────
const toast = ref({ show: false, message: '', type: 'success' })
const showToast = (type, message) => {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
