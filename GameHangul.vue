<template>
  <div class="hangul-game" :class="{ 'celebrate': gameOver }">
    <!-- Header Bar -->
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 나가기</button>
      <div class="progress-bar">
        <div class="progress-label">{{ currentQ + 1 }} / {{ totalQ }}</div>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
        </div>
      </div>
      <div class="score-badge">⭐ {{ score }}</div>
    </div>

    <!-- Game Screen -->
    <div v-if="!gameOver" class="game-screen">
      <!-- Question Letter -->
      <div class="question-area">
        <div class="question-label">이 글자는 무엇일까요?</div>
        <div
          class="question-letter"
          :class="{ 'bounce-in': letterAnimate }"
          :style="{ color: questionColor }"
        >
          {{ currentLetter }}
        </div>
        <div class="letter-type-badge">
          {{ isJaum ? '자음 (자음이에요!)' : '모음 (모음이에요!)' }}
        </div>
      </div>

      <!-- Answer Cards -->
      <div class="answers-grid">
        <button
          v-for="(choice, idx) in choices"
          :key="idx"
          class="answer-btn"
          :class="[
            cardColors[idx],
            {
              'correct-flash': answerResult === idx && answerResult !== null && isCorrectAnswer(idx),
              'wrong-shake': answerResult === idx && answerResult !== null && !isCorrectAnswer(idx),
              'disabled': answerResult !== null
            }
          ]"
          @click="selectAnswer(idx)"
          :disabled="answerResult !== null"
        >
          {{ choice }}
        </button>
      </div>

      <!-- Feedback Overlay -->
      <transition name="feedback-fade">
        <div v-if="feedbackMsg" class="feedback-overlay" :class="feedbackType">
          <div class="feedback-icon">{{ feedbackIcon }}</div>
          <div class="feedback-text">{{ feedbackMsg }}</div>
        </div>
      </transition>
    </div>

    <!-- Result Screen -->
    <div v-else class="result-screen">
      <div class="result-stars">
        <span v-for="s in 3" :key="s" class="big-star" :class="{ lit: s <= starsEarned }">⭐</span>
      </div>
      <div class="result-title">게임 끝!</div>
      <div class="result-score">
        <span class="score-num">{{ score }}</span> / {{ totalQ }} 맞았어요!
      </div>
      <div class="reward-badge">
        ⭐ {{ starsEarned }} STAR 획득!
      </div>
      <div class="result-message">{{ resultMessage }}</div>
      <div class="result-buttons">
        <button class="btn-retry" @click="startGame">다시 하기 🎮</button>
        <button class="btn-home" @click="goBack">게임 목록 🏠</button>
      </div>
    </div>

    <!-- Confetti particles when celebrating -->
    <div v-if="gameOver" class="confetti-container">
      <div v-for="i in 20" :key="i" class="confetti-piece" :style="confettiStyle(i)"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// Game data
