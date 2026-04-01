<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">총 검색횟수</div>
        <div class="text-2xl font-bold text-gray-800">{{ stats.totalSearches.toLocaleString() }}</div>
        <div class="text-xs text-green-500 mt-1">▲ 12% vs 저번달</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">오늘 검색</div>
        <div class="text-2xl font-bold text-blue-600">{{ stats.todaySearches.toLocaleString() }}</div>
        <div class="text-xs text-blue-400 mt-1">현재 진행중</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">AI 사용 비용 (월)</div>
        <div class="text-2xl font-bold text-orange-600">${{ stats.monthlyCost }}</div>
        <div class="text-xs text-orange-400 mt-1">예산의 {{ stats.budgetUsed }}%</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">캐시 히트율</div>
        <div class="text-2xl font-bold text-green-600">{{ stats.cacheHitRate }}%</div>
        <div class="text-xs text-green-400 mt-1">비용 절감 중</div>
      </div>
    </div>

    <!-- 탭 네비게이션 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="flex flex-wrap border-b border-gray-100">
        <button v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          :class="['px-5 py-3 text-sm font-medium transition border-b-2 -mb-px whitespace-nowrap',
            activeTab === tab.key
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700']">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- TAB: 검색 분석 -->
    <template v-if="activeTab === 'analytics'">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- 인기 검색어 Top 20 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 class="font-semibold text-gray-800 mb-4">인기 검색어 Top 20</h3>
          <div class="space-y-2">
            <div v-for="(query, i) in topQueries" :key="query.keyword"
              class="flex items-center gap-3">
              <span :class="['w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0',
                i === 0 ? 'bg-yellow-400 text-white' :
                i === 1 ? 'bg-gray-400 text-white' :
                i === 2 ? 'bg-orange-400 text-white' :
                'bg-gray-100 text-gray-500']">
                {{ i + 1 }}
              </span>
              <div class="flex-1 min-w-0">
                <div class="flex justify-between items-center mb-0.5">
                  <span class="text-sm font-medium text-gray-700 truncate">{{ query.keyword }}</span>
                  <span class="text-xs text-gray-400 ml-2 flex-shrink-0">{{ query.count.toLocaleString() }}회</span>
                </div>
                <!-- CSS 바 차트 -->
                <div class="h-1.5 bg-gray-100 rounded-full">
                  <div class="h-1.5 rounded-full transition-all"
                    :style="{ width: (query.count / topQueries[0].count * 100) + '%' }"
                    :class="i < 3 ? 'bg-blue-500' : 'bg-blue-300'"></div>
                </div>
              </div>
              <span :class="['text-xs flex-shrink-0', query.trend > 0 ? 'text-green-500' : 'text-red-400']">
                {{ query.trend > 0 ? '▲' : '▼' }}{{ Math.abs(query.trend) }}%
              </span>
            </div>
          </div>
        </div>

        <!-- 일별 검색 트렌드 차트 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 class="font-semibold text-gray-800 mb-4">일별 검색 트렌드 (최근 14일)</h3>
          <div class="flex items-end gap-1.5 h-40">
            <div v-for="day in dailyTrend" :key="day.date"
              class="flex-1 flex flex-col items-center gap-1">
              <span class="text-xs text-gray-400" style="font-size:10px">{{ day.count }}</span>
              <div class="w-full rounded-t transition-all bg-blue-400 hover:bg-blue-500"
                :style="{ height: (day.count / maxDailyCount * 120) + 'px' }"></div>
              <span class="text-gray-400 whitespace-nowrap" style="font-size:9px">{{ day.label }}</span>
            </div>
          </div>
          <div class="mt-4 pt-4 border-t border-gray-100 grid grid-cols-3 gap-3 text-center text-xs">
            <div>
              <div class="text-gray-400">일 평균</div>
              <div class="font-semibold text-gray-700 mt-0.5">{{ avgDaily.toLocaleString() }}회</div>
            </div>
            <div>
              <div class="text-gray-400">최고</div>
              <div class="font-semibold text-blue-600 mt-0.5">{{ maxDailyCount.toLocaleString() }}회</div>
            </div>
            <div>
              <div class="text-gray-400">증가율</div>
              <div class="font-semibold text-green-600 mt-0.5">+8.3%</div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- TAB: API 키 관리 -->
    <template v-if="activeTab === 'apikey'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-6">
        <h3 class="font-bold text-gray-800 text-lg">API 키 관리</h3>

        <!-- OpenAI API Key -->
        <div class="border border-gray-100 rounded-xl p-5">
          <div class="flex items-center justify-between mb-4">
            <div>
              <h4 class="font-semibold text-gray-800">OpenAI API Key</h4>
              <p class="text-xs text-gray-400 mt-0.5">AI 검색 기능에 사용되는 OpenAI API 키</p>
            </div>
            <span :class="['text-xs px-3 py-1 rounded-full font-medium',
              apiKeyStatus === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
              {{ apiKeyStatus === 'active' ? '연결됨' : '연결 안됨' }}
            </span>
          </div>
          <div class="flex gap-3">
            <div class="relative flex-1">
              <input :type="showApiKey ? 'text' : 'password'"
                v-model="apiKey"
                placeholder="sk-..."
                class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400 pr-12 font-mono" />
              <button @click="showApiKey = !showApiKey"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-sm">
                {{ showApiKey ? '🙈' : '👁️' }}
              </button>
            </div>
            <button @click="saveApiKey"
              class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2.5 rounded-lg text-sm font-semibold transition whitespace-nowrap">
              저장
            </button>
            <button @click="testApiKey"
              class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2.5 rounded-lg text-sm font-semibold transition whitespace-nowrap">
              연결 테스트
            </button>
          </div>
        </div>

        <!-- 모델 선택 -->
        <div class="border border-gray-100 rounded-xl p-5">
          <h4 class="font-semibold text-gray-800 mb-4">모델 선택</h4>
          <div class="space-y-3">
            <label v-for="model in models" :key="model.id"
              :class="['flex items-center gap-4 p-4 rounded-xl border cursor-pointer transition',
                selectedModel === model.id ? 'border-blue-400 bg-blue-50' : 'border-gray-100 hover:border-gray-200']">
              <input type="radio" :value="model.id" v-model="selectedModel" class="accent-blue-500" />
              <div class="flex-1">
                <div class="font-medium text-gray-800 text-sm">{{ model.name }}</div>
                <div class="text-xs text-gray-400 mt-0.5">{{ model.description }}</div>
              </div>
              <div class="text-right">
                <div class="text-sm font-semibold text-gray-700">${{ model.price }}</div>
                <div class="text-xs text-gray-400">/ 1K tokens</div>
              </div>
            </label>
          </div>
          <button @click="saveModel"
            class="mt-4 bg-blue-500 hover:bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold transition">
            모델 저장
          </button>
        </div>
      </div>
    </template>

    <!-- TAB: 검색 기록 -->
    <template v-if="activeTab === 'history'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 class="font-semibold text-gray-800">검색 기록</h3>
          <div class="flex gap-2">
            <input v-model="historySearch" type="text" placeholder="검색어 필터..."
              class="border border-gray-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400" />
            <button @click="clearHistory"
              class="bg-red-100 hover:bg-red-200 text-red-600 px-3 py-1.5 rounded-lg text-sm font-medium transition">
              기록 초기화
            </button>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-100 bg-gray-50">
                <th class="text-left py-3 px-5 text-xs text-gray-400 font-medium">검색어</th>
                <th class="text-left py-3 px-4 text-xs text-gray-400 font-medium">사용자</th>
                <th class="text-right py-3 px-4 text-xs text-gray-400 font-medium">결과수</th>
                <th class="text-right py-3 px-4 text-xs text-gray-400 font-medium">응답시간</th>
                <th class="text-right py-3 px-4 text-xs text-gray-400 font-medium">캐시</th>
                <th class="text-right py-3 px-5 text-xs text-gray-400 font-medium">날짜</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in filteredHistory" :key="log.id"
                class="border-b border-gray-50 hover:bg-gray-50 transition">
                <td class="py-2.5 px-5">
                  <span class="font-medium text-gray-800">{{ log.query }}</span>
                </td>
                <td class="py-2.5 px-4 text-xs text-gray-500">{{ log.user }}</td>
                <td class="py-2.5 px-4 text-right text-xs text-gray-500">{{ log.results }}개</td>
                <td class="py-2.5 px-4 text-right">
                  <span :class="['text-xs font-medium', log.response_time > 1000 ? 'text-orange-500' : 'text-green-500']">
                    {{ log.response_time }}ms
                  </span>
                </td>
                <td class="py-2.5 px-4 text-right">
                  <span :class="['text-xs px-2 py-0.5 rounded-full', log.cached ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500']">
                    {{ log.cached ? 'HIT' : 'MISS' }}
                  </span>
                </td>
                <td class="py-2.5 px-5 text-right text-xs text-gray-400">{{ formatDateTime(log.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- TAB: 차단 키워드 -->
    <template v-if="activeTab === 'blocked'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="font-bold text-gray-800 text-lg mb-5">차단 키워드 관리</h3>
        <p class="text-sm text-gray-500 mb-5">등록된 키워드가 포함된 검색어는 AI 검색에서 필터링됩니다.</p>

        <!-- 키워드 추가 -->
        <div class="flex gap-3 mb-6">
          <input v-model="newKeyword" type="text" placeholder="차단할 키워드 입력..."
            @keyup.enter="addKeyword"
            class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          <select v-model="newKeywordCategory"
            class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
            <option value="adult">성인/음란</option>
            <option value="violence">폭력/혐오</option>
            <option value="spam">스팸/광고</option>
            <option value="illegal">불법</option>
            <option value="custom">기타</option>
          </select>
          <button @click="addKeyword"
            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap">
            + 차단 추가
          </button>
        </div>

        <!-- 카테고리별 키워드 -->
        <div class="space-y-4">
          <div v-for="(group, cat) in groupedKeywords" :key="cat">
            <div class="flex items-center gap-2 mb-2">
              <span :class="['text-xs px-2.5 py-1 rounded-full font-medium', categoryColors[cat]]">
                {{ categoryLabels[cat] }}
              </span>
              <span class="text-xs text-gray-400">{{ group.length }}개</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <span v-for="kw in group" :key="kw.id"
                class="inline-flex items-center gap-1.5 bg-gray-100 text-gray-700 text-sm px-3 py-1.5 rounded-full">
                {{ kw.keyword }}
                <button @click="removeKeyword(kw)" class="text-gray-400 hover:text-red-500 transition leading-none text-base">&times;</button>
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- TAB: 비용 관리 -->
    <template v-if="activeTab === 'cost'">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <!-- 월별 사용량 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
          <h3 class="font-semibold text-gray-800 mb-4">월별 API 사용 비용</h3>
          <div class="space-y-3">
            <div v-for="month in monthlyCosts" :key="month.month" class="flex items-center gap-3">
              <span class="text-xs text-gray-500 w-16 flex-shrink-0">{{ month.month }}</span>
              <div class="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all flex items-center justify-end pr-2"
                  :class="month.cost > budget.limit * 0.8 ? 'bg-red-400' : 'bg-blue-400'"
                  :style="{ width: Math.min(month.cost / budget.limit * 100, 100) + '%' }">
                </div>
              </div>
              <span class="text-sm font-semibold text-gray-700 w-16 text-right flex-shrink-0">${{ month.cost }}</span>
            </div>
          </div>
        </div>

        <!-- 예산 설정 -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 space-y-5">
          <h3 class="font-semibold text-gray-800">예산 및 알림 설정</h3>

          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">월 예산 한도 ($)</label>
            <div class="flex gap-3">
              <input v-model.number="budget.limit" type="number"
                class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
              <span class="flex items-center text-sm text-gray-500">USD/월</span>
            </div>
          </div>

          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">알림 임계값 (%)</label>
            <input v-model.number="budget.alertThreshold" type="range" min="50" max="95" step="5"
              class="w-full accent-blue-500" />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>50%</span>
              <span class="font-medium text-blue-600">현재: {{ budget.alertThreshold }}% (${{ Math.round(budget.limit * budget.alertThreshold / 100) }})</span>
              <span>95%</span>
            </div>
          </div>

          <!-- 현재 사용 현황 -->
          <div class="bg-gray-50 rounded-xl p-4">
            <div class="flex justify-between text-sm mb-2">
              <span class="text-gray-600">이번 달 사용</span>
              <span class="font-semibold">${{ stats.monthlyCost }} / ${{ budget.limit }}</span>
            </div>
            <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all"
                :class="stats.budgetUsed > budget.alertThreshold ? 'bg-red-400' : 'bg-blue-500'"
                :style="{ width: stats.budgetUsed + '%' }"></div>
            </div>
            <div class="flex justify-between text-xs text-gray-400 mt-1">
              <span>0%</span>
              <span :class="stats.budgetUsed > budget.alertThreshold ? 'text-red-500 font-semibold' : 'text-gray-500'">
                {{ stats.budgetUsed }}% 사용
              </span>
              <span>100%</span>
            </div>
          </div>

          <div class="space-y-3">
            <label class="flex items-center gap-3 cursor-pointer">
              <div class="relative">
                <input type="checkbox" v-model="budget.emailAlert" class="sr-only" />
                <div :class="['w-10 h-5 rounded-full transition', budget.emailAlert ? 'bg-blue-500' : 'bg-gray-300']"></div>
                <div :class="['absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform',
                  budget.emailAlert ? 'translate-x-5' : 'translate-x-0.5']"></div>
              </div>
              <span class="text-sm text-gray-700">임계값 초과 시 이메일 알림</span>
            </label>
            <label class="flex items-center gap-3 cursor-pointer">
              <div class="relative">
                <input type="checkbox" v-model="budget.autoStop" class="sr-only" />
                <div :class="['w-10 h-5 rounded-full transition', budget.autoStop ? 'bg-red-500' : 'bg-gray-300']"></div>
                <div :class="['absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform',
                  budget.autoStop ? 'translate-x-5' : 'translate-x-0.5']"></div>
              </div>
              <span class="text-sm text-gray-700">예산 한도 초과 시 AI 검색 자동 중단</span>
            </label>
          </div>

          <button @click="saveBudget"
            class="w-full bg-blue-500 hover:bg-blue-600 text-white py-2.5 rounded-lg text-sm font-semibold transition">
            설정 저장
          </button>
        </div>
      </div>
    </template>

    <!-- 토스트 -->
    <div v-if="toast.show"
      :class="['fixed bottom-5 right-5 z-50 px-5 py-3 rounded-xl shadow-lg text-white text-sm font-medium',
        toast.type === 'success' ? 'bg-green-500' : 'bg-red-500']">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const tabs = [
  { key: 'analytics', label: '검색 분석' },
  { key: 'apikey', label: 'API 키 관리' },
  { key: 'history', label: '검색 기록' },
  { key: 'blocked', label: '차단 키워드' },
  { key: 'cost', label: '비용 관리' },
]
const activeTab = ref('analytics')

