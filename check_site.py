import paramiko, sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=30):
    print(f'\n>>> {cmd[:80]}')
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR]{err[:200]}'.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    sys.stdout.buffer.flush()
    return out

# API 라우트 목록
run(f'cd {APP} && php8.2 artisan route:list --path=api 2>&1 | head -60')

# Vue 소스 파일 확인
run(f'ls {APP}/resources/js/views/ 2>/dev/null | head -20 || echo NO_VIEWS_DIR')
run(f'ls {APP}/resources/js/ 2>/dev/null')

# nginx 설정 확인
run('nginx -t 2>&1')
run('systemctl is-active nginx')

# 사이트 응답 테스트
run('curl -s -o /dev/null -w "%{http_code}" https://somekorean.com/ 2>/dev/null || curl -s -o /dev/null -w "%{http_code}" http://somekorean.com/')
run('curl -s https://somekorean.com/api/boards 2>/dev/null | head -200 || curl -s http://somekorean.com/api/boards | head -200')

client.close()
print('\nDONE')
