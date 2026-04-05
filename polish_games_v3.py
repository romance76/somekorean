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
# 1. GameWordChain.vue — 끝말잇기 (완전 재작성)
# ============================================================
print("=== GameWordChain.vue 재작성 ===")
word_chain = r"""<template>
  <div class="chain-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🔗</div>
      <div class="score-badge">{{ score }}점</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">🔗</div>
      <h1 class="title">끝말잇기</h1>
      <p class="subtitle">마지막 글자로 시작하는 단어를 이어요!</p>
      <div class="rule-box">
        <p>예: <strong>사과</strong> → <strong>과자</strong> → <strong>자동차</strong></p>
      </div>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>

    <div v-if="phase==='play'" class="play-box">
      <div class="progress-row">
        <div class="progress-bar"><div class="progress-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span class="q-count">{{ qIdx+1 }}/{{ totalQ }}</span>
      </div>

      <div class="chain-display">
        <div v-for="(w,i) in chain" :key="i" class="chain-word" :class="{latest: i===chain.length-1}">
          <span class="word-text">{{ w }}</span>
          <span v-if="i<chain.length-1" class="arrow">→</span>
        </div>
      </div>

      <div class="prompt-box">
        <span class="prompt-label">「</span>
        <span class="last-char">{{ lastChar }}</span>
        <span class="prompt-label">」으로 시작하는 단어는?</span>
      </div>

      <div class="choices-grid">
        <button v-for="opt in opts" :key="opt"
          class="choice-btn" :disabled="answered" @click="answer(opt)">{{ opt }}</button>
      </div>
    </div>

    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">{{ score>=totalQ*8?'🏆':'🎯' }}</div>
      <h2 class="end-title">{{ score>=totalQ*8?'끝말잇기 달인!':'잘 했어요!' }}</h2>
      <p class="end-score">{{ score }}점 · {{ correct }}/{{ totalQ }} 정답</p>
      <div class="chain-review">
        <p class="review-label">이번 체인:</p>
        <p class="review-chain">{{ chain.join(' → ') }}</p>
      </div>
      <div v-if="leveled" class="levelup-badge">🌟 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
      <button class="home-btn" @click="$router.push('/games')">홈으로 🏠</button>
    </div>

    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect?'fb-correct':'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect" class="fb-answer">「{{ lastChar }}」으로 시작하는 단어: <strong>{{ correctAns }}</strong></div>
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
const level = ref(parseInt(localStorage.getItem('wordchain_level')||'1'))
const score = ref(0); const qIdx = ref(0); const correct = ref(0)
const leveled = ref(false); const answered = ref(false); const phase = ref('start')
const showFeedback = ref(false); const lastCorrect = ref(false); const fbProgress = ref(100)
const chain = ref([]); const opts = ref([]); const correctAns = ref('')
let fbTimer = null
const totalQ = 8

// 끝말잇기 단어 체인 데이터
const chainData = [
  { word:'사과', next:['과자','과일','과학'] },
  { word:'과자', next:['자동차','자전거','자연'] },
  { word:'자동차', next:['차도','차표','차가'] },
  { word:'기차', next:['차도','차장','차표'] },
  { word:'도서관', next:['관광','관심','관계'] },
  { word:'나무', next:['무지개','무서움','무릎'] },
  { word:'학교', next:['교실','교과서','교사'] },
  { word:'나라', next:['라면','라디오','라켓'] },
  { word:'바람', next:['람쥐','람사'] },
  { word:'구름', next:['름직하다'] },
  { word:'수박', next:['박수','박물관','박사'] },
  { word:'고양이', next:['이름','이사','이야기'] },
  { word:'하늘', next:['늘봄','늘다'] },
  { word:'바나나', next:['나라','나무','나비'] },
  { word:'어린이', next:['이름','이야기','이사'] },
  { word:'사랑', next:['랑데부'] },
  { word:'우리', next:['리본','리듬','리조트'] },
  { word:'모자', next:['자전거','자동차','자연'] },
  { word:'눈사람', next:['람쥐'] },
  { word:'책상', next:['상자','상어','상점'] },
  { word:'아이스크림', next:['림프','림프절'] },
  { word:'지구', next:['구름','구경','구청'] },
  { word:'별빛', next:['빛나다'] },
  { word:'봄바람', next:['람사'] },
]

// 더 체계적인 끝말잇기 퀴즈 세트
const quizSets = [
  { start:'기차', correct:'차도', wrong:['바람','나무','학교'] },
  { start:'도서관', correct:'관광', wrong:['나무','자동차','학교'] },
  { start:'나무', correct:'무지개', wrong:['학교','구름','도서관'] },
  { start:'학교', correct:'교실', wrong:['나무','바다','도서관'] },
  { start:'수박', correct:'박물관', wrong:['나무','학교','구름'] },
  { start:'고양이', correct:'이름', wrong:['나무','학교','박물관'] },
  { start:'바나나', correct:'나라', wrong:['학교','구름','도서관'] },
  { start:'어린이', correct:'이야기', wrong:['나무','학교','박물관'] },
  { start:'책상', correct:'상자', wrong:['나무','이야기','교실'] },
  { start:'지구', correct:'구름', wrong:['이름','나라','상자'] },
  { start:'모자', correct:'자전거', wrong:['이름','나라','교실'] },
  { start:'하늘', correct:'늘푸른나무', wrong:['이름','자전거','구름'] },
]

const lastChar = computed(() => chain.value.length > 0 ? chain.value[chain.value.length-1].slice(-1) : '')
const questions = ref([])
const curQ = computed(() => questions.value[qIdx.value])

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
  questions.value = shuffle(quizSets).slice(0, totalQ)
  chain.value = [questions.value[0].start]
  loadQuestion()
  speak('끝말잇기를 시작해요!')
}

function loadQuestion() {
  if (!curQ.value) return
  const q = curQ.value
  opts.value = shuffle([q.correct, ...q.wrong.slice(0,3)])
  correctAns.value = q.correct
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
      if (qIdx.value >= totalQ) { endGame(); return }
      chain.value.push(questions.value[qIdx.value].start)
      loadQuestion()
    }
  }, 50)
}

function answer(opt) {
  if (answered.value) return
  answered.value = true
  const isOk = opt === curQ.value.correct
  if (isOk) {
    score.value += 10; correct.value++
    chain.value.push(opt)
    speak(`정답! ${opt}`)
  } else {
    speak(`아쉬워요! 정답은 ${curQ.value.correct}이에요`)
  }
  triggerFeedback(isOk)
}

async function endGame() {
  phase.value = 'end'
  const passed = correct.value >= Math.ceil(totalQ * 0.6)
  if (passed) {
    level.value++; localStorage.setItem('wordchain_level', level.value); leveled.value = true
    speak('끝말잇기 달인! 레벨업!')
  } else speak('잘 했어요! 다시 도전해봐요!')
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await axios.post('/api/games/10/score',
        { score: score.value, level: level.value, result: passed?'win':'lose', duration: totalQ*8 },
        { headers: { Authorization: `Bearer ${token}` } })
    } catch(e) {}
  }
}
</script>

<style scoped>
.chain-game { min-height:100vh; background:linear-gradient(135deg,#2d1b69,#4c1d95,#5b21b6); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.rule-box { background:rgba(255,255,255,.1); border-radius:16px; padding:14px 20px; margin:16px auto; max-width:320px; color:#c4b5fd; font-size:15px; }
.rule-box strong { color:#fff; }
.start-btn { background:#7c3aed; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin:10px 6px; }
.home-btn { background:rgba(255,255,255,.2); color:#fff; border:none; padding:12px 28px; border-radius:30px; font-size:16px; font-weight:600; cursor:pointer; margin:10px 6px; }
.play-box { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.progress-bar { flex:1; height:10px; background:rgba(255,255,255,.2); border-radius:5px; }
.progress-fill { height:100%; background:#a78bfa; border-radius:5px; transition:width .3s; }
.q-count { color:rgba(255,255,255,.8); font-size:13px; }
.chain-display { display:flex; flex-wrap:wrap; gap:6px; background:rgba(255,255,255,.08); border-radius:16px; padding:14px; margin-bottom:16px; min-height:56px; align-items:center; }
.chain-word { display:flex; align-items:center; gap:6px; }
.word-text { background:rgba(255,255,255,.15); color:#fff; padding:5px 12px; border-radius:20px; font-size:14px; font-weight:600; }
.chain-word.latest .word-text { background:#7c3aed; font-size:15px; }
.arrow { color:rgba(255,255,255,.5); font-size:12px; }
.prompt-box { background:rgba(255,255,255,.12); border-radius:18px; padding:22px; text-align:center; margin-bottom:18px; }
.prompt-label { color:rgba(255,255,255,.7); font-size:20px; }
.last-char { color:#fde68a; font-size:48px; font-weight:900; margin:0 4px; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.choice-btn { background:rgba(255,255,255,.92); color:#2d1b69; border:none; padding:18px 10px; border-radius:16px; font-size:18px; font-weight:700; cursor:pointer; transition:all .15s; }
.choice-btn:hover:not(:disabled) { background:#fff; transform:scale(1.03); }
.choice-btn:disabled { cursor:default; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.end-score { color:rgba(255,255,255,.8); font-size:18px; }
.chain-review { background:rgba(255,255,255,.1); border-radius:14px; padding:16px; margin:16px auto; max-width:400px; }
.review-label { color:rgba(255,255,255,.6); font-size:13px; margin-bottom:6px; }
.review-chain { color:#c4b5fd; font-size:14px; word-break:break-all; }
.levelup-badge { background:#7c3aed; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
.feedback-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; z-index:999; backdrop-filter:blur(4px); }
.fb-correct { background:rgba(16,185,129,.88); }
.fb-wrong { background:rgba(239,68,68,.88); }
.fb-content { text-align:center; color:#fff; padding:32px 48px; }
.fb-emoji { font-size:80px; margin-bottom:8px; }
.fb-title { font-size:34px; font-weight:900; margin-bottom:8px; }
.fb-answer { font-size:17px; margin-bottom:16px; }
.fb-bar-wrap { width:200px; height:7px; background:rgba(255,255,255,.3); border-radius:4px; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:4px; transition:width .05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity .25s; }
.fb-enter-from,.fb-leave-to { opacity:0; }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/games/GameWordChain.vue', word_chain)

# ============================================================
# 2. GameTyping.vue — 한국어 타이핑 게임 (완전 재작성)
# ============================================================
print("\n=== GameTyping.vue 재작성 ===")
typing_game = r"""<template>
  <div class="typing-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} ⌨</div>
      <div class="info-row">
        <span class="timer-badge" :class="{warning: timeLeft<=5}">⏱ {{ timeLeft }}초</span>
        <span class="score-badge">{{ score }}점</span>
      </div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">⌨️</div>
      <h1 class="title">한국어 타이핑</h1>
      <p class="subtitle">단어를 빠르게 타이핑해요!</p>
      <div class="level-info">
        <p v-if="level<=2">짧은 단어 (2~3글자)</p>
        <p v-else-if="level<=4">보통 단어 (4~5글자)</p>
        <p v-else>긴 문장 도전!</p>
      </div>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>

    <div v-if="phase==='play'" class="play-box">
      <div class="stats-row">
        <div class="stat-box">
          <div class="stat-val">{{ typed }}</div>
          <div class="stat-label">완료</div>
        </div>
        <div class="timer-circle" :class="{warning: timeLeft<=5}">
          <svg viewBox="0 0 60 60">
            <circle cx="30" cy="30" r="26" fill="none" stroke="rgba(255,255,255,.2)" stroke-width="5"/>
            <circle cx="30" cy="30" r="26" fill="none" stroke="#fff" stroke-width="5"
              stroke-dasharray="163.4" :stroke-dashoffset="163.4*(1-timeLeft/totalTime)"
              stroke-linecap="round" transform="rotate(-90 30 30)"/>
          </svg>
          <div class="timer-text">{{ timeLeft }}</div>
        </div>
        <div class="stat-box">
          <div class="stat-val">{{ accuracy }}%</div>
          <div class="stat-label">정확도</div>
        </div>
      </div>

      <div class="word-display">
        <div class="word-to-type">{{ currentWord }}</div>
        <div class="word-hint" v-if="wordHint">{{ wordHint }}</div>
      </div>

      <div class="input-area">
        <input ref="inputRef" v-model="userInput"
          class="type-input" :class="inputStatus"
          @input="checkInput" @keydown.enter="skipWord"
          placeholder="여기에 타이핑하세요..."
          autocomplete="off" autocorrect="off" spellcheck="false"/>
        <button class="skip-btn" @click="skipWord">건너뛰기</button>
      </div>

      <div class="progress-words">
        <span v-for="(w,i) in wordQueue.slice(0,5)" :key="i"
          class="queued-word" :class="{active: i===0}">{{ w }}</span>
      </div>
    </div>

    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">{{ score>=80?'🏆':score>=50?'🥈':'📝' }}</div>
      <h2 class="end-title">{{ score>=80?'타이핑 마스터!':score>=50?'잘 했어요!':'계속 연습해요!' }}</h2>
      <div class="result-stats">
        <div class="r-stat"><span>완성 단어</span><strong>{{ typed }}개</strong></div>
        <div class="r-stat"><span>정확도</span><strong>{{ accuracy }}%</strong></div>
        <div class="r-stat"><span>점수</span><strong>{{ score }}점</strong></div>
      </div>
      <div v-if="leveled" class="levelup-badge">🌟 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
      <button class="home-btn" @click="$router.push('/games')">홈으로 🏠</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
