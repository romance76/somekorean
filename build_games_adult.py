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

# ===== 성인 게임 A: 속담 퀴즈 =====
game_proverb = r"""<template>
  <div class="proverb-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 📜</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">📜</div>
      <h1 class="title">속담 퀴즈</h1>
      <p class="subtitle">우리나라 속담을 맞춰보세요!</p>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 🎯</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span :style="{color:timeLeft<6?'#ef4444':'#fbbf24'}">{{ timeLeft }}초</span>
      </div>
      <div class="proverb-card">
        <div class="proverb-text">{{ curQ.proverb }}</div>
      </div>
      <div class="q-ask">이 속담의 뜻은?</div>
      <div class="choices-col">
        <button v-for="opt in curQ.options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===curQ.meaning, wrong: answered && opt===picked && opt!==curQ.meaning, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          {{ opt }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        <div>{{ wasRight ? '정답! 🎉' : '오답!' }}</div>
        <div class="explain">{{ curQ.meaning }}</div>
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

const proverbs = [
  {proverb:'가는 말이 고와야 오는 말이 곱다',meaning:'내가 먼저 잘 대해야 상대도 잘 대한다',level:1},
  {proverb:'공든 탑이 무너지랴',meaning:'정성껏 쌓은 것은 쉽게 무너지지 않는다',level:1},
  {proverb:'구슬이 서 말이라도 꿰어야 보배',meaning:'아무리 좋은 것도 활용해야 가치가 있다',level:1},
  {proverb:'낮말은 새가 듣고 밤말은 쥐가 듣는다',meaning:'항상 말을 조심해야 한다',level:1},
  {proverb:'세 살 버릇 여든까지 간다',meaning:'어릴 때 형성된 습관은 오래 지속된다',level:1},
  {proverb:'티끌 모아 태산',meaning:'작은 것도 모이면 크게 된다',level:1},
  {proverb:'하늘이 무너져도 솟아날 구멍이 있다',meaning:'아무리 어려운 상황에도 해결책이 있다',level:1},
  {proverb:'원숭이도 나무에서 떨어진다',meaning:'아무리 능숙한 사람도 실수할 때가 있다',level:2},
  {proverb:'우물 안 개구리',meaning:'세상을 좁게만 알고 식견이 없는 사람',level:2},
  {proverb:'백지장도 맞들면 낫다',meaning:'아무리 쉬운 일도 협력하면 더 잘 된다',level:2},
  {proverb:'빈 수레가 요란하다',meaning:'실속이 없는 사람이 더 떠들어댄다',level:2},
  {proverb:'소 잃고 외양간 고친다',meaning:'일이 다 잘못된 뒤에야 대책을 세운다',level:2},
  {proverb:'식은 죽 먹기',meaning:'매우 쉬운 일',level:2},
  {proverb:'아니 땐 굴뚝에 연기 날까',meaning:'원인 없는 결과는 없다',level:3},
  {proverb:'윗물이 맑아야 아랫물이 맑다',meaning:'위에 있는 사람이 잘해야 아랫사람도 잘 된다',level:3},
  {proverb:'호랑이 없는 곳에서 여우가 왕 노릇',meaning:'실력 있는 사람이 없을 때 그보다 못한 사람이 으스댄다',level:3},
]

const level = ref(parseInt(localStorage.getItem('proverb_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const curQ = ref({proverb:'',meaning:'',options:[]})
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(20)
const maxTime = ref(20)
let timer = null
let queue = []

function getPool() {
  const maxLv=level.value<=2?1:level.value<=4?2:3
  return proverbs.filter(p=>p.level<=maxLv)
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
  const pool=getPool()
  queue=shuffle(pool).slice(0,totalQ.value)
  phase.value='play'; nextQuestion()
}

function nextQuestion() {
  if(qIdx.value>=totalQ.value){endGame();return}
  const q=queue[qIdx.value]; qIdx.value++
  const pool=getPool()
  const wrongs=shuffle(pool.filter(p=>p.meaning!==q.meaning)).slice(0,3).map(p=>p.meaning)
  curQ.value={...q, options:shuffle([q.meaning,...wrongs])}
  answered.value=false; wasRight.value=false; picked.value=''
  speak(q.proverb)
  startTimer()
}

function startTimer() {
  clearInterval(timer); timeLeft.value=maxTime.value
  timer=setInterval(()=>{ timeLeft.value--; if(timeLeft.value<=0){clearInterval(timer);timeOut()} },1000)
}

function timeOut() {
  answered.value=true; wasRight.value=false
  speak('시간 초과! 정답은 ' + curQ.value.meaning)
  setTimeout(nextQuestion,2800)
}

function selectAnswer(opt) {
  if(answered.value) return
  clearInterval(timer); answered.value=true; picked.value=opt
  wasRight.value=opt===curQ.value.meaning
  if(wasRight.value){ correct.value++; score.value+=10+timeLeft.value; speak('정답!') }
  else speak('오답!')
  setTimeout(nextQuestion,2800)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=8){ level.value++; localStorage.setItem('proverb_level',level.value); leveled.value=true; speak('레벨업!') }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.proverb-game { min-height:100vh; background:linear-gradient(135deg,#14532d,#166534,#15803d); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.85); font-size:16px; }
.level-info { color:#bbf7d0; margin:10px 0; font-size:15px; }
.start-btn { background:#fbbf24; color:#14532d; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:500px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; color:rgba(255,255,255,0.7); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(255,255,255,0.2); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#fbbf24; border-radius:4px; transition:width 0.3s; }
.proverb-card { background:rgba(0,0,0,0.25); border-radius:18px; padding:28px 20px; text-align:center; margin-bottom:14px; border:1px solid rgba(251,191,36,0.3); }
.proverb-text { color:#fde68a; font-size:20px; font-weight:700; line-height:1.6; }
.q-ask { color:rgba(255,255,255,0.7); font-size:14px; text-align:center; margin-bottom:12px; }
.choices-col { display:flex; flex-direction:column; gap:8px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#14532d; border:none; padding:14px 16px; border-radius:12px; font-size:15px; font-weight:600; cursor:pointer; text-align:left; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { background:#fff; transform:translateX(4px); }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { padding:14px 16px; border-radius:12px; }
.feedback.right { background:rgba(16,185,129,0.2); color:#a7f3d0; }
.feedback.wrong { background:rgba(239,68,68,0.2); color:#fca5a5; }
.explain { font-size:14px; font-weight:400; margin-top:6px; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:52px; font-weight:900; color:#fde68a; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#fbbf24; color:#14532d; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#14532d; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#15803d; color:#fff; }
</style>
"""

