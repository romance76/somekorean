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
    if err and 'Warning' not in err and 'Deprecat' not in err:
        sys.stdout.buffer.write(f'[ERR] {err[:500]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}')
    sftp.put(local_path, remote_path)
    sys.stdout.buffer.write(f'  UP: {os.path.basename(remote_path)}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

print('\n=== 대규모 업데이트: NavBar + Dashboard + 게임 + 친구 + 코인규칙 ===')

files = [
    # NavBar
    ('resources/js/components/NavBar.vue',                f'{APP}/resources/js/components/NavBar.vue'),
    # Dashboard fix
    ('resources/js/pages/profile/UserDashboard.vue',      f'{APP}/resources/js/pages/profile/UserDashboard.vue'),
    # App.vue
    ('resources/js/App.vue',                              f'{APP}/resources/js/App.vue'),
    # Router
    ('resources/js/router/index.js',                      f'{APP}/resources/js/router/index.js'),
    # Games
    ('resources/js/pages/games/BingoGame.vue',            f'{APP}/resources/js/pages/games/BingoGame.vue'),
    ('resources/js/pages/games/OmokGame.vue',             f'{APP}/resources/js/pages/games/OmokGame.vue'),
    ('resources/js/pages/games/GameLobby.vue',            f'{APP}/resources/js/pages/games/GameLobby.vue'),
    # Point rules
    ('resources/js/pages/PointRules.vue',                 f'{APP}/resources/js/pages/PointRules.vue'),
    # Friends
    ('resources/js/pages/friends/FriendList.vue',         f'{APP}/resources/js/pages/friends/FriendList.vue'),
    # Backend: Friend
    ('app/Models/Friend.php',                             f'{APP}/app/Models/Friend.php'),
    ('app/Http/Controllers/API/FriendController.php',     f'{APP}/app/Http/Controllers/API/FriendController.php'),
    ('database/migrations/2025_01_01_000010_create_friends_table.php',
                                                          f'{APP}/database/migrations/2025_01_01_000010_create_friends_table.php'),
    # API routes
    ('routes/api.php',                                    f'{APP}/routes/api.php'),
]

print('\n[1] Uploading...')
for rel, remote in files:
    upload(os.path.join(LOCAL, *rel.split('/')), remote)

print('\n[2] Migrate friends table...')
run(f'cd {APP} && php artisan migrate --force 2>&1', timeout=60)

print('\n[3] Building...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

print('\n[4] Check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close()
client.close()
print('\n=== DONE ===')