const router = useRouter()
const level = ref(parseInt(localStorage.getItem('typing_level')||'1'))
const score = ref(0); const typed = ref(0); const mistakes = ref(0)
const leveled = ref(false); const phase = ref('start')
const userInput = ref(''); const currentWord = ref(''); const wordHint = ref('')
const inputStatus = ref(''); const inputRef = ref(null)
const timeLeft = ref(60); const totalTime = 60
const wordQueue = ref([])
let timer = null

const accuracy = computed(() => {
  const total = typed.value + mistakes.value
  return total === 0 ? 100 : Math.round(typed.value / total * 100)
})

const wordPools = {
  easy: ['나무','사과','달','별','집','물','밥','고양이','강아지','해','구름','꽃','새','책','공'],
  medium: ['학교','도서관','자동차','하늘색','선생님','친구들','가족','여행','음식','운동','공부','게임','음악','그림','바다'],
  hard: ['아이스크림','자전거타기','도서관에서','공부해요','운동장에서','뛰어놀아요','한국어를','열심히배워요']
}

function speak(t) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}
function shuffle(a){ return [...a].sort(()=>Math.random()-.5) }

function getPool() {
  if (level.value <= 2) return wordPools.easy
  if (level.value <= 4) return wordPools.medium
  return [...wordPools.medium, ...wordPools.hard]
}

