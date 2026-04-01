<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[480px] mx-auto px-4 pt-4">
      <div class="flex items-center justify-between mb-4">
        <button @click="$router.push('/games')" class="text-sm text-gray-500 hover:text-gray-700 transition">← 목록</button>
        <h1 class="text-xl font-black text-gray-800">🔡 한국어 워들</h1>
        <button @click="newGame" class="text-xs text-indigo-500 hover:text-indigo-700 font-semibold border border-indigo-200 px-3 py-1.5 rounded-lg">새 게임</button>
      </div>

      <div class="bg-white rounded-2xl shadow-sm p-5 mb-4">
        <!-- 게임 그리드 -->
        <div class="flex flex-col gap-1.5 mb-5">
          <div v-for="(row, ri) in board" :key="ri" class="flex gap-1.5 justify-center">
            <div v-for="(cell, ci) in row" :key="ci"
              class="w-12 h-12 flex items-center justify-center text-xl font-black rounded-xl border-2 transition-all duration-300"
              :class="getCellClass(ri, ci)">
              {{ cell }}
            </div>
          </div>
        </div>

        <!-- 결과 메시지 -->
        <div v-if="gameState !== 'playing'" class="text-center py-4 mb-4 rounded-2xl"
          :class="gameState === 'won' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
          <div class="text-2xl font-black mb-1" :class="gameState === 'won' ? 'text-green-700' : 'text-red-600'">
            {{ gameState === 'won' ? '🎉 정답!' : '😢 아쉬워요' }}
          </div>
          <div class="text-sm text-gray-500 mb-1">정답: <strong class="text-lg">{{ answer }}</strong></div>
          <div v-if="gameState === 'won'" class="text-xs text-green-500 mb-3">+30 🪙 COIN 획득!</div>
          <button @click="newGame" class="bg-indigo-500 hover:bg-indigo-600 text-white px-5 py-2 rounded-xl text-sm font-bold transition">
            새 게임
          </button>
        </div>

        <!-- 현재 입력 표시 -->
        <div v-if="gameState === 'playing'" class="flex gap-1.5 justify-center mb-3">
          <div v-for="(_, i) in 5" :key="i"
            class="w-12 h-12 flex items-center justify-center text-xl font-black rounded-xl border-2 border-indigo-200 transition-all"
            :class="currentInput[i] ? 'bg-indigo-50 text-indigo-700 border-indigo-400' : 'bg-white text-transparent'">
            {{ currentInput[i] || '_' }}
          </div>
        </div>

        <!-- 힌트 -->
        <div class="text-center text-xs text-gray-400 space-x-4">
          <span><span class="inline-block w-3 h-3 bg-green-500 rounded mr-1"></span>정확한 위치</span>
          <span><span class="inline-block w-3 h-3 bg-yellow-400 rounded mr-1"></span>다른 위치</span>
          <span><span class="inline-block w-3 h-3 bg-gray-300 rounded mr-1"></span>없음</span>
        </div>
      </div>

      <!-- 키보드 -->
      <div class="bg-white rounded-2xl shadow-sm p-3">
        <div v-for="(row, ri) in keyboard" :key="ri" class="flex gap-1 justify-center mb-1.5">
          <button v-for="key in row" :key="key"
            @click="typeKey(key)"
            class="px-2 py-3 rounded-lg text-xs font-bold transition min-w-[28px] text-center"
            :class="getKeyClass(key)">
            {{ key }}
          </button>
        </div>
        <div class="flex gap-2 justify-center mt-1">
          <button @click="deleteLast"
            class="px-4 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg text-sm font-bold transition">
            ⌫ 지우기
          </button>
          <button @click="submitGuess" :disabled="currentInput.length !== 5"
            class="px-6 py-3 bg-indigo-500 hover:bg-indigo-600 disabled:opacity-40 text-white rounded-lg text-sm font-bold transition">
            입력 ↵
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const WORDS = [
  '김치찌개', '불고기밥', '비빔냉면', '떡볶이집', '삼겹살집',
  '순두부찌', '갈비탕밥', '된장찌개', '잡채볶음', '제육볶음',
  '오징어볶', '닭갈비볶', '부대찌개', '감자탕집', '해물파전',
  '빈대떡집', '순대국밥', '설렁탕집', '곰탕국밥', '삼계탕집',
  '돼지국밥', '족발보쌈', '냉면집의', '막국수집', '칼국수집'
]

