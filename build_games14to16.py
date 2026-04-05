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

# ===== GAME 14: 미로 탈출 =====
game14 = r"""<template>
  <div class="maze-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🌀</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🌀</div>
      <h1 class="title">미로 탈출</h1>
      <p class="subtitle">방향키 또는 버튼으로 캐릭터를 탈출구까지 이동!</p>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="game-info-row">
        <div class="steps-display">👣 {{ steps }}걸음</div>
        <div class="timer-display">⏱ {{ timeLeft }}초</div>
        <div class="best-display">🏆 최단 {{ bestSteps || '??' }}걸음</div>
      </div>
      <div class="maze-wrapper">
        <div class="maze-grid" :style="mazeStyle">
          <div v-for="(row, r) in maze" :key="r" class="maze-row">
            <div v-for="(cell, col) in row" :key="col" class="maze-cell"
              :class="getCellClass(r, col)">
              <span v-if="r===playerR && col===playerC" class="player">🐸</span>
              <span v-else-if="r===exitR && col===exitC" class="exit-mark">🚪</span>
            </div>
          </div>
        </div>
      </div>
      <div class="dpad">
        <button class="dpad-btn" @click="move(-1,0)">↑</button>
        <div class="dpad-row">
          <button class="dpad-btn" @click="move(0,-1)">←</button>
          <div class="dpad-center">🐸</div>
          <button class="dpad-btn" @click="move(0,1)">→</button>
        </div>
        <button class="dpad-btn" @click="move(1,0)">↓</button>
      </div>
    </div>

    <div v-if="phase==='cleared'" class="cleared-box">
      <div style="font-size:80px">🎊</div>
      <h2 class="cleared-title">탈출 성공!</h2>
      <div class="cleared-stats">{{ steps }}걸음 · {{ elapsedTime }}초</div>
      <div v-if="isNewBest" class="new-best">🏆 새 기록!</div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 🔄</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const level = ref(parseInt(localStorage.getItem('maze_level') || '1'))
const score = ref(parseInt(localStorage.getItem('maze_score') || '0'))
const bestSteps = ref(parseInt(localStorage.getItem('maze_best') || '0') || null)

const phase = ref('start')
const maze = ref([])
const playerR = ref(1)
const playerC = ref(1)
const exitR = ref(0)
const exitC = ref(0)
const steps = ref(0)
const timeLeft = ref(60)
const elapsedTime = ref(0)
const isNewBest = ref(false)
const leveled = ref(false)
let timer = null
let startTime = null

function getMazeSize() {
  const base = 7 + Math.min((level.value - 1) * 2, 10)
  return base % 2 === 0 ? base + 1 : base
}

const mazeStyle = computed(() => {
  const s = getMazeSize()
  const cellSize = Math.min(36, Math.floor(320 / s))
  return { '--cell': cellSize + 'px' }
})

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9; u.pitch = 1.1
  window.speechSynthesis.speak(u)
}

function generateMaze(size) {
  const grid = Array.from({length: size}, () => Array(size).fill(1))
  function carve(r, c) {
    const dirs = [[0,2],[0,-2],[2,0],[-2,0]].sort(()=>Math.random()-0.5)
    grid[r][c] = 0
    for (const [dr, dc] of dirs) {
      const nr = r+dr, nc = c+dc
      if (nr>0 && nr<size-1 && nc>0 && nc<size-1 && grid[nr][nc]===1) {
        grid[r+dr/2][c+dc/2] = 0
        carve(nr, nc)
      }
    }
  }
  carve(1, 1)
  return grid
}

function startGame() {
  const size = getMazeSize()
  maze.value = generateMaze(size)
  playerR.value = 1; playerC.value = 1
  exitR.value = size - 2; exitC.value = size - 2
  steps.value = 0; isNewBest.value = false; leveled.value = false
  startTime = Date.now()
  timeLeft.value = level.value <= 2 ? 120 : level.value <= 4 ? 90 : 60
  phase.value = 'play'
  clearInterval(timer)
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      speak('시간 초과!')
      phase.value = 'cleared'
      elapsedTime.value = Math.round((Date.now() - startTime) / 1000)
    }
  }, 1000)
  speak('출발!')
}

function getCellClass(r, c) {
  if (maze.value[r]?.[c] === 1) return 'wall'
  if (r === exitR.value && c === exitC.value) return 'exit'
  return 'path'
}

function move(dr, dc) {
  if (phase.value !== 'play') return
  const nr = playerR.value + dr, nc = playerC.value + dc
  if (nr < 0 || nr >= maze.value.length || nc < 0 || nc >= maze.value[0].length) return
  if (maze.value[nr][nc] === 1) return
  playerR.value = nr; playerC.value = nc; steps.value++
  if (nr === exitR.value && nc === exitC.value) {
    clearInterval(timer)
    elapsedTime.value = Math.round((Date.now() - startTime) / 1000)
    const pts = Math.max(50, 200 - steps.value * 2 + timeLeft.value)
    score.value += pts
    localStorage.setItem('maze_score', score.value)
    if (!bestSteps.value || steps.value < bestSteps.value) {
      bestSteps.value = steps.value
      localStorage.setItem('maze_best', steps.value)
      isNewBest.value = true
    }
    const threshold = level.value <= 2 ? 3 : level.value <= 4 ? 5 : 7
    if (steps.value <= getMazeSize() * threshold) {
      level.value++
      localStorage.setItem('maze_level', level.value)
      leveled.value = true
    }
    phase.value = 'cleared'
    speak(leveled.value ? '탈출 성공! 레벨업!' : '탈출 성공!')
  }
}

function handleKey(e) {
  const map = {ArrowUp:[-1,0], ArrowDown:[1,0], ArrowLeft:[0,-1], ArrowRight:[0,1]}
  if (map[e.key]) { e.preventDefault(); move(...map[e.key]) }
}

function goBack() { clearInterval(timer); router.push('/games') }
onMounted(() => window.addEventListener('keydown', handleKey))
onUnmounted(() => { clearInterval(timer); window.removeEventListener('keydown', handleKey) })
</script>

<style scoped>
.maze-game { min-height:100vh; background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.7); font-size:15px; }
.level-info { color:#60a5fa; margin:10px 0; font-size:15px; }
.start-btn { background:#6366f1; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:400px; margin:0 auto; }
.game-info-row { display:flex; justify-content:space-between; margin-bottom:12px; }
.steps-display,.timer-display,.best-display { color:#fff; font-size:13px; font-weight:600; background:rgba(255,255,255,0.1); padding:5px 10px; border-radius:10px; }
.maze-wrapper { display:flex; justify-content:center; margin-bottom:16px; overflow:auto; }
.maze-grid { display:inline-flex; flex-direction:column; border:2px solid #6366f1; border-radius:6px; overflow:hidden; }
.maze-row { display:flex; }
.maze-cell { width:var(--cell); height:var(--cell); display:flex; align-items:center; justify-content:center; font-size:calc(var(--cell) - 8px); }
.maze-cell.wall { background:#334155; }
.maze-cell.path { background:#1e293b; }
.maze-cell.exit { background:rgba(99,102,241,0.3); }
.player { font-size:calc(var(--cell) - 6px); line-height:1; }
.exit-mark { font-size:calc(var(--cell) - 8px); line-height:1; }
.dpad { display:flex; flex-direction:column; align-items:center; gap:6px; }
.dpad-row { display:flex; gap:6px; align-items:center; }
.dpad-btn { width:60px; height:60px; background:rgba(99,102,241,0.7); border:none; border-radius:50%; font-size:24px; color:#fff; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all 0.1s; }
.dpad-btn:active { transform:scale(0.92); background:#6366f1; }
.dpad-center { width:60px; height:60px; display:flex; align-items:center; justify-content:center; font-size:24px; }
.cleared-box { text-align:center; padding:40px 20px; }
.cleared-title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.cleared-stats { color:rgba(255,255,255,0.8); font-size:18px; margin:8px 0; }
.new-best { color:#fbbf24; font-size:20px; font-weight:800; margin:8px 0; }
.levelup { background:#6366f1; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#1a1a2e; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#6366f1; color:#fff; }
</style>
"""

