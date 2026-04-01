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
# 1. GameMathBasic.vue — 완전 재작성 (피드백 + 점수저장 + 레벨업)
# ============================================================
print("=== GameMathBasic.vue 재작성 ===")
math_basic = r"""<template>
  <div class="math-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} ⭐</div>
      <div class="score-badge">{{ score }}점</div>
    </div>

    <!-- 시작 화면 -->
    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">🔢</div>
      <h1 class="title">기초 수학</h1>
      <p class="subtitle">덧셈과 뺄셈을 배워요!</p>
      <div class="level-preview">
        <span v-if="level<=2">⊕ 1~9 더하기 빼기</span>
        <span v-else-if="level<=4">⊕ 10~20 범위 계산</span>
        <span v-else>⊕ 받아올림/받아내림</span>
      </div>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>

    <!-- 게임 화면 -->
    <div v-if="phase==='play'" class="play-box">
      <div class="progress-row">
        <div class="progress-bar"><div class="progress-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span class="q-count">{{ qIdx+1 }}/{{ totalQ }}</span>
      </div>

      <!-- 시각적 수 표현 (레벨1) -->
      <div v-if="level<=1 && cur" class="visual-row">
        <span v-for="i in cur.a" :key="'a'+i" class="dot">●</span>
        <span class="op-label">{{ cur.op }}</span>
        <span v-for="i in (cur.op==='+'?cur.b:0)" :key="'b'+i" class="dot green-dot">●</span>
      </div>

      <div v-if="cur" class="equation-box">
        <span class="eq-num">{{ cur.a }}</span>
        <span class="eq-op">{{ cur.op }}</span>
        <span class="eq-num">{{ cur.b }}</span>
        <span class="eq-op">=</span>
        <span class="eq-ans">?</span>
      </div>

      <div class="choices-grid">
        <button v-for="opt in cur?.opts" :key="opt"
          class="choice-btn" :disabled="answered" @click="answer(opt)">
          {{ opt }}
        </button>
      </div>

      <div class="streak-row" v-if="streak>=2">
        🔥 {{ streak }}연속 정답!
      </div>
    </div>

    <!-- 결과 화면 -->
    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">{{ correct>=totalQ*0.7?'🏆':'💪' }}</div>
      <h2 class="end-title">{{ correct>=totalQ*0.7?'훌륭해요!':'잘 했어요!' }}</h2>
      <p class="end-score">{{ score }}점 · {{ correct }}/{{ totalQ }} 정답</p>
      <div v-if="leveled" class="levelup-badge">🌟 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
      <button class="home-btn" @click="$router.push('/games')">홈으로 🏠</button>
    </div>

    <!-- 피드백 오버레이 -->
    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect?'fb-correct':'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? (streak>=3?'🔥':'🎉') : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? (streak>=3?streak+'연속 정답!':'정답이에요!') : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect && cur" class="fb-answer">
            정답은 <strong>{{ cur.a }} {{ cur.op }} {{ cur.b }} = {{ cur.ans }}</strong>
          </div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const level = ref(parseInt(localStorage.getItem('mathbasic_level')||'1'))
const score = ref(0); const qIdx = ref(0); const correct = ref(0)
const streak = ref(0); const leveled = ref(false); const answered = ref(false)
const phase = ref('start')
const showFeedback = ref(false); const lastCorrect = ref(false); const fbProgress = ref(100)
let fbTimer = null
const totalQ = 10
const questions = ref([])
const cur = computed(() => questions.value[qIdx.value])

function speak(t) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}
function rand(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ return [...a].sort(()=>Math.random()-.5) }

function genQ() {
  const lv = level.value
  let a, b, op, ans
  if (lv <= 2) { a=rand(1,9); b=rand(1,Math.min(a,9)); op=Math.random()>.5?'+':'-'; ans=op==='+'?a+b:a-b }
  else if (lv <= 4) { a=rand(5,15); b=rand(1,10); op=Math.random()>.5?'+':'-'; if(op==='-')b=rand(1,a); ans=op==='+'?a+b:a-b }
  else { a=rand(10,30); b=rand(5,20); op=Math.random()>.5?'+':'-'; if(op==='-')b=rand(1,a); ans=op==='+'?a+b:a-b }
  const wrongs = new Set()
  while(wrongs.size<3){ const w=ans+rand(-5,5); if(w!==ans&&w>=0)wrongs.add(w) }
  return { a, b, op, ans, opts: shuffle([ans,...wrongs]) }
}

function startGame() {
  score.value=0; qIdx.value=0; correct.value=0; streak.value=0; leveled.value=false
  answered.value=false; showFeedback.value=false; phase.value='play'
  questions.value = Array.from({length:totalQ}, genQ)
  speak('수학 문제를 풀어봐요!')
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect; showFeedback.value = true; fbProgress.value = 100
  clearInterval(fbTimer)
  const dur = isCorrect ? 1200 : 2200; const step = 50/dur*100
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
  const isOk = opt === cur.value.ans
  if (isOk) {
    score.value += 10 + (streak.value >= 2 ? 5 : 0)
    correct.value++; streak.value++
    speak(streak.value >= 3 ? `${streak.value}연속 정답!` : '정답이에요!')
  } else {
    streak.value = 0
    speak(`아쉬워요! 정답은 ${cur.value.ans}이에요`)
  }
  triggerFeedback(isOk)
}

async function endGame() {
  phase.value = 'end'
  const passed = correct.value >= Math.ceil(totalQ * 0.7)
  if (passed) {
    level.value++; localStorage.setItem('mathbasic_level', level.value); leveled.value = true
    speak('훌륭해요! 레벨업!')
  } else speak('잘 했어요! 다시 도전해봐요!')
  // 점수 저장
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await axios.post('/api/games/8/score',
        { score: score.value, level: level.value, result: passed?'win':'lose', duration: totalQ*5 },
        { headers: { Authorization: `Bearer ${token}` } })
    } catch(e) {}
  }
}
</script>

<style scoped>
.math-game { min-height:100vh; background:linear-gradient(135deg,#134e4a,#0f766e,#0d9488); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.level-preview { background:rgba(255,255,255,.1); color:rgba(255,255,255,.9); padding:10px 20px; border-radius:20px; font-size:14px; margin:12px auto; display:inline-block; }
.start-btn { background:#14b8a6; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin:10px 6px; }
.home-btn { background:rgba(255,255,255,.2); color:#fff; border:none; padding:12px 28px; border-radius:30px; font-size:16px; font-weight:600; cursor:pointer; margin:10px 6px; }
.play-box { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.progress-bar { flex:1; height:10px; background:rgba(255,255,255,.2); border-radius:5px; }
.progress-fill { height:100%; background:#5eead4; border-radius:5px; transition:width .3s; }
.q-count { color:rgba(255,255,255,.8); font-size:13px; white-space:nowrap; }
.visual-row { display:flex; flex-wrap:wrap; gap:4px; justify-content:center; align-items:center; margin-bottom:12px; min-height:36px; background:rgba(255,255,255,.1); border-radius:14px; padding:10px; }
.dot { font-size:18px; color:#fef3c7; }
.green-dot { color:#86efac; }
.op-label { font-size:20px; color:#fff; font-weight:700; margin:0 8px; }
.equation-box { display:flex; align-items:center; justify-content:center; gap:16px; background:rgba(255,255,255,.15); border-radius:20px; padding:28px 20px; margin-bottom:24px; }
.eq-num { font-size:52px; font-weight:900; color:#fff; }
.eq-op { font-size:36px; font-weight:700; color:#5eead4; }
.eq-ans { font-size:52px; font-weight:900; color:#fde68a; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.choice-btn { background:rgba(255,255,255,.92); color:#134e4a; border:none; padding:20px; border-radius:16px; font-size:26px; font-weight:800; cursor:pointer; transition:all .15s; box-shadow:0 4px 10px rgba(0,0,0,.15); }
.choice-btn:hover:not(:disabled) { background:#fff; transform:scale(1.05); }
.choice-btn:disabled { cursor:default; }
.streak-row { text-align:center; color:#fde68a; font-size:15px; font-weight:700; margin-top:12px; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.end-score { color:rgba(255,255,255,.8); font-size:18px; }
.levelup-badge { background:#14b8a6; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
.feedback-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; z-index:999; backdrop-filter:blur(4px); }
.fb-correct { background:rgba(16,185,129,.88); }
.fb-wrong { background:rgba(239,68,68,.88); }
.fb-content { text-align:center; color:#fff; padding:32px 48px; }
.fb-emoji { font-size:80px; margin-bottom:8px; }
.fb-title { font-size:34px; font-weight:900; margin-bottom:8px; }
.fb-answer { font-size:18px; margin-bottom:16px; opacity:.95; }
.fb-bar-wrap { width:200px; height:7px; background:rgba(255,255,255,.3); border-radius:4px; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:4px; transition:width .05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity .25s; }
.fb-enter-from,.fb-leave-to { opacity:0; }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/games/GameMathBasic.vue', math_basic)

# ============================================================
# 2. GameMultiplication.vue — 피드백 오버레이 + 점수저장
# ============================================================
print("\n=== GameMultiplication.vue 재작성 ===")
multiplication = r"""<template>
  <div class="mult-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} ✖</div>
      <div class="score-badge">{{ score }}점</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">✖️</div>
      <h1 class="title">구구단</h1>
      <p class="subtitle">곱셈을 마스터해요!</p>
      <div class="level-preview">{{ levelRange }}</div>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>

    <div v-if="phase==='play'" class="play-box">
      <div class="progress-row">
        <div class="progress-bar"><div class="progress-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span class="q-count">{{ qIdx+1 }}/{{ totalQ }}</span>
      </div>
      <div v-if="cur" class="equation-box">
        <span class="eq-num">{{ cur.a }}</span>
        <span class="eq-op">×</span>
        <span class="eq-num">{{ cur.b }}</span>
        <span class="eq-op">=</span>
        <span class="eq-ans">?</span>
      </div>
      <div class="mult-hint" v-if="level<=2">
        💡 {{ cur?.a }} × {{ cur?.b }} 를 계산해요
      </div>
      <div class="choices-grid">
        <button v-for="opt in cur?.opts" :key="opt"
          class="choice-btn" :disabled="answered" @click="answer(opt)">{{ opt }}</button>
      </div>
    </div>

    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">{{ correct>=totalQ*0.7?'🏅':'📚' }}</div>
      <h2 class="end-title">{{ correct>=totalQ*0.7?'구구단 마스터!':'잘 했어요!' }}</h2>
      <p class="end-score">{{ score }}점 · {{ correct }}/{{ totalQ }} 정답</p>
      <div v-if="leveled" class="levelup-badge">🎉 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
      <button class="home-btn" @click="$router.push('/games')">홈으로 🏠</button>
    </div>

    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect?'fb-correct':'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect && cur" class="fb-answer">
            {{ cur.a }} × {{ cur.b }} = <strong>{{ cur.ans }}</strong>
          </div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const level = ref(parseInt(localStorage.getItem('mult_level')||'1'))
