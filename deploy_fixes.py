import paramiko
import os
import sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

def run(cmd, timeout=60):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:120]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err and 'Deprec' not in err:
        sys.stdout.buffer.write(f'[ERR] {err[:500]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}')
    sftp.put(local_path, remote_path)
    sys.stdout.buffer.write(f'  UP: {os.path.basename(remote_path)}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

print('\n=== Fix: NavBar 2-row + Matching + Omok + Dashboard ===')

files = [
    ('resources/js/components/NavBar.vue',            f'{APP}/resources/js/components/NavBar.vue'),
    ('resources/js/pages/profile/UserDashboard.vue',  f'{APP}/resources/js/pages/profile/UserDashboard.vue'),
    ('resources/js/pages/games/OmokGame.vue',         f'{APP}/resources/js/pages/games/OmokGame.vue'),
    ('resources/js/pages/match/MatchHome.vue',        f'{APP}/resources/js/pages/match/MatchHome.vue'),
    ('app/Http/Controllers/API/MatchController.php',  f'{APP}/app/Http/Controllers/API/MatchController.php'),
]

print('\n[1] Uploading...')
for rel, remote in files:
    upload(os.path.join(LOCAL, *rel.split('/')), remote)

print('\n[2] Clear laravel cache...')
run(f'cd {APP} && php artisan cache:clear && php artisan route:clear 2>&1')

print('\n[3] Building...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

print('\n[4] Test matching API...')
token = run(f"cd {APP} && php artisan tinker --execute=\"\\$u = App\\\\Models\\\\User::first(); echo auth('api')->login(\\$u);\"").strip()
run(f"curl -s 'https://somekorean.com/api/match/browse' -H 'Authorization: Bearer {token}' -w '\\nHTTP:%{{http_code}}' | tail -3")

print('\n[5] Site check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close()
client.close()
print('\n=== DONE ===')