// ─── 통계 ─────────────────────────────────────────
const stats = ref({ totalSearches: 48320, todaySearches: 1243, monthlyCost: 38.20, budgetUsed: 64, cacheHitRate: 72 })

// ─── 인기 검색어 ──────────────────────────────────
const topQueries = ref([
  { keyword: '미국 한인 커뮤니티', count: 1840, trend: 15 },
  { keyword: 'LA 맛집 추천', count: 1520, trend: 8 },
  { keyword: '미국 비자 신청', count: 1280, trend: -3 },
  { keyword: '코리아타운 부동산', count: 980, trend: 22 },
  { keyword: '한국어 학교', count: 840, trend: 5 },
  { keyword: '미국 운전면허', count: 760, trend: -8 },
  { keyword: 'H1B 비자 2026', count: 720, trend: 31 },
  { keyword: '한인 마트 위치', count: 680, trend: 2 },
  { keyword: '미국 세금 신고', count: 640, trend: 45 },
  { keyword: '영주권 신청 방법', count: 580, trend: 12 },
  { keyword: '한국 음식 배달', count: 520, trend: -5 },
  { keyword: '미국 의료보험', count: 490, trend: 7 },
  { keyword: '이민 변호사 추천', count: 450, trend: 18 },
  { keyword: 'OPT 연장 방법', count: 410, trend: 28 },
  { keyword: '한인 교회 정보', count: 380, trend: 3 },
  { keyword: '미국 대학 입시', count: 350, trend: -12 },
  { keyword: '한국 송금 방법', count: 320, trend: 9 },
  { keyword: '그린카드 취득', count: 290, trend: 14 },
  { keyword: '미국 공휴일 2026', count: 260, trend: 55 },
  { keyword: '한인 의사 추천', count: 240, trend: 6 },
])

