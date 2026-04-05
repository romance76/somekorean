import paramiko, base64, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
def ssh(cmd, timeout=180):
    _, out, _ = c.exec_command(cmd, timeout=timeout)
    return out.read().decode('utf-8', errors='replace').strip()
def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [enc[i:i+2000] for i in range(0, len(enc), 2000)]
    ssh('rm -f /tmp/wf_chunk')
    for p in chunks:
        ssh(f"printf '%s' '{p}' >> /tmp/wf_chunk")
    ssh(f'cat /tmp/wf_chunk | base64 -d > {path} && rm -f /tmp/wf_chunk')
    print(f'Written {path}: {ssh(f"wc -c < {path}")} bytes')

# ============================================================
# AdminGames.vue — 완전 재작성 (axios 인터셉터 활용, 헤더 불필요)
# ============================================================
admin_games = """<template>
  <div class="admin-games">
    <div class="page-header">
      <div>
        <h1 class="page-title">🎮 게임 관리</h1>
        <p class="page-sub">총 {{ games.length }}개 게임 · 활성 {{ activeCount }}개</p>
      </div>
      <div class="header-actions">
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
      <div class="stat-card orange">
        <div class="stat-num">{{ categories.length }}</div>
        <div class="stat-label">카테고리</div>
      </div>
    </div>

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
              <div class="game-stats">
                <span class="stat-pill plays">🎮 {{ (game.session_count || 0).toLocaleString() }}</span>
                <span class="stat-pill score">⭐ {{ game.top_score || 0 }}</span>
                <span v-if="game.is_new" class="stat-pill new">NEW</span>
              </div>
              <div class="game-actions">
                <button class="action-btn q-btn" @click="openQuestions(game)">📝 문제관리</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 문제 관리 모달 -->
    <Teleport to="body">
      <div v-if="qModal.open" class="modal-backdrop" @click.self="qModal.open=false">
        <div class="modal-box">
          <div class="modal-header">
            <h2>📝 {{ qModal.game?.name }} — 문제 관리</h2>
            <button class="close-btn" @click="qModal.open=false">✕</button>
          </div>
          <div class="modal-body">
            <div class="add-question-form">
              <h3 class="form-title">➕ 새 문제 추가</h3>
              <div class="form-row">
                <input v-model="newQ.question" class="form-input" placeholder="문제 내용"/>
                <input v-model="newQ.answer" class="form-input sm" placeholder="정답"/>
              </div>
              <div class="form-row">
                <input v-model="newQ.options_str" class="form-input" placeholder="보기 (쉼표 구분: 사과,배,포도)"/>
                <select v-model="newQ.difficulty" class="form-input sm">
                  <option value="1">쉬움</option>
                  <option value="2">보통</option>
                  <option value="3">어려움</option>
                </select>
              </div>
              <button class="add-btn" @click="addQuestion" :disabled="!newQ.question || !newQ.answer">
                + 문제 추가
              </button>
            </div>
            <div class="questions-list">
              <div v-if="qModal.loading" class="q-loading">불러오는 중...</div>
              <div v-else-if="qModal.questions.length === 0" class="q-empty">등록된 문제가 없어요.</div>
              <div v-for="q in qModal.questions" :key="q.id" class="q-item">
                <div class="q-content">
                  <div class="q-text">{{ q.question }}</div>
                  <div class="q-answer">정답: <strong>{{ q.answer }}</strong></div>
                  <div v-if="q.options" class="q-opts">보기: {{ parseOptions(q.options) }}</div>
                </div>
                <div class="q-meta">
                  <span class="diff-badge" :class="'diff-'+q.difficulty">{{ diffLabel(q.difficulty) }}</span>
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
const toast = ref({ show: false, msg: '', type: 'success' })
const qModal = ref({ open: false, game: null, questions: [], loading: false })
const newQ = ref({ question: '', answer: '', options_str: '', difficulty: '1' })

function catIcon(id) {
  return ['👶','👦','🧑‍🎓','👨','👴'][id - 1] || '🎮'
}

const activeCount = computed(() => games.value.filter(g => g.is_active).length)
const totalPlays = computed(() => games.value.reduce((s, g) => s + (g.session_count || 0), 0))

function gamesByCategory(catId) {
  return games.value.filter(g => {
    const matchCat = g.category_id === catId
    const matchSearch = !search.value || g.name.toLowerCase().includes(search.value.toLowerCase())
    return matchCat && matchSearch
  })
}

const filteredCategories = computed(() => {
  const cats = filterCat.value
    ? categories.value.filter(c => c.id == filterCat.value)
    : categories.value
  return cats.filter(c => gamesByCategory(c.id).length > 0)
})

async function loadGames() {
  loading.value = true
  try {
    const res = await axios.get('/api/admin/games')
    games.value = res.data
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
    await axios.post('/api/admin/games/' + qModal.value.game.id + '/questions', {
      question: newQ.value.question,
      answer: newQ.value.answer,
      options: opts,
      difficulty: parseInt(newQ.value.difficulty),
    })
    showToast('문제가 추가되었습니다!')
    newQ.value = { question: '', answer: '', options_str: '', difficulty: '1' }
    await openQuestions(qModal.value.game)
  } catch (e) {
    showToast('문제 추가 실패', 'error')
  }
}

async function deleteQuestion(qid) {
  if (!confirm('이 문제를 삭제하시겠습니까?')) return
  try {
    await axios.delete('/api/admin/questions/' + qid)
    qModal.value.questions = qModal.value.questions.filter(q => q.id !== qid)
    showToast('삭제되었습니다')
  } catch (e) {
    showToast('삭제 실패', 'error')
  }
}

function parseOptions(opts) {
  try { return JSON.parse(opts).join(', ') } catch { return opts }
}
function diffLabel(d) { return ['','쉬움','보통','어려움'][d] || '보통' }

function showToast(msg, type = 'success') {
  toast.value = { show: true, msg, type }
  setTimeout(() => { toast.value.show = false }, 3000)
}

onMounted(loadGames)
</script>

<style scoped>
.admin-games { padding: 24px; max-width: 1400px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }
.page-title { font-size: 26px; font-weight: 800; color: #1e293b; margin: 0; }
.page-sub { color: #64748b; font-size: 14px; margin: 4px 0 0; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.filter-sel, .search-input { border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 14px; font-size: 14px; outline: none; }
.filter-sel:focus, .search-input:focus { border-color: #6366f1; }
.stat-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
@media (max-width: 768px) { .stat-cards { grid-template-columns: repeat(2, 1fr); } }
.stat-card { border-radius: 16px; padding: 20px; color: #fff; text-align: center; }
.stat-card.blue { background: linear-gradient(135deg, #6366f1, #818cf8); }
.stat-card.green { background: linear-gradient(135deg, #10b981, #34d399); }
.stat-card.purple { background: linear-gradient(135deg, #8b5cf6, #a78bfa); }
.stat-card.orange { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.stat-num { font-size: 32px; font-weight: 800; }
.stat-label { font-size: 13px; opacity: 0.9; margin-top: 4px; }
.cat-group { margin-bottom: 28px; }
.cat-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }
.cat-icon { font-size: 22px; }
.cat-name { font-size: 18px; font-weight: 700; color: #1e293b; }
.cat-count { background: #e2e8f0; color: #64748b; border-radius: 20px; padding: 2px 10px; font-size: 12px; font-weight: 600; }
.games-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
.game-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; transition: all .2s; box-shadow: 0 2px 6px rgba(0,0,0,.05); }
.game-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.1); transform: translateY(-2px); }
.game-card.inactive { opacity: 0.55; background: #f8fafc; }
.game-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.game-id { font-size: 11px; color: #94a3b8; font-weight: 600; }
.game-name { font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.game-route { font-size: 11px; color: #94a3b8; margin-bottom: 10px; word-break: break-all; }
.game-stats { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.stat-pill { font-size: 11px; padding: 2px 8px; border-radius: 20px; font-weight: 600; }
.stat-pill.plays { background: #ede9fe; color: #7c3aed; }
.stat-pill.score { background: #fef9c3; color: #ca8a04; }
.stat-pill.new { background: #dcfce7; color: #16a34a; }
.game-actions { display: flex; gap: 6px; }
.action-btn { flex: 1; padding: 6px 8px; border-radius: 8px; font-size: 11px; font-weight: 600; border: none; cursor: pointer; text-align: center; }
.q-btn { background: #ede9fe; color: #7c3aed; }
.q-btn:hover { background: #ddd6fe; }
.toggle-switch { position: relative; display: inline-block; width: 38px; height: 22px; cursor: pointer; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; inset: 0; background: #cbd5e1; border-radius: 22px; transition: .3s; }
.slider:before { content: ''; position: absolute; width: 16px; height: 16px; border-radius: 50%; background: #fff; bottom: 3px; left: 3px; transition: .3s; }
input:checked + .slider { background: #10b981; }
input:checked + .slider:before { transform: translateX(16px); }
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal-box { background: #fff; border-radius: 20px; width: 100%; max-width: 700px; max-height: 85vh; display: flex; flex-direction: column; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid #e2e8f0; }
.modal-header h2 { font-size: 18px; font-weight: 700; margin: 0; }
.close-btn { background: none; border: none; font-size: 20px; cursor: pointer; color: #64748b; }
.modal-body { padding: 20px 24px; overflow-y: auto; flex: 1; }
.form-title { font-size: 14px; font-weight: 700; color: #374151; margin: 0 0 12px; }
.form-row { display: flex; gap: 10px; margin-bottom: 10px; }
.form-input { flex: 1; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; font-size: 14px; outline: none; }
.form-input.sm { flex: 0 0 110px; }
.form-input:focus { border-color: #6366f1; }
.add-btn { background: #6366f1; color: #fff; border: none; padding: 10px 24px; border-radius: 10px; font-size: 14px; font-weight: 700; cursor: pointer; margin-bottom: 20px; }
.add-btn:disabled { opacity: .5; cursor: not-allowed; }
.add-question-form { background: #f8fafc; border-radius: 14px; padding: 16px; margin-bottom: 20px; border: 1px solid #e2e8f0; }
.q-loading, .q-empty { text-align: center; color: #94a3b8; padding: 30px; }
.q-item { display: flex; justify-content: space-between; align-items: flex-start; padding: 14px; background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 10px; gap: 12px; }
.q-text { font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.q-answer { font-size: 13px; color: #10b981; }
.q-opts { font-size: 12px; color: #94a3b8; margin-top: 2px; }
.q-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 8px; min-width: 60px; }
.diff-badge { font-size: 11px; padding: 2px 8px; border-radius: 20px; font-weight: 600; }
.diff-1 { background: #dcfce7; color: #16a34a; }
.diff-2 { background: #fef9c3; color: #ca8a04; }
.diff-3 { background: #fee2e2; color: #dc2626; }
.del-btn { background: none; border: none; cursor: pointer; font-size: 16px; }
.loading-box { text-align: center; padding: 60px 20px; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #6366f1; border-radius: 50%; animation: spin .8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.toast { position: fixed; bottom: 30px; right: 30px; padding: 14px 24px; border-radius: 12px; color: #fff; font-weight: 600; font-size: 14px; z-index: 9999; box-shadow: 0 4px 16px rgba(0,0,0,.2); }
.toast.success { background: #10b981; }
.toast.error { background: #ef4444; }
.toast-enter-active, .toast-leave-active { transition: all .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(20px); }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/admin/AdminGames.vue', admin_games)

# Build
print("\n=== npm 빌드 ===")
build = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -6", timeout=300)
print(build)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

# Final test
print("\n=== API 라우트 확인 ===")
print(ssh("cd /var/www/somekorean && php artisan route:list --path=admin/games 2>&1"))

print("\n✅ AdminGames.vue 수정 완료!")
print("- axios 인터셉터가 자동으로 sk_token 헤더 추가")
print("- /api/admin/games 라우트 → admin 미들웨어 그룹 내")
print("- 수동 Authorization 헤더 제거")

c.close()
