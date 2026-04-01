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

# ===== GAME 10: 끝말잇기 =====
game10 = r"""<template>
  <div class="wordchain-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🔗</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🔗</div>
      <h1 class="title">끝말잇기</h1>
      <p class="subtitle">앞 단어의 끝 글자로 시작하는 단어를 골라요!</p>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="timer-row">
        <div class="timer-bar">
          <div class="timer-fill" :style="{width:(timeLeft/maxTime*100)+'%', background: timeLeft<4?'#ef4444':'#3b82f6'}"></div>
        </div>
        <span class="timer-num">{{ timeLeft }}초</span>
      </div>
      <div class="chain-display">
        <div class="prev-word" v-if="chainWords.length>0">
          <span class="chain-label">이전</span>
          <span class="chain-word">{{ chainWords[chainWords.length-1] }}</span>
        </div>
        <div class="arrow">↓</div>
        <div class="start-char">
          <span class="chain-label">이 글자로 시작!</span>
          <span class="start-syllable">{{ currentStart }}</span>
        </div>
      </div>
      <div class="choices-grid">
        <button v-for="opt in options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===correctAnswer, wrong: answered && opt===picked && opt!==correctAnswer, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          {{ opt }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '정답! 🎉 '+correctAnswer : '정답은 「'+correctAnswer+'」이에요' }}
      </div>
      <div class="streak-row">연속 {{ streak }}개 🔥</div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">🏆</div>
      <div class="res-score">{{ score }}점</div>
      <div class="res-detail">{{ correct }}개 정답 · 연속 최대 {{ maxStreak }}개</div>
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

// 끝말잇기 단어 DB: {word, startsWith}
const wordDB = [
  {word:'사과',next:'과'},
  {word:'과일',next:'일'},
  {word:'일요일',next:'일'},
  {word:'일기',next:'기'},
  {word:'기차',next:'차'},
  {word:'차가운',next:'운'},
  {word:'운동',next:'동'},
  {word:'동생',next:'생'},
  {word:'생일',next:'일'},
  {word:'나무',next:'무'},
  {word:'무지개',next:'개'},
  {word:'개구리',next:'리'},
  {word:'리본',next:'본'},
  {word:'본보기',next:'기'},
  {word:'기린',next:'린'},
  {word:'고양이',next:'이'},
  {word:'이불',next:'불'},
  {word:'불꽃',next:'꽃'},
  {word:'꽃게',next:'게'},
  {word:'게임',next:'임'},
  {word:'임금',next:'금'},
  {word:'금요일',next:'일'},
  {word:'바나나',next:'나'},
  {word:'나비',next:'비'},
  {word:'비행기',next:'기'},
  {word:'기억',next:'억'},
  {word:'억만장자',next:'자'},
  {word:'자동차',next:'차'},
  {word:'차갑다',next:'다'},
  {word:'다리미',next:'미'},
  {word:'미래',next:'래'},
  {word:'래퍼',next:'퍼'},
  {word:'퍼즐',next:'즐'},
  {word:'즐거움',next:'움'},
  {word:'움직임',next:'임'},
  {word:'하늘',next:'늘'},
  {word:'늘보',next:'보'},
  {word:'보물',next:'물'},
  {word:'물고기',next:'기'},
  {word:'코끼리',next:'리'},
  {word:'리듬',next:'듬'},
  {word:'소나무',next:'무'},
  {word:'무릎',next:'릎'},
  {word:'강아지',next:'지'},
  {word:'지렁이',next:'이'},
  {word:'이야기',next:'기'},
  {word:'호랑이',next:'이'},
  {word:'이상',next:'상'},
  {word:'상자',next:'자'},
]

const level = ref(parseInt(localStorage.getItem('wordchain_level') || '1'))
const score = ref(0)
const correct = ref(0)
const streak = ref(0)
const maxStreak = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const correctAnswer = ref('')
const currentStart = ref('')
const options = ref([])
const chainWords = ref([])
const timeLeft = ref(15)
const maxTime = ref(15)
let timer = null
let roundCount = 0
const totalRounds = 10

function getMaxTime() {
  if (level.value <= 2) return 15
  if (level.value <= 4) return 10
  return 7
}

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9; u.pitch = 1.1
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function startGame() {
  score.value = 0; correct.value = 0; streak.value = 0; maxStreak.value = 0
  leveled.value = false; roundCount = 0; chainWords.value = []
  maxTime.value = getMaxTime()
  phase.value = 'play'
  nextRound()
}

function nextRound() {
  if (roundCount >= totalRounds) { endGame(); return }
  roundCount++
  answered.value = false; wasRight.value = false; picked.value = ''
  // Pick a start syllable
  const starter = chainWords.value.length > 0
    ? wordDB.find(w => w.word.startsWith(chainWords.value[chainWords.value.length-1].slice(-1)))
    : null
  const startChar = starter ? chainWords.value[chainWords.value.length-1].slice(-1)
    : wordDB[Math.floor(Math.random()*wordDB.length)].word[0]
  currentStart.value = startChar
  const matching = wordDB.filter(w => w.word.startsWith(startChar) && !chainWords.value.includes(w.word))
  if (matching.length === 0) { nextRound(); return }
  const correct_w = matching[Math.floor(Math.random()*matching.length)]
  correctAnswer.value = correct_w.word
  const wrong = shuffle(wordDB.filter(w => !w.word.startsWith(startChar))).slice(0,3).map(w=>w.word)
  options.value = shuffle([correct_w.word, ...wrong])
  speak(startChar + '로 시작하는 단어는?')
  startTimer()
}

function startTimer() {
  clearInterval(timer)
  timeLeft.value = maxTime.value
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) { clearInterval(timer); timeOut() }
  }, 1000)
}

function timeOut() {
  answered.value = true; wasRight.value = false
  streak.value = 0
  speak('시간 초과! 정답은 ' + correctAnswer.value)
  setTimeout(nextRound, 2000)
}

function selectAnswer(opt) {
  if (answered.value) return
  clearInterval(timer)
  answered.value = true; picked.value = opt
  wasRight.value = opt === correctAnswer.value
  if (wasRight.value) {
    correct.value++; streak.value++
    if (streak.value > maxStreak.value) maxStreak.value = streak.value
    score.value += 10 + (streak.value > 1 ? streak.value * 2 : 0)
    chainWords.value.push(correctAnswer.value)
    speak(correctAnswer.value + '! 정답!')
  } else {
    streak.value = 0
    speak('정답은 ' + correctAnswer.value)
  }
  setTimeout(nextRound, 1800)
}

function endGame() {
  clearInterval(timer)
  phase.value = 'result'
  const threshold = level.value <= 2 ? 6 : level.value <= 4 ? 7 : 8
  if (correct.value >= threshold) {
    level.value++
    localStorage.setItem('wordchain_level', level.value)
    leveled.value = true
    speak('레벨업! 레벨 ' + level.value + '!')
  }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.wordchain-game { min-height:100vh; background:linear-gradient(135deg,#667eea,#764ba2); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.2); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.2); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.8); font-size:16px; }
.level-info { color:#fde68a; margin:10px 0; font-size:15px; }
.start-btn { background:#fbbf24; color:#1e1b4b; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:480px; margin:0 auto; }
.timer-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.timer-bar { flex:1; height:12px; background:rgba(255,255,255,0.3); border-radius:6px; overflow:hidden; }
.timer-fill { height:100%; border-radius:6px; transition:width 1s linear; }
.timer-num { color:#fff; font-weight:700; font-size:18px; min-width:35px; }
.chain-display { background:rgba(255,255,255,0.15); border-radius:16px; padding:20px; text-align:center; margin-bottom:20px; }
.prev-word,.start-char { display:flex; flex-direction:column; align-items:center; gap:4px; }
.chain-label { color:rgba(255,255,255,0.7); font-size:13px; }
.chain-word { color:#fff; font-size:28px; font-weight:700; }
.arrow { color:rgba(255,255,255,0.5); font-size:24px; margin:6px 0; }
.start-syllable { color:#fde68a; font-size:48px; font-weight:900; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#374151; border:none; padding:16px; border-radius:12px; font-size:18px; font-weight:700; cursor:pointer; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { transform:scale(1.03); background:#fff; }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { text-align:center; padding:12px; border-radius:12px; font-size:18px; font-weight:700; margin-top:8px; }
.feedback.right { background:rgba(16,185,129,0.3); color:#d1fae5; }
.feedback.wrong { background:rgba(239,68,68,0.3); color:#fee2e2; }
.streak-row { text-align:center; color:#fde68a; font-size:15px; margin-top:8px; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#fde68a; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#fbbf24; color:#1e1b4b; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#374151; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#6366f1; color:#fff; }
</style>
"""

