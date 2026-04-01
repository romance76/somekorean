<template>
  <div class="animals-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🐾</div>
      <div class="score-badge">⭐ {{ score }}점</div>
    </div>

    <!-- 시작 화면 -->
    <div v-if="phase==='start'" class="start-screen">
      <div class="start-mascot">
        <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f98c/512.png" alt="deer" class="mascot-img"/>
      </div>
      <h1 class="game-title">동물 이름 퀴즈</h1>
      <p class="game-desc">사진을 보고 동물 이름을 맞춰요!</p>
      <div class="level-card">
        <div class="lv-row" v-for="lv in levelDesc" :key="lv.lv" :class="{active: level>=lv.lv}">
          <span class="lv-badge">Lv.{{ lv.lv }}</span>
          <span>{{ lv.desc }}</span>
        </div>
      </div>
      <button class="play-btn" @click="startGame">게임 시작! 🎮</button>
    </div>

    <!-- 게임 화면 -->
    <div v-if="phase==='play'" class="play-screen">
      <div class="play-header">
        <div class="q-counter">{{ qIdx + 1 }} / {{ totalQ }}</div>
        <div class="timer-ring" v-if="maxTime > 0">
          <svg width="48" height="48" viewBox="0 0 48 48">
            <circle cx="24" cy="24" r="20" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="4"/>
            <circle cx="24" cy="24" r="20" fill="none" :stroke="timeLeft<=3?'#f87171':'#34d399'" stroke-width="4"
              :stroke-dasharray="125.6" :stroke-dashoffset="125.6*(1-timeLeft/maxTime)"
              transform="rotate(-90 24 24)" stroke-linecap="round"/>
          </svg>
          <span class="timer-text">{{ timeLeft }}</span>
        </div>
        <div class="streak-badge" v-if="streak>1">🔥 {{ streak }}연속</div>
      </div>

      <div class="animal-card">
        <div class="animal-photo-wrap">
          <img :src="animalImgUrl(curAnimal)" :alt="curAnimal.name" class="animal-photo"
            @error="(e) => e.target.src='https://fonts.gstatic.com/s/e/notoemoji/latest/1f43e/512.png'"/>
        </div>
        <div class="animal-sound" v-if="curAnimal.sound">
          <button class="sound-btn" @click="speakAnimal">🔊 {{ curAnimal.sound }}</button>
        </div>
      </div>

      <div class="choices-row">
        <button v-for="opt in choices" :key="opt.name"
          class="choice-card"
          :class="{
            selected: selectedOpt===opt.name && !showFeedback,
            correct: showFeedback && opt.name===curAnimal.name,
            wrong: showFeedback && opt.name===selectedOpt && opt.name!==curAnimal.name
          }"
          :disabled="selectedOpt!==null"
          @click="selectAnswer(opt)">
          <img :src="animalImgUrl(opt)" :alt="opt.name" class="choice-img"
            @error="(e) => e.target.src='https://fonts.gstatic.com/s/e/notoemoji/latest/1f43e/512.png'"/>
          <span class="choice-name">{{ opt.name }}</span>
        </button>
      </div>
    </div>

    <!-- 피드백 오버레이 -->
    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect ? 'fb-correct' : 'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div class="fb-answer" v-if="!lastCorrect">정답은 「<strong>{{ curAnimal?.name }}</strong>」이에요</div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>

    <!-- 결과 화면 -->
    <div v-if="phase==='result'" class="result-screen">
      <div class="result-img">
        <img :src="`https://fonts.gstatic.com/s/e/notoemoji/latest/${correct>=8?'1f3c6':'1f44f'}/512.png`"
          alt="trophy" style="width:100px;height:100px"/>
      </div>
      <div class="result-score">{{ score }}점</div>
      <div class="result-detail">{{ correct }} / {{ totalQ }} 정답</div>
      <div v-if="leveled" class="level-up-badge">🎉 레벨업! → 레벨 {{ level }}</div>
      <div class="result-btns">
        <button class="rbtn retry" @click="startGame">다시 하기 🔄</button>
        <button class="rbtn home" @click="goBack">목록으로 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const levelDesc = [
  {lv:1, desc:'기본 동물 8마리'},
  {lv:2, desc:'동물 14마리'},
  {lv:3, desc:'전체 동물 + 제한시간'},
]