const jaum = ['ㄱ','ㄴ','ㄷ','ㄹ','ㅁ','ㅂ','ㅅ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
const moum = ['ㅏ','ㅑ','ㅓ','ㅕ','ㅗ','ㅛ','ㅜ','ㅠ','ㅡ','ㅣ','ㅐ','ㅔ']
const allLetters = [...jaum, ...moum]

const totalQ = 10
const cardColors = ['card-pink', 'card-blue', 'card-green', 'card-purple']
const questionColors = ['#FF6B6B','#4ECDC4','#FFE66D','#A855F7','#F97316','#3B82F6']

// State
const score = ref(0)
const currentQ = ref(0)
const currentLetter = ref('')
const choices = ref([])
const answerResult = ref(null)
const gameOver = ref(false)
const feedbackMsg = ref('')
const feedbackType = ref('')
const feedbackIcon = ref('')
const letterAnimate = ref(false)
const questionColor = ref(questionColors[0])
const isJaum = ref(true)

const progressPct = computed(() => ((currentQ.value) / totalQ) * 100)

const starsEarned = computed(() => {
  if (score.value >= 9) return 3
  if (score.value >= 6) return 2
  if (score.value >= 3) return 1
  return 0
})

const resultMessage = computed(() => {
  if (score.value === 10) return '완벽해요! 천재 어린이! 🎉'
  if (score.value >= 8) return '잘했어요! 대단해요! 👏'
  if (score.value >= 5) return '좋아요! 조금 더 연습해요! 💪'
  return '괜찮아요! 다시 해봐요! 🌟'
})

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function pickQuestion() {
  letterAnimate.value = false
  const letter = allLetters[Math.floor(Math.random() * allLetters.length)]
  currentLetter.value = letter
  isJaum.value = jaum.includes(letter)
  questionColor.value = questionColors[Math.floor(Math.random() * questionColors.length)]

  // Pick 3 distractors from same category preferably
  const pool = isJaum.value ? jaum : moum
  const distractors = shuffle(pool.filter(l => l !== letter)).slice(0, 3)
  choices.value = shuffle([letter, ...distractors])
  answerResult.value = null
  feedbackMsg.value = ''

  // Trigger bounce animation
  setTimeout(() => { letterAnimate.value = true }, 10)
}

function isCorrectAnswer(idx) {
  return choices.value[idx] === currentLetter.value
}

function selectAnswer(idx) {
  if (answerResult.value !== null) return
  answerResult.value = idx

  if (isCorrectAnswer(idx)) {
    score.value++
    feedbackType.value = 'correct'
    feedbackIcon.value = '⭐'
    feedbackMsg.value = '정답! 잘했어요!'
  } else {
    feedbackType.value = 'wrong'
    feedbackIcon.value = '😅'
    feedbackMsg.value = `아쉬워요! 정답은 ${currentLetter.value} 이에요`
  }

  setTimeout(() => {
    feedbackMsg.value = ''
    if (currentQ.value + 1 >= totalQ) {
      currentQ.value++
      gameOver.value = true
      claimReward()
    } else {
      currentQ.value++
      pickQuestion()
    }
  }, 1200)
}

async function claimReward() {
  try {
    await axios.post('/api/wallet/daily-bonus', { source: 'game_hangul', amount: starsEarned.value })
  } catch (e) {
    // Silently fail - reward display still shows
  }
}

function startGame() {
  score.value = 0
  currentQ.value = 0
  gameOver.value = false
  answerResult.value = null
  feedbackMsg.value = ''
  pickQuestion()
}

function goBack() {
  router.push('/games')
}

function confettiStyle(i) {
  const colors = ['#FF6B6B','#FFE66D','#4ECDC4','#A855F7','#F97316','#3B82F6','#EC4899']
  const color = colors[i % colors.length]
  const left = (i * 5.2) % 100
  const delay = (i * 0.15) % 2
  const size = 8 + (i % 4) * 4
  return {
    left: left + '%',
    animationDelay: delay + 's',
    backgroundColor: color,
    width: size + 'px',
    height: size + 'px',
    borderRadius: i % 3 === 0 ? '50%' : '2px'
  }
}

onMounted(() => {
  startGame()
})
</script>

<style scoped>
.hangul-game {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF9C4 0%, #FFF3E0 50%, #F3E5F5 100%);
  display: flex;
  flex-direction: column;
  font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif;
  position: relative;
  overflow: hidden;
  user-select: none;
}

/* Header */
.game-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(10px);
  border-bottom: 3px solid rgba(255,180,60,0.3);
  position: sticky;
  top: 0;
  z-index: 10;
}

.back-btn {
  background: #FF6B6B;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.1s;
}
.back-btn:hover { transform: scale(1.05); }

.progress-bar {
  flex: 1;
}
.progress-label {
  font-size: 14px;
  font-weight: 700;
  color: #7C3AED;
  margin-bottom: 4px;
  text-align: center;
}
.progress-track {
  height: 10px;
  background: #E9D5FF;
  border-radius: 10px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #A855F7, #EC4899);
  border-radius: 10px;
  transition: width 0.4s ease;
}

.score-badge {
  font-size: 20px;
  font-weight: 800;
  color: #F59E0B;
  background: #FFFBEB;
  border: 2px solid #FDE68A;
  border-radius: 20px;
  padding: 4px 12px;
  white-space: nowrap;
}

/* Game Screen */
.game-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  gap: 30px;
}

/* Question */
.question-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.question-label {
  font-size: 20px;
  font-weight: 700;
  color: #6B7280;
  text-align: center;
}

.question-letter {
  font-size: 130px;
  font-weight: 900;
  line-height: 1;
  text-shadow: 4px 4px 0px rgba(0,0,0,0.1);
  transition: color 0.3s;
  min-width: 180px;
  text-align: center;
}

