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
# 1. game_questions 테이블 생성 (관리자 문제 관리)
# ============================================================
print("=== game_questions 테이블 생성 ===")
r = ssh("""mysql --defaults-file=/tmp/sk_main.cnf somekorean -e "
CREATE TABLE IF NOT EXISTS game_questions (
  id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  game_id INT UNSIGNED NOT NULL,
  question TEXT NOT NULL,
  answer VARCHAR(255) NOT NULL,
  options JSON NULL,
  image_url VARCHAR(500) NULL,
  difficulty TINYINT DEFAULT 1,
  is_active TINYINT(1) DEFAULT 1,
  sort_order INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_game_id (game_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
" """)
print(r or "테이블 생성 완료")

# ============================================================
# 2. GameScoreController 생성
# ============================================================
print("\n=== GameScoreController 생성 ===")
score_controller = r"""<?php
namespace App\Http\Controllers\API;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Auth;

class GameScoreController extends Controller
{
    // POST /api/games/{id}/score — 게임 점수 저장
    public function saveScore(Request $req, $gameId)
    {
        $user = Auth::user();
        $score    = (int) $req->input('score', 0);
        $duration = (int) $req->input('duration', 0);
        $result   = $req->input('result', 'win'); // win/lose/draw
        $level    = (int) $req->input('level', 1);

        // 게임 정보 조회
        $game = DB::table('games')->where('id', $gameId)->first();
        if (!$game) {
            return response()->json(['error' => '게임을 찾을 수 없습니다'], 404);
        }

        // reward 계산 (점수 * 0.1 + 기본 보상)
        $reward = max(1, (int)($score * 0.1) + ($game->reward_base ?? 10));
        if ($result === 'lose') $reward = (int)($reward * 0.3);

        // game_sessions 저장
        $sessionId = DB::table('game_sessions')->insertGetId([
            'game_id'    => $gameId,
            'user_id'    => $user->id,
            'score'      => $score,
            'result'     => $result,
            'duration'   => $duration,
            'reward'     => $reward,
            'meta'       => json_encode(['level' => $level]),
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        // 코인 지급 (user_wallets 테이블)
        DB::table('user_wallets')
            ->where('user_id', $user->id)
            ->increment('coin_balance', $reward);
        DB::table('user_wallets')
            ->where('user_id', $user->id)
            ->increment('lifetime_earned', $reward);

        // play_count 증가
        DB::table('games')->where('id', $gameId)->increment('play_count');

        return response()->json([
            'success'    => true,
            'session_id' => $sessionId,
            'score'      => $score,
            'reward'     => $reward,
            'message'    => "{$reward}코인을 받았어요!",
        ]);
    }

    // GET /api/games/my-scores — 내 게임 기록
    public function myScores(Request $req)
    {
        $user = Auth::user();
        $gameId = $req->query('game_id');

        $query = DB::table('game_sessions as gs')
            ->join('games as g', 'gs.game_id', '=', 'g.id')
            ->select('gs.id', 'gs.game_id', 'g.name as game_name', 'gs.score',
                     'gs.result', 'gs.reward', 'gs.duration', 'gs.created_at')
            ->where('gs.user_id', $user->id)
            ->orderByDesc('gs.created_at')
            ->limit(50);

        if ($gameId) {
            $query->where('gs.game_id', $gameId);
        }

        $scores = $query->get();

        // 게임별 최고점수 요약
        $summary = DB::table('game_sessions')
            ->select('game_id', DB::raw('MAX(score) as best_score'), DB::raw('COUNT(*) as play_count'), DB::raw('SUM(reward) as total_reward'))
            ->where('user_id', $user->id)
            ->groupBy('game_id')
            ->get();

        return response()->json([
            'scores'  => $scores,
            'summary' => $summary,
        ]);
    }

    // GET /api/games/leaderboard/{gameId} — 특정 게임 리더보드
    public function gameLeaderboard($gameId)
    {
        $leaders = DB::table('game_sessions as gs')
            ->join('users as u', 'gs.user_id', '=', 'u.id')
            ->select('u.id', 'u.nickname', 'u.username',
                     DB::raw('MAX(gs.score) as best_score'),
                     DB::raw('COUNT(gs.id) as play_count'))
            ->where('gs.game_id', $gameId)
            ->groupBy('u.id', 'u.nickname', 'u.username')
            ->orderByDesc('best_score')
            ->limit(20)
            ->get();

        return response()->json($leaders);
    }

    // ---- 관리자 전용 ----

    // GET /api/admin/games — 전체 게임 목록 (관리자)
    public function adminList()
    {
        $games = DB::table('games as g')
            ->leftJoin('game_categories as gc', 'g.category_id', '=', 'gc.id')
            ->select('g.*', 'gc.name as category_name',
                     DB::raw('(SELECT COUNT(*) FROM game_sessions WHERE game_id=g.id) as session_count'),
                     DB::raw('(SELECT MAX(score) FROM game_sessions WHERE game_id=g.id) as top_score'))
            ->orderBy('g.category_id')
            ->orderBy('g.sort_order')
            ->get();

        return response()->json($games);
    }

    // PUT /api/admin/games/{id}/toggle — 게임 활성/비활성
    public function toggleActive($id)
    {
        $game = DB::table('games')->where('id', $id)->first();
        if (!$game) return response()->json(['error' => '게임 없음'], 404);
        DB::table('games')->where('id', $id)->update(['is_active' => !$game->is_active]);
        return response()->json(['success' => true, 'is_active' => !$game->is_active]);
    }

    // GET /api/admin/games/{id}/questions — 게임 문제 목록
    public function getQuestions($gameId)
    {
        $questions = DB::table('game_questions')
            ->where('game_id', $gameId)
            ->orderBy('sort_order')
            ->orderBy('id')
            ->get();
        return response()->json($questions);
    }

    // POST /api/admin/games/{id}/questions — 문제 추가
    public function addQuestion(Request $req, $gameId)
    {
        $id = DB::table('game_questions')->insertGetId([
            'game_id'    => $gameId,
            'question'   => $req->input('question'),
            'answer'     => $req->input('answer'),
            'options'    => json_encode($req->input('options', [])),
            'image_url'  => $req->input('image_url'),
            'difficulty' => $req->input('difficulty', 1),
            'is_active'  => 1,
            'created_at' => now(),
            'updated_at' => now(),
        ]);
        return response()->json(['success' => true, 'id' => $id]);
    }

    // DELETE /api/admin/questions/{id} — 문제 삭제
    public function deleteQuestion($id)
    {
        DB::table('game_questions')->where('id', $id)->delete();
        return response()->json(['success' => true]);
    }
}
"""
write_file('/var/www/somekorean/app/Http/Controllers/API/GameScoreController.php', score_controller)

