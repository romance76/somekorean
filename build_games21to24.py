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

# ===== GAME 21: 한국어 맞춤법 퀴즈 =====
game21 = r"""<template>
  <div class="spelling-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} ✍️</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">✍️</div>
      <h1 class="title">한국어 맞춤법</h1>
      <p class="subtitle">올바른 맞춤법을 골라요!</p>
      <div class="level-info">
        <div>레벨 1-2: 기초 맞춤법</div>
        <div>레벨 3-4: 띄어쓰기·외래어</div>
        <div>레벨 5+: 고급 문법</div>
      </div>
      <button class="start-btn" @click="startGame">시작! ✏️</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span :style="{color:timeLeft<5?'#ef4444':'#fff'}">{{ timeLeft }}초</span>
      </div>
      <div class="question-card">
        <div class="q-label">올바른 표현은?</div>
        <div class="q-context" v-if="curQ.context">
          <span v-html="curQ.context"></span>
        </div>
      </div>
      <div class="choices-col">
        <button v-for="opt in curQ.options" :key="opt.text" class="choice-btn"
          :class="{correct: answered && opt.correct, wrong: answered && !opt.correct && opt.text===picked, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          <span class="choice-text">{{ opt.text }}</span>
          <span v-if="answered && opt.correct" class="check-mark">✓</span>
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        <div class="fb-main">{{ wasRight ? '정답! 🎉' : '오답!' }}</div>
        <div class="fb-explain">{{ curQ.explain }}</div>
      </div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">📝</div>
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

const quizDB = [
  {level:1,context:'밥을 <u>먹었어요</u> / <u>먹었어요</u>',options:[{text:'먹었어요',correct:true},{text:'먹었서요',correct:false}],explain:'"먹었어요"가 올바른 표현이에요.'},
  {level:1,context:'학교에 <u>갔어요</u> / <u>갔어요</u>',options:[{text:'갔어요',correct:true},{text:'갓어요',correct:false}],explain:'"갔어요"가 맞아요. 받침 ㅅ이 겹칩니다.'},
  {level:1,context:'',options:[{text:'되어야',correct:true},{text:'돼야',correct:false}],explain:'"되어야"와 "돼야" 둘 다 맞지만 "돼야"가 더 자연스러워요.'},
  {level:1,context:'',options:[{text:'안 돼요',correct:true},{text:'안 되요',correct:false}],explain:'"돼요"는 "되어요"의 줄임말이에요. "되요"는 틀려요.'},
  {level:1,context:'',options:[{text:'않아요',correct:true},{text:'안아요',correct:false}],explain:'"않아요" = 아니 하여요. "안아요" = 포옹하다.'},
  {level:1,context:'',options:[{text:'왠지',correct:true},{text:'웬지',correct:false}],explain:'"왠지"가 맞아요. 이유를 모를 때 씁니다.'},
  {level:1,context:'',options:[{text:'어떡해',correct:true},{text:'어떻해',correct:false}],explain:'"어떡해"가 맞아요. "어떻게 해"의 줄임말이에요.'},
  {level:1,context:'',options:[{text:'맞히다',correct:true},{text:'맞추다',correct:false}],explain:'"맞히다" = 정답을 맞추는 것. "맞추다" = 틈새를 채우는 것.'},
  {level:2,context:'',options:[{text:'오랜만에',correct:true},{text:'오랫만에',correct:false}],explain:'"오랜만에"가 맞아요. 오랜 + 만 + 에.'},
  {level:2,context:'',options:[{text:'일찍이',correct:true},{text:'일찌기',correct:false}],explain:'"일찍이"가 맞아요. "일찍 + 이".'},
  {level:2,context:'',options:[{text:'금세',correct:true},{text:'금새',correct:false}],explain:'"금세"가 맞아요. "금시에"의 줄임말이에요.'},
  {level:2,context:'',options:[{text:'이따가',correct:true},{text:'있다가',correct:false}],explain:'"이따가"는 "잠시 후에"라는 뜻이에요.'},
  {level:2,context:'',options:[{text:'역할',correct:true},{text:'역활',correct:false}],explain:'"역할"이 맞아요. 외워두세요!'},
  {level:2,context:'',options:[{text:'깨끗이',correct:true},{text:'깨끗히',correct:false}],explain:'ㅅ 받침 뒤에는 "-이" 씁니다.'},
  {level:3,context:'',options:[{text:'통째로',correct:true},{text:'통채로',correct:false}],explain:'"통째로"가 맞아요. 전체를 뜻해요.'},
  {level:3,context:'',options:[{text:'굳이',correct:true},{text:'구지',correct:false}],explain:'"굳이"가 맞아요. 발음은 [구지].'},
]

const level = ref(parseInt(localStorage.getItem('spelling_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const curQ = ref({options:[],explain:''})
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(20)
const maxTime = ref(20)
let timer = null
let queue = []

function getPool() {
  const maxLv = level.value<=2?1:level.value<=4?2:3
  return quizDB.filter(q=>q.level<=maxLv)
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
  maxTime.value = level.value<=2?20:level.value<=4?15:10
  const pool = getPool()
  queue = shuffle(pool).slice(0,totalQ.value)
  phase.value='play'
  nextQuestion()
}

function nextQuestion() {
  if(qIdx.value>=totalQ.value){endGame();return}
  const q = queue[qIdx.value]; qIdx.value++
  curQ.value = {...q, options: shuffle([...q.options])}
  answered.value=false; wasRight.value=false; picked.value=''
  speak('올바른 표현을 골라요')
  startTimer()
}

function startTimer() {
  clearInterval(timer); timeLeft.value=maxTime.value
  timer=setInterval(()=>{
    timeLeft.value--
    if(timeLeft.value<=0){clearInterval(timer);timeOut()}
  },1000)
}

function timeOut() {
  answered.value=true; wasRight.value=false
  const correctOpt = curQ.value.options.find(o=>o.correct)
  speak('시간 초과! 정답은 ' + correctOpt?.text)
  setTimeout(nextQuestion,2500)
}

function selectAnswer(opt) {
  if(answered.value) return
  clearInterval(timer)
  answered.value=true; picked.value=opt.text
  wasRight.value=opt.correct
  if(wasRight.value){ correct.value++; score.value+=10+timeLeft.value; speak('정답!') }
  else { speak('오답! ' + curQ.value.explain) }
  setTimeout(nextQuestion,2800)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=8){ level.value++; localStorage.setItem('spelling_level',level.value); leveled.value=true; speak('레벨업!') }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.spelling-game { min-height:100vh; background:linear-gradient(135deg,#7c2d12,#9a3412,#c2410c); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.85); font-size:16px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#fed7aa; font-size:14px; line-height:1.8; margin:12px auto; max-width:240px; text-align:left; }
.start-btn { background:#fff; color:#7c2d12; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; color:rgba(255,255,255,0.8); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(255,255,255,0.2); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#f97316; border-radius:4px; transition:width 0.3s; }
.question-card { background:rgba(255,255,255,0.12); border-radius:20px; padding:24px 20px; text-align:center; margin-bottom:16px; }
.q-label { color:rgba(255,255,255,0.7); font-size:14px; margin-bottom:8px; }
.q-context { color:#fff; font-size:20px; font-weight:600; }
.choices-col { display:flex; flex-direction:column; gap:10px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#7c2d12; border:none; padding:16px 20px; border-radius:12px; font-size:18px; font-weight:700; cursor:pointer; display:flex; justify-content:space-between; align-items:center; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { background:#fff; transform:translateX(4px); }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.check-mark { font-size:20px; }
.feedback { padding:14px 16px; border-radius:12px; }
.feedback.right { background:rgba(16,185,129,0.2); color:#a7f3d0; }
.feedback.wrong { background:rgba(239,68,68,0.2); color:#fca5a5; }
.fb-main { font-size:18px; font-weight:700; margin-bottom:4px; }
.fb-explain { font-size:14px; font-weight:400; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#fff; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#fff; color:#7c2d12; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#7c2d12; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#c2410c; color:#fff; }
</style>
"""

