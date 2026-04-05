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
    if err: print('[ERR]', err.strip()[:300])

run(f'ls {APP}/database/migrations/')
run(f'cat {APP}/tailwind.config.js 2>/dev/null || cat {APP}/tailwind.config.ts 2>/dev/null || echo NO_TAILWIND_CONFIG')
run(f'cat {APP}/vite.config.js 2>/dev/null || cat {APP}/vite.config.ts 2>/dev/null')
run(f'cat {APP}/resources/css/app.css 2>/dev/null | head -10')
run(f'mysql -u somekorean_user -p{DB_PASS} somekorean -e "SHOW TABLES;" 2>&1')
run(f'cd {APP} && php8.2 artisan migrate:status 2>&1 | head -30')

client.close()
print('\nDONE')
