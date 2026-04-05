import paramiko, os, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for _ in range(3):
    try: client.connect(HOST, username=USER, password=PASS, timeout=20); break
    except Exception as e: print(f'연결 재시도... {e}'); time.sleep(3)

sftp = client.open_sftp()

def run(cmd, timeout=300):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-600:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-300:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

def upload(rel):
    local  = os.path.join(LOCAL, *rel.split('/'))
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

files = [
    # UI 컴포넌트
    'resources/js/components/NavBar.vue',
    'resources/js/components/Footer.vue',      # NEW
    # 페이지
    'resources/js/pages/Home.vue',
    'resources/js/pages/community/BoardList.vue',
    'resources/js/pages/chat/ChatRooms.vue',   # CSS fix (top: 48px mobile)
    # 앱 루트 (BottomNav 제거, Footer 추가)
    'resources/js/App.vue',
    # 라우터 (커뮤니티 → BoardList, /community/qna → QnAHome)
    'resources/js/router/index.js',
    # Phase 5 시드 데이터
    'database/seeders/Phase5DataSeeder.php',   # NEW
]

for f in files:
    upload(f)

# 빌드
run(f'cd {APP} && npm run build 2>&1 | tail -8', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -3')

# Phase 5 시드 데이터 실행
print('\n=== 시드 데이터 (clubs, group_buys, mentors, rides) 실행 ===')
run(f'cd {APP} && php8.2 artisan db:seed --class=Phase5DataSeeder --force 2>&1 | tail -10', timeout=120)

# 헬스체크
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write('\n=== Deploy Done ===\n'.encode('utf-8'))
sys.stdout.buffer.flush()
