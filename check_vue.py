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
    sys.stdout.buffer.write(f'>>> {cmd[:70]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR]{err[:200]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

# Vue 페이지 구조
run(f'find {APP}/resources/js -name "*.vue" | sort')
run(f'find {APP}/resources/js -name "*.js" | grep -v node | sort')

# API 실제 응답 확인
run(f'curl -s http://somekorean.com/api/boards 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); [print(b[\'name\'], b[\'slug\']) for b in d.get(\'data\',[d] if isinstance(d,dict) else d)]" 2>/dev/null || curl -s http://somekorean.com/api/boards | head -300')

# Nginx 설정 확인 (SSL/도메인)
run('cat /etc/nginx/sites-available/somekorean 2>/dev/null || cat /etc/nginx/sites-enabled/somekorean 2>/dev/null | head -40')

# SSL 인증서 상태
run('certbot certificates 2>/dev/null | head -20 || echo NO_CERTBOT')

client.close()
print('\nDONE')
