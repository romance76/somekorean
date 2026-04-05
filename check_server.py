import paramiko

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd):
    print(f'\n>>> {cmd[:80]}')
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out.strip())
    if err: print('[ERR]', err.strip()[:300])

run(f'ls {APP}/app/Http/Controllers/API/')
run(f'ls {APP}/database/ 2>/dev/null || echo NO_DATABASE_DIR')
run(f'mysql -u somekorean_user -pEhdRh0817wodl somekorean -e "SHOW TABLES;" 2>/dev/null || mysql -uroot -pEhdRh0817wodl somekorean -e "SHOW TABLES;" 2>/dev/null || echo NO_TABLES')
run(f'grep -E "DB_HOST|DB_DATABASE|DB_USERNAME|DB_PASSWORD|APP_URL" {APP}/.env 2>/dev/null | head -10')
run(f'node --version && npm --version')
run(f'cat {APP}/package.json | grep -E "tailwind|vite|vue" | head -20')
run(f'php8.2 --version | head -1')
run(f'ls {APP}/public/build/ 2>/dev/null || echo NO_BUILD')

client.close()
print('\nDONE')
