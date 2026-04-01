<template>
  <div class="admin-games">
    <div class="page-header">
      <div>
        <h1 class="page-title">🎮 게임 관리</h1>
        <p class="page-sub">총 {{ games.length }}개 · 활성 {{ activeCount }}개 · 교육형 {{ eduCount }}개</p>
      </div>
      <div class="header-actions">
        <select v-model="filterType" class="filter-sel">
          <option value="">전체 유형</option>
          <option value="educational">📚 교육형</option>
          <option value="single">🎯 단일형</option>
          <option value="betting">🎰 베팅형</option>
          <option value="arcade">🕹️ 아케이드</option>
        </select>
        <select v-model="filterCat" class="filter-sel">
          <option value="">전체 카테고리</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
        <input v-model="search" class="search-input" placeholder="🔍 게임 검색..."/>
      </div>
    </div>

    <div class="stat-cards">
      <div class="stat-card blue">
        <div class="stat-num">{{ games.length }}</div>
        <div class="stat-label">전체 게임</div>
      </div>
      <div class="stat-card green">
        <div class="stat-num">{{ activeCount }}</div>
        <div class="stat-label">활성 게임</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-num">{{ totalPlays.toLocaleString() }}</div>
        <div class="stat-label">총 플레이</div>
      </div>
      <div class="stat-card teal">
        <div class="stat-num">{{ eduCount }}</div>
        <div class="stat-label">교육형 (문제관리)</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-num">{{ arcadeCount }}</div>
        <div class="stat-label">아케이드 게임</div>
      </div>
    </div>

    <!-- 게임 목록 -->
    <div class="games-section">
      <div v-if="loading" class="loading-box">
        <div class="spinner"></div>
        <p>게임 목록을 불러오는 중...</p>
      </div>
      <div v-else>
        <div v-for="cat in filteredCategories" :key="cat.id" class="cat-group">
          <div class="cat-header">
            <span class="cat-icon">{{ catIcon(cat.id) }}</span>
            <span class="cat-name">{{ cat.name }}</span>
            <span class="cat-count">{{ gamesByCategory(cat.id).length }}개</span>
          </div>
          <div class="games-grid">
            <div v-for="game in gamesByCategory(cat.id)" :key="game.id"
                 class="game-card" :class="{inactive: !game.is_active}">
              <div class="game-top">
                <div class="game-id">#{{ game.id }}</div>
                <label class="toggle-switch">
                  <input type="checkbox" :checked="game.is_active" @change="toggleGame(game)"/>
                  <span class="slider"></span>
                </label>
              </div>
              <div class="game-name">{{ game.name }}</div>
              <div class="game-route">{{ game.route_name || '라우트 없음' }}</div>
              <!-- 게임 유형 뱃지 -->
              <div class="type-badge" :class="'type-' + game.type">
                {{ typeLabel(game.type) }}
              </div>
              <div class="game-stats">
                <span class="stat-pill plays">🎮 {{ (game.session_count || 0).toLocaleString() }}</span>
                <span class="stat-pill score">⭐ {{ game.top_score || 0 }}</span>
                <span v-if="game.is_new" class="stat-pill new-tag">NEW</span>
              </div>
              <!-- 교육형만 문제관리 버튼 표시 -->
              <div v-if="game.type === 'educational'" class="game-actions">
                <button class="action-btn q-btn" @click="openQuestions(game)">
                  📝 문제관리
                  <span v-if="game.question_count > 0" class="q-count-badge">{{ game.question_count }}</span>
                </button>
              </div>
              <div v-else class="game-type-note">
                {{ game.type === 'betting' ? '🎰 베팅 게임' : '🎯 단일 게임' }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 아케이드 게임 섹션 -->
    <div v-if="!filterType || filterType === 'arcade'" class="arcade-section">
      <div class="cat-header">
        <span class="cat-icon">🕹️</span>
        <span class="cat-name">아케이드 게임</span>
        <span class="cat-count">{{ arcadeGames.length }}개</span>
      </div>
      <div class="games-grid">
        <div v-for="game in filteredArcadeGames" :key="game.id"
             class="game-card" :class="{inactive: !game.is_active}">
          <div class="game-top">
            <div class="game-id">🕹️ ARCADE</div>
            <label class="toggle-switch">
              <input type="checkbox" :checked="game.is_active" @change="toggleArcadeGame(game)"/>
              <span class="slider"></span>
            </label>
          </div>
          <div class="game-name">{{ game.name }}</div>
          <div class="game-route">{{ game.route_name }}</div>
          <div class="type-badge type-arcade">🕹️ 아케이드</div>
          <div class="game-stats">
            <span class="stat-pill plays">🎮 {{ (game.play_count || 0).toLocaleString() }}</span>
          </div>
          <div class="game-type-note">무료 아케이드 게임</div>
        </div>
      </div>
    </div>

    <!-- 문제 관리 모달 (교육형 전용) -->
    <Teleport to="body">
      <div v-if="qModal.open" class="modal-backdrop" @click.self="qModal.open=false">
        <div class="modal-box">
          <div class="modal-header">
            <div>
              <h2>📚 {{ qModal.game?.name }}</h2>
              <p class="modal-sub">문제 {{ qModal.questions.length }}개 등록됨</p>
            </div>
            <button class="close-btn" @click="qModal.open=false">✕</button>
          </div>
          <div class="modal-body">
            <!-- 문제 추가 폼 -->
            <div class="add-question-form">
              <h3 class="form-title">➕ 새 문제 추가</h3>
              <div class="form-row">
                <input v-model="newQ.question" class="form-input" placeholder="문제 내용 (예: 다음 중 봄 꽃은?)"/>
                <input v-model="newQ.answer" class="form-input sm" placeholder="정답"/>
              </div>
              <div class="form-row">
                <input v-model="newQ.options_str" class="form-input"
                  placeholder="보기 (쉼표로 구분, 예: 장미,국화,벚꽃,튤립) — 정답 포함 입력"/>
                <select v-model="newQ.difficulty" class="form-input sm">
                  <option value="1">⭐ 레벨 1 (쉬움)</option>
                  <option value="2">⭐⭐ 레벨 2 (보통)</option>
                  <option value="3">⭐⭐⭐ 레벨 3 (어려움)</option>
                </select>
              </div>
              <button class="add-btn" @click="addQuestion"
                :disabled="!newQ.question || !newQ.answer">
                + 문제 추가하기
              </button>
            </div>

            <!-- 레벨별 문제 목록 -->
            <div v-if="qModal.loading" class="q-loading">불러오는 중...</div>
            <div v-else-if="qModal.questions.length === 0" class="q-empty">
              <div style="font-size:48px;margin-bottom:8px">📭</div>
              <p>등록된 문제가 없습니다.</p>
              <p style="font-size:13px;color:#94a3b8">위에서 첫 번째 문제를 추가해보세요!</p>
            </div>
            <div v-else>
              <div v-for="lv in [1,2,3]" :key="lv" class="level-section">
                <div v-if="questionsByLevel(lv).length > 0">
                  <div class="level-header">
                    <span class="level-stars">{{ '⭐'.repeat(lv) }}</span>
                    <span class="level-name">레벨 {{ lv }} {{ ['(쉬움)','(보통)','(어려움)'][lv-1] }}</span>
                    <span class="level-count">{{ questionsByLevel(lv).length }}문제</span>
                  </div>
                  <div v-for="q in questionsByLevel(lv)" :key="q.id" class="q-item">
                    <div class="q-content">
                      <div class="q-text">{{ q.question }}</div>
                      <div class="q-answer-row">
                        <span class="q-answer-label">정답:</span>
                        <span class="q-answer">{{ q.answer }}</span>
                      </div>
                      <div v-if="q.options && parseOptions(q.options).length > 0" class="q-opts">
                        <span class="q-opts-label">보기:</span>
                        <span v-for="(opt, i) in parseOptions(q.options)" :key="i"
                          class="q-opt-chip" :class="{correct: opt === q.answer}">
                          {{ opt }}
                        </span>
                      </div>
                    </div>
                    <button class="del-btn" @click="deleteQuestion(q.id)" title="삭제">🗑</button>
                  </div>
                </div>
              </div>

              <!-- 레벨 미설정 문제 -->
              <div v-if="questionsByLevel(0).length > 0" class="level-section">
                <div class="level-header">
                  <span class="level-stars">❓</span>
                  <span class="level-name">레벨 미설정</span>
                  <span class="level-count">{{ questionsByLevel(0).length }}문제</span>
                </div>
                <div v-for="q in questionsByLevel(0)" :key="q.id" class="q-item">
                  <div class="q-content">
                    <div class="q-text">{{ q.question }}</div>
                    <div class="q-answer-row">
                      <span class="q-answer-label">정답:</span>
                      <span class="q-answer">{{ q.answer }}</span>
                    </div>
                  </div>
                  <button class="del-btn" @click="deleteQuestion(q.id)">🗑</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <Transition name="toast">
      <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.msg }}</div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const games = ref([])
