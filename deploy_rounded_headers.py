import paramiko, os, sys

HOST = '68.183.60.70'; USER = 'root'; PASS = 'EhdRh0817wodl'
APP = '/var/www/somekorean'; LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files'

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

def upload(rel):
    local = os.path.join(LOCAL, *rel.split('/'))
    remote = f'{APP}/{rel}'
    run(f'mkdir -p {os.path.dirname(remote)}')
    sftp.put(local, remote)
    sys.stdout.buffer.write(f'  UP: {rel.split("/")[-1]}\n'.encode('utf-8')); sys.stdout.buffer.flush()

print('\n=== Rounded headers + Dashboard fix + Omok fix ===')

files = [
    'resources/js/pages/profile/UserDashboard.vue',
    'resources/js/pages/games/OmokGame.vue',
    'resources/js/pages/jobs/JobList.vue',
    'resources/js/pages/market/MarketList.vue',
    'resources/js/pages/directory/BusinessList.vue',
    'resources/js/pages/events/EventList.vue',
    'resources/js/pages/games/GameLobby.vue',
    'resources/js/pages/match/MatchHome.vue',
    'resources/js/pages/friends/FriendList.vue',
    'resources/js/pages/PointRules.vue',
    'resources/js/pages/elder/ElderHome.vue',
    'resources/js/pages/ride/RideMain.vue',
    'resources/js/pages/chat/ChatRooms.vue',
    'resources/js/pages/news/NewsList.vue',
    'resources/js/pages/community/ClubList.vue',
]

print(f'\n[1] Uploading {len(files)} files...')
for f in files: upload(f)

print('\n[2] Building...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

print('\n[3] Check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close(); client.close()
print('\n=== DONE ===')