# ===== 성인 게임 B: 한자 퀴즈 =====
game_hanja = r"""<template>
  <div class="hanja-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 漢</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">漢</div>
      <h1 class="title">한자 퀴즈</h1>
      <p class="subtitle">한자의 음과 뜻을 맞춰보세요!</p>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 📖</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span :style="{color:timeLeft<6?'#ef4444':'#fbbf24'}">{{ timeLeft }}초</span>
      </div>
      <div class="hanja-card">
        <div class="hanja-char">{{ curQ.hanja }}</div>
        <div class="ask-type">{{ askType === 'reading' ? '이 한자의 음(소리)는?' : '이 한자의 뜻은?' }}</div>
      </div>
      <div class="choices-grid">
        <button v-for="opt in options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===correctAnswer, wrong: answered && opt===picked && opt!==correctAnswer, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          {{ opt }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '정답! 🎉' : '정답: ' + curQ.reading + ' (' + curQ.meaning + ')' }}
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
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const hanjaDB = [
  {hanja:'山',reading:'산',meaning:'산',level:1},
  {hanja:'水',reading:'수',meaning:'물',level:1},
  {hanja:'火',reading:'화',meaning:'불',level:1},
  {hanja:'木',reading:'목',meaning:'나무',level:1},
  {hanja:'金',reading:'금',meaning:'금/쇠',level:1},
  {hanja:'土',reading:'토',meaning:'흙',level:1},
  {hanja:'日',reading:'일',meaning:'날/해',level:1},
  {hanja:'月',reading:'월',meaning:'달/월',level:1},
  {hanja:'人',reading:'인',meaning:'사람',level:1},
  {hanja:'大',reading:'대',meaning:'크다',level:1},
  {hanja:'小',reading:'소',meaning:'작다',level:2},
  {hanja:'上',reading:'상',meaning:'위',level:2},
  {hanja:'下',reading:'하',meaning:'아래',level:2},
  {hanja:'東',reading:'동',meaning:'동쪽',level:2},
  {hanja:'西',reading:'서',meaning:'서쪽',level:2},
  {hanja:'南',reading:'남',meaning:'남쪽',level:2},
  {hanja:'北',reading:'북',meaning:'북쪽',level:2},
  {hanja:'中',reading:'중',meaning:'가운데',level:2},
  {hanja:'心',reading:'심',meaning:'마음',level:3},
  {hanja:'力',reading:'력',meaning:'힘',level:3},
  {hanja:'王',reading:'왕',meaning:'임금',level:3},
  {hanja:'國',reading:'국',meaning:'나라',level:3},
  {hanja:'學',reading:'학',meaning:'배우다',level:3},
  {hanja:'語',reading:'어',meaning:'말/언어',level:3},
]

const level = ref(parseInt(localStorage.getItem('hanja_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const correctAnswer = ref('')
const curQ = ref({hanja:'',reading:'',meaning:'',level:1})
const options = ref([])
const askType = ref('reading')
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(15)
const maxTime = ref(15)
let timer = null
let queue = []

function getPool() {
  const maxLv=level.value<=2?1:level.value<=4?2:3
  return hanjaDB.filter(h=>h.level<=maxLv)
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
  const pool=getPool()
  queue=shuffle(pool).slice(0,totalQ.value)
  phase.value='play'; nextQuestion()
}

function nextQuestion() {
  if(qIdx.value>=totalQ.value){endGame();return}
  const q=queue[qIdx.value]; qIdx.value++
  curQ.value=q; answered.value=false; wasRight.value=false; picked.value=''
  askType.value=Math.random()>0.5?'reading':'meaning'
  correctAnswer.value=askType.value==='reading'?q.reading:q.meaning
  const pool=getPool()
  const wrongField=askType.value==='reading'?'reading':'meaning'
  const wrongs=shuffle(pool.filter(h=>h.hanja!==q.hanja)).slice(0,3).map(h=>h[wrongField])
  options.value=shuffle([correctAnswer.value,...wrongs])
  speak(q.hanja)
  startTimer()
}

function startTimer() {
  clearInterval(timer); timeLeft.value=maxTime.value
  timer=setInterval(()=>{ timeLeft.value--; if(timeLeft.value<=0){clearInterval(timer);timeOut()} },1000)
}

function timeOut() {
  answered.value=true; wasRight.value=false
  speak('정답은 ' + correctAnswer.value)
  setTimeout(nextQuestion,2000)
}

function selectAnswer(opt) {
  if(answered.value) return
  clearInterval(timer); answered.value=true; picked.value=opt
  wasRight.value=opt===correctAnswer.value
  if(wasRight.value){ correct.value++; score.value+=10+timeLeft.value; speak('정답!') }
  else speak('오답. 정답은 ' + correctAnswer.value)
  setTimeout(nextQuestion,2000)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=8){ level.value++; localStorage.setItem('hanja_level',level.value); leveled.value=true; speak('레벨업!') }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.hanja-game { min-height:100vh; background:linear-gradient(135deg,#1e0533,#3b0764,#581c87); padding:16px; font-family:'Noto Sans KR',serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#e9d5ff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#e9d5ff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#e9d5ff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.8); font-size:16px; }
.level-info { color:#ddd6fe; margin:10px 0; font-size:15px; }
.start-btn { background:#a855f7; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:400px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; color:rgba(255,255,255,0.6); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(255,255,255,0.15); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#a855f7; border-radius:4px; transition:width 0.3s; }
.hanja-card { background:rgba(255,255,255,0.08); border-radius:20px; padding:30px 20px; text-align:center; margin-bottom:20px; border:1px solid rgba(168,85,247,0.4); }
.hanja-char { font-size:96px; color:#fff; line-height:1; margin-bottom:12px; }
.ask-type { color:#d8b4fe; font-size:16px; font-weight:600; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.12); color:#e9d5ff; border:1px solid rgba(168,85,247,0.3); padding:16px; border-radius:12px; font-size:20px; font-weight:700; cursor:pointer; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { background:rgba(168,85,247,0.25); border-color:#a855f7; }
.choice-btn.correct { background:rgba(16,185,129,0.3); border-color:#10b981; color:#a7f3d0; }
.choice-btn.wrong { background:rgba(239,68,68,0.25); border-color:#ef4444; color:#fca5a5; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { text-align:center; padding:12px; border-radius:12px; font-size:16px; font-weight:700; }
.feedback.right { background:rgba(16,185,129,0.2); color:#a7f3d0; }
.feedback.wrong { background:rgba(239,68,68,0.2); color:#fca5a5; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:52px; font-weight:900; color:#e9d5ff; }
.res-detail { color:rgba(255,255,255,0.7); font-size:16px; margin:8px 0; }
.levelup { background:#a855f7; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#3b0764; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#7c3aed; color:#fff; }
</style>
"""