const arcadeGames = ref([
  { id: 'snake', name: '🐍 뱀 게임', route_name: 'game-snake', type: 'arcade', play_count: 0, is_active: true },
  { id: 'pacman', name: '👾 팩맨', route_name: 'game-pacman', type: 'arcade', play_count: 0, is_active: true },
  { id: 'flappy', name: '🐦 클럼지 버드', route_name: 'game-flappy', type: 'arcade', play_count: 0, is_active: true },
  { id: 'duckhunt', name: '🦆 덕 헌트', route_name: 'game-duckhunt', type: 'arcade', play_count: 0, is_active: true },
  { id: 'slots', name: '🎰 슬롯머신', route_name: 'game-slots', type: 'arcade', play_count: 0, is_active: true },
  { id: 'hextris', name: '🔷 헥스트리스', route_name: 'game-hextris', type: 'arcade', play_count: 0, is_active: true },
  { id: 'mahjong', name: '🀄 마작 솔리테어', route_name: 'game-mahjong', type: 'arcade', play_count: 0, is_active: true },
])
const categories = ref([
  { id: 1, name: '아기 (0-3세)' },
  { id: 2, name: '어린이 (4-10세)' },
  { id: 3, name: '청소년 (11-18세)' },
  { id: 4, name: '성인' },
  { id: 5, name: '시니어' },
])
const loading = ref(true)
const search = ref('')
const filterCat = ref('')
const filterType = ref('')
const toast = ref({ show: false, msg: '', type: 'success' })
const qModal = ref({ open: false, game: null, questions: [], loading: false })
const newQ = ref({ question: '', answer: '', options_str: '', difficulty: '1' })

