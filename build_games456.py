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

# ===== GAME 4: 색깔 맞추기 =====
game4 = r"""<template>
  <div class="color-game" :style="bgStyle">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🎨</div>
      <div class="score">⭐ {{ totalStars }}</div>
    </div>
    <div class="progress-wrap" v-if="phase==='play'">
      <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
      <span class="prog-txt">{{ qIdx }}/{{ totalQ }}</span>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div class="big-emoji">🎨</div>
      <h1 class="title">색깔 맞추기</h1>
      <p class="subtitle">무슨 색깔이에요?</p>
      <div class="info-box">레벨 {{ level }}: {{ levelColors.length }}가지 색깔</div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>
    <div v-if="phase==='play'" class="play-area">
      <p class="question-label">무슨 색깔이에요?</p>
      <div class="color-circle" :style="{background: curColor.hex}" @click="speakQ">
        <span class="circle-emoji">{{ curColor.emoji }}</span>
      </div>
      <div class="choices">
        <button v-for="ch in choices" :key="ch.name" class="choice-btn"
          :class="{correct: answered && ch.name===curColor.name, wrong: answered && ch.name===picked && ch.name!==curColor.name, disabled: answered}"
          :disabled="answered" @click="pick(ch)">
          <span class="swatch" :style="{background: ch.hex}"></span>{{ ch.name }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight ? 'right' : 'wrong'">
        {{ wasRight ? curColor.name+'! 정답이에요! 🎉' : '다시 해봐요 💪' }}
      </div>
    </div>
    <div v-if="phase==='result'" class="result-box">
      <h2 class="res-title">결과 🎊</h2>
      <div class="res-score">{{ correct }}/{{ totalQ }}</div>
      <div class="stars-row">+{{ earned }} ⭐</div>
      <div v-if="leveled" class="levelup">🎉 레벨업! 레벨 {{ level }}!</div>
      <div class="res-btns">
        <button class="rbtn" @click="startGame">다시 🔄</button>
        <button class="rbtn home" @click="goBack">홈 🏠</button>
      </div>
    </div>
    <div v-if="sparkle" class="sparkles">
      <span v-for="i in 6" :key="i" class="sp" :style="spStyle(i)">⭐</span>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const allColors = [
  {name:'빨간색',hex:'#FF4444',emoji:'🍎'},{name:'파란색',hex:'#4488FF',emoji:'🫐'},
  {name:'노란색',hex:'#FFD700',emoji:'🌻'},{name:'초록색',hex:'#44BB44',emoji:'🐸'},
  {name:'보라색',hex:'#9944FF',emoji:'🍇'},{name:'주황색',hex:'#FF8C00',emoji:'🍊'},
  {name:'분홍색',hex:'#FF69B4',emoji:'🌸'},{name:'하늘색',hex:'#87CEEB',emoji:'🌊'},
  {name:'갈색',hex:'#8B4513',emoji:'🐻'},{name:'검은색',hex:'#555555',emoji:'🎱'},
]
const speak = t => { if(!window.speechSynthesis) return; window.speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.85; u.pitch=1.2; window.speechSynthesis.speak(u) }
const level = ref(parseInt(localStorage.getItem('color_level')||'1'))
const totalStars = ref(parseInt(localStorage.getItem('color_stars')||'0'))
const phase = ref('start'), qIdx = ref(0), totalQ = ref(10), correct = ref(0), earned = ref(0), leveled = ref(false)
const curColor = ref(allColors[0]), choices = ref([]), answered = ref(false), picked = ref(''), wasRight = ref(false), sparkle = ref(false)
const levelColors = computed(() => level.value<=2 ? allColors.slice(0,4) : level.value<=4 ? allColors.slice(0,6) : allColors)
const bgStyle = computed(() => ({background: phase.value==='play' ? `linear-gradient(135deg,${curColor.value.hex}33 0%,#fff9f0 100%)` : 'linear-gradient(135deg,#FFE0E0,#E0E0FF)'}))
const goBack = () => { window.speechSynthesis?.cancel(); router.push('/games') }
function startGame() { qIdx.value=0; correct.value=0; earned.value=0; leveled.value=false; phase.value='play'; nextQ() }
function nextQ() {
  answered.value=false; picked.value=''; sparkle.value=false
  const pool=levelColors.value; curColor.value=pool[Math.floor(Math.random()*pool.length)]
  const s=new Set([curColor.value.name])
  while(s.size<4) s.add(pool[Math.floor(Math.random()*pool.length)].name)
  choices.value=[...s].sort(()=>Math.random()-0.5).map(n=>allColors.find(c=>c.name===n))
  setTimeout(()=>speak('무슨 색깔이에요?'),300)
}
const speakQ = () => speak(curColor.value.name)
function pick(ch) {
  if(answered.value) return; answered.value=true; picked.value=ch.name
  if(ch.name===curColor.value.name){ wasRight.value=true; correct.value++; sparkle.value=true; speak(ch.name+'! 정답이에요!'); setTimeout(()=>sparkle.value=false,1500) }
  else { wasRight.value=false; speak('다시 해봐요') }
  qIdx.value++; if(qIdx.value>=totalQ.value) setTimeout(()=>showResult(),1500); else setTimeout(()=>nextQ(),1500)
}
function showResult() {
  earned.value=correct.value; totalStars.value+=earned.value; localStorage.setItem('color_stars',totalStars.value)
  if(correct.value>=8){ level.value++; leveled.value=true; localStorage.setItem('color_level',level.value); speak('레벨업! 대단해요!') }
  else speak(correct.value+'개 맞았어요!'); phase.value='result'
}
const spStyle = i => { const a=(i-1)*60*Math.PI/180,d=70+Math.random()*40; return {left:'50%',top:'40%',transform:`translate(calc(-50% + ${Math.cos(a)*d}px),calc(-50% + ${Math.sin(a)*d}px))`,animationDelay:(i*0.1)+'s'} }
onMounted(()=>speak('색깔 맞추기 게임!'))
onUnmounted(()=>window.speechSynthesis?.cancel())
</script>
<style scoped>
.color-game{min-height:100vh;display:flex;flex-direction:column;align-items:center;font-family:'Nanum Gothic',sans-serif;transition:background 0.5s;position:relative;overflow:hidden}
.game-header{width:100%;display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:rgba(255,255,255,0.3);backdrop-filter:blur(4px)}
.back-btn,.score{background:rgba(255,255,255,0.7);border:none;border-radius:20px;padding:8px 14px;font-size:14px;font-weight:bold;cursor:pointer;color:#333}
.level-badge{background:rgba(255,255,255,0.85);border-radius:20px;padding:6px 16px;font-size:16px;font-weight:bold;color:#9944FF}
.progress-wrap{width:90%;display:flex;align-items:center;gap:8px;margin:8px auto}
.prog-bar{flex:1;height:12px;background:rgba(255,255,255,0.4);border-radius:6px;overflow:hidden}
.prog-fill{height:100%;background:white;border-radius:6px;transition:width 0.4s}
.prog-txt{font-size:13px;font-weight:bold;color:rgba(255,255,255,0.9);white-space:nowrap}
.center-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:40px 20px;text-align:center}
.big-emoji{font-size:80px;animation:bob 1s ease-in-out infinite alternate}
@keyframes bob{from{transform:translateY(0)}to{transform:translateY(-12px)}}
.title{font-size:48px;font-weight:900;color:white;text-shadow:2px 2px rgba(0,0,0,0.15);margin:0}
.subtitle{font-size:24px;color:rgba(255,255,255,0.9);font-weight:bold;margin:0}
.info-box{background:rgba(255,255,255,0.3);border-radius:16px;padding:12px 24px;font-size:18px;font-weight:bold;color:white}
.start-btn{background:white;color:#9944FF;border:none;border-radius:30px;padding:16px 48px;font-size:26px;font-weight:900;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,0.2);transition:transform 0.15s}
.start-btn:hover{transform:scale(1.06)}
.play-area{flex:1;display:flex;flex-direction:column;align-items:center;width:100%;padding:16px;gap:18px}
.question-label{font-size:24px;font-weight:bold;color:#333;background:rgba(255,255,255,0.6);border-radius:20px;padding:10px 28px;margin:0}
.color-circle{width:180px;height:180px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 30px rgba(0,0,0,0.25);cursor:pointer;transition:transform 0.15s}
.color-circle:hover{transform:scale(1.05)}
.circle-emoji{font-size:64px}
.choices{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:90%;max-width:360px}
.choice-btn{display:flex;align-items:center;gap:10px;background:white;border:3px solid transparent;border-radius:20px;padding:16px 18px;font-size:20px;font-weight:bold;cursor:pointer;box-shadow:0 3px 10px rgba(0,0,0,0.15);transition:transform 0.1s;color:#333}
.choice-btn:hover:not(.disabled){transform:scale(1.04)}
.swatch{width:24px;height:24px;border-radius:50%;border:2px solid rgba(0,0,0,0.1);flex-shrink:0}
.choice-btn.correct{background:#A8FF78;border-color:#4CAF50;animation:pop 0.4s}
@keyframes pop{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}
.choice-btn.wrong{background:#FFB3B3;border-color:#F44336}
.feedback{font-size:22px;font-weight:bold;border-radius:16px;padding:10px 24px}
.feedback.right{background:rgba(168,255,120,0.5);color:#1a7a1a}
.feedback.wrong{background:rgba(255,179,179,0.5);color:#c0392b}
.result-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:30px}
.res-title{font-size:48px;font-weight:900;color:white;text-shadow:2px 2px rgba(0,0,0,0.15);margin:0}
.res-score{font-size:64px;font-weight:900;color:white;background:rgba(255,255,255,0.25);border-radius:24px;padding:14px 40px}
.stars-row{font-size:40px;font-weight:900;color:white}
.levelup{background:linear-gradient(135deg,#FFD700,#FFA500);border-radius:20px;padding:14px 30px;font-size:24px;font-weight:900;color:white;animation:pulse 0.6s ease infinite alternate}
@keyframes pulse{from{transform:scale(1)}to{transform:scale(1.05)}}
.res-btns{display:flex;gap:12px}
.rbtn{background:white;border:none;border-radius:24px;padding:14px 28px;font-size:20px;font-weight:bold;cursor:pointer;color:#9944FF;box-shadow:0 4px 14px rgba(0,0,0,0.2)}
.rbtn.home{background:rgba(255,255,255,0.4);color:white}
.sparkles{position:fixed;top:40%;left:50%;pointer-events:none;z-index:100}
.sp{position:absolute;font-size:24px;animation:spOut 1.2s ease forwards;opacity:1}
@keyframes spOut{0%{opacity:1;transform:translate(-50%,-50%) scale(0.5)}100%{opacity:0;transform:translate(var(--tx),var(--ty)) scale(1)}}
</style>"""