const score = ref(0); const qIdx = ref(0); const correct = ref(0)
const leveled = ref(false); const answered = ref(false); const phase = ref('start')
const showFeedback = ref(false); const lastCorrect = ref(false); const fbProgress = ref(100)
let fbTimer = null
const totalQ = 12
const questions = ref([])
const cur = computed(() => questions.value[qIdx.value])

const levelRange = computed(() => {
  if (level.value <= 2) return '2단 ~ 4단'
  if (level.value <= 4) return '5단 ~ 7단'
  return '8단 ~ 9단'
})

function speak(t) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}
function rand(a,b){ return Math.floor(Math.random()*(b-a+1))+a }
function shuffle(a){ return [...a].sort(()=>Math.random()-.5) }

function genQ() {
  const lv = level.value
  let tableRange
  if (lv <= 2) tableRange = [2,3,4]
  else if (lv <= 4) tableRange = [5,6,7]
  else tableRange = [8,9,6,7]
  const a = tableRange[rand(0,tableRange.length-1)]
  const b = rand(2,9)
  const ans = a*b
  const wrongs = new Set()
  while(wrongs.size<3){ const w=ans+rand(-8,8)*1; if(w!==ans&&w>0&&w<=81)wrongs.add(w) }
  return { a, b, ans, opts: shuffle([ans,...wrongs]) }
}