# ===== GAME 22: 스피드 계산 (연속 암산) =====
game22 = r"""<template>
  <div class="speedcalc-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} ⚡</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">⚡</div>
      <h1 class="title">스피드 계산</h1>
      <p class="subtitle">60초 안에 최대한 많이 맞춰요!</p>
      <div class="level-info">
        <div>레벨 1: 1-9 덧셈뺄셈</div>
        <div>레벨 3: 두 자리 연산</div>
        <div>레벨 5+: 곱셈·나눗셈 포함</div>
      </div>
      <div class="best-display">🏆 최고기록: {{ bestScore }}개</div>
      <button class="start-btn" @click="startGame">GO! ⚡</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="top-bar">
        <div class="timer-big" :class="{urgent: timeLeft<=10}">{{ timeLeft }}</div>
        <div class="count-display">
          <div class="count-correct">✅ {{ correct }}</div>
          <div class="count-wrong">❌ {{ wrong }}</div>
        </div>
      </div>
      <div class="equation-big">{{ equation }}</div>
      <div class="input-row">
        <input ref="answerInput" v-model="userAnswer" @keydown.enter="submitAnswer"
          type="number" class="answer-input" placeholder="답?"
          :class="{flash: flashing}" autocomplete="off" />
        <button class="submit-btn" @click="submitAnswer">확인</button>
      </div>
      <div class="feedback-flash" v-if="flashMsg" :class="flashType">{{ flashMsg }}</div>
      <div class="num-pad">
        <button v-for="n in [7,8,9,4,5,6,1,2,3,0]" :key="n" class="num-key" @click="appendNum(n)">{{ n }}</button>
        <button class="num-key del" @click="deleteLast">⌫</button>
        <button class="num-key neg" @click="toggleNeg">±</button>
      </div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">{{ correct >= 20 ? '🏆' : correct >= 10 ? '😊' : '💪' }}</div>
      <div class="res-score">{{ correct }}개 정답!</div>
      <div class="res-detail">정답 {{ correct }} · 오답 {{ wrong }}</div>
      <div class="res-best" v-if="isNewBest">🏆 신기록!</div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 ⚡</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const level = ref(parseInt(localStorage.getItem('speedcalc_level') || '1'))
const bestScore = ref(parseInt(localStorage.getItem('speedcalc_best') || '0'))
const phase = ref('start')
const score = ref(0)
const correct = ref(0)
const wrong = ref(0)
const equation = ref('')
const userAnswer = ref('')
const timeLeft = ref(60)
const flashing = ref(false)
const flashMsg = ref('')
const flashType = ref('ok')
const isNewBest = ref(false)
const leveled = ref(false)
const answerInput = ref(null)
let timer = null
let correctAns = 0

function speak(text) {
  if(!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang='ko-KR'; u.rate=1.1
  window.speechSynthesis.speak(u)
}

function rand(a, b) { return Math.floor(Math.random()*(b-a+1))+a }

function genEquation() {
  const lv = level.value
  if(lv <= 2) {
    const a=rand(1,9), b=rand(1,9), op=Math.random()>0.5?'+':'-'
    if(op==='+'){correctAns=a+b;equation.value=`${a} + ${b} = ?`}
    else{const big=Math.max(a,b),small=Math.min(a,b);correctAns=big-small;equation.value=`${big} - ${small} = ?`}
  } else if(lv <= 4) {
    const ops=['+','-','×']
    const op=ops[rand(0,2)]
    if(op==='+'){const a=rand(10,99),b=rand(10,99);correctAns=a+b;equation.value=`${a} + ${b} = ?`}
    else if(op==='-'){const a=rand(20,99),b=rand(1,a);correctAns=a-b;equation.value=`${a} - ${b} = ?`}
    else{const a=rand(2,9),b=rand(2,9);correctAns=a*b;equation.value=`${a} × ${b} = ?`}
  } else {
    const ops=['+','-','×','÷','²']
    const op=ops[rand(0,4)]
    if(op==='+'){const a=rand(50,999),b=rand(50,999);correctAns=a+b;equation.value=`${a} + ${b} = ?`}
    else if(op==='-'){const a=rand(100,999),b=rand(1,a);correctAns=a-b;equation.value=`${a} - ${b} = ?`}
    else if(op==='×'){const a=rand(2,12),b=rand(2,12);correctAns=a*b;equation.value=`${a} × ${b} = ?`}
    else if(op==='÷'){const b=rand(2,9),a=b*rand(2,9);correctAns=a/b;equation.value=`${a} ÷ ${b} = ?`}
    else{const a=rand(2,15);correctAns=a*a;equation.value=`${a}² = ?`}
  }
}

function startGame() {
  score.value=0; correct.value=0; wrong.value=0; leveled.value=false; isNewBest.value=false
  phase.value='play'; timeLeft.value=60; flashMsg.value=''
  genEquation(); userAnswer.value=''
  clearInterval(timer)
  timer=setInterval(()=>{
    timeLeft.value--
    if(timeLeft.value<=0){clearInterval(timer);endGame()}
  },1000)
  nextTick(()=>answerInput.value?.focus())
  speak('시작!')
}

function submitAnswer() {
  const val = parseInt(userAnswer.value)
  if(isNaN(val)) return
  userAnswer.value=''
  if(val===correctAns){
    correct.value++; score.value+=level.value*5
    flashMsg.value='✓'; flashType.value='ok'
  } else {
    wrong.value++
    flashMsg.value='✗ ' + correctAns; flashType.value='err'
  }
  flashing.value=true; setTimeout(()=>{flashing.value=false;flashMsg.value=''},500)
  genEquation()
  nextTick(()=>answerInput.value?.focus())
}

function appendNum(n) { userAnswer.value+=n; answerInput.value?.focus() }
function deleteLast() { userAnswer.value=userAnswer.value.slice(0,-1) }
function toggleNeg() {
  if(userAnswer.value.startsWith('-')) userAnswer.value=userAnswer.value.slice(1)
  else userAnswer.value='-'+userAnswer.value
}

function endGame() {
  phase.value='result'
  if(correct.value>bestScore.value){
    bestScore.value=correct.value
    localStorage.setItem('speedcalc_best',correct.value)
    isNewBest.value=true
  }
  const threshold=level.value<=2?10:level.value<=4?18:25
  if(correct.value>=threshold){
    level.value++; localStorage.setItem('speedcalc_level',level.value)
    leveled.value=true; speak('레벨업!')
  } else speak('게임종료! ' + correct.value + '개 정답!')
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.speedcalc-game { min-height:100vh; background:linear-gradient(135deg,#1c1917,#292524,#44403c); padding:16px; font-family:'Noto Sans KR',sans-serif; color:#fff; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.12); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.12); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.7); font-size:16px; }
.level-info { background:rgba(255,255,255,0.07); border-radius:12px; padding:12px 20px; color:#d6d3d1; font-size:14px; line-height:1.8; margin:12px auto; max-width:220px; text-align:left; }
.best-display { color:#fbbf24; font-size:16px; font-weight:700; margin:10px 0; }
.start-btn { background:#f59e0b; color:#1c1917; border:none; padding:14px 40px; border-radius:30px; font-size:22px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:400px; margin:0 auto; }
.top-bar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.timer-big { font-size:52px; font-weight:900; color:#f59e0b; transition:color 0.3s; min-width:70px; text-align:center; }
.timer-big.urgent { color:#ef4444; animation:pulse 0.5s infinite; }
@keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.1)} }
.count-display { display:flex; flex-direction:column; gap:4px; align-items:flex-end; }
.count-correct { color:#10b981; font-size:20px; font-weight:700; }
.count-wrong { color:#ef4444; font-size:20px; font-weight:700; }
.equation-big { font-size:52px; font-weight:900; text-align:center; margin-bottom:16px; background:rgba(255,255,255,0.07); border-radius:16px; padding:20px; letter-spacing:4px; }
.input-row { display:flex; gap:8px; margin-bottom:8px; }
.answer-input { flex:1; padding:14px 16px; font-size:28px; font-weight:700; text-align:center; background:rgba(255,255,255,0.1); border:2px solid rgba(255,255,255,0.3); color:#fff; border-radius:12px; outline:none; }
.answer-input:focus { border-color:#f59e0b; }
@keyframes flashAnim { 0%,100%{background:rgba(255,255,255,0.1)} 50%{background:rgba(245,158,11,0.3)} }
.answer-input.flash { animation:flashAnim 0.3s; }
.submit-btn { background:#f59e0b; color:#1c1917; border:none; padding:14px 20px; border-radius:12px; font-size:18px; font-weight:800; cursor:pointer; }
.feedback-flash { text-align:center; font-size:24px; font-weight:700; padding:8px; border-radius:10px; margin-bottom:8px; }
.feedback-flash.ok { color:#10b981; }
.feedback-flash.err { color:#ef4444; }
.num-pad { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-top:8px; }
.num-key { background:rgba(255,255,255,0.12); color:#fff; border:none; padding:16px; border-radius:10px; font-size:20px; font-weight:700; cursor:pointer; transition:all 0.1s; }
.num-key:active { transform:scale(0.93); background:rgba(255,255,255,0.25); }
.num-key.del { background:rgba(239,68,68,0.3); color:#fca5a5; }
.num-key.neg { background:rgba(99,102,241,0.3); color:#a5b4fc; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:52px; font-weight:900; color:#f59e0b; }
.res-detail { color:rgba(255,255,255,0.7); font-size:16px; margin:8px 0; }
.res-best { color:#fbbf24; font-size:20px; font-weight:800; margin:8px 0; }
.levelup { background:#f59e0b; color:#1c1917; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#1c1917; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#f59e0b; color:#1c1917; }
</style>
"""

