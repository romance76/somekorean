import paramiko, base64, time

def get_ssh():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect('68.183.60.70', username='root', password='EhdRh0817wodl', timeout=15)
    return c

def ssh(cmd, timeout=60):
    c = get_ssh()
    stdin, stdout, stderr = c.exec_command(cmd, timeout=timeout)
    o = stdout.read().decode('utf-8','replace').strip()
    e = stderr.read().decode('utf-8','replace').strip()
    c.close()
    return o + ('\n[STDERR]' + e if e else '')

def write_file(path, content):
    encoded = base64.b64encode(content.encode('utf-8')).decode('ascii')
    chunks = [encoded[i:i+3000] for i in range(0, len(encoded), 3000)]
    ssh('> /tmp/_wf.b64')
    for chunk in chunks:
        ssh("echo -n '{}' >> /tmp/_wf.b64".format(chunk))
    return ssh('base64 -d /tmp/_wf.b64 > {} && rm /tmp/_wf.b64 && echo OK'.format(path))

# ===== PART A: Deploy game files =====

print("=== PART A: Creating directories ===")
result = ssh('mkdir -p /var/www/somekorean/public/games/slots /var/www/somekorean/public/games/hextris /var/www/somekorean/public/games/mahjong')
print("mkdir:", result or "OK")