function catIcon(id) {
  return ['👶','👦','🧑‍🎓','👨','👴'][id - 1] || '🎮'
}
function typeLabel(type) {
  return { educational: '📚 교육형', single: '🎯 단일형', betting: '🎰 베팅형', multi: '👥 멀티', arcade: '🕹️ 아케이드' }[type] || type
}

const activeCount = computed(() => games.value.filter(g => g.is_active).length)
const eduCount = computed(() => games.value.filter(g => g.type === 'educational').length)
const arcadeCount = computed(() => arcadeGames.value.filter(g => g.is_active).length)
const totalPlays = computed(() => games.value.reduce((s, g) => s + (g.session_count || 0), 0))

const filteredArcadeGames = computed(() => {
  if (!search.value) return arcadeGames.value
  return arcadeGames.value.filter(g => g.name.toLowerCase().includes(search.value.toLowerCase()))
})

function gamesByCategory(catId) {
  return games.value.filter(g => {
    if (g.category_id !== catId) return false
    if (filterType.value && g.type !== filterType.value) return false
    if (search.value && !g.name.toLowerCase().includes(search.value.toLowerCase())) return false
    return true
  })
}

const filteredCategories = computed(() => {
  const cats = filterCat.value
    ? categories.value.filter(c => c.id == filterCat.value)
    : categories.value
  return cats.filter(c => gamesByCategory(c.id).length > 0)
})