const allAnimals = [
  {name:'강아지', hex:'1f436', sound:'멍멍!', group:1},
  {name:'고양이', hex:'1f431', sound:'야옹~', group:1},
  {name:'토끼', hex:'1f430', sound:'(폴짝)', group:1},
  {name:'곰', hex:'1f43b', sound:'으르렁', group:1},
  {name:'사자', hex:'1f981', sound:'어흥!', group:1},
  {name:'코끼리', hex:'1f418', sound:'(나팔 소리)', group:1},
  {name:'원숭이', hex:'1f412', sound:'끼끼~', group:1},
  {name:'돼지', hex:'1f437', sound:'꿀꿀~', group:1},
  {name:'여우', hex:'1f98a', sound:'(소리 없음)', group:2},
  {name:'개구리', hex:'1f438', sound:'개굴개굴', group:2},
  {name:'나비', hex:'1f98b', sound:'(팔랑팔랑)', group:2},
  {name:'펭귄', hex:'1f427', sound:'(뒤뚱뒤뚱)', group:2},
  {name:'기린', hex:'1f992', sound:'(소리 없음)', group:2},
  {name:'악어', hex:'1f40a', sound:'(으드득)', group:2},
  {name:'호랑이', hex:'1f42f', sound:'어흥!', group:3},
  {name:'상어', hex:'1f988', sound:'(파닥파닥)', group:3},
  {name:'돌고래', hex:'1f42c', sound:'끼이익~', group:3},
  {name:'문어', hex:'1f419', sound:'(소리 없음)', group:3},
  {name:'얼룩말', hex:'1f993', sound:'(히힝)', group:3},
  {name:'고슴도치', hex:'1f994', sound:'(찌르르)', group:3},
]

function animalImgUrl(animal) {
  return `https://fonts.gstatic.com/s/e/notoemoji/latest/${animal.hex}/512.png`
}

const level = ref(parseInt(localStorage.getItem('animal_level') || '1'))
const score = ref(0)
const correct = ref(0)
const streak = ref(0)
const phase = ref('start')
const qIdx = ref(0)
const totalQ = ref(10)
const curAnimal = ref(null)
const choices = ref([])
const selectedOpt = ref(null)
const showFeedback = ref(false)
const lastCorrect = ref(false)
const fbProgress = ref(100)
const leveled = ref(false)
const timeLeft = ref(0)
const maxTime = ref(0)
let fbTimer = null
let countTimer = null
let queue = []

function getPool() {
  if (level.value <= 1) return allAnimals.filter(a => a.group <= 1)
  if (level.value <= 2) return allAnimals.filter(a => a.group <= 2)
  return allAnimals
}

function speak(text, rate = 0.85) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = rate; u.pitch = 1.1
  window.speechSynthesis.speak(u)
}

function speakAnimal() {
  if (curAnimal.value) speak(curAnimal.value.name + '! ' + curAnimal.value.sound)
}

function shuffle(arr) { return [...arr].sort(() => Math.random()-0.5) }

function startGame() {
  score.value = 0; correct.value = 0; streak.value = 0; leveled.value = false
  qIdx.value = 0
  maxTime.value = level.value >= 3 ? 8 : 0
  queue = shuffle(getPool()).slice(0, totalQ.value)
  phase.value = 'play'
  speak('동물 이름을 맞춰봐요!')
  loadQuestion()
}

