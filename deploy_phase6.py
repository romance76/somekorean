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
    if err and 'Warning' not in err: sys.stdout.buffer.write(f'[ERR] {err[:500]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}')
    sftp.put(local_path, remote_path)
    sys.stdout.buffer.write(f'  UP: {remote_path}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()

print('\n=== Phase 6 (포커 + 알림 + 뉴스 + 홈 + NavBar) ===')

# ── 1. Migration ──────────────────────────────────────────────────────────────
print('\n[1] Migration...')
upload(os.path.join(LOCAL,'database','migrations','2026_03_27_000009_create_notifications_table.php'),
       f'{APP}/database/migrations/2026_03_27_000009_create_notifications_table.php')

# ── 2. Models ─────────────────────────────────────────────────────────────────
print('\n[2] Models...')
upload(os.path.join(LOCAL,'app','Models','Notification.php'), f'{APP}/app/Models/Notification.php')

# ── 3. Controllers ────────────────────────────────────────────────────────────
print('\n[3] Controllers...')
for f in ['PokerController.php','NotificationController.php']:
    upload(os.path.join(LOCAL,'app','Http','Controllers','API',f), f'{APP}/app/Http/Controllers/API/{f}')

# ── 4. Vue pages ──────────────────────────────────────────────────────────────
print('\n[4] Vue pages...')
vue_files = [
    ('resources/js/pages/games/Poker.vue',      f'{APP}/resources/js/pages/games/Poker.vue'),
    ('resources/js/pages/games/GameLobby.vue',  f'{APP}/resources/js/pages/games/GameLobby.vue'),
    ('resources/js/pages/Notifications.vue',    f'{APP}/resources/js/pages/Notifications.vue'),
    ('resources/js/pages/news/NewsList.vue',    f'{APP}/resources/js/pages/news/NewsList.vue'),
    ('resources/js/pages/Home.vue',             f'{APP}/resources/js/pages/Home.vue'),
    ('resources/js/components/NavBar.vue',      f'{APP}/resources/js/components/NavBar.vue'),
]
for local_rel, remote in vue_files:
    upload(os.path.join(LOCAL, *local_rel.split('/')), remote)

# ── 5. Routes + Router ────────────────────────────────────────────────────────
print('\n[5] Routes + Router...')
upload(os.path.join(LOCAL,'routes','api.php'), f'{APP}/routes/api.php')
upload(os.path.join(LOCAL,'resources','js','router','index.js'), f'{APP}/resources/js/router/index.js')

# ── 6. Migrate ────────────────────────────────────────────────────────────────
print('\n[6] Running migration...')
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1', timeout=60)

# ── 7. Clear caches ───────────────────────────────────────────────────────────
print('\n[7] Clearing caches...')
run(f'cd {APP} && php8.2 artisan config:clear && php8.2 artisan route:clear && php8.2 artisan cache:clear 2>&1')

# ── 8. Build ──────────────────────────────────────────────────────────────────
print('\n[8] Building frontend...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

# ── 9. Final check ────────────────────────────────────────────────────────────
print('\n[9] Final check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close()
client.close()
print('\n=== Phase 6 DONE ===')
