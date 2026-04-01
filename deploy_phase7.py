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

print('\n=== Phase 7 (검색 + 프로필 수정 + NavBar 검색창) ===')

# 1. Vue pages
print('\n[1] Vue pages...')
pages = [
    ('resources/js/pages/Search.vue',               f'{APP}/resources/js/pages/Search.vue'),
    ('resources/js/pages/profile/ProfileEdit.vue',  f'{APP}/resources/js/pages/profile/ProfileEdit.vue'),
    ('resources/js/components/NavBar.vue',           f'{APP}/resources/js/components/NavBar.vue'),
]
for rel, remote in pages:
    upload(os.path.join(LOCAL, *rel.split('/')), remote)

# 2. Router
print('\n[2] Router...')
upload(os.path.join(LOCAL,'resources','js','router','index.js'),
       f'{APP}/resources/js/router/index.js')

# 3. Build
print('\n[3] Building...')
run(f'cd {APP} && npm run build 2>&1', timeout=300)

# 4. Final check
print('\n[4] Final check...')
run(f'curl -s -o /dev/null -w "%{{http_code}}" https://somekorean.com/')

sftp.close()
client.close()
print('\n=== Phase 7 DONE ===')
