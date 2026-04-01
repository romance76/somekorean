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
    result = ssh('base64 -d /tmp/_wf.b64 > {} && rm /tmp/_wf.b64 && echo OK'.format(path))
    return result

# Step 1: Create directories
print("Creating directories...")
r = ssh('mkdir -p /var/www/somekorean/public/games/snake /var/www/somekorean/public/games/pacman /var/www/somekorean/public/games/flappy /var/www/somekorean/public/games/duckhunt')
print("mkdir result:", r)

# File 1: Snake
SNAKE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Snake</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #1a1a2e; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: Arial, sans-serif; color: white; overflow: hidden; }
#hdr { display: flex; gap: 20px; margin-bottom: 10px; font-size: 16px; }
#sc { color: #4ade80; font-weight: bold; font-size: 22px; }
#hi { color: #94a3b8; font-size: 14px; }
canvas { border: 2px solid #4ade80; border-radius: 4px; }
#ov { position: fixed; inset: 0; background: rgba(0,0,0,0.88); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 14px; }
#ov h2 { font-size: 30px; color: #4ade80; }
.btn { background: #4ade80; color: #1a1a2e; border: none; padding: 12px 28px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; }
.btn-b { background: #475569; color: white; }
#pad { display: grid; grid-template-columns: repeat(3,46px); gap:4px; margin-top:8px; }
.pb { background: #334155; border: 1px solid #4ade80; color: white; width:46px; height:46px; border-radius:6px; font-size:20px; cursor:pointer; display:flex; align-items:center; justify-content:center; user-select:none; -webkit-user-select:none; }
.pb:active { background: #4ade80; color: #1a1a2e; }
</style>
</head>
<body>
<div id="hdr"><div><div id="sc">점수: 0</div><div id="hi">최고: 0</div></div></div>
<canvas id="c"></canvas>
<div id="pad">
  <div></div><button class="pb" id="bU">&#9650;</button><div></div>
  <button class="pb" id="bL">&#9664;</button><button class="pb" id="bD">&#9660;</button><button class="pb" id="bR">&#9654;</button>
</div>
<div id="ov">
  <h2>&#128013; 뱀 게임</h2>
  <p style="color:#94a3b8">방향키 또는 버튼으로 조작</p>
  <button class="btn" onclick="start()">게임 시작</button>
</div>
<script>
const cv=document.getElementById('c'),ctx=cv.getContext('2d'),ov=document.getElementById('ov'),sc=document.getElementById('sc'),hi=document.getElementById('hi');
const SZ=18,N=22;cv.width=SZ*N;cv.height=SZ*N;
let sn,dir,nd,food,pts,best=0,iv,run=false;
function start(){sn=[{x:11,y:11},{x:10,y:11},{x:9,y:11}];dir={x:1,y:0};nd={x:1,y:0};pts=0;run=true;ov.style.display='none';sc.textContent='점수: 0';place();clearInterval(iv);iv=setInterval(tick,115);}
function place(){do{food={x:Math.floor(Math.random()*N),y:Math.floor(Math.random()*N)}}while(sn.some(s=>s.x===food.x&&s.y===food.y));}
function tick(){
  dir=nd;
  const h={x:sn[0].x+dir.x,y:sn[0].y+dir.y};
  if(h.x<0||h.x>=N||h.y<0||h.y>=N||sn.some(s=>s.x===h.x&&s.y===h.y)){over();return;}
  sn.unshift(h);
  if(h.x===food.x&&h.y===food.y){pts+=10;if(pts>best){best=pts;hi.textContent='최고: '+best;}sc.textContent='점수: '+pts;place();if(pts%50===0){clearInterval(iv);iv=setInterval(tick,Math.max(60,115-pts));}}
  else sn.pop();
  draw();
}
function draw(){
  ctx.fillStyle='#0f172a';ctx.fillRect(0,0,cv.width,cv.height);
  ctx.strokeStyle='#1e293b';ctx.lineWidth=0.5;
  for(let i=0;i<=N;i++){ctx.beginPath();ctx.moveTo(i*SZ,0);ctx.lineTo(i*SZ,cv.height);ctx.stroke();ctx.beginPath();ctx.moveTo(0,i*SZ);ctx.lineTo(cv.width,i*SZ);ctx.stroke();}
  ctx.fillStyle='#f87171';ctx.beginPath();ctx.arc(food.x*SZ+SZ/2,food.y*SZ+SZ/2,SZ/2-2,0,Math.PI*2);ctx.fill();
  sn.forEach((s,i)=>{ctx.fillStyle=i===0?'#86efac':'#4ade80';ctx.beginPath();ctx.roundRect(s.x*SZ+1,s.y*SZ+1,SZ-2,SZ-2,3);ctx.fill();});
}
function over(){clearInterval(iv);run=false;ov.innerHTML='<h2>게임 오버</h2><p>점수: <strong style="color:#4ade80">'+pts+'</strong></p><div style="display:flex;gap:10px"><button class="btn btn-b" onclick="exit()">나가기</button><button class="btn" onclick="start()">다시하기</button></div>';ov.style.display='flex';window.parent.postMessage({type:'GAME_SCORE',game:'snake',score:pts},'*');}
function exit(){window.parent.postMessage({type:'GAME_EXIT',game:'snake'},'*');}
document.addEventListener('keydown',e=>{if(!run)return;const m={ArrowUp:{x:0,y:-1},ArrowDown:{x:0,y:1},ArrowLeft:{x:-1,y:0},ArrowRight:{x:1,y:0}};const d=m[e.key];if(d&&!(d.x===-dir.x&&d.y===-dir.y)){nd=d;e.preventDefault();}});
document.getElementById('bU').addEventListener('click',()=>{if(dir.y!==1)nd={x:0,y:-1}});
document.getElementById('bD').addEventListener('click',()=>{if(dir.y!==-1)nd={x:0,y:1}});
document.getElementById('bL').addEventListener('click',()=>{if(dir.x!==1)nd={x:-1,y:0}});
document.getElementById('bR').addEventListener('click',()=>{if(dir.x!==-1)nd={x:1,y:0}});
ctx.fillStyle='#0f172a';ctx.fillRect(0,0,cv.width,cv.height);
</script>
</body>
</html>"""

# File 2: Pacman
PACMAN = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pacman</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:Arial,sans-serif;color:#fff;overflow:hidden}
#info{display:flex;gap:20px;margin-bottom:6px;font-size:15px}
.iv{color:#facc15;font-weight:bold}
canvas{display:block;max-width:100vw;max-height:70vh}
#ov{position:fixed;inset:0;background:rgba(0,0,0,0.9);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px}
#ov h2{font-size:28px;color:#facc15}
.btn{background:#facc15;color:#000;border:none;padding:12px 28px;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer}
.btn-b{background:#475569;color:#fff;margin-left:8px}
#dp{display:grid;grid-template-columns:repeat(3,46px);gap:4px;margin-top:8px}
.db{background:#1e293b;border:1px solid #facc15;color:#fff;width:46px;height:46px;border-radius:6px;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;user-select:none}
.db:active{background:#facc15;color:#000}
</style>
</head>
<body>
<div id="info"><span>점수: <span id="scEl" class="iv">0</span></span><span>생명: <span id="liEl" class="iv">3</span></span><span>레벨: <span id="lvEl" class="iv">1</span></span></div>
<canvas id="c"></canvas>
<div id="dp"><div></div><button class="db" id="dU">&#9650;</button><div></div><button class="db" id="dL">&#9664;</button><button class="db" id="dD">&#9660;</button><button class="db" id="dR">&#9654;</button></div>
<div id="ov"><h2>&#128126; 팩맨</h2><p style="color:#94a3b8">방향키로 점을 먹으세요!</p><button class="btn" onclick="go()">게임 시작</button></div>
<script>
const C=document.getElementById('c'),ctx=C.getContext('2d'),ov=document.getElementById('ov');
const SZ=18;
const MAP=[
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0],
[0,3,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,3,0],
[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
[0,1,0,0,1,0,1,0,0,0,0,0,0,0,1,0,1,0,0,1,0],
[0,1,1,1,1,0,1,1,1,0,0,0,1,1,1,0,1,1,1,1,0],
[0,0,0,0,1,0,2,2,2,0,0,0,2,2,2,0,1,0,0,0,0],
[0,0,0,0,1,0,2,0,2,2,2,2,2,0,2,0,1,0,0,0,0],
[2,2,2,2,1,2,2,0,2,2,2,2,2,0,2,2,1,2,2,2,2],
[0,0,0,0,1,0,2,0,0,0,0,0,0,0,2,0,1,0,0,0,0],
[0,0,0,0,1,0,2,2,2,2,2,2,2,2,2,0,1,0,0,0,0],
[0,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,0],
[0,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,0],
[0,3,1,0,1,1,1,1,1,1,4,1,1,1,1,1,1,0,1,3,0],
[0,0,1,0,1,0,1,0,0,0,0,0,0,0,1,0,1,0,1,0,0],
[0,1,1,1,1,0,1,1,1,0,0,0,1,1,1,0,1,1,1,1,0],
[0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0],
[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
];
const R=MAP.length,CL=MAP[0].length;
C.width=CL*SZ;C.height=R*SZ;
let map,pac,gh,sc,li,lv,pw,pwt,dir,nd,run,aId,fr;
const GC=['#ff6b6b','#ff9ff3','#54a0ff','#ffeaa7'];
function initMap(){map=MAP.map(r=>[...r]);}
function go(){
  sc=0;li=3;lv=1;pw=false;pwt=0;dir={x:0,y:0};nd={x:0,y:0};fr=0;run=true;
  ov.style.display='none';initMap();
  pac={x:10,y:13,m:0.2,md:1};
  gh=[{x:9,y:7,dx:1,dy:0},{x:10,y:7,dx:-1,dy:0},{x:11,y:7,dx:0,dy:1},{x:10,y:8,dx:0,dy:-1}].map((g,i)=>({...g,color:GC[i],sc:false,dead:false}));
  upd(['scEl','liEl','lvEl'],[0,3,1]);
  cancelAnimationFrame(aId);let lt=0;
  function loop(ts){if(!run)return;if(ts-lt>140){step();lt=ts;}draw2();aId=requestAnimationFrame(loop);}
  aId=requestAnimationFrame(loop);
}
function upd(ids,vals){ids.forEach((id,i)=>document.getElementById(id).textContent=vals[i]);}
function step(){
  fr++;
  const nx=pac.x+nd.x,ny=pac.y+nd.y;
  if(nx>=0&&nx<CL&&ny>=0&&ny<R&&map[ny][nx]!==0)dir=nd;
  const cx=(pac.x+dir.x+CL)%CL,cy=(pac.y+dir.y+R)%R;
  if(map[cy][cx]!==0){pac.x=cx;pac.y=cy;}
  if(map[pac.y][pac.x]===1){map[pac.y][pac.x]=2;sc+=10;document.getElementById('scEl').textContent=sc;}
  if(map[pac.y][pac.x]===3){map[pac.y][pac.x]=2;sc+=50;document.getElementById('scEl').textContent=sc;pw=true;pwt=30;gh.forEach(g=>{if(!g.dead)g.sc=true;});}
  if(pw){pwt--;if(pwt<=0){pw=false;gh.forEach(g=>g.sc=false);}}
  pac.m+=0.1*pac.md;if(pac.m>0.35||pac.m<0.05)pac.md*=-1;
  const dirs=[{x:1,y:0},{x:-1,y:0},{x:0,y:1},{x:0,y:-1}];
  gh.forEach(g=>{
    if(g.dead){g.x=10;g.y=7;g.dead=false;return;}
    const vl=dirs.filter(d=>{const nx2=(g.x+d.x+CL)%CL,ny2=(g.y+d.y+R)%R;return map[ny2][nx2]!==0&&!(d.x===-g.dx&&d.y===-g.dy);});
    if(!vl.length)return;
    const ch=g.sc?vl[Math.floor(Math.random()*vl.length)]:vl.reduce((b,d)=>{const nx2=(g.x+d.x+CL)%CL,ny2=(g.y+d.y+R)%R;return(Math.abs(nx2-pac.x)+Math.abs(ny2-pac.y))<(Math.abs((g.x+b.x+CL)%CL-pac.x)+Math.abs((g.y+b.y+R)%R-pac.y))?d:b;});
    g.dx=ch.x;g.dy=ch.y;g.x=(g.x+g.dx+CL)%CL;g.y=(g.y+g.dy+R)%R;
    if(g.x===pac.x&&g.y===pac.y){if(g.sc){g.dead=true;g.sc=false;sc+=200;document.getElementById('scEl').textContent=sc;}else{li--;document.getElementById('liEl').textContent=li;if(li<=0)over();}}
  });
  if(!map.flat().includes(1)&&!map.flat().includes(3)){lv++;document.getElementById('lvEl').textContent=lv;initMap();pac.x=10;pac.y=13;}
}
function draw2(){
  ctx.fillStyle='#000';ctx.fillRect(0,0,C.width,C.height);
  for(let r=0;r<R;r++)for(let cl=0;cl<CL;cl++){const v=map[r][cl],x=cl*SZ,y=r*SZ;if(v===0){ctx.fillStyle='#1e3a8a';ctx.fillRect(x,y,SZ,SZ);ctx.strokeStyle='#2563eb';ctx.strokeRect(x+1,y+1,SZ-2,SZ-2);}else if(v===1){ctx.fillStyle='#fef3c7';ctx.beginPath();ctx.arc(x+SZ/2,y+SZ/2,2,0,Math.PI*2);ctx.fill();}else if(v===3){ctx.fillStyle='#fbbf24';ctx.beginPath();ctx.arc(x+SZ/2,y+SZ/2,5,0,Math.PI*2);ctx.fill();}}
  const px=pac.x*SZ+SZ/2,py=pac.y*SZ+SZ/2,ang=dir.x<0?Math.PI:dir.y<0?Math.PI*1.5:dir.y>0?Math.PI*0.5:0;
  ctx.fillStyle='#facc15';ctx.beginPath();ctx.moveTo(px,py);ctx.arc(px,py,SZ/2-1,ang+pac.m,ang+Math.PI*2-pac.m);ctx.closePath();ctx.fill();
  gh.forEach(g=>{if(g.dead)return;const gx=g.x*SZ,gy=g.y*SZ;ctx.fillStyle=g.sc?(pwt<8&&Math.floor(pwt/2)%2===0?'#fff':'#3b82f6'):g.color;ctx.beginPath();ctx.arc(gx+SZ/2,gy+SZ/2,SZ/2-1,Math.PI,0);ctx.lineTo(gx+SZ-1,gy+SZ-3);for(let i=0;i<3;i++)ctx.lineTo(gx+SZ-1-(i+0.5)*(SZ-2)/3,gy+(i%2===0?SZ-6:SZ-2));ctx.lineTo(gx+1,gy+SZ-3);ctx.closePath();ctx.fill();if(!g.sc){ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(gx+6,gy+7,3,0,Math.PI*2);ctx.arc(gx+12,gy+7,3,0,Math.PI*2);ctx.fill();ctx.fillStyle='#000';ctx.beginPath();ctx.arc(gx+7,gy+8,1.5,0,Math.PI*2);ctx.arc(gx+13,gy+8,1.5,0,Math.PI*2);ctx.fill();}});
}
function over(){run=false;cancelAnimationFrame(aId);ov.innerHTML='<h2>'+(li>0?'&#127942; 클리어!':'&#128128; 게임 오버')+'</h2><p>점수: <strong style="color:#facc15">'+sc+'</strong></p><div style="display:flex;gap:10px"><button class="btn btn-b" onclick="exit()">나가기</button><button class="btn" onclick="go()">다시하기</button></div>';ov.style.display='flex';window.parent.postMessage({type:'GAME_SCORE',game:'pacman',score:sc},'*');}
function exit(){window.parent.postMessage({type:'GAME_EXIT',game:'pacman'},'*');}
document.addEventListener('keydown',e=>{const m={ArrowUp:{x:0,y:-1},ArrowDown:{x:0,y:1},ArrowLeft:{x:-1,y:0},ArrowRight:{x:1,y:0}};if(m[e.key]){nd=m[e.key];e.preventDefault();}});
['dU','dD','dL','dR'].forEach((id,i)=>{document.getElementById(id).addEventListener('click',()=>{nd=[{x:0,y:-1},{x:0,y:1},{x:-1,y:0},{x:1,y:0}][i];});});
draw2();
</script>
</body>
</html>"""

# File 3: Flappy
FLAPPY = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Flappy Bird</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#70c5ce;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;overflow:hidden;font-family:Arial,sans-serif;touch-action:none}
canvas{display:block;max-width:100vw;max-height:88vh}
#tip{color:white;font-size:13px;text-shadow:1px 1px 2px rgba(0,0,0,0.5);margin-bottom:4px}
#ov{position:fixed;inset:0;background:rgba(0,0,0,0.82);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;color:white}
#ov h2{font-size:28px;color:#facc15}
.btn{background:#facc15;color:#000;border:none;padding:12px 28px;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer}
.btn-b{background:#475569;color:#fff;margin-left:8px}
</style>
</head>
<body>
<div id="tip">탭/클릭/스페이스바로 날개짓!</div>
<canvas id="c"></canvas>
<div id="ov">
  <div style="font-size:48px">&#128038;</div>
  <h2>클럼지 버드</h2>
  <p style="color:#94a3b8">파이프 사이를 통과하세요!</p>
  <button class="btn" onclick="go()">시작하기</button>
</div>
<script>
const cv=document.getElementById('c'),ctx=cv.getContext('2d'),ov=document.getElementById('ov');
cv.width=320;cv.height=480;
const GR=300;
let bird,pipes,sc,best=0,run=false,aId,fr;
function Bird(){return{x:80,y:200,vy:0,a:0,flap(){this.vy=-7;}};}
function go(){bird=Bird();pipes=[];sc=0;fr=0;run=true;ov.style.display='none';cancelAnimationFrame(aId);loop();}
function loop(){update();draw3();aId=requestAnimationFrame(loop);}
function update(){
  if(!run)return;fr++;
  bird.vy+=0.38;bird.y+=bird.vy;bird.a=Math.min(Math.PI/2,bird.vy*0.055);
  if(fr%82===0)pipes.push({x:cv.width,top:Math.random()*(GR-140)+40,passed:false});
  pipes.forEach(p=>p.x-=2.2);pipes=pipes.filter(p=>p.x>-55);
  for(const p of pipes){
    if(!p.passed&&p.x+52<bird.x){p.passed=true;sc++;best=Math.max(best,sc);}
    if(bird.x+13>p.x&&bird.x-13<p.x+52&&(bird.y-13<p.top||bird.y+13>p.top+132))die();
  }
  if(bird.y+13>=GR||bird.y-13<0)die();
}
function draw3(){
  const sky=ctx.createLinearGradient(0,0,0,GR);sky.addColorStop(0,'#87CEEB');sky.addColorStop(1,'#b8e4f0');
  ctx.fillStyle=sky;ctx.fillRect(0,0,cv.width,cv.height);
  ctx.fillStyle='rgba(255,255,255,0.7)';[[40,70,22],[140,45,18],[250,80,26]].forEach(([x,y,r])=>{ctx.beginPath();ctx.arc((x-fr*0.3+cv.width)%cv.width,y,r,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(((x+20-fr*0.3)+cv.width)%cv.width,y,r*0.7,0,Math.PI*2);ctx.fill();});
  pipes.forEach(p=>{
    const g=ctx.createLinearGradient(p.x,0,p.x+52,0);g.addColorStop(0,'#3d8b20');g.addColorStop(0.4,'#74c442');g.addColorStop(1,'#3d8b20');
    ctx.fillStyle=g;ctx.fillRect(p.x,0,52,p.top);ctx.fillRect(p.x,p.top+132,52,GR-p.top-132);
    ctx.fillStyle='#3d8b20';ctx.fillRect(p.x-4,p.top-20,60,20);ctx.fillRect(p.x-4,p.top+132,60,20);
  });
  ctx.fillStyle='#c8a95a';ctx.fillRect(0,GR,cv.width,cv.height-GR);ctx.fillStyle='#5a9e2f';ctx.fillRect(0,GR-7,cv.width,9);
  ctx.save();ctx.translate(bird.x,bird.y);ctx.rotate(bird.a);
  ctx.fillStyle='#facc15';ctx.beginPath();ctx.ellipse(0,0,17,13,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#f59e0b';ctx.beginPath();ctx.ellipse(-3,4,13,5,-0.4,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(8,-4,5,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#1a1a2e';ctx.beginPath();ctx.arc(9,-4,3,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#f97316';ctx.beginPath();ctx.moveTo(14,-2);ctx.lineTo(20,0);ctx.lineTo(14,3);ctx.closePath();ctx.fill();
  ctx.restore();
  ctx.fillStyle='white';ctx.font='bold 26px Arial';ctx.textAlign='center';
  ctx.strokeStyle='rgba(0,0,0,0.4)';ctx.lineWidth=3;ctx.strokeText(sc,cv.width/2,50);ctx.fillText(sc,cv.width/2,50);
  ctx.textAlign='left';
}
function die(){run=false;cancelAnimationFrame(aId);ov.innerHTML='<h2>&#128165; 게임 오버!</h2><p>점수: <strong style="color:#facc15">'+sc+'</strong> 최고: <strong style="color:#4ade80">'+best+'</strong></p><div style="display:flex;gap:10px"><button class="btn btn-b" onclick="exit()">나가기</button><button class="btn" onclick="go()">다시하기</button></div>';ov.style.display='flex';window.parent.postMessage({type:'GAME_SCORE',game:'flappy',score:sc},'*');}
function exit(){window.parent.postMessage({type:'GAME_EXIT',game:'flappy'},'*');}
['click','touchstart'].forEach(e=>cv.addEventListener(e,ev=>{ev.preventDefault();if(run)bird.flap();}));
document.addEventListener('keydown',e=>{if(e.code==='Space'){if(run)bird.flap();e.preventDefault();}});
</script>
</body>
</html>"""

# File 4: Duck Hunt
DUCKHUNT = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Duck Hunt</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#87CEEB;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;overflow:hidden;font-family:Arial,sans-serif;user-select:none}
canvas{display:block;cursor:crosshair;max-width:100vw;max-height:80vh}
#hud{color:white;font-size:14px;font-weight:bold;text-shadow:1px 1px 3px rgba(0,0,0,0.7);margin-bottom:5px;display:flex;gap:18px}
#ov{position:fixed;inset:0;background:rgba(0,0,0,0.88);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;color:white}
#ov h2{font-size:28px;color:#ef4444}
.btn{background:#ef4444;color:#fff;border:none;padding:12px 28px;border-radius:8px;font-size:16px;font-weight:bold;cursor:pointer}
.btn-b{background:#475569;margin-left:8px}
</style>
</head>
<body>
<div id="hud"><span>&#127919; 점수: <span id="sc">0</span></span><span>&#128054; 남은: <span id="dk">10</span></span><span>&#128299; 탄환: <span id="am">3</span></span></div>
<canvas id="c"></canvas>
<div id="ov"><div style="font-size:48px">&#128054;</div><h2>덕 헌트</h2><p style="color:#94a3b8">오리를 클릭/터치해서 잡으세요!</p><button class="btn" onclick="go()">사냥 시작!</button></div>
<script>
const cv=document.getElementById('c'),ctx=cv.getContext('2d'),ov=document.getElementById('ov');
cv.width=400;cv.height=340;
const GR=290;
let ducks,sc,ammo,total,run,aId,fr,fx;
class Duck{
  constructor(){this.x=Math.random()<0.5?-40:cv.width+40;this.dx=this.x<0?2.5+Math.random()*1.5:-(2.5+Math.random()*1.5);this.y=30+Math.random()*(GR-80);this.dy=(Math.random()-0.5)*1.5;this.fl=0;this.fld=1;this.fall=false;this.vy=0;this.sz=24+Math.random()*10;this.color=['#8B4513','#228B22','#9b59b6','#e67e22'][Math.floor(Math.random()*4)];}
  update(){if(this.fall){this.vy+=0.4;this.y+=this.vy;return;}this.x+=this.dx;this.y+=this.dy;if(this.y<20)this.dy=Math.abs(this.dy);if(this.y>GR-30)this.dy=-Math.abs(this.dy);this.fl+=0.25*this.fld;if(Math.abs(this.fl)>0.4)this.fld*=-1;}
  draw(){ctx.save();ctx.translate(this.x,this.y);if(this.dx<0)ctx.scale(-1,1);const sz=this.sz;ctx.fillStyle=this.color;ctx.beginPath();ctx.ellipse(0,0,sz*0.6,sz*0.38,0,0,Math.PI*2);ctx.fill();ctx.fillStyle=this.color;ctx.beginPath();ctx.arc(sz*0.5,sz*-0.28,sz*0.26,0,Math.PI*2);ctx.fill();ctx.fillStyle='#2d7a2d';ctx.beginPath();ctx.ellipse(sz*0.28,-sz*0.06,sz*0.11,sz*0.18,0,0,Math.PI*2);ctx.fill();ctx.fillStyle=this.color;ctx.save();ctx.translate(-sz*0.1,0);ctx.rotate(this.fl);ctx.beginPath();ctx.ellipse(0,-sz*0.28,sz*0.18,sz*0.42,-0.5,0,Math.PI*2);ctx.fill();ctx.restore();ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(sz*0.58,-sz*0.32,sz*0.09,0,Math.PI*2);ctx.fill();ctx.fillStyle='#000';ctx.beginPath();ctx.arc(sz*0.6,-sz*0.32,sz*0.05,0,Math.PI*2);ctx.fill();ctx.fillStyle='#f97316';ctx.beginPath();ctx.moveTo(sz*0.73,-sz*0.26);ctx.lineTo(sz*0.98,-sz*0.22);ctx.lineTo(sz*0.73,-sz*0.16);ctx.closePath();ctx.fill();ctx.restore();}
  hit(mx,my){const dx=mx-this.x,dy=my-this.y;return Math.sqrt(dx*dx+dy*dy)<this.sz*0.75;}
}
function go(){ducks=[];sc=0;ammo=3;total=10;run=true;fr=0;fx=[];ov.style.display='none';['sc','dk','am'].forEach((id,i)=>document.getElementById(id).textContent=[0,10,3][i]);spawn();cancelAnimationFrame(aId);loop2();}
function spawn(){if(total>0&&ducks.filter(d=>!d.fall&&!d.gone).length<3){ducks.push(new Duck());total--;document.getElementById('dk').textContent=total;}}
function loop2(){step2();draw4();aId=requestAnimationFrame(loop2);}
function step2(){fr++;ducks.forEach(d=>d.update());ducks=ducks.filter(d=>!(d.fall&&d.y>cv.height+60));fx=fx.filter(f=>f.t<25);fx.forEach(f=>f.t++);if(fr%120===0)spawn();if(total===0&&ducks.length===0)over2();}
function draw4(){
  ctx.fillStyle='#87CEEB';ctx.fillRect(0,0,cv.width,cv.height);
  ctx.fillStyle='rgba(255,255,255,0.85)';[[55,45,20],[160,28,16],[290,55,24],[365,38,15]].forEach(([x,y,r])=>{ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(x+18,y,r*0.75,0,Math.PI*2);ctx.fill();});
  ctx.fillStyle='#4a7c2f';ctx.fillRect(0,GR,cv.width,cv.height-GR);ctx.fillStyle='#5a9e3d';ctx.fillRect(0,GR,cv.width,10);
  ctx.fillStyle='#3d6e20';[[48,GR],[148,GR],[296,GR],[375,GR]].forEach(([x,y])=>{ctx.beginPath();ctx.arc(x,y,18,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(x+12,y,14,0,Math.PI*2);ctx.fill();});
  ducks.forEach(d=>d.draw());
  fx.forEach(f=>{const a=1-f.t/25;ctx.fillStyle=f.hit?'rgba(255,120,0,'+a+')':'rgba(150,150,150,'+a+')';ctx.font='bold '+(14+f.t)+'px Arial';ctx.textAlign='center';ctx.fillText(f.hit?'HIT!':'MISS',f.x,f.y-f.t*0.8);ctx.textAlign='left';});
}
function shoot(mx,my){if(!run||ammo<=0)return;ammo--;document.getElementById('am').textContent=ammo;let hit=false;for(const d of ducks){if(!d.fall&&d.hit(mx,my)){d.fall=true;d.vy=-3;sc+=100;document.getElementById('sc').textContent=sc;fx.push({x:mx,y:my,t:0,hit:true});hit=true;break;}}if(!hit)fx.push({x:mx,y:my,t:0,hit:false});if(ammo<=0)setTimeout(()=>{ammo=3;document.getElementById('am').textContent=3;spawn();},900);}
function pos(e,touch){const r=cv.getBoundingClientRect(),sx=cv.width/r.width,sy=cv.height/r.height;return touch?{x:(e.touches[0].clientX-r.left)*sx,y:(e.touches[0].clientY-r.top)*sy}:{x:(e.clientX-r.left)*sx,y:(e.clientY-r.top)*sy};}
cv.addEventListener('click',e=>{const p=pos(e,false);shoot(p.x,p.y);});
cv.addEventListener('touchstart',e=>{e.preventDefault();const p=pos(e,true);shoot(p.x,p.y);});
function over2(){run=false;cancelAnimationFrame(aId);ov.innerHTML='<h2>&#127942; 사냥 완료!</h2><p>최종 점수: <strong style="color:#ef4444">'+sc+'</strong></p><div style="display:flex;gap:10px"><button class="btn btn-b" onclick="exit()">나가기</button><button class="btn" onclick="go()">다시하기</button></div>';ov.style.display='flex';window.parent.postMessage({type:'GAME_SCORE',game:'duckhunt',score:sc},'*');}
function exit(){window.parent.postMessage({type:'GAME_EXIT',game:'duckhunt'},'*');}
</script>
</body>
</html>"""

print("\nWriting snake/index.html...")
r = write_file('/var/www/somekorean/public/games/snake/index.html', SNAKE)
print("snake result:", r)

print("\nWriting pacman/index.html...")
r = write_file('/var/www/somekorean/public/games/pacman/index.html', PACMAN)
print("pacman result:", r)

print("\nWriting flappy/index.html...")
r = write_file('/var/www/somekorean/public/games/flappy/index.html', FLAPPY)
print("flappy result:", r)

print("\nWriting duckhunt/index.html...")
r = write_file('/var/www/somekorean/public/games/duckhunt/index.html', DUCKHUNT)
print("duckhunt result:", r)

print("\nVerifying files...")
for game in ['snake','pacman','flappy','duckhunt']:
    r = ssh('ls -la /var/www/somekorean/public/games/{}/'.format(game))
    print(game+":", r)

print("\nDone!")