# ===== GAME 23: 코딩 퀴즈 =====
game23 = r"""<template>
  <div class="coding-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 💻</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">💻</div>
      <h1 class="title">코딩 퀴즈</h1>
      <p class="subtitle">프로그래밍 개념을 테스트해요!</p>
      <div class="level-info">
        <div>레벨 1-2: HTML/CSS 기초</div>
        <div>레벨 3-4: JavaScript · Python</div>
        <div>레벨 5+: 알고리즘 · 자료구조</div>
      </div>
      <button class="start-btn" @click="startGame">시작! 🚀</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span :style="{color:timeLeft<6?'#ef4444':'#a5f3fc'}">{{ timeLeft }}초</span>
      </div>
      <div class="question-card">
        <div class="q-category">{{ curQ.category }}</div>
        <div class="q-text">{{ curQ.question }}</div>
        <div class="code-block" v-if="curQ.code"><pre>{{ curQ.code }}</pre></div>
      </div>
      <div class="choices-col">
        <button v-for="opt in curQ.options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===curQ.answer, wrong: answered && opt===picked && opt!==curQ.answer, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          <span class="choice-mono" v-if="curQ.codeOptions">{{ opt }}</span>
          <span v-else>{{ opt }}</span>
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        <div>{{ wasRight ? '정답! 🎉' : '오답! 정답: ' + curQ.answer }}</div>
        <div class="explain">{{ curQ.explain }}</div>
      </div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">{{ correct>=8?'🏆':'💪' }}</div>
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

const quizDB = [
  {level:1,category:'HTML',question:'웹페이지 제목을 나타내는 태그는?',options:['<title>','<head>','<h1>','<body>'],answer:'<title>',explain:'<title>은 브라우저 탭에 표시되는 페이지 제목이에요.',codeOptions:true},
  {level:1,category:'HTML',question:'링크를 만드는 HTML 태그는?',options:['<a>','<link>','<href>','<url>'],answer:'<a>',explain:'<a href="URL">텍스트</a> 형태로 사용해요.',codeOptions:true},
  {level:1,category:'CSS',question:'글자 색상을 바꾸는 CSS 속성은?',options:['color','font-color','text-color','foreground'],answer:'color',explain:'color: red; 처럼 사용해요.',codeOptions:true},
  {level:1,category:'CSS',question:'배경색을 지정하는 CSS 속성은?',options:['background-color','bg-color','back-color','color-bg'],answer:'background-color',explain:'background-color: blue; 처럼 사용해요.',codeOptions:true},
  {level:1,category:'개념',question:'HTML에서 HT는 무엇의 약자인가요?',options:['HyperText','HighType','HeatText','HardType'],answer:'HyperText',explain:'HTML = HyperText Markup Language에요.'},
  {level:2,category:'JavaScript',question:'변수를 선언하는 키워드가 아닌 것은?',options:['int','let','const','var'],answer:'int',explain:'JavaScript에는 int 키워드가 없어요. let, const, var를 사용해요.',codeOptions:true},
  {level:2,category:'JavaScript',question:'배열의 길이를 구하는 방법은?',options:['array.length','array.size()','array.count','len(array)'],answer:'array.length',explain:'JavaScript에서는 .length 속성으로 배열 길이를 구해요.',codeOptions:true},
  {level:2,category:'Python',question:'Python에서 화면에 출력하는 함수는?',options:['print()','echo()','console.log()','puts()'],answer:'print()',explain:'Python은 print("Hello") 로 출력해요.',codeOptions:true},
  {level:2,category:'Python',question:'Python 반복문: for i in ____(5):',options:['range','list','array','loop'],answer:'range',explain:'for i in range(5): 는 0,1,2,3,4를 순환해요.',codeOptions:true},
  {level:3,category:'알고리즘',question:'버블 정렬의 최악 시간 복잡도는?',options:['O(n²)','O(n)','O(log n)','O(n log n)'],answer:'O(n²)',explain:'버블 정렬은 최악의 경우 n²번 비교가 필요해요.'},
  {level:3,category:'자료구조',question:'LIFO(Last In First Out) 구조는?',options:['Stack','Queue','Tree','Graph'],answer:'Stack',explain:'Stack은 나중에 넣은 것이 먼저 나오는 구조예요.'},
  {level:3,category:'자료구조',question:'FIFO(First In First Out) 구조는?',options:['Queue','Stack','Heap','Array'],answer:'Queue',explain:'Queue는 먼저 넣은 것이 먼저 나오는 구조예요.'},
]

const level = ref(parseInt(localStorage.getItem('coding_level') || '1'))
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
  return quizDB.filter(q=>q.level<=maxLv)
}

function speak(text) {
  if(!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function startGame() {
  score.value=0; correct.value=0; leveled.value=false; qIdx.value=0
  maxTime.value=level.value<=2?25:level.value<=4?20:15
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
  timer=setInterval(()=>{
    timeLeft.value--
    if(timeLeft.value<=0){clearInterval(timer);timeOut()}
  },1000)
}

function timeOut() {
  answered.value=true; wasRight.value=false
  speak('시간 초과! 정답은 ' + curQ.value.answer)
  setTimeout(nextQuestion,2500)
}

function selectAnswer(opt) {
  if(answered.value) return
  clearInterval(timer)
  answered.value=true; picked.value=opt
  wasRight.value=opt===curQ.value.answer
  if(wasRight.value){correct.value++;score.value+=10+timeLeft.value;speak('정답!')}
  else speak('오답')
  setTimeout(nextQuestion,2800)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=8){level.value++;localStorage.setItem('coding_level',level.value);leveled.value=true;speak('레벨업!')}
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.coding-game { min-height:100vh; background:linear-gradient(135deg,#0f172a,#0c2340,#0a3d62); padding:16px; font-family:'Noto Sans KR','JetBrains Mono',monospace; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.1); color:#a5f3fc; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.1); color:#a5f3fc; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#a5f3fc; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.7); font-size:16px; }
.level-info { background:rgba(165,243,252,0.08); border-radius:12px; padding:12px 20px; color:#a5f3fc; font-size:14px; line-height:1.8; margin:12px auto; max-width:240px; text-align:left; font-family:monospace; }
.start-btn { background:#06b6d4; color:#0f172a; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:520px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; color:rgba(255,255,255,0.6); font-size:14px; }
.prog-bar { flex:1; height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden; }
.prog-fill { height:100%; background:#06b6d4; border-radius:3px; transition:width 0.3s; }
.question-card { background:rgba(255,255,255,0.06); border-radius:16px; padding:20px; margin-bottom:14px; border:1px solid rgba(165,243,252,0.15); }
.q-category { color:#06b6d4; font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:2px; margin-bottom:6px; }
.q-text { color:#fff; font-size:18px; font-weight:600; line-height:1.5; }
.code-block { background:#0d1117; border-radius:8px; padding:12px; margin-top:10px; border:1px solid rgba(165,243,252,0.2); }
.code-block pre { color:#a5f3fc; font-size:14px; font-family:monospace; margin:0; white-space:pre-wrap; }
.choices-col { display:flex; flex-direction:column; gap:8px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.08); color:#e2e8f0; border:1px solid rgba(165,243,252,0.2); padding:14px 16px; border-radius:10px; font-size:15px; font-weight:600; cursor:pointer; text-align:left; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { background:rgba(6,182,212,0.15); border-color:#06b6d4; }
.choice-btn.correct { background:rgba(16,185,129,0.25); border-color:#10b981; color:#a7f3d0; }
.choice-btn.wrong { background:rgba(239,68,68,0.2); border-color:#ef4444; color:#fca5a5; }
.choice-btn.disabled { cursor:not-allowed; }
.choice-mono { font-family:monospace; font-size:16px; }
.feedback { padding:12px 16px; border-radius:12px; margin-top:8px; }
.feedback.right { background:rgba(16,185,129,0.15); color:#a7f3d0; border:1px solid rgba(16,185,129,0.3); }
.feedback.wrong { background:rgba(239,68,68,0.1); color:#fca5a5; border:1px solid rgba(239,68,68,0.3); }
.explain { font-size:13px; font-weight:400; margin-top:4px; opacity:0.85; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:52px; font-weight:900; color:#a5f3fc; }
.res-detail { color:rgba(255,255,255,0.7); font-size:16px; margin:8px 0; }
.levelup { background:#06b6d4; color:#0f172a; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#0f172a; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#06b6d4; color:#0f172a; }
</style>
"""