function startGame() {
  score.value=0; typed.value=0; mistakes.value=0; leveled.value=false
  phase.value='play'; timeLeft.value=totalTime; userInput.value=''; inputStatus.value=''
  wordQueue.value = shuffle([...getPool(), ...getPool()]).slice(0, 20)
  loadNextWord()
  startTimer()
  nextTick(() => inputRef.value?.focus())
  speak('타이핑 게임 시작!')
}

function loadNextWord() {
  if (wordQueue.value.length === 0) { endGame(); return }
  currentWord.value = wordQueue.value.shift()
  wordHint.value = ''
  inputStatus.value = ''
}

function startTimer() {
  clearInterval(timer)
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) { clearInterval(timer); endGame() }
  }, 1000)
}

function checkInput() {
  const val = userInput.value
  const target = currentWord.value
  if (val === target) {
    inputStatus.value = 'correct'
    score.value += Math.ceil(10 * (level.value * 0.5 + 0.5))
    typed.value++
    userInput.value = ''
    loadNextWord()
  } else if (target.startsWith(val)) {
    inputStatus.value = 'typing'
  } else {
    inputStatus.value = 'wrong'
  }
}

function skipWord() {
  if (!userInput.value) {
    mistakes.value++
    loadNextWord()
  }
}

async function endGame() {
  clearInterval(timer)
  phase.value = 'end'
  const passed = typed.value >= 5 && accuracy.value >= 70
  if (passed) {
    level.value++; localStorage.setItem('typing_level', level.value); leveled.value = true
    speak('훌륭해요! 레벨업!')
  } else speak('잘 했어요! 더 빠르게 연습해봐요!')
  const token = localStorage.getItem('token')
  if (token) {
    try {
      await axios.post('/api/games/11/score',
        { score: score.value, level: level.value, result: passed?'win':'lose', duration: totalTime },
        { headers: { Authorization: `Bearer ${token}` } })
    } catch(e) {}
  }
}
</script>

