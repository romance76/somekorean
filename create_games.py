#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko, base64, sys

def log(msg):
    sys.stdout.buffer.write((str(msg) + '\n').encode('utf-8'))
    sys.stdout.buffer.flush()

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)

def ssh(cmd, timeout=60):
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

def write_file(path, content):
    enc = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunk_size = 2000
    chunks = [enc[i:i+chunk_size] for i in range(0, len(enc), chunk_size)]
    ssh("rm -f /tmp/wf_chunk")
    for p in chunks:
        ssh(f"printf '%s' '{p}' >> /tmp/wf_chunk")
    ssh(f"cat /tmp/wf_chunk | base64 -d > {path} && rm -f /tmp/wf_chunk")
    size = ssh(f"wc -c < {path}")
    log(f"Written {path} ({size} bytes)")

# ===== GameCarJump.vue =====
car_jump = '''<template>
  <div class="min-h-screen bg-gray-900 flex flex-col items-center justify-center px-4">
    <div class="w-full max-w-[600px]">
      <div class="flex items-center justify-between mb-4 text-white">
        <button @click="$router.push('/games')" class="text-sm text-gray-400 hover:text-white transition">← 게임 목록</button>
        <h1 class="text-xl font-black">🚗 자동차 점프</h1>
        <div class="text-sm text-yellow-400 font-bold">점수: {{ score }}</div>
      </div>

      <canvas ref="canvas" class="w-full rounded-2xl cursor-pointer outline-none"
        style="height:200px;background:#87CEEB"
        @click="jump" tabindex="0"></canvas>

      <div v-if="gameOver" class="text-center mt-6">
        <div class="text-white text-3xl font-black mb-2">게임 오버!</div>
        <div class="text-yellow-400 text-xl mb-2">점수: {{ score }}</div>
        <div class="text-gray-300 text-sm mb-4">최고 기록: {{ bestScore }}</div>
        <div v-if="score >= 10" class="text-green-400 text-sm mb-4">+{{ Math.floor(score/5) }} 💎 GEM 획득!</div>
        <button @click="startGame" class="bg-indigo-500 hover:bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold text-lg transition">
          다시 시작
        </button>
      </div>

      <div v-if="!started && !gameOver" class="text-center mt-6">
        <p class="text-gray-300 text-sm mb-4">🖱️ 클릭 또는 스페이스바로 점프!</p>
        <button @click="startGame" class="bg-indigo-500 hover:bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold text-lg transition">
          게임 시작
        </button>
      </div>

      <div v-if="started && !gameOver" class="text-center mt-4">
        <p class="text-gray-500 text-xs">클릭 또는 스페이스바로 점프</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from \'vue\'

const canvas = ref(null)
const score = ref(0)
const bestScore = ref(parseInt(localStorage.getItem(\'carjump_best\') || \'0\'))
const gameOver = ref(false)
const started = ref(false)

let ctx, animId, frame, speed, obstacles, car

function initGame() {
  frame = 0; speed = 4; obstacles = []
  car = { x: 80, y: 0, w: 50, h: 28, vy: 0, onGround: true }
  score.value = 0; gameOver.value = false
}

function startGame() {
  initGame()
  started.value = true
  if (canvas.value) canvas.value.focus()
  cancelAnimationFrame(animId)
  loop()
}

function jump() {
  if (!started.value) { startGame(); return }
  if (gameOver.value) { startGame(); return }
  if (car && car.onGround) { car.vy = -13; car.onGround = false }
}

function loop() {
  if (!canvas.value) return
  ctx = canvas.value.getContext(\'2d\')
  const W = canvas.value.offsetWidth
  const H = 200
  canvas.value.width = W
  canvas.value.height = H
  const groundY = H * 0.78

  ctx.clearRect(0, 0, W, H)

  // Sky gradient
  const sky = ctx.createLinearGradient(0, 0, 0, groundY)
  sky.addColorStop(0, \'#87CEEB\')
  sky.addColorStop(1, \'#B0E2FF\')
  ctx.fillStyle = sky
  ctx.fillRect(0, 0, W, groundY)

  // Ground
  ctx.fillStyle = \'#8B6914\'
  ctx.fillRect(0, groundY, W, H - groundY)
  ctx.fillStyle = \'#4CAF50\'
  ctx.fillRect(0, groundY - 6, W, 8)

  // Physics
  car.vy += 0.65
  car.y += car.vy
  if (car.y >= groundY - car.h) {
    car.y = groundY - car.h
    car.vy = 0
    car.onGround = true
  }

  // Draw car
  ctx.fillStyle = \'#EF4444\'
  ctx.beginPath()
  ctx.roundRect(car.x, car.y, car.w, car.h * 0.7, 4)
  ctx.fill()
  ctx.fillStyle = \'#DC2626\'
  ctx.fillRect(car.x + 8, car.y + car.h * 0.7, car.w - 16, car.h * 0.3)
  // Wheels
  ctx.fillStyle = \'#1F2937\'
  ctx.beginPath(); ctx.arc(car.x + 14, car.y + car.h, 7, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.arc(car.x + car.w - 14, car.y + car.h, 7, 0, Math.PI * 2); ctx.fill()
  ctx.fillStyle = \'#4B5563\'
  ctx.beginPath(); ctx.arc(car.x + 14, car.y + car.h, 3, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.arc(car.x + car.w - 14, car.y + car.h, 3, 0, Math.PI * 2); ctx.fill()

  // Obstacles
  frame++
  speed = 4 + Math.floor(frame / 300) * 0.8
  const spawnInterval = Math.max(55, 110 - Math.floor(frame / 200) * 5)
  if (frame % spawnInterval === 0) {
    const h = 30 + Math.floor(Math.random() * 25)
    obstacles.push({ x: W + 10, y: groundY - h, w: 18, h })
  }

  for (let i = obstacles.length - 1; i >= 0; i--) {
    obstacles[i].x -= speed
    // Draw cactus-like obstacle
    ctx.fillStyle = \'#F59E0B\'
    ctx.fillRect(obstacles[i].x, obstacles[i].y, obstacles[i].w, obstacles[i].h)
    ctx.fillStyle = \'#D97706\'
    ctx.fillRect(obstacles[i].x + 4, obstacles[i].y - 8, obstacles[i].w - 8, 8)
    if (obstacles[i].x + obstacles[i].w < 0) {
      obstacles.splice(i, 1)
      score.value++
      continue
    }
    // Collision detection
    const margin = 6
    if (car.x + margin < obstacles[i].x + obstacles[i].w &&
        car.x + car.w - margin > obstacles[i].x &&
        car.y + margin < obstacles[i].y + obstacles[i].h &&
        car.y + car.h - margin > obstacles[i].y) {
      endGame(); return
    }
  }

  // Score display
  ctx.fillStyle = \'rgba(0,0,0,0.5)\'
  ctx.fillRect(8, 8, 90, 28)
  ctx.fillStyle = \'#FFF\'
  ctx.font = \'bold 16px sans-serif\'
  ctx.fillText(\'점수: \' + score.value, 16, 26)

  animId = requestAnimationFrame(loop)
}

function endGame() {
  cancelAnimationFrame(animId)
  gameOver.value = true
  if (score.value > bestScore.value) {
    bestScore.value = score.value
    localStorage.setItem(\'carjump_best\', score.value)
  }
}

function handleKey(e) {
  if (e.code === \'Space\') { e.preventDefault(); jump() }
}

onMounted(() => { window.addEventListener(\'keydown\', handleKey) })
onUnmounted(() => { window.removeEventListener(\'keydown\', handleKey); cancelAnimationFrame(animId) })
</script>
'''

