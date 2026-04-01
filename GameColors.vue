<template>
  <div class="game-colors" :style="bgStyle">
    <!-- Header -->
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="game-title">🎨 색깔 맞추기</div>
      <div class="score-box">⭐ {{ totalStars }}</div>
    </div>

    <!-- Game Screen -->
    <div v-if="!gameOver" class="game-screen">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
      </div>
      <div class="question-info">{{ currentQ }} / {{ totalQ }} 문제</div>
      <div class="level-badge">레벨 {{ level }}</div>

      <!-- Mode A: See color, pick name -->
      <div v-if="currentMode === 'A'" class="mode-a">
        <p class="question-text">무슨 색깔이에요?</p>
        <div class="color-circle-wrap" :class="{ bounce: showCorrect, shake: showWrong }">
          <div class="color-circle" :style="{ background: currentColor.hex }">
            <span class="color-emoji">{{ currentColor.emoji }}</span>
          </div>
          <div v-if="showCorrect" class="stars-burst">
            <span v-for="i in 8" :key="i" class="star-particle" :style="starStyle(i)">⭐</span>
          </div>
        </div>
        <p class="object-hint">{{ currentColor.object }}</p>
        <div class="choices-grid">
          <button
            v-for="choice in choices"
            :key="choice.name"
            class="choice-btn"
            :class="{
              correct: answered && choice.name === currentColor.name,
              wrong: answered && chosen === choice.name && choice.name !== currentColor.name,
              disabled: answered
            }"
            @click="answer(choice)"
          >
            <span class="color-dot" :style="{ background: choice.hex }"></span>
            <span class="choice-text">{{ choice.name }}</span>
          </button>
        </div>
      </div>

      <!-- Mode B: Hear color, tap circle -->
      <div v-else class="mode-b">
        <p class="question-text">들어봐요! 어떤 색깔이에요?</p>
        <button class="speak-btn" @click="speakCurrentColor">🔊 다시 듣기</button>
        <div class="circles-grid">
          <div
            v-for="choice in choices"
            :key="choice.name"
            class="circle-choice"
            :class="{
              correct: answered && choice.name === currentColor.name,
              wrong: answered && chosen === choice.name && choice.name !== currentColor.name,
              disabled: answered
            }"
            :style="{ background: choice.hex }"
            @click="answer(choice)"
          >
            <span class="circle-emoji">{{ choice.emoji }}</span>
            <span v-if="answered" class="circle-label">{{ choice.name }}</span>
          </div>
        </div>
        <div v-if="showCorrect" class="mode-b-stars">
          <span v-for="i in 6" :key="i" class="star-particle-b" :style="starStyleB(i)">⭐</span>
        </div>
      </div>

      <!-- Feedback -->
      <div v-if="answered" class="feedback-area">
        <div v-if="showCorrect" class="feedback correct-feedback">
          🎉 맞아요! <strong>{{ currentColor.name }}</strong>이에요!
        </div>
        <div v-else class="feedback wrong-feedback">
          😅 다시 해봐요! 정답은 <strong>{{ currentColor.name }}</strong>
        </div>
        <button class="next-btn" @click="nextQuestion">
          {{ currentQ < totalQ ? '다음 문제 →' : '결과 보기 🎊' }}
        </button>
      </div>
    </div>

    <!-- Result Screen -->
    <div v-else class="result-screen">
      <div class="result-emoji">🎨</div>
      <h2 class="result-title">색깔 마스터!</h2>
      <div class="result-score">
        <span class="big-stars">⭐ {{ totalStars }}</span>
        <span class="stars-label">STAR 획득!</span>
      </div>
      <div class="result-accuracy">
        정답률: {{ Math.round((correctCount / totalQ) * 100) }}%
        ({{ correctCount }}/{{ totalQ }})
      </div>
      <div v-if="leveledUp" class="level-up-banner">
        🚀 레벨 업! 레벨 {{ level }}이 되었어요! 대단해요!
      </div>
      <div class="result-btns">
        <button class="play-again-btn" @click="startGame">다시 하기 🔄</button>
        <button class="home-btn" @click="goBack">홈으로 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const allColors = [
  { name: '빨간색', hex: '#FF4444', emoji: '🍎', object: '사과' },
  { name: '파란색', hex: '#4488FF', emoji: '🫐', object: '블루베리' },
  { name: '노란색', hex: '#FFD700', emoji: '🌻', object: '해바라기' },
  { name: '초록색', hex: '#44BB44', emoji: '🐸', object: '개구리' },
  { name: '보라색', hex: '#9944FF', emoji: '🍇', object: '포도' },
  { name: '주황색', hex: '#FF8C00', emoji: '🍊', object: '오렌지' },
  { name: '분홍색', hex: '#FF69B4', emoji: '🌸', object: '벚꽃' },
  { name: '하얀색', hex: '#F0F0F0', emoji: '⛄', object: '눈사람' },
  { name: '검은색', hex: '#333333', emoji: '🎱', object: '당구공' },
  { name: '갈색', hex: '#8B4513', emoji: '🐻', object: '곰' },
]

