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

# ===== GAME 7: 낱말 카드 게임 =====
game7 = r"""<template>
  <div class="wordcard-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 📖</div>
      <div class="score">⭐ {{ totalStars }}</div>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">📖</div>
      <h1 class="title">낱말 카드</h1>
      <p class="subtitle">그림을 보고 단어를 맞춰요!</p>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>
    <div v-if="phase==='play'" class="play-area">
      <div class="progress-row">
        <span>{{ qIdx }}/{{ totalQ }}</span>
        <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
        <span>레벨{{ level }}</span>
      </div>
      <div class="card" :class="{flipped: flipped}" @click="flipCard">
        <div class="card-front">
          <span class="card-emoji">{{ cur.emoji }}</span>
          <p class="card-hint">눌러서 확인!</p>
        </div>
        <div class="card-back">
          <span class="card-emoji">{{ cur.emoji }}</span>
          <span class="card-word">{{ cur.word }}</span>
          <span class="card-eng">{{ cur.eng }}</span>
        </div>
      </div>
      <div class="choices" v-if="!flipped">
        <button v-for="ch in choices" :key="ch.word" class="choice-btn"
          :class="{correct: answered && ch.word===cur.word, wrong: answered && ch.word===picked && ch.word!==cur.word, disabled: answered}"
          :disabled="answered" @click="pick(ch)">
          {{ ch.word }}
        </button>
      </div>
      <div v-if="flipped && !answered" class="flip-btns">
        <button class="next-btn" @click="nextCard">다음 카드 ▶</button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? cur.word+'! 정답! 🎉' : '정답은 '+cur.word+'이에요' }}
      </div>
    </div>
    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">📚</div>
      <div class="res-score">{{ correct }}/{{ totalQ }}</div>
      <div class="stars-row">+{{ earned }} ⭐</div>
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
const allWords = [
  {emoji:'🍎',word:'사과',eng:'Apple'},{emoji:'🐶',word:'강아지',eng:'Dog'},
  {emoji:'🏠',word:'집',eng:'House'},{emoji:'📚',word:'책',eng:'Book'},
  {emoji:'🚗',word:'자동차',eng:'Car'},{emoji:'🌸',word:'꽃',eng:'Flower'},
  {emoji:'🐱',word:'고양이',eng:'Cat'},{emoji:'✏️',word:'연필',eng:'Pencil'},
  {emoji:'☀️',word:'해',eng:'Sun'},{emoji:'🌙',word:'달',eng:'Moon'},
  {emoji:'⭐',word:'별',eng:'Star'},{emoji:'🍌',word:'바나나',eng:'Banana'},
  {emoji:'🐰',word:'토끼',eng:'Rabbit'},{emoji:'🎈',word:'풍선',eng:'Balloon'},
  {emoji:'🦋',word:'나비',eng:'Butterfly'},{emoji:'🍓',word:'딸기',eng:'Strawberry'},
  {emoji:'🐘',word:'코끼리',eng:'Elephant'},{emoji:'🌊',word:'바다',eng:'Sea'},
  {emoji:'⛰️',word:'산',eng:'Mountain'},{emoji:'🌈',word:'무지개',eng:'Rainbow'},
]
const speak = t => { if(!window.speechSynthesis) return; window.speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.85; u.pitch=1.2; window.speechSynthesis.speak(u) }
const level = ref(parseInt(localStorage.getItem('wordcard_level')||'1'))
const totalStars = ref(parseInt(localStorage.getItem('wordcard_stars')||'0'))
const phase = ref('start'), qIdx = ref(0), totalQ = ref(10), correct = ref(0), earned = ref(0), leveled = ref(false)
const cur = ref(allWords[0]), choices = ref([]), answered = ref(false), picked = ref(''), wasRight = ref(false), flipped = ref(false)
const levelWords = computed(() => level.value<=2 ? allWords.slice(0,10) : level.value<=4 ? allWords.slice(0,15) : allWords)
const goBack = () => { window.speechSynthesis?.cancel(); router.push('/games') }
function startGame() { qIdx.value=0; correct.value=0; earned.value=0; leveled.value=false; phase.value='play'; nextCard() }
function nextCard() {
  answered.value=false; picked.value=''; flipped.value=false
  const pool=levelWords.value; cur.value=pool[Math.floor(Math.random()*pool.length)]
  const s=new Set([cur.value.word])
  while(s.size<4) s.add(pool[Math.floor(Math.random()*pool.length)].word)
  choices.value=[...s].sort(()=>Math.random()-0.5).map(w=>allWords.find(x=>x.word===w))
  setTimeout(()=>speak('이 그림의 이름은 뭐예요?'),300)
}
function flipCard() { if(answered.value) return; flipped.value=!flipped.value; if(flipped.value) speak(cur.value.word) }
function pick(ch) {
  if(answered.value||flipped.value) return; answered.value=true; picked.value=ch.word
  if(ch.word===cur.value.word){ wasRight.value=true; correct.value++; speak(ch.word+'! 정답!') }
  else { wasRight.value=false; speak('정답은 '+cur.value.word+'이에요') }
  qIdx.value++; if(qIdx.value>=totalQ.value) setTimeout(()=>showResult(),1800); else setTimeout(()=>nextCard(),1800)
}
function showResult() {
  earned.value=correct.value; totalStars.value+=earned.value; localStorage.setItem('wordcard_stars',totalStars.value)
  if(correct.value>=8){ level.value++; leveled.value=true; localStorage.setItem('wordcard_level',level.value); speak('레벨업! 대단해요!') }
  else speak(correct.value+'개 맞았어요!'); phase.value='result'
}
onMounted(()=>speak('낱말 카드 게임!'))
onUnmounted(()=>window.speechSynthesis?.cancel())
</script>
<style scoped>
.wordcard-game{min-height:100vh;background:linear-gradient(135deg,#FFF9C4,#FFECB3,#FFE0B2);display:flex;flex-direction:column;align-items:center;font-family:'Nanum Gothic',sans-serif}
.game-header{width:100%;display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:rgba(255,255,255,0.4)}
.back-btn,.score{background:rgba(255,255,255,0.8);border:none;border-radius:20px;padding:8px 14px;font-size:14px;font-weight:bold;cursor:pointer;color:#333}
.level-badge{background:rgba(255,255,255,0.9);border-radius:20px;padding:6px 16px;font-size:16px;font-weight:bold;color:#E65100}
.center-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:40px 20px}
.title{font-size:44px;font-weight:900;color:#E65100;margin:0}
.subtitle{font-size:22px;color:#555;font-weight:bold;margin:0}
.start-btn{background:linear-gradient(135deg,#FF9800,#FF5722);color:white;border:none;border-radius:30px;padding:16px 48px;font-size:26px;font-weight:900;cursor:pointer;box-shadow:0 6px 20px rgba(255,152,0,0.4);transition:transform 0.15s}
.start-btn:hover{transform:scale(1.06)}
.play-area{flex:1;display:flex;flex-direction:column;align-items:center;width:100%;padding:16px;gap:16px}
.progress-row{width:90%;display:flex;align-items:center;gap:8px;font-size:14px;font-weight:bold;color:#555}
.prog-bar{flex:1;height:10px;background:rgba(255,255,255,0.5);border-radius:5px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#FF9800,#FF5722);border-radius:5px;transition:width 0.4s}
.card{width:240px;height:240px;perspective:800px;cursor:pointer;position:relative}
.card-front,.card-back{position:absolute;inset:0;border-radius:24px;backface-visibility:hidden;transition:transform 0.5s;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;box-shadow:0 8px 30px rgba(0,0,0,0.15)}
.card-front{background:white;transform:rotateY(0)}
.card-back{background:linear-gradient(135deg,#FF9800,#FF5722);transform:rotateY(180deg)}
.card.flipped .card-front{transform:rotateY(-180deg)}
.card.flipped .card-back{transform:rotateY(0)}
.card-emoji{font-size:80px}
.card-hint{font-size:14px;color:#aaa;margin:0}
.card-word{font-size:36px;font-weight:900;color:white}
.card-eng{font-size:20px;color:rgba(255,255,255,0.8)}
.choices{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:90%;max-width:340px}
.choice-btn{background:white;border:3px solid transparent;border-radius:20px;padding:16px 8px;font-size:22px;font-weight:bold;cursor:pointer;box-shadow:0 3px 10px rgba(0,0,0,0.1);transition:transform 0.1s;color:#333}
.choice-btn:hover:not(.disabled){transform:scale(1.04)}
.choice-btn.correct{background:#A8FF78;border-color:#4CAF50;animation:pop 0.4s}
@keyframes pop{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}
.choice-btn.wrong{background:#FFB3B3;border-color:#F44336}
.flip-btns{display:flex;gap:12px}
.next-btn{background:linear-gradient(135deg,#FF9800,#FF5722);color:white;border:none;border-radius:20px;padding:14px 28px;font-size:20px;font-weight:bold;cursor:pointer}
.feedback{font-size:20px;font-weight:bold;border-radius:16px;padding:10px 24px}
.feedback.right{background:rgba(168,255,120,0.6);color:#1a7a1a}
.feedback.wrong{background:rgba(255,179,179,0.6);color:#c0392b}
.result-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:30px}
.res-score{font-size:64px;font-weight:900;color:#E65100;background:rgba(255,255,255,0.8);border-radius:24px;padding:14px 40px}
.stars-row{font-size:40px;font-weight:900;color:#FF9F43}
.levelup{background:linear-gradient(135deg,#FFD700,#FFA500);border-radius:20px;padding:14px 30px;font-size:24px;font-weight:900;color:white;animation:pulse 0.6s ease infinite alternate}
@keyframes pulse{from{transform:scale(1)}to{transform:scale(1.05)}}
.res-btns{display:flex;gap:12px}
.rbtn{background:linear-gradient(135deg,#FF9800,#FF5722);color:white;border:none;border-radius:24px;padding:14px 28px;font-size:20px;font-weight:bold;cursor:pointer}
.rbtn.home{background:rgba(255,255,255,0.7);color:#333}
</style>"""

