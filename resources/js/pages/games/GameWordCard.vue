<template>
  <div class="wcard-game">
    <div class="game-header">
      <button class="back-btn" @click="$router.push('/games')">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 📚</div>
      <div class="score-badge">{{ score }}점</div>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:90px">📚</div>
      <h1 class="title">한국어 단어 카드</h1>
      <p class="subtitle">그림을 보고 단어를 맞춰요!</p>
      <button class="start-btn" @click="startGame">시작하기 ▶</button>
    </div>
    <div v-if="phase==='play'" class="play-box">
      <div class="progress-bar"><div class="progress-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
      <div class="q-count">{{ qIdx+1 }} / {{ totalQ }}</div>
      <div class="card-display">
        <div class="card-image">{{ cur.emoji }}</div>
        <div class="card-hint">{{ cur.hint }}</div>
      </div>
      <p class="question-text">이 그림의 한국어 이름은 무엇인가요?</p>
      <div class="choices">
        <button v-for="opt in cur.opts" :key="opt"
          class="choice-btn" :disabled="answered" @click="answer(opt)">{{ opt }}</button>
      </div>
    </div>
    <div v-if="phase==='end'" class="end-box">
      <div style="font-size:80px">🌟</div>
      <h2 class="end-title">잘 했어요!</h2>
      <p class="end-score">{{ score }}점 · {{ correct }}/{{ totalQ }} 정답</p>
      <div v-if="leveled" class="levelup-badge">🎉 레벨업! 레벨 {{ level }}!</div>
      <button class="start-btn" @click="startGame">다시 하기 🔄</button>
    </div>
    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect?'fb-correct':'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect" class="fb-answer">정답은 「<strong>{{ cur?.word }}</strong>」이에요</div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
const level = ref(parseInt(localStorage.getItem('wordcard_level')||'1'))
const score = ref(0); const qIdx = ref(0); const correct = ref(0)
const leveled = ref(false); const answered = ref(false); const phase = ref('start')
const showFeedback = ref(false); const lastCorrect = ref(false); const fbProgress = ref(100)
let fbTimer = null
const totalQ = 12

const allWords = [
  {word:'사과', emoji:'🍎', hint:'빨간 과일', opts:['사과','배','포도','딸기']},
  {word:'바나나', emoji:'🍌', hint:'노란 과일', opts:['바나나','레몬','망고','수박']},
  {word:'고양이', emoji:'🐱', hint:'야옹~ 하는 동물', opts:['고양이','강아지','토끼','햄스터']},
  {word:'강아지', emoji:'🐶', hint:'멍멍 하는 동물', opts:['강아지','고양이','고양이','늑대']},
  {word:'집', emoji:'🏠', hint:'우리가 사는 곳', opts:['집','학교','병원','공원']},
  {word:'책', emoji:'📚', hint:'글이 있는 것', opts:['책','공책','신문','잡지']},
  {word:'연필', emoji:'✏️', hint:'그림을 그리는 도구', opts:['연필','볼펜','크레용','붓']},
  {word:'자전거', emoji:'🚲', hint:'두 바퀴 탈 것', opts:['자전거','오토바이','자동차','버스']},
  {word:'꽃', emoji:'🌸', hint:'예쁜 식물', opts:['꽃','나무','풀','잎']},
  {word:'해', emoji:'☀️', hint:'낮에 빛나는 것', opts:['해','달','별','구름']},
  {word:'달', emoji:'🌙', hint:'밤하늘에 있는 것', opts:['달','해','별','구름']},
  {word:'물', emoji:'💧', hint:'마시는 투명한 것', opts:['물','주스','우유','차']},
  {word:'밥', emoji:'🍚', hint:'한국 주식', opts:['밥','빵','면','죽']},
  {word:'빵', emoji:'🍞', hint:'구워서 만드는 음식', opts:['빵','떡','과자','쿠키']},
  {word:'신발', emoji:'👟', hint:'발에 신는 것', opts:['신발','양말','장화','슬리퍼']},
]

