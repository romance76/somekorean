<template>
  <div class="space-y-5">

    <!-- 통계 카드 -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">전체 뉴스</div>
        <div class="text-2xl font-bold text-gray-800">{{ stats.totalNews.toLocaleString() }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">오늘 등록</div>
        <div class="text-2xl font-bold text-blue-600">{{ stats.todayNews }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">RSS 피드 수</div>
        <div class="text-2xl font-bold text-green-600">{{ stats.feedCount }}</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
        <div class="text-xs text-gray-400 mb-1">좋아요 총수</div>
        <div class="text-2xl font-bold text-purple-600">{{ stats.totalLikes.toLocaleString() }}</div>
      </div>
    </div>

    <!-- 탭 네비게이션 -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-100">
      <div class="flex border-b border-gray-100">
        <button v-for="tab in tabs" :key="tab.key"
          @click="activeTab = tab.key"
          :class="['px-5 py-3 text-sm font-medium transition border-b-2 -mb-px',
            activeTab === tab.key
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700']">
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- TAB: RSS 피드 관리 -->
    <template v-if="activeTab === 'rss'">
      <!-- 새 피드 추가 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <h3 class="font-semibold text-gray-800 mb-4">RSS 피드 추가</h3>
        <div class="flex gap-3">
          <input v-model="newFeed.name" type="text" placeholder="피드 이름 (예: 미주한국일보)"
            class="w-48 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          <input v-model="newFeed.url" type="url" placeholder="RSS URL"
            class="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
          <button @click="addFeed"
            class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap">
            + 피드 추가
          </button>
        </div>
      </div>

      <!-- 피드 목록 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <div class="px-5 py-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-800">등록된 RSS 피드 ({{ feeds.length }}개)</h3>
        </div>
        <div class="divide-y divide-gray-50">
          <div v-for="feed in feeds" :key="feed.id" class="px-5 py-4">
            <div class="flex items-center gap-4">
              <!-- 상태 아이콘 -->
              <div :class="['w-2.5 h-2.5 rounded-full flex-shrink-0',
                feed.status === 'active' ? 'bg-green-400' : 'bg-red-400']"></div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-semibold text-gray-800 text-sm">{{ feed.name }}</span>
                  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium',
                    feed.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600']">
                    {{ feed.status === 'active' ? '활성' : '오류' }}
                  </span>
                </div>
                <div class="text-xs text-gray-400 truncate">{{ feed.url }}</div>
                <div class="text-xs text-gray-400 mt-0.5">
                  마지막 수집: {{ formatDateTime(feed.last_fetch) }} · 총 {{ feed.articles_count.toLocaleString() }}개 기사
                </div>
              </div>

              <div class="flex gap-2 flex-shrink-0">
                <button @click="testFeed(feed)"
                  class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-lg text-xs font-medium transition">
                  테스트
                </button>
                <button @click="fetchFeedNow(feed)"
                  class="bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-1.5 rounded-lg text-xs font-medium transition">
                  즉시 수집
                </button>
                <button @click="toggleFeed(feed)"
                  :class="['px-3 py-1.5 rounded-lg text-xs font-medium transition',
                    feed.status === 'active'
                      ? 'bg-yellow-100 hover:bg-yellow-200 text-yellow-700'
                      : 'bg-green-100 hover:bg-green-200 text-green-700']">
                  {{ feed.status === 'active' ? '비활성화' : '활성화' }}
                </button>
                <button @click="deleteFeed(feed)"
                  class="bg-red-100 hover:bg-red-200 text-red-600 px-3 py-1.5 rounded-lg text-xs font-medium transition">
                  삭제
                </button>
              </div>
            </div>

            <!-- 테스트 미리보기 -->
            <div v-if="testingFeed === feed.id" class="mt-4 bg-gray-50 rounded-xl p-4">
              <div v-if="testLoading" class="text-sm text-gray-400 text-center py-4">
                피드를 불러오는 중...
              </div>
              <div v-else>
                <div class="text-xs font-semibold text-gray-500 mb-3">최신 기사 미리보기 (3개)</div>
                <div class="space-y-3">
                  <div v-for="(article, i) in previewArticles" :key="i"
                    class="bg-white rounded-lg p-3 border border-gray-100">
                    <div class="font-medium text-gray-800 text-sm mb-1">{{ article.title }}</div>
                    <div class="text-xs text-gray-400">{{ article.date }} · {{ feed.name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- TAB: 뉴스 목록 -->
    <template v-if="activeTab === 'list'">
      <!-- 필터/검색 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-wrap gap-3">
        <input v-model="newsSearch" type="text" placeholder="뉴스 제목 검색..."
          class="flex-1 min-w-48 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400" />
        <select v-model="newsCategory"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 카테고리</option>
          <option value="politics">정치</option>
          <option value="economy">경제</option>
          <option value="society">사회</option>
          <option value="culture">문화</option>
          <option value="sports">스포츠</option>
          <option value="tech">IT/기술</option>
        </select>
        <select v-model="newsSource"
          class="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-400">
          <option value="">전체 출처</option>
          <option v-for="f in feeds" :key="f.id" :value="f.name">{{ f.name }}</option>
        </select>
      </div>

      <!-- 뉴스 테이블 -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 bg-gray-50">
              <th class="text-left py-3 px-5 text-xs text-gray-400 font-medium">제목</th>
              <th class="text-left py-3 px-4 text-xs text-gray-400 font-medium">출처</th>
              <th class="text-left py-3 px-4 text-xs text-gray-400 font-medium">카테고리</th>
              <th class="text-left py-3 px-4 text-xs text-gray-400 font-medium">발행일</th>
              <th class="text-right py-3 px-4 text-xs text-gray-400 font-medium">조회수</th>
              <th class="text-right py-3 px-4 text-xs text-gray-400 font-medium">좋아요</th>
              <th class="text-right py-3 px-5 text-xs text-gray-400 font-medium">관리</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="news in filteredNews" :key="news.id"
              class="border-b border-gray-50 hover:bg-gray-50 transition">
              <td class="py-3 px-5">
                <div class="font-medium text-gray-800 line-clamp-1 max-w-xs">{{ news.title }}</div>
              </td>
              <td class="py-3 px-4">
                <span class="text-xs text-gray-500">{{ news.source }}</span>
              </td>
              <td class="py-3 px-4">
                <span :class="['text-xs px-2 py-0.5 rounded-full', categoryBadge(news.category)]">
                  {{ news.category_label }}
                </span>
              </td>
              <td class="py-3 px-4 text-xs text-gray-400">{{ formatDate(news.published_at) }}</td>
              <td class="py-3 px-4 text-right text-xs text-gray-500">{{ news.views.toLocaleString() }}</td>
              <td class="py-3 px-4 text-right text-xs text-gray-500">{{ news.likes }}</td>
              <td class="py-3 px-5 text-right">
                <div class="flex gap-1 justify-end">
                  <a :href="news.url" target="_blank"
                    class="bg-blue-100 text-blue-700 hover:bg-blue-200 px-2 py-1 rounded text-xs transition">보기</a>
                  <button @click="deleteNews(news)"
                    class="bg-red-100 text-red-600 hover:bg-red-200 px-2 py-1 rounded text-xs transition">삭제</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <!-- 페이지네이션 -->
        <div class="px-5 py-3 border-t border-gray-100 flex items-center justify-between">
          <span class="text-xs text-gray-400">총 {{ filteredNews.length }}개</span>
          <div class="flex gap-1">
            <button v-for="p in 5" :key="p"
              :class="['w-7 h-7 rounded text-xs font-medium transition',
                p === currentPage ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
              @click="currentPage = p">{{ p }}</button>
          </div>
        </div>
      </div>
    </template>

    <!-- TAB: 뉴스 직접 입력 -->
    <template v-if="activeTab === 'create'">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 class="font-bold text-gray-800 text-lg mb-5">뉴스 직접 작성</h3>
        <div class="space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">제목 <span class="text-red-500">*</span></label>
            <input v-model="manualNews.title" type="text" placeholder="뉴스 제목"
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-700 mb-1.5 block">카테고리</label>
              <select v-model="manualNews.category"
                class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400">
                <option value="politics">정치</option>
                <option value="economy">경제</option>
                <option value="society">사회</option>
                <option value="culture">문화</option>
                <option value="sports">스포츠</option>
                <option value="tech">IT/기술</option>
              </select>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 mb-1.5 block">출처</label>
              <input v-model="manualNews.source" type="text" placeholder="예: 직접 작성"
                class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            </div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">이미지 URL</label>
            <input v-model="manualNews.image_url" type="url" placeholder="https://..."
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400" />
            <div v-if="manualNews.image_url" class="mt-2">
              <img :src="manualNews.image_url" alt="미리보기"
                class="w-40 h-24 object-cover rounded-lg border border-gray-200"
                @error="manualNews.image_url = ''" />
            </div>
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 mb-1.5 block">내용 <span class="text-red-500">*</span></label>
            <textarea v-model="manualNews.content" rows="8"
              placeholder="뉴스 내용을 입력하세요..."
              class="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-blue-400"></textarea>
          </div>
        </div>
        <div class="flex gap-3 mt-5">
          <button @click="publishNews"
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2.5 rounded-lg text-sm font-semibold transition">
            발행
          </button>
          <button @click="saveDraft"
            class="bg-gray-100 hover:bg-gray-200 text-gray-600 px-6 py-2.5 rounded-lg text-sm font-semibold transition">
            임시저장
          </button>
          <button @click="resetManualNews"
            class="text-gray-400 hover:text-gray-600 px-4 py-2.5 text-sm transition">
            초기화
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
  { key: 'rss', label: 'RSS 피드 관리' },
  { key: 'list', label: '뉴스 목록' },
  { key: 'create', label: '뉴스 직접 입력' },
]
const activeTab = ref('rss')

const stats = ref({ totalNews: 835, todayNews: 42, feedCount: 4, totalLikes: 12840 })

// ─── RSS 피드 ─────────────────────────────────────
const feeds = ref([
  { id: 1, name: '미주한국일보', url: 'https://www.koreatimes.com/rss', status: 'active', last_fetch: '2026-03-28T09:00:00', articles_count: 245 },
  { id: 2, name: '중앙일보', url: 'https://koreajoongangdaily.joins.com/rss', status: 'active', last_fetch: '2026-03-28T08:30:00', articles_count: 180 },
  { id: 3, name: '연합뉴스', url: 'https://www.yna.co.kr/rss/all.xml', status: 'active', last_fetch: '2026-03-28T09:15:00', articles_count: 312 },
  { id: 4, name: 'VOA 한국어', url: 'https://www.voakorea.com/api/zyoqgqgr', status: 'error', last_fetch: '2026-03-27T15:00:00', articles_count: 98 },
])

const newFeed = ref({ name: '', url: '' })
const testingFeed = ref(null)
const testLoading = ref(false)
const previewArticles = ref([])

// ─── 뉴스 더미 데이터 ─────────────────────────────
const newsList = ref([
  { id: 1, title: '트럼프, 한국 자동차 관세 25% 부과 발표…현대·기아 주가 급락', source: '미주한국일보', category: 'economy', category_label: '경제', published_at: '2026-03-28T08:00:00', views: 4820, likes: 132, url: '#' },
  { id: 2, title: 'LA 코리아타운 새 한식 거리 조성 계획 발표', source: '연합뉴스', category: 'society', category_label: '사회', published_at: '2026-03-28T07:30:00', views: 2310, likes: 89, url: '#' },
  { id: 3, title: '미 의회, 한인 커뮤니티 지원 법안 발의', source: '중앙일보', category: 'politics', category_label: '정치', published_at: '2026-03-27T15:00:00', views: 1840, likes: 67, url: '#' },
  { id: 4, title: 'K-팝 그룹 새 앨범, 빌보드 1위 등극', source: '연합뉴스', category: 'culture', category_label: '문화', published_at: '2026-03-27T12:00:00', views: 9230, likes: 445, url: '#' },
  { id: 5, title: '삼성, 미 텍사스 반도체 공장 추가 투자 확정', source: 'VOA 한국어', category: 'tech', category_label: 'IT/기술', published_at: '2026-03-27T10:00:00', views: 3560, likes: 98, url: '#' },
  { id: 6, title: '미 프로야구 개막, 한국계 선수들 활약 기대', source: '미주한국일보', category: 'sports', category_label: '스포츠', published_at: '2026-03-27T09:00:00', views: 2890, likes: 156, url: '#' },
  { id: 7, title: '한국, OECD 교육 지표 아시아 1위 유지', source: '연합뉴스', category: 'society', category_label: '사회', published_at: '2026-03-26T14:00:00', views: 1240, likes: 45, url: '#' },
  { id: 8, title: '달러/원 환율 1,350원대 돌파, 한인 송금 영향은', source: '중앙일보', category: 'economy', category_label: '경제', published_at: '2026-03-26T11:00:00', views: 5670, likes: 201, url: '#' },
])

// ─── 상태 ─────────────────────────────────────────
const newsSearch = ref('')
const newsCategory = ref('')
const newsSource = ref('')
const currentPage = ref(1)
const toast = ref({ show: false, message: '', type: 'success' })
const manualNews = ref({ title: '', category: 'society', source: '', image_url: '', content: '' })

// ─── Computed ─────────────────────────────────────
const filteredNews = computed(() => {
  let list = newsList.value
  if (newsSearch.value) list = list.filter(n => n.title.includes(newsSearch.value))
  if (newsCategory.value) list = list.filter(n => n.category === newsCategory.value)
  if (newsSource.value) list = list.filter(n => n.source === newsSource.value)
  return list
})

// ─── 메서드 ───────────────────────────────────────
function formatDateTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })
}

