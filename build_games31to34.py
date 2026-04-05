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

# ===== GAME 31: 빙고 =====
game_bingo = r"""<template>
  <div class="bingo-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🎯</div>
      <div class="score">빙고 {{ bingoCount }}줄</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🎯</div>
      <h1 class="title">빙고!</h1>
      <p class="subtitle">숫자가 불리면 체크하세요! 먼저 빙고를 완성해요!</p>
      <div class="level-info">
        <div>레벨 1-2: 3×3 빙고</div>
        <div>레벨 3-4: 4×4 빙고</div>
        <div>레벨 5+: 5×5 빙고</div>
      </div>
      <button class="start-btn" @click="startGame">게임 시작! 🎲</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="called-display">
        <div class="called-label">호출된 숫자</div>
        <div class="called-number" :class="{animate: justCalled}">{{ lastCalled || '?' }}</div>
      </div>
      <div class="bingo-card" :style="cardStyle">
        <div v-for="(cell, idx) in card" :key="idx"
          class="bingo-cell" :class="{marked: cell.marked, bingo: isBingoCell(idx)}"
          @click="markCell(idx)">
          {{ cell.num }}
        </div>
      </div>
      <div class="bingo-status">
        <div class="bingo-count">빙고 {{ bingoCount }}줄</div>
        <div class="called-count">{{ calledNums.length }}번 호출됨</div>
      </div>
      <div class="called-list">
        <span v-for="n in calledNums" :key="n" class="called-chip">{{ n }}</span>
      </div>
      <button class="call-btn" @click="callNext" :disabled="phase!=='play'">다음 숫자 뽑기 🎲</button>
    </div>

    <div v-if="phase==='bingo'" class="result-box">
      <div style="font-size:80px">🎊</div>
      <h2 class="res-title">빙고!</h2>
      <div class="res-detail">{{ bingoCount }}줄 빙고! {{ calledNums.length }}번 만에!</div>
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

const level = ref(parseInt(localStorage.getItem('bingo_level') || '1'))
const phase = ref('start')
const card = ref([])
const calledNums = ref([])
const lastCalled = ref(null)
const justCalled = ref(false)
const bingoCount = ref(0)
const leveled = ref(false)

const gridSize = computed(() => level.value <= 2 ? 3 : level.value <= 4 ? 4 : 5)
const maxNum = computed(() => gridSize.value * gridSize.value * 2)

const cardStyle = computed(() => ({
  gridTemplateColumns: `repeat(${gridSize.value}, 1fr)`
}))

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(() => Math.random()-0.5) }

function startGame() {
  const size = gridSize.value
  const total = size * size
  const nums = shuffle([...Array(maxNum.value).keys()].map(i => i+1)).slice(0, total)
  card.value = nums.map(n => ({num: n, marked: false}))
  calledNums.value = []
  lastCalled.value = null
  bingoCount.value = 0
  leveled.value = false
  phase.value = 'play'
  speak(size + '곱하기 ' + size + ' 빙고 시작!')
}

function callNext() {
  const size = gridSize.value
  const remaining = [...Array(maxNum.value).keys()].map(i=>i+1).filter(n=>!calledNums.value.includes(n))
  if (remaining.length === 0) return
  const n = remaining[Math.floor(Math.random()*remaining.length)]
  calledNums.value.push(n)
  lastCalled.value = n
  justCalled.value = true
  setTimeout(() => justCalled.value = false, 800)
  // auto mark
  const idx = card.value.findIndex(c => c.num === n)
  if (idx >= 0) { card.value[idx] = {...card.value[idx], marked: true}; checkBingo() }
  speak(String(n))
}

function markCell(idx) {
  if (!card.value[idx].marked) return
}

function isBingoCell(idx) {
  const size = gridSize.value
  const r = Math.floor(idx/size), c = idx%size
  // check if this cell is in a completed line
  const rows = Array.from({length:size}, (_,i) => Array.from({length:size}, (_,j)=>i*size+j))
  const cols = Array.from({length:size}, (_,j) => Array.from({length:size}, (_,i)=>i*size+j))
  const diag1 = Array.from({length:size}, (_,i) => i*size+i)
  const diag2 = Array.from({length:size}, (_,i) => i*size+(size-1-i))
  const lines = [...rows, ...cols, diag1, diag2]
  return lines.some(line => line.includes(idx) && line.every(i => card.value[i]?.marked))
}

function checkBingo() {
  const size = gridSize.value
  const rows = Array.from({length:size}, (_,i) => Array.from({length:size}, (_,j)=>i*size+j))
  const cols = Array.from({length:size}, (_,j) => Array.from({length:size}, (_,i)=>i*size+j))
  const diag1 = Array.from({length:size}, (_,i)=>i*size+i)
  const diag2 = Array.from({length:size}, (_,i)=>i*size+(size-1-i))
  const lines = [...rows, ...cols, diag1, diag2]
  const newBingo = lines.filter(line => line.every(i => card.value[i]?.marked)).length
  if (newBingo > bingoCount.value) {
    bingoCount.value = newBingo
    speak('빙고!')
    const target = level.value <= 2 ? 1 : level.value <= 4 ? 2 : 3
    if (newBingo >= target) {
      phase.value = 'bingo'
      if (calledNums.value.length <= size*size+3) {
        level.value++
        localStorage.setItem('bingo_level', level.value)
        leveled.value = true
        speak('빙고! 레벨업!')
      }
    }
  }
}

function goBack() { router.push('/games') }
</script>

<style scoped>
.bingo-game { min-height:100vh; background:linear-gradient(135deg,#701a75,#86198f,#a21caf); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:40px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.85); font-size:15px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#f0abfc; font-size:14px; line-height:1.8; margin:12px auto; max-width:200px; text-align:left; }
.start-btn { background:#e879f9; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { display:flex; flex-direction:column; align-items:center; }
.called-display { text-align:center; margin-bottom:16px; }
.called-label { color:rgba(255,255,255,0.6); font-size:12px; }
.called-number { font-size:72px; font-weight:900; color:#e879f9; transition:all 0.3s; }
.called-number.animate { transform:scale(1.3); color:#fff; }
.bingo-card { display:grid; gap:6px; margin-bottom:14px; }
.bingo-cell { width:64px; height:64px; display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,0.15); border-radius:10px; font-size:20px; font-weight:700; color:#fff; border:2px solid transparent; transition:all 0.2s; cursor:default; }
.bingo-cell.marked { background:rgba(232,121,249,0.4); border-color:#e879f9; color:#fce7f3; }
.bingo-cell.bingo { background:#e879f9; border-color:#fff; color:#fff; }
.bingo-status { display:flex; gap:16px; margin-bottom:10px; }
.bingo-count { color:#e879f9; font-size:18px; font-weight:700; }
.called-count { color:rgba(255,255,255,0.6); font-size:14px; }
.called-list { display:flex; flex-wrap:wrap; gap:4px; max-width:340px; margin-bottom:14px; justify-content:center; }
.called-chip { background:rgba(255,255,255,0.2); color:#fff; font-size:12px; padding:2px 8px; border-radius:10px; }
.call-btn { background:#e879f9; color:#fff; border:none; padding:14px 36px; border-radius:20px; font-size:17px; font-weight:700; cursor:pointer; }
.call-btn:disabled { opacity:0.5; cursor:not-allowed; }
.result-box { text-align:center; padding:40px 20px; }
.res-title { font-size:40px; color:#e879f9; font-weight:900; margin:10px 0; }
.res-detail { color:rgba(255,255,255,0.8); font-size:18px; }
.levelup { background:#e879f9; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#701a75; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#a21caf; color:#fff; }
</style>
"""