// ─── 일별 트렌드 ──────────────────────────────────
const dailyTrend = ref([
  { date: '3/15', label: '15', count: 820 }, { date: '3/16', label: '16', count: 950 },
  { date: '3/17', label: '17', count: 1100 }, { date: '3/18', label: '18', count: 980 },
  { date: '3/19', label: '19', count: 760 }, { date: '3/20', label: '20', count: 680 },
  { date: '3/21', label: '21', count: 1050 }, { date: '3/22', label: '22', count: 1180 },
  { date: '3/23', label: '23', count: 1320 }, { date: '3/24', label: '24', count: 1050 },
  { date: '3/25', label: '25', count: 890 }, { date: '3/26', label: '26', count: 780 },
  { date: '3/27', label: '27', count: 1243 }, { date: '3/28', label: '28', count: 1243 },
])

const maxDailyCount = computed(() => Math.max(...dailyTrend.value.map(d => d.count)))
const avgDaily = computed(() => Math.round(dailyTrend.value.reduce((a, b) => a + b.count, 0) / dailyTrend.value.length))

// ─── API 키 ───────────────────────────────────────
const apiKey = ref('sk-••••••••••••••••••••••••••••••••••••••••••••••••')
const showApiKey = ref(false)
const apiKeyStatus = ref('active')