write_file('/var/www/somekorean/resources/js/pages/games/GameColors.vue', game4)

# ===== GAME 5: 동물 이름 퀴즈 =====
game5 = r"""<template>
  <div class="animal-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🐾</div>
      <div class="score">⭐ {{ totalStars }}</div>
    </div>
    <div class="progress-wrap" v-if="phase==='play'">
      <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
      <span class="prog-txt">{{ qIdx }}/{{ totalQ }}</span>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div class="big-emoji" style="font-size:90px">🦁</div>
      <h1 class="title">동물 이름 퀴즈</h1>
      <p class="subtitle">이 동물 이름은 뭐예요?</p>
      <div class="info-box">레벨 {{ level }}: {{ levelAnimals.length }}마리 동물</div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>
    <div v-if="phase==='play'" class="play-area">
      <div class="animal-display" @click="speakAnimal">
        <span class="animal-emoji">{{ cur.emoji }}</span>
      </div>
      <p class="tap-hint">👆 눌러서 소리 듣기</p>
      <div class="choices">
        <button v-for="ch in choices" :key="ch.name" class="choice-btn"
          :class="{correct: answered && ch.name===cur.name, wrong: answered && ch.name===picked && ch.name!==cur.name, disabled: answered}"
          :disabled="answered" @click="pick(ch)">
          {{ ch.emoji }} {{ ch.name }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? cur.name+'! 정답이에요! 🎉' : '정답은 '+cur.name+'이에요 💪' }}
      </div>
    </div>
    <div v-if="phase==='result'" class="result-box">
      <div class="res-emoji">🏆</div>
      <div class="res-score">{{ correct }}/{{ totalQ }}</div>
      <div class="stars-row">+{{ earned }} ⭐</div>
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
const allAnimals = [
  {name:'강아지',emoji:'🐶'},{name:'고양이',emoji:'🐱'},{name:'토끼',emoji:'🐰'},
  {name:'곰',emoji:'🐻'},{name:'사자',emoji:'🦁'},{name:'코끼리',emoji:'🐘'},
  {name:'기린',emoji:'🦒'},{name:'원숭이',emoji:'🐵'},{name:'펭귄',emoji:'🐧'},
  {name:'닭',emoji:'🐔'},{name:'오리',emoji:'🦆'},{name:'돼지',emoji:'🐷'},
  {name:'소',emoji:'🐮'},{name:'말',emoji:'🐴'},{name:'양',emoji:'🐑'},
  {name:'호랑이',emoji:'🐯'},{name:'악어',emoji:'🐊'},{name:'거북이',emoji:'🐢'},
  {name:'뱀',emoji:'🐍'},{name:'개구리',emoji:'🐸'},
]
const speak = t => { if(!window.speechSynthesis) return; window.speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.85; u.pitch=1.2; window.speechSynthesis.speak(u) }
const level = ref(parseInt(localStorage.getItem('animal_level')||'1'))
const totalStars = ref(parseInt(localStorage.getItem('animal_stars')||'0'))
const phase = ref('start'), qIdx = ref(0), totalQ = ref(10), correct = ref(0), earned = ref(0), leveled = ref(false)
const cur = ref(allAnimals[0]), choices = ref([]), answered = ref(false), picked = ref(''), wasRight = ref(false)
const levelAnimals = computed(() => level.value<=2 ? allAnimals.slice(0,8) : level.value<=4 ? allAnimals.slice(0,14) : allAnimals)
const goBack = () => { window.speechSynthesis?.cancel(); router.push('/games') }
function startGame() { qIdx.value=0; correct.value=0; earned.value=0; leveled.value=false; phase.value='play'; nextQ() }
function nextQ() {
  answered.value=false; picked.value=''
  const pool=levelAnimals.value; cur.value=pool[Math.floor(Math.random()*pool.length)]
  const s=new Set([cur.value.name])
  while(s.size<4) s.add(pool[Math.floor(Math.random()*pool.length)].name)
  choices.value=[...s].sort(()=>Math.random()-0.5).map(n=>allAnimals.find(a=>a.name===n))
  setTimeout(()=>speak('이 동물 이름은 뭐예요?'),300)
}
const speakAnimal = () => speak(cur.value.name)
function pick(ch) {
  if(answered.value) return; answered.value=true; picked.value=ch.name
  if(ch.name===cur.value.name){ wasRight.value=true; correct.value++; speak(ch.name+'! 정답이에요!') }
  else { wasRight.value=false; speak('정답은 '+cur.value.name+'이에요') }
  qIdx.value++; if(qIdx.value>=totalQ.value) setTimeout(()=>showResult(),1800); else setTimeout(()=>nextQ(),1800)
}
function showResult() {
  earned.value=correct.value; totalStars.value+=earned.value; localStorage.setItem('animal_stars',totalStars.value)
  if(correct.value>=8){ level.value++; leveled.value=true; localStorage.setItem('animal_level',level.value); speak('레벨업! 대단해요!') }
  else speak(correct.value+'마리 맞았어요!'); phase.value='result'
}
onMounted(()=>speak('동물 이름 퀴즈!'))
onUnmounted(()=>window.speechSynthesis?.cancel())
</script>
<style scoped>
.animal-game{min-height:100vh;background:linear-gradient(135deg,#E8F5E9 0%,#F3E5F5 50%,#E3F2FD 100%);display:flex;flex-direction:column;align-items:center;font-family:'Nanum Gothic',sans-serif}
.game-header{width:100%;display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:rgba(255,255,255,0.5);backdrop-filter:blur(4px)}
.back-btn,.score{background:rgba(255,255,255,0.8);border:none;border-radius:20px;padding:8px 14px;font-size:14px;font-weight:bold;cursor:pointer;color:#333}
.level-badge{background:rgba(255,255,255,0.9);border-radius:20px;padding:6px 16px;font-size:16px;font-weight:bold;color:#4CAF50}
.progress-wrap{width:90%;display:flex;align-items:center;gap:8px;margin:8px auto}
.prog-bar{flex:1;height:12px;background:rgba(255,255,255,0.6);border-radius:6px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#4CAF50,#8BC34A);border-radius:6px;transition:width 0.4s}
.prog-txt{font-size:13px;font-weight:bold;color:#555;white-space:nowrap}
.center-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:40px 20px;text-align:center}
.title{font-size:44px;font-weight:900;color:#2E7D32;text-shadow:1px 1px 0 rgba(0,0,0,0.1);margin:0}
.subtitle{font-size:22px;color:#555;font-weight:bold;margin:0}
.info-box{background:rgba(255,255,255,0.7);border-radius:16px;padding:12px 24px;font-size:18px;font-weight:bold;color:#333}
.start-btn{background:linear-gradient(135deg,#4CAF50,#8BC34A);color:white;border:none;border-radius:30px;padding:16px 48px;font-size:26px;font-weight:900;cursor:pointer;box-shadow:0 6px 20px rgba(76,175,80,0.4);transition:transform 0.15s}
.start-btn:hover{transform:scale(1.06)}
.play-area{flex:1;display:flex;flex-direction:column;align-items:center;width:100%;padding:16px;gap:16px}
.animal-display{background:white;border-radius:32px;padding:30px;box-shadow:0 8px 30px rgba(0,0,0,0.12);cursor:pointer;transition:transform 0.15s}
.animal-display:hover{transform:scale(1.05)}
.animal-emoji{font-size:120px;display:block}
.tap-hint{font-size:14px;color:#888;margin:0}
.choices{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:90%;max-width:380px}
.choice-btn{background:white;border:3px solid transparent;border-radius:20px;padding:16px 12px;font-size:20px;font-weight:bold;cursor:pointer;box-shadow:0 3px 10px rgba(0,0,0,0.1);transition:transform 0.1s;color:#333}
.choice-btn:hover:not(.disabled){transform:scale(1.04);border-color:#4CAF50}
.choice-btn.correct{background:#A8FF78;border-color:#4CAF50;animation:pop 0.4s}
@keyframes pop{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}
.choice-btn.wrong{background:#FFB3B3;border-color:#F44336}
.feedback{font-size:20px;font-weight:bold;border-radius:16px;padding:10px 24px;text-align:center}
.feedback.right{background:rgba(168,255,120,0.6);color:#1a7a1a}
.feedback.wrong{background:rgba(255,179,179,0.6);color:#c0392b}
.result-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:30px}
.res-emoji{font-size:80px}
.res-score{font-size:64px;font-weight:900;color:#2E7D32;background:rgba(255,255,255,0.8);border-radius:24px;padding:14px 40px}
.stars-row{font-size:40px;font-weight:900;color:#FF9F43}
.levelup{background:linear-gradient(135deg,#FFD700,#FFA500);border-radius:20px;padding:14px 30px;font-size:24px;font-weight:900;color:white;animation:pulse 0.6s ease infinite alternate}
@keyframes pulse{from{transform:scale(1)}to{transform:scale(1.05)}}
.res-btns{display:flex;gap:12px}
.rbtn{background:linear-gradient(135deg,#4CAF50,#8BC34A);color:white;border:none;border-radius:24px;padding:14px 28px;font-size:20px;font-weight:bold;cursor:pointer;box-shadow:0 4px 14px rgba(76,175,80,0.3)}
.rbtn.home{background:rgba(255,255,255,0.7);color:#333}
</style>"""