# ===== GAME 32: 기억력 카드 매칭 =====
game_memory = r"""<template>
  <div class="memory-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🧠</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🧠</div>
      <h1 class="title">기억력 카드</h1>
      <p class="subtitle">같은 그림을 찾아 짝을 맞춰요!</p>
      <div class="level-info">
        <div>레벨 1-2: 8쌍 카드 (4×4)</div>
        <div>레벨 3-4: 12쌍 카드 (4×6)</div>
        <div>레벨 5+: 18쌍 카드 (6×6)</div>
      </div>
      <div class="best-time" v-if="bestTime">🏆 최단시간: {{ bestTime }}초</div>
      <button class="start-btn" @click="startGame">시작! 🃏</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="game-info">
        <div class="moves-display">👆 {{ moves }}번</div>
        <div class="timer-display">⏱ {{ elapsed }}초</div>
        <div class="pairs-display">✅ {{ matched }}/{{ totalPairs }}</div>
      </div>
      <div class="card-grid" :style="gridStyle">
        <div v-for="(card, i) in cards" :key="i"
          class="memory-card" :class="{flipped: card.flipped || card.matched, matched: card.matched}"
          @click="flipCard(i)">
          <div class="card-face front">❓</div>
          <div class="card-face back">{{ card.emoji }}</div>
        </div>
      </div>
    </div>

    <div v-if="phase==='complete'" class="result-box">
      <div style="font-size:80px">🎊</div>
      <div class="res-title">완성!</div>
      <div class="res-stats">{{ moves }}번 · {{ elapsed }}초</div>
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
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const allEmojis = ['🐶','🐱','🦊','🐸','🦁','🐘','🦋','🌺','🍎','🍌','⭐','🌙','🚗','✈️','🎸','🎁','🌈','🏆','🎯','🎲','🌍','🔥','💎','🦄']

const level = ref(parseInt(localStorage.getItem('memory_level') || '1'))
const bestTime = ref(parseInt(localStorage.getItem('memory_best') || '0') || null)
const phase = ref('start')
const cards = ref([])
const moves = ref(0)
const elapsed = ref(0)
const matched = ref(0)
const score = ref(0)
const leveled = ref(false)
const isNewBest = ref(false)
let flipped1 = ref(-1)
let flipped2 = ref(-1)
let checking = false
let timerInterval = null
let startTime = null

const totalPairs = computed(() => level.value <= 2 ? 8 : level.value <= 4 ? 12 : 18)

const gridStyle = computed(() => {
  const cols = level.value <= 2 ? 4 : level.value <= 4 ? 6 : 6
  return { gridTemplateColumns: `repeat(${cols}, 1fr)` }
})

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(() => Math.random()-0.5) }

function startGame() {
  const pairs = totalPairs.value
  const emojis = shuffle(allEmojis).slice(0, pairs)
  cards.value = shuffle([...emojis, ...emojis].map(e => ({emoji:e, flipped:false, matched:false})))
  moves.value = 0; matched.value = 0; score.value = 0
  leveled.value = false; isNewBest.value = false
  flipped1.value = -1; flipped2.value = -1; checking = false
  elapsed.value = 0; startTime = Date.now()
  clearInterval(timerInterval)
  timerInterval = setInterval(() => { elapsed.value = Math.round((Date.now()-startTime)/1000) }, 1000)
  phase.value = 'play'
  speak('카드를 뒤집어 짝을 찾아요!')
}

function flipCard(i) {
  if (checking || cards.value[i].matched || cards.value[i].flipped) return
  if (flipped1.value >= 0 && flipped2.value >= 0) return
  cards.value[i] = {...cards.value[i], flipped: true}
  if (flipped1.value < 0) { flipped1.value = i; return }
  flipped2.value = i; moves.value++; checking = true
  setTimeout(() => {
    const c1 = cards.value[flipped1.value], c2 = cards.value[flipped2.value]
    if (c1.emoji === c2.emoji) {
      cards.value[flipped1.value] = {...c1, matched: true, flipped: false}
      cards.value[flipped2.value] = {...c2, matched: true, flipped: false}
      matched.value++
      score.value += Math.max(5, 20 - moves.value)
      if (matched.value === totalPairs.value) {
        clearInterval(timerInterval)
        const threshold = level.value <= 2 ? 20 : level.value <= 4 ? 30 : 50
        if (!bestTime.value || elapsed.value < bestTime.value) {
          bestTime.value = elapsed.value
          localStorage.setItem('memory_best', elapsed.value)
          isNewBest.value = true
        }
        if (moves.value <= threshold) {
          level.value++; localStorage.setItem('memory_level', level.value)
          leveled.value = true; speak('완성! 레벨업!')
        } else speak('완성!')
        phase.value = 'complete'
      }
    } else {
      cards.value[flipped1.value] = {...c1, flipped: false}
      cards.value[flipped2.value] = {...c2, flipped: false}
    }
    flipped1.value = -1; flipped2.value = -1; checking = false
  }, 800)
}

function goBack() { clearInterval(timerInterval); router.push('/games') }
onUnmounted(() => clearInterval(timerInterval))
</script>

<style scoped>
.memory-game { min-height:100vh; background:linear-gradient(135deg,#0c4a6e,#075985,#0369a1); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.85); font-size:15px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#bae6fd; font-size:14px; line-height:1.8; margin:12px auto; max-width:220px; text-align:left; }
.best-time { color:#fbbf24; font-size:15px; margin:8px 0; }
.start-btn { background:#0ea5e9; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { display:flex; flex-direction:column; align-items:center; }
.game-info { display:flex; gap:16px; margin-bottom:14px; }
.moves-display,.timer-display,.pairs-display { color:#fff; font-size:15px; font-weight:600; background:rgba(255,255,255,0.1); padding:6px 12px; border-radius:12px; }
.card-grid { display:grid; gap:8px; }
.memory-card { width:56px; height:56px; cursor:pointer; perspective:600px; position:relative; }
.card-face { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; border-radius:10px; font-size:28px; backface-visibility:hidden; transition:transform 0.4s; }
.front { background:rgba(255,255,255,0.15); border:2px solid rgba(255,255,255,0.3); transform:rotateY(0deg); }
.back { background:rgba(14,165,233,0.4); border:2px solid #0ea5e9; transform:rotateY(180deg); }
.memory-card.flipped .front { transform:rotateY(180deg); }
.memory-card.flipped .back { transform:rotateY(0deg); }
.memory-card.matched .front { transform:rotateY(180deg); }
.memory-card.matched .back { background:rgba(16,185,129,0.5); border-color:#10b981; transform:rotateY(0deg); }
.result-box { text-align:center; padding:40px 20px; }
.res-title { font-size:40px; color:#fff; font-weight:900; margin:10px 0; }
.res-stats { color:rgba(255,255,255,0.8); font-size:18px; margin:8px 0; }
.new-best { color:#fbbf24; font-size:18px; font-weight:800; margin:8px 0; }
.levelup { background:#0ea5e9; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#0c4a6e; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#0369a1; color:#fff; }
</style>
"""

