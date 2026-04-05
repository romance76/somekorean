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

# ===== 스트룹 테스트 =====
game_stroop = r"""<template>
  <div class="stroop-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🎨</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🎨</div>
      <h1 class="title">색깔 스트룹</h1>
      <p class="subtitle">글자의 색깔을 골라요! (글자 내용 말고 색깔!)</p>
      <div class="example-row">
        <span style="color:#ef4444;font-size:28px;font-weight:700">파랑</span>
        <span style="color:#3b82f6;font-size:16px;margin:0 8px">← 이 글자의 색은?</span>
        <span style="color:#fff;font-size:20px">빨강</span>
      </div>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 🎯</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="top-row">
        <div class="timer-box" :style="{color:timeLeft<4?'#ef4444':'#fff'}">⏱ {{ timeLeft }}</div>
        <div class="combo-box" v-if="combo>1">🔥 {{ combo }}콤보</div>
        <div class="count-box">{{ qIdx }}/{{ totalQ }}</div>
      </div>
      <div class="stroop-word" :style="{color: wordColor}">{{ wordText }}</div>
      <div class="color-choices">
        <button v-for="col in colorChoices" :key="col.name" class="color-btn"
          :style="{background: col.hex}"
          :class="{correct: answered && col.name===wordColorName, wrong: answered && col.name===picked && col.name!==wordColorName, disabled: answered}"
          :disabled="answered" @click="selectColor(col.name)">
          {{ col.name }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '정답! 🎉' : '글자 색은 ' + wordColorName + '이에요!' }}
      </div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">🏆</div>
      <div class="res-score">{{ score }}점</div>
      <div class="res-detail">{{ correct }}/{{ totalQ }} · 최대콤보 {{ maxCombo }}🔥</div>
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

const colors = [
  {name:'빨강',hex:'#ef4444'},
  {name:'파랑',hex:'#3b82f6'},
  {name:'초록',hex:'#10b981'},
  {name:'노랑',hex:'#fbbf24'},
  {name:'보라',hex:'#8b5cf6'},
  {name:'주황',hex:'#f97316'},
]

const level = ref(parseInt(localStorage.getItem('stroop_level') || '1'))
const score = ref(0)
const correct = ref(0)
const combo = ref(0)
const maxCombo = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const wordText = ref('')
const wordColor = ref('#fff')
const wordColorName = ref('')
const colorChoices = ref([])
const qIdx = ref(0)
const totalQ = ref(15)
const timeLeft = ref(8)
const maxTime = ref(8)
let timer = null

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function startGame() {
  score.value=0; correct.value=0; combo.value=0; maxCombo.value=0; leveled.value=false
  qIdx.value=0; maxTime.value=level.value<=2?8:level.value<=4?5:3
  const numColors = level.value<=2?4:level.value<=4?5:6
  colorChoices.value = colors.slice(0,numColors)
  phase.value='play'; nextRound()
}

function nextRound() {
  if(qIdx.value>=totalQ.value){endGame();return}
  qIdx.value++; answered.value=false; wasRight.value=false; picked.value=''
  const pool = colorChoices.value
  const textColor = pool[Math.floor(Math.random()*pool.length)]
  let displayColor = pool[Math.floor(Math.random()*pool.length)]
  // At higher levels, force mismatch more often
  if(level.value >= 3 && Math.random() > 0.3) {
    const others = pool.filter(c=>c.name!==textColor.name)
    if(others.length) displayColor = others[Math.floor(Math.random()*others.length)]
  }
  wordText.value = textColor.name
  wordColor.value = displayColor.hex
  wordColorName.value = displayColor.name
  startTimer()
}

function startTimer() {
  clearInterval(timer); timeLeft.value=maxTime.value
  timer=setInterval(()=>{ timeLeft.value--; if(timeLeft.value<=0){clearInterval(timer);timeOut()} },1000)
}

function timeOut() {
  answered.value=true; wasRight.value=false; combo.value=0
  setTimeout(nextRound, 1000)
}

function selectColor(name) {
  if(answered.value) return
  clearInterval(timer); answered.value=true; picked.value=name
  wasRight.value = name===wordColorName.value
  if(wasRight.value){ correct.value++; combo.value++; if(combo.value>maxCombo.value)maxCombo.value=combo.value; score.value+=10+timeLeft.value*2+(combo.value>1?combo.value*3:0) }
  else combo.value=0
  setTimeout(nextRound, 1000)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=12){ level.value++; localStorage.setItem('stroop_level',level.value); leveled.value=true }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.stroop-game { min-height:100vh; background:#111827; padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.12); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.12); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.7); font-size:15px; }
.example-row { margin:16px 0; display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:4px; }
.level-info { color:#9ca3af; font-size:15px; margin:10px 0; }
.start-btn { background:#8b5cf6; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:400px; margin:0 auto; display:flex; flex-direction:column; align-items:center; }
.top-row { display:flex; gap:12px; margin-bottom:20px; width:100%; justify-content:space-between; align-items:center; }
.timer-box,.combo-box,.count-box { font-size:18px; font-weight:700; padding:6px 14px; background:rgba(255,255,255,0.1); border-radius:12px; }
.timer-box { color:#fff; }
.combo-box { color:#fbbf24; }
.count-box { color:rgba(255,255,255,0.6); }
.stroop-word { font-size:72px; font-weight:900; text-align:center; margin-bottom:32px; transition:color 0.1s; }
.color-choices { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; width:100%; margin-bottom:16px; }
.color-btn { padding:18px 8px; border:none; border-radius:14px; font-size:18px; font-weight:800; color:#fff; cursor:pointer; transition:all 0.15s; text-shadow:0 1px 3px rgba(0,0,0,0.5); }
.color-btn:hover:not(.disabled) { transform:scale(1.05); }
.color-btn.correct { outline:4px solid #fff; transform:scale(1.05); }
.color-btn.wrong { opacity:0.5; }
.color-btn.disabled { cursor:not-allowed; }
.feedback { text-align:center; font-size:18px; font-weight:700; color:#fff; padding:10px; }
.feedback.right { color:#10b981; }
.feedback.wrong { color:#ef4444; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#8b5cf6; }
.res-detail { color:rgba(255,255,255,0.7); font-size:16px; margin:8px 0; }
.levelup { background:#8b5cf6; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#111827; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#8b5cf6; color:#fff; }
</style>
"""

