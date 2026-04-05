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

# ===== GAME 17: 주식 시뮬레이션 =====
game17 = r"""<template>
  <div class="stock-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 📈</div>
      <div class="cash-badge">💰 {{ cash.toLocaleString() }}원</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">📈</div>
      <h1 class="title">주식 시뮬레이션</h1>
      <p class="subtitle">가상 주식을 사고 팔아서 돈을 불려봐요!</p>
      <div class="level-info">시작 자금: {{ startCash.toLocaleString() }}원 · {{ totalDays }}일 게임</div>
      <button class="start-btn" @click="startGame">투자 시작! 📊</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="day-bar">
        <span class="day-label">📅 {{ day }}일째 / {{ totalDays }}일</span>
        <div class="portfolio-value">
          총 자산: <strong :class="totalAsset >= startCash ? 'profit' : 'loss'">{{ totalAsset.toLocaleString() }}원</strong>
        </div>
      </div>
      <div class="stocks-list">
        <div v-for="stock in stocks" :key="stock.name" class="stock-card">
          <div class="stock-top">
            <span class="stock-icon">{{ stock.icon }}</span>
            <div class="stock-info">
              <div class="stock-name">{{ stock.name }}</div>
              <div class="stock-price" :class="stock.change >= 0 ? 'up' : 'down'">
                {{ stock.price.toLocaleString() }}원
                <span class="change-badge">{{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%</span>
              </div>
            </div>
            <div class="stock-chart">
              <svg width="60" height="30" viewBox="0 0 60 30">
                <polyline :points="chartPoints(stock)" fill="none"
                  :stroke="stock.change>=0?'#10b981':'#ef4444'" stroke-width="2"/>
              </svg>
            </div>
          </div>
          <div class="stock-holding" v-if="holding[stock.name]">
            보유: {{ holding[stock.name] }}주 ({{ (holding[stock.name]*stock.price).toLocaleString() }}원)
          </div>
          <div class="stock-actions">
            <button class="buy-btn" @click="buy(stock)" :disabled="cash < stock.price">매수</button>
            <button class="sell-btn" @click="sell(stock)" :disabled="!holding[stock.name]">매도</button>
          </div>
        </div>
      </div>
      <button class="next-day-btn" @click="nextDay">다음 날 ▶</button>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">{{ profit >= 0 ? '🤑' : '😭' }}</div>
      <div class="res-title">{{ totalDays }}일 투자 결과</div>
      <div class="res-amount" :class="profit>=0?'profit':'loss'">
        {{ profit >= 0 ? '+' : '' }}{{ profit.toLocaleString() }}원
      </div>
      <div class="res-rate" :class="profit>=0?'profit':'loss'">
        수익률: {{ profitRate }}%
      </div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 📊</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const level = ref(parseInt(localStorage.getItem('stock_level') || '1'))

const stockTemplates = [
  {name:'삼성전자',icon:'📱',basePrice:70000},
  {name:'카카오',icon:'💬',basePrice:45000},
  {name:'네이버',icon:'🔍',basePrice:180000},
  {name:'현대차',icon:'🚗',basePrice:220000},
  {name:'LG전자',icon:'📺',basePrice:95000},
]

const startCash = computed(() => level.value <= 2 ? 1000000 : level.value <= 4 ? 2000000 : 5000000)
const totalDays = computed(() => level.value <= 2 ? 10 : level.value <= 4 ? 15 : 20)

const phase = ref('start')
const cash = ref(1000000)
const stocks = ref([])
const holding = ref({})
const day = ref(1)
const leveled = ref(false)

const totalAsset = computed(() => {
  let total = cash.value
  for (const stock of stocks.value) {
    total += (holding.value[stock.name] || 0) * stock.price
  }
  return total
})

const profit = computed(() => totalAsset.value - startCash.value)
const profitRate = computed(() => Math.round(profit.value / startCash.value * 100))

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9
  window.speechSynthesis.speak(u)
}

function initStocks() {
  const count = level.value <= 2 ? 3 : 5
  return stockTemplates.slice(0, count).map(t => ({
    ...t,
    price: t.basePrice,
    change: 0,
    history: [t.basePrice],
  }))
}

function startGame() {
  cash.value = startCash.value
  stocks.value = initStocks()
  holding.value = {}
  day.value = 1
  leveled.value = false
  phase.value = 'play'
  speak('주식 투자를 시작합니다!')
}

function nextDay() {
  if (day.value >= totalDays.value) { endGame(); return }
  day.value++
  stocks.value = stocks.value.map(s => {
    const changePercent = (Math.random() * 14 - 5)
    const newPrice = Math.max(1000, Math.round(s.price * (1 + changePercent / 100)))
    const history = [...s.history, newPrice].slice(-10)
    return { ...s, price: newPrice, change: Math.round(changePercent * 10) / 10, history }
  })
  const news = stocks.value[Math.floor(Math.random()*stocks.value.length)]
  if (news.change > 3) speak(news.name + ' 주가 상승!')
  else if (news.change < -3) speak(news.name + ' 주가 하락!')
}

function buy(stock) {
  if (cash.value < stock.price) return
  cash.value -= stock.price
  holding.value[stock.name] = (holding.value[stock.name] || 0) + 1
  speak(stock.name + ' 매수')
}

function sell(stock) {
  if (!holding.value[stock.name]) return
  cash.value += stock.price
  holding.value[stock.name]--
  if (!holding.value[stock.name]) delete holding.value[stock.name]
  speak(stock.name + ' 매도')
}

function chartPoints(stock) {
  const h = stock.history
  if (h.length < 2) return '0,15 60,15'
  const min = Math.min(...h), max = Math.max(...h)
  const range = max - min || 1
  return h.map((v, i) => {
    const x = i / (h.length - 1) * 60
    const y = 28 - (v - min) / range * 26
    return x + ',' + y
  }).join(' ')
}

function endGame() {
  // sell all
  for (const stock of stocks.value) {
    if (holding.value[stock.name]) {
      cash.value += holding.value[stock.name] * stock.price
      delete holding.value[stock.name]
    }
  }
  phase.value = 'result'
  if (profitRate.value >= (level.value <= 2 ? 5 : level.value <= 4 ? 10 : 15)) {
    level.value++
    localStorage.setItem('stock_level', level.value)
    leveled.value = true
    speak('레벨업! 투자 실력이 늘었어요!')
  } else {
    speak('게임 종료! 수익률 ' + profitRate.value + '퍼센트')
  }
}

function goBack() { router.push('/games') }
</script>

<style scoped>
.stock-game { min-height:100vh; background:linear-gradient(135deg,#0f172a,#1e293b); padding:16px; font-family:'Noto Sans KR',sans-serif; color:#fff; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,0.1); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.cash-badge { background:rgba(255,255,255,0.1); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:13px; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.7); font-size:16px; }
.level-info { color:#60a5fa; margin:12px 0; font-size:15px; }
.start-btn { background:#10b981; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:480px; margin:0 auto; }
.day-bar { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding:10px 14px; background:rgba(255,255,255,0.07); border-radius:12px; }
.day-label { font-size:14px; color:rgba(255,255,255,0.7); }
.portfolio-value { font-size:14px; }
.portfolio-value strong { font-size:16px; }
.profit { color:#10b981; }
.loss { color:#ef4444; }
.stocks-list { display:flex; flex-direction:column; gap:10px; margin-bottom:16px; }
.stock-card { background:rgba(255,255,255,0.08); border-radius:14px; padding:14px; }
.stock-top { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.stock-icon { font-size:28px; }
.stock-info { flex:1; }
.stock-name { font-size:15px; font-weight:700; }
.stock-price { font-size:16px; font-weight:700; display:flex; align-items:center; gap:6px; }
.stock-price.up { color:#10b981; }
.stock-price.down { color:#ef4444; }
.change-badge { font-size:12px; font-weight:600; }
.stock-holding { font-size:12px; color:rgba(255,255,255,0.6); margin-bottom:8px; }
.stock-actions { display:flex; gap:8px; }
.buy-btn,.sell-btn { flex:1; padding:8px; border:none; border-radius:8px; font-size:14px; font-weight:700; cursor:pointer; }
.buy-btn { background:#10b981; color:#fff; }
.buy-btn:disabled { background:#374151; color:#6b7280; cursor:not-allowed; }
.sell-btn { background:#ef4444; color:#fff; }
.sell-btn:disabled { background:#374151; color:#6b7280; cursor:not-allowed; }
.next-day-btn { width:100%; padding:14px; background:#3b82f6; color:#fff; border:none; border-radius:12px; font-size:17px; font-weight:700; cursor:pointer; }
.result-box { text-align:center; padding:40px 20px; }
.res-title { font-size:22px; font-weight:700; margin:10px 0; }
.res-amount { font-size:48px; font-weight:900; }
.res-rate { font-size:22px; font-weight:700; margin:8px 0; }
.levelup { background:#10b981; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#0f172a; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#3b82f6; color:#fff; }
</style>
"""