# ===== GAME 33: 미국 생활 상식 퀴즈 =====
game_uslife = r"""<template>
  <div class="uslife-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🇺🇸</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🇺🇸</div>
      <h1 class="title">미국 생활 상식</h1>
      <p class="subtitle">미국 한인으로 알아야 할 상식!</p>
      <div class="level-info">
        <div>레벨 1-2: 기초 (운전·세금)</div>
        <div>레벨 3-4: 중급 (의료·금융)</div>
        <div>레벨 5+: 고급 (법률·이민)</div>
      </div>
      <button class="start-btn" @click="startGame">시작! 📋</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span :style="{color:timeLeft<6?'#ef4444':'#93c5fd'}">{{ timeLeft }}초</span>
      </div>
      <div class="category-tag">{{ curQ.category }}</div>
      <div class="question-card">
        <div class="q-text">{{ curQ.question }}</div>
      </div>
      <div class="choices-col">
        <button v-for="opt in curQ.options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===curQ.answer, wrong: answered && opt===picked && opt!==curQ.answer, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          {{ opt }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        <div>{{ wasRight ? '정답! 🎉' : '오답! 정답: ' + curQ.answer }}</div>
        <div class="explain">{{ curQ.explain }}</div>
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
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const usQuiz = [
  {level:1,category:'운전',question:'미국에서 오른쪽에 빨간불이 있어도 할 수 있는 것은?',options:['우회전','유턴','좌회전','직진'],answer:'우회전',explain:'미국은 "No Turn On Red" 표지가 없으면 빨간불에도 우회전 가능해요.'},
  {level:1,category:'운전',question:'미국 운전면허 필기시험에서 음주운전 혈중 알코올 기준은?',options:['0.08%','0.1%','0.05%','0.03%'],answer:'0.08%',explain:'미국 대부분의 주에서 BAC 0.08% 이상이면 DUI로 처벌받아요.'},
  {level:1,category:'세금',question:'미국 연방 소득세 신고 마감일은?',options:['4월 15일','1월 31일','12월 31일','6월 15일'],answer:'4월 15일',explain:'Tax Day는 매년 4월 15일이에요. 주말이면 다음 월요일로 연장돼요.'},
  {level:1,category:'생활',question:'미국에서 팁(Tip)의 일반적인 비율은?',options:['15-20%','5-10%','25-30%','1-5%'],answer:'15-20%',explain:'레스토랑에서는 보통 15~20%의 팁을 남기는 것이 에티켓이에요.'},
  {level:1,category:'의료',question:'미국에서 119 응급전화 번호는?',options:['911','119','999','000'],answer:'911',explain:'미국 응급전화는 911이에요. 경찰·소방·구급 모두 911로 연결돼요.'},
  {level:2,category:'의료',question:'미국 의료보험 중 65세 이상 노인을 위한 것은?',options:['Medicare','Medicaid','CHIP','ACA'],answer:'Medicare',explain:'Medicare는 65세 이상 시민권자/영주권자를 위한 연방 의료보험이에요.'},
  {level:2,category:'금융',question:'미국 신용점수(FICO Score)에서 "Good"은 몇 점부터인가요?',options:['670점 이상','500점 이상','800점 이상','600점 이상'],answer:'670점 이상',explain:'FICO 점수: 670-739=Good, 740-799=Very Good, 800+=Exceptional이에요.'},
  {level:2,category:'금융',question:'미국 은행 계좌의 예금자 보호 한도는?',options:['$250,000','$100,000','$500,000','$1,000,000'],answer:'$250,000',explain:'FDIC가 인당 $250,000까지 예금을 보호해요.'},
  {level:3,category:'이민',question:'미국 영주권(Green Card) 취득 후 시민권 신청 가능 기간은?',options:['5년 후','3년 후 (배우자)','7년 후','10년 후'],answer:'3년 후 (배우자)',explain:'미국 시민권자 배우자는 3년, 일반 영주권자는 5년 후 시민권 신청 가능해요.'},
  {level:3,category:'법률',question:'미국에서 Miranda Rights(미란다 원칙)는 언제 고지해야 하나요?',options:['체포 후 심문 시','경찰 접촉 시','법원 출두 시','구금 24시간 후'],answer:'체포 후 심문 시',explain:'체포 후 심문 전 "당신은 묵비권을 행사할 수 있습니다..." 고지가 필요해요.'},
]

const level = ref(parseInt(localStorage.getItem('uslife_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const curQ = ref({options:[],answer:'',explain:'',category:'',question:''})
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(25)
const maxTime = ref(25)
let timer = null
let queue = []

function getPool() {
  const maxLv=level.value<=2?1:level.value<=4?2:3
  return usQuiz.filter(q=>q.level<=maxLv)
}

function speak(text) {
  if(!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang='ko-KR'; u.rate=0.85
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function startGame() {
  score.value=0; correct.value=0; leveled.value=false; qIdx.value=0
  queue=shuffle(getPool()).slice(0,totalQ.value)
  phase.value='play'; nextQuestion()
}

function nextQuestion() {
  if(qIdx.value>=totalQ.value){endGame();return}
  const q=queue[qIdx.value]; qIdx.value++
  curQ.value={...q, options:shuffle([...q.options])}
  answered.value=false; wasRight.value=false; picked.value=''
  speak(q.question)
  startTimer()
}

function startTimer() {
  clearInterval(timer); timeLeft.value=maxTime.value
  timer=setInterval(()=>{ timeLeft.value--; if(timeLeft.value<=0){clearInterval(timer);timeOut()} },1000)
}

function timeOut() {
  answered.value=true; wasRight.value=false
  speak('시간 초과! 정답은 ' + curQ.value.answer)
  setTimeout(nextQuestion,3000)
}

function selectAnswer(opt) {
  if(answered.value) return
  clearInterval(timer); answered.value=true; picked.value=opt
  wasRight.value=opt===curQ.value.answer
  if(wasRight.value){ correct.value++; score.value+=10+timeLeft.value; speak('정답!') }
  else speak('오답!')
  setTimeout(nextQuestion,3000)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=7){ level.value++; localStorage.setItem('uslife_level',level.value); leveled.value=true; speak('레벨업!') }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.uslife-game { min-height:100vh; background:linear-gradient(135deg,#1e3a5f,#1d4ed8,#2563eb); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:34px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.85); font-size:16px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#bfdbfe; font-size:14px; line-height:1.8; margin:12px auto; max-width:240px; text-align:left; }
.start-btn { background:#fff; color:#1e3a5f; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:500px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:12px; color:rgba(255,255,255,0.7); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(255,255,255,0.2); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#3b82f6; border-radius:4px; transition:width 0.3s; }
.category-tag { display:inline-block; background:rgba(59,130,246,0.4); color:#93c5fd; font-size:12px; font-weight:700; padding:4px 12px; border-radius:12px; margin-bottom:10px; text-transform:uppercase; letter-spacing:1px; }
.question-card { background:rgba(255,255,255,0.1); border-radius:18px; padding:22px 20px; margin-bottom:16px; }
.q-text { color:#fff; font-size:19px; font-weight:600; line-height:1.5; }
.choices-col { display:flex; flex-direction:column; gap:8px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#1e3a5f; border:none; padding:14px 16px; border-radius:12px; font-size:15px; font-weight:600; cursor:pointer; text-align:left; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { background:#fff; transform:translateX(4px); }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { padding:14px 16px; border-radius:12px; }
.feedback.right { background:rgba(16,185,129,0.2); color:#a7f3d0; }
.feedback.wrong { background:rgba(239,68,68,0.2); color:#fca5a5; }
.explain { font-size:13px; font-weight:400; margin-top:6px; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:52px; font-weight:900; color:#93c5fd; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#3b82f6; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#1e3a5f; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#1d4ed8; color:#fff; }
</style>
"""