# File 1: Slots
slots_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>슬롯머신</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#1a0533,#2d0a5e,#1a0533);min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:Arial,sans-serif;color:white;overflow:hidden}
.machine{background:linear-gradient(180deg,#7c3aed,#4c1d95);border-radius:20px;padding:20px;box-shadow:0 0 40px rgba(139,92,246,0.8);max-width:340px;width:95%;text-align:center}
h1{font-size:22px;color:#fbbf24;text-shadow:0 0 10px #fbbf24;margin-bottom:10px;letter-spacing:2px}
.cr{font-size:17px;margin-bottom:10px;color:#e879f9}
.cr span{color:#fbbf24;font-weight:bold;font-size:20px}
.reels{background:#0f0a1e;border-radius:10px;padding:10px;margin-bottom:12px;border:3px solid #7c3aed;display:flex;gap:8px;justify-content:center;height:90px;align-items:center}
.reel{width:76px;height:76px;background:#1a0533;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:40px;border:2px solid #4c1d95}
.reel.spin{animation:sp 0.09s linear infinite}
@keyframes sp{0%{transform:scaleY(1)}50%{transform:scaleY(0.8)}100%{transform:scaleY(1)}}
.bet-row{display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:12px}
.bb{background:#4c1d95;border:2px solid #7c3aed;color:white;width:34px;height:34px;border-radius:6px;font-size:18px;cursor:pointer}
.ba{font-size:16px;color:#fbbf24;font-weight:bold;min-width:70px;text-align:center}
.msg{min-height:32px;font-size:16px;font-weight:bold;color:#fbbf24;margin-bottom:10px}
.sbtn{background:linear-gradient(135deg,#f59e0b,#d97706);border:none;color:#000;padding:13px 0;border-radius:10px;font-size:17px;font-weight:bold;cursor:pointer;width:100%;box-shadow:0 4px 14px rgba(245,158,11,0.5)}
.sbtn:disabled{opacity:0.5;cursor:not-allowed}
.pt{background:rgba(0,0,0,0.3);border-radius:8px;padding:8px;font-size:11px;color:#c4b5fd;text-align:left;margin-top:10px}
.pt h3{color:#fbbf24;margin-bottom:4px;text-align:center;font-size:12px}
.pr{display:flex;justify-content:space-between;padding:2px 0}
.bk{background:#475569;border:none;color:white;padding:7px 18px;border-radius:8px;cursor:pointer;margin-top:8px;font-size:13px}
</style>
</head>
<body>
<div class="machine">
  <h1>🎰 SLOTS</h1>
  <div class="cr">크레딧: <span id="cr">1000</span></div>
  <div class="reels"><div class="reel" id="r0">🍒</div><div class="reel" id="r1">🍋</div><div class="reel" id="r2">🍊</div></div>
  <div class="bet-row"><button class="bb" onclick="cb(-10)">-</button><div class="ba">베팅: <span id="bt">10</span></div><button class="bb" onclick="cb(10)">+</button></div>
  <div class="msg" id="msg">🎰 행운을 빌어요!</div>
  <button class="sbtn" id="sb" onclick="spin()">🎰 SPIN!</button>
  <div class="pt"><h3>🏆 배당표</h3><div class="pr"><span>💎💎💎</span><span>×100</span></div><div class="pr"><span>7️⃣7️⃣7️⃣</span><span>×50</span></div><div class="pr"><span>🍀🍀🍀</span><span>×20</span></div><div class="pr"><span>⭐⭐⭐</span><span>×10</span></div><div class="pr"><span>같은 3개</span><span>×3</span></div><div class="pr"><span>같은 2개</span><span>×1.5</span></div><div class="pr"><span>🍒 하나</span><span>×1.2</span></div></div>
  <button class="bk" onclick="exit()">← 나가기</button>
</div>
<script>
const SYM=['🍒','🍋','🍊','🍇','⭐','🍀','7️⃣','💎'];
const WT=[20,18,15,12,10,8,5,3];
const TOT=WT.reduce((a,b)=>a+b,0);
let cr=1000,bt=10,spinning=false,won=0;
function rng(){let r=Math.random()*TOT,s=0;for(let i=0;i<SYM.length;i++){s+=WT[i];if(r<s)return SYM[i];}return SYM[0];}
function cb(d){if(spinning)return;bt=Math.min(100,Math.max(10,bt+d));document.getElementById('bt').textContent=bt;}
let timers=[];
function spin(){
  if(spinning||cr<bt)return;spinning=true;cr-=bt;
  document.getElementById('cr').textContent=cr;
  document.getElementById('msg').textContent='🎲 돌리는 중...';
  document.getElementById('sb').disabled=true;
  const reels=[0,1,2].map(i=>document.getElementById('r'+i));
  reels.forEach(r=>r.classList.add('spin'));
  const res=[];
  timers.forEach(t=>clearInterval(t));timers=[];
  reels.forEach((r,i)=>{
    const t=setInterval(()=>r.textContent=SYM[Math.floor(Math.random()*SYM.length)],80);
    timers.push(t);
    setTimeout(()=>{clearInterval(t);const s=rng();res[i]=s;r.textContent=s;r.classList.remove('spin');if(i===2)setTimeout(()=>calc(res),200);},800+i*300);
  });
}
function calc(r){
  const [a,b,c]=r;let m=0,msg='';
  if(a===b&&b===c){if(a==='💎')m=100;else if(a==='7️⃣')m=50;else if(a==='🍀')m=20;else if(a==='⭐')m=10;else m=3;msg=`🎉 JACKPOT! ×${m}`;}
  else if(a===b||b===c||a===c){m=1.5;msg='✨ 2개 일치! ×1.5';}
  else if(r.includes('🍒')){m=1.2;msg='🍒 체리! ×1.2';}
  else{msg='😢 다시 도전!';}
  if(m>0){const w=Math.floor(bt*m);cr+=w;won+=w;document.getElementById('cr').textContent=cr;msg+=` +${w}`;}
  document.getElementById('msg').textContent=msg;
  document.getElementById('sb').disabled=false;spinning=false;
  if(cr<=0){setTimeout(over,1000);}
}
function over(){window.parent.postMessage({type:'GAME_SCORE',game:'slots',score:won},'*');}
function exit(){window.parent.postMessage({type:'GAME_EXIT',game:'slots'},'*');}
</script>
</body>
</html>'''

# File 2: Hextris
hextris_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hextris</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#0f172a;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;overflow:hidden;font-family:Arial,sans-serif;color:white;touch-action:none}
#sa{display:flex;gap:24px;margin-bottom:8px;font-size:15px}
.sv{color:#818cf8;font-weight:bold;font-size:18px}
canvas{display:block}
#ov{position:fixed;inset:0;background:rgba(0,0,0,0.9);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;color:white}
#ov h2{font-size:28px;color:#818cf8}
.btn{background:#818cf8;color:#000;border:none;padding:12px 28px;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer}
.btn-b{background:#475569;color:white;margin-left:8px}
#ctrl{display:flex;gap:14px;margin-top:8px}
.cb{background:#1e293b;border:2px solid #818cf8;color:white;padding:10px 18px;border-radius:8px;font-size:18px;cursor:pointer}
.cb:active{background:#818cf8;color:#000}
</style>
</head>
<body>
<div id="sa"><span>점수: <span class="sv" id="scEl">0</span></span><span>레벨: <span class="sv" id="lvEl">1</span></span></div>
<canvas id="c"></canvas>
<div id="ctrl"><button class="cb" id="bL">◀ 좌회전</button><button class="cb" id="bR">우회전 ▶</button></div>
<div id="ov">
  <h2>🔷 헥스트리스</h2>
  <p style="color:#94a3b8">블록이 중심으로 떨어집니다!</p>
  <p style="color:#94a3b8">같은 색 3개 이상 → 제거!</p>
  <p style="color:#94a3b8">A/D 키 또는 버튼으로 회전</p>
  <button class="btn" onclick="go()">게임 시작</button>
</div>
<script>
const cv=document.getElementById('c'),ctx=cv.getContext('2d'),ov=document.getElementById('ov'),scEl=document.getElementById('scEl'),lvEl=document.getElementById('lvEl');
const SZ=Math.min(window.innerWidth,window.innerHeight*0.75,380);
cv.width=SZ;cv.height=SZ;
const CX=SZ/2,CY=SZ/2,SIDES=6;
const COLS=['#f87171','#fb923c','#facc15','#4ade80','#60a5fa','#c084fc'];
let rings,sc,lv,inc,run,aId,lt,spd;
function go(){
  rings=Array(3).fill(null).map(()=>Array(SIDES).fill(null).map(()=>({c:null})));
  sc=0;lv=1;spd=1200;run=true;ov.style.display='none';
  scEl.textContent=0;lvEl.textContent=1;
  inc=np();lt=performance.now();
  cancelAnimationFrame(aId);
  function loop(ts){const dt=ts-lt;lt=ts;if(run)upd(dt);drw();aId=requestAnimationFrame(loop);}
  aId=requestAnimationFrame(loop);
}
function np(){return{side:Math.floor(Math.random()*SIDES),color:COLS[Math.floor(Math.random()*COLS.length)],prog:0};}
function upd(dt){
  inc.prog+=dt/spd;
  if(inc.prog>=1){place();inc=np();}
  const nl=Math.floor(sc/200)+1;if(nl>lv){lv=nl;spd=Math.max(280,1200-lv*80);lvEl.textContent=lv;}
}
function place(){
  const s=inc.side;
  for(let r=rings.length-1;r>=0;r--){if(!rings[r][s].c){rings[r][s].c=inc.color;check();return;}}
  over();
}
function check(){
  let changed=true;
  while(changed){
    changed=false;
    for(let s=0;s<SIDES;s++){const col=rings.map(r=>r[s].c).filter(c=>c);if(col.length>=3&&col.every(c=>c===col[0])){rings.forEach(r=>r[s].c=null);sc+=col.length*10;scEl.textContent=sc;changed=true;break;}}
    for(let r=0;r<rings.length&&!changed;r++){
      const ring=rings[r];let rs=0,rc=ring[0].c,rl=1;
      for(let s=1;s<=SIDES;s++){const c=ring[s%SIDES].c;if(c&&c===rc){rl++;}else{if(rc&&rl>=3){for(let i=0;i<rl;i++)ring[(rs+i)%SIDES].c=null;sc+=rl*15;scEl.textContent=sc;changed=true;break;}rs=s;rc=c;rl=1;}}
    }
    rings=rings.filter(r=>r.some(c=>c.c));
    while(rings.length<3)rings.push(Array(SIDES).fill(null).map(()=>({c:null})));
    if(rings.length>8){over();return;}
  }
}
function rot(d){if(!run)return;inc.side=(inc.side+d+SIDES)%SIDES;}
function drw(){
  ctx.clearRect(0,0,SZ,SZ);ctx.fillStyle='#0f172a';ctx.fillRect(0,0,SZ,SZ);
  const maxR=SZ*0.44,rw=maxR/(rings.length+2);
  for(let r=0;r<rings.length;r++){
    const ri=(r+1)*rw;
    for(let s=0;s<SIDES;s++){
      const sA=(s/SIDES)*Math.PI*2-Math.PI/2,eA=((s+1)/SIDES)*Math.PI*2-Math.PI/2;
      ctx.beginPath();ctx.arc(CX,CY,ri+rw,sA,eA);ctx.arc(CX,CY,ri,eA,sA,true);ctx.closePath();
      ctx.fillStyle=rings[r][s].c||'rgba(255,255,255,0.04)';ctx.fill();ctx.strokeStyle='#1e293b';ctx.lineWidth=1.5;ctx.stroke();
    }
  }
  const pR=(rings.length+1)*rw,pr=inc.prog;
  const sA=(inc.side/SIDES)*Math.PI*2-Math.PI/2,eA=((inc.side+1)/SIDES)*Math.PI*2-Math.PI/2;
  ctx.beginPath();ctx.arc(CX,CY,pR+rw*(1-pr),sA,eA);ctx.arc(CX,CY,pR*(1-pr)+rw*0.5,eA,sA,true);ctx.closePath();
  ctx.fillStyle=inc.color;ctx.globalAlpha=0.85;ctx.fill();ctx.globalAlpha=1;
  ctx.fillStyle='#1e293b';ctx.beginPath();ctx.arc(CX,CY,rw*0.7,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#818cf8';ctx.font=`bold ${Math.floor(rw*0.5)}px Arial`;ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(sc,CX,CY);
}
function over(){run=false;cancelAnimationFrame(aId);ov.innerHTML=`<h2>게임 오버!</h2><p>최종 점수: <strong style="color:#818cf8">${sc}</strong></p><div style="display:flex;gap:10px"><button class="btn btn-b" onclick="exit()">나가기</button><button class="btn" onclick="go()">다시하기</button></div>`;ov.style.display='flex';window.parent.postMessage({type:'GAME_SCORE',game:'hextris',score:sc},'*');}
function exit(){window.parent.postMessage({type:'GAME_EXIT',game:'hextris'},'*');}
document.getElementById('bL').addEventListener('click',()=>rot(-1));
document.getElementById('bR').addEventListener('click',()=>rot(1));
document.addEventListener('keydown',e=>{if(e.key==='a'||e.key==='ArrowLeft')rot(-1);if(e.key==='d'||e.key==='ArrowRight')rot(1);});
let tx=0;cv.addEventListener('touchstart',e=>tx=e.touches[0].clientX);
cv.addEventListener('touchend',e=>{const dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>30)rot(dx>0?1:-1);});
ctx.fillStyle='#0f172a';ctx.fillRect(0,0,SZ,SZ);
</script>
</body>
</html>'''

# File 3: Mahjong
mahjong_html = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>마작 솔리테어</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#1a3a2a;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;font-family:Arial,sans-serif;color:white;overflow:auto;padding:8px}
#hud{display:flex;gap:16px;margin-bottom:8px;font-size:14px;flex-wrap:wrap;justify-content:center}
.hv{color:#86efac;font-weight:bold;font-size:17px}
#board{display:flex;flex-direction:column;align-items:center;gap:3px}
.row{display:flex;gap:3px;justify-content:center}
.tile{width:42px;height:52px;border-radius:5px;display:flex;align-items:center;justify-content:center;font-size:20px;cursor:pointer;user-select:none;-webkit-user-select:none;transition:transform 0.1s}
.free{background:linear-gradient(135deg,#f0fdf4,#dcfce7);color:#000;border:2px solid rgba(0,100,0,0.3);box-shadow:2px 2px 0 #166534}
.free:hover{transform:translateY(-3px);box-shadow:2px 5px 0 #166534}
.blocked{background:#1e3a2a;color:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.08);cursor:default}
.sel{background:linear-gradient(135deg,#fef3c7,#fde68a)!important;transform:translateY(-5px)!important;box-shadow:2px 7px 0 #92400e!important;border-color:#f59e0b!important}
#ov{position:fixed;inset:0;background:rgba(0,0,0,0.9);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;color:white}
#ov h2{font-size:26px;color:#86efac}
.btn{background:#22c55e;color:#000;border:none;padding:12px 28px;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer}
.btn-b{background:#475569;color:white;margin-left:8px}
</style>
</head>
<body>
<div id="hud"><span>남은: <span class="hv" id="leftEl">56</span></span><span>점수: <span class="hv" id="scEl">0</span></span><span>시간: <span class="hv" id="tmEl">0:00</span></span></div>
<div id="board"></div>
<div id="ov"><div style="font-size:44px">🀄</div><h2>마작 솔리테어</h2><p style="color:#94a3b8">같은 패 2개를 짝지어 제거!</p><p style="color:#94a3b8">양쪽이 열린 패만 선택 가능</p><button class="btn" onclick="go()">게임 시작</button></div>
<script>
const TILES=['🀇','🀈','🀉','🀊','🀋','🀌','🀍','🀎','🀏','🀙','🀚','🀛','🀜','🀝','🀞','🀟','🀠','🀡','🀀','🀁','🀂','🀃','🀄','🀅','🀆','🀇','🀈','🀉'];
const LAYOUT=[
  [1,1,1,1,1,1,1,1,1,1,1,1],
  [0,1,1,1,1,1,1,1,1,1,1,0],
  [1,1,1,1,1,1,1,1,1,1,1,1],
  [0,0,1,1,1,1,1,1,1,1,0,0],
  [1,1,1,1,1,1,1,1,1,1,1,1],
  [0,1,1,1,1,1,1,1,1,1,1,0],
  [1,1,1,1,1,1,1,1,1,1,1,1],
];
const ROWS=LAYOUT.length,COLS=LAYOUT[0].length;
let board,sel,sc,startT,tmIv,run;
const ov=document.getElementById('ov'),brd=document.getElementById('board'),leftEl=document.getElementById('leftEl'),scEl=document.getElementById('scEl'),tmEl=document.getElementById('tmEl');

function go(){
  const pos=[];LAYOUT.forEach((r,ri)=>r.forEach((c,ci)=>{if(c)pos.push({r:ri,c:ci});}));
  const types=[];for(let i=0;i<pos.length/2;i++){const t=TILES[i%TILES.length];types.push(t,t);}
  for(let i=types.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[types[i],types[j]]=[types[j],types[i]];}
  board=pos.map((p,i)=>({...p,t:types[i],rm:false,sel:false}));
  sel=null;sc=0;run=true;ov.style.display='none';
  clearInterval(tmIv);startT=Date.now();
  tmIv=setInterval(()=>{const s=Math.floor((Date.now()-startT)/1000);tmEl.textContent=`${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`;},1000);
  render();
}

function isFree(t){
  if(t.rm)return false;
  const L=board.filter(x=>!x.rm&&x.r===t.r&&x.c===t.c-1).length;
  const R=board.filter(x=>!x.rm&&x.r===t.r&&x.c===t.c+1).length;
  return L===0||R===0;
}

function render(){
  brd.innerHTML='';
  const rem=board.filter(x=>!x.rm).length;leftEl.textContent=rem;
  for(let r=0;r<ROWS;r++){
    const row=document.createElement('div');row.className='row';
    for(let c=0;c<COLS;c++){
      const tile=board.find(t=>t.r===r&&t.c===c&&!t.rm);
      const div=document.createElement('div');
      if(tile){const fr=isFree(tile);div.className='tile '+(fr?'free':'blocked')+(sel===tile?' sel':'');div.textContent=tile.t;if(fr)div.addEventListener('click',()=>click(tile));}
      else{div.className='tile';div.style.visibility='hidden';}
      row.appendChild(div);
    }
    brd.appendChild(row);
  }
}

function click(tile){
  if(!isFree(tile))return;
  if(sel===tile){sel=null;render();return;}
  if(sel&&sel.t===tile.t){sel.rm=true;tile.rm=true;sc+=20;scEl.textContent=sc;sel=null;render();
    const rem=board.filter(t=>!t.rm);if(!rem.length)over(true);else if(!hasMove())over(false);}
  else{sel=tile;render();}
}

function hasMove(){const fr=board.filter(t=>!t.rm&&isFree(t));for(let i=0;i<fr.length;i++)for(let j=i+1;j<fr.length;j++)if(fr[i].t===fr[j].t)return true;return false;}

function over(won){run=false;clearInterval(tmIv);const fin=sc+(won?Math.max(0,2000-Math.floor((Date.now()-startT)/1000)*8):0);ov.innerHTML=`<h2>${won?'🏆 클리어!':'😢 막혔어요!'}</h2><p>점수: <strong style="color:#86efac">${fin}</strong></p><div style="display:flex;gap:10px"><button class="btn btn-b" onclick="exit()">나가기</button><button class="btn" onclick="go()">다시하기</button></div>`;ov.style.display='flex';window.parent.postMessage({type:'GAME_SCORE',game:'mahjong',score:fin},'*');}
function exit(){window.parent.postMessage({type:'GAME_EXIT',game:'mahjong'},'*');}
render();
</script>
</body>
</html>'''

print("\n=== Writing slots/index.html ===")
r = write_file('/var/www/somekorean/public/games/slots/index.html', slots_html)
print("slots:", r)

print("\n=== Writing hextris/index.html ===")
r = write_file('/var/www/somekorean/public/games/hextris/index.html', hextris_html)
print("hextris:", r)

print("\n=== Writing mahjong/index.html ===")
r = write_file('/var/www/somekorean/public/games/mahjong/index.html', mahjong_html)
print("mahjong:", r)

print("\n=== Verifying files ===")
print(ssh('ls -lh /var/www/somekorean/public/games/slots/index.html /var/www/somekorean/public/games/hextris/index.html /var/www/somekorean/public/games/mahjong/index.html'))

# ===== PART B: Reverb daemon =====
print("\n\n=== PART B: Reverb daemon ===")

print("\n--- 1. Check if Reverb is running ---")
reverb_ps = ssh('ps aux | grep "reverb" | grep -v grep')
print(reverb_ps if reverb_ps else "(not running)")

print("\n--- 2. Check .env ---")
print(ssh('grep -E "REVERB_PORT|REVERB_HOST|REVERB_SCHEME" /var/www/somekorean/.env'))

print("\n--- 3. Check supervisor ---")
print(ssh('which supervisorctl && supervisorctl status 2>/dev/null || echo "no supervisor"'))

if not reverb_ps:
    print("\n--- 4. Check port 8080 ---")
    print(ssh('ss -tlnp | grep 8080 || echo "port free"'))

    print("\n--- 5. Starting Reverb ---")
    start_result = ssh('cd /var/www/somekorean && nohup php artisan reverb:start --host=0.0.0.0 --port=8080 > /var/log/reverb.log 2>&1 &', timeout=15)
    print("start:", start_result or "launched")
    time.sleep(4)
    ps_check = ssh('ps aux | grep "reverb" | grep -v grep')
    print("ps after start:", ps_check if ps_check else "(not found in ps)")
else:
    print("\n--- Reverb already running, skipping start ---")

print("\n--- 6. Reverb log tail ---")
print(ssh('tail -20 /var/log/reverb.log 2>/dev/null || echo "no log"'))

print("\n=== DONE ===")