# ===== GAME 18: SAT 단어 퀴즈 =====
game18 = r"""<template>
  <div class="sat-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 📚</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">📚</div>
      <h1 class="title">SAT 영단어</h1>
      <p class="subtitle">대학 수준 영어 단어를 정복해요!</p>
      <div class="level-info">
        <div>레벨 1-2: 기초 수준</div>
        <div>레벨 3-4: 중급 수준</div>
        <div>레벨 5+: SAT 고급</div>
      </div>
      <button class="start-btn" @click="startGame">시작! 📖</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span>{{ qIdx }}/{{ totalQ }}</span>
      </div>
      <div class="timer-row">
        <div class="timer-bar">
          <div class="timer-fill" :style="{width:(timeLeft/maxTime*100)+'%', background:timeLeft<5?'#ef4444':'#6366f1'}"></div>
        </div>
        <span class="timer-num">{{ timeLeft }}</span>
      </div>
      <div class="word-card">
        <div class="word-eng">{{ curQ.word }}</div>
        <div class="word-phonetic">{{ curQ.phonetic }}</div>
        <div class="word-pos">{{ curQ.pos }}</div>
        <button class="listen-btn" @click="listenWord">🔊</button>
      </div>
      <div class="choices-col">
        <button v-for="opt in options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===curQ.kor, wrong: answered && opt===picked && opt!==curQ.kor, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          {{ opt }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '정답! 🎉' : '정답: ' + curQ.kor }}
        <div class="example" v-if="curQ.example">예문: {{ curQ.example }}</div>
      </div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">🎓</div>
      <div class="res-score">{{ score }}점</div>
      <div class="res-detail">{{ correct }}/{{ totalQ }} 정답</div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 📖</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const wordBank = [
  // Level 1 (basic)
  {word:'Abundant',phonetic:'어번던트',pos:'형용사',kor:'풍부한',example:'Food is abundant here.',level:1},
  {word:'Benevolent',phonetic:'베네볼런트',pos:'형용사',kor:'자비로운',example:'She is a benevolent person.',level:1},
  {word:'Candid',phonetic:'캔디드',pos:'형용사',kor:'솔직한',example:'He gave a candid answer.',level:1},
  {word:'Diligent',phonetic:'딜리전트',pos:'형용사',kor:'부지런한',example:'She is a diligent student.',level:1},
  {word:'Eloquent',phonetic:'엘로퀀트',pos:'형용사',kor:'웅변적인',example:'He gave an eloquent speech.',level:1},
  {word:'Frugal',phonetic:'프루걸',pos:'형용사',kor:'검소한',example:'She lives a frugal life.',level:1},
  {word:'Generous',phonetic:'제너러스',pos:'형용사',kor:'관대한',example:'He is very generous.',level:1},
  {word:'Humble',phonetic:'험블',pos:'형용사',kor:'겸손한',example:'Stay humble.',level:1},
  // Level 2
  {word:'Ambiguous',phonetic:'앰비귀어스',pos:'형용사',kor:'모호한',example:'The instructions were ambiguous.',level:2},
  {word:'Brevity',phonetic:'브레비티',pos:'명사',kor:'간결함',example:'Brevity is the soul of wit.',level:2},
  {word:'Concise',phonetic:'컨사이스',pos:'형용사',kor:'간결한',example:'Write in a concise manner.',level:2},
  {word:'Deduce',phonetic:'디듀스',pos:'동사',kor:'추론하다',example:'She deduced the answer.',level:2},
  {word:'Empirical',phonetic:'엠피리컬',pos:'형용사',kor:'경험적인',example:'Empirical evidence is needed.',level:2},
  {word:'Feasible',phonetic:'피저블',pos:'형용사',kor:'실현가능한',example:'Is this plan feasible?',level:2},
  {word:'Inherent',phonetic:'인히런트',pos:'형용사',kor:'내재적인',example:'There are inherent risks.',level:2},
  {word:'Juxtapose',phonetic:'저스타포즈',pos:'동사',kor:'나란히 놓다',example:'Juxtapose the two images.',level:2},
  // Level 3 (SAT)
  {word:'Ameliorate',phonetic:'어밀리어레이트',pos:'동사',kor:'개선하다',example:'We must ameliorate conditions.',level:3},
  {word:'Capricious',phonetic:'커프리셔스',pos:'형용사',kor:'변덕스러운',example:'She is capricious.',level:3},
  {word:'Disparate',phonetic:'디스퍼릿',pos:'형용사',kor:'이질적인',example:'These are disparate ideas.',level:3},
  {word:'Ephemeral',phonetic:'이페머럴',pos:'형용사',kor:'일시적인',example:'Fame is ephemeral.',level:3},
  {word:'Fastidious',phonetic:'패스티디어스',pos:'형용사',kor:'까다로운',example:'He is fastidious about details.',level:3},
  {word:'Gregarious',phonetic:'그레게리어스',pos:'형용사',kor:'사교적인',example:'She is very gregarious.',level:3},
  {word:'Laconic',phonetic:'러코닉',pos:'형용사',kor:'간결한 말투의',example:'His reply was laconic.',level:3},
  {word:'Mendacious',phonetic:'멘데이셔스',pos:'형용사',kor:'거짓말하는',example:'He is mendacious.',level:3},
]

const level = ref(parseInt(localStorage.getItem('sat_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const curQ = ref({word:'',kor:'',phonetic:'',pos:'',example:'',level:1})
const options = ref([])
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(20)
const maxTime = ref(20)
let timer = null
let queue = []

function getPool() {
  const maxLv = level.value <= 2 ? 1 : level.value <= 4 ? 2 : 3
  return wordBank.filter(w => w.level <= maxLv)
}

function speak(text, lang = 'ko-KR') {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = lang; u.rate = 0.75; u.pitch = 1.0
  window.speechSynthesis.speak(u)
}

function listenWord() {
  speak(curQ.value.word, 'en-US')
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function startGame() {
  score.value = 0; correct.value = 0; leveled.value = false; qIdx.value = 0
  maxTime.value = level.value <= 2 ? 20 : level.value <= 4 ? 15 : 10
  queue = shuffle(getPool()).slice(0, totalQ.value)
  phase.value = 'play'
  nextQuestion()
}

function nextQuestion() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  const q = queue[qIdx.value]; qIdx.value++
  curQ.value = q; answered.value = false; wasRight.value = false; picked.value = ''
  const pool = getPool()
  const wrongs = shuffle(pool.filter(w => w.kor !== q.kor)).slice(0, 3).map(w => w.kor)
  options.value = shuffle([q.kor, ...wrongs])
  speak(q.word, 'en-US')
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
  speak('정답은 ' + curQ.value.kor)
  setTimeout(nextQuestion, 2500)
}

function selectAnswer(opt) {
  if (answered.value) return
  clearInterval(timer)
  answered.value = true; picked.value = opt
  wasRight.value = opt === curQ.value.kor
  if (wasRight.value) {
    correct.value++
    score.value += 10 + timeLeft.value
    speak('정답!')
  } else {
    speak('정답은 ' + curQ.value.kor)
  }
  setTimeout(nextQuestion, 2500)
}

function endGame() {
  clearInterval(timer)
  phase.value = 'result'
  if (correct.value >= 8) {
    level.value++
    localStorage.setItem('sat_level', level.value)
    leveled.value = true
    speak('레벨업!')
  }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.sat-game { min-height:100vh; background:linear-gradient(135deg,#1e1b4b,#312e81,#4338ca); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.8); font-size:16px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#c7d2fe; font-size:14px; line-height:1.8; margin:12px auto; max-width:240px; text-align:left; }
.start-btn { background:#6366f1; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:8px; color:rgba(255,255,255,0.7); font-size:13px; }
.prog-bar { flex:1; height:6px; background:rgba(255,255,255,0.2); border-radius:3px; overflow:hidden; }
.prog-fill { height:100%; background:#6366f1; border-radius:3px; transition:width 0.3s; }
.timer-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.timer-bar { flex:1; height:10px; background:rgba(255,255,255,0.2); border-radius:5px; overflow:hidden; }
.timer-fill { height:100%; border-radius:5px; transition:width 1s linear; }
.timer-num { color:#fff; font-weight:700; font-size:18px; min-width:28px; text-align:right; }
.word-card { background:rgba(255,255,255,0.12); border-radius:20px; padding:28px 20px; text-align:center; margin-bottom:16px; }
.word-eng { font-size:38px; font-weight:900; color:#fff; letter-spacing:1px; }
.word-phonetic { color:#a5b4fc; font-size:16px; margin:4px 0; }
.word-pos { color:#818cf8; font-size:13px; background:rgba(99,102,241,0.3); display:inline-block; padding:2px 10px; border-radius:10px; margin:4px 0; }
.listen-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 16px; border-radius:20px; cursor:pointer; font-size:16px; margin-top:8px; }
.choices-col { display:flex; flex-direction:column; gap:8px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#1e1b4b; border:none; padding:14px 20px; border-radius:12px; font-size:16px; font-weight:700; cursor:pointer; text-align:left; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { background:#fff; transform:translateX(4px); }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { padding:12px 16px; border-radius:12px; font-size:15px; font-weight:700; }
.feedback.right { background:rgba(16,185,129,0.2); color:#a7f3d0; }
.feedback.wrong { background:rgba(239,68,68,0.2); color:#fca5a5; }
.example { font-size:13px; font-weight:400; font-style:italic; margin-top:6px; opacity:0.85; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#a5b4fc; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#6366f1; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#1e1b4b; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#4338ca; color:#fff; }
</style>
"""