# Write files
print("=== 게임 31: 빙고 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameBingo.vue', game_bingo)

print("=== 게임 32: 기억력 카드 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameMemory.vue', game_memory)

print("=== 게임 35: 미국 생활 상식 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameUSLife.vue', game_uslife)

# Update router
print("\n=== 라우터 업데이트 ===")
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
new_routes = """  { path: '/games/bingo', component: () => import('../pages/games/GameBingo.vue'), name: 'game-bingo' },
  { path: '/games/memory', component: () => import('../pages/games/GameMemory.vue'), name: 'game-memory' },
  { path: '/games/us-life', component: () => import('../pages/games/GameUSLife.vue'), name: 'game-us-life' },"""

if 'game-bingo' not in router_content:
    updated = router_content.replace(
        "  { path: '/games/proverb'",
        new_routes + "\n  { path: '/games/proverb'"
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', updated)
    print("Router updated")

# Fix DB routes
print("\n=== DB 라우트 수정 ===")
db_fixes = [
    (31, 'game-bingo'),
    (32, 'game-memory'),
    (33, 'game-daily-quiz'),  # 일일 퀴즈는 quiz page로
    (34, 'game-wordle'),      # 워들 이미 있음
    (35, 'game-us-life'),
    (36, 'game-slots'),
    (37, 'game-matgo'),
    (38, 'game-number-memory'),
    (39, 'game-picture-memory'),
    (40, 'game-proverb'),
    (41, 'game-stroop'),
    (42, 'game-brain-calc'),
    (43, 'game-word-search'),
    (44, 'game-world-geo'),
    (45, 'game-breathing'),
    (46, 'game-senior-memory'),
    (47, 'game-senior-bingo'),
]
for gid, route in db_fixes:
    r = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"UPDATE games SET route_name='{route}' WHERE id={gid};\"")
    print(f"ID {gid} -> {route}: {r or 'OK'}")

# Build
print("\n=== npm 빌드 ===")
build_result = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -6", timeout=300)
print(build_result)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

print("\n✅ 게임 31-35 배포 완료!")
c.close()