function loadQuestion() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  const animal = queue[qIdx.value]
  curAnimal.value = animal
  selectedOpt.value = null
  showFeedback.value = false

  const pool = getPool()
  const wrongs = shuffle(pool.filter(a => a.name !== animal.name)).slice(0, 3)
  choices.value = shuffle([animal, ...wrongs])

  clearInterval(countTimer)
  if (maxTime.value > 0) {
    timeLeft.value = maxTime.value
    countTimer = setInterval(() => {
      timeLeft.value--
      if (timeLeft.value <= 0) { clearInterval(countTimer); autoFail() }
    }, 1000)
  }
  speak('이 동물의 이름은?')
}

function autoFail() {
  selectedOpt.value = '__timeout__'
  triggerFeedback(false)
}

function selectAnswer(opt) {
  if (selectedOpt.value !== null) return
  clearInterval(countTimer)
  selectedOpt.value = opt.name
  const isCorrect = opt.name === curAnimal.value.name
  if (isCorrect) {
    correct.value++; streak.value++
    score.value += 10 + (streak.value > 1 ? streak.value * 3 : 0) + (maxTime.value > 0 ? timeLeft.value * 2 : 0)
    speak(opt.name + '! 맞아요!')
  } else {
    streak.value = 0
    speak('아쉬워요! 정답은 ' + curAnimal.value.name)
  }
  triggerFeedback(isCorrect)
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect
  showFeedback.value = true
  fbProgress.value = 100
  clearInterval(fbTimer)
  const duration = isCorrect ? 1400 : 2000
  const step = 50 / duration * 100
  fbTimer = setInterval(() => {
    fbProgress.value = Math.max(0, fbProgress.value - step)
    if (fbProgress.value <= 0) {
      clearInterval(fbTimer)
      showFeedback.value = false
      qIdx.value++
      loadQuestion()
    }
  }, 50)
}

function endGame() {
  phase.value = 'result'
  const threshold = level.value <= 1 ? 7 : level.value <= 2 ? 8 : 9
  if (correct.value >= threshold) {
    level.value++
    localStorage.setItem('animal_level', level.value)
    leveled.value = true
    speak('레벨업! 레벨 ' + level.value + '!')
  } else {
    speak(correct.value + '개 맞았어요! 잘했어요!')
  }
}

function goBack() {
  clearInterval(fbTimer); clearInterval(countTimer)
  window.speechSynthesis?.cancel()
  router.push('/games')
}
onUnmounted(() => { clearInterval(fbTimer); clearInterval(countTimer) })
</script>