# ===== GameNumberMemory.vue =====
num_memory = '''<template>
  <div class="min-h-screen bg-purple-50 flex flex-col items-center justify-center px-4 pb-20">
    <div class="w-full max-w-[480px]">
      <div class="flex items-center justify-between mb-6">
        <button @click="$router.push(\'/games\')" class="text-sm text-purple-400 hover:text-purple-600 transition">← 게임 목록</button>
        <h1 class="text-xl font-black text-purple-800">🔢 숫자 기억하기</h1>
        <div class="text-sm font-bold text-purple-600 bg-purple-100 px-3 py-1 rounded-full">Lv.{{ level }}</div>
      </div>

      <div class="bg-white rounded-3xl shadow-lg p-8 text-center mb-4">

        <!-- 시작 화면 -->
        <div v-if="phase === \'start\'">
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
        <div v-if="phase === \'show\'" class="py-4">
          <p class="text-gray-400 text-sm mb-6">이 숫자를 기억하세요!</p>
          <div class="text-6xl font-black text-purple-600 tracking-[0.2em] mb-8">{{ currentNumber }}</div>
          <div class="h-3 bg-gray-100 rounded-full overflow-hidden">
            <div class="h-full bg-purple-400 rounded-full transition-all duration-100" :style="{width: timerPct + \'%\'}"></div>
          </div>
          <p class="text-xs text-gray-300 mt-2">{{ Math.ceil(timeLeft / 1000) }}초</p>
        </div>

        <!-- 입력 단계 -->
        <div v-if="phase === \'input\'">
          <p class="text-gray-500 text-sm mb-6 font-medium">방금 본 숫자를 입력하세요</p>
          <input v-model="userInput" type="tel"
            class="w-full text-center text-5xl font-black border-2 rounded-2xl px-4 py-5 focus:outline-none tracking-[0.2em] transition"
            :class="userInput.length > 0 ? \'border-purple-400 text-purple-700\' : \'border-gray-200 text-gray-400\'"
            placeholder="?" @keyup.enter="checkAnswer" autofocus />
          <button @click="checkAnswer" :disabled="userInput.length === 0"
            class="mt-4 w-full bg-purple-500 hover:bg-purple-600 disabled:opacity-40 text-white py-4 rounded-2xl font-bold text-lg transition">
            확인
          </button>
        </div>

        <!-- 결과 단계 -->
        <div v-if="phase === \'result\'" class="py-2">
          <div class="text-6xl mb-3">{{ lastCorrect ? \'✅\' : \'❌\' }}</div>
          <p class="text-xl font-black mb-2" :class="lastCorrect ? \'text-green-600\' : \'text-red-500\'">
            {{ lastCorrect ? \'정답!' : \'틀렸어요\' }}
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
            :class="lastCorrect ? \'bg-green-500 hover:bg-green-600 text-white\' : \'bg-purple-500 hover:bg-purple-600 text-white\'">
            {{ lastCorrect ? \'다음 단계 →\' : \'다시 시작\' }}
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
import { ref } from \'vue\'

const phase = ref(\'start\')
const level = ref(1)
const score = ref(0)
const bestScore = ref(parseInt(localStorage.getItem(\'numbermem_best\') || \'0\'))
const currentNumber = ref(\'\')
const userInput = ref(\'\')
const lastCorrect = ref(false)
const timerPct = ref(100)
const timeLeft = ref(3000)

let timerInterval

function getDigits() { return Math.min(2 + level.value, 9) }

function generateNumber() {
  const d = getDigits()
  let n = \'\'
  for (let i = 0; i < d; i++) n += i === 0 ? String(1 + Math.floor(Math.random() * 9)) : String(Math.floor(Math.random() * 10))
  return n
}

function startGame() { level.value = 1; score.value = 0; showNumber() }

function showNumber() {
  currentNumber.value = generateNumber()
  userInput.value = \'\'
  phase.value = \'show\'
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
      phase.value = \'input\'
      setTimeout(() => { const inp = document.querySelector(\'input[type=tel]\'); if (inp) inp.focus() }, 100)
    }
  }, 50)
}

function checkAnswer() {
  clearInterval(timerInterval)
  lastCorrect.value = userInput.value.trim() === currentNumber.value
  if (lastCorrect.value) { score.value += level.value * 10; level.value++ }
  phase.value = \'result\'
}

function nextRound() {
  if (!lastCorrect.value) {
    if (score.value > bestScore.value) {
      bestScore.value = score.value
      localStorage.setItem(\'numbermem_best\', score.value)
    }
    level.value = 1; score.value = 0
  }
  showNumber()
}
</script>
'''