# ============================================================
# 3. api.php 라우트 추가
# ============================================================
print("\n=== api.php 라우트 추가 ===")
api_content = ssh("cat /var/www/somekorean/routes/api.php")

if 'GameScoreController' not in api_content:
    # use 추가
    use_line = "use App\\Http\\Controllers\\API\\GameCategoryController;"
    new_use = use_line + "\nuse App\\Http\\Controllers\\API\\GameScoreController;"
    api_content = api_content.replace(use_line, new_use)

    # 공개 라우트 (리더보드)
    pub_anchor = "Route::get('game-leaderboard', [App\\Http\\Controllers\\API\\GameCategoryController::class, 'leaderboard']);"
    pub_new = pub_anchor + """
Route::get('games/{id}/leaderboard', [GameScoreController::class, 'gameLeaderboard']);"""
    api_content = api_content.replace(pub_anchor, pub_new)

    # auth 라우트 — Route::post('games/rooms/{id}/stop' 뒤에 추가
    auth_anchor = "Route::post('games/rooms/{id}/stop',          [GameController::class, 'stop']);"
    auth_new = auth_anchor + """
        // 교육 게임 점수
        Route::post('games/{id}/score',              [GameScoreController::class, 'saveScore']);
        Route::get('games/my-scores',                [GameScoreController::class, 'myScores']);
        // 관리자 게임 관리
        Route::get('admin/games',                    [GameScoreController::class, 'adminList']);
        Route::put('admin/games/{id}/toggle',        [GameScoreController::class, 'toggleActive']);
        Route::get('admin/games/{id}/questions',     [GameScoreController::class, 'getQuestions']);
        Route::post('admin/games/{id}/questions',    [GameScoreController::class, 'addQuestion']);
        Route::delete('admin/questions/{id}',        [GameScoreController::class, 'deleteQuestion']);"""
    api_content = api_content.replace(auth_anchor, auth_new)

    write_file('/var/www/somekorean/routes/api.php', api_content)
    print("api.php 업데이트 완료")