<style scoped>
.animals-game { min-height:100vh; background:linear-gradient(160deg,#ecfdf5 0%,#d1fae5 50%,#a7f3d0 100%); font-family:'Noto Sans KR',sans-serif; padding:0; }
.game-header { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:rgba(255,255,255,0.7); backdrop-filter:blur(10px); border-bottom:1px solid rgba(255,255,255,0.5); }
.back-btn { background:#10b981; color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; font-weight:600; }
.level-badge,.score-badge { background:#10b981; color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }

/* 시작 화면 */
.start-screen { display:flex; flex-direction:column; align-items:center; padding:30px 20px; }
.start-mascot { margin-bottom:10px; }
.mascot-img { width:100px; height:100px; }
.game-title { font-size:32px; font-weight:900; color:#065f46; margin:8px 0; }
.game-desc { color:#047857; font-size:16px; margin-bottom:16px; }
.level-card { background:rgba(255,255,255,0.8); border-radius:16px; padding:14px 20px; width:100%; max-width:320px; margin-bottom:20px; }
.lv-row { display:flex; align-items:center; gap:10px; padding:6px 0; color:#374151; font-size:14px; border-bottom:1px solid #d1fae5; }
.lv-row:last-child { border-bottom:none; }
.lv-row.active { color:#065f46; font-weight:700; }
.lv-badge { background:#10b981; color:#fff; font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px; min-width:36px; text-align:center; }
.play-btn { background:linear-gradient(135deg,#10b981,#059669); color:#fff; border:none; padding:16px 48px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; box-shadow:0 4px 20px rgba(16,185,129,0.4); }

/* 게임 화면 */
.play-screen { padding:12px 16px; max-width:500px; margin:0 auto; }
.play-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
.q-counter { background:rgba(255,255,255,0.8); padding:6px 14px; border-radius:20px; font-size:15px; font-weight:700; color:#065f46; }
.timer-ring { position:relative; width:48px; height:48px; }
.timer-text { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:13px; font-weight:800; color:#374151; }
.streak-badge { background:#f59e0b; color:#fff; padding:6px 12px; border-radius:20px; font-size:13px; font-weight:700; }

.animal-card { background:rgba(255,255,255,0.9); border-radius:24px; padding:20px; text-align:center; margin-bottom:16px; box-shadow:0 8px 32px rgba(16,185,129,0.15); }
.animal-photo-wrap { width:200px; height:200px; margin:0 auto 12px; border-radius:20px; overflow:hidden; background:#f0fdf4; display:flex; align-items:center; justify-content:center; }
.animal-photo { width:180px; height:180px; object-fit:contain; }
.sound-btn { background:#ecfdf5; color:#059669; border:1px solid #a7f3d0; padding:8px 16px; border-radius:20px; cursor:pointer; font-size:14px; font-weight:600; }

.choices-row { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.choice-card { background:rgba(255,255,255,0.9); border:2px solid transparent; border-radius:16px; padding:12px 8px; display:flex; flex-direction:column; align-items:center; gap:6px; cursor:pointer; transition:all 0.2s; box-shadow:0 2px 10px rgba(0,0,0,0.06); }
.choice-card:hover:not([disabled]) { transform:translateY(-2px); border-color:#10b981; box-shadow:0 6px 20px rgba(16,185,129,0.2); }
.choice-img { width:64px; height:64px; object-fit:contain; }
.choice-name { font-size:16px; font-weight:700; color:#374151; }
.choice-card.correct { border-color:#10b981; background:#d1fae5; }
.choice-card.wrong { border-color:#ef4444; background:#fee2e2; }

/* 피드백 오버레이 */
.feedback-overlay { position:fixed; inset:0; z-index:100; display:flex; align-items:center; justify-content:center; }
.fb-correct { background:rgba(16,185,129,0.92); }
.fb-wrong { background:rgba(239,68,68,0.92); }
.fb-content { text-align:center; padding:32px 40px; border-radius:24px; background:rgba(255,255,255,0.15); backdrop-filter:blur(4px); }
.fb-emoji { font-size:72px; margin-bottom:8px; }
.fb-title { font-size:32px; font-weight:900; color:#fff; margin-bottom:6px; }
.fb-answer { font-size:17px; color:rgba(255,255,255,0.9); margin-bottom:12px; }
.fb-answer strong { font-size:20px; }
.fb-bar-wrap { width:200px; height:6px; background:rgba(255,255,255,0.3); border-radius:3px; overflow:hidden; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:3px; transition:width 0.05s linear; }

/* 전환 애니메이션 */
.fb-enter-active,.fb-leave-active { transition:opacity 0.2s,transform 0.2s; }
.fb-enter-from,.fb-leave-to { opacity:0; transform:scale(0.95); }

/* 결과 화면 */
.result-screen { display:flex; flex-direction:column; align-items:center; padding:40px 20px; text-align:center; }
.result-img { margin-bottom:10px; }
.result-score { font-size:56px; font-weight:900; color:#059669; }
.result-detail { color:#047857; font-size:18px; margin:6px 0 16px; }
.level-up-badge { background:#10b981; color:#fff; padding:10px 24px; border-radius:20px; font-size:18px; font-weight:800; margin-bottom:20px; }
.result-btns { display:flex; gap:12px; }
.rbtn { padding:14px 28px; border-radius:20px; border:none; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.retry { background:#10b981; color:#fff; }
.rbtn.home { background:#fff; color:#065f46; border:2px solid #10b981; }
</style>
