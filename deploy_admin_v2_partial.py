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
        sys.stdout.buffer.write(f'SKIP (not found): {rel}\n'.encode('utf-8'))
        sys.stdout.buffer.flush()
        return False
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return True

# 완료된 파일들 업로드
files = [
    # AdminLayout (그룹 사이드바)
    'resources/js/pages/admin/AdminLayout.vue',
    # 새 Vue 페이지 (팀1, 팀3)
    'resources/js/pages/admin/MenuManager.vue',
    'resources/js/pages/admin/BoardManager.vue',
    'resources/js/pages/admin/SiteSettings.vue',
    # 라우터 + API
    'resources/js/router/index.js',
    'routes/api.php',
    # 백엔드 (팀5)
    'app/Http/Controllers/API/AdminSettingsController.php',
    # 마이그레이션
    'database/migrations/2026_03_29_000001_create_site_settings_table.php',
    'database/migrations/2026_03_29_000002_create_payments_table.php',
    'database/migrations/2026_03_29_000003_create_banners_table.php',
    # 시더
    'database/seeders/AdminDummyDataSeeder.php',
]

for f in files:
    upload(f)

# 마이그레이션 실행
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1 | tail -10')
# 더미 데이터 시더
run(f'cd {APP} && php8.2 artisan db:seed --class=AdminDummyDataSeeder --force 2>&1 | tail -5')
# 빌드
run(f'cd {APP} && npm run build 2>&1 | tail -6', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -3')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write(b'\n=== Partial Deploy Done ===\n')
sys.stdout.buffer.flush()
