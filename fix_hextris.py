import paramiko, base64

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
<div id="ctrl"><button class="cb" id="bL">LEFT</button><button class="cb" id="bR">RIGHT</button></div>
<div id="ov">
  <h2>HEXTRIS</h2>
  <p style="color:#94a3b8">블록이 중심으로 떨어집니다!</p>
  <p style="color:#94a3b8">같은 색 3개 이상 제거!</p>
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
  ctx.fillStyle='#818cf8';ctx.font='bold '+Math.floor(rw*0.5)+'px Arial';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(sc,CX,CY);
}
function over(){run=false;cancelAnimationFrame(aId);ov.innerHTML='<h2>Game Over!</h2><p>Score: <strong style="color:#818cf8">'+sc+'</strong></p><div style="display:flex;gap:10px"><button class="btn btn-b" onclick="exit()">Exit</button><button class="btn" onclick="go()">Retry</button></div>';ov.style.display='flex';window.parent.postMessage({type:'GAME_SCORE',game:'hextris',score:sc},'*');}
function exit(){window.parent.postMessage({type:'GAME_EXIT',game:'hextris'},'*');}
document.getElementById('bL').addEventListener('click',function(){rot(-1);});
document.getElementById('bR').addEventListener('click',function(){rot(1);});
document.addEventListener('keydown',function(e){if(e.key==='a'||e.key==='ArrowLeft')rot(-1);if(e.key==='d'||e.key==='ArrowRight')rot(1);});
var tx=0;cv.addEventListener('touchstart',function(e){tx=e.touches[0].clientX;});
cv.addEventListener('touchend',function(e){var dx=e.changedTouches[0].clientX-tx;if(Math.abs(dx)>30)rot(dx>0?1:-1);});
ctx.fillStyle='#0f172a';ctx.fillRect(0,0,SZ,SZ);
</script>
</body>
</html>'''

print("=== Fixing hextris/index.html ===")
r = write_file('/var/www/somekorean/public/games/hextris/index.html', hextris_html)
print("hextris:", r)

print("\n=== Verifying all files ===")
print(ssh('ls -lh /var/www/somekorean/public/games/slots/index.html /var/www/somekorean/public/games/hextris/index.html /var/www/somekorean/public/games/mahjong/index.html'))
