import paramiko, os, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for _ in range(3):
    try: client.connect(HOST, username=USER, password=PASS, timeout=20); break
    except Exception as e: time.sleep(3)

sftp = client.open_sftp()

def run(cmd, timeout=120):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-1000:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-400:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

def upload(rel):
    local = os.path.join(LOCAL, *rel.split('/'))
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

sys.stdout.buffer.write(b'\n=== [V6 Fix2] News Cleanup + Shopping Data ===\n')
sys.stdout.buffer.flush()

files = [
    'resources/js/pages/news/NewsDetail.vue',      # audio strip fix for plain text
    'app/Models/ShoppingDeal.php',                  # updated fillable
    'database/migrations/2026_03_29_000012_fix_shopping_deals_add_store_columns.php',
    'database/seeders/ShoppingSeeder.php',
]

for f in files:
    upload(f)

sys.stdout.buffer.write(b'\n=== Running Migration ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1 | tail -6')

sys.stdout.buffer.write(b'\n=== Seeding Shopping Data ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && php8.2 artisan db:seed --class=ShoppingSeeder 2>&1 | tail -10')

sys.stdout.buffer.write(b'\n=== Building Frontend ===\n')
sys.stdout.buffer.flush()
run(f'cd {APP} && npm run build 2>&1 | tail -5', timeout=180)

run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -3')

sys.stdout.buffer.write(b'\n=== Verify ===\n')
sys.stdout.buffer.flush()
run(f'curl -s "http://localhost/api/shopping/stores" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\'stores: {{len(d)}}건\')" 2>&1')
run(f'curl -s "http://localhost/api/shopping/deals" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\'deals: {{d[\\\"total\\\"]}}건\')" 2>&1')

sys.stdout.buffer.write(b'\n=== Fix2 DONE ===\n')
sys.stdout.buffer.flush()

sftp.close(); client.close()
