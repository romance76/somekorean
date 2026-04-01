import paramiko, os, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for _ in range(3):
    try: client.connect(HOST, username=USER, password=PASS, timeout=20); break
    except: time.sleep(3)

sftp = client.open_sftp()

def run(cmd, timeout=120):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-800:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-300:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

def upload(rel):
    local = os.path.join(LOCAL, *rel.split('/'))
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

sys.stdout.buffer.write(b'\n=== [Fix3] Shopping Links + News Images + Type Filter ===\n')
sys.stdout.buffer.flush()

files = [
    'resources/js/pages/shopping/ShoppingHome.vue',          # dealLink fix + type filter UI
    'app/Http/Controllers/API/ShoppingController.php',        # type filter in deals()
    'app/Console/Commands/UpdateNewsImages.php',              # new command
]

for f in files:
    upload(f)

sys.stdout.buffer.write(b'\n=== Building Frontend ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && npm run build 2>&1 | tail -5', timeout=180)

run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -2')

sys.stdout.buffer.write(b'\n=== Updating News Images (max 50) ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan news:update-images --limit=50 2>&1 | tail -20', timeout=120)

sys.stdout.buffer.write(b'\n=== Verify ===\n')
sys.stdout.buffer.flush()
run(f'mysql -u somekorean_user \"-pSK_DB@2026!secure\" somekorean -e "SELECT COUNT(*) total, SUM(image_url IS NOT NULL AND image_url != \'\') has_image FROM news;" 2>/dev/null')

sys.stdout.buffer.write(b'\n=== Fix3 DONE ===\n')
sys.stdout.buffer.flush()

sftp.close(); client.close()