const level = ref(parseInt(localStorage.getItem('colors_level') || '1'))
const totalStars = ref(0)
const gameOver = ref(false)
const leveledUp = ref(false)

const currentQ = ref(0)
const totalQ = ref(10)
const correctCount = ref(0)
const answered = ref(false)
const chosen = ref('')
const showCorrect = ref(false)
const showWrong = ref(false)
const currentMode = ref('A')

const questions = ref([])
const currentColor = ref(allColors[0])
const choices = ref([])

const progressPct = computed(() => (currentQ.value / totalQ.value) * 100)

const bgStyle = computed(() => {
  const hex = currentColor.value.hex
  return {
    background: `linear-gradient(135deg, ${hex}22 0%, ${hex}11 50%, #fff8f0 100%)`
  }
})

const speak = (text) => {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.85; u.pitch = 1.2
  window.speechSynthesis.speak(u)
}

const getActiveColors = () => {
  if (level.value <= 2) return allColors.slice(0, 4)
  if (level.value <= 4) return allColors.slice(0, 6)
  return allColors
}

const shuffle = (arr) => {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

const buildQuestions = () => {
  const active = getActiveColors()
  totalQ.value = level.value >= 5 ? 12 : 10
  const qs = []
  for (let i = 0; i < totalQ.value; i++) {
    qs.push(active[i % active.length])
  }
  return shuffle(qs)
}

const buildChoices = (correct) => {
  const active = getActiveColors()
  const others = shuffle(active.filter(c => c.name !== correct.name)).slice(0, 3)
  return shuffle([correct, ...others])
}

const startGame = () => {
  gameOver.value = false
  leveledUp.value = false
  currentQ.value = 0
  correctCount.value = 0
  totalStars.value = 0
  answered.value = false
  chosen.value = ''
  showCorrect.value = false
  showWrong.value = false
  questions.value = buildQuestions()
  loadQuestion(0)
}

const loadQuestion = (idx) => {
  const color = questions.value[idx]
  currentColor.value = color
  choices.value = buildChoices(color)
  answered.value = false
  chosen.value = ''
  showCorrect.value = false
  showWrong.value = false
  currentMode.value = (level.value >= 3 && idx % 3 === 2) ? 'B' : 'A'
  setTimeout(() => {
    if (currentMode.value === 'A') {
      speak('이것은 무슨 색깔이에요?')
    } else {
      speak(color.name)
    }
  }, 300)
}

const speakCurrentColor = () => {
  speak(currentColor.value.name)
}

const answer = (choice) => {
  if (answered.value) return
  answered.value = true
  chosen.value = choice.name
  if (choice.name === currentColor.value.name) {
    showCorrect.value = true
    correctCount.value++
    const earned = level.value >= 3 ? 3 : 2
    totalStars.value += earned
    speak(`맞아요! ${currentColor.value.name}이에요!`)
  } else {
    showWrong.value = true
    speak('다시 해봐요')
    setTimeout(() => { showWrong.value = false }, 600)
  }
}

const nextQuestion = () => {
  const next = currentQ.value + 1
  if (next >= totalQ.value) {
    finishGame()
  } else {
    currentQ.value = next
    loadQuestion(next)
  }
}

const finishGame = () => {
  const accuracy = correctCount.value / totalQ.value
  if (accuracy >= 0.8) {
    const prevLevel = level.value
    level.value++
    localStorage.setItem('colors_level', level.value)
    if (level.value > prevLevel) {
      leveledUp.value = true
      speak('레벨 업! 대단해요!')
    }
  }
  const rounds = parseInt(localStorage.getItem('colors_rounds') || '0') + 1
  localStorage.setItem('colors_rounds', rounds)
  gameOver.value = true
}

const starStyle = (i) => {
  const angle = (i - 1) * 45
  const rad = (angle * Math.PI) / 180
  const dist = 80
  return {
    transform: `translate(${Math.cos(rad) * dist}px, ${Math.sin(rad) * dist}px)`,
    animationDelay: `${(i - 1) * 60}ms`
  }
}

const starStyleB = (i) => {
  const angle = (i - 1) * 60
  const rad = (angle * Math.PI) / 180
  const dist = 100
  return {
    transform: `translate(${Math.cos(rad) * dist}px, ${Math.sin(rad) * dist}px)`,
    animationDelay: `${(i - 1) * 80}ms`
  }
}

const goBack = () => {
  if (window.speechSynthesis) window.speechSynthesis.cancel()
  router.push('/games')
}

onMounted(() => {
  startGame()
})

onUnmounted(() => {
  if (window.speechSynthesis) window.speechSynthesis.cancel()
})
</script>

<style scoped>
.game-colors {
  min-height: 100vh;
  padding: 0;
  font-family: 'Noto Sans KR', sans-serif;
  transition: background 0.5s ease;
}

.game-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  background: none;
  border: 2px solid #ddd;
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 14px;
  cursor: pointer;
  color: #555;
  transition: all 0.2s;
}
.back-btn:hover { background: #f5f5f5; }

.game-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.score-box {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  padding: 6px 14px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(255,165,0,0.3);
}

.game-screen {
  padding: 16px 20px;
  max-width: 480px;
  margin: 0 auto;
}

.progress-bar {
  height: 8px;
  background: rgba(0,0,0,0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF6B6B, #FFD700);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.question-info {
  text-align: center;
  font-size: 14px;
  color: #888;
  margin-bottom: 4px;
}

.level-badge {
  text-align: center;
  font-size: 13px;
  color: #fff;
  background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 3px 12px;
  border-radius: 12px;
  margin: 0 auto 16px;
  display: block;
  width: fit-content;
}

.question-text {
  text-align: center;
  font-size: 22px;
  font-weight: 700;
  color: #333;
  margin: 0 0 20px;
}

/* Mode A */
.mode-a {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.color-circle-wrap {
  position: relative;
  margin-bottom: 8px;
}

.color-circle {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  border: 6px solid rgba(255,255,255,0.7);
}

.color-emoji {
  font-size: 80px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.bounce .color-circle {
  animation: bounceAnim 0.6s ease;
}

@keyframes bounceAnim {
  0% { transform: scale(1); }
  30% { transform: scale(1.2); }
  60% { transform: scale(0.95); }
  80% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.shake .color-circle {
  animation: shakeAnim 0.5s ease;
}

@keyframes shakeAnim {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-10px); }
  40% { transform: translateX(10px); }
  60% { transform: translateX(-8px); }
  80% { transform: translateX(8px); }
}

.stars-burst {
  position: absolute;
  top: 50%;
  left: 50%;
  pointer-events: none;
}

.star-particle {
  position: absolute;
  font-size: 20px;
  animation: starBurst 0.8s ease-out forwards;
  opacity: 0;
}

@keyframes starBurst {
  0% { opacity: 1; transform: translate(0, 0) scale(0.5); }
  60% { opacity: 1; }
  100% { opacity: 0; }
}

.object-hint {
  font-size: 16px;
  color: #666;
  margin: 4px 0 20px;
  text-align: center;
}

.choices-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  width: 100%;
  max-width: 360px;
}

.choice-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border: 3px solid #e0e0e0;
  border-radius: 16px;
  background: #fff;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 3px 10px rgba(0,0,0,0.08);
}

.choice-btn:hover:not(.disabled) {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
  border-color: #aaa;
}

.choice-btn.correct {
  background: linear-gradient(135deg, #4CAF50, #81C784);
  border-color: #4CAF50;
  color: #fff;
  transform: scale(1.05);
}

.choice-btn.wrong {
  background: #FFEBEE;
  border-color: #FF5252;
  animation: shakeAnim 0.4s ease;
}

.choice-btn.disabled { cursor: default; }

.color-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid rgba(0,0,0,0.15);
  flex-shrink: 0;
}

.choice-text {
  font-size: 17px;
  color: inherit;
}

/* Mode B */
.mode-b {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.speak-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border: none;
  border-radius: 24px;
  padding: 10px 24px;
  font-size: 18px;
  cursor: pointer;
  margin-bottom: 24px;
  box-shadow: 0 4px 14px rgba(102,126,234,0.4);
  transition: all 0.2s;
}
.speak-btn:hover { transform: scale(1.05); }

.circles-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
  max-width: 360px;
}

