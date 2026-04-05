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

print('\n=== Phase 8 (검색 픽스 + 이벤트 RSVP + EventDetail + 프로필수정) ===')

# 1. Migration
print('\n[1] Migration...')
upload(os.path.join(LOCAL,'database','migrations','2026_03_27_000010_create_event_attendees_table.php'),
       f'{APP}/database/migrations/2026_03_27_000010_create_event_attendees_table.php')

# 2. EventController
print('\n[2] EventController...')
upload(os.path.join(LOCAL,'app','Http','Controllers','API','EventController.php'),
       f'{APP}/app/Http/Controllers/API/EventController.php')

# 3. Routes
print('\n[3] Routes...')
upload(os.path.join(LOCAL,'routes','api.php'), f'{APP}/routes/api.php')

# 4. Vue pages
print('\n[4] Vue pages...')
pages = [
    ('resources/js/pages/Search.vue',                f'{APP}/resources/js/pages/Search.vue'),
    ('resources/js/pages/events/EventDetail.vue',    f'{APP}/resources/js/pages/events/EventDetail.vue'),
    ('resources/js/pages/Home.vue',                  f'{APP}/resources/js/pages/Home.vue'),
    ('resources/js/router/index.js',                 f'{APP}/resources/js/router/index.js'),
]
for rel, remote in pages:
    upload(os.path.join(LOCAL, *rel.split('/')), remote)

# 5. Migrate
print('\n[5] Running migration...')
run(f'cd {APP} && php8.2 artisan migrate --force 2>&1', timeout=60)

# 6. Route cache clear
print('\n[6] Clearing caches...')
run(f'cd {APP} && php8.2 artisan route:clear && php8.2 artisan config:clear 2>&1')

# 7. Build
print('\n[7] Building...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

# 8. Final check
print('\n[8] Final check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')
run(f'curl -s "https://somekorean.com/api/search?q=한인" | head -c 200')

sftp.close()
client.close()
print('\n=== Phase 8 DONE ===')