const models = ref([
  { id: 'gpt-4o', name: 'GPT-4o', description: '최신 멀티모달 모델, 가장 뛰어난 성능', price: '0.015' },
  { id: 'gpt-4', name: 'GPT-4', description: '강력한 추론 능력, 높은 정확도', price: '0.030' },
  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: '빠르고 경제적, 일반 검색에 적합', price: '0.002' },
])
const selectedModel = ref('gpt-4o')

// ─── 검색 기록 ────────────────────────────────────
const searchHistory = ref([
  { id: 1, query: 'LA 한인 맛집', user: '김민준', results: 8, response_time: 342, cached: true, created_at: '2026-03-28T09:30:00' },
  { id: 2, query: 'H1B 비자 2026', user: '박서연', results: 12, response_time: 1240, cached: false, created_at: '2026-03-28T09:28:00' },
  { id: 3, query: '미국 운전면허', user: '이하은', results: 6, response_time: 280, cached: true, created_at: '2026-03-28T09:25:00' },
  { id: 4, query: '한국 음식 배달', user: '최지훈', results: 15, response_time: 890, cached: false, created_at: '2026-03-28T09:20:00' },
  { id: 5, query: '미국 세금 신고', user: '정수아', results: 10, response_time: 560, cached: false, created_at: '2026-03-28T09:15:00' },
  { id: 6, query: '코리아타운 부동산', user: '윤채원', results: 7, response_time: 310, cached: true, created_at: '2026-03-28T09:10:00' },
  { id: 7, query: '영주권 신청 방법', user: '한도준', results: 9, response_time: 1050, cached: false, created_at: '2026-03-28T09:05:00' },
  { id: 8, query: 'OPT 연장 방법', user: '임지수', results: 5, response_time: 420, cached: true, created_at: '2026-03-28T09:00:00' },
])
const historySearch = ref('')
const filteredHistory = computed(() => {
  if (!historySearch.value) return searchHistory.value
  return searchHistory.value.filter(h => h.query.includes(historySearch.value) || h.user.includes(historySearch.value))
})