.circle-choice {
  width: 100%;
  aspect-ratio: 1;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 5px solid rgba(255,255,255,0.7);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
  transition: all 0.2s;
  gap: 4px;
}

.circle-choice:hover:not(.disabled) {
  transform: scale(1.08);
  box-shadow: 0 10px 28px rgba(0,0,0,0.22);
}

.circle-choice.correct {
  border-color: #4CAF50;
  border-width: 6px;
  box-shadow: 0 0 0 4px rgba(76,175,80,0.4);
  transform: scale(1.1);
}

.circle-choice.wrong {
  border-color: #FF5252;
  animation: shakeAnim 0.4s ease;
}

.circle-emoji {
  font-size: 48px;
}

.circle-label {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 3px rgba(0,0,0,0.6);
  background: rgba(0,0,0,0.25);
  padding: 2px 8px;
  border-radius: 10px;
}

.mode-b-stars {
  position: absolute;
  top: 50%;
  left: 50%;
  pointer-events: none;
}

.star-particle-b {
  position: absolute;
  font-size: 24px;
  animation: starBurst 1s ease-out forwards;
  opacity: 0;
}

/* Feedback */
.feedback-area {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.feedback {
  font-size: 20px;
  font-weight: 700;
  padding: 12px 24px;
  border-radius: 16px;
  text-align: center;
}

.correct-feedback {
  background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
  color: #2E7D32;
  border: 2px solid #4CAF50;
}

.wrong-feedback {
  background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
  color: #E65100;
  border: 2px solid #FF9800;
}

.next-btn {
  background: linear-gradient(135deg, #FF6B6B, #FF8E53);
  color: #fff;
  border: none;
  border-radius: 24px;
  padding: 14px 32px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(255,107,107,0.4);
  transition: all 0.2s;
}
.next-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255,107,107,0.5); }

