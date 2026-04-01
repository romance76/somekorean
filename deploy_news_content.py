import paramiko, os, sys
HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()
def run(cmd, timeout=300):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:100]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write(out.strip()[-500:].encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err and 'Deprec' not in err:
        sys.stdout.buffer.write(f'ERR: {err[:200]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

files = [
    'database/migrations/2025_01_01_000015_add_content_to_news.php',
    'app/Models/News.php',
    'app/Http/Controllers/API/NewsController.php',
    'app/Console/Commands/FetchNews.php',
    'app/Console/Commands/SeedRecentNews.php',
    'routes/api.php',
]

sys.stdout.buffer.write(b'[1] Uploading files...\n'); sys.stdout.buffer.flush()
for rel in files:
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {os.path.dirname(remote)}')
    sftp.put(os.path.join(LOCAL, *rel.split('/')), remote)
    sys.stdout.buffer.write(f'  UP: {rel.split("/")[-1]}\n'.encode('utf-8')); sys.stdout.buffer.flush()

sys.stdout.buffer.write(b'\n[2] Running migration...\n'); sys.stdout.buffer.flush()
run(f'cd {APP} && php artisan migrate --force 2>&1')

sys.stdout.buffer.write(b'\n[3] Seeding news with full content...\n'); sys.stdout.buffer.flush()
run(f'cd {APP} && php artisan news:seed 2>&1')

sys.stdout.buffer.write(b'\n[4] Clearing cache...\n'); sys.stdout.buffer.flush()
run(f'cd {APP} && php artisan cache:clear && php artisan route:clear && php artisan config:clear 2>&1')

sys.stdout.buffer.write(b'\n[5] Testing API endpoint...\n'); sys.stdout.buffer.flush()
run(f'curl -s https://somekorean.com/api/news/1 | head -c 500 2>&1')

sys.stdout.buffer.write(b'\n[6] Done!\n'); sys.stdout.buffer.flush()
sftp.close()
client.close()