write_file('/var/www/somekorean/resources/js/pages/games/GameWordCard.vue', game7)

# ===== GAME 8: 덧셈 뺄셈 =====
game8 = r"""<template>
  <div class="math-game" :class="{shake: shaking, flash: flashing}">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🔢</div>
      <div class="score">⭐ {{ totalStars }}</div>
    </div>
    <div class="progress-wrap" v-if="phase==='play'">
      <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
      <span class="prog-txt">{{ qIdx }}/{{ totalQ }}</span>
      <div v-if="timerOn" class="timer-wrap">
        <svg width="36" height="36" class="timer-svg">
          <circle cx="18" cy="18" r="15" fill="none" stroke="#eee" stroke-width="3"/>
          <circle cx="18" cy="18" r="15" fill="none" :stroke="timerColor" stroke-width="3"
            stroke-dasharray="94.2" :stroke-dashoffset="94.2*(1-timeLeft/maxTime)"
            stroke-linecap="round" transform="rotate(-90 18 18)" style="transition:stroke-dashoffset 1s linear"/>
        </svg>
        <span class="timer-num">{{ timeLeft }}</span>
      </div>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🔢</div>
      <h1 class="title">덧셈 뺄셈</h1>
      <p class="subtitle">계산해 봐요!</p>
      <div class="info-box">
        레벨 {{ level }}: {{ levelInfo }}
      </div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>
    <div v-if="phase==='play'" class="play-area">
      <div class="equation">
        <span class="num">{{ a }}</span>
        <span class="op">{{ op }}</span>
        <span class="num">{{ b }}</span>
        <span class="eq">=</span>
        <span class="q-mark">?</span>
      </div>
      <div class="choices">
        <button v-for="ch in choices" :key="ch" class="choice-btn"
          :class="{correct: answered && ch===answer, wrong: answered && ch===picked && ch!==answer, disabled: answered}"
          :disabled="answered" @click="pick(ch)">
          {{ ch }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? answer+'! 정답이에요! 🎉' : '정답은 '+answer+'이에요 💪' }}
      </div>
    </div>
    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">🏆</div>
      <div class="res-score">{{ correct }}/{{ totalQ }}</div>
      <div class="stars-row">+{{ earned }} ⭐</div>
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
const speak = t => { if(!window.speechSynthesis) return; window.speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.85; u.pitch=1.1; window.speechSynthesis.speak(u) }
const level = ref(parseInt(localStorage.getItem('mathbasic_level')||'1'))
const totalStars = ref(parseInt(localStorage.getItem('mathbasic_stars')||'0'))
const phase = ref('start'), qIdx = ref(0), totalQ = ref(10), correct = ref(0), earned = ref(0), leveled = ref(false)
const a = ref(1), b = ref(1), op = ref('+'), answer = ref(2)
const choices = ref([]), answered = ref(false), picked = ref(0), wasRight = ref(false)
const shaking = ref(false), flashing = ref(false)
const timeLeft = ref(15), maxTime = ref(15), timerOn = computed(()=>level.value>=4)
const timerColor = computed(()=>timeLeft.value>maxTime.value*0.5?'#4CAF50':timeLeft.value>maxTime.value*0.25?'#FF9800':'#F44336')
let timerInterval = null
const levelInfo = computed(()=>{
  if(level.value<=2) return '1~5 덧셈'
  if(level.value<=3) return '1~10 덧셈'
  if(level.value<=5) return '덧셈 뺄셈 (15초)'
  return '덧셈 뺄셈 (10초)'
})
const goBack = () => { clearInterval(timerInterval); window.speechSynthesis?.cancel(); router.push('/games') }
function startGame() { qIdx.value=0; correct.value=0; earned.value=0; leveled.value=false; phase.value='play'; nextQ() }
function nextQ() {
  answered.value=false; picked.value=0; shaking.value=false; flashing.value=false
  clearInterval(timerInterval)
  const maxN = level.value<=2?5:level.value<=3?10:level.value<=5?15:20
  const useSubtract = level.value>=3
  if(useSubtract && Math.random()<0.4) {
    op.value='-'; a.value=Math.floor(Math.random()*maxN)+2; b.value=Math.floor(Math.random()*(a.value-1))+1; answer.value=a.value-b.value
  } else {
    op.value='+'; a.value=Math.floor(Math.random()*(maxN/2))+1; b.value=Math.floor(Math.random()*(maxN/2))+1; answer.value=a.value+b.value
  }
  const s=new Set([answer.value])
  while(s.size<4){ const r=answer.value+Math.floor(Math.random()*7)-3; if(r>=0&&r!==answer.value) s.add(r) }
  choices.value=[...s].sort((x,y)=>x-y)
  const q = `${a.value} ${op.value==='+'?'더하기':'빼기'} ${b.value} 는?`
  setTimeout(()=>speak(q),300)
  if(timerOn.value) {
    maxTime.value=level.value>=6?10:15; timeLeft.value=maxTime.value
    timerInterval=setInterval(()=>{ timeLeft.value--; if(timeLeft.value<=0){ clearInterval(timerInterval); timeOut() } },1000)
  }
}
function timeOut() { answered.value=true; wasRight.value=false; shaking.value=true; speak('시간 초과!'); qIdx.value++; setTimeout(()=>{ if(qIdx.value>=totalQ.value) showResult(); else nextQ() },1500) }
function pick(ch) {
  if(answered.value) return; clearInterval(timerInterval); answered.value=true; picked.value=ch
  if(ch===answer.value){ wasRight.value=true; correct.value++; flashing.value=true; speak(ch+'! 정답이에요!'); setTimeout(()=>flashing.value=false,1000) }
  else { wasRight.value=false; shaking.value=true; speak('정답은 '+answer.value+'이에요'); setTimeout(()=>shaking.value=false,600) }
  qIdx.value++; if(qIdx.value>=totalQ.value) setTimeout(()=>showResult(),1800); else setTimeout(()=>nextQ(),1800)
}
function showResult() {
  earned.value=correct.value; totalStars.value+=earned.value; localStorage.setItem('mathbasic_stars',totalStars.value)
  if(correct.value>=8){ level.value++; leveled.value=true; localStorage.setItem('mathbasic_level',level.value); speak('레벨업! 대단해요!') }
  else speak(correct.value+'개 맞았어요!'); phase.value='result'
}
onMounted(()=>speak('덧셈 뺄셈 게임!'))
onUnmounted(()=>{ clearInterval(timerInterval); window.speechSynthesis?.cancel() })
</script>
<style scoped>
.math-game{min-height:100vh;background:linear-gradient(135deg,#E3F2FD,#BBDEFB,#90CAF9);display:flex;flex-direction:column;align-items:center;font-family:'Nanum Gothic',sans-serif;transition:background 0.3s;position:relative}
.math-game.flash{background:linear-gradient(135deg,#A8FF78,#78FFD6)}
.math-game.shake{animation:shake 0.5s ease}
@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-10px)}40%{transform:translateX(10px)}60%{transform:translateX(-8px)}80%{transform:translateX(8px)}}
.game-header{width:100%;display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:rgba(255,255,255,0.4)}
.back-btn,.score{background:rgba(255,255,255,0.8);border:none;border-radius:20px;padding:8px 14px;font-size:14px;font-weight:bold;cursor:pointer;color:#333}
.level-badge{background:rgba(255,255,255,0.9);border-radius:20px;padding:6px 16px;font-size:16px;font-weight:bold;color:#1565C0}
.progress-wrap{width:90%;display:flex;align-items:center;gap:8px;margin:8px auto}
.prog-bar{flex:1;height:12px;background:rgba(255,255,255,0.5);border-radius:6px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#2196F3,#00BCD4);border-radius:6px;transition:width 0.4s}
.prog-txt{font-size:13px;font-weight:bold;color:#1565C0;white-space:nowrap}
.timer-wrap{position:relative;width:36px;height:36px;display:flex;align-items:center;justify-content:center}
.timer-svg{position:absolute;inset:0}
.timer-num{font-size:13px;font-weight:900;color:#333;position:relative;z-index:1}
.center-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:40px 20px;text-align:center}
.title{font-size:44px;font-weight:900;color:#1565C0;margin:0}
.subtitle{font-size:22px;color:#555;font-weight:bold;margin:0}
.info-box{background:rgba(255,255,255,0.7);border-radius:16px;padding:12px 24px;font-size:18px;font-weight:bold;color:#333}
.start-btn{background:linear-gradient(135deg,#1976D2,#00BCD4);color:white;border:none;border-radius:30px;padding:16px 48px;font-size:26px;font-weight:900;cursor:pointer;box-shadow:0 6px 20px rgba(25,118,210,0.4);transition:transform 0.15s}
.start-btn:hover{transform:scale(1.06)}
.play-area{flex:1;display:flex;flex-direction:column;align-items:center;width:100%;padding:16px;gap:20px;justify-content:center}
.equation{display:flex;align-items:center;gap:12px;background:white;border-radius:28px;padding:24px 36px;box-shadow:0 8px 30px rgba(0,0,0,0.15)}
.num{font-size:64px;font-weight:900;color:#1565C0;line-height:1}
.op{font-size:56px;font-weight:900;color:#FF5722;line-height:1}
.eq{font-size:56px;font-weight:900;color:#333;line-height:1}
.q-mark{font-size:64px;font-weight:900;color:#E91E63;line-height:1}
.choices{display:grid;grid-template-columns:1fr 1fr;gap:14px;width:90%;max-width:360px}
.choice-btn{background:white;border:3px solid transparent;border-radius:20px;padding:18px;font-size:36px;font-weight:900;cursor:pointer;box-shadow:0 3px 10px rgba(0,0,0,0.1);transition:transform 0.1s;color:#333}
.choice-btn:hover:not(.disabled){transform:scale(1.06);border-color:#1976D2}
.choice-btn.correct{background:#A8FF78;border-color:#4CAF50;animation:pop 0.4s}
@keyframes pop{0%,100%{transform:scale(1)}50%{transform:scale(1.15)}}
.choice-btn.wrong{background:#FFB3B3;border-color:#F44336}
.feedback{font-size:22px;font-weight:bold;border-radius:16px;padding:12px 28px;text-align:center}
.feedback.right{background:rgba(168,255,120,0.6);color:#1a7a1a}
.feedback.wrong{background:rgba(255,179,179,0.6);color:#c0392b}
.result-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:30px}
.res-score{font-size:64px;font-weight:900;color:#1565C0;background:rgba(255,255,255,0.8);border-radius:24px;padding:14px 40px}
.stars-row{font-size:40px;font-weight:900;color:#FF9F43}
.levelup{background:linear-gradient(135deg,#FFD700,#FFA500);border-radius:20px;padding:14px 30px;font-size:24px;font-weight:900;color:white;animation:pulse 0.6s ease infinite alternate}
@keyframes pulse{from{transform:scale(1)}to{transform:scale(1.05)}}
.res-btns{display:flex;gap:12px}
.rbtn{background:linear-gradient(135deg,#1976D2,#00BCD4);color:white;border:none;border-radius:24px;padding:14px 28px;font-size:20px;font-weight:bold;cursor:pointer}
.rbtn.home{background:rgba(255,255,255,0.7);color:#333}
</style>"""

write_file('/var/www/somekorean/resources/js/pages/games/GameMathBasic.vue', game8)

# Update router
router_content = ssh('cat /var/www/somekorean/resources/js/router/index.js')
new_routes = """    { path: '/games/wordcard', component: () => import('../pages/games/GameWordCard.vue'), name: 'game-wordcard' },
    { path: '/games/math-basic', component: () => import('../pages/games/GameMathBasic.vue'), name: 'game-math-basic' },"""

if 'game-shapes' in router_content and 'game-wordcard' not in router_content:
    router_content = router_content.replace(
        "{ path: '/games/shapes', component: () => import('../pages/games/GameShapes.vue'), name: 'game-shapes' },",
        "{ path: '/games/shapes', component: () => import('../pages/games/GameShapes.vue'), name: 'game-shapes' },\n    " + new_routes
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', router_content)
    print('Router updated with games 7,8')

print('Building...')
result = ssh('cd /var/www/somekorean && npm run build 2>&1 | tail -5', timeout=300)
print(result)
print('Route cache:', ssh('php /var/www/somekorean/artisan route:cache 2>&1 | tail -2'))
c.close()
