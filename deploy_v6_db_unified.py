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

# === V6: DB 통일화 + 실제 데이터 연동 ===
files = [
    # 사이드바 상단 버튼 이동
    'resources/js/pages/admin/AdminLayout.vue',
    # 뉴스 오디오 제거 + 이미지 수정
    'resources/js/pages/news/NewsDetail.vue',
    'resources/js/pages/news/NewsList.vue',
    # 채팅 관리 실제 DB 연동
    'resources/js/pages/admin/Chats.vue',
    # 쇼핑 정보 실제 API 연동
    'resources/js/pages/admin/AdminShopping.vue',
    # 백엔드: 채팅 admin API + 쇼핑 admin API
    'app/Http/Controllers/API/AdminController.php',
    'routes/api.php',
    # 뉴스 RSS 이미지 개선
    'app/Console/Commands/FetchNews.php',
    # 쇼핑 RSS 명령어
    'app/Console/Commands/FetchShopping.php',
    # 쇼핑 DB 마이그레이션
    'database/migrations/2026_03_29_000010_create_shopping_deals_table.php',
    # 시더 버그 수정 (content→message)
    'database/seeders/AdminDummyDataSeeder.php',
]

sys.stdout.buffer.write(b'\n=== [V6] Uploading Files ===\n')
sys.stdout.buffer.flush()
uploaded = 0
for f in files:
    if upload(f):
        uploaded += 1

sys.stdout.buffer.write(f'\nUploaded {uploaded}/{len(files)} files\n'.encode('utf-8'))

# 마이그레이션 (shopping_deals 테이블 생성)
sys.stdout.buffer.write(b'\n=== Running Migrations ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1 | tail -8')

# 시더 실행 (chat_messages 필드 수정 + 데이터 채우기)
sys.stdout.buffer.write(b'\n=== Running Seeder ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan db:seed --class=AdminDummyDataSeeder --force 2>&1 | tail -8')

# 뉴스 RSS 가져오기 (실제 뉴스 + 이미지)
sys.stdout.buffer.write(b'\n=== Fetching Real News ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan news:fetch 2>&1 | tail -10', timeout=120)

# 쇼핑 딜 가져오기
sys.stdout.buffer.write(b'\n=== Fetching Shopping Deals ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan shopping:fetch 2>&1 | tail -10', timeout=60)

# 프론트엔드 빌드
sys.stdout.buffer.write(b'\n=== Building Frontend ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && npm run build 2>&1 | tail -12', timeout=360)

# 캐시 클리어
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -3')

# 확인
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')
run(f'curl -s -o /dev/null -w " admin:%{{http_code}}" https://somekorean.com/admin')

sftp.close(); client.close()
sys.stdout.buffer.write(b'\n=== V6 DB Unified Deploy DONE ===\n')
sys.stdout.buffer.flush()