# ===== GAME 11: 타자 연습 =====
game11 = r"""<template>
  <div class="typing-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} ⌨️</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">⌨️</div>
      <h1 class="title">타자 연습</h1>
      <p class="subtitle">화면의 단어를 따라 타이핑해요!</p>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <div class="wpm-display">{{ wpm }} WPM</div>
      </div>
      <div class="target-display">
        <span v-for="(ch, i) in currentWord.split('')" :key="i"
          :class="charClass(i)">{{ ch }}</span>
      </div>
      <div class="input-area">
        <input ref="inputRef" v-model="typed" @input="onInput" @keydown.enter="checkWord"
          class="type-input" :placeholder="inputPlaceholder" autocomplete="off" autocorrect="off"
          autocapitalize="off" spellcheck="false" :disabled="answered" />
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '완벽해요! 🎉' : '아쉬워요! 다시 도전해요' }}
      </div>
      <div class="combo-row" v-if="combo > 1">🔥 콤보 {{ combo }}!</div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">🏆</div>
      <div class="res-score">{{ score }}점</div>
      <div class="res-detail">정확도 {{ accuracy }}% · {{ finalWpm }} WPM</div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 🔄</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const wordsByLevel = {
  1: ['사과','나무','강아지','고양이','하늘','바다','학교','집','밥','물'],
  2: ['아이스크림','자동차','비행기','기차','버스','도서관','병원','공원','시장','은행'],
  3: ['가족','친구','선생님','학생','공부','숙제','운동장','도서관','급식','쉬는시간'],
  4: ['대한민국','서울특별시','부산광역시','제주도','한강','남산타워','경복궁','인사동'],
  5: ['봄에는꽃이피고','여름에는바다에가요','가을에는단풍이들어','겨울에는눈이와요'],
}

const level = ref(parseInt(localStorage.getItem('typing_level') || '1'))
const score = ref(0)
const phase = ref('start')
const qIdx = ref(0)
const totalQ = ref(10)
const currentWord = ref('')
const typed = ref('')
const answered = ref(false)
const wasRight = ref(false)
const combo = ref(0)
const correct = ref(0)
const leveled = ref(false)
const wpm = ref(0)
const finalWpm = ref(0)
const accuracy = ref(0)
const inputRef = ref(null)
let startTime = null
let wordStartTime = null
let totalChars = 0
let correctChars = 0
let queue = []

const inputPlaceholder = computed(() => level.value >= 5 ? '여기에 타이핑하세요...' : '단어를 입력하세요')

function getWords() {
  const lv = Math.min(level.value, 5)
  const pool = wordsByLevel[lv] || wordsByLevel[1]
  return [...pool].sort(()=>Math.random()-0.5).slice(0, totalQ.value)
}

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.85; u.pitch = 1.0
  window.speechSynthesis.speak(u)
}

function charClass(i) {
  if (i >= typed.value.length) return 'ch-pending'
  return typed.value[i] === currentWord.value[i] ? 'ch-correct' : 'ch-wrong'
}

function startGame() {
  score.value = 0; correct.value = 0; combo.value = 0; leveled.value = false
  qIdx.value = 0; totalChars = 0; correctChars = 0
  queue = getWords()
  startTime = Date.now()
  phase.value = 'play'
  nextQuestion()
}

function nextQuestion() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  qIdx.value++
  currentWord.value = queue[qIdx.value - 1]
  typed.value = ''; answered.value = false; wasRight.value = false
  wordStartTime = Date.now()
  speak(currentWord.value)
  nextTick(() => inputRef.value?.focus())
}

function onInput() {
  if (typed.value === currentWord.value) {
    checkWord()
  }
  // live WPM
  const elapsed = (Date.now() - startTime) / 60000
  if (elapsed > 0) wpm.value = Math.round(totalChars / 5 / elapsed)
}

function checkWord() {
  if (answered.value) return
  answered.value = true
  const t = typed.value.trim()
  wasRight.value = t === currentWord.value
  totalChars += currentWord.value.length
  if (wasRight.value) {
    correct.value++; combo.value++
    correctChars += currentWord.value.length
    const timeTaken = (Date.now() - wordStartTime) / 1000
    const bonus = Math.max(0, Math.round(20 - timeTaken))
    score.value += 10 + bonus + (combo.value > 1 ? combo.value * 2 : 0)
    speak('잘했어요!')
  } else {
    combo.value = 0
    speak('틀렸어요. 정답은 ' + currentWord.value)
  }
  setTimeout(nextQuestion, 1500)
}

function endGame() {
  const elapsed = (Date.now() - startTime) / 60000
  finalWpm.value = elapsed > 0 ? Math.round(totalChars / 5 / elapsed) : 0
  accuracy.value = totalChars > 0 ? Math.round(correctChars / totalChars * 100) : 0
  phase.value = 'result'
  const threshold = level.value <= 2 ? 7 : level.value <= 4 ? 8 : 9
  if (correct.value >= threshold) {
    level.value++
    localStorage.setItem('typing_level', level.value)
    leveled.value = true
    speak('레벨업! 레벨 ' + level.value + '!')
  }
}

function goBack() { router.push('/games') }
</script>

<style scoped>
.typing-game { min-height:100vh; background:linear-gradient(135deg,#0f172a,#1e3a5f); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.7); font-size:16px; }
.level-info { color:#60a5fa; margin:10px 0; font-size:15px; }
.start-btn { background:#3b82f6; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:560px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:20px; color:rgba(255,255,255,0.7); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(255,255,255,0.2); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#3b82f6; border-radius:4px; transition:width 0.3s; }
.wpm-display { color:#60a5fa; font-weight:700; font-size:13px; }
.target-display { background:rgba(255,255,255,0.1); border-radius:16px; padding:30px 20px; text-align:center; font-size:clamp(28px,6vw,48px); font-weight:700; letter-spacing:4px; margin-bottom:20px; min-height:100px; display:flex; align-items:center; justify-content:center; flex-wrap:wrap; }
.ch-pending { color:rgba(255,255,255,0.7); }
.ch-correct { color:#34d399; }
.ch-wrong { color:#f87171; text-decoration:underline; }
.input-area { margin-bottom:16px; }
.type-input { width:100%; padding:16px 20px; font-size:20px; border:2px solid rgba(255,255,255,0.3); background:rgba(255,255,255,0.1); color:#fff; border-radius:12px; outline:none; text-align:center; letter-spacing:2px; box-sizing:border-box; }
.type-input:focus { border-color:#3b82f6; background:rgba(59,130,246,0.1); }
.type-input::placeholder { color:rgba(255,255,255,0.4); }
.feedback { text-align:center; padding:12px; border-radius:12px; font-size:18px; font-weight:700; }
.feedback.right { background:rgba(52,211,153,0.2); color:#6ee7b7; }
.feedback.wrong { background:rgba(248,113,113,0.2); color:#fca5a5; }
.combo-row { text-align:center; color:#fbbf24; font-size:16px; font-weight:700; margin-top:8px; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#60a5fa; }
.res-detail { color:rgba(255,255,255,0.7); font-size:16px; margin:8px 0; }
.levelup { background:#3b82f6; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#1e3a5f; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#3b82f6; color:#fff; }
</style>
"""

