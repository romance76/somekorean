<template>
  <div class="maze-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🌀</div>
      <div class="score">⭐ {{ score }}</div>
    </div>

    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🌀</div>
      <h1 class="title">미로 탈출</h1>
      <p class="subtitle">방향키 또는 버튼으로 캐릭터를 탈출구까지 이동!</p>
      <div class="level-info">현재 레벨: {{ level }}</div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>

    <div v-if="phase==='play'" class="play-area">
      <div class="game-info-row">
        <div class="steps-display">👣 {{ steps }}걸음</div>
        <div class="timer-display">⏱ {{ timeLeft }}초</div>
        <div class="best-display">🏆 최단 {{ bestSteps || '??' }}걸음</div>
      </div>
      <div class="maze-wrapper">
        <div class="maze-grid" :style="mazeStyle">
          <div v-for="(row, r) in maze" :key="r" class="maze-row">
            <div v-for="(cell, col) in row" :key="col" class="maze-cell"
              :class="getCellClass(r, col)">
              <span v-if="r===playerR && col===playerC" class="player">🐸</span>
              <span v-else-if="r===exitR && col===exitC" class="exit-mark">🚪</span>
            </div>
          </div>
        </div>
      </div>
      <div class="dpad">
        <button class="dpad-btn" @click="move(-1,0)">↑</button>
        <div class="dpad-row">
          <button class="dpad-btn" @click="move(0,-1)">←</button>
          <div class="dpad-center">🐸</div>
          <button class="dpad-btn" @click="move(0,1)">→</button>
        </div>
        <button class="dpad-btn" @click="move(1,0)">↓</button>
      </div>
    </div>

    <div v-if="phase==='cleared'" class="cleared-box">
      <div style="font-size:80px">🎊</div>
      <h2 class="cleared-title">탈출 성공!</h2>
      <div class="cleared-stats">{{ steps }}걸음 · {{ elapsedTime }}초</div>
      <div v-if="isNewBest" class="new-best">🏆 새 기록!</div>
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

const level = ref(parseInt(localStorage.getItem('maze_level') || '1'))
const score = ref(parseInt(localStorage.getItem('maze_score') || '0'))
const bestSteps = ref(parseInt(localStorage.getItem('maze_best') || '0') || null)

const phase = ref('start')
const maze = ref([])
const playerR = ref(1)
const playerC = ref(1)
const exitR = ref(0)
const exitC = ref(0)
const steps = ref(0)
const timeLeft = ref(60)
const elapsedTime = ref(0)
const isNewBest = ref(false)
const leveled = ref(false)
let timer = null
let startTime = null

function getMazeSize() {
  const base = 7 + Math.min((level.value - 1) * 2, 10)
  return base % 2 === 0 ? base + 1 : base
}

const mazeStyle = computed(() => {
  const s = getMazeSize()
  const cellSize = Math.min(36, Math.floor(320 / s))
  return { '--cell': cellSize + 'px' }
})

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.9; u.pitch = 1.1
  window.speechSynthesis.speak(u)
}

function generateMaze(size) {
  const grid = Array.from({length: size}, () => Array(size).fill(1))
  function carve(r, c) {
    const dirs = [[0,2],[0,-2],[2,0],[-2,0]].sort(()=>Math.random()-0.5)
    grid[r][c] = 0
    for (const [dr, dc] of dirs) {
      const nr = r+dr, nc = c+dc
      if (nr>0 && nr<size-1 && nc>0 && nc<size-1 && grid[nr][nc]===1) {
        grid[r+dr/2][c+dc/2] = 0
        carve(nr, nc)
      }
    }
  }
  carve(1, 1)
  return grid
}

function startGame() {
  const size = getMazeSize()
  maze.value = generateMaze(size)
  playerR.value = 1; playerC.value = 1
  exitR.value = size - 2; exitC.value = size - 2
  steps.value = 0; isNewBest.value = false; leveled.value = false
  startTime = Date.now()
  timeLeft.value = level.value <= 2 ? 120 : level.value <= 4 ? 90 : 60
  phase.value = 'play'
  clearInterval(timer)
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      speak('시간 초과!')
      phase.value = 'cleared'
      elapsedTime.value = Math.round((Date.now() - startTime) / 1000)
    }
  }, 1000)
  speak('출발!')
}