function questionsByLevel(lv) {
  return qModal.value.questions.filter(q => {
    if (lv === 0) return !q.difficulty || (q.difficulty !== 1 && q.difficulty !== 2 && q.difficulty !== 3)
    return q.difficulty === lv
  })
}

async function loadGames() {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/games')
    // Add question count to each game
    games.value = res.data
    // Load question counts for educational games
    const eduGames = games.value.filter(g => g.type === 'educational')
    await Promise.all(eduGames.map(async g => {
      try {
        const r = await axios.get('/api/admin/games/' + g.id + '/questions')
        g.question_count = r.data.length
      } catch { g.question_count = 0 }
    }))
  } catch (e) {
    showToast('게임 목록을 불러오지 못했습니다', 'error')
  } finally {
    loading.value = false
  }
}

async function toggleGame(game) {
  const prev = game.is_active
  game.is_active = !game.is_active
  try {
    await axios.put('/api/admin/games/' + game.id + '/toggle')
    showToast(game.name + ': ' + (game.is_active ? '활성화' : '비활성화') + ' 완료')
  } catch (e) {
    game.is_active = prev
    showToast('변경 실패', 'error')
  }
}

function toggleArcadeGame(game) {
  game.is_active = !game.is_active
  showToast(game.name + ': ' + (game.is_active ? '활성화' : '비활성화') + ' 완료')
}

async function openQuestions(game) {
  qModal.value = { open: true, game, questions: [], loading: true }
  newQ.value = { question: '', answer: '', options_str: '', difficulty: '1' }
  try {
    const res = await axios.get('/api/admin/games/' + game.id + '/questions')
    qModal.value.questions = res.data
  } catch (e) {
    showToast('문제 목록 로드 실패', 'error')
  } finally {
    qModal.value.loading = false
  }
}

async function addQuestion() {
  const opts = newQ.value.options_str
    ? newQ.value.options_str.split(',').map(s => s.trim()).filter(Boolean)
    : []
  try {
    const res = await axios.post('/api/admin/games/' + qModal.value.game.id + '/questions', {
      question: newQ.value.question,
      answer: newQ.value.answer,
      options: opts,
      difficulty: parseInt(newQ.value.difficulty),
    })
    showToast('문제가 추가되었습니다!')
    newQ.value = { question: '', answer: '', options_str: '', difficulty: '1' }
    // Reload questions
    const r = await axios.get('/api/admin/games/' + qModal.value.game.id + '/questions')
    qModal.value.questions = r.data
    // Update count in game card
    const g = games.value.find(g => g.id === qModal.value.game.id)
    if (g) g.question_count = r.data.length
  } catch (e) {
    showToast('문제 추가 실패', 'error')
  }
}

async function deleteQuestion(qid) {
  if (!confirm('이 문제를 삭제하시겠습니까?')) return
  try {
    await axios.delete('/api/admin/questions/' + qid)
    qModal.value.questions = qModal.value.questions.filter(q => q.id !== qid)
    const g = games.value.find(g => g.id === qModal.value.game.id)
    if (g) g.question_count = qModal.value.questions.length
    showToast('삭제되었습니다')
  } catch (e) {
    showToast('삭제 실패', 'error')
  }
}

function parseOptions(opts) {
  try {
    const parsed = JSON.parse(opts)
    return Array.isArray(parsed) ? parsed : []
  } catch { return [] }
}