# ===== GameWordle.vue =====
wordle = '''<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <div class="max-w-[480px] mx-auto px-4 pt-4">
      <div class="flex items-center justify-between mb-4">
        <button @click="$router.push(\'/games\')" class="text-sm text-gray-500 hover:text-gray-700 transition">← 목록</button>
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
        <div v-if="gameState !== \'playing\'" class="text-center py-4 mb-4 rounded-2xl"
          :class="gameState === \'won\' ? \'bg-green-50 border border-green-200\' : \'bg-red-50 border border-red-200\'">
          <div class="text-2xl font-black mb-1" :class="gameState === \'won\' ? \'text-green-700\' : \'text-red-600\'">
            {{ gameState === \'won\' ? \'🎉 정답!' : \'😢 아쉬워요\' }}
          </div>
          <div class="text-sm text-gray-500 mb-1">정답: <strong class="text-lg">{{ answer }}</strong></div>
          <div v-if="gameState === \'won\'" class="text-xs text-green-500 mb-3">+30 🪙 COIN 획득!</div>
          <button @click="newGame" class="bg-indigo-500 hover:bg-indigo-600 text-white px-5 py-2 rounded-xl text-sm font-bold transition">
            새 게임
          </button>
        </div>

        <!-- 현재 입력 표시 -->
        <div v-if="gameState === \'playing\'" class="flex gap-1.5 justify-center mb-3">
          <div v-for="(_, i) in 5" :key="i"
            class="w-12 h-12 flex items-center justify-center text-xl font-black rounded-xl border-2 border-indigo-200 transition-all"
            :class="currentInput[i] ? \'bg-indigo-50 text-indigo-700 border-indigo-400\' : \'bg-white text-transparent\'">
            {{ currentInput[i] || \'_\' }}
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
import { ref, reactive } from \'vue\'

const WORDS = [
  \'김치찌개\', \'불고기밥\', \'비빔냉면\', \'떡볶이집\', \'삼겹살집\',
  \'순두부찌\', \'갈비탕밥\', \'된장찌개\', \'잡채볶음\', \'제육볶음\',
  \'오징어볶\', \'닭갈비볶\', \'부대찌개\', \'감자탕집\', \'해물파전\',
  \'빈대떡집\', \'순대국밥\', \'설렁탕집\', \'곰탕국밥\', \'삼계탕집\',
  \'돼지국밥\', \'족발보쌈\', \'냉면집의\', \'막국수집\', \'칼국수집\'
]

const keyboard = [
  [\'ㅂ\',\'ㅈ\',\'ㄷ\',\'ㄱ\',\'ㅅ\',\'ㅛ\',\'ㅕ\',\'ㅑ\',\'ㅐ\',\'ㅔ\'],
  [\'ㅁ\',\'ㄴ\',\'ㅇ\',\'ㄹ\',\'ㅎ\',\'ㅗ\',\'ㅓ\',\'ㅏ\',\'ㅣ\'],
  [\'ㅋ\',\'ㅌ\',\'ㅊ\',\'ㅍ\',\'ㅠ\',\'ㅜ\',\'ㅡ\'],
]

const answer = ref(WORDS[Math.floor(Math.random() * WORDS.length)])
const board = ref(Array(6).fill(null).map(() => Array(5).fill(\'\')))
const results = ref(Array(6).fill(null).map(() => Array(5).fill(\'\')))
const currentRow = ref(0)
const currentInput = ref(\'\')
const gameState = ref(\'playing\')
const usedKeys = reactive({})

function submitGuess() {
  const g = currentInput.value
  if (g.length !== 5 || currentRow.value >= 6 || gameState.value !== \'playing\') return
  const row = currentRow.value
  const ans = answer.value
  const res = Array(5).fill(\'absent\')
  const ansArr = ans.split(\'\')
  const gArr = g.split(\'\')
  gArr.forEach((ch, i) => { if (ch === ansArr[i]) { res[i] = \'correct\'; ansArr[i] = null } })
  gArr.forEach((ch, i) => {
    if (res[i] === \'correct\') return
    const idx = ansArr.indexOf(ch)
    if (idx !== -1) { res[i] = \'present\'; ansArr[idx] = null }
  })
  board.value[row] = gArr
  results.value[row] = res
  gArr.forEach((ch, i) => {
    const cur = usedKeys[ch]
    if (res[i] === \'correct\') usedKeys[ch] = \'correct\'
    else if (res[i] === \'present\' && cur !== \'correct\') usedKeys[ch] = \'present\'
    else if (!cur) usedKeys[ch] = \'absent\'
  })
  if (g === ans) { gameState.value = \'won\' }
  else if (row === 5) { gameState.value = \'lost\' }
  currentRow.value++
  currentInput.value = \'\'
}

function typeKey(k) { if (currentInput.value.length < 5 && gameState.value === \'playing\') currentInput.value += k }
function deleteLast() { currentInput.value = currentInput.value.slice(0, -1) }

function getCellClass(ri, ci) {
  const r = results.value[ri][ci]
  if (!board.value[ri][ci] && ri === currentRow.value) return \'border-gray-200 bg-white\'
  if (!r && board.value[ri][ci]) return \'border-gray-200 bg-gray-50 text-gray-400\'
  if (r === \'correct\') return \'border-green-500 bg-green-500 text-white shadow-sm\'
  if (r === \'present\') return \'border-yellow-400 bg-yellow-400 text-white shadow-sm\'
  if (r === \'absent\') return \'border-gray-200 bg-gray-100 text-gray-400\'
  return \'border-gray-200 bg-white text-gray-800\'
}

function getKeyClass(k) {
  const s = usedKeys[k]
  if (s === \'correct\') return \'bg-green-500 text-white\'
  if (s === \'present\') return \'bg-yellow-400 text-white\'
  if (s === \'absent\') return \'bg-gray-200 text-gray-400\'
  return \'bg-gray-100 text-gray-700 hover:bg-gray-200\'
}

function newGame() {
  answer.value = WORDS[Math.floor(Math.random() * WORDS.length)]
  board.value = Array(6).fill(null).map(() => Array(5).fill(\'\'))
  results.value = Array(6).fill(null).map(() => Array(5).fill(\'\'))
  currentRow.value = 0; currentInput.value = \'\'; gameState.value = \'playing\'
  Object.keys(usedKeys).forEach(k => delete usedKeys[k])
}
</script>
'''

