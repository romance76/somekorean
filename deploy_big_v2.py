import paramiko, os, sys

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, username=USER, password=PASS, timeout=15)
sftp = client.open_sftp()

def run(cmd, timeout=120):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(f'\n>>> {cmd[:120]}\n'.encode('utf-8'))
    if out.strip(): sys.stdout.buffer.write(out.strip()[:600].encode('utf-8')); sys.stdout.buffer.write(b'\n')
    if err and 'Warning' not in err and 'Deprec' not in err:
        sys.stdout.buffer.write(f'[ERR] {err[:300]}\n'.encode('utf-8'))
    sys.stdout.buffer.flush()
    return out

def upload(rel):
    local = os.path.join(LOCAL, *rel.split('/'))
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {os.path.dirname(remote)}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'  UP: {rel.split("/")[-1]}\n'.encode('utf-8')); sys.stdout.buffer.flush()

sys.stdout.buffer.write(b'\n=== Big V2 Deploy ===\n'); sys.stdout.buffer.flush()

# All files to upload
files = [
    # New components
    'resources/js/components/LocationFilter.vue',
    'resources/js/components/NavBar.vue',
    # Modified pages
    'resources/js/pages/Notifications.vue',
    'resources/js/pages/messages/MessageInbox.vue',
    'resources/js/pages/profile/UserDashboard.vue',
    'resources/js/pages/directory/BusinessList.vue',
    'resources/js/pages/jobs/JobList.vue',
    'resources/js/pages/market/MarketList.vue',
    'resources/js/pages/community/ClubList.vue',
    'resources/js/pages/match/MatchHome.vue',
    'resources/js/pages/chat/ChatRoom.vue',
    # Backend
    'app/Models/Club.php',
    'app/Models/ClubMember.php',
    'app/Http/Controllers/API/ClubController.php',
    'routes/api.php',
    # Migrations
    'database/migrations/2025_01_01_000011_create_clubs_table.php',
    'database/migrations/2025_01_01_000012_create_knowledge_ranks_table.php',
    'database/migrations/2025_01_01_000013_add_location_fields.php',
]

sys.stdout.buffer.write(f'\n[1] Uploading {len(files)} files...\n'.encode('utf-8')); sys.stdout.buffer.flush()
for f in files:
    upload(f)

sys.stdout.buffer.write(b'\n[2] Running migrations...\n'); sys.stdout.buffer.flush()
run(f'cd {APP} && php artisan migrate --force 2>&1', timeout=60)

sys.stdout.buffer.write(b'\n[3] Building frontend...\n'); sys.stdout.buffer.flush()
run(f'cd {APP} && npm run build 2>&1 | tail -5', timeout=300)

sys.stdout.buffer.write(b'\n[4] Site check...\n'); sys.stdout.buffer.flush()
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
sys.stdout.buffer.write(b'\n=== DONE ===\n'); sys.stdout.buffer.flush()