// ─── 차단 키워드 ──────────────────────────────────
const blockedKeywords = ref([
  { id: 1, keyword: '도박', category: 'illegal' }, { id: 2, keyword: '불법', category: 'illegal' },
  { id: 3, keyword: '마약', category: 'illegal' }, { id: 4, keyword: '성인', category: 'adult' },
  { id: 5, keyword: '음란', category: 'adult' }, { id: 6, keyword: '폭력', category: 'violence' },
  { id: 7, keyword: '사기', category: 'spam' }, { id: 8, keyword: '무료 돈', category: 'spam' },
  { id: 9, keyword: '당첨', category: 'spam' },
])
const newKeyword = ref('')
const newKeywordCategory = ref('custom')
const categoryLabels = { adult: '성인/음란', violence: '폭력/혐오', spam: '스팸/광고', illegal: '불법', custom: '기타' }
const categoryColors = {
  adult: 'bg-pink-100 text-pink-700', violence: 'bg-red-100 text-red-700',
  spam: 'bg-orange-100 text-orange-700', illegal: 'bg-red-200 text-red-800', custom: 'bg-gray-100 text-gray-600'
}
const groupedKeywords = computed(() => {
  const groups = {}
  blockedKeywords.value.forEach(kw => {
    if (!groups[kw.category]) groups[kw.category] = []
    groups[kw.category].push(kw)
  })
  return groups
})

