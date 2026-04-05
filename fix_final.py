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

# Fix: game 23 (타워 디펜스) → tower-defense route, create placeholder
# Actually let's just rename game 23 to game-tower-defense and create a coming soon page
print("=== 게임 23 라우트 수정 (타워 디펜스) ===")
r = ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"UPDATE games SET route_name='game-tower-defense' WHERE id=23;\"")
print(f"ID 23 -> game-tower-defense: {r or 'OK'}")

# Create a simple Tower Defense placeholder
tower_defense = r"""<template>
  <div class="tower-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🏰</div>
      <div class="score">⭐ {{ score }}</div>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div style="font-size:80px">🏰</div>
      <h1 class="title">타워 디펜스</h1>
      <p class="subtitle">수학 문제를 풀어 적을 막아요!</p>
      <button class="start-btn" @click="startGame">시작! ⚔️</button>
    </div>
    <div v-if="phase==='play'" class="play-area">
      <div class="hud">
        <div class="hp-display">🏰 {{ hp }}HP</div>
        <div class="wave-display">웨이브 {{ wave }}</div>
        <div class="gold-display">💰 {{ gold }}</div>
      </div>
      <div class="game-area">
        <div class="enemy-lane">
          <div v-for="enemy in enemies" :key="enemy.id" class="enemy"
            :style="{left: enemy.x+'%'}">
            <div class="enemy-hp">{{ enemy.hp }}</div>
            <div class="enemy-icon">{{ enemy.icon }}</div>
          </div>
        </div>
        <div class="towers-row">
          <div v-for="(tower, i) in towers" :key="i" class="tower-slot"
            :class="{placed: tower.placed}" @click="placeTower(i)">
            {{ tower.placed ? '🗼' : '＋' }}
          </div>
        </div>
      </div>
      <div class="question-area" v-if="currentQ">
        <div class="q-text">{{ currentQ.eq }}</div>
        <div class="q-choices">
          <button v-for="opt in currentQ.opts" :key="opt" class="q-btn"
            :class="{correct: answered && opt===currentQ.ans, wrong: answered && opt===picked && opt!==currentQ.ans}"
            :disabled="answered" @click="answer(opt)">{{ opt }}</button>
        </div>
      </div>
    </div>
    <div v-if="phase==='gameover' || phase==='victory'" class="result-box">
      <div style="font-size:80px">{{ phase==='victory'?'🏆':'💀' }}</div>
      <div class="res-title">{{ phase==='victory'?'승리!':'게임오버' }}</div>
      <div class="res-detail">웨이브 {{ wave }} · {{ score }}점</div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 🔄</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()

const level = ref(parseInt(localStorage.getItem('tower_level') || '1'))
const score = ref(0)
const hp = ref(20)
const gold = ref(50)
const wave = ref(1)
const enemies = ref([])
const towers = ref(Array.from({length:5}, () => ({placed:false})))
const currentQ = ref(null)
const answered = ref(false)
const picked = ref(null)
const leveled = ref(false)
const phase = ref('start')
let gameLoop = null
let spawnTimer = null
let enemyId = 0

function speak(text) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'ko-KR'; u.rate = 0.95
  window.speechSynthesis.speak(u)
}

function rand(a, b) { return Math.floor(Math.random()*(b-a+1))+a }

function genQuestion() {
  const lv = level.value
  let a, b, op, ans
  if (lv <= 2) { a=rand(1,9); b=rand(1,9); op=Math.random()>0.5?'+':'-'; if(op==='+'){ ans=a+b } else { a=Math.max(a,b); b=Math.min(a,b); ans=a-b } }
  else { a=rand(2,9); b=rand(2,9); op='×'; ans=a*b }
  const eq = `${a} ${op} ${b} = ?`
  const wrongs = new Set()
  while(wrongs.size<3){ const w=ans+rand(-5,5); if(w!==ans&&w>0)wrongs.add(w) }
  const opts = [ans,...wrongs].sort(()=>Math.random()-0.5)
  return { eq, ans, opts }
}

function startGame() {
  hp.value=20; gold.value=50; wave.value=1; score.value=0; leveled.value=false
  enemies.value=[]; towers.value=Array.from({length:5},()=>({placed:false}))
  currentQ.value=null; answered.value=false; phase.value='play'
  speak('타워 디펜스 시작!')
  spawnWave()
}

function spawnWave() {
  const waveSize = wave.value + 2
  const speed = Math.max(0.3, 1.5 - wave.value * 0.1)
  let spawned = 0
  spawnTimer = setInterval(() => {
    if (spawned >= waveSize) { clearInterval(spawnTimer); return }
    const hp_val = wave.value + rand(1,3)
    enemies.value.push({ id: enemyId++, x: 0, hp: hp_val, maxHp: hp_val, icon: wave.value<=2?'🧟':'🐉', speed })
    spawned++
  }, 1500)
  gameLoop = setInterval(tick, 100)
  if (!currentQ.value) currentQ.value = genQuestion()
}

function tick() {
  if (phase.value !== 'play') return
  enemies.value = enemies.value.map(e => {
    const dmg = towers.value.filter(t=>t.placed).length * 0.5
    const newX = e.x + e.speed
    if (newX >= 100) { hp.value -= 1; if(hp.value<=0){endGame('gameover')}; return null }
    return {...e, x: newX}
  }).filter(Boolean)
}

function placeTower(i) {
  if (gold.value < 20) { speak('골드가 부족해요!'); return }
  if (towers.value[i].placed) return
  gold.value -= 20
  towers.value[i] = {placed: true}
  speak('타워 설치!')
}

function answer(opt) {
  if (answered.value) return
  answered.value = true; picked.value = opt
  if (opt === currentQ.value.ans) {
    score.value += 10
    const target = enemies.value[0]
    if (target) {
      target.hp -= 3
      if (target.hp <= 0) { enemies.value.shift(); gold.value += 10; wave.value++; if(wave.value>5)endGame('victory') }
    }
    speak('정답!')
  } else speak('오답!')
  setTimeout(() => { answered.value=false; picked.value=null; currentQ.value=genQuestion() }, 1200)
}

function endGame(result) {
  clearInterval(gameLoop); clearInterval(spawnTimer)
  phase.value = result
  if (result === 'victory') {
    level.value++; localStorage.setItem('tower_level', level.value); leveled.value=true
    speak('승리! 레벨업!')
  } else speak('게임 오버!')
}

function goBack() { clearInterval(gameLoop); clearInterval(spawnTimer); router.push('/games') }
onUnmounted(() => { clearInterval(gameLoop); clearInterval(spawnTimer) })
</script>

<style scoped>
.tower-game { min-height:100vh; background:linear-gradient(135deg,#052e16,#14532d,#166534); padding:16px; font-family:'Noto Sans KR',sans-serif; }
.game-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; }
.back-btn { background:rgba(255,255,255,0.15); color:#fff; border:none; padding:8px 14px; border-radius:20px; cursor:pointer; font-size:14px; }
.level-badge,.score { background:rgba(255,255,255,0.15); color:#fff; padding:6px 14px; border-radius:20px; font-weight:700; }
.center-box { text-align:center; padding:40px 20px; }
.title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.subtitle { color:rgba(255,255,255,0.8); font-size:16px; }
.start-btn { background:#22c55e; color:#fff; border:none; padding:14px 40px; border-radius:30px; font-size:20px; font-weight:800; cursor:pointer; margin-top:20px; }
.play-area { max-width:480px; margin:0 auto; }
.hud { display:flex; justify-content:space-between; margin-bottom:12px; }
.hp-display,.wave-display,.gold-display { color:#fff; font-size:14px; font-weight:700; background:rgba(255,255,255,0.1); padding:6px 12px; border-radius:10px; }
.game-area { background:rgba(0,0,0,0.3); border-radius:16px; padding:12px; margin-bottom:12px; min-height:120px; position:relative; }
.enemy-lane { height:60px; position:relative; margin-bottom:8px; }
.enemy { position:absolute; bottom:0; display:flex; flex-direction:column; align-items:center; }
.enemy-hp { font-size:11px; color:#fff; background:rgba(239,68,68,0.8); padding:1px 5px; border-radius:6px; }
.enemy-icon { font-size:28px; }
.towers-row { display:flex; gap:8px; justify-content:center; }
.tower-slot { width:48px; height:48px; background:rgba(255,255,255,0.1); border:2px dashed rgba(255,255,255,0.3); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:24px; cursor:pointer; color:rgba(255,255,255,0.5); }
.tower-slot.placed { background:rgba(34,197,94,0.3); border-color:#22c55e; border-style:solid; }
.question-area { background:rgba(255,255,255,0.1); border-radius:14px; padding:16px; text-align:center; }
.q-text { color:#fff; font-size:28px; font-weight:800; margin-bottom:12px; }
.q-choices { display:flex; gap:8px; justify-content:center; }
.q-btn { background:rgba(255,255,255,0.9); color:#052e16; border:none; padding:12px 20px; border-radius:10px; font-size:20px; font-weight:700; cursor:pointer; }
.q-btn.correct { background:#10b981; color:#fff; }
.q-btn.wrong { background:#ef4444; color:#fff; }
.result-box { text-align:center; padding:40px 20px; }
.res-title { font-size:36px; color:#fff; font-weight:900; margin:10px 0; }
.res-detail { color:rgba(255,255,255,0.8); font-size:16px; }
.levelup { background:#22c55e; color:#fff; padding:10px 20px; border-radius:20px; font-weight:800; font-size:18px; margin:14px auto; display:inline-block; }
.res-btns { display:flex; gap:12px; justify-content:center; margin-top:20px; }
.rbtn { background:rgba(255,255,255,0.9); color:#052e16; border:none; padding:12px 28px; border-radius:20px; font-size:16px; font-weight:700; cursor:pointer; }
.rbtn.home { background:#166534; color:#fff; }
</style>
"""