function categoryBadge(cat) {
  const map = {
    politics: 'bg-red-100 text-red-600',
    economy: 'bg-blue-100 text-blue-600',
    society: 'bg-green-100 text-green-600',
    culture: 'bg-purple-100 text-purple-600',
    sports: 'bg-orange-100 text-orange-600',
    tech: 'bg-cyan-100 text-cyan-600',
  }
  return map[cat] || 'bg-gray-100 text-gray-600'
}

function addFeed() {
  if (!newFeed.value.name || !newFeed.value.url) { showToast('이름과 URL을 모두 입력하세요', 'error'); return }
  feeds.value.push({
    id: Date.now(), name: newFeed.value.name, url: newFeed.value.url,
    status: 'active', last_fetch: new Date().toISOString(), articles_count: 0
  })
  newFeed.value = { name: '', url: '' }
  stats.value.feedCount++
  showToast('RSS 피드가 추가되었습니다', 'success')
}

async function testFeed(feed) {
  if (testingFeed.value === feed.id) { testingFeed.value = null; return }
  testingFeed.value = feed.id
  testLoading.value = true
  await new Promise(r => setTimeout(r, 800))
  testLoading.value = false
  if (feed.status === 'error') {
    previewArticles.value = []
    showToast('피드 연결에 실패했습니다', 'error')
    testingFeed.value = null
    return
  }
  previewArticles.value = [
    { title: `[${feed.name}] 최신 기사 제목 예시 1 - 오늘의 주요 뉴스`, date: '2026-03-28' },
    { title: `[${feed.name}] 최신 기사 제목 예시 2 - 한인 커뮤니티 소식`, date: '2026-03-28' },
    { title: `[${feed.name}] 최신 기사 제목 예시 3 - 미국 한인 관련 뉴스`, date: '2026-03-27' },
  ]
}