write_file('/var/www/somekorean/resources/js/pages/games/GameAnimals.vue', game5)

# ===== GAME 6: 모양 맞추기 =====
game6 = r"""<template>
  <div class="shape-game">
    <div class="game-header">
      <button class="back-btn" @click="goBack">← 뒤로</button>
      <div class="level-badge">레벨 {{ level }} 🔷</div>
      <div class="score">⭐ {{ totalStars }}</div>
    </div>
    <div class="progress-wrap" v-if="phase==='play'">
      <div class="prog-bar"><div class="prog-fill" :style="{width:(qIdx/totalQ*100)+'%'}"></div></div>
      <span class="prog-txt">{{ qIdx }}/{{ totalQ }}</span>
    </div>
    <div v-if="phase==='start'" class="center-box">
      <div class="shapes-preview">🔴🔷🟩🔶</div>
      <h1 class="title">모양 맞추기</h1>
      <p class="subtitle">이 모양 이름은 뭐예요?</p>
      <div class="info-box">레벨 {{ level }}: {{ levelShapes.length }}가지 모양</div>
      <button class="start-btn" @click="startGame">시작! 🎮</button>
    </div>
    <div v-if="phase==='play'" class="play-area">
      <div class="shape-display" @click="speakShape">
        <svg :viewBox="cur.viewBox" class="shape-svg">
          <path :d="cur.path" :fill="cur.color" />
        </svg>
      </div>
      <p class="tap-hint">👆 눌러서 소리 듣기</p>
      <div class="choices">
        <button v-for="ch in choices" :key="ch.name" class="choice-btn"
          :class="{correct: answered && ch.name===cur.name, wrong: answered && ch.name===picked && ch.name!==cur.name, disabled: answered}"
          :disabled="answered" @click="pick(ch)">
          {{ ch.name }}
        </button>
      </div>
      <div v-if="answered" class="feedback" :class="wasRight?'right':'wrong'">
        {{ wasRight ? cur.name+'! 정답이에요! 🎉' : '정답은 '+cur.name+'이에요 💪' }}
      </div>
    </div>
    <div v-if="phase==='result'" class="result-box">
      <div style="font-size:80px">🔷</div>
      <div class="res-score">{{ correct }}/{{ totalQ }}</div>
      <div class="stars-row">+{{ earned }} ⭐</div>
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
const allShapes = [
  {name:'동그라미',viewBox:'0 0 100 100',path:'M50 10 A40 40 0 1 1 49.9 10Z',color:'#FF6B6B'},
  {name:'네모',viewBox:'0 0 100 100',path:'M10 10 H90 V90 H10 Z',color:'#4ECDC4'},
  {name:'세모',viewBox:'0 0 100 100',path:'M50 5 L95 95 L5 95 Z',color:'#FFE66D'},
  {name:'별',viewBox:'0 0 100 100',path:'M50 5 L61 35 L93 35 L68 57 L79 91 L50 70 L21 91 L32 57 L7 35 L39 35 Z',color:'#F7DC6F'},
  {name:'하트',viewBox:'0 0 100 100',path:'M50 85 L15 50 C5 35 15 15 30 15 C38 15 45 20 50 28 C55 20 62 15 70 15 C85 15 95 35 85 50 Z',color:'#E91E63'},
  {name:'다이아몬드',viewBox:'0 0 100 100',path:'M50 5 L95 50 L50 95 L5 50 Z',color:'#9B59B6'},
  {name:'타원',viewBox:'0 0 120 80',path:'M60 10 A50 30 0 1 1 59.9 10Z',color:'#3498DB'},
  {name:'육각형',viewBox:'0 0 100 100',path:'M50 5 L90 27.5 L90 72.5 L50 95 L10 72.5 L10 27.5 Z',color:'#2ECC71'},
]
const speak = t => { if(!window.speechSynthesis) return; window.speechSynthesis.cancel(); const u=new SpeechSynthesisUtterance(t); u.lang='ko-KR'; u.rate=0.85; u.pitch=1.2; window.speechSynthesis.speak(u) }
const level = ref(parseInt(localStorage.getItem('shape_level')||'1'))
const totalStars = ref(parseInt(localStorage.getItem('shape_stars')||'0'))
const phase = ref('start'), qIdx = ref(0), totalQ = ref(10), correct = ref(0), earned = ref(0), leveled = ref(false)
const cur = ref(allShapes[0]), choices = ref([]), answered = ref(false), picked = ref(''), wasRight = ref(false)
const levelShapes = computed(() => level.value<=2 ? allShapes.slice(0,4) : level.value<=4 ? allShapes.slice(0,6) : allShapes)
const goBack = () => { window.speechSynthesis?.cancel(); router.push('/games') }
function startGame() { qIdx.value=0; correct.value=0; earned.value=0; leveled.value=false; phase.value='play'; nextQ() }
function nextQ() {
  answered.value=false; picked.value=''
  const pool=levelShapes.value; cur.value=pool[Math.floor(Math.random()*pool.length)]
  const s=new Set([cur.value.name])
  while(s.size<4) s.add(pool[Math.floor(Math.random()*pool.length)].name)
  choices.value=[...s].sort(()=>Math.random()-0.5).map(n=>allShapes.find(a=>a.name===n))
  setTimeout(()=>speak('이 모양 이름은 뭐예요?'),300)
}
const speakShape = () => speak(cur.value.name)
function pick(ch) {
  if(answered.value) return; answered.value=true; picked.value=ch.name
  if(ch.name===cur.value.name){ wasRight.value=true; correct.value++; speak(ch.name+'! 정답이에요!') }
  else { wasRight.value=false; speak('정답은 '+cur.value.name+'이에요') }
  qIdx.value++; if(qIdx.value>=totalQ.value) setTimeout(()=>showResult(),1800); else setTimeout(()=>nextQ(),1800)
}
function showResult() {
  earned.value=correct.value; totalStars.value+=earned.value; localStorage.setItem('shape_stars',totalStars.value)
  if(correct.value>=8){ level.value++; leveled.value=true; localStorage.setItem('shape_level',level.value); speak('레벨업! 대단해요!') }
  else speak(correct.value+'개 맞았어요!'); phase.value='result'
}
onMounted(()=>speak('모양 맞추기 게임!'))
onUnmounted(()=>window.speechSynthesis?.cancel())
</script>
<style scoped>
.shape-game{min-height:100vh;background:linear-gradient(135deg,#EDE7F6 0%,#E3F2FD 50%,#E8F5E9 100%);display:flex;flex-direction:column;align-items:center;font-family:'Nanum Gothic',sans-serif}
.game-header{width:100%;display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:rgba(255,255,255,0.5);backdrop-filter:blur(4px)}
.back-btn,.score{background:rgba(255,255,255,0.8);border:none;border-radius:20px;padding:8px 14px;font-size:14px;font-weight:bold;cursor:pointer;color:#333}
.level-badge{background:rgba(255,255,255,0.9);border-radius:20px;padding:6px 16px;font-size:16px;font-weight:bold;color:#673AB7}
.progress-wrap{width:90%;display:flex;align-items:center;gap:8px;margin:8px auto}
.prog-bar{flex:1;height:12px;background:rgba(255,255,255,0.6);border-radius:6px;overflow:hidden}
.prog-fill{height:100%;background:linear-gradient(90deg,#7C4DFF,#E040FB);border-radius:6px;transition:width 0.4s}
.prog-txt{font-size:13px;font-weight:bold;color:#555;white-space:nowrap}
.center-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:40px 20px;text-align:center}
.shapes-preview{font-size:60px;letter-spacing:8px}
.title{font-size:44px;font-weight:900;color:#512DA8;text-shadow:1px 1px 0 rgba(0,0,0,0.1);margin:0}
.subtitle{font-size:22px;color:#555;font-weight:bold;margin:0}
.info-box{background:rgba(255,255,255,0.7);border-radius:16px;padding:12px 24px;font-size:18px;font-weight:bold;color:#333}
.start-btn{background:linear-gradient(135deg,#7C4DFF,#E040FB);color:white;border:none;border-radius:30px;padding:16px 48px;font-size:26px;font-weight:900;cursor:pointer;box-shadow:0 6px 20px rgba(124,77,255,0.4);transition:transform 0.15s}
.start-btn:hover{transform:scale(1.06)}
.play-area{flex:1;display:flex;flex-direction:column;align-items:center;width:100%;padding:16px;gap:14px}
.shape-display{background:white;border-radius:32px;padding:30px;box-shadow:0 8px 30px rgba(0,0,0,0.12);cursor:pointer;transition:transform 0.15s}
.shape-display:hover{transform:scale(1.05)}
.shape-svg{width:160px;height:160px}
.tap-hint{font-size:14px;color:#888;margin:0}
.choices{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:90%;max-width:360px}
.choice-btn{background:white;border:3px solid transparent;border-radius:20px;padding:18px 12px;font-size:22px;font-weight:bold;cursor:pointer;box-shadow:0 3px 10px rgba(0,0,0,0.1);transition:transform 0.1s;color:#333}
.choice-btn:hover:not(.disabled){transform:scale(1.04);border-color:#7C4DFF}
.choice-btn.correct{background:#E8F5E9;border-color:#4CAF50;color:#1a7a1a;animation:pop 0.4s}
@keyframes pop{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}
.choice-btn.wrong{background:#FFEBEE;border-color:#F44336;color:#c0392b}
.feedback{font-size:20px;font-weight:bold;border-radius:16px;padding:10px 24px;text-align:center}
.feedback.right{background:rgba(168,255,120,0.6);color:#1a7a1a}
.feedback.wrong{background:rgba(255,179,179,0.6);color:#c0392b}
.result-box{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:30px}
.res-score{font-size:64px;font-weight:900;color:#512DA8;background:rgba(255,255,255,0.8);border-radius:24px;padding:14px 40px}
.stars-row{font-size:40px;font-weight:900;color:#FF9F43}
.levelup{background:linear-gradient(135deg,#FFD700,#FFA500);border-radius:20px;padding:14px 30px;font-size:24px;font-weight:900;color:white;animation:pulse 0.6s ease infinite alternate}
@keyframes pulse{from{transform:scale(1)}to{transform:scale(1.05)}}
.res-btns{display:flex;gap:12px}
.rbtn{background:linear-gradient(135deg,#7C4DFF,#E040FB);color:white;border:none;border-radius:24px;padding:14px 28px;font-size:20px;font-weight:bold;cursor:pointer;box-shadow:0 4px 14px rgba(124,77,255,0.3)}
.rbtn.home{background:rgba(255,255,255,0.7);color:#333}
</style>"""

