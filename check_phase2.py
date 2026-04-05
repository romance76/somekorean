import paramiko, sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=30):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:80]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:300]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

# Reverb 설치 여부
run(f'cd {APP} && php8.2 artisan reverb:start --help 2>&1 | head -5 || echo NO_REVERB')
# composer.json에 reverb 있는지
run(f'cat {APP}/composer.json | grep -E "reverb|broadcasting" | head -10')
# Redis 상태
run('redis-cli ping 2>/dev/null || echo NO_REDIS')
# Supervisor 상태
run('supervisorctl status 2>/dev/null || echo NO_SUPERVISOR_RUNNING')
run('ls /etc/supervisor/conf.d/')
# .env broadcast 설정
run(f'grep -E "BROADCAST|REVERB|REDIS" {APP}/.env | head -15')
# 기존 migrations 에 chat 관련 있는지
run(f'ls {APP}/database/migrations/ | grep -E "chat|elder|quiz"')
# package.json echo/pinia 확인
run(f'cat {APP}/package.json | grep -E "echo|pusher|pinia|socket" | head -10')

client.close()
print('\nDONE')