# ===== GAME 19: 수학 챌린지 =====
game19 = r"""<template>
  <div class="mathchallenge-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🧮</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🧮</div>
      <h1 class="title">수학 챌린지</h1>
      <p class="subtitle">빠르게 계산해서 정답을 맞춰요!</p>
      <div class="level-info">
        <div>레벨 1-2: 사칙연산</div>
        <div>레벨 3-4: 괄호·분수</div>
        <div>레벨 5+: 방정식·제곱</div>
      </div>
      <button class="start-btn" @click="startGame">도전! 🚀</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="top-row">
        <div class="combo-badge" v-if="combo > 1">🔥 {{ combo }}콤보</div>
        <div class="timer-circle">
          <svg width="60" height="60" viewBox="0 0 60 60">
            <circle cx="30" cy="30" r="26" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="5"/>
            <circle cx="30" cy="30" r="26" fill="none" :stroke="timeLeft < 4 ? '#ef4444' : '#6366f1'" stroke-width="5"
              stroke-dasharray="163" :stroke-dashoffset="163*(1-timeLeft/maxTime)" stroke-linecap="round"
              transform="rotate(-90 30 30)"/>
          </svg>
          <span class="timer-text">{{ timeLeft }}</span>
        </div>
        <div class="qcount">{{ qIdx }}/{{ totalQ }}</div>
      </div>
      <div class="equation-card" :class="{shake: shaking}">
        <div class="equation-text">{{ equation }}</div>
        <div class="equation-sub" v-if="subHint">({{ subHint }})</div>
      </div>
      <div class="choices-grid">
        <button v-for="opt in options" :key="opt" class="choice-btn"
          :class="{correct: answered && opt===correctAns, wrong: answered && opt===picked && opt!==correctAns, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          {{ opt }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '정답! 🎉' : '정답: ' + correctAns }}
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

const level = ref(parseInt(localStorage.getItem('mathchallenge_level') || '1'))
const score = ref(0)
const correct = ref(0)
const combo = ref(0)
const maxCombo = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref(null)
const correctAns = ref(0)
const equation = ref('')
const subHint = ref('')
const options = ref([])
const shaking = ref(false)
const qIdx = ref(0)
const totalQ = ref(12)
const timeLeft = ref(15)
const maxTime = ref(15)
let timer = null

function getMaxTime() { return level.value <= 2 ? 15 : level.value <= 4 ? 10 : 7 }

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }
function rand(a, b) { return Math.floor(Math.random()*(b-a+1))+a }

function generateQuestion() {
  subHint.value = ''
  if (level.value <= 2) {
    const ops = ['+','-','×','÷']
    const op = ops[rand(0,3)]
    let a,b,ans
    if (op==='+') { a=rand(10,99); b=rand(10,99); ans=a+b; equation.value=`${a} + ${b} = ?` }
    else if (op==='-') { a=rand(20,99); b=rand(1,a); ans=a-b; equation.value=`${a} - ${b} = ?` }
    else if (op==='×') { a=rand(2,12); b=rand(2,12); ans=a*b; equation.value=`${a} × ${b} = ?` }
    else { a=rand(2,9); b=rand(2,9); ans=a*b; equation.value=`${ans} ÷ ${a} = ?`; const t=ans; ans=b; }
    return ans
  } else if (level.value <= 4) {
    const type = rand(1,3)
    if (type===1) {
      const a=rand(2,9),b=rand(2,9),c=rand(1,10)
      const ans=(a+b)*c; equation.value=`(${a} + ${b}) × ${c} = ?`
      return ans
    } else if (type===2) {
      const a=rand(2,9),b=rand(2,9),c=rand(2,5)
      const ans=a*b+c; equation.value=`${a} × ${b} + ${c} = ?`
      return ans
    } else {
      const a=rand(1,5),b=rand(1,5)
      const num=a*rand(1,3), den=b
      const ans=num+a; equation.value=`${num}/${den} + ${a} = ?`
      subHint.value='분수를 정수로 변환'
      return ans
    }
  } else {
    const type = rand(1,3)
    if (type===1) {
      const a=rand(2,10); const ans=a*a; equation.value=`${a}² = ?`
      return ans
    } else if (type===2) {
      const ans=rand(1,9); equation.value=`x + ${ans+3} = ${ans*2+3}, x = ?`
      return ans
    } else {
      const a=rand(2,8),b=rand(1,5)
      const ans=a*a-b; equation.value=`${a}² - ${b} = ?`
      return ans
    }
  }
}

function startGame() {
  score.value=0; correct.value=0; combo.value=0; maxCombo.value=0; leveled.value=false
  qIdx.value=0; maxTime.value=getMaxTime()
  phase.value='play'
  nextRound()
}

function nextRound() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  qIdx.value++
  answered.value=false; wasRight.value=false; picked.value=null
  correctAns.value = generateQuestion()
  const wrongs = new Set()
  while (wrongs.size < 3) {
    const w = correctAns.value + rand(-10,10)
    if (w !== correctAns.value) wrongs.add(w)
  }
  options.value = shuffle([correctAns.value, ...wrongs])
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
  answered.value=true; wasRight.value=false; combo.value=0
  shaking.value=true; setTimeout(()=>shaking.value=false, 500)
  speak('시간 초과! 정답은 ' + correctAns.value)
  setTimeout(nextRound, 1800)
}

function selectAnswer(opt) {
  if (answered.value) return
  clearInterval(timer)
  answered.value=true; picked.value=opt
  wasRight.value = opt === correctAns.value
  if (wasRight.value) {
    correct.value++; combo.value++
    if (combo.value > maxCombo.value) maxCombo.value=combo.value
    score.value += 10 + timeLeft.value*2 + (combo.value>1?combo.value*5:0)
    speak(combo.value > 2 ? combo.value + '콤보! 대단해요!' : '정답!')
  } else {
    combo.value=0; shaking.value=true; setTimeout(()=>shaking.value=false, 500)
    speak('오답. 정답은 ' + correctAns.value)
  }
  setTimeout(nextRound, 1500)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if (correct.value >= (level.value<=2?9:level.value<=4?10:11)) {
    level.value++; localStorage.setItem('mathchallenge_level', level.value)
    leveled.value=true; speak('레벨업!')
  }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.mathchallenge-game { min-height:100vh; background:linear-gradient(135deg,#0c4a6e,#0369a1,#0284c7); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.85); font-size:16px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#bae6fd; font-size:14px; line-height:1.8; margin:12px auto; max-width:220px; text-align:left; }
.start-btn { background:#fff; color:#0c4a6e; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:480px; margin:0 auto; }
.top-row { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.combo-badge { background:#f59e0b; color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.timer-circle { position:relative; width:60px; height:60px; }
.timer-text { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:#fff; font-weight:700; font-size:16px; }
.qcount { color:rgba(255,255,255,0.7); font-size:15px; font-weight:600; }
.equation-card { background:rgba(255,255,255,0.12); border-radius:20px; padding:30px 20px; text-align:center; margin-bottom:20px; }
.equation-text { font-size:44px; font-weight:900; color:#fff; letter-spacing:2px; }
.equation-sub { color:#7dd3fc; font-size:14px; margin-top:6px; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-8px)} 75%{transform:translateX(8px)} }
.shake { animation:shake 0.4s ease; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#0c4a6e; border:none; padding:18px; border-radius:14px; font-size:26px; font-weight:800; cursor:pointer; transition:all 0.2s; }
.choice-btn:hover:not(.disabled) { transform:scale(1.04); background:#fff; }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.feedback { text-align:center; padding:12px; border-radius:12px; font-size:17px; font-weight:700; }
.feedback.right { background:rgba(16,185,129,0.2); color:#a7f3d0; }
.feedback.wrong { background:rgba(239,68,68,0.2); color:#fca5a5; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#fff; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#fff; color:#0c4a6e; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#0c4a6e; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#0369a1; color:#fff; }
</style>
"""