/* Result Screen */
.result-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 70px);
  padding: 40px 20px;
  text-align: center;
}

.result-emoji { font-size: 80px; margin-bottom: 12px; }

.result-title {
  font-size: 32px;
  font-weight: 800;
  color: #333;
  margin: 0 0 20px;
}

.result-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 12px;
}

.big-stars {
  font-size: 48px;
  font-weight: 800;
  color: #FFA500;
  text-shadow: 0 2px 8px rgba(255,165,0,0.4);
}

.stars-label {
  font-size: 18px;
  color: #888;
  margin-top: 4px;
}

.result-accuracy {
  font-size: 18px;
  color: #555;
  margin-bottom: 16px;
  background: rgba(255,255,255,0.7);
  padding: 10px 24px;
  border-radius: 16px;
}

.level-up-banner {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  padding: 12px 28px;
  border-radius: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 16px rgba(102,126,234,0.4);
  animation: bounceAnim 0.6s ease;
}

.result-btns {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  justify-content: center;
}

.play-again-btn {
  background: linear-gradient(135deg, #FF6B6B, #FF8E53);
  color: #fff;
  border: none;
  border-radius: 24px;
  padding: 14px 28px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(255,107,107,0.35);
  transition: all 0.2s;
}
.play-again-btn:hover { transform: translateY(-2px); }

.home-btn {
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: #fff;
  border: none;
  border-radius: 24px;
  padding: 14px 28px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(76,175,80,0.35);
  transition: all 0.2s;
}
.home-btn:hover { transform: translateY(-2px); }
</style>