<style scoped>
.typing-game { min-height:100vh; background:linear-gradient(135deg,#0a0a2e,#1a1a5e,#0f3460); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:8px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.info-row { display:flex; gap:8px; }
.timer-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.timer-badge.warning { background:rgba(239,68,68,.5); animation:pulse 1s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.6} }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.level-info { background:rgba(255,255,255,.1); color:#93c5fd; padding:10px 20px; border-radius:16px; display:inline-block; margin:12px 0; font-size:14px; }
.start-btn { background:#2563eb; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin:10px 6px; }
.home-btn { background:rgba(255,255,255,.2); color:#fff; border:none; padding:12px 28px; border-radius:30px; font-size:16px; font-weight:600; cursor:pointer; margin:10px 6px; }
.play-box { max-width:480px; margin:0 auto; }
.stats-row { display:flex; justify-content:space-around; align-items:center; margin-bottom:20px; }
.stat-box { text-align:center; }
.stat-val { font-size:28px; font-weight:800; color:#fff; }
.stat-label { font-size:12px; color:rgba(255,255,255,.6); }
.timer-circle { position:relative; width:70px; height:70px; }
.timer-circle svg { width:100%; height:100%; }
.timer-text { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; color:#fff; font-size:20px; font-weight:800; }
.timer-circle.warning .timer-text { color:#fca5a5; }
.word-display { background:rgba(255,255,255,.1); border-radius:20px; padding:28px 20px; margin-bottom:16px; text-align:center; }
.word-to-type { font-size:44px; font-weight:900; color:#fff; letter-spacing:4px; }
.word-hint { color:rgba(255,255,255,.6); font-size:14px; margin-top:8px; }
.input-area { display:flex; gap:10px; margin-bottom:16px; }
.type-input { flex:1; background:rgba(255,255,255,.9); border:3px solid transparent; border-radius:16px; padding:16px 20px; font-size:22px; font-weight:700; color:#0a0a2e; outline:none; font-family:inherit; transition:border-color .2s; }
.type-input.typing { border-color:#60a5fa; }
.type-input.correct { border-color:#34d399; background:#f0fdf4; }
.type-input.wrong { border-color:#f87171; background:#fff5f5; }
.skip-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:0 16px; border-radius:14px; font-size:13px; cursor:pointer; white-space:nowrap; }
.progress-words { display:flex; gap:8px; flex-wrap:wrap; }
.queued-word { background:rgba(255,255,255,.08); color:rgba(255,255,255,.5); padding:5px 12px; border-radius:20px; font-size:13px; }
.queued-word.active { background:rgba(37,99,235,.5); color:#fff; font-weight:700; }
.result-stats { display:flex; gap:16px; justify-content:center; margin:16px 0; flex-wrap:wrap; }
.r-stat { background:rgba(255,255,255,.1); padding:14px 20px; border-radius:14px; text-align:center; min-width:90px; }
.r-stat span { display:block; color:rgba(255,255,255,.6); font-size:12px; }
.r-stat strong { display:block; color:#fff; font-size:22px; font-weight:800; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.levelup-badge { background:#2563eb; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
</style>
"""
write_file('/var/www/somekorean/resources/js/pages/games/GameTyping.vue', typing_game)

# ============================================================
# 3. Build
# ============================================================
print("\n=== npm 빌드 ===")
build = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -8", timeout=300)
print(build)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

# ============================================================
# 4. 전체 현황 확인
# ============================================================
print("\n=== 전체 게임 현황 ===")
print(ssh("""mysql --defaults-file=/tmp/sk_main.cnf somekorean -e "
SELECT g.id, g.name, gc.name as category, g.route_name, g.is_active
FROM games g
LEFT JOIN game_categories gc ON g.category_id=gc.id
ORDER BY g.category_id, g.sort_order, g.id;
" """))

print("\n========================================")
print("✅ Phase 3 완료!")
print("========================================")
print("1. GameWordChain: 끝말잇기 체인 표시 + 피드백 오버레이 + 점수저장")
print("2. GameTyping: 타이머 + 정확도 측정 + 실시간 입력 체크 + 점수저장")
print("========================================")
print("\n모든 어린이/청소년 게임 피드백 오버레이 완료!")
print("게임 ID별 점수저장 API 연동 완료!")

c.close()