# ===== GAME 20: 세계 지리 퀴즈 =====
game20 = r"""<template>
  <div class="geo-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🌍</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🌍</div>
      <h1 class="title">세계 지리 퀴즈</h1>
      <p class="subtitle">나라, 수도, 국기를 맞춰봐요!</p>
      <div class="level-info">
        <div>레벨 1-2: 아시아 · 유럽</div>
        <div>레벨 3-4: 아메리카 · 아프리카</div>
        <div>레벨 5+: 수도 · 국기 종합</div>
      </div>
      <button class="start-btn" @click="startGame">탐험 시작! 🗺️</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <div class="timer-num" :style="{color:timeLeft<5?'#ef4444':'#fff'}">{{ timeLeft }}초</div>
      </div>
      <div class="question-card">
        <div class="q-flag" v-if="curQ.type==='flag'">{{ curQ.flag }}</div>
        <div class="q-question">{{ curQ.question }}</div>
      </div>
      <div class="choices-grid">
        <button v-for="opt in options" :key="opt.id" class="choice-btn"
          :class="{correct: answered && opt.id===curQ.id, wrong: answered && opt.id===picked && opt.id!==curQ.id, disabled: answered}"
          :disabled="answered" @click="selectAnswer(opt)">
          <span v-if="opt.flag" class="choice-flag">{{ opt.flag }}</span>
          {{ opt.answer }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? '정답! 🎉 '+curQ.fact : curQ.fact }}
      </div>
    </div>

    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">🌐</div>
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

const geoData = [
  // Asia
  {id:'kr',country:'한국',capital:'서울',flag:'🇰🇷',continent:'아시아',level:1},
  {id:'jp',country:'일본',capital:'도쿄',flag:'🇯🇵',continent:'아시아',level:1},
  {id:'cn',country:'중국',capital:'베이징',flag:'🇨🇳',continent:'아시아',level:1},
  {id:'th',country:'태국',capital:'방콕',flag:'🇹🇭',continent:'아시아',level:1},
  {id:'vn',country:'베트남',capital:'하노이',flag:'🇻🇳',continent:'아시아',level:1},
  {id:'in',country:'인도',capital:'뉴델리',flag:'🇮🇳',continent:'아시아',level:1},
  // Europe
  {id:'fr',country:'프랑스',capital:'파리',flag:'🇫🇷',continent:'유럽',level:1},
  {id:'de',country:'독일',capital:'베를린',flag:'🇩🇪',continent:'유럽',level:1},
  {id:'it',country:'이탈리아',capital:'로마',flag:'🇮🇹',continent:'유럽',level:1},
  {id:'es',country:'스페인',capital:'마드리드',flag:'🇪🇸',continent:'유럽',level:1},
  {id:'gb',country:'영국',capital:'런던',flag:'🇬🇧',continent:'유럽',level:1},
  {id:'ru',country:'러시아',capital:'모스크바',flag:'🇷🇺',continent:'유럽',level:1},
  // Americas
  {id:'us',country:'미국',capital:'워싱턴 D.C.',flag:'🇺🇸',continent:'아메리카',level:2},
  {id:'ca',country:'캐나다',capital:'오타와',flag:'🇨🇦',continent:'아메리카',level:2},
  {id:'br',country:'브라질',capital:'브라질리아',flag:'🇧🇷',continent:'아메리카',level:2},
  {id:'mx',country:'멕시코',capital:'멕시코시티',flag:'🇲🇽',continent:'아메리카',level:2},
  {id:'ar',country:'아르헨티나',capital:'부에노스아이레스',flag:'🇦🇷',continent:'아메리카',level:2},
  // Africa
  {id:'eg',country:'이집트',capital:'카이로',flag:'🇪🇬',continent:'아프리카',level:2},
  {id:'za',country:'남아공',capital:'프리토리아',flag:'🇿🇦',continent:'아프리카',level:2},
  {id:'ng',country:'나이지리아',capital:'아부자',flag:'🇳🇬',continent:'아프리카',level:2},
  {id:'ke',country:'케냐',capital:'나이로비',flag:'🇰🇪',continent:'아프리카',level:2},
  // Oceania
  {id:'au',country:'호주',capital:'캔버라',flag:'🇦🇺',continent:'오세아니아',level:3},
  {id:'nz',country:'뉴질랜드',capital:'웰링턴',flag:'🇳🇿',continent:'오세아니아',level:3},
]

function buildQuestions(pool) {
  const qs = []
  for (const d of pool) {
    qs.push({
      id: d.id, type: 'capital',
      question: `${d.country}의 수도는?`,
      answer: d.capital,
      fact: `${d.country}의 수도는 ${d.capital}이에요`,
      flag: null,
    })
    qs.push({
      id: d.id, type: 'flag',
      question: `이 국기는 어느 나라?`,
      answer: d.country,
      flag: d.flag,
      fact: `${d.flag} 는 ${d.country}의 국기예요`,
    })
  }
  return qs
}

const level = ref(parseInt(localStorage.getItem('geo_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const answered = ref(false)
const wasRight = ref(false)
const picked = ref('')
const curQ = ref({id:'',question:'',answer:'',flag:null,fact:'',type:'capital'})
const options = ref([])
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(15)
const maxTime = ref(15)
let timer = null
let queue = []

function getPool() {
  const maxLv = level.value <= 2 ? 1 : level.value <= 4 ? 2 : 3
  return geoData.filter(d => d.level <= maxLv)
}

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(()=>Math.random()-0.5) }

function startGame() {
  score.value=0; correct.value=0; leveled.value=false; qIdx.value=0
  maxTime.value = level.value<=2?15:level.value<=4?12:10
  const pool = getPool()
  const allQs = buildQuestions(pool)
  queue = shuffle(allQs).slice(0, totalQ.value)
  phase.value='play'
  nextQuestion()
}

function nextQuestion() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  const q = queue[qIdx.value]; qIdx.value++
  curQ.value = q; answered.value=false; wasRight.value=false; picked.value=''
  const pool = getPool()
  const wrongs = shuffle(pool.filter(d => d.id !== q.id)).slice(0,3).map(d => ({
    id: d.id, answer: q.type==='capital' ? d.capital : d.country, flag: q.type==='flag' ? d.flag : null
  }))
  options.value = shuffle([{id:q.id, answer:q.answer, flag: q.type==='flag'?q.flag:null}, ...wrongs])
  speak(q.question)
  startTimer()
}

function startTimer() {
  clearInterval(timer)
  timeLeft.value=maxTime.value
  timer = setInterval(()=>{
    timeLeft.value--
    if(timeLeft.value<=0){clearInterval(timer);timeOut()}
  },1000)
}

function timeOut() {
  answered.value=true; wasRight.value=false
  speak('시간 초과! ' + curQ.value.fact)
  setTimeout(nextQuestion, 2500)
}

function selectAnswer(opt) {
  if(answered.value) return
  clearInterval(timer)
  answered.value=true; picked.value=opt.id
  wasRight.value = opt.id===curQ.value.id
  if(wasRight.value){ correct.value++; score.value+=10+timeLeft.value; speak('정답!') }
  else speak(curQ.value.fact)
  setTimeout(nextQuestion, 2500)
}

function endGame() {
  clearInterval(timer); phase.value='result'
  if(correct.value>=8){ level.value++; localStorage.setItem('geo_level',level.value); leveled.value=true; speak('레벨업!') }
}

function goBack() { clearInterval(timer); router.push('/games') }
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.geo-game { min-height:100vh; background:linear-gradient(135deg,#064e3b,#065f46,#047857); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:30px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.85); font-size:16px; }
.level-info { background:rgba(0,0,0,0.2); border-radius:12px; padding:12px 20px; color:#a7f3d0; font-size:14px; line-height:1.8; margin:12px auto; max-width:240px; text-align:left; }
.start-btn { background:#10b981; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:16px; }
.play-area { max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; color:rgba(255,255,255,0.7); font-size:14px; }
.prog-bar { flex:1; height:8px; background:rgba(255,255,255,0.2); border-radius:4px; overflow:hidden; }
.prog-fill { height:100%; background:#10b981; border-radius:4px; transition:width 0.3s; }
.timer-num { font-weight:700; font-size:16px; min-width:32px; text-align:right; transition:color 0.3s; }
.question-card { background:rgba(255,255,255,0.12); border-radius:20px; padding:28px 20px; text-align:center; margin-bottom:20px; }
.q-flag { font-size:64px; margin-bottom:12px; }
.q-question { font-size:22px; font-weight:700; color:#fff; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:12px; }
.choice-btn { background:rgba(255,255,255,0.9); color:#064e3b; border:none; padding:14px 8px; border-radius:12px; font-size:15px; font-weight:700; cursor:pointer; transition:all 0.2s; display:flex; flex-direction:column; align-items:center; gap:2px; }
.choice-btn:hover:not(.disabled) { transform:scale(1.03); background:#fff; }
.choice-btn.correct { background:#10b981; color:#fff; }
.choice-btn.wrong { background:#ef4444; color:#fff; }
.choice-btn.disabled { cursor:not-allowed; }
.choice-flag { font-size:24px; }
.feedback { text-align:center; padding:12px; border-radius:12px; font-size:15px; font-weight:700; }
.feedback.right { background:rgba(16,185,129,0.25); color:#d1fae5; }
.feedback.wrong { background:rgba(239,68,68,0.25); color:#fee2e2; }
.result-box { text-align:center; padding:40px 20px; }
.res-score { font-size:56px; font-weight:900; color:#fff; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; margin:8px 0; }
.levelup { background:#10b981; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#064e3b; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#047857; color:#fff; }
</style>
"""