else:
    print("GameScoreController 이미 등록됨")

# ============================================================
# 4. AdminGames.vue 완전 재작성 (실제 API 연결)
# ============================================================
print("\n=== AdminGames.vue 재작성 ===")
admin_games = r"""<template>
  <div class="admin-games">
    <!-- 헤더 -->
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

    <!-- 통계 카드 -->
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

    <!-- 게임 목록 -->
    <div class="games-section">
      <div v-if="loading" class="loading-box">
        <div class="spinner"></div>
        <p>게임 목록을 불러오는 중...</p>
      </div>
      <div v-else>
        <!-- 카테고리별 그룹 -->
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
                <label class="toggle-switch" :title="game.is_active ? '비활성화' : '활성화'">
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
                <a v-if="game.route_name" :href="'/'+game.route_name.replace('game-','')" target="_blank"
                   class="action-btn preview-btn">👁 미리보기</a>
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
            <!-- 문제 추가 폼 -->
            <div class="add-question-form">
              <h3 class="form-title">➕ 새 문제 추가</h3>
              <div class="form-row">
                <input v-model="newQ.question" class="form-input" placeholder="문제 내용"/>
                <input v-model="newQ.answer" class="form-input sm" placeholder="정답"/>
              </div>
              <div class="form-row">
                <input v-model="newQ.options_str" class="form-input" placeholder="보기 (쉼표로 구분, 예: 사과,바나나,딸기)"/>
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
            <!-- 기존 문제 목록 -->
            <div class="questions-list">
              <div v-if="qModal.loading" class="q-loading">불러오는 중...</div>
              <div v-else-if="qModal.questions.length === 0" class="q-empty">
                등록된 문제가 없습니다. 위에서 추가해보세요!
              </div>
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

    <!-- 토스트 알림 -->
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
    const res = await axios.get('/api/admin/games', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
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
    await axios.put(`/api/admin/games/${game.id}/toggle`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    showToast(`${game.name}: ${game.is_active ? '활성화' : '비활성화'} 완료`)
  } catch (e) {
    game.is_active = prev
    showToast('변경 실패', 'error')
  }
}

async function openQuestions(game) {
  qModal.value = { open: true, game, questions: [], loading: true }
  newQ.value = { question: '', answer: '', options_str: '', difficulty: '1' }
  try {
    const res = await axios.get(`/api/admin/games/${game.id}/questions`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
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
    await axios.post(`/api/admin/games/${qModal.value.game.id}/questions`, {
      question: newQ.value.question,
      answer: newQ.value.answer,
      options: opts,
      difficulty: parseInt(newQ.value.difficulty),
    }, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
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
    await axios.delete(`/api/admin/questions/${qid}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
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
.action-btn { flex: 1; padding: 6px 8px; border-radius: 8px; font-size: 11px; font-weight: 600; border: none; cursor: pointer; text-align: center; text-decoration: none; display: block; }
.q-btn { background: #ede9fe; color: #7c3aed; }
.q-btn:hover { background: #ddd6fe; }
.preview-btn { background: #e0f2fe; color: #0284c7; }
.preview-btn:hover { background: #bae6fd; }

/* Toggle Switch */
.toggle-switch { position: relative; display: inline-block; width: 38px; height: 22px; cursor: pointer; }
.toggle-switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; inset: 0; background: #cbd5e1; border-radius: 22px; transition: .3s; }
.slider:before { content: ''; position: absolute; width: 16px; height: 16px; border-radius: 50%; background: #fff; bottom: 3px; left: 3px; transition: .3s; }
input:checked + .slider { background: #10b981; }
input:checked + .slider:before { transform: translateX(16px); }

/* 모달 */
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

/* 로딩 */
.loading-box { text-align: center; padding: 60px 20px; color: #64748b; }
.spinner { width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #6366f1; border-radius: 50%; animation: spin .8s linear infinite; margin: 0 auto 16px; }
@keyframes spin { to { transform: rotate(360deg); } }

/* 토스트 */
.toast { position: fixed; bottom: 30px; right: 30px; padding: 14px 24px; border-radius: 12px; color: #fff; font-weight: 600; font-size: 14px; z-index: 9999; box-shadow: 0 4px 16px rgba(0,0,0,.2); }
.toast.success { background: #10b981; }
.toast.error { background: #ef4444; }
.toast-enter-active, .toast-leave-active { transition: all .3s; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(20px); }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/admin/AdminGames.vue', admin_games)

# ============================================================
# 5. 나머지 어린이 게임 피드백 오버레이 패치
# ============================================================
print("\n=== GameShapes.vue 피드백 오버레이 패치 ===")
shapes_game = r"""<template>
  <div class="shapes-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} ⭐</div>
      <div class="score-badge">{{ score }}점</div>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">🔷</div>
      <h1 class="title">도형 맞추기</h1>
      <p class="subtitle">어떤 도형일까요?</p>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>
    <div v-if="phase==='play'" class="play-box">
      <div class="progress-bar"><div class="progress-fill" :style="{width: (qIdx/totalQ*100)+'%'}"></div></div>
      <div class="q-count">{{ qIdx+1 }} / {{ totalQ }}</div>
      <div class="shape-display">
        <svg viewBox="0 0 200 200" class="shape-svg">
          <polygon v-if="cur.shape==='triangle'" points="100,20 180,180 20,180"
            :fill="cur.color" stroke="white" stroke-width="4"/>
          <rect v-if="cur.shape==='square'" x="30" y="30" width="140" height="140"
            :fill="cur.color" stroke="white" stroke-width="4" rx="8"/>
          <circle v-if="cur.shape==='circle'" cx="100" cy="100" r="75"
            :fill="cur.color" stroke="white" stroke-width="4"/>
          <ellipse v-if="cur.shape==='oval'" cx="100" cy="100" rx="85" ry="55"
            :fill="cur.color" stroke="white" stroke-width="4"/>
          <polygon v-if="cur.shape==='pentagon'" points="100,15 185,70 155,170 45,170 15,70"
            :fill="cur.color" stroke="white" stroke-width="4"/>
          <polygon v-if="cur.shape==='star'" points="100,10 120,70 185,70 130,110 150,170 100,135 50,170 70,110 15,70 80,70"
            :fill="cur.color" stroke="white" stroke-width="4"/>
          <rect v-if="cur.shape==='rectangle'" x="20" y="60" width="160" height="80"
            :fill="cur.color" stroke="white" stroke-width="4" rx="6"/>
          <polygon v-if="cur.shape==='diamond'" points="100,15 185,100 100,185 15,100"
            :fill="cur.color" stroke="white" stroke-width="4"/>
        </svg>
      </div>
      <p class="question-text">이 도형의 이름은 무엇인가요?</p>
      <div class="choices">
        <button v-for="opt in cur.opts" :key="opt"
          class="choice-btn" :disabled="answered" @click="answer(opt)">
          {{ opt }}
        </button>
      </div>
    </div>
    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">🎉</div>
      <h2 class="end-title">훌륭해요!</h2>
      <p class="end-score">{{ score }}점 · {{ correct }}/{{ totalQ }} 정답</p>
      <div v-if="leveled" class="levelup-badge">🌟 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
    </div>

    <!-- 피드백 오버레이 -->
    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect?'fb-correct':'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect" class="fb-answer">정답은 「<strong>{{ cur?.korName }}</strong>」이에요</div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const level = ref(parseInt(localStorage.getItem('shapes_level')||'1'))
