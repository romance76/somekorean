import paramiko, sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=120):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:70]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:500]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

# certbot으로 SSL 발급 (nginx 플러그인 사용, 자동 nginx 설정 수정)
run('certbot --nginx -d somekorean.com -d www.somekorean.com --non-interactive --agree-tos --email admin@somekorean.com --redirect 2>&1', timeout=120)

# nginx 설정 확인
run('nginx -t 2>&1')
run('systemctl reload nginx 2>&1')

# HTTPS 테스트
run('curl -s -o /dev/null -w "%{http_code}" https://somekorean.com/ 2>/dev/null')

client.close()
print('\nDONE')
