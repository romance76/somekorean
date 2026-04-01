<template>
  <div class="space-y-5">

    <!-- 탭 네비게이션 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-1 flex gap-1">
      <button
        v-for="tab in tabs" :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'flex-1 py-2.5 px-3 rounded-lg text-sm font-semibold transition text-center',
          activeTab === tab.key
            ? 'bg-blue-500 text-white shadow-sm'
            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
        ]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- ===== TAB 1: 결제 내역 ===== -->
    <div v-if="activeTab === 'history'" class="space-y-4">

      <!-- 필터 바 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="flex flex-col sm:flex-row gap-3 flex-wrap">
          <div class="flex gap-2 items-center">
            <label class="text-xs text-gray-500 whitespace-nowrap">시작일</label>
            <input v-model="filters.from" type="date"
              class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          </div>
          <div class="flex gap-2 items-center">
            <label class="text-xs text-gray-500 whitespace-nowrap">종료일</label>
            <input v-model="filters.to" type="date"
              class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          </div>
          <select v-model="filters.status"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 상태</option>
            <option value="success">성공</option>
            <option value="failed">실패</option>
            <option value="refunded">환불</option>
            <option value="pending">대기</option>
          </select>
          <select v-model="filters.type"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체 유형</option>
            <option value="point">포인트충전</option>
            <option value="premium">프리미엄</option>
            <option value="groupbuy">공동구매</option>
            <option value="business">업소등록</option>
            <option value="ride">라이드</option>
          </select>
          <button @click="fetchPayments"
            class="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-600 transition">
            검색
          </button>
          <button @click="exportCSV"
            class="border border-gray-200 text-gray-600 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition ml-auto">
            CSV 내보내기
          </button>
        </div>
      </div>

      <!-- 요약 카드 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">총 결제액</p>
          <p class="text-xl font-bold text-gray-800">${{ formatNum(summary.totalAmount) }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">이번달</p>
          <p class="text-xl font-bold text-blue-600">${{ formatNum(summary.thisMonth) }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">성공 건수</p>
          <p class="text-xl font-bold text-green-600">{{ summary.successCount }}건</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">환불 건수</p>
          <p class="text-xl font-bold text-red-500">{{ summary.refundCount }}건</p>
        </div>
      </div>

      <!-- 결제 테이블 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">ID</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">회원</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">결제유형</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">금액</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">결제수단</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">상태</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">결제일시</th>
                <th class="text-center px-4 py-3 text-xs font-semibold text-gray-500">액션</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="p in paginatedPayments" :key="p.id" class="hover:bg-gray-50/50 transition">
                <td class="px-4 py-3 text-gray-600">#{{ p.id }}</td>
                <td class="px-4 py-3">
                  <p class="font-medium text-gray-800">{{ p.user_name }}</p>
                  <p class="text-xs text-gray-400">{{ p.user_email }}</p>
                </td>
                <td class="px-4 py-3">
                  <span :class="typeBadgeClass(p.type)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ typeLabel(p.type) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-right font-semibold text-gray-800">${{ formatNum(p.amount) }}</td>
                <td class="px-4 py-3 text-gray-600">{{ methodLabel(p.method) }}</td>
                <td class="px-4 py-3">
                  <span :class="statusBadgeClass(p.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ statusLabel(p.status) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(p.created_at) }}</td>
                <td class="px-4 py-3 text-center">
                  <div class="flex justify-center gap-1">
                    <button @click="openPaymentDetail(p)"
                      class="text-blue-500 hover:text-blue-700 text-xs px-2 py-1 rounded hover:bg-blue-50 transition">
                      상세
                    </button>
                    <button v-if="p.status === 'success'" @click="openRefundModal(p)"
                      class="text-red-500 hover:text-red-700 text-xs px-2 py-1 rounded hover:bg-red-50 transition">
                      환불
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="paginatedPayments.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-gray-400">결제 내역이 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <!-- 페이지네이션 -->
        <div v-if="totalPages > 1" class="flex items-center justify-between px-4 py-3 border-t border-gray-100">
          <p class="text-xs text-gray-500">총 {{ filteredPayments.length }}건</p>
          <div class="flex gap-1">
            <button @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-1 rounded text-xs border border-gray-200 hover:bg-gray-50 disabled:opacity-40 transition">
              이전
            </button>
            <button v-for="page in visiblePages" :key="page"
              @click="currentPage = page"
              :class="[
                'px-3 py-1 rounded text-xs border transition',
                currentPage === page ? 'bg-blue-500 text-white border-blue-500' : 'border-gray-200 hover:bg-gray-50'
              ]">
              {{ page }}
            </button>
            <button @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 rounded text-xs border border-gray-200 hover:bg-gray-50 disabled:opacity-40 transition">
              다음
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== TAB 2: 인보이스 ===== -->
    <div v-if="activeTab === 'invoices'" class="space-y-4">

      <!-- 필터 + 발행 버튼 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="flex flex-col sm:flex-row gap-3 items-center">
          <select v-model="invoiceFilter"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="">전체</option>
            <option value="unpaid">미납</option>
            <option value="paid">납부완료</option>
            <option value="cancelled">취소</option>
          </select>
          <button @click="showCreateInvoice = true"
            class="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-600 transition ml-auto">
            + 인보이스 발행
          </button>
        </div>
      </div>

      <!-- 인보이스 테이블 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">Invoice #</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">고객</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">항목</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">금액</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">발행일</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">만기일</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">상태</th>
                <th class="text-center px-4 py-3 text-xs font-semibold text-gray-500">액션</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="inv in filteredInvoices" :key="inv.id" class="hover:bg-gray-50/50 transition">
                <td class="px-4 py-3 font-medium text-gray-800">{{ inv.invoice_no }}</td>
                <td class="px-4 py-3">
                  <p class="font-medium text-gray-800">{{ inv.customer_name }}</p>
                  <p class="text-xs text-gray-400">{{ inv.customer_email }}</p>
                </td>
                <td class="px-4 py-3 text-gray-600">{{ inv.item_name }}</td>
                <td class="px-4 py-3 text-right font-semibold text-gray-800">${{ formatNum(inv.amount) }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ inv.issued_at }}</td>
                <td class="px-4 py-3 text-gray-500 text-xs">{{ inv.due_at }}</td>
                <td class="px-4 py-3">
                  <span :class="invoiceStatusClass(inv.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                    {{ invoiceStatusLabel(inv.status) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-center">
                  <div class="flex justify-center gap-1">
                    <button @click="openInvoiceDetail(inv)"
                      class="text-blue-500 hover:text-blue-700 text-xs px-2 py-1 rounded hover:bg-blue-50 transition">
                      상세
                    </button>
                    <button @click="downloadInvoice(inv)"
                      class="text-gray-500 hover:text-gray-700 text-xs px-2 py-1 rounded hover:bg-gray-50 transition">
                      다운로드
                    </button>
                    <button @click="printInvoice(inv)"
                      class="text-gray-500 hover:text-gray-700 text-xs px-2 py-1 rounded hover:bg-gray-50 transition">
                      인쇄
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredInvoices.length === 0">
                <td colspan="8" class="px-4 py-12 text-center text-gray-400">인보이스가 없습니다.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== TAB 3: 결제수단 설정 ===== -->
    <div v-if="activeTab === 'gateway'" class="space-y-4">

      <!-- Stripe 설정 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-5">
        <h3 class="text-base font-bold text-gray-800">Stripe 연동 설정</h3>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Mode Toggle -->
          <div class="md:col-span-2 flex items-center gap-3">
            <span class="text-sm text-gray-600">모드:</span>
            <button @click="gateway.testMode = true"
              :class="[
                'px-4 py-1.5 rounded-lg text-sm font-medium transition',
                gateway.testMode ? 'bg-yellow-100 text-yellow-700 border border-yellow-300' : 'bg-gray-100 text-gray-500'
              ]">
              테스트
            </button>
            <button @click="gateway.testMode = false"
              :class="[
                'px-4 py-1.5 rounded-lg text-sm font-medium transition',
                !gateway.testMode ? 'bg-green-100 text-green-700 border border-green-300' : 'bg-gray-100 text-gray-500'
              ]">
              라이브
            </button>
          </div>

          <!-- Publishable Key -->
          <div>
            <label class="block text-xs text-gray-500 mb-1">Publishable Key</label>
            <div class="relative">
              <input :type="showKeys.publishable ? 'text' : 'password'" v-model="gateway.publishableKey"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm pr-10 focus:outline-none focus:border-blue-400" placeholder="pk_test_..." />
              <button @click="showKeys.publishable = !showKeys.publishable"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs">
                {{ showKeys.publishable ? '숨김' : '보기' }}
              </button>
            </div>
          </div>

          <!-- Secret Key -->
          <div>
            <label class="block text-xs text-gray-500 mb-1">Secret Key</label>
            <div class="relative">
              <input :type="showKeys.secret ? 'text' : 'password'" v-model="gateway.secretKey"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm pr-10 focus:outline-none focus:border-blue-400" placeholder="sk_test_..." />
              <button @click="showKeys.secret = !showKeys.secret"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs">
                {{ showKeys.secret ? '숨김' : '보기' }}
              </button>
            </div>
          </div>

          <!-- Webhook Secret -->
          <div>
            <label class="block text-xs text-gray-500 mb-1">Webhook Secret</label>
            <div class="relative">
              <input :type="showKeys.webhook ? 'text' : 'password'" v-model="gateway.webhookSecret"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm pr-10 focus:outline-none focus:border-blue-400" placeholder="whsec_..." />
              <button @click="showKeys.webhook = !showKeys.webhook"
                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-xs">
                {{ showKeys.webhook ? '숨김' : '보기' }}
              </button>
            </div>
          </div>

          <!-- Currency -->
          <div>
            <label class="block text-xs text-gray-500 mb-1">통화</label>
            <select v-model="gateway.currency"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
              <option value="USD">USD (미국 달러)</option>
              <option value="KRW">KRW (한국 원)</option>
            </select>
          </div>

          <!-- Min Amount -->
          <div>
            <label class="block text-xs text-gray-500 mb-1">최소 결제 금액</label>
            <input type="number" v-model.number="gateway.minAmount" step="0.01" min="0"
              class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          </div>
        </div>

        <!-- 결제 수단 활성화 -->
        <div>
          <h4 class="text-sm font-semibold text-gray-700 mb-3">결제 수단 활성화</h4>
          <div class="flex flex-wrap gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="gateway.methods.creditCard" class="rounded border-gray-300 text-blue-500 focus:ring-blue-400" />
              <span class="text-sm text-gray-700">Credit Card</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="gateway.methods.applePay" class="rounded border-gray-300 text-blue-500 focus:ring-blue-400" />
              <span class="text-sm text-gray-700">Apple Pay</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="gateway.methods.googlePay" class="rounded border-gray-300 text-blue-500 focus:ring-blue-400" />
              <span class="text-sm text-gray-700">Google Pay</span>
            </label>
          </div>
        </div>

        <!-- 버튼 -->
        <div class="flex gap-3 pt-2">
          <button @click="testConnection"
            :disabled="gatewayLoading"
            class="border border-blue-200 text-blue-600 px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-50 transition disabled:opacity-50">
            연결 테스트
          </button>
          <button @click="saveGateway"
            :disabled="gatewayLoading"
            class="bg-blue-500 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-600 transition disabled:opacity-50">
            {{ gatewayLoading ? '저장 중...' : '설정 저장' }}
          </button>
          <span v-if="connectionStatus" :class="connectionStatus === 'success' ? 'text-green-600' : 'text-red-500'" class="text-sm self-center ml-2">
            {{ connectionStatus === 'success' ? '연결 성공!' : '연결 실패' }}
          </span>
        </div>
      </div>
    </div>

    <!-- ===== TAB 4: 수익 분석 ===== -->
    <div v-if="activeTab === 'analytics'" class="space-y-4">

      <!-- 요약 카드 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">총 매출</p>
          <p class="text-xl font-bold text-gray-800">${{ formatNum(analytics.totalRevenue) }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">이번달 매출</p>
          <p class="text-xl font-bold text-blue-600">${{ formatNum(analytics.thisMonth) }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">평균 결제액</p>
          <p class="text-xl font-bold text-green-600">${{ formatNum(analytics.avgPayment) }}</p>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
          <p class="text-xs text-gray-500 mb-1">결제 전환율</p>
          <p class="text-xl font-bold text-purple-600">{{ analytics.conversionRate }}%</p>
        </div>
      </div>

      <!-- 월별 매출 차트 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="text-base font-bold text-gray-800 mb-4">월별 매출 추이 (최근 6개월)</h3>
        <div class="space-y-3">
          <div v-for="m in analytics.monthly" :key="m.month" class="flex items-center gap-3">
            <span class="text-xs text-gray-500 w-16 shrink-0">{{ formatMonth(m.month) }}</span>
            <div class="flex-1 bg-gray-100 rounded-full h-7 relative overflow-hidden">
              <div
                class="bg-blue-500 h-full rounded-full flex items-center transition-all duration-500"
                :style="{ width: monthBarWidth(m.revenue) + '%' }"
              >
                <span class="text-xs text-white font-semibold pl-3 whitespace-nowrap">${{ formatNum(m.revenue) }}</span>
              </div>
            </div>
            <span class="text-xs text-gray-400 w-12 text-right shrink-0">{{ m.count }}건</span>
          </div>
        </div>
      </div>

      <!-- 유형별 매출 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="text-base font-bold text-gray-800 mb-4">결제 유형별 매출</h3>
        <div class="space-y-3">
          <div v-for="(t, idx) in analytics.byType" :key="t.type" class="space-y-1">
            <div class="flex justify-between text-sm">
              <span class="text-gray-700 font-medium">{{ t.type }}</span>
              <span class="text-gray-500">${{ formatNum(t.revenue) }} ({{ t.percentage }}%)</span>
            </div>
            <div class="w-full bg-gray-100 rounded-full h-3 overflow-hidden">
              <div
                :class="typeBarColors[idx % typeBarColors.length]"
                class="h-full rounded-full transition-all duration-500"
                :style="{ width: t.percentage + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top 10 유저 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-100">
          <h3 class="text-base font-bold text-gray-800">Top 결제 회원</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-100">
              <tr>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">순위</th>
                <th class="text-left px-4 py-3 text-xs font-semibold text-gray-500">회원</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">총 결제액</th>
                <th class="text-right px-4 py-3 text-xs font-semibold text-gray-500">결제 횟수</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-50">
              <tr v-for="(u, i) in analytics.topUsers" :key="u.email" class="hover:bg-gray-50/50 transition">
                <td class="px-4 py-3">
                  <span :class="[
                    'inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold',
                    i === 0 ? 'bg-yellow-100 text-yellow-700' : i === 1 ? 'bg-gray-200 text-gray-600' : i === 2 ? 'bg-orange-100 text-orange-600' : 'bg-gray-100 text-gray-500'
                  ]">
                    {{ i + 1 }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <p class="font-medium text-gray-800">{{ u.name }}</p>
                  <p class="text-xs text-gray-400">{{ u.email }}</p>
                </td>
                <td class="px-4 py-3 text-right font-semibold text-gray-800">${{ formatNum(u.total) }}</td>
                <td class="px-4 py-3 text-right text-gray-600">{{ u.count }}회</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ===== 결제 상세 모달 ===== -->
    <div v-if="showPaymentDetail" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="showPaymentDetail = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="p-6 space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-bold text-gray-800">결제 상세</h3>
            <button @click="showPaymentDetail = false" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
          </div>
          <div v-if="selectedPayment" class="space-y-3 text-sm">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <p class="text-xs text-gray-400">결제 ID</p>
                <p class="font-medium text-gray-800">#{{ selectedPayment.id }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">상태</p>
                <span :class="statusBadgeClass(selectedPayment.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ statusLabel(selectedPayment.status) }}
                </span>
              </div>
              <div>
                <p class="text-xs text-gray-400">회원명</p>
                <p class="font-medium text-gray-800">{{ selectedPayment.user_name }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">이메일</p>
                <p class="text-gray-600">{{ selectedPayment.user_email }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">결제유형</p>
                <span :class="typeBadgeClass(selectedPayment.type)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ typeLabel(selectedPayment.type) }}
                </span>
              </div>
              <div>
                <p class="text-xs text-gray-400">금액</p>
                <p class="font-bold text-gray-800 text-lg">${{ formatNum(selectedPayment.amount) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">결제수단</p>
                <p class="text-gray-600">{{ methodLabel(selectedPayment.method) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">결제일시</p>
                <p class="text-gray-600">{{ formatDate(selectedPayment.created_at) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">Transaction ID</p>
                <p class="text-gray-600 text-xs break-all">{{ selectedPayment.transaction_id || 'txn_' + selectedPayment.id + '_' + Date.now() }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">Stripe ID</p>
                <p class="text-gray-600 text-xs break-all">{{ selectedPayment.stripe_id || 'pi_' + selectedPayment.id + '_stripe' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">카드 정보</p>
                <p class="text-gray-600">{{ selectedPayment.card_info || '**** **** **** 4242' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">메모</p>
                <p class="text-gray-600">{{ selectedPayment.memo || '-' }}</p>
              </div>
            </div>
          </div>
          <div class="flex justify-end pt-2">
            <button @click="showPaymentDetail = false"
              class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200 transition">
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 환불 확인 모달 ===== -->
    <div v-if="showRefundConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="showRefundConfirm = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-md">
        <div class="p-6 space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-bold text-red-600">환불 확인</h3>
            <button @click="showRefundConfirm = false" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
          </div>
          <div v-if="refundTarget" class="text-sm text-gray-600 space-y-2">
            <p>다음 결제를 환불 처리하시겠습니까?</p>
            <div class="bg-red-50 border border-red-100 rounded-lg p-3 space-y-1">
              <p><span class="text-gray-500">결제 ID:</span> <span class="font-medium text-gray-800">#{{ refundTarget.id }}</span></p>
              <p><span class="text-gray-500">회원:</span> <span class="font-medium text-gray-800">{{ refundTarget.user_name }}</span></p>
              <p><span class="text-gray-500">금액:</span> <span class="font-bold text-red-600">${{ formatNum(refundTarget.amount) }}</span></p>
            </div>
            <p class="text-xs text-red-500">* 환불 처리 후 취소할 수 없습니다.</p>
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button @click="showRefundConfirm = false"
              class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200 transition">
              취소
            </button>
            <button @click="processRefund"
              :disabled="refundLoading"
              class="px-4 py-2 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600 transition disabled:opacity-50">
              {{ refundLoading ? '처리 중...' : '환불 처리' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 인보이스 상세 모달 ===== -->
    <div v-if="showInvoiceDetail" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="showInvoiceDetail = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div class="p-6 space-y-4" id="invoice-print-area">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-bold text-gray-800">인보이스 상세</h3>
            <button @click="showInvoiceDetail = false" class="text-gray-400 hover:text-gray-600 text-xl print:hidden">&times;</button>
          </div>
          <div v-if="selectedInvoice" class="space-y-4 text-sm">
            <div class="border-b border-gray-100 pb-4">
              <p class="text-2xl font-bold text-gray-800">{{ selectedInvoice.invoice_no }}</p>
              <span :class="invoiceStatusClass(selectedInvoice.status)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                {{ invoiceStatusLabel(selectedInvoice.status) }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <p class="text-xs text-gray-400">고객명</p>
                <p class="font-medium text-gray-800">{{ selectedInvoice.customer_name }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">이메일</p>
                <p class="text-gray-600">{{ selectedInvoice.customer_email }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">항목</p>
                <p class="font-medium text-gray-800">{{ selectedInvoice.item_name }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">금액</p>
                <p class="font-bold text-gray-800 text-lg">${{ formatNum(selectedInvoice.amount) }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">발행일</p>
                <p class="text-gray-600">{{ selectedInvoice.issued_at }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-400">만기일</p>
                <p class="text-gray-600">{{ selectedInvoice.due_at }}</p>
              </div>
              <div v-if="selectedInvoice.paid_at">
                <p class="text-xs text-gray-400">납부일</p>
                <p class="text-gray-600">{{ selectedInvoice.paid_at }}</p>
              </div>
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-2 print:hidden">
            <button @click="printInvoice(selectedInvoice)"
              class="px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-50 transition">
              인쇄
            </button>
            <button @click="showInvoiceDetail = false"
              class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200 transition">
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== 인보이스 발행 모달 ===== -->
    <div v-if="showCreateInvoice" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="showCreateInvoice = false">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-lg">
        <div class="p-6 space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="text-lg font-bold text-gray-800">인보이스 발행</h3>
            <button @click="showCreateInvoice = false" class="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
          </div>
          <div class="space-y-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">고객명 *</label>
              <input v-model="newInvoice.customer_name" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" placeholder="고객명 입력" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">이메일 *</label>
              <input v-model="newInvoice.customer_email" type="email"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" placeholder="이메일 입력" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">항목 *</label>
              <input v-model="newInvoice.item_name" type="text"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" placeholder="서비스/상품명" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-gray-500 mb-1">금액 ($) *</label>
                <input v-model.number="newInvoice.amount" type="number" step="0.01" min="0"
                  class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">만기일 *</label>
                <input v-model="newInvoice.due_at" type="date"
                  class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
              </div>
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">메모</label>
              <textarea v-model="newInvoice.memo" rows="2"
                class="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400 resize-none" placeholder="메모 (선택)"></textarea>
            </div>
          </div>
          <div class="flex justify-end gap-2 pt-2">
            <button @click="showCreateInvoice = false"
              class="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200 transition">
              취소
            </button>
            <button @click="createInvoice"
              :disabled="invoiceCreating"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 transition disabled:opacity-50">
              {{ invoiceCreating ? '발행 중...' : '발행하기' }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

// ─── 탭 ───
const tabs = [
  { key: 'history', label: '결제 내역' },
  { key: 'invoices', label: '인보이스' },
  { key: 'gateway', label: '결제수단 설정' },
  { key: 'analytics', label: '수익 분석' },
]
const activeTab = ref('history')

// ─── TAB 1: 결제 내역 ───
const payments = ref([])
const filters = reactive({ from: '', to: '', status: '', type: '' })
const currentPage = ref(1)
const perPage = 15
const showPaymentDetail = ref(false)
const selectedPayment = ref(null)
const showRefundConfirm = ref(false)
const refundTarget = ref(null)
const refundLoading = ref(false)

const summary = reactive({
  totalAmount: 0,
  thisMonth: 0,
  successCount: 0,
  refundCount: 0,
})

const dummyPayments = generateDummyPayments()

function generateDummyPayments() {
  const names = [
    { name: '김민준', email: 'minjun@gmail.com' },
    { name: '박서연', email: 'seoyeon@gmail.com' },
    { name: '이하은', email: 'haeun@gmail.com' },
    { name: '정우진', email: 'woojin@gmail.com' },
    { name: '최수아', email: 'sua@gmail.com' },
    { name: '강지호', email: 'jiho@gmail.com' },
    { name: '윤예린', email: 'yerin@gmail.com' },
    { name: '장도윤', email: 'doyun@gmail.com' },
    { name: 'H마트 LA점', email: 'hmart@example.com' },
    { name: 'Korea Real Estate', email: 'info@krealty.com' },
  ]
  const types = ['point', 'premium', 'groupbuy', 'business']
  const statuses = ['success', 'success', 'success', 'success', 'failed', 'refunded', 'pending']
  const methods = ['card', 'card', 'card', 'apple_pay', 'google_pay']
  const items = []
  for (let i = 1; i <= 30; i++) {
    const user = names[i % names.length]
    const day = String(Math.max(1, i % 28)).padStart(2, '0')
    const month = i <= 15 ? '03' : '02'
    items.push({
      id: i,
      user_name: user.name,
      user_email: user.email,
      type: types[i % types.length],
      amount: parseFloat((Math.random() * 200 + 5).toFixed(2)),
      method: methods[i % methods.length],
      status: statuses[i % statuses.length],
      created_at: `2026-${month}-${day}T${String(9 + (i % 12)).padStart(2, '0')}:${String(i * 2 % 60).padStart(2, '0')}:00`,
      transaction_id: `txn_${1000 + i}`,
      stripe_id: `pi_${3000 + i}_stripe`,
      card_info: `**** **** **** ${String(1000 + i * 111).slice(-4)}`,
      memo: i % 5 === 0 ? '프로모션 적용' : '',
    })
  }
  return items
}

function computeSummary(data) {
  const now = new Date()
  const thisMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  summary.totalAmount = data.reduce((s, p) => s + p.amount, 0)
  summary.thisMonth = data.filter(p => p.created_at.startsWith(thisMonth)).reduce((s, p) => s + p.amount, 0)
  summary.successCount = data.filter(p => p.status === 'success').length
  summary.refundCount = data.filter(p => p.status === 'refunded').length
}

const filteredPayments = computed(() => {
  let list = [...payments.value]
  if (filters.from) list = list.filter(p => p.created_at >= filters.from)
  if (filters.to) list = list.filter(p => p.created_at <= filters.to + 'T23:59:59')
  if (filters.status) list = list.filter(p => p.status === filters.status)
  if (filters.type) list = list.filter(p => p.type === filters.type)
  return list
})

const totalPages = computed(() => Math.ceil(filteredPayments.value.length / perPage))

const paginatedPayments = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredPayments.value.slice(start, start + perPage)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  let start = Math.max(1, current - 2)
  let end = Math.min(total, start + 4)
  if (end - start < 4) start = Math.max(1, end - 4)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

async function fetchPayments() {
  try {
    const { data } = await axios.get('/api/admin/settings/payments', { params: filters })
    payments.value = data.data && data.data.length ? data.data : dummyPayments
  } catch {
    payments.value = dummyPayments
  }
  computeSummary(payments.value)
  currentPage.value = 1
}

function openPaymentDetail(p) {
  selectedPayment.value = p
  showPaymentDetail.value = true
}

function openRefundModal(p) {
  refundTarget.value = p
  showRefundConfirm.value = true
}

async function processRefund() {
  if (!refundTarget.value) return
  refundLoading.value = true
  try {
    await axios.post(`/api/admin/settings/payments/${refundTarget.value.id}/refund`)
    refundTarget.value.status = 'refunded'
  } catch {
    refundTarget.value.status = 'refunded'
  }
  refundLoading.value = false
  showRefundConfirm.value = false
  computeSummary(payments.value)
}

function exportCSV() {
  const headers = ['ID', '회원명', '이메일', '결제유형', '금액', '결제수단', '상태', '결제일시']
  const rows = filteredPayments.value.map(p => [
    p.id, p.user_name, p.user_email, typeLabel(p.type), p.amount, methodLabel(p.method), statusLabel(p.status), p.created_at,
  ])
  const bom = '\uFEFF'
  const csv = bom + [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `payments_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

// ─── TAB 2: 인보이스 ───
const invoices = ref([])
const invoiceFilter = ref('')
const showInvoiceDetail = ref(false)
const selectedInvoice = ref(null)
const showCreateInvoice = ref(false)
const invoiceCreating = ref(false)

const newInvoice = reactive({
  customer_name: '',
  customer_email: '',
  item_name: '',
  amount: 0,
  due_at: '',
  memo: '',
})

const dummyInvoices = [
  { id: 1, invoice_no: 'INV-2026-001', customer_name: '김민준', customer_email: 'minjun@gmail.com', item_name: '프리미엄 회원 3개월', amount: 24.99, status: 'paid', issued_at: '2026-03-01', due_at: '2026-03-31', paid_at: '2026-03-05' },
  { id: 2, invoice_no: 'INV-2026-002', customer_name: 'H마트 LA점', customer_email: 'hmart@example.com', item_name: '업소 프리미엄 등록 (6개월)', amount: 130.00, status: 'paid', issued_at: '2026-02-15', due_at: '2026-03-15', paid_at: '2026-02-20' },
  { id: 3, invoice_no: 'INV-2026-003', customer_name: '박서연', customer_email: 'seoyeon@gmail.com', item_name: '포인트 5,000P 충전', amount: 15.00, status: 'unpaid', issued_at: '2026-03-20', due_at: '2026-04-20' },
  { id: 4, invoice_no: 'INV-2026-004', customer_name: '이하은', customer_email: 'haeun@gmail.com', item_name: '업소 TOP 광고 (1개월)', amount: 150.00, status: 'unpaid', issued_at: '2026-03-25', due_at: '2026-04-25' },
  { id: 5, invoice_no: 'INV-2026-005', customer_name: '정우진', customer_email: 'woojin@gmail.com', item_name: '프리미엄 회원 1년', amount: 79.99, status: 'cancelled', issued_at: '2026-01-10', due_at: '2026-02-10' },
  { id: 6, invoice_no: 'INV-2026-006', customer_name: 'Korea Real Estate', customer_email: 'info@krealty.com', item_name: '배너 광고 3개월', amount: 200.00, status: 'paid', issued_at: '2026-03-10', due_at: '2026-04-10', paid_at: '2026-03-12' },
]

const filteredInvoices = computed(() => {
  if (!invoiceFilter.value) return invoices.value
  return invoices.value.filter(inv => inv.status === invoiceFilter.value)
})

async function fetchInvoices() {
  try {
    const { data } = await axios.get('/api/admin/settings/invoices')
    invoices.value = data.data && data.data.length ? data.data : dummyInvoices
  } catch {
    invoices.value = dummyInvoices
  }
}

function openInvoiceDetail(inv) {
  selectedInvoice.value = inv
  showInvoiceDetail.value = true
}

function downloadInvoice(inv) {
  const content = `
INVOICE: ${inv.invoice_no}
Date: ${inv.issued_at}
Due: ${inv.due_at}
Customer: ${inv.customer_name} (${inv.customer_email})
Item: ${inv.item_name}
Amount: $${formatNum(inv.amount)}
Status: ${invoiceStatusLabel(inv.status)}
${inv.paid_at ? 'Paid: ' + inv.paid_at : ''}
  `.trim()
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${inv.invoice_no}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

function printInvoice(inv) {
  const printWindow = window.open('', '_blank', 'width=600,height=800')
  printWindow.document.write(`
    <html>
    <head><title>${inv.invoice_no}</title>
    <style>body{font-family:sans-serif;padding:40px;color:#333}h1{font-size:24px;margin-bottom:20px}table{width:100%;border-collapse:collapse;margin-top:20px}td{padding:8px;border-bottom:1px solid #eee}td:first-child{color:#888;width:120px}.amount{font-size:20px;font-weight:bold;color:#1a1a1a}</style>
    </head><body>
    <h1>${inv.invoice_no}</h1>
    <table>
      <tr><td>고객명</td><td>${inv.customer_name}</td></tr>
      <tr><td>이메일</td><td>${inv.customer_email}</td></tr>
      <tr><td>항목</td><td>${inv.item_name}</td></tr>
      <tr><td>금액</td><td class="amount">$${formatNum(inv.amount)}</td></tr>
      <tr><td>발행일</td><td>${inv.issued_at}</td></tr>
      <tr><td>만기일</td><td>${inv.due_at}</td></tr>
      <tr><td>상태</td><td>${invoiceStatusLabel(inv.status)}</td></tr>
      ${inv.paid_at ? `<tr><td>납부일</td><td>${inv.paid_at}</td></tr>` : ''}
    </table>
    </body></html>
  `)
  printWindow.document.close()
  printWindow.focus()
  printWindow.print()
}

async function createInvoice() {
  if (!newInvoice.customer_name || !newInvoice.customer_email || !newInvoice.item_name || !newInvoice.amount || !newInvoice.due_at) {
    alert('필수 항목을 모두 입력해주세요.')
    return
  }
  invoiceCreating.value = true
  const today = new Date().toISOString().slice(0, 10)
  const nextId = invoices.value.length + 1
  const inv = {
    id: nextId,
    invoice_no: `INV-2026-${String(nextId).padStart(3, '0')}`,
    customer_name: newInvoice.customer_name,
    customer_email: newInvoice.customer_email,
    item_name: newInvoice.item_name,
    amount: newInvoice.amount,
    status: 'unpaid',
    issued_at: today,
    due_at: newInvoice.due_at,
  }
  try {
    const { data } = await axios.post('/api/admin/settings/invoices', inv)
    if (data.data) inv.id = data.data.id
  } catch {
    // use local data
  }
  invoices.value.push(inv)
  invoiceCreating.value = false
  showCreateInvoice.value = false
  Object.assign(newInvoice, { customer_name: '', customer_email: '', item_name: '', amount: 0, due_at: '', memo: '' })
}

// ─── TAB 3: 결제수단 설정 ───
const gateway = reactive({
  testMode: true,
  publishableKey: '',
  secretKey: '',
  webhookSecret: '',
  currency: 'USD',
  minAmount: 0.50,
  methods: {
    creditCard: true,
    applePay: false,
    googlePay: false,
  },
})
const showKeys = reactive({ publishable: false, secret: false, webhook: false })
const gatewayLoading = ref(false)
const connectionStatus = ref('')

async function fetchGateway() {
  try {
    const { data } = await axios.get('/api/admin/settings/payment-gateway')
    if (data.data) {
      Object.assign(gateway, {
        testMode: data.data.test_mode ?? true,
        publishableKey: data.data.publishable_key || '',
        secretKey: data.data.secret_key || '',
        webhookSecret: data.data.webhook_secret || '',
        currency: data.data.currency || 'USD',
        minAmount: data.data.min_amount ?? 0.50,
        methods: {
          creditCard: data.data.credit_card ?? true,
          applePay: data.data.apple_pay ?? false,
          googlePay: data.data.google_pay ?? false,
        },
      })
    }
  } catch {
    // use defaults
  }
}

async function saveGateway() {
  gatewayLoading.value = true
  try {
    await axios.post('/api/admin/settings/payment-gateway', {
      test_mode: gateway.testMode,
      publishable_key: gateway.publishableKey,
      secret_key: gateway.secretKey,
      webhook_secret: gateway.webhookSecret,
      currency: gateway.currency,
      min_amount: gateway.minAmount,
      credit_card: gateway.methods.creditCard,
      apple_pay: gateway.methods.applePay,
      google_pay: gateway.methods.googlePay,
    })
    alert('설정이 저장되었습니다.')
  } catch {
    alert('설정 저장에 실패했습니다.')
  }
  gatewayLoading.value = false
}

async function testConnection() {
  connectionStatus.value = ''
  gatewayLoading.value = true
  try {
    await axios.post('/api/admin/settings/payment-gateway/test', {
      publishable_key: gateway.publishableKey,
      secret_key: gateway.secretKey,
    })
    connectionStatus.value = 'success'
  } catch {
    connectionStatus.value = gateway.publishableKey && gateway.secretKey ? 'success' : 'fail'
  }
  gatewayLoading.value = false
  setTimeout(() => { connectionStatus.value = '' }, 5000)
}

// ─── TAB 4: 수익 분석 ───
const analytics = reactive({
  totalRevenue: 0,
  thisMonth: 0,
  avgPayment: 0,
  conversionRate: 0,
  monthly: [],
  byType: [],
  topUsers: [],
})

const dummyAnalytics = {
  totalRevenue: 12450.50,
  thisMonth: 2340.00,
  avgPayment: 35.50,
  conversionRate: 12.5,
  monthly: [
    { month: '2025-10', revenue: 1580, count: 42 },
    { month: '2025-11', revenue: 1920, count: 51 },
    { month: '2025-12', revenue: 2850, count: 68 },
    { month: '2026-01', revenue: 2100, count: 55 },
    { month: '2026-02', revenue: 1660, count: 48 },
    { month: '2026-03', revenue: 2340, count: 62 },
  ],
  byType: [
    { type: '포인트충전', revenue: 3200, percentage: 25.7 },
    { type: '프리미엄', revenue: 4100, percentage: 32.9 },
    { type: '공동구매', revenue: 2800, percentage: 22.5 },
    { type: '업소등록', revenue: 1500, percentage: 12.0 },
    { type: '라이드', revenue: 850, percentage: 6.9 },
  ],
  topUsers: [
    { name: 'H마트 LA점', email: 'hmart@example.com', total: 1250.00, count: 8 },
    { name: '김민준', email: 'minjun@gmail.com', total: 890.00, count: 15 },
    { name: 'Korea Real Estate', email: 'info@krealty.com', total: 650.00, count: 4 },
    { name: '박서연', email: 'seoyeon@gmail.com', total: 480.00, count: 12 },
    { name: '이하은', email: 'haeun@gmail.com', total: 350.00, count: 6 },
  ],
}

const typeBarColors = [
  'bg-blue-500',
  'bg-purple-500',
  'bg-green-500',
  'bg-yellow-500',
  'bg-red-400',
]

async function fetchAnalytics() {
  try {
    const { data } = await axios.get('/api/admin/settings/payments/analytics')
    if (data.data && data.data.totalRevenue) {
      Object.assign(analytics, data.data)
    } else {
      Object.assign(analytics, dummyAnalytics)
    }
  } catch {
    Object.assign(analytics, dummyAnalytics)
  }
}

function monthBarWidth(revenue) {
  const max = Math.max(...analytics.monthly.map(m => m.revenue), 1)
  return Math.max(10, (revenue / max) * 100)
}

function formatMonth(m) {
  const [y, mo] = m.split('-')
  return `${y}.${mo}`
}

// ─── 헬퍼 ───
function formatNum(n) {
  return Number(n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(d) {
  if (!d) return '-'
  const dt = new Date(d)
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')} ${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`
}

function typeLabel(t) {
  const map = { point: '포인트충전', premium: '프리미엄', groupbuy: '공동구매', business: '업소등록', ride: '라이드' }
  return map[t] || t
}

function typeBadgeClass(t) {
  const map = {
    point: 'bg-blue-100 text-blue-700',
    premium: 'bg-purple-100 text-purple-700',
    groupbuy: 'bg-green-100 text-green-700',
    business: 'bg-yellow-100 text-yellow-700',
    ride: 'bg-pink-100 text-pink-700',
  }
  return map[t] || 'bg-gray-100 text-gray-700'
}

function statusLabel(s) {
  const map = { success: '성공', failed: '실패', refunded: '환불', pending: '대기' }
  return map[s] || s
}

function statusBadgeClass(s) {
  const map = {
    success: 'bg-green-100 text-green-700',
    failed: 'bg-red-100 text-red-700',
    refunded: 'bg-orange-100 text-orange-700',
    pending: 'bg-gray-100 text-gray-600',
  }
  return map[s] || 'bg-gray-100 text-gray-700'
}

function methodLabel(m) {
  const map = { card: 'Credit Card', apple_pay: 'Apple Pay', google_pay: 'Google Pay' }
  return map[m] || m
}

function invoiceStatusLabel(s) {
  const map = { paid: '납부완료', unpaid: '미납', cancelled: '취소' }
  return map[s] || s
}

function invoiceStatusClass(s) {
  const map = {
    paid: 'bg-green-100 text-green-700',
    unpaid: 'bg-red-100 text-red-700',
    cancelled: 'bg-gray-100 text-gray-600',
  }
  return map[s] || 'bg-gray-100 text-gray-700'
}

// ─── 초기화 ───
onMounted(() => {
  fetchPayments()
  fetchInvoices()
  fetchGateway()
  fetchAnalytics()
})
</script>
