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
    sys.stdout.buffer.write(f'\n>>> {cmd[:80]}\n'.encode('utf-8'))
    if out: sys.stdout.buffer.write(out.encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:400]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}')
    sftp.put(local_path, remote_path)
    sys.stdout.buffer.write(f'  UP: {remote_path}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

print('\n=== Phase 5 Deploy (게임 로비 + 고스톱 + 리더보드 + 포인트샵) ===')

# ── 1. Migration ──────────────────────────────────────────────────────────────
print('\n[1] Migration...')
upload(
    os.path.join(LOCAL, 'database', 'migrations', '2026_03_27_000008_create_game_rooms_table.php'),
    f'{APP}/database/migrations/2026_03_27_000008_create_game_rooms_table.php'
)

# ── 2. Models ─────────────────────────────────────────────────────────────────
print('\n[2] Models...')
for f in ['GameRoom.php', 'GamePlayer.php']:
    upload(os.path.join(LOCAL, 'app', 'Models', f), f'{APP}/app/Models/{f}')

# ── 3. Controllers ────────────────────────────────────────────────────────────
print('\n[3] Controller...')
upload(os.path.join(LOCAL, 'app', 'Http', 'Controllers', 'API', 'GameController.php'),
       f'{APP}/app/Http/Controllers/API/GameController.php')

# ── 4. Events ─────────────────────────────────────────────────────────────────
print('\n[4] Event...')
upload(os.path.join(LOCAL, 'app', 'Events', 'GameStateChanged.php'),
       f'{APP}/app/Events/GameStateChanged.php')

# ── 5. Vue pages ──────────────────────────────────────────────────────────────
print('\n[5] Vue pages...')
vue_files = [
    ('resources/js/pages/games/GameLobby.vue',   f'{APP}/resources/js/pages/games/GameLobby.vue'),
    ('resources/js/pages/games/GoStop.vue',      f'{APP}/resources/js/pages/games/GoStop.vue'),
    ('resources/js/pages/games/Leaderboard.vue', f'{APP}/resources/js/pages/games/Leaderboard.vue'),
    ('resources/js/pages/games/PointShop.vue',   f'{APP}/resources/js/pages/games/PointShop.vue'),
]
for local_rel, remote in vue_files:
    upload(os.path.join(LOCAL, *local_rel.split('/')), remote)

# ── 6. Routes + Router ────────────────────────────────────────────────────────
print('\n[6] Routes + Router...')
upload(os.path.join(LOCAL, 'routes', 'api.php'), f'{APP}/routes/api.php')
upload(os.path.join(LOCAL, 'resources', 'js', 'router', 'index.js'), f'{APP}/resources/js/router/index.js')

# ── 7. Migrate ────────────────────────────────────────────────────────────────
print('\n[7] Running migration...')
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1', timeout=60)

# ── 8. Clear caches ───────────────────────────────────────────────────────────
print('\n[8] Clearing caches...')
run(f'cd {APP} && php8.2 artisan config:clear && php8.2 artisan route:clear && php8.2 artisan cache:clear 2>&1')

# ── 9. Build frontend ─────────────────────────────────────────────────────────
print('\n[9] Building frontend...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

# ── 10. Final check ───────────────────────────────────────────────────────────
print('\n[10] Final site check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close()
client.close()
print('\n=== Phase 5 Deploy DONE ===')