# ===== 명상 호흡 게임 (시니어) =====
game_breathing = r"""<template>
  <div class="breathing-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🧘</div>
      <div class="score">{{ completedCycles }}회 완료</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🧘</div>
      <h1 class="title">명상 호흡</h1>
      <p class="subtitle">화면을 따라 천천히 숨 쉬어요<br>마음이 편안해져요</p>
      <div class="level-info">
        <div>레벨 1: 4-4-4 호흡 (박스 호흡)</div>
        <div>레벨 2: 4-7-8 호흡 (이완 호흡)</div>
        <div>레벨 3: 복식 호흡 훈련</div>
      </div>
      <button class="start-btn" @click="startGame">시작 🍃</button>
    </div>

    <div v-if="phase==='breathing'" class="breathing-area">
      <div class="cycle-count">{{ completedCycles }}회 / {{ targetCycles }}회</div>
      <div class="breath-circle" :class="breathPhase" :style="circleStyle">
        <div class="breath-text">{{ breathInstruction }}</div>
        <div class="breath-count">{{ breathCount }}</div>
      </div>
      <div class="phase-label">{{ phaseLabel }}</div>
      <div class="progress-dots">
        <span v-for="i in targetCycles" :key="i" class="dot" :class="{done: i<=completedCycles}"></span>
      </div>
      <button class="stop-btn" @click="stopGame">일시정지</button>
    </div>

    <div v-if="phase==='complete'" class="result-box">
      <div style="font-size:80px">🌟</div>
      <h2 class="res-title">수고했어요!</h2>
      <div class="res-detail">{{ completedCycles }}회 호흡 완료</div>
      <div class="res-msg">몸과 마음이 편안해졌나요?</div>
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

const level = ref(parseInt(localStorage.getItem('breathing_level') || '1'))
const phase = ref('start')
const breathPhase = ref('inhale')
const breathCount = ref(4)
const completedCycles = ref(0)
const leveled = ref(false)
let breathTimer = null

const patterns = {
  1: [{phase:'inhale',dur:4,text:'들이쉬기',label:'코로 천천히 들이쉬어요'},{phase:'hold',dur:4,text:'참기',label:'숨을 참아요'},{phase:'exhale',dur:4,text:'내쉬기',label:'입으로 천천히 내쉬어요'},{phase:'hold2',dur:4,text:'참기',label:'잠시 쉬어요'}],
  2: [{phase:'inhale',dur:4,text:'들이쉬기',label:'코로 4초 들이쉬어요'},{phase:'hold',dur:7,text:'참기',label:'7초 동안 참아요'},{phase:'exhale',dur:8,text:'내쉬기',label:'입으로 8초 내쉬어요'}],
  3: [{phase:'inhale',dur:5,text:'배로 숨쉬기',label:'배가 불룩해지도록 들이쉬어요'},{phase:'hold',dur:2,text:'참기',label:'잠깐 멈춰요'},{phase:'exhale',dur:6,text:'배 집어넣기',label:'배를 집어넣으며 내쉬어요'}],
}

const targetCycles = computed(() => level.value <= 1 ? 5 : level.value <= 2 ? 6 : 8)

const breathInstruction = ref('준비')
const phaseLabel = ref('시작해요')
const circleStyle = ref({})

function speak(text, rate = 0.7) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = rate; u.pitch = 0.9; u.volume = 0.8
  window.speechSynthesis.speak(u)
}

function startGame() {
  completedCycles.value = 0; leveled.value = false
  phase.value = 'breathing'
  speak('호흡 명상을 시작합니다. 편안하게 앉으세요.')
  setTimeout(runBreathing, 2000)
}

async function runBreathing() {
  const pattern = patterns[Math.min(level.value, 3)]
  while (completedCycles.value < targetCycles.value && phase.value === 'breathing') {
    for (const step of pattern) {
      if (phase.value !== 'breathing') return
      breathPhase.value = step.phase
      breathInstruction.value = step.text
      phaseLabel.value = step.label
      circleStyle.value = {
        transform: step.phase === 'inhale' ? 'scale(1.3)' : step.phase === 'exhale' ? 'scale(0.85)' : 'scale(1.1)',
        transition: `transform ${step.dur}s ease`
      }
      speak(step.text, 0.6)
      for (let i = step.dur; i >= 1; i--) {
        if (phase.value !== 'breathing') return
        breathCount.value = i
        await delay(1000)
      }
    }
    completedCycles.value++
    if (completedCycles.value < targetCycles.value) speak('잘했어요. 한 번 더.')
  }
  if (phase.value === 'breathing') {
    phase.value = 'complete'
    speak('모두 완료했어요. 수고했습니다.')
    if (targetCycles.value >= 5) {
      level.value++; localStorage.setItem('breathing_level', level.value)
      leveled.value = true
    }
  }
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)) }
function stopGame() { phase.value = 'start'; window.speechSynthesis.cancel() }
function goBack() { phase.value = 'start'; window.speechSynthesis.cancel(); router.push('/games') }
onUnmounted(() => { clearInterval(breathTimer); window.speechSynthesis?.cancel() })
</script>

<style scoped>
.breathing-game { min-height:100vh; background:linear-gradient(180deg,#0f2027,#203a43,#2c5364); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; }
.back-btn { background:rgba(255,255,255,0.1); color:#a7f3d0; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.1); color:#a7f3d0; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#a7f3d0; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.7); font-size:16px; line-height:1.8; }
.level-info { background:rgba(255,255,255,0.07); border-radius:12px; padding:14px 20px; color:#6ee7b7; font-size:14px; line-height:1.9; margin:16px auto; max-width:280px; text-align:left; }
.start-btn { background:#10b981; color:#fff; border:none; padding:16px 44px; border-radius:30px; font-size:20px; font-weight:700; cursor:pointer; margin-top:20px; }
.breathing-area { display:flex; flex-direction:column; align-items:center; padding:20px; }
.cycle-count { color:#6ee7b7; font-size:16px; font-weight:600; margin-bottom:20px; }
.breath-circle { width:200px; height:200px; border-radius:50%; background:radial-gradient(circle,rgba(16,185,129,0.5),rgba(6,182,212,0.2)); border:3px solid rgba(16,185,129,0.5); display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:24px; box-shadow:0 0 40px rgba(16,185,129,0.2); }
.breath-text { color:#fff; font-size:22px; font-weight:700; }
.breath-count { color:#6ee7b7; font-size:36px; font-weight:900; margin-top:4px; }
.phase-label { color:rgba(255,255,255,0.7); font-size:16px; text-align:center; margin-bottom:24px; }
.progress-dots { display:flex; gap:10px; margin-bottom:24px; }
.dot { width:16px; height:16px; border-radius:50%; background:rgba(255,255,255,0.2); transition:background 0.5s; }
.dot.done { background:#10b981; }
.stop-btn { background:rgba(255,255,255,0.12); color:#a7f3d0; border:none; padding:10px 24px; border-radius:20px; cursor:pointer; font-size:15px; }
.result-box { text-align:center; padding:40px 20px; }
.res-title { font-size:34px; color:#a7f3d0; font-weight:900; margin:10px 0; }
.res-detail { color:rgba(255,255,255,0.8); font-size:18px; }
.res-msg { color:#6ee7b7; font-size:16px; margin:8px 0; }
.levelup { background:#10b981; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#0f2027; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#10b981; color:#fff; }
</style>
"""