@keyframes bounceIn {
  0% { transform: scale(0.3) rotate(-10deg); opacity: 0; }
  60% { transform: scale(1.2) rotate(5deg); }
  80% { transform: scale(0.95) rotate(-2deg); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

.bounce-in {
  animation: bounceIn 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}

.letter-type-badge {
  font-size: 16px;
  font-weight: 700;
  background: rgba(255,255,255,0.8);
  color: #6D28D9;
  padding: 5px 16px;
  border-radius: 20px;
  border: 2px solid #DDD6FE;
}

/* Answers */
.answers-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
  max-width: 480px;
}

.answer-btn {
  font-size: 72px;
  font-weight: 900;
  padding: 20px 10px;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  transition: transform 0.12s, box-shadow 0.12s;
  box-shadow: 0 6px 0 rgba(0,0,0,0.15);
  line-height: 1;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: manipulation;
}

.answer-btn:hover:not(.disabled) {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 10px 0 rgba(0,0,0,0.15);
}

.answer-btn:active:not(.disabled) {
  transform: translateY(2px);
  box-shadow: 0 2px 0 rgba(0,0,0,0.15);
}

.answer-btn.disabled {
  cursor: default;
}

.card-pink   { background: linear-gradient(135deg, #FBCFE8, #F9A8D4); color: #9D174D; }
.card-blue   { background: linear-gradient(135deg, #BFDBFE, #93C5FD); color: #1E3A8A; }
.card-green  { background: linear-gradient(135deg, #BBF7D0, #86EFAC); color: #14532D; }
.card-purple { background: linear-gradient(135deg, #E9D5FF, #C4B5FD); color: #4C1D95; }

/* Correct flash */
@keyframes correctFlash {
  0%   { transform: scale(1); background: #86EFAC; }
  25%  { transform: scale(1.15); background: #4ADE80; box-shadow: 0 0 30px #4ADE80; }
  75%  { transform: scale(1.1); background: #4ADE80; }
  100% { transform: scale(1); }
}

.correct-flash {
  animation: correctFlash 0.5s ease-out forwards !important;
  color: #14532D !important;
}

/* Wrong shake */
@keyframes wrongShake {
  0%  { transform: translateX(0); background: #FCA5A5; }
  20% { transform: translateX(-12px); background: #F87171; }
  40% { transform: translateX(12px); }
  60% { transform: translateX(-8px); }
  80% { transform: translateX(8px); }
  100%{ transform: translateX(0); background: #FECACA; }
}

.wrong-shake {
  animation: wrongShake 0.5s ease-out forwards !important;
  color: #7F1D1D !important;
}

/* Feedback Overlay */
.feedback-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255,255,255,0.95);
  border-radius: 30px;
  padding: 30px 50px;
  text-align: center;
  z-index: 50;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
  pointer-events: none;
}

.feedback-overlay.correct {
  border: 4px solid #4ADE80;
}
.feedback-overlay.wrong {
  border: 4px solid #F87171;
}

.feedback-icon {
  font-size: 60px;
  line-height: 1;
  margin-bottom: 10px;
}

.feedback-text {
  font-size: 22px;
  font-weight: 800;
  color: #1F2937;
}

.feedback-fade-enter-active,
.feedback-fade-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.feedback-fade-enter-from,
.feedback-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.7);
}

/* Result Screen */
.result-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 30px 20px;
  text-align: center;
}

.result-stars {
  display: flex;
  gap: 10px;
  font-size: 60px;
}

.big-star {
  display: inline-block;
  filter: grayscale(1) opacity(0.3);
  transition: all 0.4s;
}

.big-star.lit {
  filter: none;
  animation: starPop 0.5s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
}

@keyframes starPop {
  0%  { transform: scale(0); }
  60% { transform: scale(1.3); }
  100%{ transform: scale(1); }
}

.result-title {
  font-size: 48px;
  font-weight: 900;
  color: #7C3AED;
  text-shadow: 3px 3px 0 rgba(124,58,237,0.2);
}

.result-score {
  font-size: 28px;
  font-weight: 700;
  color: #374151;
}

.score-num {
  font-size: 52px;
  font-weight: 900;
  color: #F59E0B;
}

.reward-badge {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 3px solid #F59E0B;
  border-radius: 30px;
  padding: 14px 30px;
  color: #92400E;
  box-shadow: 0 4px 15px rgba(245,158,11,0.3);
}

.result-message {
  font-size: 22px;
  font-weight: 700;
  color: #6B7280;
}

.result-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.btn-retry, .btn-home {
  font-size: 20px;
  font-weight: 800;
  padding: 16px 32px;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  transition: transform 0.12s, box-shadow 0.12s;
  box-shadow: 0 5px 0 rgba(0,0,0,0.15);
}

.btn-retry {
  background: linear-gradient(135deg, #A855F7, #7C3AED);
  color: white;
}

.btn-home {
  background: linear-gradient(135deg, #F97316, #EA580C);
  color: white;
}

.btn-retry:hover, .btn-home:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 0 rgba(0,0,0,0.15);
}

/* Confetti */
.confetti-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 5;
  overflow: hidden;
}

@keyframes confettiFall {
  0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
  100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
}

.confetti-piece {
  position: absolute;
  top: -20px;
  animation: confettiFall 2.5s ease-in forwards;
  animation-iteration-count: infinite;
}

/* Mobile responsive */
@media (max-width: 480px) {
  .question-letter {
    font-size: 100px;
  }
  .answer-btn {
    font-size: 56px;
    padding: 15px 5px;
  }
  .answers-grid {
    gap: 12px;
  }
  .result-title {
    font-size: 36px;
  }
  .score-num {
    font-size: 42px;
  }
}
</style>