# ===== GAME 12: 구구단 마스터 =====
game12 = r"""<template>
  <div class="multiplication-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} ✖️</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">✖️</div>
      <h1 class="title">구구단 마스터</h1>
      <p class="subtitle">곱셈을 빠르게 계산해요!</p>
      <div class="level-info">
        <div>레벨 1-2: 2단·3단</div>
        <div>레벨 3-4: 4단·5단 추가</div>
        <div>레벨 5+: 6단~9단 모두</div>
        <div style="margin-top:8px">현재 레벨: {{ level }}</div>
      </div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="timer-row">
        <div class="timer-bar">
          <div class="timer-fill" :style="{width:(timeLeft/maxTime*100)+'%', background: timeLeft<4?'#ef4444':'#f59e0b'}"></div>
        </div>
        <span class="timer-num">{{ timeLeft }}</span>
      </div>
      <div class="question-card">
        <div class="dan-label">{{ currentA }}단</div>
        <div class="equation">{{ currentA }} × {{ currentB }} = ?</div>
      </div>
      <div class="choices-grid">
        <button v-for="opt in options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===correctAns, wrong: answered && opt===picked && opt!==correctAns, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          {{ opt }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '정답! '+currentA+'×'+currentB+'='+correctAns+'🎉' : currentA+'×'+currentB+'='+correctAns+' 이에요!' }}
      </div>
      <div class="progress-info">{{ qIdx }}/{{ totalQ }} · 연속 {{ streak }}🔥</div>
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

const korNum = ['','일','이','삼','사','오','육','칠','팔','구','십','십일','십이','십삼','십사','십오','십육','십칠','십팔','십구','이십','이십일','이십이','이십삼','이십사','이십오','이십육','이십칠','이십팔','이십구','삼십','삼십일','삼십이','삼십삼','삼십사','삼십오','삼십육','삼십칠','삼십팔','삼십구','사십','사십일','사십이','사십삼','사십사','사십오','사십육','사십칠','사십팔','사십구','오십','오십일','오십이','오십삼','오십사','오십오','오십육','오십칠','오십팔','오십구','육십','육십일','육십이','육십삼','육십사','육십오','육십육','육십칠','육십팔','육십구','칠십','칠십일','칠십이']

function getDans() {
  if (level.value <= 2) return [2,3]
  if (level.value <= 4) return [2,3,4,5]
  return [2,3,4,5,6,7,8,9]
}

const level = ref(parseInt(localStorage.getItem('multiplication_level') || '1'))
const score = ref(0)
const correct = ref(0)
const streak = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref(null)
const correctAns = ref(0)
const currentA = ref(2)
const currentB = ref(1)
const options = ref([])
const qIdx = ref(0)
const totalQ = ref(12)
const timeLeft = ref(10)
const maxTime = ref(10)
let timer = null
let roundCount = 0

function getMaxTime() {
  return level.value <= 2 ? 15 : level.value <= 4 ? 10 : 7
}

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.85; u.pitch = 1.0
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function startGame() {
  score.value = 0; correct.value = 0; streak.value = 0; leveled.value = false
  roundCount = 0; qIdx.value = 0; maxTime.value = getMaxTime()
  phase.value = 'play'
  nextRound()
}

function nextRound() {
  if (roundCount >= totalQ.value) { endGame(); return }
  roundCount++; qIdx.value = roundCount
  answered.value = false; wasRight.value = false; picked.value = null
  const dans = getDans()
  currentA.value = dans[Math.floor(Math.random()*dans.length)]
  currentB.value = Math.floor(Math.random()*9)+1
  correctAns.value = currentA.value * currentB.value
  // wrong answers
  const wrongs = new Set()
  while (wrongs.size < 3) {
    const w = correctAns.value + (Math.floor(Math.random()*8)-4)
    if (w > 0 && w !== correctAns.value) wrongs.add(w)
  }
  options.value = shuffle([correctAns.value, ...wrongs])
  speak(korNum[currentA.value] + ' 곱하기 ' + korNum[currentB.value] + ' 는?')
  startTimer()
}

function startTimer() {
  clearInterval(timer)
  timeLeft.value = maxTime.value
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) { clearInterval(timer); timeOut() }
  }, 1000)
}

function timeOut() {
  answered.value = true; wasRight.value = false
  streak.value = 0
  speak('시간 초과! 정답은 ' + korNum[correctAns.value])
  setTimeout(nextRound, 2000)
}

function selectAnswer(opt) {
  if (answered.value) return
  clearInterval(timer)
  answered.value = true; picked.value = opt
  wasRight.value = opt === correctAns.value
  if (wasRight.value) {
    correct.value++; streak.value++
    score.value += 10 + Math.max(0, timeLeft.value) + (streak.value > 1 ? streak.value * 3 : 0)
    speak(korNum[correctAns.value] + '! 정답!')
  } else {
    streak.value = 0
    speak('정답은 ' + korNum[correctAns.value])
  }
  setTimeout(nextRound, 1800)
}

function endGame() {
  clearInterval(timer)
  phase.value = 'result'
  const threshold = level.value <= 2 ? 8 : level.value <= 4 ? 9 : 10
  if (correct.value >= threshold) {
    level.value++
    localStorage.setItem('multiplication_level', level.value)
    leveled.value = true
    speak('레벨업! 레벨 ' + level.value + '!')
  }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.multiplication-game { min-height:100vh; background:linear-gradient(135deg,#f59e0b,#d97706,#b45309); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.2); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.2); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.9); font-size:16px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#fde68a; font-size:14px; line-height:1.8; margin:12px auto; max-width:280px; text-align:left; }
.start-btn { background:#fff; color:#b45309; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:480px; margin:0 auto; }
.timer-row { display:flex; align-items:center; gap:10px; margin-bottom:20px; }
.timer-bar { flex:1; height:14px; background:rgba(0,0,0,0.2); border-radius:7px; overflow:hidden; }
.timer-fill { height:100%; border-radius:7px; transition:width 1s linear; }
.timer-num { color:#fff; font-weight:900; font-size:24px; min-width:30px; text-align:right; }
.question-card { background:rgba(0,0,0,0.25); border-radius:20px; padding:30px 20px; text-align:center; margin-bottom:24px; }
.dan-label { color:#fde68a; font-size:16px; font-weight:700; margin-bottom:8px; }
.equation { color:#fff; font-size:52px; font-weight:900; letter-spacing:4px; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#374151; border:none; padding:18px; border-radius:14px; font-size:26px; font-weight:800; cursor:pointer; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { transform:scale(1.04); background:#fff; }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { text-align:center; padding:12px; border-radius:12px; font-size:16px; font-weight:700; margin-top:12px; }
.feedback.right { background:rgba(255,255,255,0.25); color:#fff; }
.feedback.wrong { background:rgba(0,0,0,0.2); color:#fde68a; }
.progress-info { text-align:center; color:rgba(255,255,255,0.8); font-size:14px; margin-top:8px; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#fff; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#fff; color:#b45309; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#92400e; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#92400e; color:#fff; }
</style>
"""

