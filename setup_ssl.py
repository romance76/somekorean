import paramiko, sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:70]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:300]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out, err

# 사이트 동작 확인
run('curl -s -o /dev/null -w "%{http_code}" http://somekorean.com/')
run('curl -s http://somekorean.com/api/boards | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\'Boards: {len(d)}개\')" 2>/dev/null')
run('curl -s http://somekorean.com/ | grep -o "<title>.*</title>" | head -5')

# SSL 설치 여부 확인 및 설치
run('which certbot || apt-get install -y certbot python3-certbot-nginx 2>&1 | tail -5', timeout=120)
run('certbot --version 2>&1')

# 도메인 DNS 확인
run('dig somekorean.com +short | head -3 2>/dev/null || host somekorean.com | head -3')

# storage link
run(f'cd {APP} && php8.2 artisan storage:link 2>&1')

client.close()
print('\nDONE')