// ─── 비용 관리 ────────────────────────────────────
const budget = ref({ limit: 60, alertThreshold: 80, emailAlert: true, autoStop: false })
const monthlyCosts = ref([
  { month: '2025-10', cost: 22.40 }, { month: '2025-11', cost: 28.10 },
  { month: '2025-12', cost: 31.80 }, { month: '2026-01', cost: 29.50 },
  { month: '2026-02', cost: 34.20 }, { month: '2026-03', cost: 38.20 },
])

// ─── 토스트 ───────────────────────────────────────
const toast = ref({ show: false, message: '', type: 'success' })
function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 2500)
}

// ─── 메서드 ───────────────────────────────────────
function formatDateTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function saveApiKey() {
  if (!apiKey.value || apiKey.value.length < 10) { showToast('올바른 API 키를 입력하세요', 'error'); return }
  apiKeyStatus.value = 'active'
  showToast('API 키가 저장되었습니다', 'success')
}

function testApiKey() {
  showToast('API 연결 테스트 중...', 'success')
  setTimeout(() => { showToast('API 연결 성공! (GPT-4o 사용 가능)', 'success') }, 1000)
}

function saveModel() { showToast(`모델이 ${selectedModel.value}로 설정되었습니다`, 'success') }

function clearHistory() {
  if (!confirm('검색 기록을 모두 초기화하시겠습니까?')) return
  searchHistory.value = []
  showToast('검색 기록이 초기화되었습니다', 'success')
}

function addKeyword() {
  if (!newKeyword.value.trim()) { showToast('키워드를 입력하세요', 'error'); return }
  blockedKeywords.value.push({ id: Date.now(), keyword: newKeyword.value.trim(), category: newKeywordCategory.value })
  newKeyword.value = ''
  showToast('차단 키워드가 추가되었습니다', 'success')
}

function removeKeyword(kw) {
  const idx = blockedKeywords.value.findIndex(k => k.id === kw.id)
  if (idx !== -1) blockedKeywords.value.splice(idx, 1)
  showToast('키워드가 제거되었습니다', 'success')
}

function saveBudget() { showToast('예산 설정이 저장되었습니다', 'success') }
</script>