# ===== GAME 13: 한국어 단어 맞추기 (빈칸 채우기) =====
game13 = r"""<template>
  <div class="wordblank-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 📝</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">📝</div>
      <h1 class="title">단어 맞추기</h1>
      <p class="subtitle">빈칸에 들어갈 글자를 골라요!</p>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span>{{ streak }}🔥</span>
      </div>
      <div class="hint-emoji">{{ currentQ.emoji }}</div>
      <div class="word-display">
        <span v-for="(ch, i) in currentQ.word.split('')" :key="i" class="word-char"
          :class="{blank: i===currentQ.blankIdx}">
          {{ i === currentQ.blankIdx ? '?' : ch }}
        </span>
      </div>
      <div class="hint-text">{{ currentQ.hint }}</div>
      <div class="choices-grid">
        <button v-for="opt in options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===currentQ.word[currentQ.blankIdx], wrong: answered && opt===picked && opt!==currentQ.word[currentQ.blankIdx], disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          {{ opt }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '정답! '+currentQ.word+'! 🎉' : '정답은 「'+currentQ.word+'」이에요' }}
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const allWords = [
  {word:'사과',emoji:'🍎',hint:'빨간 과일',blankIdx:1},
  {word:'나무',emoji:'🌳',hint:'숲에 있어요',blankIdx:0},
  {word:'강아지',emoji:'🐶',hint:'멍멍 짖어요',blankIdx:1},
  {word:'고양이',emoji:'🐱',hint:'야옹 울어요',blankIdx:2},
  {word:'하늘',emoji:'☀️',hint:'위를 봐요',blankIdx:1},
  {word:'바나나',emoji:'🍌',hint:'노란 과일',blankIdx:2},
  {word:'자동차',emoji:'🚗',hint:'도로를 달려요',blankIdx:1},
  {word:'비행기',emoji:'✈️',hint:'하늘을 날아요',blankIdx:2},
  {word:'기차',emoji:'🚂',hint:'레일 위를 달려요',blankIdx:0},
  {word:'책',emoji:'📚',hint:'읽는 물건',blankIdx:1},
  {word:'학교',emoji:'🏫',hint:'공부하는 곳',blankIdx:0},
  {word:'선생님',emoji:'👩‍🏫',hint:'가르쳐 주세요',blankIdx:2},
  {word:'친구',emoji:'👫',hint:'같이 노는 사람',blankIdx:1},
  {word:'가족',emoji:'👨‍👩‍👧',hint:'함께 사는 사람들',blankIdx:1},
  {word:'병원',emoji:'🏥',hint:'아플 때 가요',blankIdx:0},
  {word:'도서관',emoji:'📖',hint:'책이 많은 곳',blankIdx:2},
  {word:'운동장',emoji:'⚽',hint:'운동하는 곳',blankIdx:1},
  {word:'수영장',emoji:'🏊',hint:'물에서 놀아요',blankIdx:2},
  {word:'음식',emoji:'🍱',hint:'먹는 것',blankIdx:1},
  {word:'하마',emoji:'🦛',hint:'물에 사는 동물',blankIdx:1},
  {word:'사자',emoji:'🦁',hint:'으르렁 왕',blankIdx:2},
  {word:'토끼',emoji:'🐰',hint:'귀가 길어요',blankIdx:1},
  {word:'펭귄',emoji:'🐧',hint:'남극에 살아요',blankIdx:0},
  {word:'거북이',emoji:'🐢',hint:'느린 동물',blankIdx:2},
  {word:'코끼리',emoji:'🐘',hint:'코가 길어요',blankIdx:1},
]

function getPool() {
  if (level.value <= 2) return allWords.filter(w => w.word.length <= 2)
  if (level.value <= 4) return allWords.filter(w => w.word.length <= 3)
  return allWords
}

const jamo = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㄲㄸㅃㅆㅉ아에이오우애에워웨위으ᅥᅦᅡᅧ가나다라마바사아자차카타파하'
const korChars = '가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허기니디리미비시이지치키티피히고노도로모보소오조초코토포호구누두루무부수우주추쿠투푸후'

const level = ref(parseInt(localStorage.getItem('wordblank_level') || '1'))
const score = ref(0)
const correct = ref(0)
const streak = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const currentQ = ref({word:'',emoji:'',hint:'',blankIdx:0})
const options = ref([])
const qIdx = ref(0)
const totalQ = ref(10)
let queue = []

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.85; u.pitch = 1.1
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function startGame() {
  score.value = 0; correct.value = 0; streak.value = 0; leveled.value = false
  qIdx.value = 0
  const pool = getPool()
  queue = shuffle(pool).slice(0, totalQ.value)
  phase.value = 'play'
  nextQuestion()
}

function nextQuestion() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  const q = queue[qIdx.value]; qIdx.value++
  currentQ.value = q
  answered.value = false; wasRight.value = false; picked.value = ''
  const correctChar = q.word[q.blankIdx]
  // generate wrong chars from similar looking/sounding characters
  const wrongPool = korChars.split('').filter(c => c !== correctChar)
  const wrongs = shuffle(wrongPool).slice(0,3)
  options.value = shuffle([correctChar, ...wrongs])
  speak(q.hint + '. 빈칸에 뭐가 들어갈까요?')
}

function selectAnswer(opt) {
  if (answered.value) return
  answered.value = true; picked.value = opt
  wasRight.value = opt === currentQ.value.word[currentQ.value.blankIdx]
  if (wasRight.value) {
    correct.value++; streak.value++
    score.value += 10 + (streak.value > 1 ? streak.value * 2 : 0)
    speak(currentQ.value.word + '! 정답!')
  } else {
    streak.value = 0
    speak('정답은 ' + currentQ.value.word + ' 이에요')
  }
  setTimeout(nextQuestion, 1800)
}

function endGame() {
  phase.value = 'result'
  const threshold = level.value <= 2 ? 7 : level.value <= 4 ? 8 : 9
  if (correct.value >= threshold) {
    level.value++
    localStorage.setItem('wordblank_level', level.value)
    leveled.value = true
    speak('레벨업! 레벨 ' + level.value + '!')
  }
}

function goBack() { router.push('/games') }
</script>

<style scoped>
.wordblank-game { min-height:100vh; background:linear-gradient(135deg,#10b981,#059669,#047857); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.2); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.2); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.9); font-size:16px; }
.level-info { color:#d1fae5; margin:10px 0; font-size:15px; }
.start-btn { background:#fff; color:#047857; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:20px; color:rgba(255,255,255,0.8); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(0,0,0,0.2); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#fff; border-radius:4px; transition:width 0.3s; }
.hint-emoji { text-align:center; font-size:80px; margin-bottom:12px; }
.word-display { display:flex; justify-content:center; gap:8px; margin-bottom:12px; }
.word-char { width:52px; height:52px; display:flex; align-items:center; justify-content:center; background:rgba(255,255,255,0.2); border-radius:10px; font-size:28px; font-weight:700; color:#fff; }
.word-char.blank { background:#fbbf24; color:#1e1b4b; font-size:32px; font-weight:900; box-shadow:0 0 12px rgba(251,191,36,0.5); }
.hint-text { text-align:center; color:#d1fae5; font-size:15px; margin-bottom:16px; }
.choices-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#047857; border:none; padding:14px 8px; border-radius:12px; font-size:22px; font-weight:800; cursor:pointer; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { transform:scale(1.06); background:#fff; }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { text-align:center; padding:12px; border-radius:12px; font-size:17px; font-weight:700; }
.feedback.right { background:rgba(255,255,255,0.2); color:#fff; }
.feedback.wrong { background:rgba(0,0,0,0.2); color:#fde68a; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#fff; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#fff; color:#047857; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#047857; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#047857; color:#fff; }
</style>
"""