# Write files
print("=== 게임 17: 주식 시뮬레이션 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameStockSim.vue', game17)

print("=== 게임 18: SAT 영단어 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameSATWords.vue', game18)

print("=== 게임 19: 수학 챌린지 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameMathChallenge.vue', game19)

print("=== 게임 20: 세계 지리 퀴즈 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameWorldGeo.vue', game20)

# Update router
print("\n=== 라우터 업데이트 ===")
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
new_routes = """  { path: '/games/stock', component: () => import('../pages/games/GameStockSim.vue'), name: 'game-stock' },
  { path: '/games/sat-words', component: () => import('../pages/games/GameSATWords.vue'), name: 'game-sat-words' },
  { path: '/games/math-challenge', component: () => import('../pages/games/GameMathChallenge.vue'), name: 'game-math-challenge' },
  { path: '/games/world-geo', component: () => import('../pages/games/GameWorldGeo.vue'), name: 'game-world-geo' },"""

if 'game-stock' not in router_content:
    updated = router_content.replace(
        "  { path: '/games/maze'",
        new_routes + "\n  { path: '/games/maze'"
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', updated)
    print("Router updated")
else:
    print("Routes already exist")

# Update DB
print("\n=== DB 업데이트 ===")
updates = [
    ("주식", "game-stock"),
    ("SAT", "game-sat-words"),
    ("수학챌린지", "game-math-challenge"),
    ("지리", "game-world-geo"),
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

print("\n✅ 게임 17-20 (청소년 1) 배포 완료!")
c.close()