# ===== GAME 15: 그림 조각 퍼즐 (숫자 슬라이딩 퍼즐) =====
game15 = r"""<template>
  <div class="puzzle-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🧩</div>
      <div class="score">⭐ {{ moves }}수</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🧩</div>
      <h1 class="title">퍼즐 맞추기</h1>
      <p class="subtitle">숫자를 순서대로 맞춰요!</p>
      <div class="level-info">
        <div>레벨 1-2: 3×3 (8칸)</div>
        <div>레벨 3-4: 4×4 (15칸)</div>
        <div>레벨 5+: 5×5 (24칸)</div>
        <div style="margin-top:8px">현재 레벨: {{ level }}</div>
      </div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="puzzle-info">
        <span>{{ moves }}수</span>
        <span>⏱ {{ timeLeft }}초</span>
        <span>{{ gridSize }}×{{ gridSize }}</span>
      </div>
      <div class="puzzle-grid" :style="gridStyle">
        <div v-for="(val, idx) in tiles" :key="idx"
          class="puzzle-tile" :class="{empty: val===0, correct: isCorrect(val,idx)}"
          :style="tileStyle(val, idx)" @click="clickTile(idx)">
          <span v-if="val !== 0">{{ val }}</span>
        </div>
      </div>
      <button class="shuffle-btn" @click="shuffleTiles">🔀 섞기</button>
    </div>

    <div v-if="phase==='solved'" class="solved-box">
      <div style="font-size:80px">🎊</div>
      <h2 class="solved-title">완성!</h2>
      <div class="solved-stats">{{ moves }}수 · {{ elapsedTime }}초</div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 🔄</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const level = ref(parseInt(localStorage.getItem('puzzle_level') || '1'))
const moves = ref(0)
const phase = ref('start')
const tiles = ref([])
const timeLeft = ref(300)
const elapsedTime = ref(0)
const leveled = ref(false)
let timer = null
let startTime = null

const gridSize = computed(() => level.value <= 2 ? 3 : level.value <= 4 ? 4 : 5)

const gridStyle = computed(() => ({
  gridTemplateColumns: `repeat(${gridSize.value}, 1fr)`,
  width: `${gridSize.value * 72}px`
}))

function tileStyle(val, idx) {
  if (val === 0) return {}
  return { background: isCorrect(val, idx) ? '#10b981' : '#6366f1' }
}

function isCorrect(val, idx) {
  return val === idx + 1 || (val === 0 && idx === tiles.value.length - 1)
}

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9; u.pitch = 1.0
  window.speechSynthesis.speak(u)
}

function createSolved() {
  const size = gridSize.value
  const total = size * size
  return [...Array(total - 1).keys()].map(i => i + 1).concat(0)
}

function isSolvable(arr, size) {
  let inv = 0
  for (let i = 0; i < arr.length; i++)
    for (let j = i+1; j < arr.length; j++)
      if (arr[i] && arr[j] && arr[i] > arr[j]) inv++
  if (size % 2 === 1) return inv % 2 === 0
  const emptyRow = Math.floor(arr.indexOf(0) / size)
  return (inv + emptyRow) % 2 === 1
}

function shuffleTiles() {
  const size = gridSize.value
  let arr = createSolved()
  do { arr = [...arr].sort(()=>Math.random()-0.5) } while (!isSolvable(arr, size))
  tiles.value = arr
  moves.value = 0
}

function startGame() {
  leveled.value = false
  shuffleTiles()
  startTime = Date.now()
  timeLeft.value = level.value <= 2 ? 300 : level.value <= 4 ? 240 : 180
  phase.value = 'play'
  clearInterval(timer)
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) { clearInterval(timer); speak('시간 초과!') }
  }, 1000)
  speak(gridSize.value + '곱하기 ' + gridSize.value + ' 퍼즐 시작!')
}

function clickTile(idx) {
  if (phase.value !== 'play') return
  const emptyIdx = tiles.value.indexOf(0)
  const size = gridSize.value
  const r1 = Math.floor(idx/size), c1 = idx%size
  const r2 = Math.floor(emptyIdx/size), c2 = emptyIdx%size
  if (Math.abs(r1-r2)+Math.abs(c1-c2) !== 1) return
  const arr = [...tiles.value]
  arr[emptyIdx] = arr[idx]; arr[idx] = 0
  tiles.value = arr; moves.value++
  if (checkSolved()) {
    clearInterval(timer)
    elapsedTime.value = Math.round((Date.now() - startTime) / 1000)
    const movesThreshold = level.value <= 2 ? 30 : level.value <= 4 ? 60 : 100
    if (moves.value <= movesThreshold) {
      level.value++
      localStorage.setItem('puzzle_level', level.value)
      leveled.value = true
    }
    phase.value = 'solved'
    speak(leveled.value ? '완성! 레벨업!' : '완성!')
  }
}

function checkSolved() {
  const sol = createSolved()
  return tiles.value.every((v, i) => v === sol[i])
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.puzzle-game { min-height:100vh; background:linear-gradient(135deg,#4c1d95,#5b21b6,#7c3aed); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.8); font-size:16px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#ddd6fe; font-size:14px; line-height:1.8; margin:12px auto; max-width:240px; text-align:left; }
.start-btn { background:#fff; color:#5b21b6; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { display:flex; flex-direction:column; align-items:center; }
.puzzle-info { display:flex; gap:16px; margin-bottom:16px; color:#fff; font-size:15px; font-weight:600; }
.puzzle-grid { display:grid; gap:4px; margin-bottom:16px; }
.puzzle-tile { width:68px; height:68px; display:flex; align-items:center; justify-content:center; border-radius:10px; font-size:22px; font-weight:800; color:#fff; cursor:pointer; transition:all 0.15s; user-select:none; }
.puzzle-tile:not(.empty):hover { transform:scale(0.96); }
.puzzle-tile.empty { background:rgba(255,255,255,0.1); cursor:default; }
.shuffle-btn { background:rgba(255,255,255,0.2); color:#fff; border:none; padding:10px 24px; border-radius:20px; font-size:15px; cursor:pointer; }
.solved-box { text-align:center; padding:40px 20px; }
.solved-title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.solved-stats { color:rgba(255,255,255,0.8); font-size:18px; margin:8px 0; }
.levelup { background:#fff; color:#5b21b6; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#4c1d95; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#7c3aed; color:#fff; }
</style>
"""