const score = ref(0)
const qIdx = ref(0)
const correct = ref(0)
const leveled = ref(false)
const answered = ref(false)
const phase = ref('start')
const showFeedback = ref(false)
const lastCorrect = ref(false)
const fbProgress = ref(100)
let fbTimer = null
const totalQ = 10

const allShapes = [
  {shape:'circle',    korName:'원',        opts:['원','삼각형','사각형','별']},
  {shape:'triangle',  korName:'삼각형',    opts:['삼각형','원','마름모','오각형']},
  {shape:'square',    korName:'사각형',    opts:['사각형','직사각형','원','삼각형']},
  {shape:'rectangle', korName:'직사각형',  opts:['직사각형','사각형','타원','별']},
  {shape:'oval',      korName:'타원',      opts:['타원','원','사각형','삼각형']},
  {shape:'pentagon',  korName:'오각형',    opts:['오각형','육각형','사각형','삼각형']},
  {shape:'star',      korName:'별',        opts:['별','오각형','삼각형','원']},
  {shape:'diamond',   korName:'마름모',    opts:['마름모','사각형','별','삼각형']},
]
const colors = ['#ef4444','#f97316','#eab308','#22c55e','#3b82f6','#8b5cf6','#ec4899']
const questions = ref([])
const cur = computed(() => questions.value[qIdx.value])

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-.5) }

