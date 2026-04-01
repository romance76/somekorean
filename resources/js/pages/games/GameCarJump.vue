<template>
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
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
const score = ref(0)
const bestScore = ref(parseInt(localStorage.getItem('carjump_best') || '0'))
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
  ctx = canvas.value.getContext('2d')
  const W = canvas.value.offsetWidth
  const H = 200
  canvas.value.width = W
  canvas.value.height = H
  const groundY = H * 0.78

  ctx.clearRect(0, 0, W, H)

  // Sky gradient
  const sky = ctx.createLinearGradient(0, 0, 0, groundY)
  sky.addColorStop(0, '#87CEEB')
  sky.addColorStop(1, '#B0E2FF')
  ctx.fillStyle = sky
  ctx.fillRect(0, 0, W, groundY)

  // Ground
  ctx.fillStyle = '#8B6914'
  ctx.fillRect(0, groundY, W, H - groundY)
  ctx.fillStyle = '#4CAF50'
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
  ctx.fillStyle = '#EF4444'
  ctx.beginPath()
  ctx.roundRect(car.x, car.y, car.w, car.h * 0.7, 4)
  ctx.fill()
  ctx.fillStyle = '#DC2626'
  ctx.fillRect(car.x + 8, car.y + car.h * 0.7, car.w - 16, car.h * 0.3)
  // Wheels
  ctx.fillStyle = '#1F2937'
  ctx.beginPath(); ctx.arc(car.x + 14, car.y + car.h, 7, 0, Math.PI * 2); ctx.fill()
  ctx.beginPath(); ctx.arc(car.x + car.w - 14, car.y + car.h, 7, 0, Math.PI * 2); ctx.fill()
  ctx.fillStyle = '#4B5563'
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
    ctx.fillStyle = '#F59E0B'
    ctx.fillRect(obstacles[i].x, obstacles[i].y, obstacles[i].w, obstacles[i].h)
    ctx.fillStyle = '#D97706'
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
  ctx.fillStyle = 'rgba(0,0,0,0.5)'
  ctx.fillRect(8, 8, 90, 28)
  ctx.fillStyle = '#FFF'
  ctx.font = 'bold 16px sans-serif'
  ctx.fillText('점수: ' + score.value, 16, 26)

  animId = requestAnimationFrame(loop)
}

function endGame() {
  cancelAnimationFrame(animId)
  gameOver.value = true
  if (score.value > bestScore.value) {
    bestScore.value = score.value
    localStorage.setItem('carjump_best', score.value)
  }
}

function handleKey(e) {
  if (e.code === 'Space') { e.preventDefault(); jump() }
}

onMounted(() => { window.addEventListener('keydown', handleKey) })
onUnmounted(() => { window.removeEventListener('keydown', handleKey); cancelAnimationFrame(animId) })
</script>