write_file('/var/www/somekorean/resources/js/pages/games/GameShapes.vue', game6)

# Update router - add games 4, 5, 6
router_content = ssh('cat /var/www/somekorean/resources/js/router/index.js')
new_routes = """    { path: '/games/colors', component: () => import('../pages/games/GameColors.vue'), name: 'game-colors' },
    { path: '/games/animals', component: () => import('../pages/games/GameAnimals.vue'), name: 'game-animals' },
    { path: '/games/shapes', component: () => import('../pages/games/GameShapes.vue'), name: 'game-shapes' },"""

# Find the right insertion point - after game-counting
if 'game-counting' in router_content and new_routes.strip() not in router_content:
    router_content = router_content.replace(
        "{ path: '/games/counting', component: () => import('../pages/games/GameCounting.vue'), name: 'game-counting' },",
        "{ path: '/games/counting', component: () => import('../pages/games/GameCounting.vue'), name: 'game-counting' },\n    " + new_routes
    )
    write_file('/var/www/somekorean/resources/js/router/index.js', router_content)
    print('Router updated with games 4,5,6')
else:
    print('Router already has these routes or insertion point not found')

print('Building...')
result = ssh('cd /var/www/somekorean && npm run build 2>&1 | tail -5', timeout=300)
print(result)
print('Route cache:', ssh('php /var/www/somekorean/artisan route:cache 2>&1 | tail -2'))
c.close()