# Write game files
write_file('/var/www/somekorean/resources/js/pages/games/GameCarJump.vue', car_jump)
write_file('/var/www/somekorean/resources/js/pages/games/GameNumberMemory.vue', num_memory)
write_file('/var/www/somekorean/resources/js/pages/games/GameWordle.vue', wordle)

# Check GameLobby.vue - was it updated?
log("\n=== GameLobby.vue check ===")
lobby_check = ssh("grep -c 'ageTabs\\|age_group\\|game-categories' /var/www/somekorean/resources/js/pages/games/GameLobby.vue 2>/dev/null")
log(f"Age tabs references in GameLobby: {lobby_check}")

log("\n=== Running build ===")
build_out = ssh("cd /var/www/somekorean && npm run build 2>&1", timeout=120)
log(build_out[-800:] if len(build_out) > 800 else build_out)

log("\n=== Cache clear ===")
log(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:clear && php artisan route:cache 2>&1"))

log("\n=== API Tests ===")
log("game-categories: " + ssh("curl -sk https://somekorean.com/api/game-categories | python3 -c \"import sys,json; d=json.load(sys.stdin); print(len(d), 'categories,', sum(len(c.get('games',[])) for c in d), 'games')\" 2>&1"))
log("QA: " + ssh("curl -sk 'https://somekorean.com/api/qa?page=1' | python3 -c \"import sys,json; d=json.load(sys.stdin); print('total:', d.get('total'), 'user sample:', d.get('data',[{}])[0].get('user',{}).get('nickname','?'))\" 2>&1"))
log("Recipe detail: " + ssh("curl -sk https://somekorean.com/api/recipes/1 | python3 -c \"import sys,json; d=json.load(sys.stdin); print('related:', len(d.get('related',[])), 'avg_rating:', d.get('avg_rating'), 'comments:', d.get('comment_count'))\" 2>&1"))

c.close()
log("\nAll done!")