# ===== GAME 16: 영어 단어 카드 =====
game16 = r"""<template>
  <div class="engcard-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🇺🇸</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🇺🇸</div>
      <h1 class="title">영어 단어 카드</h1>
      <p class="subtitle">영어 단어를 그림으로 배워요!</p>
      <div class="level-info">
        <div>레벨 1-2: 기초 단어 (동물·과일)</div>
        <div>레벨 3-4: 일상 단어 (학교·집)</div>
        <div>레벨 5+: 중급 단어 (자연·도시)</div>
        <div style="margin-top:8px">현재 레벨: {{ level }}</div>
      </div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span>{{ correct }}✅</span>
      </div>
      <div class="question-card">
        <div class="card-emoji">{{ curWord.emoji }}</div>
        <div class="card-question">
          <span v-if="mode==='eng2kor'">
            <span class="eng-word">{{ curWord.eng }}</span>
            <span class="sub-label">은(는) 한국어로?</span>
          </span>
          <span v-else>
            <span class="kor-word">{{ curWord.kor }}</span>
            <span class="sub-label">은(는) 영어로?</span>
          </span>
        </div>
        <button class="hear-btn" @click="speakWord">🔊 듣기</button>
      </div>
      <div class="choices-grid">
        <button v-for="opt in options" :key="opt.eng" class="choice-btn"
          :class="{correct: answered && opt.eng===curWord.eng, wrong: answered && opt.eng===picked && opt.eng!==curWord.eng, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          <span class="choice-emoji">{{ opt.emoji }}</span>
          <span class="choice-text">{{ mode==='eng2kor' ? opt.kor : opt.eng }}</span>
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? curWord.eng+' = '+curWord.kor+' 🎉' : curWord.eng+' = '+curWord.kor }}
      </div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">🏆</div>
      <div class="res-score">{{ score }}점</div>
      <div class="res-detail">{{ correct }}/{{ totalQ }} 정답</div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 🔄</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const wordsByLevel = {
  1: [
    {emoji:'🐶',eng:'Dog',kor:'개'},
    {emoji:'🐱',eng:'Cat',kor:'고양이'},
    {emoji:'🐸',eng:'Frog',kor:'개구리'},
    {emoji:'🐘',eng:'Elephant',kor:'코끼리'},
    {emoji:'🦁',eng:'Lion',kor:'사자'},
    {emoji:'🐧',eng:'Penguin',kor:'펭귄'},
    {emoji:'🍎',eng:'Apple',kor:'사과'},
    {emoji:'🍌',eng:'Banana',kor:'바나나'},
    {emoji:'🍇',eng:'Grape',kor:'포도'},
    {emoji:'🍓',eng:'Strawberry',kor:'딸기'},
  ],
  2: [
    {emoji:'🏠',eng:'House',kor:'집'},
    {emoji:'🏫',eng:'School',kor:'학교'},
    {emoji:'📚',eng:'Book',kor:'책'},
    {emoji:'✏️',eng:'Pencil',kor:'연필'},
    {emoji:'🎒',eng:'Bag',kor:'가방'},
    {emoji:'⏰',eng:'Clock',kor:'시계'},
    {emoji:'🪑',eng:'Chair',kor:'의자'},
    {emoji:'🚗',eng:'Car',kor:'자동차'},
    {emoji:'✈️',eng:'Plane',kor:'비행기'},
    {emoji:'🚢',eng:'Ship',kor:'배'},
  ],
  3: [
    {emoji:'🌸',eng:'Flower',kor:'꽃'},
    {emoji:'🌳',eng:'Tree',kor:'나무'},
    {emoji:'🌊',eng:'Wave',kor:'파도'},
    {emoji:'⛰️',eng:'Mountain',kor:'산'},
    {emoji:'🌙',eng:'Moon',kor:'달'},
    {emoji:'⭐',eng:'Star',kor:'별'},
    {emoji:'☁️',eng:'Cloud',kor:'구름'},
    {emoji:'🌈',eng:'Rainbow',kor:'무지개'},
    {emoji:'❄️',eng:'Snow',kor:'눈'},
    {emoji:'🌺',eng:'Hibiscus',kor:'히비스커스'},
  ],
  4: [
    {emoji:'👨‍⚕️',eng:'Doctor',kor:'의사'},
    {emoji:'👩‍🍳',eng:'Cook',kor:'요리사'},
    {emoji:'👮',eng:'Police',kor:'경찰'},
    {emoji:'🧑‍🏫',eng:'Teacher',kor:'선생님'},
    {emoji:'💊',eng:'Medicine',kor:'약'},
    {emoji:'🍕',eng:'Pizza',kor:'피자'},
    {emoji:'🍜',eng:'Noodles',kor:'국수'},
    {emoji:'🎂',eng:'Cake',kor:'케이크'},
    {emoji:'☕',eng:'Coffee',kor:'커피'},
    {emoji:'🥛',eng:'Milk',kor:'우유'},
  ],
}

const level = ref(parseInt(localStorage.getItem('engcard_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const curWord = ref({emoji:'',eng:'',kor:''})
const options = ref([])
const qIdx = ref(0)
const totalQ = ref(10)
const mode = ref('eng2kor')
let queue = []

function getPool() {
  const lv = Math.min(level.value, 4)
  const pool = []
  for (let i = 1; i <= lv; i++) { if (wordsByLevel[i]) pool.push(...wordsByLevel[i]) }
  return pool
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function speak(text, lang = 'ko-KR') {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = lang; u.rate = 0.8; u.pitch = 1.1
  window.speechSynthesis.speak(u)
}

function speakWord() {
  speak(curWord.value.eng, 'en-US')
  setTimeout(() => speak(curWord.value.kor, 'ko-KR'), 1200)
}

function startGame() {
  score.value = 0; correct.value = 0; leveled.value = false; qIdx.value = 0
  const pool = getPool()
  queue = shuffle(pool).slice(0, totalQ.value)
  mode.value = level.value >= 3 ? (Math.random() > 0.5 ? 'eng2kor' : 'kor2eng') : 'eng2kor'
  phase.value = 'play'
  nextQuestion()
}

function nextQuestion() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  const q = queue[qIdx.value]; qIdx.value++
  curWord.value = q; answered.value = false; wasRight.value = false; picked.value = ''
  const pool = getPool()
  const wrongs = shuffle(pool.filter(w => w.eng !== q.eng)).slice(0, 3)
  options.value = shuffle([q, ...wrongs])
  if (mode.value === 'eng2kor') speak(q.eng, 'en-US')
  else speak(q.kor, 'ko-KR')
}

function selectAnswer(opt) {
  if (answered.value) return
  answered.value = true; picked.value = opt.eng
  wasRight.value = opt.eng === curWord.value.eng
  if (wasRight.value) {
    correct.value++
    score.value += 10
    speak('정답! ' + curWord.value.kor, 'ko-KR')
  } else {
    speak('정답은 ' + curWord.value.kor + ' 이에요', 'ko-KR')
  }
  setTimeout(nextQuestion, 2000)
}

function endGame() {
  phase.value = 'result'
  const threshold = level.value <= 2 ? 7 : level.value <= 4 ? 8 : 9
  if (correct.value >= threshold) {
    level.value++
    localStorage.setItem('engcard_level', level.value)
    leveled.value = true
    speak('레벨업! 레벨 ' + level.value + '!', 'ko-KR')
  }
}

function goBack() { router.push('/games') }
</script>

<style scoped>
.engcard-game { min-height:100vh; background:linear-gradient(135deg,#1d4ed8,#2563eb,#3b82f6); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.2); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.2); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.85); font-size:16px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#bfdbfe; font-size:14px; line-height:1.8; margin:12px auto; max-width:280px; text-align:left; }
.start-btn { background:#fff; color:#1d4ed8; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:500px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; color:rgba(255,255,255,0.8); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(255,255,255,0.2); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#fff; border-radius:4px; transition:width 0.3s; }
.question-card { background:rgba(255,255,255,0.15); border-radius:20px; padding:24px 20px; text-align:center; margin-bottom:20px; }
.card-emoji { font-size:72px; margin-bottom:12px; }
.card-question { display:block; margin-bottom:12px; }
.eng-word { font-size:36px; font-weight:900; color:#fff; display:block; }
.kor-word { font-size:36px; font-weight:900; color:#fff; display:block; }
.sub-label { font-size:14px; color:rgba(255,255,255,0.7); display:block; margin-top:4px; }
.hear-btn { background:rgba(255,255,255,0.2); color:#fff; border:none; padding:8px 18px; border-radius:20px; cursor:pointer; font-size:14px; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#1d4ed8; border:none; padding:14px 10px; border-radius:12px; cursor:pointer; transition:all 0.2s; display:flex; flex-direction:column; align-items:center; gap:4px; }
.choice-btn:hover:not(.disabled) { transform:scale(1.03); background:#fff; }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.choice-emoji { font-size:28px; }
.choice-text { font-size:15px; font-weight:700; }
.feedback { text-align:center; padding:12px; border-radius:12px; font-size:16px; font-weight:700; }
.feedback.right { background:rgba(16,185,129,0.25); color:#d1fae5; }
.feedback.wrong { background:rgba(239,68,68,0.25); color:#fee2e2; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#fff; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#fff; color:#1d4ed8; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#1d4ed8; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#1d4ed8; color:#fff; }
</style>
"""