# ===== GAME 24: 한국 역사 퀴즈 (타워 디펜스 대신 역사 퀴즈로 변경) =====
game24 = r"""<template>
  <div class="history-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🏛️</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🏛️</div>
      <h1 class="title">한국 역사 퀴즈</h1>
      <p class="subtitle">우리 역사를 알아보아요!</p>
      <div class="level-info">
        <div>레벨 1-2: 삼국시대 · 고려</div>
        <div>레벨 3-4: 조선시대</div>
        <div>레벨 5+: 근현대사</div>
      </div>
      <button class="start-btn" @click="startGame">시작! 🎖️</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span :style="{color:timeLeft<6?'#ef4444':'#fde68a'}">{{ timeLeft }}초</span>
      </div>
      <div class="era-badge">{{ curQ.era }}</div>
      <div class="question-card">
        <div class="q-text">{{ curQ.question }}</div>
        <div class="q-year" v-if="curQ.year">{{ curQ.year }}</div>
      </div>
      <div class="choices-grid">
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

const historyDB = [
  {level:1,era:'고조선',question:'우리나라 최초의 국가는?',options:['고조선','고구려','백제','신라'],answer:'고조선',year:'기원전 2333년',explain:'단군왕검이 세운 우리나라 최초의 국가예요.'},
  {level:1,era:'삼국시대',question:'신라가 삼국을 통일한 해는?',options:['676년','668년','660년','612년'],answer:'676년',year:'676년',explain:'신라는 당나라를 몰아내고 676년에 삼국통일을 완성했어요.'},
  {level:1,era:'삼국시대',question:'백제를 세운 사람은?',options:['온조','주몽','박혁거세','김수로'],answer:'온조',year:'기원전 18년',explain:'온조왕이 백제를 건국했어요.'},
  {level:1,era:'고려',question:'고려를 세운 사람은?',options:['왕건','궁예','견훤','최충헌'],answer:'왕건',year:'918년',explain:'왕건(태조)이 918년 고려를 건국했어요.'},
  {level:1,era:'고려',question:'팔만대장경을 만든 시대는?',options:['고려','조선','신라','고구려'],answer:'고려',year:'1236-1251년',explain:'몽골 침략을 물리치기 위해 고려에서 팔만대장경을 만들었어요.'},
  {level:2,era:'조선',question:'조선을 건국한 사람은?',options:['이성계','이순신','세종대왕','정도전'],answer:'이성계',year:'1392년',explain:'이성계(태조)가 1392년 조선을 건국했어요.'},
  {level:2,era:'조선',question:'한글을 창제한 왕은?',options:['세종대왕','태종','성종','연산군'],answer:'세종대왕',year:'1443년',explain:'세종대왕이 1443년 훈민정음(한글)을 창제했어요.'},
  {level:2,era:'조선',question:'임진왜란 때 활약한 장군은?',options:['이순신','강감찬','을지문덕','김유신'],answer:'이순신',year:'1592년',explain:'이순신 장군이 거북선으로 왜군을 물리쳤어요.'},
  {level:3,era:'근현대',question:'3·1운동이 일어난 해는?',options:['1919년','1945년','1910년','1920년'],answer:'1919년',year:'1919년 3월 1일',explain:'일제강점기에 독립을 외친 만세운동이에요.'},
  {level:3,era:'근현대',question:'광복절은 몇 월 며칠인가요?',options:['8월 15일','3월 1일','10월 3일','10월 9일'],answer:'8월 15일',year:'1945년',explain:'1945년 8월 15일 일본으로부터 광복을 되찾았어요.'},
  {level:3,era:'근현대',question:'한국전쟁이 시작된 해는?',options:['1950년','1945년','1953년','1948년'],answer:'1950년',year:'1950년 6월 25일',explain:'6·25전쟁이라고도 하며 1950년에 시작되었어요.'},
]

const level = ref(parseInt(localStorage.getItem('history_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const curQ = ref({options:[],answer:'',explain:'',era:'',question:''})
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(20)
const maxTime = ref(20)
let timer = null
let queue = []

function getPool() {
  const maxLv=level.value<=2?1:level.value<=4?2:3
  return historyDB.filter(q=>q.level<=maxLv)
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
  maxTime.value=level.value<=2?20:level.value<=4?15:12
  queue=shuffle(getPool()).slice(0,totalQ.value)
  phase.value='play'; nextQuestion()
}

function nextQuestion() {
  if(qIdx.value>=totalQ.value){endGame();return}
  const q=queue[qIdx.value]; qIdx.value++
  curQ.value={...q,options:shuffle([...q.options])}
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
  setTimeout(nextQuestion,2800)
}

function selectAnswer(opt) {
  if(answered.value) return
  clearInterval(timer); answered.value=true; picked.value=opt
  wasRight.value=opt===curQ.value.answer
  if(wasRight.value){ correct.value++; score.value+=10+timeLeft.value; speak('정답!') }
  else speak('오답! 정답은 ' + curQ.value.answer)
  setTimeout(nextQuestion,2800)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=8){ level.value++; localStorage.setItem('history_level',level.value); leveled.value=true; speak('레벨업!') }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.history-game { min-height:100vh; background:linear-gradient(135deg,#451a03,#78350f,#92400e); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fde68a; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fde68a; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fde68a; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.8); font-size:16px; }
.level-info { background:rgba(0,0,0,0.25); border-radius:12px; padding:12px 20px; color:#fde68a; font-size:14px; line-height:1.8; margin:12px auto; max-width:240px; text-align:left; }
.start-btn { background:#fde68a; color:#451a03; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:12px; color:rgba(255,255,255,0.7); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(255,255,255,0.2); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#fde68a; border-radius:4px; transition:width 0.3s; }
.era-badge { display:inline-block; background:rgba(253,230,138,0.2); color:#fde68a; font-size:12px; font-weight:700; padding:4px 12px; border-radius:12px; margin-bottom:10px; }
.question-card { background:rgba(255,255,255,0.1); border-radius:18px; padding:22px 20px; margin-bottom:16px; }
.q-text { color:#fff; font-size:20px; font-weight:700; line-height:1.5; }
.q-year { color:#fde68a; font-size:14px; margin-top:6px; font-weight:600; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.12); color:#fff; border:1px solid rgba(253,230,138,0.3); padding:14px 8px; border-radius:12px; font-size:15px; font-weight:600; cursor:pointer; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { background:rgba(253,230,138,0.2); border-color:#fde68a; }
.choice-btn.correct { background:rgba(16,185,129,0.3); border-color:#10b981; color:#a7f3d0; }
.choice-btn.wrong { background:rgba(239,68,68,0.25); border-color:#ef4444; color:#fca5a5; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { padding:12px 16px; border-radius:12px; }
.feedback.right { background:rgba(16,185,129,0.15); color:#a7f3d0; }
.feedback.wrong { background:rgba(239,68,68,0.15); color:#fca5a5; }
.explain { font-size:13px; font-weight:400; margin-top:4px; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:52px; font-weight:900; color:#fde68a; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#fde68a; color:#451a03; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#451a03; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#92400e; color:#fff; }
</style>
"""

