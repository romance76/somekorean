import paramiko, sys, base64
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=120):
    _, out, err = c.exec_command(cmd, timeout=timeout)
    o = out.read().decode('utf-8', errors='replace').strip()
    e = err.read().decode('utf-8', errors='replace').strip()
    return o + (('\nERR:'+e) if e else '')

def write_file(path, content):
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [encoded[i:i+3000] for i in range(0, len(encoded), 3000)]
    ssh('> /tmp/_wf.b64')
    for chunk in chunks:
        ssh("echo -n '{}' >> /tmp/_wf.b64".format(chunk))
    return ssh('base64 -d /tmp/_wf.b64 > {} && rm /tmp/_wf.b64 && echo OK'.format(path))

new_shorts = '''<template>
  <div class="shorts-wrap" @wheel.passive="onWheel">

    <!-- ── 헤더 (safe-area 상단 적용) ── -->
    <div class="fixed left-0 right-0 z-50 flex items-center justify-between px-4 py-2"
         style="top: env(safe-area-inset-top, 0px); padding-top: max(12px, env(safe-area-inset-top, 0px))">
      <h1 class="text-white font-bold text-lg drop-shadow">📱 숏츠</h1>
      <div class="flex gap-2">
        <button @click="shuffleShorts"
          class="text-white/80 bg-white/10 backdrop-blur-sm rounded-full px-3 py-1 text-xs hover:bg-white/20 active:scale-95 transition-transform">
          🔀 셔플
        </button>
        <button @click="showInterests = true"
          class="text-white/80 bg-white/10 backdrop-blur-sm rounded-full px-3 py-1 text-xs hover:bg-white/20 active:scale-95 transition-transform">
          관심설정
        </button>
        <RouterLink v-if="auth.isLoggedIn" to="/shorts/upload"
          class="bg-red-500 text-white rounded-full px-3 py-1 text-xs font-bold hover:bg-red-600 active:scale-95 transition-transform">
          + 공유
        </RouterLink>
      </div>
    </div>

    <!-- ── 슬라이드 컨테이너 ── -->
    <div ref="slider" class="shorts-slider"
      :style="{ transform: `translateY(calc(-${currentIndex * 100}% + ${dragOffset}px))` }">

      <div v-for="(short, idx) in shorts" :key="short.id"
        class="short-slide"
        :class="{ active: currentIndex === idx }">

        <!-- ① 블러 배경 (썸네일) - 어떤 비율의 영상이 와도 빈 공간을 채움 -->
        <div class="bg-blur" aria-hidden="true">
          <img v-if="short.thumbnail" :src="short.thumbnail" alt=""/>
          <div v-else class="w-full h-full bg-gray-900"></div>
        </div>

        <!-- ② 9:16 고정 비율 비디오 박스 -->
        <div class="video-box">
          <!-- YouTube -->
          <template v-if="short.platform === 'youtube'">
            <iframe v-if="currentIndex === idx"
              :src="embedUrl(short)"
              frameborder="0"
              allow="autoplay; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowfullscreen>
            </iframe>
            <!-- 비활성 슬라이드: 썸네일만 -->
            <div v-else class="w-full h-full relative">
              <img v-if="short.thumbnail" :src="short.thumbnail" class="w-full h-full object-cover"/>
              <div v-else class="w-full h-full bg-black"></div>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-14 h-14 rounded-full bg-black/40 flex items-center justify-center">
                  <svg class="w-7 h-7 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </div>
              </div>
            </div>
          </template>

          <!-- TikTok / Instagram -->
          <template v-else-if="short.platform === 'tiktok' || short.platform === 'instagram'">
            <iframe v-if="currentIndex === idx"
              :src="embedUrl(short)"
              frameborder="0" scrolling="no" allowfullscreen
              allow="encrypted-media">
            </iframe>
            <div v-else class="w-full h-full flex items-center justify-center bg-gray-900">
              <div class="text-4xl">{{ short.platform === 'tiktok' ? '🎵' : '📸' }}</div>
            </div>
          </template>

          <!-- 기타 -->
          <template v-else>
            <a :href="short.url" target="_blank" rel="noopener"
              class="w-full h-full flex flex-col items-center justify-center text-white gap-3 p-8 text-center bg-gray-900">
              <svg class="w-12 h-12 opacity-60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
              <span class="text-sm opacity-80 break-all">{{ short.url }}</span>
            </a>
          </template>
        </div>

        <!-- ③ 스와이프 캡처 오버레이 (iframe 이벤트 차단 해결) -->
        <div class="swipe-overlay"
          @touchstart.passive="onTouchStart"
          @touchmove.passive="onTouchMove"
          @touchend.passive="onTouchEnd">
        </div>

        <!-- ④ 하단 그라디언트 + 정보 -->
        <div class="info-overlay">
          <!-- 제목/유저 정보 -->
          <div class="flex items-end gap-3 px-4 pb-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <div class="w-8 h-8 rounded-full bg-gray-600 overflow-hidden flex-shrink-0 ring-2 ring-white/20">
                  <img v-if="short.user?.avatar" :src="short.user.avatar" class="w-full h-full object-cover"/>
                  <span v-else class="w-full h-full flex items-center justify-center text-white text-xs font-bold bg-gray-700">
                    {{ (short.user?.username || '?')[0].toUpperCase() }}
                  </span>
                </div>
                <span class="text-white text-sm font-semibold drop-shadow">
                  {{ short.user?.username ? '@' + short.user.username : platformLabel(short.platform) }}
                </span>
              </div>
              <p v-if="short.title" class="text-white text-sm font-medium mb-1 drop-shadow line-clamp-2">{{ short.title }}</p>
              <div v-if="short.tags?.length" class="flex flex-wrap gap-1">
                <span v-for="tag in short.tags.slice(0,4)" :key="tag"
                  class="text-xs text-white/70 bg-white/10 rounded-full px-2 py-0.5">#{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ⑤ 오른쪽 액션 버튼 (safe-area 하단 적용) -->
        <div class="action-btns">
          <!-- 좋아요 -->
          <button @click="toggleLike(short)" class="flex flex-col items-center gap-1">
            <div :class="short.liked ? 'bg-red-500/80' : 'bg-black/30'"
              class="w-11 h-11 rounded-full flex items-center justify-center transition-all active:scale-90">
              <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
            </div>
            <span class="text-white text-xs drop-shadow">{{ short.like_count || 0 }}</span>
          </button>

          <!-- 공유 -->
          <button @click="shareShort(short)" class="flex flex-col items-center gap-1">
            <div class="w-11 h-11 rounded-full bg-black/30 flex items-center justify-center text-white active:scale-90 transition-transform">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
              </svg>
            </div>
            <span class="text-white text-xs drop-shadow">공유</span>
          </button>

          <!-- 원본 -->
          <a :href="short.url" target="_blank" rel="noopener" class="flex flex-col items-center gap-1">
            <div class="w-11 h-11 rounded-full bg-black/30 flex items-center justify-center text-white active:scale-90 transition-transform">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
            </div>
            <span class="text-white text-xs drop-shadow">원본</span>
          </a>
        </div>

        <!-- ⑥ 좌측 이전/다음 버튼 -->
        <div class="nav-btns">
          <button @click="goPrev" :disabled="currentIndex === 0"
            class="w-9 h-9 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white disabled:opacity-20 active:scale-90 transition-transform">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 15l7-7 7 7"/>
            </svg>
          </button>
          <!-- 위치 인디케이터 -->
          <div class="flex flex-col items-center gap-1 py-1">
            <div v-for="(_, i) in Math.min(shorts.length, 7)" :key="i"
              :class="i === currentIndex % 7 ? 'bg-white h-5' : 'bg-white/30 h-2'"
              class="w-1 rounded-full transition-all duration-200">
            </div>
          </div>
          <button @click="goNext" :disabled="currentIndex >= shorts.length - 1"
            class="w-9 h-9 rounded-full bg-black/50 backdrop-blur-sm flex items-center justify-center text-white disabled:opacity-20 active:scale-90 transition-transform">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
        </div>

      </div><!-- /short-slide -->

      <!-- 로딩 -->
      <div v-if="loading" class="short-slide flex items-center justify-center bg-gray-900">
        <div class="animate-spin rounded-full h-10 w-10 border-4 border-white border-t-transparent"></div>
      </div>
    </div>

    <!-- 첫 화면 스와이프 힌트 -->
    <Transition name="fade">
      <div v-if="showHint && currentIndex === 0 && shorts.length > 1"
        class="fixed bottom-10 left-1/2 -translate-x-1/2 z-40 pointer-events-none flex flex-col items-center gap-1">
        <p class="text-white/60 text-xs">위로 스와이프</p>
        <svg class="w-6 h-6 text-white/60 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
        </svg>
      </div>
    </Transition>

    <!-- 관심 태그 모달 -->
    <Transition name="slide-up">
      <div v-if="showInterests" class="fixed inset-0 z-[100] bg-black/70 flex items-end"
        @click.self="showInterests = false">
        <div class="w-full bg-gray-900 rounded-t-2xl p-5"
          :style="{ paddingBottom: 'max(20px, env(safe-area-inset-bottom, 20px))' }">
          <div class="w-10 h-1 bg-gray-600 rounded-full mx-auto mb-4"></div>
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-white font-bold text-lg">관심 태그 설정</h3>
            <button @click="showInterests = false" class="text-white/60 hover:text-white text-xl">✕</button>
          </div>
          <p class="text-white/60 text-sm mb-4">선택한 태그의 콘텐츠를 우선 보여드립니다</p>
          <div class="flex flex-wrap gap-2 mb-5">
            <button v-for="tag in allTags" :key="tag"
              @click="toggleTag(tag)"
              :class="selectedTags.includes(tag) ? 'bg-red-500 text-white border-red-500' : 'bg-transparent text-white/70 border-white/30'"
              class="border rounded-full px-4 py-1.5 text-sm transition-all active:scale-95">
              #{{ tag }}
            </button>
          </div>
          <button @click="saveInterests"
            class="w-full bg-red-500 text-white font-bold py-3 rounded-xl hover:bg-red-600 active:scale-98 transition-transform">
            저장하기
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import axios from 'axios'

const auth = useAuthStore()
const shorts = ref([])
const loading = ref(false)
const currentIndex = ref(0)
const hasMore = ref(true)
const dragOffset = ref(0)
const touchStartY = ref(0)
const touchLastY = ref(0)
const showInterests = ref(false)
const showHint = ref(true)
const selectedTags = ref([])
const allTags = ['요리','여행','뷰티','운동','육아','K-POP','게임','뉴스','재미','음식','패션','생활정보','부동산','자동차','애완동물']

// ── 실제 모바일 뷰포트 높이 (주소창 제외) ──────────────────────────
function setVh() {
  const vh = window.innerHeight * 0.01
  document.documentElement.style.setProperty('--vh', `${vh}px`)
}

// ── Interleave (YouTube 5개마다 회원 숏츠 1개 끼워넣기) ───────────
function interleave(ytList, userList, every = 5) {
  if (!userList.length) return ytList
  const result = []
  let ui = 0
  for (let i = 0; i < ytList.length; i++) {
    result.push(ytList[i])
    if ((i + 1) % every === 0 && ui < userList.length) result.push(userList[ui++])
  }
  while (ui < userList.length) result.push(userList[ui++])
  return result
}

// ── Fisher-Yates shuffle ──────────────────────────────────────────
function shuffle(arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[arr[i], arr[j]] = [arr[j], arr[i]]
  }
  return arr
}

function shuffleShorts() {
  const current = shorts.value[currentIndex.value]
  shuffle(shorts.value)
  if (current) {
    const idx = shorts.value.indexOf(current)
    if (idx > 0) { shorts.value.splice(idx, 1); shorts.value.unshift(current) }
  }
  currentIndex.value = 0
}

// ── 데이터 로드 ──────────────────────────────────────────────────
async function loadShorts() {
  if (loading.value || !hasMore.value) return
  loading.value = true
  try {
    const { data } = await axios.get('/api/shorts', { params: { per_page: 500 } })
    if (data.data && data.data.length > 0) {
      const all = data.data
      const ytShorts = shuffle(all.filter(s => s.platform === 'youtube' || !s.user_id))
      const memberShorts = shuffle(all.filter(s => s.user_id && s.platform !== 'youtube'))
      shorts.value = interleave(ytShorts, memberShorts, 5)
      hasMore.value = false
    } else {
      hasMore.value = false
    }
  } catch {
    hasMore.value = false
  } finally {
    loading.value = false
  }
}

// ── embed URL 생성 ────────────────────────────────────────────────
function embedUrl(short) {
  if (short.platform !== 'youtube') return short.embed_url || short.url
  // 항상 /shorts/ 형식의 embed 사용 → 세로 플레이어 강제
  const match = (short.url || short.embed_url || '').match(/(?:shorts\/|embed\/|v=|youtu\.be\/)([A-Za-z0-9_-]{11})/)
  if (!match) return short.embed_url
  const vid = match[1]
  return `https://www.youtube.com/embed/${vid}?autoplay=1&mute=1&loop=1&playlist=${vid}&rel=0&controls=1&playsinline=1`
}

function platformLabel(p) {
  return { youtube: 'YouTube', tiktok: 'TikTok', instagram: 'Instagram' }[p] || '숏츠'
}

// ── 스와이프 / 휠 ────────────────────────────────────────────────
function onWheel(e) {
  if (e.deltaY > 30) goNext()
  else if (e.deltaY < -30) goPrev()
}

function onTouchStart(e) {
  touchStartY.value = e.touches[0].clientY
  touchLastY.value = e.touches[0].clientY
}

function onTouchMove(e) {
  touchLastY.value = e.touches[0].clientY
}

function onTouchEnd() {
  const diff = touchStartY.value - touchLastY.value
  if (diff > 50) goNext()
  else if (diff < -50) goPrev()
  dragOffset.value = 0
}

function onKeydown(e) {
  if (e.key === 'ArrowDown' || e.key === 'ArrowRight') goNext()
  if (e.key === 'ArrowUp'   || e.key === 'ArrowLeft')  goPrev()
}

function goNext() {
  if (currentIndex.value < shorts.value.length - 1) {
    currentIndex.value++
    showHint.value = false
    recordView()
    if (currentIndex.value >= shorts.value.length - 5) loadShorts()
  }
}

function goPrev() {
  if (currentIndex.value > 0) currentIndex.value--
}

function recordView() {
  const s = shorts.value[currentIndex.value]
  if (s) axios.post(`/api/shorts/${s.id}/view`).catch(() => {})
}

// ── 좋아요 / 공유 ────────────────────────────────────────────────
async function toggleLike(short) {
  if (!auth.isLoggedIn) { alert('로그인이 필요합니다.'); return }
  try {
    const { data } = await axios.post(`/api/shorts/${short.id}/like`)
    short.liked = data.liked
    short.like_count = data.like_count
  } catch {}
}

function shareShort(short) {
  if (navigator.share) {
    navigator.share({ title: short.title || 'SomeKorean 숏츠', url: short.url })
  } else {
    navigator.clipboard?.writeText(short.url)
    alert('링크가 복사되었습니다!')
  }
}

// ── 관심 태그 ────────────────────────────────────────────────────
function toggleTag(tag) {
  const i = selectedTags.value.indexOf(tag)
  if (i >= 0) selectedTags.value.splice(i, 1)
  else if (selectedTags.value.length < 10) selectedTags.value.push(tag)
}

async function saveInterests() {
  if (auth.isLoggedIn) {
    try { await axios.post('/api/shorts/interests', { tags: selectedTags.value }) } catch {}
  }
  showInterests.value = false
  shorts.value = []; hasMore.value = true; currentIndex.value = 0
  loadShorts()
}

// ── 라이프사이클 ─────────────────────────────────────────────────
onMounted(async () => {
  setVh()
  window.addEventListener('resize', setVh)
  document.addEventListener('keydown', onKeydown)
  document.body.style.overflow = 'hidden'
  await loadShorts()
  // 3초 후 힌트 숨김
  setTimeout(() => { showHint.value = false }, 3000)
  if (auth.isLoggedIn) {
    try {
      const { data } = await axios.get('/api/shorts/interests')
      selectedTags.value = data.tags || []
    } catch {}
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', setVh)
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* ── 전체 래퍼: 화면 완전 고정 ────────────────────────────────── */
.shorts-wrap {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  overflow: hidden;
  background: #000;
  /* 100dvh: 모바일 브라우저 주소창 포함 계산 방지 */
  height: 100dvh;
  height: calc(var(--vh, 1vh) * 100); /* fallback */
}

/* ── 슬라이더 ─────────────────────────────────────────────────── */
.shorts-slider {
  position: absolute;
  top: 0; left: 0; right: 0;
  will-change: transform;
  transition: transform 0.38s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* ── 슬라이드 1장: 화면 꽉 채움 ─────────────────────────────── */
.short-slide {
  position: relative;
  width: 100vw;
  height: 100dvh;
  height: calc(var(--vh, 1vh) * 100);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
}

/* ── ① 블러 배경 ─────────────────────────────────────────────── */
.bg-blur {
  position: absolute;
  inset: 0;
  z-index: 1;
  overflow: hidden;
}
.bg-blur img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(24px) brightness(0.25);
  transform: scale(1.15); /* blur 가장자리 잘림 방지 */
}

/* ── ② 9:16 고정 비디오 박스 ────────────────────────────────── */
.video-box {
  position: relative;
  z-index: 2;
  /* 세로 비율 9:16 강제 - 어떤 영상이 와도 크기 고정 */
  width: min(100vw, calc(100dvh * 9 / 16));
  width: min(100vw, calc(var(--vh, 1vh) * 100 * 9 / 16));
  aspect-ratio: 9 / 16;
  max-height: 100dvh;
  max-height: calc(var(--vh, 1vh) * 100);
  overflow: hidden;
  background: #000;
  border-radius: 0;
}
.video-box iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

/* ── ③ 스와이프 오버레이 ─────────────────────────────────────── */
.swipe-overlay {
  position: absolute;
  inset: 0;
  z-index: 10;
  /* 하단 액션버튼/정보 영역은 터치 통과 */
  /* 실제 클릭은 z-index 높은 요소들이 처리 */
}

/* ── ④ 하단 정보 오버레이 ────────────────────────────────────── */
.info-overlay {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  z-index: 20;
  background: linear-gradient(to top, rgba(0,0,0,0.75) 0%, transparent 100%);
  padding-bottom: max(16px, env(safe-area-inset-bottom, 16px));
  pointer-events: none;
}

/* ── ⑤ 오른쪽 액션 버튼 ─────────────────────────────────────── */
.action-btns {
  position: absolute;
  right: 12px;
  z-index: 25;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  /* 하단 safe area + 하단 정보 영역 위 */
  bottom: calc(max(80px, 72px + env(safe-area-inset-bottom, 0px)));
}

/* ── ⑥ 좌측 이전/다음 버튼 ─────────────────────────────────── */
.nav-btns {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 25;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

/* ── 트랜지션 ────────────────────────────────────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s }
.fade-enter-from, .fade-leave-to { opacity: 0 }
.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94) }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%) }
</style>
'''

print("Writing ShortsHome.vue...")
print(write_file('/var/www/somekorean/resources/js/pages/shorts/ShortsHome.vue', new_shorts))

print("\nBuilding...")
result = ssh('cd /var/www/somekorean && npm run build 2>&1', timeout=180)
lines = result.splitlines()
has_error = any('error' in l.lower() for l in lines if 'ERR' not in l)
if has_error:
    for l in lines:
        if 'Error' in l or ('error' in l.lower() and 'WARN' not in l):
            print(l)
print('\n'.join(lines[-8:]))
c.close()
