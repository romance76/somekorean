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

# === Admin V4 - 전체 완성 배포 ===
files = [
    # ── 레이아웃 & 라우터 ──
    'resources/js/pages/admin/AdminLayout.vue',
    'resources/js/router/index.js',

    # ── 기존 페이지 (수정됨) ──
    'resources/js/pages/admin/Members.vue',      # 빈화면 버그 수정 + 6탭
    'resources/js/pages/admin/Payments.vue',
    'resources/js/pages/admin/Elder.vue',
    'resources/js/pages/admin/Business.vue',
    'resources/js/pages/admin/Rides.vue',        # 드라이버 승인 + ACH 정산
    'resources/js/pages/admin/GroupBuy.vue',     # 기업전용 + ACH
    'resources/js/pages/admin/Chats.vue',        # 말풍선 UI + 신고관리
    'resources/js/pages/admin/BoardManager.vue', # 탭 버그 수정
    'resources/js/pages/admin/SiteSettings.vue',
    'resources/js/pages/admin/Banners.vue',
    'resources/js/pages/admin/MenuManager.vue',
    'resources/js/pages/admin/Overview.vue',

    # ── 신규 어드민 페이지 ──
    'resources/js/pages/admin/AdminJobs.vue',
    'resources/js/pages/admin/AdminMarket.vue',
    'resources/js/pages/admin/AdminClubs.vue',
    'resources/js/pages/admin/AdminEvents.vue',
    'resources/js/pages/admin/AdminShorts.vue',
    'resources/js/pages/admin/AdminGames.vue',
    'resources/js/pages/admin/AdminMatching.vue',
    'resources/js/pages/admin/AdminMentor.vue',
    'resources/js/pages/admin/AdminNews.vue',
    'resources/js/pages/admin/AdminAI.vue',
    'resources/js/pages/admin/AdminFriends.vue',
    'resources/js/pages/admin/AdminRealestate.vue',
    'resources/js/pages/admin/AdminShopping.vue',

    # ── 공개 페이지 (뉴스 표시 개선) ──
    'resources/js/pages/news/NewsDetail.vue',

    # ── 백엔드 ──
    'routes/api.php',
    'app/Http/Controllers/API/AdminController.php',
    'app/Http/Controllers/API/AdminSettingsController.php',

    # ── 시더 ──
    'database/seeders/AdminDummyDataSeeder.php',
]

sys.stdout.buffer.write(b'\n=== [V4] Uploading Files ===\n')
sys.stdout.buffer.flush()
uploaded = 0
for f in files:
    if upload(f):
        uploaded += 1

sys.stdout.buffer.write(f'\nUploaded {uploaded}/{len(files)} files\n'.encode('utf-8'))

# 마이그레이션
sys.stdout.buffer.write(b'\n=== Running Migrations ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1 | tail -5')

# 더미 데이터
sys.stdout.buffer.write(b'\n=== Running Seeder ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan db:seed --class=AdminDummyDataSeeder --force 2>&1 | tail -8')

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
sys.stdout.buffer.write(b'\n=== Admin V4 Complete Deploy DONE ===\n')
sys.stdout.buffer.flush()
