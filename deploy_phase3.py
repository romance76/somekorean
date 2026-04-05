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

print('\n=== Phase 3+4 Deploy (Ride + Match + Events + Demo Data) ===')

# ── 1. Migrations ──────────────────────────────────────────────────────────────
print('\n[1] Migrations...')
for f in ['2026_03_27_000006_create_rides_table.php', '2026_03_27_000007_create_match_tables.php']:
    upload(os.path.join(LOCAL, 'database', 'migrations', f), f'{APP}/database/migrations/{f}')

# ── 2. Models ──────────────────────────────────────────────────────────────────
print('\n[2] Models...')
for f in ['Ride.php','DriverProfile.php','RideReview.php','MatchProfile.php','MatchLike.php','Event.php']:
    upload(os.path.join(LOCAL, 'app', 'Models', f), f'{APP}/app/Models/{f}')

# ── 3. Controllers ─────────────────────────────────────────────────────────────
print('\n[3] Controllers...')
for f in ['RideController.php','DriverController.php','MatchController.php','EventController.php']:
    upload(os.path.join(LOCAL, 'app', 'Http', 'Controllers', 'API', f), f'{APP}/app/Http/Controllers/API/{f}')

# ── 4. Seeder ──────────────────────────────────────────────────────────────────
print('\n[4] Seeder...')
upload(
    os.path.join(LOCAL, 'database', 'seeders', 'DemoDataSeeder.php'),
    f'{APP}/database/seeders/DemoDataSeeder.php'
)

# ── 5. Vue pages ───────────────────────────────────────────────────────────────
print('\n[5] Vue pages...')
vue_files = [
    ('resources/js/pages/ride/RideMain.vue',           f'{APP}/resources/js/pages/ride/RideMain.vue'),
    ('resources/js/pages/ride/RideRequest.vue',        f'{APP}/resources/js/pages/ride/RideRequest.vue'),
    ('resources/js/pages/ride/RideHistory.vue',        f'{APP}/resources/js/pages/ride/RideHistory.vue'),
    ('resources/js/pages/ride/DriverDashboard.vue',    f'{APP}/resources/js/pages/ride/DriverDashboard.vue'),
    ('resources/js/pages/ride/DriverRegister.vue',     f'{APP}/resources/js/pages/ride/DriverRegister.vue'),
    ('resources/js/pages/match/MatchHome.vue',         f'{APP}/resources/js/pages/match/MatchHome.vue'),
    ('resources/js/pages/match/MatchBrowse.vue',       f'{APP}/resources/js/pages/match/MatchBrowse.vue'),
    ('resources/js/pages/match/MatchProfileSetup.vue', f'{APP}/resources/js/pages/match/MatchProfileSetup.vue'),
    ('resources/js/pages/events/EventList.vue',        f'{APP}/resources/js/pages/events/EventList.vue'),
    ('resources/js/pages/events/EventCreate.vue',      f'{APP}/resources/js/pages/events/EventCreate.vue'),
]
for local_rel, remote in vue_files:
    upload(os.path.join(LOCAL, *local_rel.split('/')), remote)

# ── 6. Router + Routes + PWA ──────────────────────────────────────────────────
print('\n[6] Router + Routes + PWA...')
upload(os.path.join(LOCAL, 'resources', 'js', 'router', 'index.js'), f'{APP}/resources/js/router/index.js')
upload(os.path.join(LOCAL, 'routes', 'api.php'), f'{APP}/routes/api.php')
upload(os.path.join(LOCAL, 'public', 'manifest.json'), f'{APP}/public/manifest.json')
upload(os.path.join(LOCAL, 'public', 'sw.js'), f'{APP}/public/sw.js')

# ── 7. Run migrations ─────────────────────────────────────────────────────────
print('\n[7] Running migrations...')
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1', timeout=60)

# ── 8. Run Demo Data Seeder ───────────────────────────────────────────────────
print('\n[8] Running DemoDataSeeder (50 records per table)...')
run(f'cd {APP} && php8.2 artisan db:seed --class=DemoDataSeeder --force 2>&1', timeout=120)

# ── 9. Clear caches ───────────────────────────────────────────────────────────
print('\n[9] Clearing caches...')
run(f'cd {APP} && php8.2 artisan config:clear && php8.2 artisan cache:clear && php8.2 artisan route:clear 2>&1')

# ── 10. Build frontend ────────────────────────────────────────────────────────
print('\n[10] Building frontend...')
run(f'cd {APP} && npm run build 2>&1', timeout=240)

# ── 11. PWA manifest link in blade ───────────────────────────────────────────
print('\n[11] Checking manifest link in index.blade.php...')
out = run(f'grep -c "manifest.json" {APP}/resources/views/app.blade.php 2>/dev/null || echo 0')
if out.strip() == '0':
    run(f'''sed -i 's|</head>|    <link rel="manifest" href="/manifest.json">\\n    <meta name="theme-color" content="#2563eb">\\n    <link rel="apple-touch-icon" href="/icons/icon-192x192.png">\\n</head>|' {APP}/resources/views/app.blade.php''')
    print('  manifest link added to blade')
else:
    print('  manifest already linked')

# ── 12. Check data counts ─────────────────────────────────────────────────────
print('\n[12] DB counts...')
run(f'mysql -u somekorean_user -p\'SK_DB@2026!secure\' somekorean -e "SELECT \'users\' AS tbl, COUNT(*) AS cnt FROM users UNION SELECT \'posts\', COUNT(*) FROM posts UNION SELECT \'job_posts\', COUNT(*) FROM job_posts UNION SELECT \'market_items\', COUNT(*) FROM market_items UNION SELECT \'businesses\', COUNT(*) FROM businesses UNION SELECT \'quiz_questions\', COUNT(*) FROM quiz_questions UNION SELECT \'chat_rooms\', COUNT(*) FROM chat_rooms UNION SELECT \'rides\' AS tbl, COUNT(*) AS cnt FROM rides UNION SELECT \'events\', COUNT(*) FROM events;" 2>/dev/null')

# ── 13. Final check ───────────────────────────────────────────────────────────
print('\n[13] Final site check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close()
client.close()
print('\n=== Phase 3+4 Deploy DONE ===')
