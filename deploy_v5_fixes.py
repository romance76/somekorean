import paramiko, os, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for _ in range(3):
    try: client.connect(HOST, username=USER, password=PASS, timeout=20); break
    except Exception as e: time.sleep(3)

sftp = client.open_sftp()

def run(cmd, timeout=300):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-800:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-300:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

def upload(rel):
    local = os.path.join(LOCAL, *rel.split('/'))
    if not os.path.exists(local):
        sys.stdout.buffer.write(f'SKIP: {rel}\n'.encode('utf-8'))
        sys.stdout.buffer.flush()
        return False
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return True

# === V5 Fix Deploy ===
# 1. AdminLayout: 아코디언 사이드바
# 2. BoardManager: 카테고리 탭 버그 수정
# 3. AdminMatching: 본인인증 기능 추가
# 4. NewsDetail: 뉴스 본문 단락 표시 수정

files = [
    'resources/js/pages/admin/AdminLayout.vue',
    'resources/js/pages/admin/BoardManager.vue',
    'resources/js/pages/admin/AdminMatching.vue',
    'resources/js/pages/news/NewsDetail.vue',
]

sys.stdout.buffer.write(b'\n=== [V5] Uploading Fix Files ===\n')
sys.stdout.buffer.flush()
uploaded = 0
for f in files:
    if upload(f):
        uploaded += 1

sys.stdout.buffer.write(f'\nUploaded {uploaded}/{len(files)} files\n'.encode('utf-8'))

# 빌드
sys.stdout.buffer.write(b'\n=== Building Frontend ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && npm run build 2>&1 | tail -12', timeout=360)

# 캐시 클리어
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -3')

# 확인
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')
run(f'curl -s -o /dev/null -w " admin:%{{http_code}}" https://somekorean.com/admin')

sftp.close(); client.close()
sys.stdout.buffer.write(b'\n=== V5 Fix Deploy DONE ===\n')
sys.stdout.buffer.flush()