# ===== 시니어 기억력 카드 (더 쉬운 버전) =====
game_senior_memory = r"""<template>
  <div class="senior-memory">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🌸</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🌸</div>
      <h1 class="title">기억력 카드</h1>
      <p class="subtitle">같은 그림 두 장을 찾아요!</p>
      <div class="level-info">
        <div style="font-size:16px">레벨 1: 4쌍 (2×4)</div>
        <div style="font-size:16px">레벨 2: 6쌍 (3×4)</div>
        <div style="font-size:16px">레벨 3+: 8쌍 (4×4)</div>
      </div>
      <button class="start-btn" @click="startGame">시작해요! 🃏</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="game-top">
        <div class="moves-info">👆 {{ moves }}번</div>
        <div class="matched-info">✅ {{ matched }}/{{ totalPairs }}쌍</div>
        <div class="timer-info">⏱ {{ elapsed }}초</div>
      </div>
      <div class="card-grid" :style="gridStyle">
        <div v-for="(card, i) in cards" :key="i"
          class="big-card" :class="{flipped: card.flipped||card.matched, matched: card.matched}"
          @click="flipCard(i)">
          <div class="big-face front">?</div>
          <div class="big-face back">{{ card.emoji }}</div>
        </div>
      </div>
    </div>

    <div v-if="phase==='complete'" class="result-box">
      <div style="font-size:80px">🎊</div>
      <div class="res-title">잘했어요!</div>
      <div class="res-stats">{{ moves }}번 만에 완성!</div>
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

const seniorEmojis = ['🌸','🌻','🌺','🍎','🍊','🍇','🌙','⭐','🌈','🦋','🐶','🐱','🌳','🏠','❤️','🎵']

const level = ref(parseInt(localStorage.getItem('senior_memory_level') || '1'))
const phase = ref('start')
const cards = ref([])
const moves = ref(0)
const matched = ref(0)
const elapsed = ref(0)
const score = ref(0)
const leveled = ref(false)
let f1 = ref(-1), f2 = ref(-1), checking = false
let timerInterval = null, startTime = null

const totalPairs = computed(() => level.value <= 1 ? 4 : level.value <= 2 ? 6 : 8)
const gridStyle = computed(() => {
  const cols = level.value <= 1 ? 4 : 4
  return { gridTemplateColumns: `repeat(${cols}, 1fr)` }
})

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.8; u.pitch = 1.0
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(() => Math.random()-0.5) }

function startGame() {
  const pairs = totalPairs.value
  const emojis = shuffle(seniorEmojis).slice(0, pairs)
  cards.value = shuffle([...emojis, ...emojis].map(e => ({emoji:e, flipped:false, matched:false})))
  moves.value = 0; matched.value = 0; score.value = 0; leveled.value = false
  f1.value = -1; f2.value = -1; checking = false
  elapsed.value = 0; startTime = Date.now()
  clearInterval(timerInterval)
  timerInterval = setInterval(() => { elapsed.value = Math.round((Date.now()-startTime)/1000) }, 1000)
  phase.value = 'play'
  speak('같은 그림을 찾아보세요!')
}

function flipCard(i) {
  if (checking || cards.value[i].matched || cards.value[i].flipped) return
  if (f1.value >= 0 && f2.value >= 0) return
  cards.value[i] = {...cards.value[i], flipped: true}
  if (f1.value < 0) { f1.value = i; return }
  f2.value = i; moves.value++; checking = true
  setTimeout(() => {
    const c1 = cards.value[f1.value], c2 = cards.value[f2.value]
    if (c1.emoji === c2.emoji) {
      cards.value[f1.value] = {...c1, matched:true, flipped:false}
      cards.value[f2.value] = {...c2, matched:true, flipped:false}
      matched.value++; speak('맞아요!')
      if (matched.value === totalPairs.value) {
        clearInterval(timerInterval)
        const threshold = level.value <= 1 ? 12 : level.value <= 2 ? 18 : 24
        if (moves.value <= threshold) { level.value++; localStorage.setItem('senior_memory_level', level.value); leveled.value = true }
        phase.value = 'complete'
        speak(leveled.value ? '완성! 레벨업!' : '완성! 잘하셨어요!')
      }
    } else {
      cards.value[f1.value] = {...c1, flipped:false}
      cards.value[f2.value] = {...c2, flipped:false}
    }
    f1.value = -1; f2.value = -1; checking = false
  }, 1200)
}

function goBack() { clearInterval(timerInterval); router.push('/games') }
onUnmounted(() => clearInterval(timerInterval))
</script>

<style scoped>
.senior-memory { min-height:100vh; background:linear-gradient(135deg,#fdf4ff,#fce7f3,#ffe4e6); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(0,0,0,0.08); color:#831843; border:none; padding:10px 16px; border-radius:20px; cursor:pointer; font-size:15px; font-weight:600; }
.level-badge,.score { background:rgba(0,0,0,0.08); color:#831843; padding:8px 16px; border-radius:20px; font-weight:700; font-size:15px; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:40px; color:#831843; font-weight:900; margin:10px 0; }
.subtitle { color:#9d174d; font-size:18px; }
.level-info { background:rgba(255,255,255,0.7); border-radius:12px; padding:16px 20px; color:#831843; line-height:2; margin:16px auto; max-width:240px; }
.start-btn { background:#ec4899; color:#fff; border:none; padding:18px 48px; border-radius:30px; font-size:22px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { display:flex; flex-direction:column; align-items:center; }
.game-top { display:flex; gap:12px; margin-bottom:16px; }
.moves-info,.matched-info,.timer-info { background:rgba(255,255,255,0.8); color:#831843; padding:8px 14px; border-radius:12px; font-size:16px; font-weight:700; }
.card-grid { display:grid; gap:10px; }
.big-card { width:76px; height:76px; cursor:pointer; perspective:600px; position:relative; }
.big-face { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; border-radius:14px; font-size:36px; backface-visibility:hidden; transition:transform 0.5s; }
.front { background:rgba(255,255,255,0.8); border:3px solid #f9a8d4; color:#9d174d; font-size:32px; font-weight:900; transform:rotateY(0deg); }
.back { background:rgba(255,255,255,0.95); border:3px solid #ec4899; transform:rotateY(180deg); }
.big-card.flipped .front { transform:rotateY(180deg); }
.big-card.flipped .back { transform:rotateY(0deg); }
.big-card.matched .front { transform:rotateY(180deg); }
.big-card.matched .back { background:#fce7f3; border-color:#ec4899; transform:rotateY(0deg); }
.result-box { text-align:center; padding:40px 20px; }
.res-title { font-size:40px; color:#831843; font-weight:900; margin:10px 0; }
.res-stats { color:#9d174d; font-size:20px; margin:8px 0; }
.levelup { background:#ec4899; color:#fff; padding:12px 24px; border-radius:20px; font-weight:800; font-size:20px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#831843; border:2px solid #f9a8d4; padding:14px 30px; border-radius:20px; font-size:18px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#ec4899; color:#fff; border:none; }
</style>
"""

