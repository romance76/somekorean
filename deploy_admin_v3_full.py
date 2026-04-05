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

# === 전체 어드민 V3 배포 ===
files = [
    # Vue 어드민 페이지 (8개 팀 결과물)
    'resources/js/pages/admin/Members.vue',
    'resources/js/pages/admin/Payments.vue',
    'resources/js/pages/admin/Elder.vue',
    'resources/js/pages/admin/Business.vue',
    'resources/js/pages/admin/Rides.vue',
    'resources/js/pages/admin/GroupBuy.vue',
    'resources/js/pages/admin/Chats.vue',
    'resources/js/pages/admin/BoardManager.vue',
    'resources/js/pages/admin/SiteSettings.vue',
    # 기존 유지
    'resources/js/pages/admin/AdminLayout.vue',
    'resources/js/pages/admin/MenuManager.vue',
    'resources/js/pages/admin/Banners.vue',
    'resources/js/pages/admin/Overview.vue',
    # 라우터
    'resources/js/router/index.js',
    # 백엔드
    'routes/api.php',
    'app/Http/Controllers/API/AdminController.php',
    'app/Http/Controllers/API/AdminSettingsController.php',
    # 마이그레이션 & 시더
    'database/migrations/2026_03_29_000001_create_site_settings_table.php',
    'database/migrations/2026_03_29_000002_create_payments_table.php',
    'database/migrations/2026_03_29_000003_create_banners_table.php',
    'database/seeders/AdminDummyDataSeeder.php',
]

sys.stdout.buffer.write(b'\n=== Uploading Files ===\n')
sys.stdout.buffer.flush()
for f in files:
    upload(f)

# 마이그레이션
sys.stdout.buffer.write(b'\n=== Running Migrations ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1 | tail -10')

# 더미 데이터 시더 (기존 데이터가 있으면 스킵)
sys.stdout.buffer.write(b'\n=== Running Seeder ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan db:seed --class=AdminDummyDataSeeder --force 2>&1 | tail -8')

# 빌드
sys.stdout.buffer.write(b'\n=== Building Frontend ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && npm run build 2>&1 | tail -10', timeout=300)

# 캐시 초기화
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -3')

# 사이트 확인
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write(b'\n=== Admin V3 Full Deploy Complete ===\n')
sys.stdout.buffer.flush()