function buildQuestions() {
  const qs = []
  const pool = shuffle(allShapes)
  for (let i=0; i<totalQ; i++) {
    const s = pool[i % pool.length]
    qs.push({ ...s, color: colors[Math.floor(Math.random()*colors.length)], opts: shuffle(s.opts) })
  }
  return qs
}

function startGame() {
  score.value=0; qIdx.value=0; correct.value=0; leveled.value=false
  answered.value=false; showFeedback.value=false; phase.value='play'
  questions.value = buildQuestions()
  speak('도형 이름을 맞춰보세요!')
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect
  showFeedback.value = true
  fbProgress.value = 100
  clearInterval(fbTimer)
  const duration = isCorrect ? 1400 : 2000
  const step = 50 / duration * 100
  fbTimer = setInterval(() => {
    fbProgress.value = Math.max(0, fbProgress.value - step)
    if (fbProgress.value <= 0) {
      clearInterval(fbTimer); showFeedback.value = false
      answered.value = false
      qIdx.value++
      if (qIdx.value >= totalQ) endGame()
    }
  }, 50)
}

function answer(opt) {
  if (answered.value) return
  answered.value = true
  const isCorrect = opt === cur.value.korName
  if (isCorrect) { score.value += 10; correct.value++ }
  speak(isCorrect ? '정답이에요!' : `정답은 ${cur.value.korName}이에요`)
  triggerFeedback(isCorrect)
}

function endGame() {
  phase.value = 'end'
  const needed = Math.ceil(totalQ * 0.7)
  if (correct.value >= needed) {
    level.value++; localStorage.setItem('shapes_level', level.value)
    leveled.value = true
    speak('훌륭해요! 레벨업!')
  } else { speak('잘 했어요! 다시 도전해봐요!') }
}
</script>

