import paramiko, os, sys, time

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for _ in range(3):
    try: client.connect(HOST, username=USER, password=PASS, timeout=20); break
    except Exception as e: print(f'연결 실패: {e}'); time.sleep(3)

sftp = client.open_sftp()

def run(cmd, timeout=300):
    _, o, e = client.exec_command(cmd, timeout=timeout)
    out = o.read().decode('utf-8', errors='replace')
    err = e.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'>>> {cmd[:80]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write((out.strip()[-600:]+'\n').encode('utf-8'))
    if err.strip() and 'warn' not in err.lower() and 'deprecated' not in err.lower():
        sys.stdout.buffer.write(('ERR: '+err.strip()[-300:]+'\n').encode('utf-8'))
    sys.stdout.buffer.flush()

def upload(rel):
    local  = os.path.join(LOCAL, *rel.split('/'))
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {remote.rsplit("/",1)[0]}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'UP: {rel.split("/")[-1]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

files = [
    # 어드민 Vue 페이지 (전체)
    'resources/js/pages/admin/AdminLayout.vue',
    'resources/js/pages/admin/Overview.vue',
    'resources/js/pages/admin/Users.vue',
    'resources/js/pages/admin/Content.vue',
    'resources/js/pages/admin/Elder.vue',
    'resources/js/pages/admin/Business.vue',
    'resources/js/pages/admin/Rides.vue',
    'resources/js/pages/admin/GroupBuy.vue',
    'resources/js/pages/admin/Chats.vue',
    'resources/js/pages/admin/System.vue',

    # 라우터 (nested admin routes)
    'resources/js/router/index.js',

    # App.vue (isAdminPage 추가)
    'resources/js/App.vue',

    # API 라우트
    'routes/api.php',

    # AdminController
    'app/Http/Controllers/API/AdminController.php',
]

for f in files:
    upload(f)

run(f'cd {APP} && npm run build 2>&1 | tail -8', timeout=300)
run(f'cd {APP} && php8.2 artisan optimize:clear 2>&1 | tail -3')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write('\n=== Admin Dashboard Deploy Done ===\n'.encode('utf-8'))
sys.stdout.buffer.flush()
