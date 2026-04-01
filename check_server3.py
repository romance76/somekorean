import paramiko

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
DB_PASS = 'SK_DB@2026!secure'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd):
    print(f'\n>>> {cmd[:80]}')
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out.strip())
    if err: print('[ERR]', err.strip()[:200])

# boards/admin 데이터 확인
run(f'mysql -u somekorean_user -p{DB_PASS} somekorean -e "SELECT COUNT(*) as boards FROM boards;" 2>/dev/null')
run(f'mysql -u somekorean_user -p{DB_PASS} somekorean -e "SELECT COUNT(*) as users FROM users;" 2>/dev/null')
# node_modules 상태
run(f'ls {APP}/node_modules/.package-lock.json 2>/dev/null && echo MODULES_OK || echo NO_MODULES')
run(f'ls {APP}/node_modules/tailwindcss/ 2>/dev/null | head -3 || echo NO_TAILWIND')
# 현재 api.php 라우트 수
run(f'grep -c "Route::" {APP}/routes/api.php')

client.close()
print('\nDONE')