# Write files
print("=== 색깔 스트룹 테스트 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameStroop.vue', game_stroop)

print("=== 명상 호흡 게임 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameBreathing.vue', game_breathing)

print("=== 시니어 기억력 카드 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameSeniorMemory.vue', game_senior_memory)

# Update router
print("\n=== 라우터 업데이트 ===")
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
new_routes = """  { path: '/games/stroop', component: () => import('../pages/games/GameStroop.vue'), name: 'game-stroop' },
  { path: '/games/breathing', component: () => import('../pages/games/GameBreathing.vue'), name: 'game-breathing' },
  { path: '/games/senior-memory', component: () => import('../pages/games/GameSeniorMemory.vue'), name: 'game-senior-memory' },
  { path: '/games/senior-bingo', component: () => import('../pages/games/GameBingo.vue'), name: 'game-senior-bingo' },
  { path: '/games/brain-calc', component: () => import('../pages/games/GameSpeedCalc.vue'), name: 'game-brain-calc' },
  { path: '/games/picture-memory', component: () => import('../pages/games/GameMemory.vue'), name: 'game-picture-memory' },"""

if 'game-stroop' not in router_content:
    updated = router_content.replace(
        "  { path: '/games/bingo'",
        new_routes + "\n  { path: '/games/bingo'"
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', updated)
    print("Router updated")
else:
    print("Routes already exist")

# Build
print("\n=== npm 빌드 ===")
build_result = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -6", timeout=300)
print(build_result)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

# Final DB check
print("\n=== 최종 라우트 현황 ===")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SELECT id, name, route_name FROM games ORDER BY id;\""))

print("\n✅ 모든 게임 배포 완료!")
c.close()