async function fetchFeedNow(feed) {
  showToast(`${feed.name} 피드를 수집 중...`, 'success')
  await new Promise(r => setTimeout(r, 600))
  feed.last_fetch = new Date().toISOString()
  feed.articles_count += Math.floor(Math.random() * 10) + 1
  showToast(`${feed.name} 수집 완료`, 'success')
}

function toggleFeed(feed) {
  feed.status = feed.status === 'active' ? 'error' : 'active'
  showToast(`피드가 ${feed.status === 'active' ? '활성화' : '비활성화'}되었습니다`, 'success')
}

function deleteFeed(feed) {
  if (!confirm(`"${feed.name}" 피드를 삭제하시겠습니까?`)) return
  const idx = feeds.value.findIndex(f => f.id === feed.id)
  if (idx !== -1) feeds.value.splice(idx, 1)
  stats.value.feedCount--
  showToast('피드가 삭제되었습니다', 'success')
}

function deleteNews(news) {
  if (!confirm(`"${news.title.slice(0, 20)}..." 뉴스를 삭제하시겠습니까?`)) return
  const idx = newsList.value.findIndex(n => n.id === news.id)
  if (idx !== -1) newsList.value.splice(idx, 1)
  stats.value.totalNews--
  showToast('뉴스가 삭제되었습니다', 'success')
}

function publishNews() {
  if (!manualNews.value.title || !manualNews.value.content) {
    showToast('제목과 내용을 입력하세요', 'error'); return
  }
  const catLabels = { politics: '정치', economy: '경제', society: '사회', culture: '문화', sports: '스포츠', tech: 'IT/기술' }
  newsList.value.unshift({
    id: Date.now(), title: manualNews.value.title,
    source: manualNews.value.source || '직접 작성',
    category: manualNews.value.category, category_label: catLabels[manualNews.value.category],
    published_at: new Date().toISOString(), views: 0, likes: 0, url: '#'
  })
  stats.value.totalNews++
  stats.value.todayNews++
  resetManualNews()
  showToast('뉴스가 발행되었습니다', 'success')
  activeTab.value = 'list'
}

function saveDraft() { showToast('임시저장되었습니다', 'success') }

function resetManualNews() {
  manualNews.value = { title: '', category: 'society', source: '', image_url: '', content: '' }
}

function showToast(message, type = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => { toast.value.show = false }, 2500)
}
</script>