# ===== 시니어 게임 A: 건강 상식 퀴즈 =====
game_health = r"""<template>
  <div class="health-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🏥</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🏥</div>
      <h1 class="title">건강 상식 퀴즈</h1>
      <p class="subtitle">건강한 생활을 위한 상식을 알아봐요!</p>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 💊</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span :style="{color:timeLeft<8?'#ef4444':'#6ee7b7'}">{{ timeLeft }}초</span>
      </div>
      <div class="question-card">
        <div class="q-emoji">{{ curQ.emoji }}</div>
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
      <div style="font-size:80px">🌟</div>
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

const healthQuiz = [
  {emoji:'🚶',question:'하루 권장 걷기 목표는 몇 보인가요?',options:['5,000보','10,000보','3,000보','20,000보'],answer:'10,000보',explain:'하루 만 보 걷기가 건강에 도움이 돼요.',level:1},
  {emoji:'💧',question:'하루 물 권장 섭취량은?',options:['1리터','2리터','500ml','3리터'],answer:'2리터',explain:'성인은 하루 약 2리터(8잔)의 물을 마시는 게 좋아요.',level:1},
  {emoji:'🛌',question:'성인의 적정 수면 시간은?',options:['4-5시간','6-8시간','10-12시간','3-4시간'],answer:'6-8시간',explain:'성인은 하루 6~8시간 수면이 건강에 좋아요.',level:1},
  {emoji:'🧂',question:'고혈압 예방을 위해 줄여야 할 것은?',options:['나트륨(소금)','칼슘','단백질','비타민C'],answer:'나트륨(소금)',explain:'소금을 줄이면 혈압 조절에 도움이 돼요.',level:1},
  {emoji:'☀️',question:'비타민 D는 주로 어떻게 얻나요?',options:['햇빛','음식','수면','운동'],answer:'햇빛',explain:'햇볕을 쬐면 피부에서 비타민 D가 생성돼요.',level:1},
  {emoji:'🩺',question:'당뇨 예방에 가장 효과적인 것은?',options:['규칙적 운동과 식이조절','비타민 복용','충분한 수면만','약 복용'],answer:'규칙적 운동과 식이조절',explain:'적절한 운동과 균형 잡힌 식사가 당뇨 예방의 핵심이에요.',level:2},
  {emoji:'🧠',question:'치매 예방에 도움이 되는 활동은?',options:['독서와 두뇌 활동','장시간 TV 시청','과음','불규칙한 생활'],answer:'독서와 두뇌 활동',explain:'두뇌를 꾸준히 활동시키면 치매 예방에 도움이 돼요.',level:2},
  {emoji:'🦴',question:'골다공증 예방에 중요한 영양소는?',options:['칼슘과 비타민D','비타민C','철분','나트륨'],answer:'칼슘과 비타민D',explain:'칼슘과 비타민D는 뼈 건강에 필수적이에요.',level:2},
  {emoji:'❤️',question:'심장 건강에 나쁜 것은?',options:['흡연','규칙적 운동','과일 섭취','충분한 수면'],answer:'흡연',explain:'흡연은 심장 질환의 주요 위험 요인이에요.',level:2},
  {emoji:'🍎',question:'항산화 효과가 뛰어난 과일 색깔은?',options:['진한 빨강·파랑·보라','흰색','연한 노랑','갈색'],answer:'진한 빨강·파랑·보라',explain:'색이 진한 과채류일수록 항산화 성분이 풍부해요.',level:3},
]

const level = ref(parseInt(localStorage.getItem('health_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const curQ = ref({options:[],answer:'',explain:'',emoji:'',question:''})
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(25)
const maxTime = ref(25)
let timer = null
let queue = []

function getPool() {
  const maxLv=level.value<=2?1:level.value<=4?2:3
  return healthQuiz.filter(q=>q.level<=maxLv)
}

function speak(text) {
  if(!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang='ko-KR'; u.rate=0.8; u.pitch=1.0
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
  if(wasRight.value){ correct.value++; score.value+=10+timeLeft.value; speak('정답입니다!') }
  else speak('오답이에요. 정답은 ' + curQ.value.answer)
  setTimeout(nextQuestion,3000)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=7){ level.value++; localStorage.setItem('health_level',level.value); leveled.value=true; speak('레벨업!') }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(()=>clearInterval(timer))
</script>

<style scoped>
.health-game { min-height:100vh; background:linear-gradient(135deg,#ecfdf5,#d1fae5,#a7f3d0); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.7); color:#065f46; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; font-weight:600; }
.level-badge,.score { background:rgba(255,255,255,0.7); color:#065f46; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:34px; color:#065f46; font-weight:900; margin:10px 0; }
.subtitle { color:#047857; font-size:16px; }
.level-info { color:#059669; margin:10px 0; font-size:15px; }
.start-btn { background:#059669; color:#fff; border:none; padding:16px 44px; border-radius:30px; font-size:22px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:500px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; color:#047857; font-size:15px; }
.prog-bar { flex:1; height:10px; background:rgba(5,150,105,0.2); border-radius:5px; overflow:hidden; }
.prog-fill { height:100%; background:#059669; border-radius:5px; transition:width 0.3s; }
.question-card { background:#fff; border-radius:20px; padding:24px 20px; text-align:center; margin-bottom:16px; box-shadow:0 4px 20px rgba(0,0,0,0.08); }
.q-emoji { font-size:56px; margin-bottom:12px; }
.q-text { color:#1f2937; font-size:19px; font-weight:700; line-height:1.5; }
.choices-col { display:flex; flex-direction:column; gap:10px; margin-bottom:12px; }
.choice-btn { background:#fff; color:#1f2937; border:2px solid #d1fae5; padding:14px 16px; border-radius:12px; font-size:16px; font-weight:600; cursor:pointer; text-align:left; transition:all 0.2s; box-shadow:0 2px 8px rgba(0,0,0,0.05); }
.choice-btn:hover:not(.disabled) { border-color:#059669; transform:translateX(4px); }
.choice-btn.correct { background:#059669; color:#fff; border-color:#059669; }
.choice-btn.wrong { background:#ef4444; color:#fff; border-color:#ef4444; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { padding:14px 16px; border-radius:14px; box-shadow:0 2px 8px rgba(0,0,0,0.08); }
.feedback.right { background:#d1fae5; color:#065f46; }
.feedback.wrong { background:#fee2e2; color:#991b1b; }
.explain { font-size:14px; font-weight:400; margin-top:6px; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:52px; font-weight:900; color:#059669; }
.res-detail { color:#047857; font-size:16px; margin:8px 0; }
.levelup { background:#059669; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:#fff; color:#065f46; border:2px solid #059669; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#059669; color:#fff; border:none; }
</style>
"""

