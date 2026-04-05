import paramiko
import os

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
DB_PASS = 'SK_DB@2026!secure'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print('Connecting...')
client.connect(HOST, username=USER, password=PASS, timeout=15)
print('Connected!')

sftp = client.open_sftp()

def run(cmd, show=True):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if show:
        if out: print('OUT:', out.strip())
        if err and 'Warning' not in err: print('ERR:', err.strip()[:300])
    return out, err

def upload(local_path, remote_path):
    # 디렉토리 생성
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}', show=False)
    sftp.put(local_path, remote_path)
    print(f'OK: {remote_path}')

# ─── 업로드할 파일들 ───────────────────────────────────────
files = [
    # 새 컨트롤러 3개
    (r'app\Http\Controllers\API\ProfileController.php',
     f'{APP}/app/Http/Controllers/API/ProfileController.php'),
    (r'app\Http\Controllers\API\SearchController.php',
     f'{APP}/app/Http/Controllers/API/SearchController.php'),
    (r'app\Http\Controllers\API\ReportController.php',
     f'{APP}/app/Http/Controllers/API/ReportController.php'),
    # 업데이트된 라우트
    (r'routes\api.php',
     f'{APP}/routes/api.php'),
]

print('\n=== [1/3] 파일 업로드 ===')
for local_rel, remote in files:
    local_full = os.path.join(LOCAL, local_rel)
    upload(local_full, remote)

print('\n=== [2/3] Laravel 캐시 클리어 ===')
run(f'cd {APP} && php8.2 artisan config:clear && php8.2 artisan route:clear && php8.2 artisan cache:clear')

print('\n=== [3/3] npm run build ===')
out, err = run(f'cd {APP} && npm run build 2>&1')
print(out[:2000] if out else '')
if err: print('ERR:', err[:500])

# 결과 확인
print('\n=== 결과 확인 ===')
run(f'ls {APP}/app/Http/Controllers/API/')
run(f'ls {APP}/public/build/assets/ | tail -5')
run(f'cd {APP} && php8.2 artisan route:list --path=api --columns=method,uri 2>&1 | grep -E "profile|search|report" | head -10')

sftp.close()
client.close()
print('\n=== 완료! ===')