function startGame() {
  score.value=0; qIdx.value=0; correct.value=0; leveled.value=false
  answered.value=false; showFeedback.value=false; phase.value='play'
  questions.value = Array.from({length:totalQ}, genQ)
  speak('구구단을 풀어봐요!')
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect; showFeedback.value = true; fbProgress.value = 100
  clearInterval(fbTimer)
  const dur = isCorrect ? 1200 : 2200; const step = 50/dur*100
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
  const isOk = opt === cur.value.ans
  if (isOk) { score.value += 10; correct.value++ }
  speak(isOk ? '정답이에요!' : `정답은 ${cur.value.ans}이에요`)
  triggerFeedback(isOk)
}

async function endGame() {
  phase.value = 'end'
  const passed = correct.value >= Math.ceil(totalQ * 0.7)
  if (passed) {
    level.value++; localStorage.setItem('mult_level', level.value); leveled.value = true
    speak('구구단 마스터! 레벨업!')
  } else speak('다시 도전해봐요!')
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await axios.post('/api/games/12/score',
        { score: score.value, level: level.value, result: passed?'win':'lose', duration: totalQ*5 },
        { headers: { Authorization: `Bearer ${token}` } })
    } catch(e) {}
  }
}
</script>

<style scoped>
.mult-game { min-height:100vh; background:linear-gradient(135deg,#1e3a5f,#1d4ed8,#2563eb); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.level-preview { background:rgba(255,255,255,.1); color:#bfdbfe; padding:10px 24px; border-radius:20px; font-size:15px; font-weight:600; display:inline-block; margin:10px 0; }
.start-btn { background:#3b82f6; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin:10px 6px; }
.home-btn { background:rgba(255,255,255,.2); color:#fff; border:none; padding:12px 28px; border-radius:30px; font-size:16px; font-weight:600; cursor:pointer; margin:10px 6px; }
.play-box { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:20px; }
.progress-bar { flex:1; height:10px; background:rgba(255,255,255,.2); border-radius:5px; }
.progress-fill { height:100%; background:#93c5fd; border-radius:5px; transition:width .3s; }
.q-count { color:rgba(255,255,255,.8); font-size:13px; }
.equation-box { display:flex; align-items:center; justify-content:center; gap:12px; background:rgba(255,255,255,.15); border-radius:24px; padding:32px 20px; margin-bottom:16px; }
.eq-num { font-size:56px; font-weight:900; color:#fff; }
.eq-op { font-size:40px; font-weight:700; color:#93c5fd; }
.eq-ans { font-size:56px; font-weight:900; color:#fde68a; }
.mult-hint { text-align:center; color:rgba(255,255,255,.7); font-size:14px; margin-bottom:16px; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.choice-btn { background:rgba(255,255,255,.92); color:#1e3a5f; border:none; padding:20px; border-radius:16px; font-size:28px; font-weight:800; cursor:pointer; transition:all .15s; }
.choice-btn:hover:not(:disabled) { background:#fff; transform:scale(1.05); }
.choice-btn:disabled { cursor:default; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.end-score { color:rgba(255,255,255,.8); font-size:18px; }
.levelup-badge { background:#3b82f6; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
.feedback-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; z-index:999; backdrop-filter:blur(4px); }
.fb-correct { background:rgba(16,185,129,.88); }
.fb-wrong { background:rgba(239,68,68,.88); }
.fb-content { text-align:center; color:#fff; padding:32px 48px; }
.fb-emoji { font-size:80px; margin-bottom:8px; }
.fb-title { font-size:34px; font-weight:900; margin-bottom:8px; }
.fb-answer { font-size:20px; margin-bottom:16px; }
.fb-bar-wrap { width:200px; height:7px; background:rgba(255,255,255,.3); border-radius:4px; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:4px; transition:width .05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity .25s; }
.fb-enter-from,.fb-leave-to { opacity:0; }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/games/GameMultiplication.vue', multiplication)

# ============================================================
# 3. GameWordBlank.vue — 피드백 오버레이 + 점수저장
# ============================================================
print("\n=== GameWordBlank.vue 재작성 ===")
word_blank = r"""<template>
  <div class="wordblank-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 📝</div>
      <div class="score-badge">{{ score }}점</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">📝</div>
      <h1 class="title">빈칸 채우기</h1>
      <p class="subtitle">알맞은 단어로 빈칸을 채워요!</p>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>

    <div v-if="phase==='play'" class="play-box">
      <div class="progress-row">
        <div class="progress-bar"><div class="progress-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span class="q-count">{{ qIdx+1 }}/{{ totalQ }}</span>
      </div>
      <div v-if="cur" class="sentence-box">
        <p class="sentence-text" v-html="cur.display"></p>
        <p class="sentence-hint">{{ cur.hint }}</p>
      </div>
      <div class="choices-grid">
        <button v-for="opt in cur?.opts" :key="opt"
          class="choice-btn" :disabled="answered" @click="answer(opt)">{{ opt }}</button>
      </div>
    </div>

    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">{{ correct>=totalQ*0.7?'🎊':'📖' }}</div>
      <h2 class="end-title">{{ correct>=totalQ*0.7?'완벽해요!':'계속 연습해요!' }}</h2>
      <p class="end-score">{{ score }}점 · {{ correct }}/{{ totalQ }} 정답</p>
      <div v-if="leveled" class="levelup-badge">🌟 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
      <button class="home-btn" @click="$router.push('/games')">홈으로 🏠</button>
    </div>

    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect?'fb-correct':'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect && cur" class="fb-answer">정답은 「<strong>{{ cur.ans }}</strong>」이에요</div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const level = ref(parseInt(localStorage.getItem('wordblank_level')||'1'))
const score = ref(0); const qIdx = ref(0); const correct = ref(0)
const leveled = ref(false); const answered = ref(false); const phase = ref('start')
const showFeedback = ref(false); const lastCorrect = ref(false); const fbProgress = ref(100)
let fbTimer = null
const totalQ = 10
const questions = ref([])
const cur = computed(() => questions.value[qIdx.value])

const allQ = [
  { sentence:'나는 학교에 ___ 갑니다.', ans:'걸어서', hint:'도보로 이동하는 방법', opts:['걸어서','날아서','헤엄쳐서','기어서'] },
  { sentence:'하늘은 ___ 색입니다.', ans:'파란', hint:'맑은 날 하늘 색', opts:['파란','빨간','노란','초록'] },
  { sentence:'봄에는 ___ 꽃이 핍니다.', ans:'벚꽃', hint:'봄의 상징', opts:['벚꽃','해바라기','장미','국화'] },
  { sentence:'아침에 일어나서 ___ 을 합니다.', ans:'세수', hint:'얼굴을 씻는 것', opts:['세수','요리','청소','쇼핑'] },
  { sentence:'나는 배가 ___ 밥을 먹었습니다.', ans:'고파서', hint:'배고플 때', opts:['고파서','불러서','아파서','뜨거워서'] },
  { sentence:'도서관에서는 ___ 해야 합니다.', ans:'조용히', hint:'도서관 예절', opts:['조용히','크게','빠르게','자유롭게'] },
  { sentence:'여름은 ___ 계절입니다.', ans:'더운', hint:'여름의 특징', opts:['더운','추운','시원한','따뜻한'] },
  { sentence:'국어, 영어, 수학은 학교 ___ 입니다.', ans:'과목', hint:'학교에서 배우는 것', opts:['과목','친구','선생님','교실'] },
  { sentence:'버스를 타려면 ___ 에 가야 합니다.', ans:'정류장', hint:'버스가 멈추는 곳', opts:['정류장','공항','항구','역'] },
  { sentence:'바다에서 수영할 때 ___ 가 필요합니다.', ans:'수영복', hint:'수영할 때 입는 옷', opts:['수영복','외투','교복','잠옷'] },
  { sentence:'음식이 너무 ___ 물을 마셨어요.', ans:'매워서', hint:'맵게 느낄 때', opts:['매워서','달아서','써서','시어서'] },
  { sentence:'친구 생일에 ___ 을 줬어요.', ans:'선물', hint:'특별한 날에 주는 것', opts:['선물','숙제','편지','벌금'] },
  { sentence:'비가 오면 ___ 을 씁니다.', ans:'우산', hint:'비를 막는 도구', opts:['우산','선글라스','장갑','목도리'] },
  { sentence:'밤에는 ___ 이 빛납니다.', ans:'별', hint:'밤하늘에 반짝이는 것', opts:['별','태양','구름','비'] },
  { sentence:'병원에서 의사에게 ___ 을 받아요.', ans:'진료', hint:'병원에 가는 이유', opts:['진료','수업','재판','훈련'] },
]

function speak(t) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}
function shuffle(a){ return [...a].sort(()=>Math.random()-.5) }

function startGame() {
  score.value=0; qIdx.value=0; correct.value=0; leveled.value=false
  answered.value=false; showFeedback.value=false; phase.value='play'
  questions.value = shuffle(allQ).slice(0, totalQ).map(q=>({
    ...q,
    display: q.sentence.replace('___', '<span class="blank">　　　</span>'),
    opts: shuffle(q.opts)
  }))
  speak('빈칸에 알맞은 단어를 골라요!')
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect; showFeedback.value = true; fbProgress.value = 100
  clearInterval(fbTimer)
  const dur = isCorrect ? 1300 : 2200; const step = 50/dur*100
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
  const isOk = opt === cur.value.ans
  if (isOk) { score.value += 10; correct.value++ }
  speak(isOk ? '정답이에요!' : `정답은 ${cur.value.ans}이에요`)
  triggerFeedback(isOk)
}

async function endGame() {
  phase.value = 'end'
  const passed = correct.value >= Math.ceil(totalQ * 0.7)
  if (passed) {
    level.value++; localStorage.setItem('wordblank_level', level.value); leveled.value = true
    speak('완벽해요! 레벨업!')
  } else speak('잘 했어요! 다시 도전해봐요!')
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await axios.post('/api/games/13/score',
        { score: score.value, level: level.value, result: passed?'win':'lose', duration: totalQ*6 },
        { headers: { Authorization: `Bearer ${token}` } })
    } catch(e) {}
  }
}
</script>

<style scoped>
.wordblank-game { min-height:100vh; background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.start-btn { background:#e94560; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin:10px 6px; }
.home-btn { background:rgba(255,255,255,.2); color:#fff; border:none; padding:12px 28px; border-radius:30px; font-size:16px; font-weight:600; cursor:pointer; margin:10px 6px; }
.play-box { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:20px; }
.progress-bar { flex:1; height:10px; background:rgba(255,255,255,.2); border-radius:5px; }
.progress-fill { height:100%; background:#e94560; border-radius:5px; transition:width .3s; }
.q-count { color:rgba(255,255,255,.8); font-size:13px; }
.sentence-box { background:rgba(255,255,255,.1); border-radius:20px; padding:28px 20px; margin-bottom:20px; text-align:center; }
.sentence-text { font-size:22px; color:#fff; font-weight:700; line-height:1.8; margin:0 0 10px; }
.sentence-hint { color:rgba(255,255,255,.6); font-size:14px; margin:0; }
:deep(.blank) { display:inline-block; border-bottom:3px solid #e94560; min-width:80px; color:transparent; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.choice-btn { background:rgba(255,255,255,.92); color:#1a1a2e; border:none; padding:18px 12px; border-radius:16px; font-size:17px; font-weight:700; cursor:pointer; transition:all .15s; }
.choice-btn:hover:not(:disabled) { background:#fff; transform:scale(1.03); }
.choice-btn:disabled { cursor:default; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.end-score { color:rgba(255,255,255,.8); font-size:18px; }
.levelup-badge { background:#e94560; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
.feedback-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; z-index:999; backdrop-filter:blur(4px); }
.fb-correct { background:rgba(16,185,129,.88); }
.fb-wrong { background:rgba(239,68,68,.88); }
.fb-content { text-align:center; color:#fff; padding:32px 48px; }
.fb-emoji { font-size:80px; margin-bottom:8px; }
.fb-title { font-size:34px; font-weight:900; margin-bottom:8px; }
.fb-answer { font-size:18px; margin-bottom:16px; }
.fb-bar-wrap { width:200px; height:7px; background:rgba(255,255,255,.3); border-radius:4px; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:4px; transition:width .05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity .25s; }
.fb-enter-from,.fb-leave-to { opacity:0; }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/games/GameWordBlank.vue', word_blank)

# ============================================================
# 4. GameEngCard.vue — 피드백 오버레이 + 점수저장
# ============================================================
print("\n=== GameEngCard.vue 재작성 ===")
eng_card = r"""<template>
  <div class="engcard-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🇺🇸</div>
      <div class="score-badge">{{ score }}점</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">📖</div>
      <h1 class="title">영어 단어 카드</h1>
      <p class="subtitle">영어 단어와 한국어 뜻을 맞춰요!</p>
      <div class="mode-btns">
        <button :class="['mode-btn', mode==='eng2kor'?'active':'']" @click="mode='eng2kor'">영어 → 한국어</button>
        <button :class="['mode-btn', mode==='kor2eng'?'active':'']" @click="mode='kor2eng'">한국어 → 영어</button>
      </div>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>

    <div v-if="phase==='play'" class="play-box">
      <div class="progress-row">
        <div class="progress-bar"><div class="progress-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span class="q-count">{{ qIdx+1 }}/{{ totalQ }}</span>
      </div>
      <div v-if="cur" class="word-card">
        <div class="word-category">{{ cur.category }}</div>
        <div class="word-display">{{ mode==='eng2kor' ? cur.eng : cur.kor }}</div>
        <div class="word-phonetic" v-if="mode==='eng2kor'">{{ cur.phonetic }}</div>
      </div>
      <p class="question-text">{{ mode==='eng2kor' ? '한국어 뜻은 무엇인가요?' : '영어 단어는 무엇인가요?' }}</p>
      <div class="choices-grid">
        <button v-for="opt in cur?.opts" :key="opt"
          class="choice-btn" :disabled="answered" @click="answer(opt)">{{ opt }}</button>
      </div>
    </div>

    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">{{ correct>=totalQ*0.7?'🌟':'📚' }}</div>
      <h2 class="end-title">{{ correct>=totalQ*0.7?'영어 실력 UP!':'계속 연습해요!' }}</h2>
      <p class="end-score">{{ score }}점 · {{ correct }}/{{ totalQ }} 정답</p>
      <div v-if="leveled" class="levelup-badge">🎉 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
      <button class="home-btn" @click="$router.push('/games')">홈으로 🏠</button>
    </div>

    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect?'fb-correct':'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect && cur" class="fb-answer">
            정답: <strong>{{ mode==='eng2kor' ? cur.kor : cur.eng }}</strong>
          </div>
          <div v-if="cur" class="fb-extra">{{ cur.eng }} = {{ cur.kor }}</div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const level = ref(parseInt(localStorage.getItem('engcard_level')||'1'))
const score = ref(0); const qIdx = ref(0); const correct = ref(0)
const leveled = ref(false); const answered = ref(false); const phase = ref('start')
const showFeedback = ref(false); const lastCorrect = ref(false); const fbProgress = ref(100)
const mode = ref('eng2kor')
let fbTimer = null
const totalQ = 12
const questions = ref([])
const cur = computed(() => questions.value[qIdx.value])

const allWords = [
  {eng:'apple',    kor:'사과',    phonetic:'애플',   category:'과일'},
  {eng:'banana',   kor:'바나나',  phonetic:'바나나', category:'과일'},
  {eng:'orange',   kor:'오렌지',  phonetic:'오렌지', category:'과일'},
  {eng:'grape',    kor:'포도',    phonetic:'그레입', category:'과일'},
  {eng:'cat',      kor:'고양이',  phonetic:'캣',    category:'동물'},
  {eng:'dog',      kor:'강아지',  phonetic:'독',    category:'동물'},
  {eng:'bird',     kor:'새',      phonetic:'버드',  category:'동물'},
  {eng:'fish',     kor:'물고기',  phonetic:'피쉬',  category:'동물'},
  {eng:'book',     kor:'책',      phonetic:'북',    category:'물건'},
  {eng:'pen',      kor:'펜',      phonetic:'펜',    category:'물건'},
  {eng:'bag',      kor:'가방',    phonetic:'백',    category:'물건'},
  {eng:'chair',    kor:'의자',    phonetic:'체어',  category:'물건'},
  {eng:'red',      kor:'빨간색',  phonetic:'레드',  category:'색상'},
  {eng:'blue',     kor:'파란색',  phonetic:'블루',  category:'색상'},
  {eng:'green',    kor:'초록색',  phonetic:'그린',  category:'색상'},
  {eng:'yellow',   kor:'노란색',  phonetic:'옐로우', category:'색상'},
  {eng:'school',   kor:'학교',    phonetic:'스쿨',  category:'장소'},
  {eng:'house',    kor:'집',      phonetic:'하우스', category:'장소'},
  {eng:'hospital', kor:'병원',    phonetic:'하스피틀', category:'장소'},
  {eng:'park',     kor:'공원',    phonetic:'파크',  category:'장소'},
  {eng:'happy',    kor:'행복한',  phonetic:'해피',  category:'감정'},
  {eng:'sad',      kor:'슬픈',    phonetic:'새드',  category:'감정'},
  {eng:'angry',    kor:'화난',    phonetic:'앵그리', category:'감정'},
  {eng:'tired',    kor:'피곤한',  phonetic:'타이어드', category:'감정'},
]

function speak(t) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}
function shuffle(a){ return [...a].sort(()=>Math.random()-.5) }

function startGame() {
  score.value=0; qIdx.value=0; correct.value=0; leveled.value=false
  answered.value=false; showFeedback.value=false; phase.value='play'
  const pool = shuffle(allWords).slice(0, totalQ)
  questions.value = pool.map(w => {
    const distractors = shuffle(allWords.filter(x=>x!==w)).slice(0,3)
    const opts = mode.value==='eng2kor'
      ? shuffle([w.kor, ...distractors.map(d=>d.kor)])
      : shuffle([w.eng, ...distractors.map(d=>d.eng)])
    return {...w, opts}
  })
  speak('영어 단어를 맞춰봐요!')
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect; showFeedback.value = true; fbProgress.value = 100
  clearInterval(fbTimer)
  const dur = isCorrect ? 1300 : 2400; const step = 50/dur*100
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
  const correctAns = mode.value==='eng2kor' ? cur.value.kor : cur.value.eng
  const isOk = opt === correctAns
  if (isOk) { score.value += 10; correct.value++ }
  speak(isOk ? '정답이에요!' : `정답은 ${correctAns}이에요`)
  triggerFeedback(isOk)
}

async function endGame() {
  phase.value = 'end'
  const passed = correct.value >= Math.ceil(totalQ * 0.7)
  if (passed) {
    level.value++; localStorage.setItem('engcard_level', level.value); leveled.value = true
    speak('영어 실력이 늘었어요! 레벨업!')
  } else speak('계속 연습하면 잘 할 수 있어요!')
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await axios.post('/api/games/16/score',
        { score: score.value, level: level.value, result: passed?'win':'lose', duration: totalQ*6 },
        { headers: { Authorization: `Bearer ${token}` } })
    } catch(e) {}
  }
}
</script>

<style scoped>
.engcard-game { min-height:100vh; background:linear-gradient(135deg,#0f2027,#203a43,#2c5364); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.mode-btns { display:flex; gap:10px; justify-content:center; margin:16px 0; }
.mode-btn { background:rgba(255,255,255,.15); color:rgba(255,255,255,.7); border:none; padding:10px 20px; border-radius:20px; font-size:14px; font-weight:600; cursor:pointer; transition:all .2s; }
.mode-btn.active { background:#06b6d4; color:#fff; }
.start-btn { background:#06b6d4; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin:10px 6px; }
.home-btn { background:rgba(255,255,255,.2); color:#fff; border:none; padding:12px 28px; border-radius:30px; font-size:16px; font-weight:600; cursor:pointer; margin:10px 6px; }
.play-box { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:20px; }
.progress-bar { flex:1; height:10px; background:rgba(255,255,255,.2); border-radius:5px; }
.progress-fill { height:100%; background:#06b6d4; border-radius:5px; transition:width .3s; }
.q-count { color:rgba(255,255,255,.8); font-size:13px; }
.word-card { background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.2); border-radius:24px; padding:36px 24px; margin-bottom:20px; text-align:center; }
.word-category { font-size:12px; color:#67e8f9; font-weight:600; text-transform:uppercase; letter-spacing:2px; margin-bottom:12px; }
.word-display { font-size:48px; font-weight:900; color:#fff; margin-bottom:8px; }
.word-phonetic { font-size:16px; color:rgba(255,255,255,.6); }
.question-text { color:rgba(255,255,255,.85); font-size:16px; font-weight:600; text-align:center; margin-bottom:16px; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.choice-btn { background:rgba(255,255,255,.9); color:#0f2027; border:none; padding:16px 10px; border-radius:16px; font-size:16px; font-weight:700; cursor:pointer; transition:all .15s; }
.choice-btn:hover:not(:disabled) { background:#fff; transform:scale(1.03); }
.choice-btn:disabled { cursor:default; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.end-score { color:rgba(255,255,255,.8); font-size:18px; }
.levelup-badge { background:#06b6d4; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
.feedback-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; z-index:999; backdrop-filter:blur(4px); }
.fb-correct { background:rgba(16,185,129,.88); }
.fb-wrong { background:rgba(239,68,68,.88); }
.fb-content { text-align:center; color:#fff; padding:32px 48px; }
.fb-emoji { font-size:80px; margin-bottom:8px; }
.fb-title { font-size:34px; font-weight:900; margin-bottom:8px; }
.fb-answer { font-size:18px; margin-bottom:6px; }
.fb-extra { font-size:15px; opacity:.85; margin-bottom:12px; }
.fb-bar-wrap { width:200px; height:7px; background:rgba(255,255,255,.3); border-radius:4px; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:4px; transition:width .05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity .25s; }
.fb-enter-from,.fb-leave-to { opacity:0; }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/games/GameEngCard.vue', eng_card)

# ============================================================
# 5. Build
# ============================================================
print("\n=== npm 빌드 ===")
build = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -8", timeout=300)
print(build)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

print("\n========================================")
print("✅ Phase 2 완료!")
print("========================================")
print("1. GameMathBasic: 시각적 수 표현 + 연속정답 보너스 + 피드백 + 점수저장")
print("2. GameMultiplication: 단계별 구구단 + 피드백 + 점수저장")
print("3. GameWordBlank: 15개 빈칸 문제 + 피드백 + 점수저장")
print("4. GameEngCard: 영→한/한→영 모드 선택 + 24개 단어 + 피드백 + 점수저장")
print("========================================")

c.close()
