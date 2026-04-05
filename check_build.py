import paramiko, sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=180):
    print(f'\n>>> {cmd[:80]}')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out:
        sys.stdout.buffer.write(out.encode('utf-8', errors='replace'))
        sys.stdout.buffer.write(b'\n')
        sys.stdout.buffer.flush()
    if err and 'Warning' not in err:
        sys.stdout.buffer.write(f'[ERR] {err[:300]}'.encode('utf-8', errors='replace'))
        sys.stdout.buffer.write(b'\n')
        sys.stdout.buffer.flush()

# 현재 빌드 상태 확인
run(f'ls -la {APP}/public/build/ 2>/dev/null')
run(f'ls {APP}/app/Http/Controllers/API/')

# 빌드 다시 실행
print('\n=== npm run build ===')
run(f'cd {APP} && npm run build 2>&1', timeout=180)

# 라우트 확인
run(f'cd {APP} && php8.2 artisan route:list --path=api --columns=method,uri 2>&1 | head -50')

client.close()
print('\nDONE')