function showToast(msg, type = 'success') {
  toast.value = { show: true, msg, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}

onMounted(loadGames)
</script>

<style scoped>
.admin-games { padding: 24px; max-width: 1400px; margin: 0 auto; font-family: 'Noto Sans KR', sans-serif; }

/* 헤더 */
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 26px; font-weight: 800; color: #1e293b; margin: 0; }
.page-sub { color: #64748b; font-size: 14px; margin: 4px 0 0; }
.header-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.filter-sel, .search-input { border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 14px; font-size: 14px; outline: none; background: #fff; }
.filter-sel:focus, .search-input:focus { border-color: #6366f1; }

/* 통계 카드 */
.stat-cards { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 28px; }
@media (max-width: 768px) { .stat-cards { grid-template-columns: repeat(2, 1fr); } }
.stat-card { border-radius: 16px; padding: 20px; color: #fff; text-align: center; }
.stat-card.blue { background: linear-gradient(135deg, #6366f1, #818cf8); }
.stat-card.green { background: linear-gradient(135deg, #10b981, #34d399); }
.stat-card.purple { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }
.stat-card.teal { background: linear-gradient(135deg, #0891b2, #06b6d4); }
.stat-card.orange { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.stat-num { font-size: 32px; font-weight: 800; }
.stat-label { font-size: 13px; opacity: 0.9; margin-top: 4px; }

/* 카테고리 그룹 */
.cat-group { margin-bottom: 32px; }
.cat-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 2px solid #e2e8f0; }
.cat-icon { font-size: 22px; }
.cat-name { font-size: 18px; font-weight: 700; color: #1e293b; }
.cat-count { background: #e2e8f0; color: #64748b; border-radius: 20px; padding: 2px 10px; font-size: 12px; font-weight: 600; }

/* 게임 카드 그리드 */
.games-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 14px; }
.game-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; transition: all .2s; box-shadow: 0 2px 6px rgba(0,0,0,.04); }
.game-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.1); transform: translateY(-2px); }
.game-card.inactive { opacity: 0.5; background: #f8fafc; }
.game-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.game-id { font-size: 11px; color: #94a3b8; font-weight: 600; }
.game-name { font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 3px; line-height: 1.3; }
.game-route { font-size: 11px; color: #94a3b8; margin-bottom: 8px; word-break: break-all; }
.type-badge { display: inline-block; font-size: 11px; padding: 3px 10px; border-radius: 20px; font-weight: 600; margin-bottom: 8px; }
.type-educational { background: #dbeafe; color: #1d4ed8; }
.type-single { background: #f3f4f6; color: #4b5563; }
.type-betting { background: #fef3c7; color: #b45309; }
.type-arcade { background: #fce7f3; color: #be185d; }
.game-stats { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.stat-pill { font-size: 11px; padding: 2px 8px; border-radius: 20px; font-weight: 600; }
.stat-pill.plays { background: #ede9fe; color: #7c3aed; }
.stat-pill.score { background: #fef9c3; color: #ca8a04; }
.stat-pill.new-tag { background: #dcfce7; color: #16a34a; }
.game-actions { }
.action-btn { width: 100%; padding: 8px 12px; border-radius: 10px; font-size: 12px; font-weight: 700; border: none; cursor: pointer; text-align: center; display: flex; align-items: center; justify-content: center; gap: 6px; }
.q-btn { background: #ede9fe; color: #7c3aed; transition: background .15s; }
.q-btn:hover { background: #ddd6fe; }
.q-count-badge { background: #7c3aed; color: #fff; border-radius: 20px; padding: 1px 7px; font-size: 11px; }
.game-type-note { text-align: center; font-size: 12px; color: #9ca3af; padding: 6px 0; }

/* 토글 스위치 */
.toggle-switch { position: relative; display: inline-block; width: 38px; height: 22px; cursor: pointer; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; inset: 0; background: #cbd5e1; border-radius: 22px; transition: .3s; }
.slider:before { content: ''; position: absolute; width: 16px; height: 16px; border-radius: 50%; background: #fff; bottom: 3px; left: 3px; transition: .3s; }
input:checked + .slider { background: #10b981; }
input:checked + .slider:before { transform: translateX(16px); }

/* 모달 */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal-box { background: #fff; border-radius: 20px; width: 100%; max-width: 720px; max-height: 90vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: flex-start; padding: 20px 24px 16px; border-bottom: 1px solid #e2e8f0; }
.modal-header h2 { font-size: 20px; font-weight: 800; margin: 0; color: #1e293b; }
.modal-sub { font-size: 13px; color: #64748b; margin: 4px 0 0; }
.close-btn { background: none; border: none; font-size: 20px; cursor: pointer; color: #64748b; padding: 0; }
.modal-body { padding: 20px 24px; overflow-y: auto; flex: 1; }

/* 문제 추가 폼 */
.form-title { font-size: 13px; font-weight: 700; color: #374151; margin: 0 0 10px; text-transform: uppercase; letter-spacing: .5px; }
.form-row { display: flex; gap: 10px; margin-bottom: 10px; }
.form-input { flex: 1; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; font-size: 14px; outline: none; font-family: inherit; }
.form-input.sm { flex: 0 0 140px; }
.form-input:focus { border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99,102,241,.1); }
.add-btn { background: #6366f1; color: #fff; border: none; padding: 10px 28px; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; margin-bottom: 24px; }
.add-btn:disabled { opacity: .4; cursor: not-allowed; }
.add-question-form { background: #f8fafc; border-radius: 14px; padding: 16px 18px; margin-bottom: 20px; border: 1px solid #e2e8f0; }

/* 레벨별 문제 목록 */
.level-section { margin-bottom: 20px; }
.level-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; padding: 8px 12px; background: #f1f5f9; border-radius: 10px; }
.level-stars { font-size: 14px; }
.level-name { font-size: 14px; font-weight: 700; color: #1e293b; flex: 1; }
.level-count { font-size: 12px; color: #64748b; background: #fff; padding: 2px 10px; border-radius: 20px; }

.q-loading { text-align: center; color: #94a3b8; padding: 30px; }
.q-empty { text-align: center; color: #94a3b8; padding: 40px 20px; }
.q-item { display: flex; justify-content: space-between; align-items: flex-start; padding: 14px 16px; background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 8px; gap: 10px; transition: border-color .2s; }
.q-item:hover { border-color: #c7d2fe; }
.q-content { flex: 1; }
.q-text { font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 6px; line-height: 1.5; }
.q-answer-row { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.q-answer-label { font-size: 12px; color: #64748b; }
.q-answer { font-size: 13px; font-weight: 700; color: #059669; background: #d1fae5; padding: 2px 8px; border-radius: 6px; }
.q-opts { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; margin-top: 6px; }
.q-opts-label { font-size: 12px; color: #64748b; margin-right: 2px; }
.q-opt-chip { font-size: 12px; padding: 2px 8px; border-radius: 6px; background: #f1f5f9; color: #475569; font-weight: 500; }
.q-opt-chip.correct { background: #d1fae5; color: #059669; font-weight: 700; }
.del-btn { background: none; border: none; cursor: pointer; font-size: 18px; opacity: .5; flex-shrink: 0; padding: 4px; transition: opacity .15s; }
.del-btn:hover { opacity: 1; }

/* 로딩 */
.loading-box { text-align: center; padding: 60px 20px; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #6366f1; border-radius: 50%; animation: spin .8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 아케이드 섹션 */
.arcade-section { margin-bottom: 32px; }

/* 토스트 */
.toast { position: fixed; bottom: 30px; right: 30px; padding: 14px 24px; border-radius: 12px; color: #fff; font-weight: 600; font-size: 14px; z-index: 9999; box-shadow: 0 4px 20px rgba(0,0,0,.2); }
.toast.success { background: #10b981; }
.toast.error { background: #ef4444; }
.toast-enter-active, .toast-leave-active { transition: all .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(20px); }
</style>