# Write files
print("=== 게임 21: 한국어 맞춤법 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameSpelling.vue', game21)

print("=== 게임 22: 스피드 계산 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameSpeedCalc.vue', game22)

print("=== 게임 23: 코딩 퀴즈 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameCodingQuiz.vue', game23)

print("=== 게임 24: 한국 역사 퀴즈 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameHistory.vue', game24)

# Update router
print("\n=== 라우터 업데이트 ===")
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
new_routes = """  { path: '/games/spelling', component: () => import('../pages/games/GameSpelling.vue'), name: 'game-spelling' },
  { path: '/games/speed-calc', component: () => import('../pages/games/GameSpeedCalc.vue'), name: 'game-speed-calc' },
  { path: '/games/coding-quiz', component: () => import('../pages/games/GameCodingQuiz.vue'), name: 'game-coding-quiz' },
  { path: '/games/history', component: () => import('../pages/games/GameHistory.vue'), name: 'game-history' },"""

if 'game-spelling' not in router_content:
    updated = router_content.replace(
        "  { path: '/games/stock'",
        new_routes + "\n  { path: '/games/stock'"
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', updated)
    print("Router updated")
else:
    print("Routes already exist")

# Update DB
print("\n=== DB 업데이트 ===")
updates = [
    ("맞춤법", "game-spelling"),
    ("스피드", "game-speed-calc"),
    ("코딩", "game-coding-quiz"),
    ("역사", "game-history"),
]
for name, route in updates:
    r = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"UPDATE games SET route_name='{route}' WHERE name LIKE '%{name}%';\"")
    print(f"{name} -> {route}: {r or 'OK'}")

# Build
print("\n=== npm 빌드 ===")
build_result = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -8", timeout=300)
print(build_result)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

print("\n✅ 게임 21-24 (청소년 완성) 배포 완료!")
c.close()