const keyboard = [
  ['ㅂ','ㅈ','ㄷ','ㄱ','ㅅ','ㅛ','ㅕ','ㅑ','ㅐ','ㅔ'],
  ['ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ'],
  ['ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ'],
]

const answer = ref(WORDS[Math.floor(Math.random() * WORDS.length)])
const board = ref(Array(6).fill(null).map(() => Array(5).fill('')))
const results = ref(Array(6).fill(null).map(() => Array(5).fill('')))
const currentRow = ref(0)
const currentInput = ref('')
const gameState = ref('playing')
const usedKeys = reactive({})

function submitGuess() {
  const g = currentInput.value
  if (g.length !== 5 || currentRow.value >= 6 || gameState.value !== 'playing') return
  const row = currentRow.value
  const ans = answer.value
  const res = Array(5).fill('absent')
  const ansArr = ans.split('')
  const gArr = g.split('')
  gArr.forEach((ch, i) => { if (ch === ansArr[i]) { res[i] = 'correct'; ansArr[i] = null } })
  gArr.forEach((ch, i) => {
    if (res[i] === 'correct') return
    const idx = ansArr.indexOf(ch)
    if (idx !== -1) { res[i] = 'present'; ansArr[idx] = null }
  })
  board.value[row] = gArr
  results.value[row] = res
  gArr.forEach((ch, i) => {
    const cur = usedKeys[ch]
    if (res[i] === 'correct') usedKeys[ch] = 'correct'
    else if (res[i] === 'present' && cur !== 'correct') usedKeys[ch] = 'present'
    else if (!cur) usedKeys[ch] = 'absent'
  })
  if (g === ans) { gameState.value = 'won' }
  else if (row === 5) { gameState.value = 'lost' }
  currentRow.value++
  currentInput.value = ''
}

function typeKey(k) { if (currentInput.value.length < 5 && gameState.value === 'playing') currentInput.value += k }
function deleteLast() { currentInput.value = currentInput.value.slice(0, -1) }

function getCellClass(ri, ci) {
  const r = results.value[ri][ci]
  if (!board.value[ri][ci] && ri === currentRow.value) return 'border-gray-200 bg-white'
  if (!r && board.value[ri][ci]) return 'border-gray-200 bg-gray-50 text-gray-400'
  if (r === 'correct') return 'border-green-500 bg-green-500 text-white shadow-sm'
  if (r === 'present') return 'border-yellow-400 bg-yellow-400 text-white shadow-sm'
  if (r === 'absent') return 'border-gray-200 bg-gray-100 text-gray-400'
  return 'border-gray-200 bg-white text-gray-800'
}

function getKeyClass(k) {
  const s = usedKeys[k]
  if (s === 'correct') return 'bg-green-500 text-white'
  if (s === 'present') return 'bg-yellow-400 text-white'
  if (s === 'absent') return 'bg-gray-200 text-gray-400'
  return 'bg-gray-100 text-gray-700 hover:bg-gray-200'
}

function newGame() {
  answer.value = WORDS[Math.floor(Math.random() * WORDS.length)]
  board.value = Array(6).fill(null).map(() => Array(5).fill(''))
  results.value = Array(6).fill(null).map(() => Array(5).fill(''))
  currentRow.value = 0; currentInput.value = ''; gameState.value = 'playing'
  Object.keys(usedKeys).forEach(k => delete usedKeys[k])
}
</script>