# Write game files
print("=== 게임 10: 끝말잇기 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameWordChain.vue', game10)

print("=== 게임 11: 타자 연습 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameTyping.vue', game11)

print("=== 게임 12: 구구단 마스터 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameMultiplication.vue', game12)

print("=== 게임 13: 한국어 단어 맞추기 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameWordBlank.vue', game13)

# Update router
print("\n=== 라우터 업데이트 ===")
router_addition = ssh("grep -n 'game-wordle' /var/www/somekorean/resources/js/router/index.js | tail -1")
print("Wordle route line:", router_addition)

# Read current router and add new routes
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
new_routes = """  { path: '/games/wordchain', component: () => import('../pages/games/GameWordChain.vue'), name: 'game-wordchain' },
  { path: '/games/typing', component: () => import('../pages/games/GameTyping.vue'), name: 'game-typing' },
  { path: '/games/multiplication', component: () => import('../pages/games/GameMultiplication.vue'), name: 'game-multiplication' },
  { path: '/games/wordblank', component: () => import('../pages/games/GameWordBlank.vue'), name: 'game-wordblank' },"""

if 'game-wordchain' not in router_content:
    # Add before the closing of routes array
    updated = router_content.replace(
        "  { path: '/games/wordle'",
        new_routes + "\n  { path: '/games/wordle'"
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', updated)
    print("Router updated")
else:
    print("Routes already exist")

# Update DB route names
print("\n=== DB 라우트명 업데이트 ===")
updates = [
    ("끝말잇기", "game-wordchain"),
    ("타자연습", "game-typing"),
    ("구구단", "game-multiplication"),
    ("단어맞추기", "game-wordblank"),
]
for name, route in updates:
    r = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"UPDATE games SET route_name='{route}' WHERE name LIKE '%{name}%' OR slug LIKE '%{name}%';\"")
    print(f"{name} -> {route}: {r or 'OK'}")

# Build
print("\n=== npm 빌드 시작 ===")
build_result = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -20", timeout=300)
print(build_result)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

print("\n✅ 게임 10-13 배포 완료!")
c.close()