# Write files
print("=== 성인 게임: 속담 퀴즈 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameProverb.vue', game_proverb)

print("=== 성인 게임: 한자 퀴즈 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameHanja.vue', game_hanja)

print("=== 시니어 게임: 건강 상식 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameHealth.vue', game_health)

# Update router
print("\n=== 라우터 업데이트 ===")
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
new_routes = """  { path: '/games/proverb', component: () => import('../pages/games/GameProverb.vue'), name: 'game-proverb' },
  { path: '/games/hanja', component: () => import('../pages/games/GameHanja.vue'), name: 'game-hanja' },
  { path: '/games/health', component: () => import('../pages/games/GameHealth.vue'), name: 'game-health' },"""

if 'game-proverb' not in router_content:
    updated = router_content.replace(
        "  { path: '/games/spelling'",
        new_routes + "\n  { path: '/games/spelling'"
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', updated)
    print("Router updated")
else:
    print("Routes already exist")

# Update DB
print("\n=== DB 업데이트 ===")
updates = [
    ("속담", "game-proverb"),
    ("한자", "game-hanja"),
    ("건강", "game-health"),
]
for name, route in updates:
    r = ssh(f"mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"UPDATE games SET route_name='{route}' WHERE name LIKE '%{name}%';\"")
    print(f"{name} -> {route}: {r or 'OK'}")

# Check current DB routes
print("\n=== 현재 DB 라우트 현황 ===")
routes_status = ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SELECT id, name, route_name FROM games ORDER BY id LIMIT 30;\"")
print(routes_status)

# Build
print("\n=== npm 빌드 ===")
build_result = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -8", timeout=300)
print(build_result)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

print("\n✅ 성인/시니어 게임 배포 완료!")
c.close()