print("=== 타워 디펜스 게임 ===")
write_file('/var/www/somekorean/resources/js/pages/games/GameTowerDefense.vue', tower_defense)

# Update router
print("\n=== 라우터 업데이트 ===")
router_content = ssh("cat /var/www/somekorean/resources/js/router/index.js")
if 'game-tower-defense' not in router_content:
    updated = router_content.replace(
        "  { path: '/games/stroop'",
        "  { path: '/games/tower-defense', component: () => import('../pages/games/GameTowerDefense.vue'), name: 'game-tower-defense' },\n  { path: '/games/stroop'"
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', updated)
    print("Router updated")

# Build
print("\n=== 최종 npm 빌드 ===")
build_result = ssh("cd /var/www/somekorean && npm run build 2>&1 | tail -6", timeout=300)
print(build_result)

print("\n=== 캐시 클리어 ===")
print(ssh("cd /var/www/somekorean && php artisan config:clear && php artisan cache:clear && php artisan route:cache 2>&1"))

# Summary
print("\n========================================")
print("🎮 게임 개발 완료 요약")
print("========================================")
total = ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SELECT COUNT(*) as total FROM games;\"")
routed = ssh("mysql --defaults-file=/tmp/sk_main.cnf somekorean -e \"SELECT COUNT(*) as routed FROM games WHERE route_name IS NOT NULL AND route_name != '';\"")
print(f"전체 게임: {total}")
print(f"라우트 연결된 게임: {routed}")
print("========================================")

c.close()
