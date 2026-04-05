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

print('\n=== Phase 2 Deploy ===')

# ── 1. Migrations ─────────────────────────────────────────────────────────────
migrations = [
    '2026_03_27_000001_create_chat_rooms_table.php',
    '2026_03_27_000002_create_chat_messages_table.php',
    '2026_03_27_000003_create_elder_settings_table.php',
    '2026_03_27_000004_create_quiz_questions_table.php',
    '2026_03_27_000005_create_quiz_attempts_table.php',
]
print('\n[1] Uploading migrations...')
for f in migrations:
    upload(
        os.path.join(LOCAL, 'database', 'migrations', f),
        f'{APP}/database/migrations/{f}'
    )

# ── 2. Models ─────────────────────────────────────────────────────────────────
models = ['ChatRoom.php', 'ChatMessage.php', 'ElderSetting.php', 'QuizQuestion.php', 'QuizAttempt.php']
print('\n[2] Uploading models...')
for f in models:
    upload(os.path.join(LOCAL, 'app', 'Models', f), f'{APP}/app/Models/{f}')

# ── 3. Controllers ────────────────────────────────────────────────────────────
controllers = ['ChatController.php', 'ElderController.php', 'QuizController.php']
print('\n[3] Uploading controllers...')
for f in controllers:
    upload(
        os.path.join(LOCAL, 'app', 'Http', 'Controllers', 'API', f),
        f'{APP}/app/Http/Controllers/API/{f}'
    )

# ── 4. Event + Command ────────────────────────────────────────────────────────
print('\n[4] Uploading events & commands...')
upload(
    os.path.join(LOCAL, 'app', 'Events', 'MessageSent.php'),
    f'{APP}/app/Events/MessageSent.php'
)
upload(
    os.path.join(LOCAL, 'app', 'Console', 'Commands', 'ElderCheckCommand.php'),
    f'{APP}/app/Console/Commands/ElderCheckCommand.php'
)

# ── 5. Routes ─────────────────────────────────────────────────────────────────
print('\n[5] Uploading routes...')
upload(os.path.join(LOCAL, 'routes', 'api.php'),      f'{APP}/routes/api.php')
upload(os.path.join(LOCAL, 'routes', 'channels.php'), f'{APP}/routes/channels.php')

# ── 6. Supervisor reverb.conf ─────────────────────────────────────────────────
print('\n[6] Uploading reverb supervisor config...')
upload(os.path.join(LOCAL, 'reverb.conf'), '/etc/supervisor/conf.d/reverb.conf')

# ── 7. Vue files ──────────────────────────────────────────────────────────────
vue_files = [
    ('resources/js/pages/chat/ChatRooms.vue',           f'{APP}/resources/js/pages/chat/ChatRooms.vue'),
    ('resources/js/pages/chat/ChatRoom.vue',             f'{APP}/resources/js/pages/chat/ChatRoom.vue'),
    ('resources/js/pages/elder/ElderHome.vue',           f'{APP}/resources/js/pages/elder/ElderHome.vue'),
    ('resources/js/pages/elder/ElderCheckin.vue',        f'{APP}/resources/js/pages/elder/ElderCheckin.vue'),
    ('resources/js/pages/elder/GuardianDashboard.vue',   f'{APP}/resources/js/pages/elder/GuardianDashboard.vue'),
    ('resources/js/pages/games/QuizGame.vue',            f'{APP}/resources/js/pages/games/QuizGame.vue'),
    ('resources/js/router/index.js',                     f'{APP}/resources/js/router/index.js'),
    ('resources/js/components/NavBar.vue',               f'{APP}/resources/js/components/NavBar.vue'),
    ('resources/js/components/BottomNav.vue',            f'{APP}/resources/js/components/BottomNav.vue'),
]
print('\n[7] Uploading Vue files...')
for local_rel, remote in vue_files:
    upload(os.path.join(LOCAL, *local_rel.split('/')), remote)

# ── 8. Run migrations ─────────────────────────────────────────────────────────
print('\n[8] Running migrations...')
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1', timeout=60)

# ── 9. Seed chat rooms + quiz questions ───────────────────────────────────────
print('\n[9] Uploading and running quiz/chat seed...')
upload(
    os.path.join(LOCAL, 'database', 'quiz_seed.sql'),
    f'{APP}/database/quiz_seed.sql'
)
run(f'mysql -u somekorean_user -p\'SK_DB@2026!secure\' somekorean < {APP}/database/quiz_seed.sql 2>&1')

# ── 10. Add cron for elder:check ──────────────────────────────────────────────
print('\n[10] Adding cron job for elder:check...')
run('crontab -l 2>/dev/null | grep -v elder || true')
# Add if not already present
run('''(crontab -l 2>/dev/null; echo "0 * * * * cd /var/www/somekorean && php8.2 artisan elder:check >> /var/log/elder_check.log 2>&1") | sort -u | crontab -''')
run('crontab -l | grep elder')

# ── 11. Supervisor reload + start reverb ─────────────────────────────────────
print('\n[11] Starting Reverb via supervisor...')
run('supervisorctl reread 2>&1')
run('supervisorctl update 2>&1')
run('supervisorctl start reverb 2>&1 || supervisorctl restart reverb 2>&1')
run('supervisorctl status 2>&1')

# ── 12. Update .env VITE_ variables ──────────────────────────────────────────
print('\n[12] Checking .env for VITE_ reverb vars...')
out = run(f'grep -c "VITE_REVERB_APP_KEY" {APP}/.env 2>/dev/null || echo 0')
if out.strip() == '0':
    run(f'''echo '\nVITE_REVERB_APP_KEY="${{REVERB_APP_KEY}}"\nVITE_REVERB_HOST="${{REVERB_HOST}}"\nVITE_REVERB_PORT="${{REVERB_PORT}}"\nVITE_REVERB_SCHEME="${{REVERB_SCHEME}}"' >> {APP}/.env''')
    print('  Added VITE_REVERB_* to .env')
else:
    print('  VITE_REVERB_* already in .env')

# ── 13. Clear caches ─────────────────────────────────────────────────────────
print('\n[13] Clearing caches...')
run(f'cd {APP} && php8.2 artisan config:clear && php8.2 artisan cache:clear && php8.2 artisan route:clear 2>&1')

# ── 14. Build frontend ────────────────────────────────────────────────────────
print('\n[14] Building frontend (npm run build)...')
out = run(f'cd {APP} && npm run build 2>&1', timeout=180)
if 'error' in out.lower() and 'warn' not in out.lower():
    sys.stdout.buffer.write(b'[BUILD MAY HAVE ERRORS - check above]\n')

# ── 15. Reverb status check ───────────────────────────────────────────────────
print('\n[15] Final checks...')
run('supervisorctl status reverb 2>&1')
run(f'php8.2 {APP}/artisan reverb:start --help 2>&1 | head -3')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/ 2>/dev/null')

sftp.close()
client.close()
print('\n=== Phase 2 Deploy DONE ===')
