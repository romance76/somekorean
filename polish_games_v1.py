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

# === DB 수정 ===
print("=== DB: 수학 챌린지 → 어린이 카테고리 ===")
print(ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"UPDATE games SET category_id=2 WHERE id=19;\"") or "OK")

# =========================================================
# GameAnimals.vue - Noto Emoji 고화질 이미지 + 피드백 오버레이
# =========================================================
game_animals = r"""<template>
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
"""

# =========================================================
# GameWorldGeo.vue - 실제 국기 이미지 사용
# =========================================================
game_world_geo = r"""<template>
  <div class="geo-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🌍</div>
      <div class="score-badge">⭐ {{ score }}점</div>
    </div>

    <div v-if="phase==='start'" class="start-screen">
      <div class="globe-icon">🌍</div>
      <h1 class="game-title">세계 지리 퀴즈</h1>
      <p class="game-desc">나라 이름, 수도, 국기를 맞춰봐요!</p>
      <div class="level-card">
        <div class="lv-row" :class="{active:level>=1}"><span class="lv-badge">Lv.1</span>아시아 · 유럽 국기</div>
        <div class="lv-row" :class="{active:level>=3}"><span class="lv-badge">Lv.3</span>아메리카 · 아프리카</div>
        <div class="lv-row" :class="{active:level>=5}"><span class="lv-badge">Lv.5</span>수도 + 국기 종합</div>
      </div>
      <button class="play-btn" @click="startGame">탐험 시작! 🗺️</button>
    </div>

    <div v-if="phase==='play'" class="play-screen">
      <div class="play-header">
        <div class="q-counter">{{ qIdx + 1 }} / {{ totalQ }}</div>
        <div class="timer-ring">
          <svg width="48" height="48" viewBox="0 0 48 48">
            <circle cx="24" cy="24" r="20" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="4"/>
            <circle cx="24" cy="24" r="20" fill="none" :stroke="timeLeft<=4?'#f87171':'#34d399'" stroke-width="4"
              :stroke-dasharray="125.6" :stroke-dashoffset="125.6*(1-timeLeft/maxTime)"
              transform="rotate(-90 24 24)" stroke-linecap="round"/>
          </svg>
          <span class="timer-text">{{ timeLeft }}</span>
        </div>
        <div class="score-small">{{ score }}점</div>
      </div>

      <div class="question-card">
        <!-- 국기 문제 -->
        <div v-if="curQ.type==='flag'" class="flag-question">
          <div class="flag-wrap">
            <img :src="`https://flagcdn.com/w160/${curQ.code}.png`"
              :alt="curQ.country" class="flag-img"
              @error="(e) => e.target.style.display='none'"/>
          </div>
          <div class="q-text">이 국기는 어느 나라의 것일까요?</div>
        </div>
        <!-- 수도 문제 -->
        <div v-else class="capital-question">
          <div class="country-flag-small">
            <img :src="`https://flagcdn.com/w80/${curQ.code}.png`" :alt="curQ.country" class="flag-sm"/>
          </div>
          <div class="country-name-big">{{ curQ.country }}</div>
          <div class="q-text">이 나라의 수도는 어디일까요?</div>
        </div>
      </div>

      <div class="choices-grid">
        <button v-for="opt in options" :key="opt.id" class="choice-btn"
          :class="{
            correct: showFeedback && opt.id===curQ.id,
            wrong: showFeedback && opt.id===selectedId && opt.id!==curQ.id
          }"
          :disabled="selectedId!==null"
          @click="selectAnswer(opt)">
          <img v-if="curQ.type==='flag'" :src="`https://flagcdn.com/w40/${opt.code}.png`"
            :alt="opt.country" class="choice-flag"/>
          <span class="choice-text">{{ curQ.type==='flag' ? opt.country : opt.capital }}</span>
        </button>
      </div>
    </div>

    <!-- 피드백 오버레이 -->
    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect ? 'fb-correct' : 'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '아쉬워요!' }}</div>
          <div v-if="!lastCorrect" class="fb-answer">
            정답은 「<strong>{{ lastCorrect ? '' : correctAnswerText }}</strong>」이에요
          </div>
          <div v-if="lastCorrect && factText" class="fb-fact">💡 {{ factText }}</div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>

    <div v-if="phase==='result'" class="result-screen">
      <img src="https://fonts.gstatic.com/s/e/notoemoji/latest/1f3c6/512.png" alt="trophy" class="trophy"/>
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
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const geoData = [
  {id:'kr',code:'kr',country:'한국',capital:'서울',continent:'아시아',level:1,fact:'한국의 수도 서울은 600년 역사의 도시예요'},
  {id:'jp',code:'jp',country:'일본',capital:'도쿄',continent:'아시아',level:1,fact:'도쿄는 세계에서 가장 큰 도시 중 하나예요'},
  {id:'cn',code:'cn',country:'중국',capital:'베이징',continent:'아시아',level:1,fact:'중국은 세계에서 인구가 가장 많은 나라예요'},
  {id:'th',code:'th',country:'태국',capital:'방콕',continent:'아시아',level:1,fact:'태국은 불교 문화로 유명한 나라예요'},
  {id:'vn',code:'vn',country:'베트남',capital:'하노이',continent:'아시아',level:1,fact:'베트남은 쌀국수와 커피로 유명해요'},
  {id:'in',code:'in',country:'인도',capital:'뉴델리',continent:'아시아',level:1,fact:'인도는 세계 최대 민주주의 국가예요'},
  {id:'fr',code:'fr',country:'프랑스',capital:'파리',continent:'유럽',level:1,fact:'파리는 \'빛의 도시\'라 불려요'},
  {id:'de',code:'de',country:'독일',capital:'베를린',continent:'유럽',level:1,fact:'독일은 자동차 산업으로 유명해요'},
  {id:'it',code:'it',country:'이탈리아',capital:'로마',continent:'유럽',level:1,fact:'로마는 \'영원의 도시\'라 불려요'},
  {id:'es',code:'es',country:'스페인',capital:'마드리드',continent:'유럽',level:1,fact:'스페인은 투우와 플라멩코로 유명해요'},
  {id:'gb',code:'gb',country:'영국',capital:'런던',continent:'유럽',level:1,fact:'런던에는 빅벤과 버킹엄 궁전이 있어요'},
  {id:'ru',code:'ru',country:'러시아',capital:'모스크바',continent:'유럽',level:2,fact:'러시아는 세계에서 가장 넓은 나라예요'},
  {id:'us',code:'us',country:'미국',capital:'워싱턴 D.C.',continent:'아메리카',level:2,fact:'미국의 국기는 \'성조기\'라 해요'},
  {id:'ca',code:'ca',country:'캐나다',capital:'오타와',continent:'아메리카',level:2,fact:'캐나다는 세계 2위 영토를 가진 나라예요'},
  {id:'br',code:'br',country:'브라질',capital:'브라질리아',continent:'아메리카',level:2,fact:'브라질은 아마존 열대우림이 있어요'},
  {id:'mx',code:'mx',country:'멕시코',capital:'멕시코시티',continent:'아메리카',level:2,fact:'멕시코는 타코와 마리아치로 유명해요'},
  {id:'ar',code:'ar',country:'아르헨티나',capital:'부에노스아이레스',continent:'아메리카',level:2,fact:'아르헨티나는 축구와 탱고로 유명해요'},
  {id:'eg',code:'eg',country:'이집트',capital:'카이로',continent:'아프리카',level:2,fact:'이집트에는 피라미드와 스핑크스가 있어요'},
  {id:'za',code:'za',country:'남아공',capital:'프리토리아',continent:'아프리카',level:2,fact:'남아공은 무지개의 나라라 불려요'},
  {id:'au',code:'au',country:'호주',capital:'캔버라',continent:'오세아니아',level:3,fact:'호주에는 캥거루와 코알라가 살아요'},
  {id:'nz',code:'nz',country:'뉴질랜드',capital:'웰링턴',continent:'오세아니아',level:3,fact:'뉴질랜드는 반지의 제왕 촬영지예요'},
]

function buildQuestions(pool) {
  const qs = []
  for (const d of pool) {
    qs.push({...d, type:'flag', answer: d.country})
    if (level.value >= 3) qs.push({...d, type:'capital', answer: d.capital})
  }
  return qs
}

const level = ref(parseInt(localStorage.getItem('geo_level') || '1'))
const score = ref(0)
const correct = ref(0)
const leveled = ref(false)
const phase = ref('start')
const selectedId = ref(null)
const showFeedback = ref(false)
const lastCorrect = ref(false)
const correctAnswerText = ref('')
const factText = ref('')
const fbProgress = ref(100)
const curQ = ref({})
const options = ref([])
const qIdx = ref(0)
const totalQ = ref(10)
const timeLeft = ref(15)
const maxTime = ref(15)
let fbTimer = null
let countTimer = null
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

function shuffle(arr) { return [...arr].sort(() => Math.random()-0.5) }

function startGame() {
  score.value=0; correct.value=0; leveled.value=false; qIdx.value=0
  maxTime.value = level.value <= 2 ? 15 : level.value <= 4 ? 12 : 10
  const pool = getPool()
  queue = shuffle(buildQuestions(pool)).slice(0, totalQ.value)
  phase.value = 'play'
  loadQuestion()
}

function loadQuestion() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  const q = queue[qIdx.value]
  curQ.value = q
  selectedId.value = null; showFeedback.value = false

  const pool = getPool()
  const wrongs = shuffle(pool.filter(d => d.id !== q.id)).slice(0, 3)
  options.value = shuffle([pool.find(d=>d.id===q.id) || q, ...wrongs])

  clearInterval(countTimer)
  timeLeft.value = maxTime.value
  countTimer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) { clearInterval(countTimer); autoFail() }
  }, 1000)

  speak(q.type === 'flag' ? '이 국기는 어느 나라일까요?' : q.country + '의 수도는 어디일까요?')
}

function autoFail() {
  selectedId.value = '__timeout__'
  correctAnswerText.value = curQ.value.answer
  factText.value = ''
  triggerFeedback(false)
}

function selectAnswer(opt) {
  if (selectedId.value !== null) return
  clearInterval(countTimer)
  selectedId.value = opt.id
  const isCorrect = opt.id === curQ.value.id
  if (isCorrect) {
    correct.value++
    score.value += 10 + timeLeft.value
    factText.value = curQ.value.fact || ''
    speak('정답!')
  } else {
    correctAnswerText.value = curQ.value.answer
    factText.value = ''
    speak('아쉬워요! 정답은 ' + curQ.value.answer)
  }
  triggerFeedback(isCorrect)
}

function triggerFeedback(isCorrect) {
  lastCorrect.value = isCorrect
  showFeedback.value = true
  fbProgress.value = 100
  clearInterval(fbTimer)
  const duration = isCorrect ? 1600 : 2200
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
  clearInterval(countTimer); phase.value = 'result'
  const threshold = level.value <= 2 ? 7 : level.value <= 4 ? 8 : 9
  if (correct.value >= threshold) {
    level.value++; localStorage.setItem('geo_level', level.value)
    leveled.value = true; speak('레벨업!')
  }
}

function goBack() { clearInterval(fbTimer); clearInterval(countTimer); router.push('/games') }
onUnmounted(() => { clearInterval(fbTimer); clearInterval(countTimer) })
</script>

<style scoped>
.geo-game { min-height:100vh; background:linear-gradient(160deg,#ecfeff 0%,#cffafe 50%,#a5f3fc 100%); font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:rgba(255,255,255,0.7); backdrop-filter:blur(10px); border-bottom:1px solid rgba(255,255,255,0.5); }
.back-btn { background:#0891b2; color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; font-weight:600; }
.level-badge,.score-badge { background:#0891b2; color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; font-size:14px; }
.start-screen { display:flex; flex-direction:column; align-items:center; padding:30px 20px; }
.globe-icon { font-size:80px; margin-bottom:8px; }
.game-title { font-size:32px; font-weight:900; color:#0e7490; margin:8px 0; }
.game-desc { color:#0891b2; font-size:16px; margin-bottom:16px; }
.level-card { background:rgba(255,255,255,0.8); border-radius:16px; padding:14px 20px; width:100%; max-width:320px; margin-bottom:20px; }
.lv-row { display:flex; align-items:center; gap:10px; padding:7px 0; color:#374151; font-size:14px; border-bottom:1px solid #cffafe; }
.lv-row:last-child { border-bottom:none; }
.lv-row.active { color:#0e7490; font-weight:700; }
.lv-badge { background:#0891b2; color:#fff; font-size:11px; font-weight:700; padding:2px 8px; border-radius:10px; min-width:36px; text-align:center; }
.play-btn { background:linear-gradient(135deg,#0891b2,#0e7490); color:#fff; border:none; padding:16px 48px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; box-shadow:0 4px 20px rgba(8,145,178,0.4); }
.play-screen { padding:12px 16px; max-width:500px; margin:0 auto; }
.play-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
.q-counter,.score-small { background:rgba(255,255,255,0.8); padding:6px 14px; border-radius:20px; font-size:14px; font-weight:700; color:#0e7490; }
.timer-ring { position:relative; width:48px; height:48px; }
.timer-text { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-size:13px; font-weight:800; color:#374151; }
.question-card { background:rgba(255,255,255,0.9); border-radius:24px; padding:24px; text-align:center; margin-bottom:16px; box-shadow:0 8px 32px rgba(8,145,178,0.1); }
.flag-wrap { display:flex; justify-content:center; margin-bottom:14px; }
.flag-img { width:200px; height:auto; border-radius:8px; box-shadow:0 4px 16px rgba(0,0,0,0.15); border:1px solid rgba(0,0,0,0.08); }
.q-text { font-size:18px; font-weight:700; color:#1f2937; }
.capital-question { display:flex; flex-direction:column; align-items:center; gap:8px; }
.flag-sm { width:64px; height:auto; border-radius:6px; box-shadow:0 2px 8px rgba(0,0,0,0.1); }
.country-name-big { font-size:32px; font-weight:900; color:#0e7490; }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.choice-btn { background:rgba(255,255,255,0.9); border:2px solid transparent; border-radius:16px; padding:12px 8px; display:flex; flex-direction:column; align-items:center; gap:6px; cursor:pointer; transition:all 0.2s; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.choice-btn:hover:not([disabled]) { transform:translateY(-2px); border-color:#0891b2; }
.choice-flag { width:48px; height:auto; border-radius:4px; box-shadow:0 1px 4px rgba(0,0,0,0.1); }
.choice-text { font-size:15px; font-weight:700; color:#374151; text-align:center; }
.choice-btn.correct { border-color:#10b981; background:#d1fae5; }
.choice-btn.wrong { border-color:#ef4444; background:#fee2e2; }
.feedback-overlay { position:fixed; inset:0; z-index:100; display:flex; align-items:center; justify-content:center; }
.fb-correct { background:rgba(16,185,129,0.92); }
.fb-wrong { background:rgba(239,68,68,0.92); }
.fb-content { text-align:center; padding:32px 40px; border-radius:24px; background:rgba(255,255,255,0.15); }
.fb-emoji { font-size:72px; margin-bottom:8px; }
.fb-title { font-size:32px; font-weight:900; color:#fff; margin-bottom:6px; }
.fb-answer { font-size:17px; color:rgba(255,255,255,0.9); margin-bottom:8px; }
.fb-answer strong { font-size:20px; }
.fb-fact { font-size:14px; color:rgba(255,255,255,0.85); font-style:italic; margin-bottom:10px; max-width:280px; }
.fb-bar-wrap { width:200px; height:6px; background:rgba(255,255,255,0.3); border-radius:3px; overflow:hidden; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:3px; transition:width 0.05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity 0.2s,transform 0.2s; }
.fb-enter-from,.fb-leave-to { opacity:0; transform:scale(0.95); }
.result-screen { display:flex; flex-direction:column; align-items:center; padding:40px 20px; text-align:center; }
.trophy { width:100px; height:100px; margin-bottom:12px; }
.result-score { font-size:56px; font-weight:900; color:#0e7490; }
.result-detail { color:#0891b2; font-size:18px; margin:6px 0 16px; }
.level-up-badge { background:#0891b2; color:#fff; padding:10px 24px; border-radius:20px; font-size:18px; font-weight:800; margin-bottom:20px; }
.result-btns { display:flex; gap:12px; }
.rbtn { padding:14px 28px; border-radius:20px; border:none; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.retry { background:#0891b2; color:#fff; }
.rbtn.home { background:#fff; color:#0e7490; border:2px solid #0891b2; }
</style>
"""