function getCellClass(r, c) {
  if (maze.value[r]?.[c] === 1) return 'wall'
  if (r === exitR.value && c === exitC.value) return 'exit'
  return 'path'
}

function move(dr, dc) {
  if (phase.value !== 'play') return
  const nr = playerR.value + dr, nc = playerC.value + dc
  if (nr < 0 || nr >= maze.value.length || nc < 0 || nc >= maze.value[0].length) return
  if (maze.value[nr][nc] === 1) return
  playerR.value = nr; playerC.value = nc; steps.value++
  if (nr === exitR.value && nc === exitC.value) {
    clearInterval(timer)
    elapsedTime.value = Math.round((Date.now() - startTime) / 1000)
    const pts = Math.max(50, 200 - steps.value * 2 + timeLeft.value)
    score.value += pts
    localStorage.setItem('maze_score', score.value)
    if (!bestSteps.value || steps.value < bestSteps.value) {
      bestSteps.value = steps.value
      localStorage.setItem('maze_best', steps.value)
      isNewBest.value = true
    }
    const threshold = level.value <= 2 ? 3 : level.value <= 4 ? 5 : 7
    if (steps.value <= getMazeSize() * threshold) {
      level.value++
      localStorage.setItem('maze_level', level.value)
      leveled.value = true
    }
    phase.value = 'cleared'
    speak(leveled.value ? '탈출 성공! 레벨업!' : '탈출 성공!')
  }
}

function handleKey(e) {
  const map = {ArrowUp:[-1,0], ArrowDown:[1,0], ArrowLeft:[0,-1], ArrowRight:[0,1]}
  if (map[e.key]) { e.preventDefault(); move(...map[e.key]) }
}

function goBack() { clearInterval(timer); router.push('/games') }
onMounted(() => window.addEventListener('keydown', handleKey))
onUnmounted(() => { clearInterval(timer); window.removeEventListener('keydown', handleKey) })
</script>

<style scoped>
.maze-game { min-height:100vh; background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.7); font-size:15px; }
.level-info { color:#60a5fa; margin:10px 0; font-size:15px; }
.start-btn { background:#6366f1; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:400px; margin:0 auto; }
.game-info-row { display:flex; justify-content:space-between; margin-bottom:12px; }
.steps-display,.timer-display,.best-display { color:#fff; font-size:13px; font-weight:600; background:rgba(255,255,255,0.1); padding:5px 10px; border-radius:10px; }
.maze-wrapper { display:flex; justify-content:center; margin-bottom:16px; overflow:auto; }
.maze-grid { display:inline-flex; flex-direction:column; border:2px solid #6366f1; border-radius:6px; overflow:hidden; }
.maze-row { display:flex; }
.maze-cell { width:var(--cell); height:var(--cell); display:flex; align-items:center; justify-content:center; font-size:calc(var(--cell) - 8px); }
.maze-cell.wall { background:#334155; }
.maze-cell.path { background:#1e293b; }
.maze-cell.exit { background:rgba(99,102,241,0.3); }
.player { font-size:calc(var(--cell) - 6px); line-height:1; }
.exit-mark { font-size:calc(var(--cell) - 8px); line-height:1; }
.dpad { display:flex; flex-direction:column; align-items:center; gap:6px; }
.dpad-row { display:flex; gap:6px; align-items:center; }
.dpad-btn { width:60px; height:60px; background:rgba(99,102,241,0.7); border:none; border-radius:50%; font-size:24px; color:#fff; cursor:pointer; display:flex; align-items:center; justify-content:center; transition:all 0.1s; }
.dpad-btn:active { transform:scale(0.92); background:#6366f1; }
.dpad-center { width:60px; height:60px; display:flex; align-items:center; justify-content:center; font-size:24px; }
.cleared-box { text-align:center; padding:40px 20px; }
.cleared-title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.cleared-stats { color:rgba(255,255,255,0.8); font-size:18px; margin:8px 0; }
.new-best { color:#fbbf24; font-size:20px; font-weight:800; margin:8px 0; }
.levelup { background:#6366f1; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#1a1a2e; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#6366f1; color:#fff; }
</style>