<style scoped>
.shapes-game { min-height:100vh; background:linear-gradient(135deg,#1e1b4b,#312e81,#4c1d95); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.start-btn { background:#a855f7; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-box { max-width:480px; margin:0 auto; }
.progress-bar { height:8px; background:rgba(255,255,255,.2); border-radius:4px; margin-bottom:8px; }
.progress-fill { height:100%; background:#a855f7; border-radius:4px; transition:width .3s; }
.q-count { color:rgba(255,255,255,.7); font-size:13px; text-align:right; margin-bottom:16px; }
.shape-display { background:rgba(255,255,255,.1); border-radius:20px; padding:20px; margin-bottom:20px; }
.shape-svg { width:180px; height:180px; display:block; margin:0 auto; }
.question-text { color:#fff; font-size:18px; font-weight:700; text-align:center; margin-bottom:16px; }
.choices { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.choice-btn { background:rgba(255,255,255,.9); color:#1e1b4b; border:none; padding:16px; border-radius:14px; font-size:17px; font-weight:700; cursor:pointer; transition:all .15s; }
.choice-btn:hover:not(:disabled) { background:#fff; transform:scale(1.03); }
.choice-btn:disabled { cursor:default; opacity:.8; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.end-score { color:rgba(255,255,255,.8); font-size:18px; }
.levelup-badge { background:#a855f7; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
.feedback-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; z-index:999; backdrop-filter:blur(4px); }
.fb-correct { background:rgba(16,185,129,.85); }
.fb-wrong { background:rgba(239,68,68,.85); }
.fb-content { text-align:center; color:#fff; padding:32px 48px; }
.fb-emoji { font-size:72px; margin-bottom:8px; }
.fb-title { font-size:32px; font-weight:900; margin-bottom:8px; }
.fb-answer { font-size:18px; margin-bottom:16px; }
.fb-bar-wrap { width:200px; height:6px; background:rgba(255,255,255,.3); border-radius:4px; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:4px; transition:width .05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity .25s; }
.fb-enter-from,.fb-leave-to { opacity:0; }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/games/GameShapes.vue', shapes_game)

# ============================================================
# 6. GameWordCard.vue 피드백 오버레이 패치
# ============================================================
print("\n=== GameWordCard.vue 피드백 오버레이 ===")
wordcard_game = r"""<template>
  <div class="wcard-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 📚</div>
      <div class="score-badge">{{ score }}점</div>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">📚</div>
      <h1 class="title">한국어 단어 카드</h1>
      <p class="subtitle">그림을 보고 단어를 맞춰요!</p>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>
    <div v-if="phase==='play'" class="play-box">
      <div class="progress-bar"><div class="progress-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
      <div class="q-count">{{ qIdx+1 }} / {{ totalQ }}</div>
      <div class="card-display">
        <div class="card-image">{{ cur.emoji }}</div>
        <div class="card-hint">{{ cur.hint }}</div>
      </div>
      <p class="question-text">이 그림의 한국어 이름은 무엇인가요?</p>
      <div class="choices">
        <button v-for="opt in cur.opts" :key="opt"
          class="choice-btn" :disabled="answered" @click="answer(opt)">{{ opt }}</button>
      </div>
    </div>
    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">🌟</div>
      <h2 class="end-title">잘 했어요!</h2>
      <p class="end-score">{{ score }}점 · {{ correct }}/{{ totalQ }} 정답</p>
      <div v-if="leveled" class="levelup-badge">🎉 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
    </div>
    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect?'fb-correct':'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect" class="fb-answer">정답은 「<strong>{{ cur?.word }}</strong>」이에요</div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const level = ref(parseInt(localStorage.getItem('wordcard_level')||'1'))
const score = ref(0); const qIdx = ref(0); const correct = ref(0)
const leveled = ref(false); const answered = ref(false); const phase = ref('start')
const showFeedback = ref(false); const lastCorrect = ref(false); const fbProgress = ref(100)
let fbTimer = null
const totalQ = 12

const allWords = [
  {word:'사과', emoji:'🍎', hint:'빨간 과일', opts:['사과','배','포도','딸기']},
  {word:'바나나', emoji:'🍌', hint:'노란 과일', opts:['바나나','레몬','망고','수박']},
  {word:'고양이', emoji:'🐱', hint:'야옹~ 하는 동물', opts:['고양이','강아지','토끼','햄스터']},
  {word:'강아지', emoji:'🐶', hint:'멍멍 하는 동물', opts:['강아지','고양이','고양이','늑대']},
  {word:'집', emoji:'🏠', hint:'우리가 사는 곳', opts:['집','학교','병원','공원']},
  {word:'책', emoji:'📚', hint:'글이 있는 것', opts:['책','공책','신문','잡지']},
  {word:'연필', emoji:'✏️', hint:'그림을 그리는 도구', opts:['연필','볼펜','크레용','붓']},
  {word:'자전거', emoji:'🚲', hint:'두 바퀴 탈 것', opts:['자전거','오토바이','자동차','버스']},
  {word:'꽃', emoji:'🌸', hint:'예쁜 식물', opts:['꽃','나무','풀','잎']},
  {word:'해', emoji:'☀️', hint:'낮에 빛나는 것', opts:['해','달','별','구름']},
  {word:'달', emoji:'🌙', hint:'밤하늘에 있는 것', opts:['달','해','별','구름']},
  {word:'물', emoji:'💧', hint:'마시는 투명한 것', opts:['물','주스','우유','차']},
  {word:'밥', emoji:'🍚', hint:'한국 주식', opts:['밥','빵','면','죽']},
  {word:'빵', emoji:'🍞', hint:'구워서 만드는 음식', opts:['빵','떡','과자','쿠키']},
  {word:'신발', emoji:'👟', hint:'발에 신는 것', opts:['신발','양말','장화','슬리퍼']},
]

const questions = ref([])
const cur = computed(() => questions.value[qIdx.value])

function speak(t) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}

function shuffle(a) { return [...a].sort(()=>Math.random()-.5) }

function startGame() {
  score.value=0; qIdx.value=0; correct.value=0; leveled.value=false
  answered.value=false; showFeedback.value=false; phase.value='play'
  questions.value = shuffle(allWords).slice(0, totalQ).map(w=>({...w, opts:shuffle(w.opts)}))
  speak('단어 카드를 시작해요!')
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect; showFeedback.value = true; fbProgress.value = 100
  clearInterval(fbTimer)
  const dur = isCorrect ? 1400 : 2000; const step = 50/dur*100
  fbTimer = setInterval(() => {
    fbProgress.value = Math.max(0, fbProgress.value - step)
    if (fbProgress.value <= 0) {
      clearInterval(fbTimer); showFeedback.value = false; answered.value = false
      qIdx.value++
      if (qIdx.value >= totalQ) endGame()
    }
  }, 50)
}

function answer(opt) {
  if (answered.value) return
  answered.value = true
  const ok = opt === cur.value.word
  if (ok) { score.value += 10; correct.value++ }
  speak(ok ? '정답이에요!' : `정답은 ${cur.value.word}이에요`)
  triggerFeedback(ok)
}

function endGame() {
  phase.value = 'end'
  if (correct.value >= Math.ceil(totalQ * 0.7)) {
    level.value++; localStorage.setItem('wordcard_level', level.value); leveled.value = true
    speak('레벨업! 잘 했어요!')
  } else speak('다시 한번 도전해봐요!')
}
</script>

<style scoped>
.wcard-game { min-height:100vh; background:linear-gradient(135deg,#0c4a6e,#0369a1,#0284c7); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.start-btn { background:#0ea5e9; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-box { max-width:480px; margin:0 auto; }
.progress-bar { height:8px; background:rgba(255,255,255,.2); border-radius:4px; margin-bottom:8px; }
.progress-fill { height:100%; background:#38bdf8; border-radius:4px; transition:width .3s; }
.q-count { color:rgba(255,255,255,.7); font-size:13px; text-align:right; margin-bottom:16px; }
.card-display { background:rgba(255,255,255,.15); border-radius:20px; padding:32px 20px; margin-bottom:20px; text-align:center; }
.card-image { font-size:100px; line-height:1; margin-bottom:8px; }
.card-hint { color:rgba(255,255,255,.8); font-size:15px; }
.question-text { color:#fff; font-size:17px; font-weight:700; text-align:center; margin-bottom:14px; }
.choices { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.choice-btn { background:rgba(255,255,255,.9); color:#0c4a6e; border:none; padding:16px; border-radius:14px; font-size:17px; font-weight:700; cursor:pointer; transition:all .15s; }
.choice-btn:hover:not(:disabled) { background:#fff; transform:scale(1.03); }
.choice-btn:disabled { cursor:default; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.end-score { color:rgba(255,255,255,.8); font-size:18px; }
.levelup-badge { background:#0ea5e9; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
.feedback-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; z-index:999; backdrop-filter:blur(4px); }
.fb-correct { background:rgba(16,185,129,.85); }
.fb-wrong { background:rgba(239,68,68,.85); }
.fb-content { text-align:center; color:#fff; padding:32px 48px; }
.fb-emoji { font-size:72px; margin-bottom:8px; }
.fb-title { font-size:32px; font-weight:900; margin-bottom:8px; }
.fb-answer { font-size:18px; margin-bottom:16px; }
.fb-bar-wrap { width:200px; height:6px; background:rgba(255,255,255,.3); border-radius:4px; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:4px; transition:width .05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity .25s; }
.fb-enter-from,.fb-leave-to { opacity:0; }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/games/GameWordCard.vue', wordcard_game)

# ============================================================
# 7. Build
# ============================================================
print("\n=== npm 빌드 ===")
build = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -8", timeout=300)
print(build)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

print("\n========================================")
print("✅ 백엔드 + 관리자 페이지 업데이트 완료")
print("========================================")
print("1. game_questions 테이블 생성됨")
print("2. GameScoreController: 점수저장/내기록/리더보드 API")
print("3. api.php: 새 라우트 6개 추가")
print("4. AdminGames.vue: 실제 API 연결 완료")
print("5. GameShapes.vue: 피드백 오버레이 추가")
print("6. GameWordCard.vue: 피드백 오버레이 추가")
print("========================================")

c.close()