print("=== GameAnimals.vue 업데이트 (Noto Emoji 이미지 + 피드백 오버레이) ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameAnimals.vue', game_animals)

print("=== GameWorldGeo.vue 업데이트 (실제 국기 이미지 flagcdn.com) ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameWorldGeo.vue', game_world_geo)

# =========================================================
# GameColors.vue - 피드백 오버레이 추가 + 더 나은 디자인
# =========================================================
print("=== GameColors.vue 피드백 오버레이 패치 ===")
colors_content = ssh("cat /var/www/somekorean/resources/js/pages/games/GameColors.vue")

# Read the current file from server and patch it
# For now, let's patch the key parts: add feedback overlay + fix feedback timing

# Build improved feedback - just update the selectAnswer and nextQuestion logic
# The issue is that games auto-advance too fast without clear feedback
# Let's create a targeted patch

colors_patch = r"""<template>
  <div class="colors-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🎨</div>
      <div class="score-badge">⭐ {{ score }}점</div>
    </div>

    <div v-if="phase==='start'" class="start-screen">
      <div style="font-size:80px">🎨</div>
      <h1 class="game-title">색깔 맞추기</h1>
      <p class="game-desc">화면에 나타나는 색깔 이름을 맞춰요!</p>
      <button class="play-btn" @click="startGame">시작하기! 🚀</button>
    </div>

    <div v-if="phase==='play'" class="play-screen">
      <div class="progress-row">
        <div class="q-num">{{ qIdx + 1 }} / {{ totalQ }}</div>
        <div class="prog-wrap"><div class="prog-bar" :style="{width:(qIdx+1)/totalQ*100+'%'}"></div></div>
        <div class="streak" v-if="streak>1">🔥{{ streak }}</div>
      </div>

      <div class="color-display" :style="{background: curColor.hex}">
        <div class="color-question">무슨 색깔일까요?</div>
      </div>

      <div class="choices-grid">
        <button v-for="opt in choices" :key="opt.name"
          class="color-choice"
          :style="{borderColor: opt.hex}"
          :class="{
            correct: showFeedback && opt.name===curColor.name,
            wrong: showFeedback && opt.name===selectedName && opt.name!==curColor.name
          }"
          :disabled="selectedName!==null"
          @click="selectAnswer(opt)">
          <div class="color-dot" :style="{background:opt.hex}"></div>
          <span>{{ opt.name }}</span>
        </button>
      </div>
    </div>

    <!-- 피드백 오버레이 -->
    <Transition name="fb">
      <div v-if="showFeedback" class="feedback-overlay" :class="lastCorrect ? 'fb-correct' : 'fb-wrong'">
        <div class="fb-content">
          <div class="fb-emoji">{{ lastCorrect ? '🎉' : '😢' }}</div>
          <div class="fb-title">{{ lastCorrect ? '정답이에요!' : '오답이에요!' }}</div>
          <div v-if="!lastCorrect" class="fb-answer">정답은 「<strong>{{ curColor.name }}</strong>」이에요</div>
          <div class="fb-bar-wrap"><div class="fb-bar" :style="{width:fbProgress+'%'}"></div></div>
        </div>
      </div>
    </Transition>

    <div v-if="phase==='result'" class="result-screen">
      <div style="font-size:80px">🎊</div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const allColors = [
  {name:'빨간색', hex:'#ef4444'},
  {name:'파란색', hex:'#3b82f6'},
  {name:'초록색', hex:'#10b981'},
  {name:'노란색', hex:'#fbbf24'},
  {name:'보라색', hex:'#8b5cf6'},
  {name:'주황색', hex:'#f97316'},
  {name:'분홍색', hex:'#ec4899'},
  {name:'하늘색', hex:'#38bdf8'},
  {name:'갈색', hex:'#92400e'},
  {name:'회색', hex:'#6b7280'},
]

const level = ref(parseInt(localStorage.getItem('color_level') || '1'))
const score = ref(0)
const correct = ref(0)
const streak = ref(0)
const phase = ref('start')
const qIdx = ref(0)
const totalQ = ref(12)
const curColor = ref({name:'',hex:''})
const choices = ref([])
const selectedName = ref(null)
const showFeedback = ref(false)
const lastCorrect = ref(false)
const fbProgress = ref(100)
const leveled = ref(false)
let fbTimer = null
let queue = []

function getPool() {
  if (level.value <= 2) return allColors.slice(0, 4)
  if (level.value <= 4) return allColors.slice(0, 6)
  return allColors
}

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9; u.pitch = 1.1
  window.speechSynthesis.speak(u)
}

function shuffle(arr) { return [...arr].sort(() => Math.random()-0.5) }

function startGame() {
  score.value=0; correct.value=0; streak.value=0; leveled.value=false; qIdx.value=0
  queue = shuffle(getPool()).slice(0, totalQ.value)
  phase.value='play'; loadQuestion()
}

function loadQuestion() {
  if (qIdx.value >= totalQ.value) { endGame(); return }
  curColor.value = queue[qIdx.value]
  selectedName.value = null; showFeedback.value = false
  const pool = getPool()
  const wrongs = shuffle(pool.filter(c => c.name !== curColor.value.name)).slice(0, 3)
  choices.value = shuffle([curColor.value, ...wrongs])
  speak('무슨 색깔일까요?')
}

function selectAnswer(opt) {
  if (selectedName.value !== null) return
  selectedName.value = opt.name
  const isCorrect = opt.name === curColor.value.name
  if (isCorrect) {
    correct.value++; streak.value++
    score.value += 10 + (streak.value > 1 ? streak.value * 2 : 0)
    speak(opt.name + '! 정답이에요!')
  } else {
    streak.value = 0
    speak('아쉬워요! 정답은 ' + curColor.value.name)
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
      clearInterval(fbTimer); showFeedback.value = false
      qIdx.value++; loadQuestion()
    }
  }, 50)
}

function endGame() {
  phase.value = 'result'
  if (correct.value >= 9) {
    level.value++; localStorage.setItem('color_level', level.value)
    leveled.value = true; speak('레벨업!')
  }
}

function goBack() { clearInterval(fbTimer); router.push('/games') }
</script>

<style scoped>
.colors-game { min-height:100vh; background:linear-gradient(160deg,#fff7ed,#ffedd5,#fed7aa); font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:rgba(255,255,255,0.7); backdrop-filter:blur(10px); border-bottom:1px solid rgba(255,255,255,0.5); }
.back-btn { background:#f97316; color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; font-weight:600; }
.level-badge,.score-badge { background:#f97316; color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.start-screen { display:flex; flex-direction:column; align-items:center; padding:40px 20px; text-align:center; }
.game-title { font-size:32px; font-weight:900; color:#9a3412; margin:10px 0; }
.game-desc { color:#c2410c; font-size:16px; margin-bottom:20px; }
.play-btn { background:linear-gradient(135deg,#f97316,#ea580c); color:#fff; border:none; padding:16px 48px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; }
.play-screen { padding:16px; max-width:480px; margin:0 auto; }
.progress-row { display:flex; align-items:center; gap:10px; margin-bottom:16px; }
.q-num { font-size:14px; font-weight:700; color:#9a3412; }
.prog-wrap { flex:1; height:8px; background:rgba(0,0,0,0.1); border-radius:4px; overflow:hidden; }
.prog-bar { height:100%; background:#f97316; border-radius:4px; transition:width 0.3s; }
.streak { font-size:14px; font-weight:700; color:#f97316; }
.color-display { height:200px; border-radius:24px; display:flex; align-items:center; justify-content:center; margin-bottom:20px; box-shadow:0 8px 32px rgba(0,0,0,0.15); }
.color-question { font-size:22px; font-weight:700; color:rgba(255,255,255,0.95); text-shadow:0 2px 8px rgba(0,0,0,0.3); }
.choices-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.color-choice { background:#fff; border:3px solid transparent; border-radius:16px; padding:14px; display:flex; align-items:center; gap:10px; cursor:pointer; font-size:17px; font-weight:700; color:#374151; transition:all 0.2s; box-shadow:0 2px 8px rgba(0,0,0,0.06); }
.color-choice:hover:not([disabled]) { transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,0.12); }
.color-dot { width:28px; height:28px; border-radius:50%; flex-shrink:0; }
.color-choice.correct { border-color:#10b981; background:#d1fae5; }
.color-choice.wrong { border-color:#ef4444; background:#fee2e2; }
.feedback-overlay { position:fixed; inset:0; z-index:100; display:flex; align-items:center; justify-content:center; }
.fb-correct { background:rgba(16,185,129,0.92); }
.fb-wrong { background:rgba(239,68,68,0.92); }
.fb-content { text-align:center; padding:32px 40px; border-radius:24px; background:rgba(255,255,255,0.15); }
.fb-emoji { font-size:72px; }
.fb-title { font-size:32px; font-weight:900; color:#fff; margin:8px 0; }
.fb-answer { font-size:17px; color:rgba(255,255,255,0.9); margin-bottom:12px; }
.fb-answer strong { font-size:20px; }
.fb-bar-wrap { width:200px; height:6px; background:rgba(255,255,255,0.3); border-radius:3px; overflow:hidden; margin:0 auto; }
.fb-bar { height:100%; background:#fff; border-radius:3px; transition:width 0.05s linear; }
.fb-enter-active,.fb-leave-active { transition:opacity 0.2s,transform 0.2s; }
.fb-enter-from,.fb-leave-to { opacity:0; transform:scale(0.95); }
.result-screen { display:flex; flex-direction:column; align-items:center; padding:40px 20px; text-align:center; }
.result-score { font-size:56px; font-weight:900; color:#ea580c; }
.result-detail { color:#9a3412; font-size:18px; margin:6px 0 16px; }
.level-up-badge { background:#f97316; color:#fff; padding:10px 24px; border-radius:20px; font-size:18px; font-weight:800; margin-bottom:20px; }
.result-btns { display:flex; gap:12px; }
.rbtn { padding:14px 28px; border-radius:20px; border:none; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.retry { background:#f97316; color:#fff; }
.rbtn.home { background:#fff; color:#9a3412; border:2px solid #f97316; }
</style>
"""

write_file('/var/www/somekorean/resources/js/pages/games/GameColors.vue', colors_patch)

# Build
print("\n=== npm 빌드 ===")
build_result = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -5", timeout=300)
print(build_result)
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1 | head -5"))

print("\n✅ Phase 1 완료: 동물/세계지리/색깔 게임 개선!")
c.close()