const questions = ref([])
const cur = computed(() => questions.value[qIdx.value])

function speak(t) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.9
  window.speechSynthesis.speak(u)
}

function shuffle(a) { return [...a].sort(()=>Math.random()-.5) }

function startGame() {
  score.value=0; qIdx.value=0; correct.value=0; leveled.value=false
  answered.value=false; showFeedback.value=false; phase.value='play'
  questions.value = shuffle(allWords).slice(0, totalQ).map(w=>({...w, opts:shuffle(w.opts)}))
  speak('단어 카드를 시작해요!')
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect; showFeedback.value = true; fbProgress.value = 100
  clearInterval(fbTimer)
  const dur = isCorrect ? 1400 : 2000; const step = 50/dur*100
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
  const ok = opt === cur.value.word
  if (ok) { score.value += 10; correct.value++ }
  speak(ok ? '정답이에요!' : `정답은 ${cur.value.word}이에요`)
  triggerFeedback(ok)
}

function endGame() {
  phase.value = 'end'
  if (correct.value >= Math.ceil(totalQ * 0.7)) {
    level.value++; localStorage.setItem('wordcard_level', level.value); leveled.value = true
    speak('레벨업! 잘 했어요!')
  } else speak('다시 한번 도전해봐요!')
}
</script>

<style scoped>
.wcard-game { min-height:100vh; background:linear-gradient(135deg,#0c4a6e,#0369a1,#0284c7); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score-badge { background:rgba(255,255,255,.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.center-box,.end-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,.8); font-size:16px; }
.start-btn { background:#0ea5e9; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-box { max-width:480px; margin:0 auto; }
.progress-bar { height:8px; background:rgba(255,255,255,.2); border-radius:4px; margin-bottom:8px; }
.progress-fill { height:100%; background:#38bdf8; border-radius:4px; transition:width .3s; }
.q-count { color:rgba(255,255,255,.7); font-size:13px; text-align:right; margin-bottom:16px; }
.card-display { background:rgba(255,255,255,.15); border-radius:20px; padding:32px 20px; margin-bottom:20px; text-align:center; }
.card-image { font-size:100px; line-height:1; margin-bottom:8px; }
.card-hint { color:rgba(255,255,255,.8); font-size:15px; }
.question-text { color:#fff; font-size:17px; font-weight:700; text-align:center; margin-bottom:14px; }
.choices { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.choice-btn { background:rgba(255,255,255,.9); color:#0c4a6e; border:none; padding:16px; border-radius:14px; font-size:17px; font-weight:700; cursor:pointer; transition:all .15s; }
.choice-btn:hover:not(:disabled) { background:#fff; transform:scale(1.03); }
.choice-btn:disabled { cursor:default; }
.end-title { font-size:32px; color:#fff; font-weight:900; }
.end-score { color:rgba(255,255,255,.8); font-size:18px; }
.levelup-badge { background:#0ea5e9; color:#fff; padding:10px 24px; border-radius:20px; font-weight:800; font-size:16px; display:inline-block; margin:14px 0; }
.feedback-overlay { position:fixed; inset:0; display:flex; align-items:center; justify-content:center; z-index:999; backdrop-filter:blur(4px); }
.fb-correct { background:rgba(16,185,129,.85); }
.fb-wrong { background:rgba(239,68,68,.85); }
.fb-content { text-align:center; color:#fff; padding:32px 48px; }
.fb-emoji { font-size:72px; margin-bottom:8px; }
.fb-title { font-size:32px; font-weight:900; margin-bottom:8px; }
.fb-answer { font-size:18px; margin-bottom:16px; }
.fb-bar-wrap { width:200px; height:6px; background:rgba(255,255,255,.3); border-radius:4px; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:4px; transition:width .05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity .25s; }
.fb-enter-from,.fb-leave-to { opacity:0; }
</style>