# Write files
print("=== 게임 14: 미로 탈출 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameMaze.vue', game14)

print("=== 게임 15: 퍼즐 맞추기 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GamePuzzle.vue', game15)

print("=== 게임 16: 영어 단어 카드 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameEngCard.vue', game16)

# Update router
print("\n=== 라우터 업데이트 ===")
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
new_routes = """  { path: '/games/maze', component: () => import('../pages/games/GameMaze.vue'), name: 'game-maze' },
  { path: '/games/puzzle', component: () => import('../pages/games/GamePuzzle.vue'), name: 'game-puzzle' },
  { path: '/games/engcard', component: () => import('../pages/games/GameEngCard.vue'), name: 'game-engcard' },"""

if 'game-maze' not in router_content:
    updated = router_content.replace(
        "  { path: '/games/wordchain'",
        new_routes + "\n  { path: '/games/wordchain'"
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', updated)
    print("Router updated")
else:
    print("Routes already exist")

# Update DB
print("\n=== DB 업데이트 ===")
updates = [
    ("미로", "game-maze"),
    ("퍼즐", "game-puzzle"),
    ("영어단어", "game-engcard"),
]
for name, route in updates:
    r = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"UPDATE games SET route_name='{route}' WHERE name LIKE '%{name}%';\"")
    print(f"{name} -> {route}: {r or 'OK'}")

# Build
print("\n=== npm 빌드 ===")
build_result = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -15", timeout=300)
print(build_result)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

print("\n✅ 게임 14-16 배포 완료! 어린이 게임 완성!")
c.close()
