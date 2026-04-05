import paramiko, os, sys

HOST = '68.183.60.70'
USER = 'root'
PASS = 'EhdRh0817wodl'
APP  = '/var/www/somekorean'
LOCAL = r'C:\Users\Admin\Desktop\somekorean\server_files\resources'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print('Connecting...')
client.connect(HOST, username=USER, password=PASS, timeout=15)
print('Connected!')

sftp = client.open_sftp()

def run(cmd, timeout=180):
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    sys.stdout.buffer.write(out.encode('utf-8'))
    sys.stdout.buffer.write(b'\n')
    sys.stdout.buffer.flush()
    if err and 'Warning' not in err:
        sys.stdout.buffer.write(f'[ERR] {err[:300]}\n'.encode('utf-8'))
        sys.stdout.buffer.flush()

def upload(local_path, remote_path):
    remote_dir = os.path.dirname(remote_path)
    run(f'mkdir -p {remote_dir}')
    sftp.put(local_path, remote_path)
    print(f'OK: {os.path.basename(remote_path)}')

# 업로드할 Vue 파일들
vue_files = [
    (r'js\router\index.js',                           f'{APP}/resources/js/router/index.js'),
    (r'js\pages\community\BoardList.vue',             f'{APP}/resources/js/pages/community/BoardList.vue'),
    (r'js\pages\community\PostDetail.vue',            f'{APP}/resources/js/pages/community/PostDetail.vue'),
    (r'js\pages\community\PostWrite.vue',             f'{APP}/resources/js/pages/community/PostWrite.vue'),
    (r'js\pages\jobs\JobList.vue',                    f'{APP}/resources/js/pages/jobs/JobList.vue'),
    (r'js\pages\jobs\JobDetail.vue',                  f'{APP}/resources/js/pages/jobs/JobDetail.vue'),
    (r'js\pages\jobs\JobWrite.vue',                   f'{APP}/resources/js/pages/jobs/JobWrite.vue'),
    (r'js\pages\market\MarketList.vue',               f'{APP}/resources/js/pages/market/MarketList.vue'),
    (r'js\pages\market\MarketDetail.vue',             f'{APP}/resources/js/pages/market/MarketDetail.vue'),
    (r'js\pages\market\MarketWrite.vue',              f'{APP}/resources/js/pages/market/MarketWrite.vue'),
    (r'js\pages\directory\BusinessList.vue',          f'{APP}/resources/js/pages/directory/BusinessList.vue'),
    (r'js\pages\directory\BusinessDetail.vue',        f'{APP}/resources/js/pages/directory/BusinessDetail.vue'),
    (r'js\pages\directory\BusinessRegister.vue',      f'{APP}/resources/js/pages/directory/BusinessRegister.vue'),
    (r'js\pages\points\PointDashboard.vue',           f'{APP}/resources/js/pages/points/PointDashboard.vue'),
    (r'js\pages\messages\MessageInbox.vue',           f'{APP}/resources/js/pages/messages/MessageInbox.vue'),
    (r'js\pages\admin\Dashboard.vue',                 f'{APP}/resources/js/pages/admin/Dashboard.vue'),
    (r'js\pages\profile\UserProfile.vue',             f'{APP}/resources/js/pages/profile/UserProfile.vue'),
]

print(f'\n=== [1/2] Vue 파일 업로드 ({len(vue_files)}개) ===')
for local_rel, remote in vue_files:
    local_full = os.path.join(LOCAL, local_rel)
    upload(local_full, remote)

print('\n=== [2/2] npm run build ===')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

# 결과 확인
print('\n=== 결과 확인 ===')
run(f'find {APP}/resources/js -name "*.vue" -exec wc -l {{}} \\; | grep -v "^0 "')
run(f'ls {APP}/public/build/assets/ | wc -l')

sftp.close()
client.close()
print('\n=== 완료! ===')
