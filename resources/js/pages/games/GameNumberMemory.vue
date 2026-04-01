<template>
  <div class="min-h-screen bg-purple-50 flex flex-col items-center justify-center px-4 pb-20">
    <div class="w-full max-w-[480px]">
      <div class="flex items-center justify-between mb-6">
        <button @click="$router.push('/games')" class="text-sm text-purple-400 hover:text-purple-600 transition">← 게임 목록</button>
        <h1 class="text-xl font-black text-purple-800">🔢 숫자 기억하기</h1>
        <div class="text-sm font-bold text-purple-600 bg-purple-100 px-3 py-1 rounded-full">Lv.{{ level }}</div>
      </div>

      <div class="bg-white rounded-3xl shadow-lg p-8 text-center mb-4">

        <!-- 시작 화면 -->
        <div v-if="phase === 'start'">
          <div class="text-6xl mb-4">🧠</div>
          <h2 class="text-2xl font-black text-purple-800 mb-2">숫자 기억하기</h2>
          <p class="text-gray-500 text-sm mb-6 leading-relaxed">
            숫자를 보고 기억한 뒤 그대로 입력하세요.<br/>
            단계가 올라갈수록 자릿수가 늘어납니다!
          </p>
          <div class="grid grid-cols-3 gap-3 mb-6 text-sm">
            <div class="bg-purple-50 rounded-xl p-3"><div class="font-bold text-purple-600 text-lg">Lv.1</div><div class="text-gray-400">3자리</div></div>
            <div class="bg-purple-50 rounded-xl p-3"><div class="font-bold text-purple-600 text-lg">Lv.3</div><div class="text-gray-400">5자리</div></div>
            <div class="bg-purple-50 rounded-xl p-3"><div class="font-bold text-purple-600 text-lg">Lv.5+</div><div class="text-gray-400">7자리+</div></div>
          </div>
          <button @click="startGame" class="w-full bg-purple-500 hover:bg-purple-600 text-white py-4 rounded-2xl font-bold text-lg transition">
            시작하기
          </button>
        </div>

        <!-- 숫자 표시 단계 -->
        <div v-if="phase === 'show'" class="py-4">
          <p class="text-gray-400 text-sm mb-6">이 숫자를 기억하세요!</p>
          <div class="text-6xl font-black text-purple-600 tracking-[0.2em] mb-8">{{ currentNumber }}</div>
          <div class="h-3 bg-gray-100 rounded-full overflow-hidden">
            <div class="h-full bg-purple-400 rounded-full transition-all duration-100" :style="{width: timerPct + '%'}"></div>
          </div>
          <p class="text-xs text-gray-300 mt-2">{{ Math.ceil(timeLeft / 1000) }}초</p>
        </div>

        <!-- 입력 단계 -->
        <div v-if="phase === 'input'">
          <p class="text-gray-500 text-sm mb-6 font-medium">방금 본 숫자를 입력하세요</p>
          <input v-model="userInput" type="tel"
            class="w-full text-center text-5xl font-black border-2 rounded-2xl px-4 py-5 focus:outline-none tracking-[0.2em] transition"
            :class="userInput.length > 0 ? 'border-purple-400 text-purple-700' : 'border-gray-200 text-gray-400'"
            placeholder="?" @keyup.enter="checkAnswer" autofocus />
          <button @click="checkAnswer" :disabled="userInput.length === 0"
            class="mt-4 w-full bg-purple-500 hover:bg-purple-600 disabled:opacity-40 text-white py-4 rounded-2xl font-bold text-lg transition">
            확인
          </button>
        </div>

        <!-- 결과 단계 -->
        <div v-if="phase === 'result'" class="py-2">
          <div class="text-6xl mb-3">{{ lastCorrect ? '✅' : '❌' }}</div>
          <p class="text-xl font-black mb-2" :class="lastCorrect ? 'text-green-600' : 'text-red-500'">
            {{ lastCorrect ? '정답!' : '틀렸어요' }}
          </p>
          <p v-if="!lastCorrect" class="text-gray-500 text-base mb-3">
            정답: <strong class="text-purple-600 text-xl tracking-widest">{{ currentNumber }}</strong>
          </p>
          <div class="bg-gray-50 rounded-xl px-4 py-3 mb-4 text-sm text-gray-500">
            현재 점수: <strong class="text-purple-600 text-lg">{{ score }}</strong>
            <span class="mx-2">|</span>
            최고: <strong>{{ bestScore }}</strong>
          </div>
          <button @click="nextRound"
            class="w-full py-4 rounded-2xl font-bold text-lg transition"
            :class="lastCorrect ? 'bg-green-500 hover:bg-green-600 text-white' : 'bg-purple-500 hover:bg-purple-600 text-white'">
            {{ lastCorrect ? '다음 단계 →' : '다시 시작' }}
          </button>
        </div>
      </div>

      <div v-if="score > 0 || bestScore > 0" class="text-center text-xs text-purple-300">
        +{{ score }} COIN 획득 예정 (게임 완료 시)
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const phase = ref('start')
const level = ref(1)
const score = ref(0)
const bestScore = ref(parseInt(localStorage.getItem('numbermem_best') || '0'))
const currentNumber = ref('')
const userInput = ref('')
const lastCorrect = ref(false)
const timerPct = ref(100)
const timeLeft = ref(3000)

let timerInterval

function getDigits() { return Math.min(2 + level.value, 9) }

function generateNumber() {
  const d = getDigits()
  let n = ''
  for (let i = 0; i < d; i++) n += i === 0 ? String(1 + Math.floor(Math.random() * 9)) : String(Math.floor(Math.random() * 10))
  return n
}

function startGame() { level.value = 1; score.value = 0; showNumber() }

function showNumber() {
  currentNumber.value = generateNumber()
  userInput.value = ''
  phase.value = 'show'
  timerPct.value = 100
  const duration = 2500 + level.value * 400
  timeLeft.value = duration
  const start = Date.now()
  clearInterval(timerInterval)
  timerInterval = setInterval(() => {
    const elapsed = Date.now() - start
    timeLeft.value = Math.max(0, duration - elapsed)
    timerPct.value = Math.max(0, 100 - (elapsed / duration * 100))
    if (elapsed >= duration) {
      clearInterval(timerInterval)
      phase.value = 'input'
      setTimeout(() => { const inp = document.querySelector('input[type=tel]'); if (inp) inp.focus() }, 100)
    }
  }, 50)
}

function checkAnswer() {
  clearInterval(timerInterval)
  lastCorrect.value = userInput.value.trim() === currentNumber.value
  if (lastCorrect.value) { score.value += level.value * 10; level.value++ }
  phase.value = 'result'
}

function nextRound() {
  if (!lastCorrect.value) {
    if (score.value > bestScore.value) {
      bestScore.value = score.value
      localStorage.setItem('numbermem_best', score.value)
    }
    level.value = 1; score.value = 0
  }
  showNumber()
}
</script>
